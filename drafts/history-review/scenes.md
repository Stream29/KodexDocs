# History-review scenes (draft)

## Status

- Directory status: draft only; no route, homepage, navigation, or theme changes.
- Source baseline: Kodex `0.4.3`, submodule `89205188d5da39f36b983a0bfb57752977feb21a`, working tree clean.
- Existing CLI used only for isolated preflight: `Kodex/app/cli/build/bin/linuxX64/releaseExecutable/kodex-cli.kexe`, SHA256 `92539baaa88f4cb78a58ad73c5a23844ef49f65babb4ee968a692c80f26e6720`.
- Existing preflight result: isolated bwrap/tmux launch reached `[Sessions] [New Session]` and an empty composer; no personal Home, session, credential, or network was used.
- Recording status: not recorded. `out/docs-demos/history-review/` does not contain an artifact.

## Disposable-data construction entrances

- **History mutation fixture**: `Kodex/app/viewmodel/session/src/commonTest/kotlin/io/github/stream29/kodex/cli/session/AgentHistoryActionTest.kt:33-169`.
  - Creates `InMemoryKodexSessionRepository`.
  - Initializes `storage`, writes safe `StableUserMessage` / `StableAssistantMessage` entries at explicit indexes, then exercises `requestHistoryRevert`, `confirmHistoryRevert`, and `session.fork`.
  - Verifies that the selected entry remains, later entries are removed, a new fork gets `[fork]` in its title, stale generations are rejected, and accepted revert survives frontend cancellation.
- **Filesystem shape reference**: `Kodex/agent-session/filesystem/src/commonTest/kotlin/io/github/stream29/kodex/agentsession/filesystem/FileSystemKodexSessionRepositoryTest.kt:128-190,500-531`.
  - Uses a temporary repository root and writes through the storage API; it is a construction reference, not a checked-in recording fixture.
  - The persisted shape is under `sessions/<index>/`; do not hand-edit a personal Home or reuse it for recording.
- **Result fixtures**:
  - Tool summaries, deferred arguments/results, command output, and `[ ]/[>]/[x]`: `Kodex/app/view/history/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/history/CleanEventViewTest.kt:215-309,340-475,639-687`.
  - Structured Patch, `Changes`, colored additions/removals, failure state, and `Show next 200 lines`: `Kodex/app/view/patch/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/patch/PatchToolEventViewTest.kt:21-55,96-128,131-159,203-250`.
  - These are real component fixtures and test the production renderers, but they are not an application export format and must not be presented as a live CLI recording.

## Planned scene operations

### A. Older history and position recovery

1. Start a disposable CLI copy with a disposable Home, project, tmux socket, and port.
2. Use a safe history fixture containing several messages and at least one expandable work/tool item.
3. Scroll upward; capture the visible old item and the appearance of `[↓]`.
4. Expand one item without changing the reading anchor.
5. Select `[↓]`; verify the view returns to the bottom.

### B. Entry actions

1. Stop the Agent and select a committed entry that remains in the current history window.
2. Open the entry context menu; show `Revert to here` and `Fork from here`.
3. Choose `Fork from here`; verify a separate `[fork]` session opens while the source remains.
4. In a separate disposable session, choose `Revert to here`.
5. Show the confirmation text, cancel once, then repeat and confirm only if the disposable fixture is safe to destroy.
6. Verify the selected entry remains and later history disappears; do not inspect or claim file/Git changes.

### C. Result reading

1. Expand a real completed or failed tool entry; show the user-facing summary, elapsed time, raw tool name, and deferred payload sections.
2. Expand a Patch entry, then `Changes`, then one more page of lines if the fixture exceeds 200 lines.
3. Show a real plan entry with `[ ]`, `[>]`, and `[x]`.
4. Keep success and failure states truthful in captions and markers.

## Current blockers and validation scope

- No CLI import/replay command or checked-in persistent history/tool-result fixture was found.
- The available deterministic construction paths are in-memory/filesystem test code and Mosaic component tests; implementing a test exporter is outside this task.
- The isolated CLI preflight proves only safe startup and Home isolation. It does not prove history, Fork/Revert, tool-result, Patch paging, or plan behavior in the native CLI.
- Existing test-result evidence was inspected without rebuilding shared Kodex outputs:
  - `agentHistoryAnchorTest`: 4 passed;
  - `agentHistoryEntryInteractionTest`: 6 passed;
  - `cleanEventViewTest`: 21 passed;
  - `historyEntryContextMenuTest`: 2 passed;
  - `patchToolEventViewTest`: 7 passed;
  - `agentHistoryActionTest` result file is stale/failed (3 tests, 2 failures) because its generated class rejected the target as absent from the current window; it is not treated as proof of a successful runtime operation.
- Browser/static-site verification, language switching, narrow-screen layout, and a real `.cast` audit remain unverified.
