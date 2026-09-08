# 輸入編輯與目錄導覽

> 草稿：網站目錄與播放器接入尚未確認。本頁只記錄已核對的功能、真實終端演示與邊界。

## 輸入編輯

Kodex 的 Composer 是終端輸入框，不會把畫面上的折行寫成文字換行。

1. 聚焦輸入框。
2. 貼上包含中文、英文、數字與多行內容的文字。
3. 在較窄的輸入區域中，長行會按照終端 cell 寬度軟換行；貼上內容中的 `CRLF` / `CR` 會規範化為 `LF`。
4. 用方向鍵移動游標，再繼續編輯。游標位置映射到原始文字邊界，中文等寬字元按終端 cell 計算。

軟換行只是顯示布局：它不會在文字中插入 `\n`。真正的換行由目前設定的換行鍵產生。預設是 `Shift+Enter` 換行、`Enter` 提交；也可以把換行改為 `Enter`，此時提交鍵會成對改為 `Ctrl+Enter`。文案與演示不應把某一個組合說成永遠固定的提交鍵。

### 編輯歷史

- `Ctrl+W` 刪除游標前的一個詞組；詞、空白與標點按照輸入元件的分組規則處理。
- `Ctrl+Z` 復原最近的編輯交易，`Ctrl+Y` 重做。
- 一次貼上作為原子編輯處理；連續輸入與刪除按元件的歷史合併規則記錄。

原始碼與測試依據：

- `Kodex/app/view/components/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/components/TextInput.kt:102-156,221-305`
- `Kodex/app/view/components/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/components/TextInputTest.kt:83-103,181-249,251-364,366-395`
- `Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeUiPrimitives.kt:31-70,194-202`
- `Kodex/app/shared/settings/contract/src/commonMain/kotlin/io/github/stream29/kodex/cli/settings/KodexGlobalSettings.kt:124-147`
- `Kodex/app/view/application/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/app/ComposerInputTest.kt:24-59,89-127`

## 目錄選擇

從設定中的工作目錄入口打開選擇器後：

1. 直接輸入字母過濾目前目錄的子目錄；過濾不分大小寫，檔案不會顯示為可選目錄。
2. `Enter` 進入過濾結果的首項；再次按 `Enter` 確認目前目錄。也可以聚焦 `[Select]` 按鈕確認。
3. 滑鼠 `Button8` 返回父目錄，同時清除過濾條件。
4. `Escape` 分層處理：有過濾時先清除過濾；再次按下關閉目錄彈層；若設定仍開啟，再按一次關閉設定。

`Button8` 是真實終端滑鼠事件，不是播放器中的文字選取。播放器選字也不能證明真實終端的 `Shift+拖曳` 選取；本批尚未驗證終端原生文字選取，因此不把它寫成已支援的 Kodex 應用功能。

原始碼與測試依據：

- `Kodex/app/view/path-picker/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/pathpicker/DirectoryPickerPopup.kt:46-134,154-229`
- `Kodex/app/contract/path-picker/src/commonMain/kotlin/io/github/stream29/kodex/app/pathpicker/contract/DirectoryPickerState.kt:67-91`
- `Kodex/app/viewmodel/path-picker/src/commonMain/kotlin/io/github/stream29/kodex/app/pathpicker/DirectoryPickerViewModel.kt:45-88`
- `Kodex/app/view/path-picker/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/pathpicker/DirectoryPickerPopupTest.kt:31-182,184-233`

## 演示邊界

本批真實演示使用 **原生 CLI → asciinema → asciinema-player**，不是模擬 TUI，也不是網頁端線上操作。錄製採用獨立臨時 Home、tmux socket、CLI 副本與無網路沙箱。正式內容仍需在確認後的目錄合入；目前草稿不代表 Pages 已接入。
