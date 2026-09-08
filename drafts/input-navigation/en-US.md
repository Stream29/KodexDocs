# Input Editing and Directory Navigation

> Draft: the site directory and player integration are not approved yet. This page records only checked behavior, real-terminal evidence, and boundaries.

## Editing input

Kodex's Composer is a terminal input field. A line that wraps on screen is not written as a newline.

1. Focus the input.
2. Paste text containing CJK, English, numbers, and multiple lines.
3. In a narrower input area, long text soft-wraps according to terminal-cell width; pasted `CRLF` and `CR` endings are normalized to `LF`.
4. Move the cursor with the arrow keys and continue editing. Cursor positions map to source-text boundaries, with wide characters measured in terminal cells.

Soft wrapping is display layout only: it does not insert `\n` into the text. A real newline is produced by the configured newline key. The default pairing is `Shift+Enter` for newline and `Enter` for submit. The alternative pairing is `Enter` for newline and `Ctrl+Enter` for submit. Documentation and demos must not hard-code one submit chord as universal.

### Editing history

- `Ctrl+W` deletes the preceding word group according to the input component's word, whitespace, and punctuation grouping.
- `Ctrl+Z` undoes the latest edit transaction; `Ctrl+Y` redoes it.
- A paste is one atomic edit; typed characters and deletions follow the component's history-merging rules.

Source and test references:

- `Kodex/app/view/components/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/components/TextInput.kt:102-156,221-305`
- `Kodex/app/view/components/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/components/TextInputTest.kt:83-103,181-249,251-364,366-395`
- `Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeUiPrimitives.kt:31-70,194-202`
- `Kodex/app/shared/settings/contract/src/commonMain/kotlin/io/github/stream29/kodex/cli/settings/KodexGlobalSettings.kt:124-147`
- `Kodex/app/view/application/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/app/ComposerInputTest.kt:24-59,89-127`

## Selecting a directory

Open the working-directory picker from Settings:

1. Type letters to filter direct child directories. Matching is case-insensitive; files are not selectable entries.
2. Press `Enter` to enter the first filtered match, then press `Enter` again to confirm the current directory. The focused `[Select]` button also confirms.
3. Press mouse `Button8` to navigate to the parent directory and clear the filter.
4. `Escape` is layered: with a filter it clears the filter first; the next press closes the picker; if Settings remains open, a third press closes Settings.

`Button8` is a real terminal mouse event, not player text selection. Selecting text in the player does not demonstrate native terminal `Shift+drag` selection. Native terminal text selection was not verified in this batch and is intentionally not presented as a Kodex application feature.

Source and test references:

- `Kodex/app/view/path-picker/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/pathpicker/DirectoryPickerPopup.kt:46-134,154-229`
- `Kodex/app/contract/path-picker/src/commonMain/kotlin/io/github/stream29/kodex/app/pathpicker/contract/DirectoryPickerState.kt:67-91`
- `Kodex/app/viewmodel/path-picker/src/commonMain/kotlin/io/github/stream29/kodex/app/pathpicker/DirectoryPickerViewModel.kt:45-88`
- `Kodex/app/view/path-picker/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/pathpicker/DirectoryPickerPopupTest.kt:31-182,184-233`

## Demo boundary

This batch uses **native CLI → asciinema → asciinema-player**. It is not a simulated TUI and does not provide online Kodex interaction. Recording used an isolated temporary Home, tmux socket, CLI copy, and network-disabled sandbox. Formal content still waits for an approved directory; these drafts do not mean that Pages integration is complete.
