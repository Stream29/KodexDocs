# 运行中输入与执行控制（草稿）

> 本页是首批功能草稿。按钮文字和行为以当前 Kodex 源码为准；真实模型运行、终端录制和浏览器验收尚未完成。

## 先分清两种提交

### 运行中提交：Pending steer

1. 当前 Agent 正在运行时，在 Composer 输入文字。
2. 提交后，Composer 会先清空。
3. 内容加入当前 runtime 的 `pendingSteer`，结果是 `QueuedAsSteer`。
4. 界面显示 `Submit to steer`，并在 Composer 上方显示 `Pending steer (数量)` 与预览。

这不是立即抢占。提交操作只把干净的用户消息放入待处理队列；它不会直接取消当前 Responses 请求，也不能保证当前工具调用马上停止。runtime 在允许追加用户消息的边界取走它：进入下一次 delegation 前，以及一次可追加的 delegation 返回后再次检查。若当前仍是 `ToolPending`，steer 会继续等待工具输出。

源码依据：

- [AgentRuntimeViewModel.kt:199-229](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L199-L229)
- [AgentRuntimeScreen.kt:59-75](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/AgentRuntimeScreen.kt#L59-L75)、[172-194](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/AgentRuntimeScreen.kt#L172-L194)
- [SteerRuntime.kt:22-49](../../../Kodex/agent-runtime/decorator/steer/src/commonMain/kotlin/io/github/stream29/kodex/agentruntime/decorator/steer/SteerRuntime.kt#L22-L49)

### 空闲提交：新一轮

1. Agent 不在运行中时提交 Composer。
2. ViewModel 调用 `appendUserMessage`。
3. 随后启动一次 runtime `resume()`；结果是 `Submitted`。

因此，空闲提交是接受一条新的用户消息并启动运行，不是给已经存在的运行追加 steer。ViewModel 会拒绝在运行中走这条新一轮路径；运行中的 Composer 提交必须走上面的 Pending steer 分支。

源码依据：[AgentRuntimeViewModel.kt:504-525](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L504-L525)。

## 状态栏控制

状态不是“所有按钮都等于取消”。当前控制选择顺序是：

| 当前条件 | 主按钮 | 实际作用 |
| --- | --- | --- |
| `canCancel` 为真：有 running turn 或 ViewModel 自己的 runtime 操作 | `Stop` | 取消活动协程；runtime 取消路径会把仍未完成的工具调用以 `user interrupt` 完成，然后恢复到持久化状态 |
| 不在运行，且状态是 `ToolPending` | `Clear pending` | 逐个失败当前待处理的本地工具调用；不清除 Composer 中已提交的 Pending steer，也不启动模型 |
| 其他情况 | `Resume` | 请求 runtime 继续；只有状态能力允许时才是有效的继续（`UserMessage`、`AssistantMessage`、`ToolCompleted` 等） |

`Stop`、`Clear pending`、`Resume` 是三个不同的状态转换：

- `Stop` 对应 `viewModel.cancel()`，取消 running turn 和 ViewModel 持有的运行操作。
- `Clear pending` 对应 `session.runtime.clearPending()`，把所有当前待处理工具调用写成失败结果，失败文本为 `user interrupt`。
- `Resume` 对应 `session.runtime.resume()`，继续当前已持久化的状态；它不是“撤销 Stop”或“清掉队列”。

实现细节：

- [AgentRuntimeControl.kt:5-17](../../../Kodex/app/view/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeControl.kt#L5-L17)
- [RuntimeStatusBar.kt:70-95](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L70-L95)、[529-535](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L529-L535)
- [AgentRuntimeViewModel.kt:232-257](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L232-L257)
- [KodexAgentRuntimeComposition.kt:151-173](../../../Kodex/agent-runtime/impl/src/commonMain/kotlin/io/github/stream29/kodex/agentruntime/impl/KodexAgentRuntimeComposition.kt#L151-L173)
- [KodexAgentStateExtensions.kt:51-63](../../../Kodex/agent-state/contract/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/contract/KodexAgentStateExtensions.kt#L51-L63)

一个容易误读的边界：主按钮的 `runtimeControl()` 在没有 `canCancel`、`canClearPending` 时回退显示 `Resume`；这不应被写成“任何状态都能恢复”。实际合法能力由 [AgentRuntimeViewModel.kt:700-725](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L700-L725) 决定，空状态并不是已有对话的可恢复运行。

## Compact

`Compact` 是上下文压缩，不是取消：

- 按钮在 `!execution.running` 时可见；只有 `canCompact` 为真时启用。
- 可压缩状态是稳定的 `UserMessage`、`AssistantMessage` 或 `ToolCompleted`；运行中、请求流式响应中、`ToolPending` 和 `Empty` 不满足这个条件。
- 手动点击调用 `forcedCompact()`，使用 `Manual / UserRequested / StandaloneTurn` 元数据，发起一次远端上下文压缩并提交 checkpoint。
- 成功压缩后，runtime 从 `Compacting` 恢复；压缩会重置当前上下文的 token 计数基线。自动压缩是另一条路径：runtime 在回合开始或回合中发现 token 预算到零时按上下文限制触发。

源码依据：[RuntimeStatusBar.kt:87-94](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L87-L94)、[KodexAgentState.kt:91-108](../../../Kodex/agent-state/contract/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/contract/KodexAgentState.kt#L91-L108)、[KodexAgentStateExtensions.kt:41-48](../../../Kodex/agent-state/contract/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/contract/KodexAgentStateExtensions.kt#L41-L48)、[KodexAgentCompactionRuntime.kt:38-91](../../../Kodex/agent-runtime/decorator/compact/src/commonMain/kotlin/io/github/stream29/kodex/agentruntime/decorator/compact/KodexAgentCompactionRuntime.kt#L38-L91)。

## 状态栏数字与耗时

### `123t`

- 状态栏的 `t` 是最近一次模型完成响应报告的 `usage.totalTokens`。
- 初始没有 provider token usage 时可以是未知，不应解释为账号余额、套餐配额或本地字符数。
- `Compact` 成功后，存储层为新的上下文窗口提供合成的零值基线；下一次模型响应报告后再更新。
- 当前状态栏只显示 token 数，不显示“保证还剩多少 token”；自动压缩阈值还要结合模型上下文窗口和配置的 `autoCompactionTokenLimit`。

源码依据：[RuntimeStatusBar.kt:70-74](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L70-L74)、[KodexAgentStateImpl.kt:215-220](../../../Kodex/agent-state/impl/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/impl/KodexAgentStateImpl.kt#L215-L220)、[ContextWindowTokenBudget.kt:9-40](../../../Kodex/agent-state/context-window/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/contextwindow/ContextWindowTokenBudget.kt#L9-L40)。

### `Worked for Ns`

- 运行中的回合在 Composer 分隔线显示 `Worked for ...`。
- 计时从当前活动回合的用户消息时间戳开始，依据当前时钟刷新，并四舍五入到秒。
- 计时绑定 running turn；runtime 停止或回到等待宿主工具输出后，不应把它当成持续的网络耗时计数器。

源码依据：[AgentRuntimeScreen.kt:64-67](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/AgentRuntimeScreen.kt#L64-L67)、[AgentHistoryViewModel.kt:111-131](../../../Kodex/app/viewmodel/history/src/commonMain/kotlin/io/github/stream29/kodex/cli/history/AgentHistoryViewModel.kt#L111-L131)、[IndexHistoryRead.kt:213-228](../../../Kodex/app/viewmodel/history/src/commonMain/kotlin/io/github/stream29/kodex/cli/history/IndexHistoryRead.kt#L213-L228)、[SessionTreeUiPrimitives.kt:110-123](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeUiPrimitives.kt#L110-L123)。

## 当前草稿边界

本批只核对源码和 mock/in-memory fixture。没有使用私人账号，没有把空 Home 的禁网 CLI 启动当成在线模型运行证据，也没有生成伪造 ANSI 或 `.cast`。真实运行控制录制需先有可安全播出的 runtime/ViewModel 状态入口。
