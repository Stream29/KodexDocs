# Input During Execution and Runtime Controls (Draft)

> First-batch functional draft. Labels and behavior below follow the current Kodex source. Live model execution, terminal recording, and browser acceptance are not complete.

## Two different submissions

### Submit while running: Pending steer

1. The Agent is running and the Composer contains text.
2. Submission clears the Composer.
3. The text is appended to the runtime's `pendingSteer`; the result is `QueuedAsSteer`.
4. The UI shows `Submit to steer` and a `Pending steer (count)` preview above the Composer.

This is not immediate preemption. The submit path only queues a clean user message. It does not cancel the current Responses request and does not guarantee that an active tool call stops immediately. The runtime takes the queue at steer delivery boundaries: before a delegation and again after an appendable delegation result. If the state is still `ToolPending`, the steer remains queued until tool output makes a delivery boundary possible.

Source:

- [AgentRuntimeViewModel.kt:199-229](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L199-L229)
- [AgentRuntimeScreen.kt:59-75](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/AgentRuntimeScreen.kt#L59-L75), [172-194](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/AgentRuntimeScreen.kt#L172-L194)
- [SteerRuntime.kt:22-49](../../../Kodex/agent-runtime/decorator/steer/src/commonMain/kotlin/io/github/stream29/kodex/agentruntime/decorator/steer/SteerRuntime.kt#L22-L49)

### Submit while idle: a new turn

1. The Agent is not running.
2. The ViewModel calls `appendUserMessage`.
3. It starts a runtime `resume()`; the result is `Submitted`.

An idle submission therefore accepts a new user message and starts execution. It is not a steer for an existing run. The ViewModel rejects the new-turn path while running; the running Composer path is the Pending steer branch.

Source: [AgentRuntimeViewModel.kt:504-525](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L504-L525).

## State-bar controls

The controls are not all forms of cancellation. The current selection order is:

| Condition | Primary button | Actual effect |
| --- | --- | --- |
| `canCancel`: a running turn or a ViewModel-owned runtime operation exists | `Stop` | Cancels the active coroutine; the runtime cancellation path completes unfinished tool calls as `user interrupt`, then restores persisted state |
| Not running and the state is `ToolPending` | `Clear pending` | Fails the currently pending local tool calls one by one; it does not clear already queued Pending steer text or start the model |
| Otherwise | `Resume` | Requests `session.runtime.resume()`; it is a meaningful continuation only when the state capabilities allow it, such as `UserMessage`, `AssistantMessage`, or `ToolCompleted` |

These are distinct transitions:

- `Stop` calls `viewModel.cancel()`, cancelling the running turn and the ViewModel-owned runtime operation.
- `Clear pending` calls `session.runtime.clearPending()`, persisting failed tool results with the text `user interrupt`.
- `Resume` calls `session.runtime.resume()` to continue the persisted state. It is not an undo for Stop and it does not clear a queue.

Implementation:

- [AgentRuntimeControl.kt:5-17](../../../Kodex/app/view/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeControl.kt#L5-L17)
- [RuntimeStatusBar.kt:70-95](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L70-L95), [529-535](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L529-L535)
- [AgentRuntimeViewModel.kt:232-257](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L232-L257)
- [KodexAgentRuntimeComposition.kt:151-173](../../../Kodex/agent-runtime/impl/src/commonMain/kotlin/io/github/stream29/kodex/agentruntime/impl/KodexAgentRuntimeComposition.kt#L151-L173)
- [KodexAgentStateExtensions.kt:51-63](../../../Kodex/agent-state/contract/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/contract/KodexAgentStateExtensions.kt#L51-L63)

One UI nuance matters: `runtimeControl()` falls back to the `Resume` label when neither `canCancel` nor `canClearPending` is true. That must not be documented as “every state can resume.” The actual admissible capabilities are derived in [AgentRuntimeViewModel.kt:700-725](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L700-L725); an empty state is not a resumable existing conversation.

## Compact

`Compact` is context compaction, not cancellation:

- The button is visible when `!execution.running` and enabled only when `canCompact` is true.
- The compactable stable states are `UserMessage`, `AssistantMessage`, and `ToolCompleted`; running, streaming response, `ToolPending`, and `Empty` do not satisfy the condition.
- A manual click calls `forcedCompact()` with `Manual / UserRequested / StandaloneTurn` metadata, performs a remote context-compaction request, and commits a checkpoint.
- After success, the runtime leaves `Compacting`; compaction resets the token-count baseline for the context window. Automatic compaction is separate: the runtime triggers it before or during a turn when the token budget reaches zero.

Source: [RuntimeStatusBar.kt:87-94](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L87-L94), [KodexAgentState.kt:91-108](../../../Kodex/agent-state/contract/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/contract/KodexAgentState.kt#L91-L108), [KodexAgentStateExtensions.kt:41-48](../../../Kodex/agent-state/contract/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/contract/KodexAgentStateExtensions.kt#L41-L48), [KodexAgentCompactionRuntime.kt:38-91](../../../Kodex/agent-runtime/decorator/compact/src/commonMain/kotlin/io/github/stream29/kodex/agentruntime/decorator/compact/KodexAgentCompactionRuntime.kt#L38-L91).

## Status numbers and elapsed time

### `123t`

- `t` is the latest `usage.totalTokens` reported when a model response completes.
- Before provider token usage exists, the value can be unknown. It is not account balance, plan quota, or a local character count.
- Successful `Compact` supplies a synthetic zero baseline for the new context window; the next model response can update it.
- The current status bar shows the count, not a guaranteed remaining-token number. The automatic-compaction threshold also depends on model context metadata and `autoCompactionTokenLimit`.

Source: [RuntimeStatusBar.kt:70-74](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L70-L74), [KodexAgentStateImpl.kt:215-220](../../../Kodex/agent-state/impl/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/impl/KodexAgentStateImpl.kt#L215-L220), [ContextWindowTokenBudget.kt:9-40](../../../Kodex/agent-state/context-window/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/contextwindow/ContextWindowTokenBudget.kt#L9-L40).

### `Worked for Ns`

- The active turn displays `Worked for ...` on the separator above the Composer.
- The duration starts at the active turn's user-message timestamp, updates from the current clock, and is rounded to seconds.
- It is tied to the running turn. After the runtime stops or reaches a host-tool wait, it should not be described as a continuously running network-latency timer.

Source: [AgentRuntimeScreen.kt:64-67](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/AgentRuntimeScreen.kt#L64-L67), [AgentHistoryViewModel.kt:111-131](../../../Kodex/app/viewmodel/history/src/commonMain/kotlin/io/github/stream29/kodex/cli/history/AgentHistoryViewModel.kt#L111-L131), [IndexHistoryRead.kt:213-228](../../../Kodex/app/viewmodel/history/src/commonMain/kotlin/io/github/stream29/kodex/cli/history/IndexHistoryRead.kt#L213-L228), [SessionTreeUiPrimitives.kt:110-123](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeUiPrimitives.kt#L110-L123).

## Scope of this draft

This batch only checks source and mock/in-memory fixtures. It does not use a private account, treat an empty Home/offline CLI as evidence of online model execution, or generate fake ANSI output or a `.cast`. A safe runtime/ViewModel state entry point is still required before recording real execution-control scenes.
