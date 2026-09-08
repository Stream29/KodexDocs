# Workspace: sessions, dual sidebars, and history navigation (draft)

> This is product-manual material, not an approved site outline. UI names and behavior below come from the real CLI; a state that was not recorded or run is not replaced with an empty-panel claim.

## Meet the workspace

The top bar contains session tabs. The left and right sides are **independent sidebars**: each side keeps its own expanded/collapsed state, pinned state, width, and content selection. The center remains the current session; opening a sidebar does not select another session.

An isolated Home with no selected Agent may show an empty History index or Terminal sessions body. That only means there is no data to display in the current state; it does not mean the feature is unavailable.

## Expand, pin, and resize a sidebar

1. Move the pointer over the left or right collapsed button to reveal that sidebar and inspect its header and body.
2. Click the button to pin that side. After the pointer leaves, a pinned sidebar remains expanded.
3. Operate the sides independently: pinning the left side does not pin the right side, and vice versa.
4. Drag the divider between an expanded sidebar and the center content to resize that side. Releasing the pointer persists the width. When both sides are open, the application keeps space for the center.

The recording uses a 120×36 terminal: the left side is dragged from the default 28 columns to 38 columns, then the isolated Home `settings.yml` is checked for `sidebars.left_width: 38`. Coordinates belong to this recording size and should not be documented as stable shortcuts.

## Choose sidebar content

Click a sidebar title to open its content menu. Each side can be configured separately:

- **None**: keep the sidebar header and controls without a body.
- **Terminal sessions**: show active terminal processes owned by the selected Agent.
- **History index**: show the selected Agent's sparse history-index timeline.

Do not describe a sidebar as a fixed “session directory.” After selecting None, an empty body is the explicit configuration. For the other choices, whether rows exist depends on the current session state.

## History index: preview and positioning

When history entries exist:

1. Hover an entry and wait for the preview. The preview loads the complete entry; question entries reuse a read-only history form.
2. Open the entry's context menu to see its index and **Check out**.
3. Choose **Check out** to position the current history view at that entry, then close the menu. It does not roll back the conversation, rewrite history, or run Git checkout.

This batch did not fabricate history entries. The isolated empty Home has no selected Agent, so it is not safe to claim an online preview or Check out demonstration; see the blockers in `scenes.md`.

## Terminal sessions: inspect and close a process

When the selected Agent is running a unified-exec command, Terminal sessions lists its unfinished terminal processes. Hover a row to see `Session <ID>` and the complete command. Right-click the row and choose **Close session** to close only that terminal process.

This is different from closing a Kodex session tab. With no selected Agent or no active unified-exec process, the list is empty. This batch did not use credentials or an online model to manufacture a process, so it documents the entry point without presenting an empty list as process-management evidence.

## When there are many session tabs

- When tabs exceed the visible width, the tab bar supports horizontal paging and brings the selected tab into view.
- Right-clicking an inactive tab opens its menu for that tab without selecting it first.
- A left click selects a tab; opening the context menu is not a session switch.

These behaviors have dedicated `SessionTabBarTest` anchors. This batch focuses the recording on the dual sidebars and did not create many tabs in the isolated CLI, so the tab section needs a later recording with real multiple-session state.

## Evidence and boundaries for this batch

- Retained: `out/docs-demos/workspace-tour/workspace-tour.cast` and the corresponding PTY frame captures.
- Actually run: dual-sidebar hover, independent pinning, staying expanded after leaving, left-sidebar resizing, and the `None` / `Terminal sessions` content menu.
- Not actually run: populated History index preview/Check out, Terminal sessions hover/Close session with an active process, tab overflow, and right-clicking an inactive tab.
- This draft does not settle the site outline, player mounting, or browser acceptance. Those wait for structure confirmation and formal integration.

## Source basis

- Independent sidebar state, expand animation, and persisted resize handling: `SessionTreeCliScreen.kt`.
- Sidebar content choices, history preview, and terminal-process menu: `SessionSidebar.kt`.
- Horizontal tab scrolling, selected-tab visibility, and inactive-tab context menus: `SessionTabBar.kt` and `SessionTabBarTest.kt`.
