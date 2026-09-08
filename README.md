# KodexDocs

Minimal [Kodex](https://github.com/Stream29/Kodex) documentation built with
[VitePress](https://vuejs.github.io/vitepress/v1/guide/custom-theme).
The custom theme displays **literal Markdown**, not rendered rich text or a simulated application.

## Write documentation

- `docs/index.md`: en-US.
- `docs/zh-CN/index.md`: zh-CN.
- `docs/zh-TW/index.md`: zh-TW.
- Edit Markdown and save; VitePress refreshes the local preview.
- Level-two headings automatically populate the chapter navigation.
- Keep one UI showcase page per language, with matching demo order for language switching.
- Code fences, links, HTML and Vue expressions remain literal text. VitePress Markdown/Vue extensions are intentionally not rendered.
- Only UI demonstrations and explicitly requested content belong on the site;
  installation, connections, and standalone reference pages have been removed.
- Feature content follows source revision `89205188d5da`. Do not equate source features with a release.

## Local development

Use Node.js 22 or newer.
VitePress is pinned to stable 1.6.4. A Vite 6.4.3 override avoids
[security advisories in its default Vite 5 dependency](https://github.com/vitejs/vite/security/advisories/GHSA-fx2h-pf6j-xcff);
revalidate build, HMR, and browser behavior when changing either version.

```sh
npm ci
npm run dev
```

Open http://127.0.0.1:4173/KodexDocs/.

```sh
npm run check  # production build, then unit/static-output tests
npm run preview
```

Stop the dev server before starting preview; both use port 4173.
Generated output is ignored at `docs/.vitepress/dist/`; do not edit or commit it.

## Theme

- Only navigation, language switching, resource links, and Markdown source.
- Full-width terminal-like layout: sidebar flush with the left edge, no centered reading container.
- Language labels: `zh-CN`, `zh-TW`, `en-US`.
- Left sidebar starts collapsed: hover previews, click pins/unpins; leaving an unpinned sidebar collapses it.
- Expansion/collapse uses a short CSS/Vue transition; `prefers-reduced-motion` disables the animation.
- `[→]` / `[←]` follows the real CLI sidebar button notation, not an invented app screenshot.
- Keyboard focus opens navigation; Enter/Space pins and Escape collapses. Touch uses the same button.
- Without JavaScript the Markdown and expanded navigation remain available.
- Theme/configuration lives in `docs/.vitepress/`; routine writing requires only Markdown changes.
- Raw-file delivery uses Vite asset imports; event cleanup/mount state reuse VueUse already included by VitePress. There is no custom file server, copy step, or additional UI/CSS framework.
- Navigation discovery also uses Vite's glob, so adding/removing a Markdown file
  does not need a handwritten watcher.

## Real terminal demonstrations

- Put `<!-- kodex-player: workspace -->` on its own line under an H2.
  The marker remains literal text. Each section can mount one allowlisted recording.
- Allowed names live in `docs/.vitepress/theme/terminal-recordings.mjs`.
  Unknown names are inert, including JavaScript prototype names.
- Players have no generated caption or small-screen hint. Provenance stays in
  the manifest; original native footage and component fixtures remain distinguished there.
- All recordings start automatically; the built-in pause and playback controls remain available.
- `results-history` starts at 190.1 seconds, after the recorded preparation and
  repeated redraw interval. This uses the player's `startAt`, not edited ANSI.
- `docs/public/recordings/` contains eight isolated native CLI recordings and four
  recordings exported from actual production Compose components.
- Component recordings use offline fixtures and edited two-second checkpoints:
  no live model call or real project/process operation is implied. The
  manifest distinguishes them from native PTY clips.
- `execution` is an actual authenticated model run, continuing an authorized English
  excerpt of a local feature discussion in a disposable Session/project. The original
  conversation is never opened by the demo CLI. Authentication is bound read-only;
  no credentials are included in recordings. The player starts at 2× and shortens idle waits.
- `history-index` shows the native CLI's mixed real history and hover transitions.
  `results-history` is one continuous native review of the same run, including actual
  command results, patch changes, questions, plans, compaction, Fork and Revert.
- `hooks` records actual configuration validation, event selection, editing and deletion.
  `mcp` uses a disposable stdio server to exercise real connection failure/reconnect,
  enable/disable, editing, Codex import and deletion. HTTP/OAuth is an unsaved
  configuration draft, not a successful external authorization.
- On narrow screens the fixed terminal grid scales down; use landscape/full screen.
  This is playback, not a live terminal.
- `manifest.json` records format, source revision, generators, timing, and hashes.
  The native binary was freshly built from that revision plus the recorded
  testability-only dialog visibility change, not taken from an untraceable old probe.

Regenerate from the BuildKodex workspace, using its documented Gradle JDK and
recording isolation rules:

```sh
# In Kodex/, build :app-cli:linkReleaseExecutableLinuxX64 with the existing daemon JDK.
# From BuildKodex/, with asciinema 3.2.1, tmux and bubblewrap installed:
uv run python KodexDocs/scripts/record-native.py workspace \
  --cli Kodex/app/cli/build/bin/linuxX64/releaseExecutable/kodex-cli.kexe \
  --asciinema /path/to/asciinema --output out/docs-native-current
# Repeat for input and configuration; output files must not already exist.

# Hooks and MCP use their own isolated demo configuration and checked action scripts.
uv run python KodexDocs/scripts/record-integrations.py hooks \
  --cli Kodex/app/cli/build/bin/linuxX64/releaseExecutable/kodex-cli.kexe \
  --asciinema /path/to/asciinema --output out/docs-integrations/final \
  --actions KodexDocs/scripts/fixtures/hooks-actions.json
# Repeat with scene mcp and fixtures/mcp-actions.json.
```

For the component clips, run `:app-view-application:jvmTest --rerun` in Kodex/
with `KODEX_DOCS_RECORDINGS_DIR` pointing to an absolute output directory.
The opt-in exporters are `DocsRecordingTest.kt`, `DocsHistoryRecordingTest.kt`, and
`DocsWorkspaceRecordingTest.kt`; ordinary test runs do not export files.
Review the plain frames against browser playback before copying casts into
`docs/public/recordings/`, then run `uv run python KodexDocs/scripts/recording-manifest.py`
from BuildKodex. Keep the native `.provenance.json` files in `out/docs-native-current/`
for that command. Never replace recorded output with hand-written ANSI.
The integrations recorder also retains settings snapshots and local MCP request/start
logs under `out/docs-integrations/final/` for verification, not as public site assets.

Authenticated recording requires explicit authorization. `scripts/record-live.py`
loads the reviewed `history-index.en.json` resource into a separate Home and accepts
JSON commands on stdin. It needs `--cli`, `--asciinema`, `--auth-file`, and `--output`.
The source credential file is read-only; if refresh is required, stop rather than
making it writable. Keep the generated provenance under `out/docs-live-current/`.
After an interrupted recording, verify that its dedicated tmux and CLI processes
have stopped before deleting the temporary Home. Do not publish failed attempts,
private credentials, logs, or unreviewed raw Session storage.

## GitHub Pages

- Site: https://stream29.github.io/KodexDocs/.
- `.github/workflows/pages.yml` builds/tests source and deploys generated output on pushes to `main`.
- **Migration is currently local only.** The live initial commit `d49bddc` still uses branch publishing from `main:/docs`.
- Before publishing this migration, change repository Settings → Pages → Build and deployment → Source to **GitHub Actions**, then commit/push the migration with separate authorization.
- Do not push this source layout while retaining branch publishing; it is not the deployable site.
- After that one-time switch, routine documentation changes need only Markdown edits and a push; Actions builds/publishes automatically.

See the [VitePress deployment guide](https://vuejs.github.io/vitepress/v1/guide/deploy#github-pages).
