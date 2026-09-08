# Workspace-tour scenes and evidence

## Scope

- This is the first-batch draft for the workspace-tour task. It is intentionally outside `KodexDocs/docs/`; no route or navigation is implied.
- The retained evidence is a real native CLI PTY recording, not a recreated TUI and not a video capture.
- The recording is limited to safe state available in an isolated empty Home. History and process rows are not claimed complete just because their configured panels were opened.

## Baseline

| Item | Observed value |
| --- | --- |
| Capture date | 2026-09-08 (Asia/Singapore) |
| Kodex submodule HEAD | `89205188d5da39f36b983a0bfb57752977feb21a` |
| CLI path | `Kodex/app/cli/build/bin/linuxX64/releaseExecutable/kodex-cli.kexe` |
| CLI SHA-256 | `92539baaa88f4cb78a58ad73c5a23844ef49f65babb4ee968a692c80f26e6720` |
| CLI version shown by isolated Home | `0.4.3` |
| asciinema | 3.2.1, SHA-256 `bec9781bc8f297a9d3d74ff60205599507f2abba1183578b8b2f22be4c999214` |
| terminal | tmux 3.6, 120×36, `xterm-256color`, truecolor |
| input capture | Disabled; no `--capture-input`, no upload |
| recording | `out/docs-demos/workspace-tour/workspace-tour.cast` |
| recording SHA-256 | `7951d5598ce6ab70eefcc11d816c14e9753573969b7860307a8cc5f3894fe8ee` |
| recording size | 679,312 bytes; v3 header, exit event status `0` |

The binary was already present before this task and was not rebuilt. Its hash is recorded for reproducibility, but it is not traceable to the submodule HEAD above; this is a limitation of the available binary, not a release-build claim. The outer repository and the KodexDocs checkout already had unrelated worktree changes; this task did not overwrite them.

## Recorded scenes

| Frame / scene | Steps | Evidence and result |
| --- | --- | --- |
| `frame-00-start.txt` | Launch the CLI in a fresh isolated Home. | Both sidebars are collapsed; the center and session controls are visible. |
| `frame-01-left-hover.txt` | Move over the left collapsed control. | Left sidebar reveals `History Index`; right side stays collapsed. |
| `frame-02-left-pinned.txt` | Click the left control, then move away. | Left sidebar remains expanded after the pointer leaves. |
| `frame-03-left-still-pinned.txt` | Move into the center. | Left remains pinned independently. |
| `frame-04-right-hover.txt` | Move over the right collapsed control. | Right sidebar reveals `Terminal sessions` without changing the left state. |
| `frame-05-both-pinned.txt` | Click the right control, then move away. | Both sides remain expanded. |
| `frame-06-both-still-pinned.txt` | Move into the center. | Both pinned states persist independently. |
| `frame-07-left-resized.txt` | Drag the left one-column splitter from the 28-column default to 38 columns. | The isolated Home records `left_width: 38` after release; `settings-after-resize.yml` is retained as a non-private assertion artifact. |
| `frame-08-content-menu.txt` | Open the left title menu. | The real menu shows `None`, `Terminal sessions`, and `History Index`. |
| `frame-09-none.txt` | Select `None`. | The left header changes to `None` and its body is empty by explicit choice. |
| `frame-10-terminal-sessions.txt` | Reopen the left menu and select `Terminal sessions`. | The left header changes to `Terminal sessions`; the body has no rows because there is no selected Agent. |

The PTY command used a copied CLI, a private temporary Home, a private tmux socket, and an isolated project containing only empty `docs`, `src`, and `tests` directories. Network access was removed with bubblewrap. The temporary Home, recorder Home, CLI copy, and socket were removed after the retained artifacts were copied.

## Source and test anchors checked

| Behavior | Anchor | What was confirmed |
| --- | --- | --- |
| Independent expand/pin state and animated widths | [`SessionTreeCliScreen.kt`](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeCliScreen.kt#L96), [`SessionTreeCliScreen.kt`](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeCliScreen.kt#L427) | Left/right state is held separately; resize end calls the corresponding settings update. |
| Content choices | [`SessionSidebar.kt`](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionSidebar.kt#L170) | `None`, `TerminalSessions`, and `HistoryIndex` are enum-backed choices, not a hard-coded directory. |
| History hover and read-only question preview | [`SessionSidebar.kt`](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionSidebar.kt#L707) | Hover loads detail after a delay; question entries use read-only history rows. |
| Check out semantics | [`SessionTreeCliScreen.kt`](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeCliScreen.kt#L743) | The callback requests a history scroll to the storage index; no rollback or Git operation is called. |
| Terminal process hover/menu | [`SessionSidebar.kt`](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionSidebar.kt#L647) | Hover title includes session ID and command; the menu action calls the process session's `close`. |
| Tab overflow and selection | [`SessionTabBarTest.kt`](../../../Kodex/app/view/application/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/app/SessionTabBarTest.kt#L169) | Overflow uses horizontal paging and keeps later tabs reachable. |
| Inactive-tab right click | [`SessionTabBarTest.kt`](../../../Kodex/app/view/application/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/app/SessionTabBarTest.kt#L316) | The inactive target opens the menu while the selected target remains unchanged. |

## Safe construction entries and blockers

### History index

- Safe component-fixture entry: [`HistoryIndexViewModelTest.kt`](../../../Kodex/app/viewmodel/agent/src/commonTest/kotlin/io/github/stream29/kodex/cli/agent/HistoryIndexViewModelTest.kt#L48) uses `InMemoryKodexAgentStorage` and synthetic stable entries. The test covers summaries, full details, incremental indexes, and invalidation without private data or network access.
- Live CLI entry would require an isolated selected Agent with persisted timeline entries. The current CLI has no supported “seed history” command, and an empty Home has no selected Agent. A future recording should use a dedicated fixture/export path or a local test renderer, clearly labeled as fixture-driven.
- Blocked in this batch: populated hover detail, question-form preview, right-click `Check out`, and the visible post-positioning result. No empty panel is presented as proof of these behaviors.

### Terminal sessions

- Safe component-fixture entry: [`SessionSidebarTest.kt`](../../../Kodex/app/view/application/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/app/SessionSidebarTest.kt#L208) uses `TestAgentShellSession` to verify the `Close session` action without spawning a real process.
- Live CLI entry: select an Agent, start a long-running unified-exec command, select `Terminal sessions`, then hover and right-click its row. The runtime source adapts `unifiedExecToolClient.activeSessions` in `AgentRuntimeViewModel.kt`.
- Blocked in this batch: isolated empty Home has no selected Agent and no active unified-exec process. Creating one through the model would require credentials/network and would violate the safe recording boundary; an empty list is not evidence.

### Session tabs

- Safe test entry: `SessionTabBarTest` creates ten in-memory sessions for overflow and two in-memory sessions for the inactive-tab context-menu assertion.
- Blocked in this batch: no supported offline CLI action was used to create many real session tabs without starting agent sessions. The source and tests are checked, but this section is not a live-cast claim.

## Validation status

### Actually validated

- The native CLI launched and exited with status `0` in the isolated PTY.
- The retained cast contains the real hover, click, pointer-leave, drag, and menu transitions; it contains no captured input events.
- The frame captures show independent left/right reveal and pin behavior, the three content options, and the explicit `None` / `Terminal sessions` choices.
- The post-drag isolated settings file records `left_width: 38`.
- Source anchors and the named test anchors were read against the current Kodex checkout.
- `./gradlew -Dorg.gradle.java.home=/home/stream/.gradle/jdks/eclipse_adoptium-25-amd64-linux.2 :app-view-application:linuxX64Test --rerun-tasks` passed: 77 tests, 0 failures, 0 skipped. The relevant `sessionSidebarTest` and `sessionTabBarTest` suites are included in that report.

### Not yet validated

- No VitePress/player integration, language switch, browser rendering, narrow-screen readability, or Pages deployment was validated.
- No populated history/process live scene or live multi-tab overflow scene was recorded.
- The existing binary was not rebuilt, so the recording is evidence for the recorded binary, not proof of a freshly built release.
