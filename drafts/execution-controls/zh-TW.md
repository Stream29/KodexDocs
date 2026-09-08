# 執行中的輸入與執行控制（草稿）

> 本頁是首批功能草稿。按鈕文字與行為以目前 Kodex 原始碼為準；真實模型執行、終端錄製與瀏覽器驗收尚未完成。

## 先分清兩種提交

### 執行中提交：Pending steer

1. Agent 正在執行時，在 Composer 輸入文字。
2. 提交後 Composer 會先清空。
3. 內容加入目前 runtime 的 `pendingSteer`，結果是 `QueuedAsSteer`。
4. 介面顯示 `Submit to steer`，並在 Composer 上方顯示 `Pending steer (數量)` 與預覽。

這不是立即搶佔。提交操作只把乾淨的使用者訊息放入待處理佇列；它不會直接取消目前的 Responses 請求，也不能保證目前工具呼叫馬上停止。runtime 只會在允許追加使用者訊息的邊界取走它：進入下一次 delegation 前，以及一次可追加的 delegation 返回後再次檢查。若目前仍是 `ToolPending`，steer 會繼續等待工具輸出。

原始碼依據：

- [AgentRuntimeViewModel.kt:199-229](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L199-L229)
- [AgentRuntimeScreen.kt:59-75](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/AgentRuntimeScreen.kt#L59-L75)、[172-194](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/AgentRuntimeScreen.kt#L172-L194)
- [SteerRuntime.kt:22-49](../../../Kodex/agent-runtime/decorator/steer/src/commonMain/kotlin/io/github/stream29/kodex/agentruntime/decorator/steer/SteerRuntime.kt#L22-L49)

### 閒置提交：新一輪

1. Agent 不在執行中時提交 Composer。
2. ViewModel 呼叫 `appendUserMessage`。
3. 接著啟動一次 runtime `resume()`；結果是 `Submitted`。

因此，閒置提交是接受一則新的使用者訊息並啟動執行，不是給已存在的執行追加 steer。ViewModel 會拒絕在執行中走這條新一輪路徑；執行中的 Composer 提交必須走上面的 Pending steer 分支。

原始碼依據：[AgentRuntimeViewModel.kt:504-525](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L504-L525)。

## 狀態列控制

狀態不是「所有按鈕都等於取消」。目前控制選擇順序如下：

| 目前條件 | 主按鈕 | 實際作用 |
| --- | --- | --- |
| `canCancel` 為真：有 running turn 或 ViewModel 自己的 runtime 操作 | `Stop` | 取消活動協程；runtime 取消路徑會把尚未完成的工具呼叫以 `user interrupt` 完成，然後恢復到持久化狀態 |
| 不在執行，且狀態是 `ToolPending` | `Clear pending` | 逐個失敗目前待處理的本地工具呼叫；不清除 Composer 中已提交的 Pending steer，也不啟動模型 |
| 其他情況 | `Resume` | 要求 runtime 繼續；只有狀態能力允許時才是有效的繼續（例如 `UserMessage`、`AssistantMessage`、`ToolCompleted`） |

`Stop`、`Clear pending`、`Resume` 是三種不同的狀態轉換：

- `Stop` 對應 `viewModel.cancel()`，取消 running turn 與 ViewModel 持有的執行操作。
- `Clear pending` 對應 `session.runtime.clearPending()`，把所有目前待處理工具呼叫寫成失敗結果，失敗文字為 `user interrupt`。
- `Resume` 對應 `session.runtime.resume()`，繼續目前已持久化的狀態；它不是「撤銷 Stop」或「清掉佇列」。

實作細節：

- [AgentRuntimeControl.kt:5-17](../../../Kodex/app/view/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeControl.kt#L5-L17)
- [RuntimeStatusBar.kt:70-95](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L70-L95)、[529-535](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L529-L535)
- [AgentRuntimeViewModel.kt:232-257](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L232-L257)
- [KodexAgentRuntimeComposition.kt:151-173](../../../Kodex/agent-runtime/impl/src/commonMain/kotlin/io/github/stream29/kodex/agentruntime/impl/KodexAgentRuntimeComposition.kt#L151-L173)
- [KodexAgentStateExtensions.kt:51-63](../../../Kodex/agent-state/contract/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/contract/KodexAgentStateExtensions.kt#L51-L63)

容易誤讀的一點：`runtimeControl()` 在沒有 `canCancel`、`canClearPending` 時回退顯示 `Resume`；這不應寫成「任何狀態都能恢復」。實際合法能力由 [AgentRuntimeViewModel.kt:700-725](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L700-L725) 決定，空狀態並不是已有對話的可恢復執行。

## Compact

`Compact` 是上下文壓縮，不是取消：

- 按鈕在 `!execution.running` 時可見；只有 `canCompact` 為真時啟用。
- 可壓縮狀態是穩定的 `UserMessage`、`AssistantMessage` 或 `ToolCompleted`；執行中、串流回應中、`ToolPending` 和 `Empty` 不符合條件。
- 手動點擊呼叫 `forcedCompact()`，使用 `Manual / UserRequested / StandaloneTurn` 元資料，發起一次遠端上下文壓縮並提交 checkpoint。
- 成功壓縮後，runtime 從 `Compacting` 恢復；壓縮會重設目前上下文的 token 計數基線。自動壓縮是另一條路徑：runtime 在回合開始或回合中發現 token 預算到零時按上下文限制觸發。

原始碼依據：[RuntimeStatusBar.kt:87-94](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L87-L94)、[KodexAgentState.kt:91-108](../../../Kodex/agent-state/contract/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/contract/KodexAgentState.kt#L91-L108)、[KodexAgentStateExtensions.kt:41-48](../../../Kodex/agent-state/contract/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/contract/KodexAgentStateExtensions.kt#L41-L48)、[KodexAgentCompactionRuntime.kt:38-91](../../../Kodex/agent-runtime/decorator/compact/src/commonMain/kotlin/io/github/stream29/kodex/agentruntime/decorator/compact/KodexAgentCompactionRuntime.kt#L38-L91)。

## 狀態列數字與耗時

### `123t`

- 狀態列的 `t` 是最近一次模型完成回應報告的 `usage.totalTokens`。
- 初始沒有 provider token usage 時可以未知，不應解釋為帳號餘額、方案配額或本地字元數。
- `Compact` 成功後，儲存層為新的上下文視窗提供合成的零值基線；下一次模型回應報告後再更新。
- 目前狀態列只顯示 token 數，不顯示「保證還剩多少 token」；自動壓縮閾值還要結合模型上下文視窗與 `autoCompactionTokenLimit` 設定。

原始碼依據：[RuntimeStatusBar.kt:70-74](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L70-L74)、[KodexAgentStateImpl.kt:215-220](../../../Kodex/agent-state/impl/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/impl/KodexAgentStateImpl.kt#L215-L220)、[ContextWindowTokenBudget.kt:9-40](../../../Kodex/agent-state/context-window/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/contextwindow/ContextWindowTokenBudget.kt#L9-L40)。

### `Worked for Ns`

- 執行中的回合在 Composer 分隔線顯示 `Worked for ...`。
- 計時從目前活動回合的使用者訊息時間戳開始，依目前時鐘更新，並四捨五入到秒。
- 計時綁定 running turn；runtime 停止或回到等待宿主工具輸出後，不應把它當成持續的網路耗時計數器。

原始碼依據：[AgentRuntimeScreen.kt:64-67](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/AgentRuntimeScreen.kt#L64-L67)、[AgentHistoryViewModel.kt:111-131](../../../Kodex/app/viewmodel/history/src/commonMain/kotlin/io/github/stream29/kodex/cli/history/AgentHistoryViewModel.kt#L111-L131)、[IndexHistoryRead.kt:213-228](../../../Kodex/app/viewmodel/history/src/commonMain/kotlin/io/github/stream29/kodex/cli/history/IndexHistoryRead.kt#L213-L228)、[SessionTreeUiPrimitives.kt:110-123](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeUiPrimitives.kt#L110-L123)。

## 本批草稿邊界

本批只核對原始碼與 mock/in-memory fixture。沒有使用私人帳號，沒有把空 Home 的禁網 CLI 啟動當成線上模型執行證據，也沒有產生偽造 ANSI 或 `.cast`。真實執行控制錄製仍需要可安全播放的 runtime/ViewModel 狀態入口。
