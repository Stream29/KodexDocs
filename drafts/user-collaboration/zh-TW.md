# 提問表單與建議會話審批（草稿）

> 這是首批內容草稿，不是已批准的網站頁面。以下行為按 Kodex `0.4.3` 原始碼基線核對；線上模型實際提出什麼問題，仍取決於模型、服務與目前執行狀態。

## 回答 Agent 的問題

當 Agent 停在 `request_user_input` 時，工作區會顯示問題、選項與必要的自由輸入，而不是把問題當成一般 Composer 文字。

1. 第一題的第一個選項會取得焦點。
2. 選取選項後，答案先寫入目前互動的草稿，焦點會前進到下一題；最後一題之後焦點前進到 `Submit`。
3. 有選項的題目會顯示 `Other`。選取後會出現自由輸入框並取得焦點；輸入非空文字後，按 Enter 才會前進到下一題。空白文字不能成為有效答案。
4. 沒有選項的題目會直接顯示自由輸入框。
5. 即使所有題目都有答案，仍要明確選取 `Submit`。提交前的選項與文字只是目前 pending call 的答案草稿；成功提交後 Kodex 才完成工具呼叫並恢復 Agent。

如果 pending call 被替換，舊 call 的草稿不會帶到新問題。提交會用 call id 與 revision 驗證，過期的前端事件不會修改另一組問題。

## `ask user` 與 `no question`

狀態列與下拉選單使用兩個明確標籤：`ask user` 與 `no question`。原始碼沒有另外的第三種提問模式。

- `ask user` 會把 `request_user_input` 與 `suggest_subagent_task` 加入目前 Agent 可見的工具集合。
- `no question` 不會加入這兩個工具；這不是「線上自動替你完成所有選擇」的承諾。
- 在建議會話的接受前設定中，也可以選擇這兩個標籤；那是這一批新 Session 的設定，不是逐項建議各自設定。

## 審核 Suggested Sessions

建議面板標題為 `Suggested Sessions`，按批次顯示每項建議的名稱與**完整任務提示**。提示很長時，請在面板內捲動查看，不要只根據名稱批准。

接受前，先檢查這一批共用的設定：

- model
- reasoning effort
- service tier
- `ask user` / `no question`
- working directory（`cwd`）

然後選擇：

- `Accept`：提交這一批建議。應用程式會為每項建議建立普通的新 Session，並把對應提示提交給它。
- `Reject`：展開可選的意見輸入；意見可以留白，再按 Enter 或選取 `Submit rejection` 提交拒絕。

`Accept` 只表示使用者批准建立並啟動這批建議的 Session；它不表示任務已經完成，也不表示結果已自動合併到目前 Session。建立後的執行、失敗、輸出與後續審查仍要分別查看。

## 事實邊界與依據

- 元件顯示與焦點：`Kodex/app/view/agent/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeView.kt:47-180,276-433`
- 提問狀態、答案草稿、明確提交與 revision：`Kodex/app/contract/agent/src/commonMain/kotlin/io/github/stream29/kodex/app/agent/contract/RequestUserInputViewModel.kt:7-141`、`Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/RequestUserInputViewModel.kt:37-146`
- 兩種模式的顯示標籤：`Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeUiPrimitives.kt:128-141`
- 模式對可見工具的影響：`Kodex/agent-state/tool/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/tool/KodexVisibleToolSpecs.kt:50-55`
- 建議批次設定與應用程式入口：`Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/AgentRuntimeScreen.kt:146-169`、`Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt:177-189,402-479`
- 建議提交結果、可選拒絕意見：`Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/SuggestSubagentTaskViewModel.kt:36-100`
- 接受後的 Session 建立與提示提交：`Kodex/app/viewmodel/application/src/commonMain/kotlin/io/github/stream29/kodex/cli/app/ApplicationViewModel.kt:145-187`
