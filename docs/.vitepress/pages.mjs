// Vite's glob handles additions/deletions as well as edits, without a custom watcher.
const sources = import.meta.glob('../**/*.md', {
  eager: true, query: '?raw', import: 'default',
});
export const pages = Object.entries(sources).map(([file, source]) => {
  const url = file.replace(/^\.\./, '').replace(/index\.md$/, '').replace(/\.md$/, '.html');
  return {
    url,
    lang: url.startsWith('/zh-CN/') ? 'zh-CN' : url.startsWith('/zh-TW/') ? 'zh-TW' : 'en-US',
    title: source.match(/^# (.+)$/m)?.[1] ?? url,
  };
}).sort((a, b) => a.url.localeCompare(b.url));
