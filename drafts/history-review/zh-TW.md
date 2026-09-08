# 閱讀歷史、分支與執行結果（草稿）

> 首批草稿；目錄尚未核准。內容以 Kodex `0.4.3` 原始碼與現有測試為準，不是錄製成片。

## 先看懂歷史位置

- 歷史以反向列表顯示，最新項目在底部；預設會跟隨最新內容。
- 向上捲動閱讀舊項目後，位置會保持；新內容不會強制把視角拉回底部。
- 分隔線出現 `[↓]` 時，按下即可回到底部並恢復跟隨最新內容。
- 歷史視窗會按需載入較舊或較新的頁面；載入時保留目前可見項目的位置。
- 一筆記錄可能是訊息、`Take N actions` 工作組、工具摘要、Patch 或計畫；先讀摘要，再按需展開。

## 展開項目與閱讀結果

- 一般工具折疊時顯示給人的摘要，例如 `Run: pwd`；原始工具名稱、參數和結果在展開後分層查看。
- 工具結果保留真實狀態：執行中、完成或失敗由介面狀態／顏色表達；不要把失敗項目寫成成功示例。
- 在具體歷史項目按右鍵可開啟歷史操作選單；選單只對目前仍在視窗中的項目有效。
- Patch 使用專用檢視：
  1. 展開項目查看 `Tool: apply_patch`；
  2. 展開 `Changes` 查看檔案及增刪行；
  3. 大型 Patch 初始只顯示一頁，按 `Show next 200 lines` 繼續查看，並顯示剩餘行數。
- `update_plan` 不是原始 JSON，而是清單：`[ ]` 待處理、`[>]` 進行中、`[x]` 已完成。

## Fork from here 與 Revert to here

- 只有 Agent 已停止、歷史能力可用，而且所選項目仍屬於目前歷史代時，項目選單才會提供 `Fork from here` / `Revert to here`。
- `Fork from here` 會在所選邊界建立新的持久工作階段，標題帶有 `[fork]`，並開啟新工作階段；來源工作階段不會被刪除。
- `Revert to here` 先開啟確認框：
  - 保留所選歷史項目；
  - 刪除該項目之後的歷史；
  - 明確顯示 `This cannot be undone.`；
  - `Cancel` 不改變歷史，`Revert` 才會開始非同步回退。
- 這裡的回退只修改 Kodex 工作階段歷史與待處理 steer，不是工作目錄檔案回滾，也不是 Git 回滾；演示不得暗示檔案內容會跟著歷史恢復。
- 工作台歷史索引的 `Check out` 是定位：只要求捲動到某個歷史項目，與按項目 Fork/Revert 的分支或破壞性歷史變更不同。

## 演示邊界

- 真實演示必須使用獨立且可丟棄的 Home、tmux socket、連接埠與 CLI 副本；不讀取或修改個人工作階段。
- 結果演示只能使用真實成功／失敗記錄，不能把測試斷言或手寫文字當作成功結果。
- 目前只完成隔離 CLI 啟動預檢，畫面只有工作階段入口和空的新工作階段，尚未錄製歷史操作；沒有 CLI 可匯入的安全歷史／工具結果 fixture，因此不產生 `.cast`。

## 原始碼依據（目前工作樹）

- 歷史位置與 `[↓]`：`Kodex/app/viewmodel/history/src/commonMain/kotlin/io/github/stream29/kodex/cli/history/AgentHistoryViewModel.kt:95-215,376-819`、`Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeUiPrimitives.kt:75-108`。
- 歷史列表、展開與右鍵入口：`Kodex/app/view/history/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/history/AgentHistoryView.kt:102-188,315-414`。
- 狀態限制、確認與不可撤銷文字：`Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeCliScreen.kt:1372-1498`、`Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt:305-414,700-738`。
- Fork 的新工作階段邊界：`Kodex/app/viewmodel/session/src/commonMain/kotlin/io/github/stream29/kodex/cli/session/SessionViewModels.kt:301-363`。
- Patch 分層與更多行：`Kodex/app/view/patch/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/patch/PatchToolEventView.kt:83-225`。
- 計畫標記：`Kodex/app/view/history/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/history/PlanUpdateView.kt:36-68`。
