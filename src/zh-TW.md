# Kodex / 快速入門

Kodex 是 Codex 的 Kotlin Multiplatform 實作。
本指南適用於原生 CLI 發行版 v0.4.3。

## 安裝

依作業系統與 CPU 選擇封存檔：

- macOS Apple Silicon：kodex-0.4.3-macos-arm64.tar.gz
- Linux x64：kodex-0.4.3-linux-x64.tar.gz
- Linux ARM64：kodex-0.4.3-linux-arm64.tar.gz
- Windows x64：kodex-0.4.3-windows-x64.zip

下載頁面：
https://github.com/Stream29/Kodex/releases/tag/v0.4.3

這些原生發行版不需要 JVM。此版本沒有 Intel macOS 封存檔。

執行前，計算封存檔的 SHA-256，與同一發行版中的 kodex-0.4.3-SHA256SUMS.txt 對應檔名的值比較。
macOS 使用 `shasum -a 256`，Linux 使用 `sha256sum`，Windows 使用 `Get-FileHash -Algorithm SHA256`。

macOS / Linux：在下載封存檔所在的資料夾執行。
以下以 Linux x64 為例，macOS 或 ARM64 請替換為對應檔名：

```sh
tar -xzf kodex-0.4.3-linux-x64.tar.gz
chmod +x kodex
./kodex
```

Windows / PowerShell：在下載 ZIP 所在的資料夾執行：

```powershell
Expand-Archive -Path .\kodex-0.4.3-windows-x64.zip -DestinationPath .\kodex
.\kodex\kodex.exe
```

選用：將執行檔放在 PATH 中的目錄，即可在專案目錄使用 `kodex` 啟動；否則使用完整路徑。

## 第一次工作階段

1. 在互動式終端中執行解壓縮後的執行檔。
2. 開啟 Settings → OpenAI，將 Authentication 設為 Kodex，再點選 Browser sign-in 下的 Sign in。
   也可以選擇 Codex，使用 Codex CLI 管理的憑證並點選 Reload。
3. 使用 + 開啟新工作階段，確認工作目錄指向你的專案。
4. 選擇可用的模型、推理強度與服務層級。
5. 使用輸入框顯示的送出快捷鍵傳送一個小任務，換行方式可以在設定中調整。

先試一個唯讀請求：

```text
閱讀專案指引，解釋目錄結構。
不要修改任何檔案。建議一個小的後續步驟。
```

Kodex 能執行指令和編輯檔案。請在可信任的專案中使用，保留備份或乾淨的 Git 基準，並檢查變更與測試結果。
提示詞是行為指引，不是安全沙箱。不要把憑證貼到對話中。

## 工作階段與歷史

- Sessions：重新開啟已儲存的對話。
- +：開始新工作階段。
- Close：關閉分頁，不是刪除已儲存的工作階段。
- Fork：從既有歷史開啟獨立對話。
- Archive：封存已完成的工作，使用 Show archived 再次檢視。
- Delete：確認後刪除工作階段。

分支或還原對話狀態前，先檢查歷史與工具詳情。
對話操作不能取代 Git 或檔案備份。

## 設定與工具

- OpenAI：管理驗證、檢視帳號用量，可用模型取決於帳號。
- Context sources：設定專案指引與 skill 來源。專案指引使用 AGENTS.md，skill 使用 SKILL.md。
- MCP：新增可信任的伺服器，或使用 Import from Codex。使用前檢查連線與驗證狀態。
- Hooks：按需設定自訂自動化，啟用前檢查指令內容。

MCP 工具可能存取外部系統，hook 會在你的電腦上執行。
請檢查實際設定，不要假設不同 agent 共用同一個 Home。

## 常見問題

- 找不到指令：
  macOS/Linux 在解壓縮目錄執行 `./kodex`，Windows 執行 `.\kodex.exe`。若要在任意目錄啟動，將所在目錄加入 PATH。
- macOS 阻止啟動：
  確認來源與校驗碼，再依系統安全提示處理。不要關閉系統層級的安全保護。
- 登入沒有完成：
  閱讀登入對話框；瀏覽器未開啟時使用其中的 URL。檢查網路後重試。不要公開回呼 URL 或 token。
- 模型請求失敗：
  檢查驗證、所選模型、帳號用量和網路連線。先閱讀介面錯誤訊息再重試。
- 資料儲存位置：
  Kodex Home 位於 `~/.kodex`，Windows 也在使用者家目錄下。遷移或手動編輯前先備份。目錄可能包含憑證和私人對話，不要整個上傳。

回報問題時，請提供版本、作業系統、終端、重現步驟與去識別化後的錯誤：
https://github.com/Stream29/Kodex/issues
