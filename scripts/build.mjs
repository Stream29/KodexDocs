import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { locales, repository, sections } from '../src/site.mjs';

const root = new URL('../', import.meta.url);
const check = process.argv.includes('--check');
const site = 'https://stream29.github.io/KodexDocs/';
const escape = (text) => text.replaceAll('&', '&amp;').replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');

function render(lang, t, markdown) {
  const base = lang === 'en-US' ? './' : '../';
  // Split only for navigation anchors. The Markdown itself is not rendered.
  const [intro, ...chapters] = markdown.split(/(?=^## )/m);
  if (chapters.length !== sections.length) throw new Error(`${lang}: expected ${sections.length} chapters`);
  const titles = chapters.map((chapter) => chapter.split('\n')[0].slice(3));
  const link = (href, label) => `<a href="${escape(href)}">${escape(label)}</a>`;
  return `<!doctype html>
<html lang="${lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Kodex Docs — ${t.title}</title>
  <meta name="description" content="${escape(t.description)}">
  <meta name="theme-color" content="#101617">
  <link rel="canonical" href="${site}${t.path}">
  ${Object.entries(locales).map(([id, locale]) => `<link rel="alternate" hreflang="${id}" href="${site}${locale.path}">`).join('\n  ')}
  <link rel="alternate" hreflang="x-default" href="${site}">
  <link rel="icon" href="${base}favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="${base}style.css">
  <script src="${base}app.js" defer></script>
</head>
<body id="top">
  <a class="skip-link" href="#main">${t.skip}</a>
  <header class="topbar">
    <a class="brand" href="${base}${t.path}"><span aria-hidden="true">&gt;_</span> Kodex Docs</a>
    <nav class="languages" aria-label="${t.language}">
      ${Object.entries(locales).map(([id, locale]) => `<a class="language" href="${base}${locale.path}" lang="${id}" hreflang="${id}"${id === lang ? ' aria-current="true"' : ''}>${locale.name}</a>`).join('\n      ')}
    </nav>
  </header>
  <div class="workspace">
    <aside class="sidebar">
      <nav class="contents" aria-label="${t.navigation}">
        ${sections.map((id, i) => link(`#${id}`, titles[i])).join('\n        ')}
      </nav>
      <nav class="resources" aria-label="${t.source}">
        ${link(`${repository}/releases`, `${t.release} ↗`)}
        ${link(repository, `${t.source} ↗`)}
        ${link(`${base}${lang}.md`, `${t.raw} ↗`)}
        ${link(`https://github.com/Stream29/KodexDocs/edit/main/src/${lang}.md`, `${t.edit} ↗`)}
      </nav>
    </aside>
    <main id="main" tabindex="-1">
      <h1 class="sr-only">Kodex / ${t.title}</h1>
      <pre class="markdown">${escape(intro)}</pre>
      ${chapters.map((chapter, i) => `<section id="${sections[i]}" aria-label="${escape(titles[i])}"><pre class="markdown">${escape(chapter)}</pre></section>`).join('\n      ')}
    </main>
  </div>
</body>
</html>
`;
}

async function emit(path, content) {
  const target = new URL(`docs/${path}`, root);
  if (check) {
    if (await readFile(target, 'utf8') !== content) throw new Error(`Stale output: docs/${path}. Run npm run build.`);
  } else {
    await mkdir(new URL('./', target), { recursive: true });
    await writeFile(target, content);
  }
}
for (const [lang, content] of Object.entries(locales)) {
  const markdown = await readFile(new URL(`src/${lang}.md`, root), 'utf8');
  await emit(`${content.path}index.html`, render(lang, content, markdown));
  await emit(`${lang}.md`, markdown);
}
for (const name of ['style.css', 'app.js', 'favicon.svg']) await emit(name, await readFile(new URL(`src/${name}`, root), 'utf8'));
await emit('.nojekyll', '');
await emit('404.html', `<!doctype html>
<html lang="en-US"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>404 — Kodex Docs</title><link rel="stylesheet" href="/KodexDocs/style.css">
<main class="not-found"><h1>404 / Kodex Docs</h1>
<p>Page not found / 页面不存在 / 頁面不存在</p>
<nav><a href="/KodexDocs/">English</a> · <a href="/KodexDocs/zh-CN/">简体中文</a> · <a href="/KodexDocs/zh-TW/">繁體中文</a></nav></main></html>\n`);
await emit('sitemap.xml', `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${Object.values(locales).map(({ path }) => `<url><loc>${site}${path}</loc></url>`).join('')}</urlset>\n`);
console.log(`${check ? 'Checked' : 'Built'} 3 unrendered Markdown guides in docs/`);
