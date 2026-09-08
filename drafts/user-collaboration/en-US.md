# User collaboration: questions and suggested Sessions (draft)

> This is first-batch content, not an approved website page. The behavior below was checked against the Kodex `0.4.3` source baseline. What an online model actually asks still depends on the model, service, and current runtime state.

## Answering an Agent question

When an Agent is paused at `request_user_input`, the workspace renders the questions, choices, and any required free-form input instead of treating the question as ordinary Composer text.

1. The first option of the first question receives focus.
2. Selecting an option stores an answer draft for this interaction and advances focus to the next question; after the last question, focus advances to `Submit`.
3. A question with options shows `Other`. Selecting it reveals a free-form input and focuses it. Enter advances only after non-blank text has been entered; blank text is not a valid answer.
4. A question with no options renders a free-form input directly.
5. Even when every question has an answer, choose `Submit` explicitly. Until submission, choices and text are only drafts for the current pending call; a successful submission completes the tool call and resumes the Agent.

If the pending call is replaced, drafts from the old call are discarded. Submission is checked against the call id and revision, so a stale frontend event cannot edit a different question set.

## `ask user` and `no question`

The status bar and dropdown use two explicit labels: `ask user` and `no question`. The source does not define another question mode.

- `ask user` adds `request_user_input` and `suggest_subagent_task` to the tools visible to the current Agent.
- `no question` does not add those two tools. It is not a promise that an online model will automatically make every choice for the user.
- The suggested-Session approval surface can also choose either label. That setting applies to the batch of new Sessions, not separately to each suggested item.

## Reviewing Suggested Sessions

The panel is headed `Suggested Sessions`. It shows every suggested item's name and its **full task prompt**. Scroll through a long panel before deciding; do not approve from names alone.

Before accepting, inspect the shared batch configuration:

- model
- reasoning effort
- service tier
- `ask user` / `no question`
- working directory (`cwd`)

Then choose:

- `Accept`: submit the batch. The application creates an ordinary new Session for each suggestion and submits that item's prompt to it.
- `Reject`: reveal optional feedback. Feedback may be empty; press Enter or choose `Submit rejection` to submit the rejection.

`Accept` means that the user approved creating and starting the suggested Sessions. It does **not** mean the tasks are complete, and it does **not** mean their results are automatically merged into the current Session. Inspect execution, failures, output, and follow-up review separately.

## Evidence and boundaries

- Component rendering and focus: `Kodex/app/view/agent/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeView.kt:47-180,276-433`
- Question state, answer drafts, explicit submission, and revisions: `Kodex/app/contract/agent/src/commonMain/kotlin/io/github/stream29/kodex/app/agent/contract/RequestUserInputViewModel.kt:7-141` and `Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/RequestUserInputViewModel.kt:37-146`
- Mode labels: `Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeUiPrimitives.kt:128-141`
- Mode effect on visible tools: `Kodex/agent-state/tool/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/tool/KodexVisibleToolSpecs.kt:50-55`
- Suggested-batch configuration and placement: `Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/AgentRuntimeScreen.kt:146-169` and `Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt:177-189,402-479`
- Suggestion submission and optional rejection feedback: `Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/SuggestSubagentTaskViewModel.kt:36-100`
- Session creation and prompt submission after acceptance: `Kodex/app/viewmodel/application/src/commonMain/kotlin/io/github/stream29/kodex/cli/app/ApplicationViewModel.kt:145-187`
