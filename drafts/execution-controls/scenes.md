# Execution-controls scenes and verification record

## Status

- Draft content and state research: **in progress**.
- Formal docs merge, player integration, and browser acceptance: **not done**.
- Real execution-control `.cast`: **not produced**. No fake ANSI or synthetic runtime output was added.
- Reason for the recording block: the approved PTY route can run the existing CLI with an isolated empty Home and no network, but that route has no authenticated/model-safe way to enter a real running turn. Using a personal Home or credentials is out of scope.

## Scene A — Running Composer submission becomes Pending steer

### Intended real recording steps

1. Start Kodex in an isolated Home, isolated tmux socket, isolated port, and a copied CLI.
2. Open a session whose model request is safe to run and whose output is held long enough to keep `execution.running == true`.
3. Type a short, non-sensitive steer in Composer.
4. Submit it while the turn is running.
5. Capture the `Submit to steer` hint, the `Pending steer (1)` preview, and the fact that the current output/tool activity is not falsely shown as immediately cancelled.
6. Wait for the runtime's next steer-delivery boundary and capture the subsequent state.

### Existing fixture entry

- Runtime-level route: [`SteerRuntimeTest.kt:46-65`](../../../Kodex/agent-runtime/decorator/steer/src/commonTest/kotlin/io/github/stream29/kodex/agentruntime/decorator/steer/SteerRuntimeTest.kt#L46-L65) constructs `InMemoryKodexAgentStorage`, `KodexAgentState`, `TestRuntime`, and `steerRuntime`.
- Queue/delivery route: [`SteerRuntimeTest.kt:67-114`](../../../Kodex/agent-runtime/decorator/steer/src/commonTest/kotlin/io/github/stream29/kodex/agentruntime/decorator/steer/SteerRuntimeTest.kt#L67-L114) checks multiple pending inputs and delivery through one logical runtime resume.
- Late delivery route: [`SteerRuntimeTest.kt:116-162`](../../../Kodex/agent-runtime/decorator/steer/src/commonTest/kotlin/io/github/stream29/kodex/agentruntime/decorator/steer/SteerRuntimeTest.kt#L116-L162) adds a steer after a delegation result and verifies another delegation.
- Tool-wait boundary: [`SteerRuntimeTest.kt:305-333`](../../../Kodex/agent-runtime/decorator/steer/src/commonTest/kotlin/io/github/stream29/kodex/agentruntime/decorator/steer/SteerRuntimeTest.kt#L305-L333) verifies that `ToolPending` does not consume the pending input.
- Frontend state/Composer route: [`SessionViewModelTestFixture.kt:17-54`](../../../Kodex/app/view/application/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/app/SessionViewModelTestFixture.kt#L17-L54) and [`SessionViewModelTestRegistry.kt:13-35`](../../../Kodex/app/view/application/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/app/SessionViewModelTestRegistry.kt#L13-L35) create an in-memory session and `AgentRuntimeViewModel`, but do not provide a running model turn or cast export.

### Preparation and validation

- Prepare a seeded `RequestResponse`/running-turn state without changing product code.
- Verify the Composer branch returns `QueuedAsSteer`, `pendingSteer` contains the stable user message, and the preview is rendered by the real `AgentRuntimeScreen`.
- Record only after the state is created by an existing fixture or a separately approved harness.
- Compare each key frame with `tmux capture-pane`; do not hand-write ANSI.

### Blocker

- There is no current checked-in test that mounts `AgentRuntimeScreen` with a running `AgentRuntimeViewModel` and exports its ANSI/PTY frames.
- The existing empty-Home offline CLI cannot prove this online/model behavior.
- Implementing a test exporter or adding a product/test harness is explicitly outside this batch.

## Scene B — Idle submission starts a new turn

### Intended real recording steps

1. Start from an initialized, non-running session with no pending host tool call.
2. Type a new request in Composer.
3. Submit it.
4. Capture the transition from idle/new user message to runtime execution.
5. Do not label this frame as Pending steer.

### Existing fixture entry

- The ViewModel branch is [`AgentRuntimeViewModel.kt:504-525`](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L504-L525).
- The UI calls `submitComposer` from [`AgentRuntimeScreen.kt:181-194`](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/AgentRuntimeScreen.kt#L181-L194).
- In-memory session construction is [`InMemoryKodexSessionRepository.kt:91-125`](../../../Kodex/agent-session/in-memory/src/commonMain/kotlin/io/github/stream29/kodex/agentsession/inmemory/InMemoryKodexSessionRepository.kt#L91-L125); test dependencies use `mockOpenAiClient`, a test model catalog, and no external service at [`TestKodexAgentDependencies.kt:15-32`](../../../Kodex/agent-session/test/src/commonMain/kotlin/io/github/stream29/kodex/agentsession/test/TestKodexAgentDependencies.kt#L15-L32).

### Blocker

- The mock client route can assert state transitions, but no existing full-screen fixture produces a safe real terminal recording.
- The live integration helper reads `CODEX_HOME` and requires auth at [`MinimalAgentConversationTest.kt:254-266`](../../../Kodex/integration-test/src/commonTest/kotlin/io/github/stream29/kodex/integrationtest/MinimalAgentConversationTest.kt#L254-L266); it is not used.

## Scene C — Stop versus Clear pending

### Intended real recording steps

#### Stop

1. Prepare a running turn, ideally with a mock response held open.
2. Confirm the toolbar chooses `Stop` because `canCancel` is true.
3. Press `Stop`.
4. Capture the turn ending and any persisted failed tool result only if the real fixture exposes one.

#### Clear pending

1. Prepare an idle `ToolPending` state with a host-owned pending call.
2. Confirm the toolbar chooses `Clear pending`, not `Stop`.
3. Press `Clear pending`.
4. Capture the state after each pending call is completed as `user interrupt`.

### Existing fixture entry and source baseline

- Control mapping and labels: [`AgentRuntimeControl.kt:5-17`](../../../Kodex/app/view/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeControl.kt#L5-L17), [`RuntimeStatusBar.kt:70-95`](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L70-L95).
- Host-pending state: [`InMemoryKodexSessionRepositoryTest.kt:246-272`](../../../Kodex/agent-session/in-memory/src/commonTest/kotlin/io/github/stream29/kodex/agentsession/inmemory/InMemoryKodexSessionRepositoryTest.kt#L246-L272).
- Cancellation behavior: [`InMemoryKodexSessionRepositoryTest.kt:274-312`](../../../Kodex/agent-session/in-memory/src/commonTest/kotlin/io/github/stream29/kodex/agentsession/inmemory/InMemoryKodexSessionRepositoryTest.kt#L274-L312).
- Direct pending clearing: [`KodexAgentStateImplTest.kt:471-498`](../../../Kodex/agent-state/impl/src/commonTest/kotlin/io/github/stream29/kodex/agentstate/impl/KodexAgentStateImplTest.kt#L471-L498).

### Blocker

- The state tests verify the behavior with mock clients, but there is no existing safe PTY/export route for the corresponding full `AgentRuntimeScreen`.
- Pending steer and pending tool calls are different data paths; a `Clear pending` recording must not be staged with a queued steer and then described as clearing it.

## Scene D — Resume and Compact

### Intended real recording steps

1. Prepare a non-running resumable state such as `UserMessage`, `AssistantMessage`, or `ToolCompleted`.
2. Capture `Resume`, then capture the next runtime phase.
3. From a compactable idle state, capture enabled `Compact`.
4. Trigger it and capture `Compacting`, the returned checkpoint state, and the token baseline after completion.
5. Do not call either action “cancel”.

### Existing fixture entry

- Resume/compact ViewModel calls: [`AgentRuntimeViewModel.kt:232-257`](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L232-L257).
- Compact visibility/capability: [`RuntimeStatusBar.kt:87-94`](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L87-L94) and [`AgentRuntimeViewModel.kt:700-725`](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L700-L725).
- Manual compact fixture: [`KodexAgentCompactionRuntimeTest.kt:344-393`](../../../Kodex/agent-runtime/decorator/compact/src/commonTest/kotlin/io/github/stream29/kodex/agentruntime/decorator/compact/KodexAgentCompactionRuntimeTest.kt#L344-L393).
- Token reset assertion: [`KodexAgentStateImplTest.kt:670-713`](../../../Kodex/agent-state/impl/src/commonTest/kotlin/io/github/stream29/kodex/agentstate/impl/KodexAgentStateImplTest.kt#L670-L713).

### Blocker

- The compaction fixture is state/runtime-level and uses a mock remote compaction response; it is not a full terminal fixture.
- A real compaction recording would require a safe remote model/compaction response or an approved fixture-to-screen bridge. Neither exists in the current scope.

## Scene E — Status token and elapsed time

### Intended real recording steps

1. Use a completed response with a known provider `total_tokens` in a fixture.
2. Capture the status-bar `t` value and record the response usage that produced it.
3. Capture `Worked for ...` only while `runningTurn` is non-null.
4. Capture the stopped/tool-wait state separately; do not extend the label past the running turn.

### Existing fixture entry

- Token persistence is [`KodexAgentStateImpl.kt:215-220`](../../../Kodex/agent-state/impl/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/impl/KodexAgentStateImpl.kt#L215-L220); the model usage shape is [`ResponsesApiModels.kt:511-518`](../../../Kodex/openai/models/src/commonMain/kotlin/io/github/stream29/kodex/openai/ResponsesApiModels.kt#L511-L518).
- Token-window interpretation is [`ContextWindowTokenBudget.kt:16-40`](../../../Kodex/agent-state/context-window/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/contextwindow/ContextWindowTokenBudget.kt#L16-L40).
- Active duration ticker and running-turn boundary are [`AgentHistoryViewModel.kt:111-131`](../../../Kodex/app/viewmodel/history/src/commonMain/kotlin/io/github/stream29/kodex/cli/history/AgentHistoryViewModel.kt#L111-L131).

### Blocker

- The existing mock/state tests can verify numeric persistence, but no approved full-screen export path is available.
- Do not invent a token value, elapsed time, ANSI frame, or model output for the recording directory.

## Verification performed in this batch

### Source and fixture checks

- Kodex source baseline: commit `89205188d5da39f36b983a0bfb57752977feb21a` (`feat: snapshot`).
- Existing CLI binary: `Kodex/app/cli/build/bin/linuxX64/releaseExecutable/kodex-cli.kexe`.
- Existing binary SHA-256: `92539baaa88f4cb78a58ad73c5a23844ef49f65babb4ee968a692c80f26e6720`.
- The binary predates/does not prove every source behavior; the working tree was clean when checked, but the binary's build provenance is not tied to a release build.
- Relevant tests were run sequentially with the existing Gradle daemon JVM (Temurin 25) using:

  ```text
  :agent-runtime-decorator-steer:jvmTest
  :agent-runtime-decorator-compact:jvmTest
  :agent-state-impl:jvmTest
  :app-view-application:jvmTest
  ```

- Result: Gradle `BUILD SUCCESSFUL`; these tests validate runtime/state/control logic, not a real model run or browser rendering.
- The earlier Java 21 Gradle attempt was blocked because this checkout's buildSrc requires JVM 25; the successful run used `/home/stream/.gradle/jdks/eclipse_adoptium-25-amd64-linux.2`.
- No Gradle test exporter, product code, site navigation, theme, or shared build directory was changed for this batch.

### Recording protocol to use once unblocked

- Copy the CLI and `asciinema` into a new task-specific temporary directory.
- Use independent `home/`, `recorder-home/`, `tmux.sock`, and an unused localhost port.
- Clear inherited environment as in [`kodex-terminal-recording.md`](../../../shared-context/findings/kodex-terminal-recording.md), and keep network disabled.
- Start from a fixture that can safely create the target runtime/ViewModel state; never fall back to a personal Home or online account.
- After every key input, save `tmux capture-pane` output and compare it to the player timeline.
- Only after real verification, place the reviewed `.cast` and its manifest under `out/docs-demos/execution-controls/`.

## Next dependency

1. Provide or approve a safe fixture-to-`AgentRuntimeScreen` entry that can hold a model/runtime state without credentials.
2. Decide whether a test-only renderer/exporter is authorized; this batch deliberately did not implement one.
3. Re-record each scene with its own Home, socket, port, and CLI copy.
4. Browser-verify the real player, language switching, text, and narrow-screen behavior after the player task exposes the final mounting path.
