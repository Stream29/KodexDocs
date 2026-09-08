import assert from 'node:assert/strict';
import { readFile, access, readdir } from 'node:fs/promises';
import { resolve } from 'node:path';
import { test } from 'node:test';
import { createHash } from 'node:crypto';
import { createMarkdownRenderer } from 'vitepress';
import { rawDocument } from '../docs/.vitepress/raw-content.mjs';
import config from '../docs/.vitepress/config.mjs';
import { recordingForText } from '../docs/.vitepress/theme/terminal-recordings.mjs';

const output = resolve('docs/.vitepress/dist');
const md = await createMarkdownRenderer(resolve('docs'));
const decode = text => text.replace(/&(lt|gt|amp|quot|#39);/g, (_, entity) =>
  ({ lt: '<', gt: '>', amp: '&', quot: '"', '#39': "'" })[entity]);

test('headings drive navigation without changing source or including fenced headings', () => {
  const source = '# Guide\n\n## Install\n\n```md\n## Not a chapter\n```\n\n## Next\n\n<script>alert(1)</script>\n{{ 1 + 1 }}\n';
  const document = rawDocument(source, md.parse(source, {}));
  assert.equal(document.title, 'Guide');
  assert.deepEqual(document.chunks.map(chunk => chunk.title), ['', 'Install', 'Next']);
  assert.equal(document.chunks.map(chunk => chunk.text).join(''), source);
  assert.deepEqual(document.chunks.map(chunk => chunk.id), ['introduction', 'section-1', 'section-2']);
});

test('empty, CRLF, duplicate and non-Latin headings keep source and unique anchors', () => {
  for (const source of ['', '## 安裝\r\n\r\n## 安裝\r\n', '# No chapters\n', '## Start\nbody']) {
    const document = rawDocument(source, md.parse(source, {}));
    assert.equal(document.chunks.map(chunk => chunk.text).join(''), source);
    assert.equal(new Set(document.chunks.map(chunk => chunk.id)).size, document.chunks.length);
  }
});

test('literal HTML/Vue survives page-data serialization without becoming a script block', async () => {
  config.markdown.config(md);
  const result = await config.transformPageData(
    { relativePath: 'literal.md' },
    { siteConfig: { srcDir: resolve('test/fixtures') } },
  );
  assert.equal(md.render('<script>alert(1)</script>'), '');
  assert.doesNotMatch(result.rawDocument, /[<>]/);
  const document = JSON.parse(decodeURIComponent(result.rawDocument));
  assert.equal(document.chunks.map(chunk => chunk.text).join(''),
    await readFile('test/fixtures/literal.md', 'utf8'));
  assert.deepEqual(document.chunks.map(chunk => chunk.title), ['', 'Literal content']);
});

test('terminal markers preserve source and select only allowlisted recordings', async () => {
  const source = await readFile('docs/index.md', 'utf8');
  const document = rawDocument(source, md.parse(source, {}));
  assert.equal(document.chunks.map(chunk => chunk.text).join(''), source);
  assert.equal(recordingForText(source)?.src, '/recordings/workspace.cast');
  assert.equal(recordingForText('<!-- kodex-player: unknown -->'), undefined);
  for (const name of ['constructor', 'toString', '__proto__', 'hasOwnProperty']) {
    assert.equal(recordingForText(`<!-- kodex-player: ${name} -->`), undefined);
  }
});

for (const [lang, path] of [['en-US', ''], ['zh-CN', 'zh-CN/'], ['zh-TW', 'zh-TW/']]) {
 for (const name of ['index']) {
  test(`${lang}/${name}: pre-rendered HTML and raw endpoint exactly preserve Markdown`, async () => {
    const source = await readFile(`docs/${path}${name}.md`, 'utf8');
    const html = await readFile(`${output}/${path}${name}.html`, 'utf8');
    const rawUrl = html.match(/href="([^"]+)" target="_blank" rel="noopener"/)?.[1];
    assert.ok(rawUrl?.startsWith('/KodexDocs/assets/'), rawUrl);
    const raw = await readFile(resolve(output, rawUrl.slice('/KodexDocs/'.length)), 'utf8');
    const text = [...html.matchAll(/<pre class="markdown">([\s\S]*?)<\/pre>/g)]
      .map(match => decode(match[1])).join('');
    assert.equal(text, source);
    assert.equal(raw, source);
    assert.ok(html.includes(`lang="${lang}"`));
    for (const code of ['zh-CN', 'zh-TW', 'en-US']) assert.ok(html.includes(`>${code}</a>`));
    assert.ok(html.includes('aria-controls="sidebar-panel"'));
    assert.ok(html.includes('aria-pressed="false"'));
    for (const [, pre] of html.matchAll(/<pre class="markdown">([\s\S]*?)<\/pre>/g)) {
      assert.doesNotMatch(pre, /<(?:script|code)[ >]/);
    }
    assert.doesNotMatch(text, /KODEX_HOME|\/home\/stream\/|�/);
    assert.doesNotMatch(html, /terminal-player__note|playback only|On small screens|窄屏可|窄螢幕可/);
    assert.doesNotMatch(html, /github\.com\/Stream29\/KodexDocs\/edit\//);
    assert.match(html, /class="terminal-player__mount" inert/);
    for (const chunk of rawDocument(source, md.parse(source, {})).chunks) {
      const recording = recordingForText(chunk.text);
      if (!recording) continue;
      assert.ok(html.includes(`data-marker="${recording.marker}"`));
      assert.ok(html.includes(`data-recording="/KodexDocs${recording.src}"`));
      const cast = (await readFile(`${output}${recording.src}`, 'utf8')).trim().split('\n').map(JSON.parse);
      assert.ok([2, 3].includes(cast[0].version));
      assert.ok(cast.length > 3);
      assert.ok(cast.slice(1).every(event =>
        event[1] === 'o' || (event[1] === 'x' && event[2] === '0')), 'output and successful exit only');
    }
  });

  test(`${lang}/${name}: local links and assets resolve under the Pages base`, async () => {
    const html = await readFile(`${output}/${path}${name}.html`, 'utf8');
    for (const [, href] of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
      if (/^(?:https?:|data:)/.test(href)) continue;
      if (href.startsWith('#')) {
        assert.ok(html.includes(`id="${href.slice(1)}"`), href);
        continue;
      }
      assert.ok(href.startsWith('/KodexDocs/'), href);
      let local = href.slice('/KodexDocs/'.length).split(/[?#]/)[0];
      if (!local || local.endsWith('/')) local += 'index.html';
      await access(resolve(output, local));
    }
  });
 }
}

test('404 and sitemap are generated by VitePress', async () => {
  const html = await readFile(`${output}/404.html`, 'utf8');
  assert.ok(html.includes('<title>404 | Kodex</title>'));
  const sitemap = await readFile(`${output}/sitemap.xml`, 'utf8');
  for (const path of ['', 'zh-CN/', 'zh-TW/']) {
    assert.ok(sitemap.includes(`https://stream29.github.io/KodexDocs/${path}`));
  }
});

test('all twelve recordings match their provenance and authentication boundaries', async () => {
  const manifest = JSON.parse(await readFile('docs/public/recordings/manifest.json', 'utf8'));
  assert.equal(Object.keys(manifest.recordings).length, 12);
  for (const [name, entry] of Object.entries(manifest.recordings)) {
    const bytes = await readFile(`docs/public/recordings/${name}.cast`);
    assert.equal(createHash('sha256').update(bytes).digest('hex'), entry.castSha256);
    assert.equal(recordingForText(`<!-- kodex-player: ${name} -->`)?.src, `/recordings/${name}.cast`);
    assert.ok(entry.durationSeconds > 0);
    assert.equal(entry.modelCalled, name === 'execution');
    if (['hooks', 'mcp'].includes(name)) {
      assert.equal(entry.kind, 'native-cli');
      assert.equal(entry.networkIsolated, true);
      assert.equal(entry.actionsSha256, createHash('sha256').update(
        await readFile(`scripts/fixtures/${name}-actions.json`)).digest('hex'));
      assert.equal(entry.generatorSha256, createHash('sha256').update(
        await readFile('scripts/record-integrations.py')).digest('hex'));
      assert.equal(entry.fixtureSha256, createHash('sha256').update(
        await readFile('scripts/fixtures/mcp-demo.py')).digest('hex'));
    }
    if (['execution', 'results-history', 'history-index'].includes(name)) {
      assert.equal(entry.originalSessionOpened, false);
      assert.match(entry.credentialAccess, /read-only/);
      assert.ok(entry.translatedHistory.sha256);
    }
    assert.equal(entry.originalHomeMounted, false);
    assert.doesNotMatch(bytes.toString(), /\/home\/stream\/|Bearer [A-Za-z0-9]|sk-[A-Za-z0-9]{20}/);
  }
});

test('only UI showcase remains, with the same twelve demos in each language', async () => {
  const expected = ['workspace', 'history-index', 'terminal-sessions', 'input', 'session-tabs',
    'execution', 'questions', 'suggestions', 'results-history', 'configuration', 'hooks', 'mcp'];
  for (const prefix of ['', 'zh-CN/', 'zh-TW/']) {
    assert.deepEqual((await readdir(`docs/${prefix}`)).filter(name => name.endsWith('.md')), ['index.md']);
    assert.deepEqual((await readdir(`${output}/${prefix}`)).filter(name => name.endsWith('.html') && name !== '404.html'), ['index.html']);
    const text = await readFile(`docs/${prefix}index.md`, 'utf8');
    assert.ok(text.startsWith('# UI showcase\n'));
    assert.doesNotMatch(text, /^#{1,2} .*(?:Installation|Connections|安装|安裝|连接|連線)/mi);
    const chunks = rawDocument(text, md.parse(text, {})).chunks.filter(chunk => chunk.title);
    assert.equal(chunks.length, 12);
    for (const chunk of chunks.filter(chunk => recordingForText(chunk.text)?.marker !== 'configuration')) {
      assert.equal(chunk.text.replace(/^## .+$/m, '').replace(/<!-- kodex-player: [a-z0-9-]+ -->/, '').trim(), '');
    }
    assert.deepEqual(chunks.map(chunk => recordingForText(chunk.text)?.marker), expected);
    assert.equal((text.match(/<!-- kodex-player: results-history -->/g) ?? []).length, 1);
    for (const old of ['workspace', 'run-session', 'review-history', 'configuration', 'connections', 'install-reference']) {
      await assert.rejects(access(`${output}/${prefix}${old}.html`));
    }
  }
});

test('results preparation is collapsed for every loop without changing terminal output', async () => {
  const recording = recordingForText('<!-- kodex-player: results-history -->');
  assert.equal(recording.startAt, undefined);
  const manifest = JSON.parse(await readFile('docs/public/recordings/manifest.json', 'utf8'));
  const provenance = manifest.recordings['results-history'];
  const events = (await readFile('docs/public/recordings/results-history.cast', 'utf8')).trim().split('\n').map(JSON.parse);
  assert.equal(provenance.preparationSecondsCollapsed, 190.1);
  assert.match(provenance.sourceCastSha256, /^[a-f0-9]{64}$/);
  assert.equal(events[1][0], 0);
  assert.equal(createHash('sha256').update(events.slice(1).filter(event => event[1] === 'o')
    .map(event => event[2]).join('')).digest('hex'), provenance.sourceOutputSha256);
  assert.equal(createHash('sha256').update(await readFile('scripts/recording_timing.py'))
    .digest('hex'), provenance.timingEditorSha256);
});
