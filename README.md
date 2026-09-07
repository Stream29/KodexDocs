# Kodex Docs

Minimal getting-started documentation for [Kodex](https://github.com/Stream29/Kodex). The site displays Markdown **as plain text**, without rendering its syntax.

- [English](https://stream29.github.io/KodexDocs/)
- [简体中文](https://stream29.github.io/KodexDocs/zh-CN/)
- [繁體中文](https://stream29.github.io/KodexDocs/zh-TW/)

## Develop

- Use Node.js 22 or newer; no packages need to be installed.
- Run `npm run build` to generate `docs/`.
- Run `npm test` for content, link, accessibility-markup, and generation checks.
- Run `npm run preview`, then open `http://127.0.0.1:4173/KodexDocs/`.
- Run `npm run check` to detect stale generated files.
- Browser checks: desktop/mobile wrapping, exact Markdown text, locale switching with anchors, keyboard navigation, and reading with JavaScript disabled.

## Edit

- `src/en-US.md`, `src/zh-CN.md`, `src/zh-TW.md`: source documentation.
- `src/site.mjs`: locale metadata, navigation IDs, and release version.
- `scripts/build.mjs`: shared HTML template, metadata, sitemap, and 404 page.
- `src/style.css`: terminal-inspired theme and responsive layout.
- `src/app.js`: active navigation and preservation of the current anchor when switching languages.
- `docs/`: generated public site. Regenerate rather than editing directly.
- Keep five level-two sections in the same order across locales; the generator uses them only as navigation boundaries and preserves the source text exactly.
- When updating releases, verify archive names, checksums, and current UI labels; update version-specific text in all locales and `src/site.mjs`.
- Do not include credentials, private conversations, or local environment details.

## Publish

- GitHub Pages source: **Deploy from a branch → main → /docs**.
- Commit source and regenerated `docs/` together; pushing `main` triggers publication.
- No custom Actions workflow, external fonts, analytics, or runtime dependencies.
- This follows [GitHub’s branch publishing guidance](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
- This repository is independently versioned and included as `KodexDocs/` in BuildKodex.

## Content baseline

- Initial guide targets [Kodex v0.4.3](https://github.com/Stream29/Kodex/releases/tag/v0.4.3).
- UI and behavior references: Kodex `app/cli`, `app/view/application`, `app/view/settings`, and `utils/kodex-home`.
- Colors are adapted from Kodex `TuiTheme.kt`.
- No product UI illustration. Any future UI demonstration must capture real application rendering rather than fabricate an interface.
