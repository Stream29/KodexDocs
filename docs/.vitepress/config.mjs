import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { defineConfig } from 'vitepress';
import { locales } from './locales.mjs';
import { rawDocument } from './raw-content.mjs';

let markdown;

export default defineConfig({
  base: '/KodexDocs/',
  title: 'Kodex',
  description: locales['en-US'].description,
  appearance: false,
  scrollOffset: 30,
  head: [['link', { rel: 'icon', href: '/KodexDocs/favicon.svg' }]],
  locales: Object.fromEntries(Object.entries(locales).map(([lang, locale]) => [
    locale.path.replace(/\/$/, '') || 'root',
    { lang, label: lang, title: 'Kodex', description: locale.description },
  ])),
  sitemap: { hostname: 'https://stream29.github.io/KodexDocs/' },
  markdown: {
    config(md) {
      markdown = md;
      // This theme displays source, not compiled Markdown/Vue. In particular,
      // literal <script> and {{ expressions }} must never become executable UI.
      md.render = () => '';
    },
  },
  async transformPageData(page, { siteConfig }) {
    if (page.relativePath === '404.md') return;
    const raw = await readFile(join(siteConfig.srcDir, page.relativePath), 'utf8');
    const document = rawDocument(raw, markdown.parse(raw, {}));
    // Page data is embedded in a Vue SFC by VitePress. Encode literal </script>
    // and other source markup so it cannot terminate that generated script block.
    return {
      title: document.title.replace(/<[^>]*>/g, ''),
      rawDocument: encodeURIComponent(JSON.stringify(document)),
    };
  },
});
