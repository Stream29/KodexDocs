# 阅读历史、分支与执行结果（草稿）

> 首批草稿；目录尚未批准。内容以 Kodex `0.4.3` 源码和现有测试为准，不是录制成片。

## 先把历史位置看懂

- 历史按反向列表显示，最新条目在底部；默认跟随最新内容。
- 向上滚动阅读旧条目后，位置会保持，新增内容不会把阅读位置强行拉回底部。
- 分隔线中出现 `[↓]` 时，点击它回到底部并恢复跟随最新内容。
- 历史窗口按需加载旧/新页；加载页会保留当前可见条目的位置。
- 一条记录可能是消息、`Take N actions` 工作组、工具摘要、Patch 或计划；先看摘要，再按需展开。

## 展开条目和阅读结果

- 普通工具条目折叠时显示面向人的摘要，例如 `Run: pwd`；原始工具名、参数和结果在展开后分层查看。
- 工具结果显示真实状态：运行中、完成或失败由界面状态/颜色表达；不要把失败条目写成成功示例。
- 右键具体历史条目可进入历史操作菜单；菜单只作用于当前仍在窗口中的条目。
- Patch 使用专用视图：
  1. 展开条目查看 `Tool: apply_patch`；
  2. 展开 `Changes` 查看文件及增删行；
  3. 大 Patch 初始只显示一页，点击 `Show next 200 lines` 继续查看，并显示剩余行数。
- `update_plan` 不是原始 JSON，而是清单：`[ ]` 待处理、`[>]` 进行中、`[x]` 已完成。

## Fork from here 与 Revert to here

- 只有 Agent 已停止、历史能力可用且所选条目仍属于当前历史代时，条目菜单才提供 `Fork from here` / `Revert to here`。
- `Fork from here` 在所选边界创建新的持久会话，标题带 `[fork]`，并打开新会话；源会话不被删除。
- `Revert to here` 先打开确认框：
  - 保留所选条目；
  - 删除该条目之后的历史；
  - 明确显示 `This cannot be undone.`；
  - `Cancel` 不改变历史，`Revert` 才开始异步回退。
- 这里的回退只改 Kodex 的会话历史和待处理 steer，不是工作目录文件回滚，也不是 Git 回滚；文档演示不得暗示文件内容随历史一起恢复。
- 工作台历史索引的 `Check out` 是定位：它只请求滚动到某个历史条目。它与按条目 Fork/Revert 的分支或破坏性历史变更不同。

## 演示边界

- 真实演示必须来自独立可丢弃 Home、tmux socket、端口和 CLI 副本；不读取或修改个人会话。
- 结果演示只能使用真实成功/失败记录，不能把测试断言或手写文本当成成功结果。
- 当前仅完成隔离 CLI 启动预检，画面只有会话入口和空的新会话，未录制历史操作；缺少 CLI 可导入的安全历史/工具结果 fixture，因此不生成 `.cast`。

## 源码依据（当前工作树）

- 历史位置与 `[↓]`：`Kodex/app/viewmodel/history/src/commonMain/kotlin/io/github/stream29/kodex/cli/history/AgentHistoryViewModel.kt:95-215,376-819`、`Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeUiPrimitives.kt:75-108`。
- 历史列表、展开和右键入口：`Kodex/app/view/history/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/history/AgentHistoryView.kt:102-188,315-414`。
- 状态限制、确认和不可撤销文字：`Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeCliScreen.kt:1372-1498`、`Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt:305-414,700-738`。
- Fork 的新会话边界：`Kodex/app/viewmodel/session/src/commonMain/kotlin/io/github/stream29/kodex/cli/session/SessionViewModels.kt:301-363`。
- Patch 分层和更多行：`Kodex/app/view/patch/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/patch/PatchToolEventView.kt:83-225`。
- 计划标记：`Kodex/app/view/history/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/history/PlanUpdateView.kt:36-68`。
