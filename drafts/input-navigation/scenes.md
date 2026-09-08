# Input-navigation scenes

## Baseline and evidence

- Route: native Linux CLI → asciinema 3.2.1 → local asciinema-player 3.17.0.
- Cast: `out/docs-demos/input-navigation/input-navigation.cast`
- Player fixture: `out/docs-demos/input-navigation/public/index.html`
- Captured terminal size: 120×36; tmux 3.6; asciicast v3; duration 21.887 s; 102 output events and one exit event.
- CLI SHA256: `92539baaa88f4cb78a58ad73c5a23844ef49f65babb4ee968a692c80f26e6720`
- asciinema SHA256: `bec9781bc8f297a9d3d74ff60205599507f2abba1183578b8b2f22be4c999214`
- Current `Kodex/` HEAD at inspection: `89205188d5da39f36b983a0bfb57752977feb21a`.
- The binary was already present and was not rebuilt. Its provenance from the current source commit is not demonstrated; the runtime Settings screen is older than the checked source's input-settings UI. Treat key-pair configuration as source/test evidence only, not as a claim that this cast exercised the Settings dropdown.

## Recorded scenes

| Scene | Native actions | Evidence frame |
| --- | --- | --- |
| Soft wrap and cell text | Focus input; bracketed-paste a long CJK/English line; move left four times | `frame-01-soft-wrap.txt` |
| Ctrl+W | Press `Ctrl+W` after the cursor movement | `frame-02-ctrl-w.txt` |
| Undo / redo | Press `Ctrl+Z`, then `Ctrl+Y` | `frame-03-undo.txt`, `frame-04-redo.txt` |
| Picker filter | Open Settings → Browse; type `d`, then `o` with a short wait | `frame-06-picker-root.txt`, `frame-07-filter-do.txt` |
| Enter and confirm | Enter `docs/`, then Enter again to confirm | `frame-08-enter-docs.txt`, `frame-10-confirmed.txt` |
| Button8 parent | From `/work/demo/docs`, send SGR mouse Button8 (`128`) | `frame-09-button8-parent.txt` |
| Layered Escape | Reopen picker; filter; Escape clears filter, closes picker, then closes Settings | `frame-11-filter-before-escape.txt` through `frame-14-settings-closed.txt` |

Every captured frame is 36 rows and is compared against the corresponding browser-player frame in `verification.json`. The browser check found the frame sequence at monotonic times, observed CJK spans with two-cell offsets, matched the recorded truecolor foreground/background, and confirmed no page errors, request failures, or horizontal overflow at 1440/1024/768/390/320 px. Mobile scaling is not a claim of mobile readability: 120 columns become small on a phone.

## Source/test checklist

- Soft wrapping preserves source ranges and cell-aware cursor mapping: `TextInput.kt:102-156`; vertical and Unicode movement: `TextInputTest.kt:181-249,251-333`.
- Paste normalization and atomic history: `TextInput.kt:221-223,558-573`; `TextInputTest.kt:83-103,366-395`.
- `Ctrl+W`: `TextInput.kt:237-241`; grouping coverage: `TextInputTest.kt:346-364`.
- Configured newline/submit pairing: `KodexGlobalSettings.kt:124-147`; matching and callback behavior: `SessionTreeUiPrimitives.kt:50-62,194-202`; `ComposerInputTest.kt:24-59`.
- Directory filter, confirmation, Button8, and Escape: `DirectoryPickerPopup.kt:97-134,154-229`; `DirectoryPickerPopupTest.kt:85-182,184-233`.
- Application-managed text selection is absent; Shift+drag/native terminal selection remains unverified: `TextInputTest.kt:67-81`; `TextInput.kt:311-330`.

## Validation and blockers

- Completed: isolated real CLI recording; frame text captured from tmux; cast header/event/privacy audit; local player frame comparison; truecolor/CJK checks; responsive-width checks.
- Not run: Gradle/`mosaicTest` tests and a source rebuild, because the task explicitly forbids rebuilding the shared `Kodex` build directory. The source/test references above are static inspection, not a fresh test run.
- Not completed: VitePress integration, approved website directory, formal three-language merge, and browser acceptance of the integrated site.
- Not verified: native terminal `Shift+drag` text selection; current-source Settings dropdown interaction in a traceable binary.
