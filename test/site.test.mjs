import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, access } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { locales, sections, version } from '../src/site.mjs';

const root = new URL('../', import.meta.url);
const unescape = (text) => text.replaceAll('&lt;', '<').replaceAll('&gt;', '>')
  .replaceAll('&quot;', '"').replaceAll('&#39;', "'").replaceAll('&amp;', '&');

test('generated output matches source', () => {
  execFileSync(process.execPath, ['scripts/build.mjs', '--check'], { cwd: root });
});
for (const [lang, locale] of Object.entries(locales)) {
  const path = `${locale.path}index.html`;
  const page = await readFile(new URL(`docs/${path}`, root), 'utf8');
  const markdown = await readFile(new URL(`src/${lang}.md`, root), 'utf8');
  test(`${lang}: displayed and downloadable Markdown exactly match source`, async () => {
    const displayed = [...page.matchAll(/<pre class="markdown">([\s\S]*?)<\/pre>/g)].map((match) => unescape(match[1])).join('');
    assert.equal(displayed, markdown);
    assert.equal(await readFile(new URL(`docs/${lang}.md`, root), 'utf8'), markdown);
    assert.ok(markdown.includes('```sh\n'));
    assert.ok(markdown.includes('```powershell\n'));
    assert.ok(!page.includes('\uFFFD'));
    assert.ok(!page.includes('/home/stream/'));
    assert.ok(!page.includes('terminal-preview'));
    assert.ok(!page.includes('<code>'), 'Markdown is not rendered');
    assert.equal((page.match(/<h1 /g) ?? []).length, 1);
  });
  test(`${lang}: navigation and local assets resolve under the project base path`, async () => {
    const base = new URL(path, 'https://stream29.github.io/KodexDocs/');
    const ids = [...page.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]);
    assert.equal(new Set(ids).size, ids.length);
    for (const section of sections) assert.ok(ids.includes(section));
    for (const [, attribute] of page.matchAll(/(?:href|src)="([^"]+)"/g)) {
      const target = new URL(attribute, base);
      if (target.origin !== base.origin) continue;
      assert.ok(target.pathname.startsWith('/KodexDocs/'), attribute);
      let filePath = target.pathname.slice('/KodexDocs/'.length);
      if (filePath.endsWith('/')) filePath += 'index.html';
      const file = new URL(`docs/${filePath}`, root);
      await access(file);
      if (target.hash) assert.ok((await readFile(file, 'utf8')).includes(`id="${target.hash.slice(1)}"`), attribute);
    }
  });
  test(`${lang}: release archive names and language metadata are complete`, () => {
    for (const suffix of ['macos-arm64.tar.gz', 'linux-x64.tar.gz', 'linux-arm64.tar.gz', 'windows-x64.zip', 'SHA256SUMS.txt']) {
      assert.ok(markdown.includes(`kodex-${version}-${suffix}`));
    }
    assert.ok(page.includes(`<html lang="${lang}">`));
    for (const language of Object.keys(locales)) assert.ok(page.includes(`hreflang="${language}"`));
    assert.equal((page.match(/class="language"/g) ?? []).length, 3);
    assert.ok(!page.includes('src="https://'), 'no third-party scripts');
  });
}
