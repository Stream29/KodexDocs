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
- The original twelve clips follow source revision `89205188d5da`; three
  completion clips use `2b16ae50`. Neither source snapshot is a release claim.

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
- Recordings behave like animations: native autoplay/loop, no controls, and an
  inert mount that prevents mouse, keyboard, focus, and selection interaction.
- `results-history` collapses the first 190.1 seconds of preparation to timestamp
  zero so every loop starts at the actual history. All terminal output is preserved;
  the original recording and output hashes are retained in provenance.
- `docs/public/recordings/` contains eight isolated native CLI recordings and seven
  recordings exported from production Compose components.
- Component clips use edited two-second checkpoints and no live model call.
  The original four use offline component fixtures; the three completion clips
  use a disposable filesystem Home and in-memory RPC with the full application
  shell. `suggestions-accepted` receives a suggestion tool call from the mocked
  model, then creates and automatically opens real disposable Session tabs;
  a child tab is selected to show its result.
  The manifest distinguishes all of them from native PTY clips.
- `execution` is an actual authenticated model run, continuing an authorized English
  excerpt of a local feature discussion in a disposable Session/project. The original
  conversation is never opened by the demo CLI. Authentication is bound read-only;
  no credentials are included in recordings. The player starts at 2× and shortens idle waits.
- `history-index` shows the native CLI's mixed real history and hover transitions.
  `results-history` is one continuous native review of the same run, including actual
  command results, patch changes, questions, plans, compaction, Fork and Revert.
- `session-management` shows rename, close, catalog reopen, archive/unarchive and
  cancelled/confirmed deletion with persisted results. `history-invalidation`
  shows a running turn dismissing the history menu and changing the selected
  Session dismissing a stale Revert confirmation; the current UI does not retain
  a disabled action in either case.
- `hooks` records actual configuration validation, event selection, editing and deletion.
  `mcp` uses a disposable stdio server to exercise real connection failure/reconnect,
  enable/disable, editing, Codex import and deletion. HTTP/OAuth is an unsaved
  configuration draft, not a successful external authorization.
- On narrow screens the fixed terminal grid scales down; use landscape/full screen.
  This is playback, not a live terminal.
- `manifest.json` records format, source revisions, generators, timing, and hashes.
  The original native binary was freshly built from its recorded revision plus
  the recorded testability-only dialog visibility change.

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

The earlier component clips were exported with the old
`DocsRecordingTest.kt`, `DocsHistoryRecordingTest.kt`, and
`DocsWorkspaceRecordingTest.kt` sources. For the three current-source
completion clips, run `:app-impl-view:jvmTest` in Kodex/ with
`KODEX_DOCS_RECORDINGS_DIR` pointing to an absolute output directory and
`--tests` filters for `docsCompletionRecordingTest`,
`docsSessionManagementRecordingTest`, and
`docsHistoryInvalidationRecordingTest`. These tests use disposable Home
directories and a mocked model client; ordinary test runs do not export files.
Review the plain frames against browser playback before copying casts into
`docs/public/recordings/`. Collapse the reviewed results preparation interval with
`uv run python KodexDocs/scripts/recording_timing.py out/docs-live-current/results-history.cast KodexDocs/docs/public/recordings/results-history.cast --before 190.1`.
From BuildKodex, run
`uv run python -B KodexDocs/scripts/update-completion-manifest.py --source-revision <tested-Kodex-revision>`
after reviewing the three completion clips. It preserves older provenance.
`recording-manifest.py` describes the earlier source layout and should not be
rerun against the current checkout. Keep the earlier native
`.provenance.json` files in `out/docs-native-current/`; never replace recorded
output with hand-written ANSI.
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
