# 提问表单与建议会话审批（草稿）

> 这是首批内容草稿，不是已批准的网站页面。以下行为按 Kodex `0.4.3` 源码基线核对；在线模型实际提出什么问题，仍取决于模型、服务和当前运行状态。

## 回答 Agent 的问题

当 Agent 暂停在 `request_user_input` 时，工作区显示问题、选项和必要的自由输入，而不是把问题当作普通 Composer 文本。

1. 第一个问题的第一个选项会获得焦点。
2. 选中一个选项后，答案先写入当前交互的草稿，并把焦点推进到下一题；最后一题之后焦点推进到 `Submit`。
3. 题目有选项时会显示 `Other`。选中它会出现自由输入框并取得焦点；输入非空文字后，按 Enter 才会继续到下一题。空白文字不能作为有效答案。
4. 没有选项的题目直接显示自由输入框。
5. 即使所有题目已有答案，也要显式选择 `Submit`。提交前的选项和文字只是当前 pending call 的答案草稿；成功提交后 Kodex 才完成工具调用并恢复 Agent。

如果 pending call 被替换，旧 call 的草稿不会带到新问题。提交使用 call id 和 revision 校验，过期的前端事件不会修改另一组问题。

## `ask user` 与 `no question`

状态栏和下拉菜单使用两个明确的标签：`ask user` 与 `no question`。源码没有另外的第三种提问模式。

- `ask user` 会把 `request_user_input` 和 `suggest_subagent_task` 加入当前 Agent 可见的工具集合。
- `no question` 不加入这两个工具；它不是“自动替你完成所有选择”的在线结果承诺。
- 在建议会话的接受前配置中，也可以选择这两个标签；那是这一批新 Session 的设置，不是逐条建议分别设置。

## 审核 Suggested Sessions

建议面板标题为 `Suggested Sessions`，按批次展示每项建议的名称和**完整任务提示**。提示很长时在面板内滚动查看，不要只根据名称批准。

接受前，先检查这一批共用的配置：

- model
- reasoning effort
- service tier
- `ask user` / `no question`
- working directory（`cwd`）

然后选择：

- `Accept`：提交这一批建议。应用为每个建议创建普通的新 Session，并把对应提示提交给它。
- `Reject`：展开可选反馈输入；反馈可以留空，按 Enter 或选择 `Submit rejection` 提交拒绝。

`Accept` 只表示用户批准创建并启动这批建议的 Session；它不表示任务已经完成，也不表示结果已自动合并到当前 Session。创建后的执行、失败、输出和后续审查仍要分别查看。

## 事实边界与依据

- 组件显示与焦点：`Kodex/app/view/agent/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeView.kt:47-180,276-433`
- 提问状态、答案草稿、显式提交与 revision：`Kodex/app/contract/agent/src/commonMain/kotlin/io/github/stream29/kodex/app/agent/contract/RequestUserInputViewModel.kt:7-141`、`Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/RequestUserInputViewModel.kt:37-146`
- 两种模式的显示标签：`Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeUiPrimitives.kt:128-141`
- 模式对可见工具的影响：`Kodex/agent-state/tool/src/commonMain/kotlin/io/github/stream29/kodex/agentstate/tool/KodexVisibleToolSpecs.kt:50-55`
- 建议批次配置与应用入口：`Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/AgentRuntimeScreen.kt:146-169`、`Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt:177-189,402-479`
- 建议提交结果、可选拒绝反馈：`Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/SuggestSubagentTaskViewModel.kt:36-100`
- 接受后的 Session 创建与提示提交：`Kodex/app/viewmodel/application/src/commonMain/kotlin/io/github/stream29/kodex/cli/app/ApplicationViewModel.kt:145-187`
