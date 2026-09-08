# Configuration scope and automatic session titles (first-batch draft)

> This is a manual draft, not an approved site route. The current CLI labels are still the English labels in source.

## Three things to remember

- **Current session** is the open session's snapshot; editing it targets that session only.
- **New-session defaults** are stored globally and copied when a new session draft is created. They do not rewrite every existing session.
- **Automatic session titles** are a separate global setting from the session model, reasoning effort, and service tier.

## Three scopes

| Location | Controls | Takes effect |
| --- | --- | --- |
| `Settings > Current session` | The selected session's model, reasoning effort, service tier, question mode, and working directory | After the session snapshot is updated; subsequent work in that target sees it |
| `Settings > New session` → `Model behavior` | Initial model, reasoning effort, service tier, and question mode for a new-session draft | When the next draft is created; an already-open draft keeps its local values |
| `Settings > New session` → `Title generation` | Automatic-title switch, Title model, and Title reasoning | On the next eligible first text submission; it does not rewrite existing titles |

The global settings model stores `new_session` and `session_title` separately. `new_session` is a default copied into a new thread, not a live binding for every session. Once created, a session keeps its own `KodexAgentSettings`.

## Entering from the status bar

The status bar configuration button shows the target's model, reasoning effort, and the service tier when it is not `default`. Its first menu is nested:

1. **Model**
2. **Reasoning**
3. **Service tier**

The second button is **Questions**, with `ask user` and `no question`. The working-directory button opens the directory picker, and **Settings** on the right opens the settings popup. Both a materialized session and a new-session draft use these entry points. The popup is bound to the target captured when it opens.

Use the status bar for a quick change to the current target. To change the defaults for future sessions, use **New session** in Settings; a status-bar change is not a global-default change.

## Entering from Settings

Select a page on the left:

- **Current session**: edit a materialized session, or inspect the session-level snapshot of the current new-session draft.
- **New session**: edit the global new-session defaults. Its `Model behavior` section exposes model, reasoning, service tier, and Questions.
- **Title generation**: edit the independent automatic-title switch, Title model, and Title reasoning. The controls are rendered on the New session page, but they update global `session_title`, not the draft's model configuration.

Changing a New session default does not turn an already-open draft into a new draft. Draft creation reads the current global value once into `initialSettings`; the draft then has its own ViewModel. The status bar and Current session page edit that draft, not the global default.

## When an automatic title is actually generated

Automatic title generation is not proven by displaying the control. A session is eligible only when:

- an automatic-title configuration is present;
- the title still matches the default `Session N` form;
- the first accepted input contains nonblank text; and
- `Automatic session title` is enabled.

Kodex then starts a separate best-effort title request for that one opportunity. It uses **Title model**; when no model is explicitly configured, the compiled fallback is `gpt-5.3-codex-spark`. Its reasoning effort comes from **Title reasoning**, not the session's `Reasoning` field. Before persisting the result, Kodex checks that the current title is still unchanged.

This is a one-shot auxiliary request. A manual rename invalidates an in-flight result. Disabling the switch, manually naming a session, or submitting no text must not be described as a bulk rewrite of existing sessions.

## How to verify it

- **Control visibility**: use a real CLI recording to inspect the status bar, Settings, New session model behavior, and Title generation controls.
- **Behavior**: inspect persisted settings, or use tests/a mock title generator with assertions for the request model, reasoning effort, one-shot gate, and conditional write-back.
- **Do not conflate them**: an offline settings demo proves only that controls can be displayed and edited. It cannot prove that a live model request generated a title. This first-batch recording does not claim title-generation output.

See [`scenes.md`](./scenes.md) for source and test evidence, recording/build baselines, validation, and blockers.
