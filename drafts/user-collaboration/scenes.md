# User collaboration scenes

## Scope and baseline

- Draft-only delivery: this file and the three language drafts live under `KodexDocs/drafts/user-collaboration/`; no site route, homepage, navigation, theme, or product code is changed.
- Product baseline checked: Kodex `0.4.3`, `Kodex` HEAD `89205188d5da39f36b983a0bfb57752977feb21a` (`feat: snapshot`, 2026-09-08). The source tree and the existing `KodexDocs` working tree were treated as read-only inputs except for this task's draft directory.
- A scene is marked as **component**, **submission**, or **online behavior** evidence. A component test is not a proof of an online model response; a successful submission is not proof that the resulting work is finished.

## Fixture inventory

### Q1 — multi-question form, Other, and focus

- **Fixture:** `Kodex/app/view/agent/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/agent/RequestUserInputOptionsTest.kt:75-235`.
- **Data:** two questions; the first has `Alpha`/`Beta` and `Other`, and the second has `Beta`. The test first selects `Alpha`, then selects `Other`, types `custom`, and finally selects `Beta`.
- **Component expectation:** option rows render as buttons; selection changes `○` to `●`; `Other` creates a `> ` free-form input; focus moves to the next question after a valid answer and to `Submit` after the last one.
- **Submission expectation:** the fixture's ViewModel is not submitted by a selection alone; the final Enter/Submit action is separate.
- **Source basis:** `AgentRuntimeView.kt:91-131,299-335,369-378`; `RequestUserInputOptionsTest.kt:150-235`.
- **Online boundary:** no online model is used by this Mosaic test.

### Q2 — answer drafts and explicit completion

- **Fixture:** `Kodex/app/viewmodel/agent/src/commonTest/kotlin/io/github/stream29/kodex/cli/agent/RequestUserInputViewModelTest.kt:20-80`.
- **Data:** a pending `request_user_input` call with `Scope`, `Current module`, and `Whole workspace`.
- **Real input steps when a pending form is present:** select `Current module`; inspect the draft; attempt the old revision (expected stale); submit with the current revision.
- **Expected result:** the draft is stored in `RequestUserInputState.Pending`, `canSubmit` becomes true, an old revision returns `StaleRevision`, and only a valid submit completes the tool call. Replacing the call clears the old draft.
- **Source basis:** `RequestUserInputViewModel.kt:37-146,148-187`; contract `RequestUserInputViewModel.kt:41-124`.
- **Evidence type:** submission/ViewModel behavior, not a browser recording.

### Q3 — mode labels and visible-tool boundary

- **Fixture:** `Kodex/app/view/application/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBarTest.kt:35-39,149-194`; configuration fixture in `SuggestedConfigurationTest.kt:29-122`.
- **Real input steps when a configuration dropdown is present:** open the mode trigger; choose `ask user`; reopen it; choose `no question`.
- **Component expectation:** the exact labels are `[ask user]` and `[no question]`; the configuration surface keeps one selected mode.
- **Submission/runtime expectation:** the selected mode is written through the relevant settings ViewModel. `KodexVisibleToolSpecs.kt:50-55` adds the two host-interaction tools only for `AskUser`.
- **Online boundary:** the tests verify labels/configuration and tool-spec selection, not an online model's decision.

### Q4 — Suggested Sessions batch review and rejection

- **Fixture:** `Kodex/app/view/agent/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/agent/SuggestSubagentTaskPanelTest.kt:31-141`.
- **Data:** four tasks named `Task 0`–`Task 3`, each with a long prompt; configuration uses model `test`, low reasoning, default service tier, `.` as cwd, and `ask user`.
- **Real input steps when a pending suggestion panel is present:**
  1. Scroll until the full task text and `Accept`/`Reject` controls can be reviewed.
  2. For acceptance, optionally inspect the batch configuration, then choose `Accept`.
  3. For rejection, choose `Reject`, type an optional message, then press Enter or choose `Submit rejection`.
- **Component expectation:** the panel title is `Suggested Sessions`; names and prompts are shown; `Accept` precedes `Reject`; rejection reveals an optional input.
- **Submission expectation:** Accept submits `accepted = true`; Reject submits `accepted = false`; blank feedback is omitted, while non-blank feedback is carried in the rejected response.
- **Source basis:** `AgentRuntimeView.kt:183-273`; `SuggestSubagentTaskViewModel.kt:36-100`; `SuggestSubagentTaskFeedbackTest.kt:29-85`.
- **Important wording:** acceptance creates ordinary Sessions and submits their prompts, but does not mean the tasks are complete or that results are merged into the current Session.

### Q5 — accepted/rejected history is read-only

- **Fixture:** `Kodex/app/view/history/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/history/SuggestSubagentTaskHistoryViewTest.kt:18-54`.
- **Expected result:** accepted history can show task names, returned Session URIs, full prompts, and `[● Accept]`; rejected history shows `[● Reject]` and optional feedback, without inventing Session URIs.
- **Evidence type:** completed-history component projection, not a live approval surface and not proof of task completion.

## Recording plan and blocker

### Intended safe recording steps

If a future build supplies a safe pending-interaction entry, use the existing isolated route from `shared-context/findings/kodex-terminal-recording.md`:

1. Copy the CLI into a task-local temporary directory; use a task-local Home, recorder Home, tmux socket, and port.
2. Start only with `env -i`, `bwrap`, and a fixture containing the Q1/Q4 data above; do not use a personal Home, account, session, or credentials.
3. Send real keyboard/mouse input for Q1 (`Enter` on an option, `Down`/`Enter` on `Other`, type `custom`, `Enter`, then explicit `Submit`) or Q4 (scroll, review, `Reject`, type feedback, `Submit rejection`).
4. Save only an inspected asciicast and browser verification under `out/docs-demos/user-collaboration/`; record the exact CLI hash, source baseline, terminal size, and verification result.

### Current result: blocked, no recording retained

- The existing CLI entry `Kodex/app/cli/build/bin/linuxX64/releaseExecutable/kodex-cli.kexe` starts the normal application but has no documented fixture/session injection for a pending `request_user_input` or `suggest_subagent_task` call.
- The available pending states are constructed inside Mosaic tests and ViewModel tests (`FakeRequestUserInputViewModel`, `SuggestSubagentTaskState.Pending`, and in-memory repositories); they are not a runnable CLI fixture.
- The closest real runtime probe is `Kodex/integration-test/src/commonTest/kotlin/io/github/stream29/kodex/integrationtest/MinimalAgentConversationTest.kt:794-850`, which uses `realOpenAiClient()` and a real model. Using it would require an online/private account and would not satisfy the safe-recording constraint.
- No fixture-to-terminal exporter exists in the checked sources. Implementing one, modifying the product to add an injection path, or using another user's account/session is out of scope.
- Therefore `out/docs-demos/user-collaboration/` was not created, and no hand-drawn form, fabricated ANSI, or copied unrelated recording is presented as this scene.

## Verification status

- **Static source cross-check:** completed for the listed component, ViewModel, contract, configuration, history, and test fixtures.
- **Runtime tests:** passed against the existing Gradle checkout with `./gradlew -Dorg.gradle.java.home=/home/stream/.gradle/jdks/eclipse_adoptium-25-amd64-linux.2 --no-parallel :app-view-agent:jvmTest :app-view-application:jvmTest :app-viewmodel-agent:jvmTest :app-view-history:jvmTest` (`BUILD SUCCESSFUL`, 347 actionable tasks; 108 executed, 239 up-to-date). This documentation task does not change product code.
- **Browser recording verification:** not applicable because the safe pending-interaction entrance is blocked; the existing `out/kodex-recording-probe/` belongs to another scene and is not reused.
