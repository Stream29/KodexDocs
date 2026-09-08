# Reading history, branches, and execution results (draft)

> First-pass draft; the site directory is not approved. Based on the current Kodex `0.4.3` source and tests, not a finished recording.

## Understand the history position first

- History is rendered in reverse order, with the newest entry at the bottom; it follows the latest content by default.
- Scrolling upward to read older entries keeps the reading position. New content does not force the view back to the bottom.
- When `[↓]` appears in the separator, select it to return to the bottom and resume following the latest content.
- The history window pages older and newer entries on demand and preserves the visible-item anchor while a page arrives.
- An entry may be a message, a `Take N actions` work group, a tool summary, a Patch, or a plan. Read the summary first, then expand only what is needed.

## Expand entries and read results

- A collapsed tool entry uses a user-facing summary such as `Run: pwd`; the raw tool name, arguments, and result are layered behind expansion.
- Results keep their actual state: running, completed, and failed states are expressed by UI state/color. Do not describe a failed entry as a successful example.
- Right-clicking a concrete history entry opens the history action menu; the menu is valid only while that entry is still in the current window.
- Patch has a dedicated view:
  1. expand the entry to see `Tool: apply_patch`;
  2. expand `Changes` to see files and additions/removals;
  3. large patches start with one page, then use `Show next 200 lines`, which also reports the remaining count.
- `update_plan` is shown as a checklist, not raw JSON: `[ ]` pending, `[>]` in progress, and `[x]` completed.

## Fork from here and Revert to here

- The entry menu exposes `Fork from here` / `Revert to here` only when the Agent is stopped, the required history capabilities are available, and the target still belongs to the current history generation.
- `Fork from here` creates a new persisted session at the selected boundary, prefixes its title with `[fork]`, and opens that session; the source session is not deleted.
- `Revert to here` opens a confirmation dialog:
  - keep the selected history entry;
  - remove all history after it;
  - explicitly show `This cannot be undone.`;
  - `Cancel` leaves history unchanged; `Revert` starts the asynchronous destructive operation.
- This revert changes Kodex session history and clears pending steer. It is not a working-directory file rollback and not a Git rollback; the demo must not imply that files are restored with the history.
- The workbench history index `Check out` is navigation: it only requests scrolling to an entry. It is distinct from per-entry Fork/Revert branching or destructive history replacement.

## Demonstration boundary

- A real demo must use an isolated disposable Home, tmux socket, port, and CLI copy; it must not read or modify personal sessions.
- Result examples must use real success/failure records, never test assertions or hand-written output presented as success.
- Only an isolated CLI launch preflight has been completed. It showed the session entry and an empty new session; no history operation was recorded. There is no safe CLI-importable history/tool-result fixture, so no `.cast` is produced.

## Current-source evidence

- History position and `[↓]`: `Kodex/app/viewmodel/history/src/commonMain/kotlin/io/github/stream29/kodex/cli/history/AgentHistoryViewModel.kt:95-215,376-819`, `Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeUiPrimitives.kt:75-108`.
- History list, expansion, and context-menu entry point: `Kodex/app/view/history/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/history/AgentHistoryView.kt:102-188,315-414`.
- Capability gates, confirmation, and irreversible text: `Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeCliScreen.kt:1372-1498`, `Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt:305-414,700-738`.
- Fork boundary and new-session creation: `Kodex/app/viewmodel/session/src/commonMain/kotlin/io/github/stream29/kodex/cli/session/SessionViewModels.kt:301-363`.
- Patch layers and paging: `Kodex/app/view/patch/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/patch/PatchToolEventView.kt:83-225`.
- Plan markers: `Kodex/app/view/history/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/history/PlanUpdateView.kt:36-68`.
