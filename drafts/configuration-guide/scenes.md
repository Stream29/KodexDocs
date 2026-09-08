# 配置指南场景与证据（首批）

本文件是首批草稿的工作证据，不是最终目录决定。认证、MCP、Hooks 等内容不在本任务范围内。

## 作用域对照

| 场景 | 目标 | 写入位置 | 生效时机 |
| --- | --- | --- | --- |
| 全局新会话默认值 | 未来新草稿的初始 model / reasoning / tier / Questions | Kodex 私有 `settings.yml` 的 `new_session` | `NewSessionViewModelArgumentsProvider.create()` 创建草稿时读取一次 |
| 当前会话 | 已打开目标的设置 | 目标会话自己的 `KodexAgentSettings` / runtime storage | 更新目标后，后续操作读取新快照 |
| 新会话草稿 | 尚未物化的单个草稿 | 草稿 ViewModel 的本地 `mutableSettings` | 状态栏或 Current session 页立即改该草稿；不自动写回全局默认值 |
| 自动标题 | 首条合格文本的一次性辅助请求 | 全局 `session_title`；生成结果另写入目标标题 | 提交首条合格文本时读取当前标题设置；不回溯改写既有标题 |

关键边界：修改全局默认值不会把所有已有会话改成新值。对于自动标题，源码是在一次标题尝试开始时读取当前全局开关和参数；这不等于给已有会话批量重命名。

## 场景 A：真实录制中的配置入口

### 步骤

1. 使用 [`kodex-terminal-recording.md`](../../../shared-context/findings/kodex-terminal-recording.md) 的隔离路线：独立 Home、`bwrap`、独立 tmux socket、独立 CLI 副本；不继承私人 Home、账号或会话。
2. 从状态栏观察当前显示的 model + reasoning（以及非默认 tier）、Questions、工作目录和 Settings。
3. 打开 model 菜单，按 `model → reasoning → service tier` 的层级查看；只在隔离 Home 的演示配置中修改。
4. 打开 Settings，记录左侧 `Current session` 与 `New session` 入口；在 New session 页面查看 `Model behavior` 和 `Title generation`。
5. 用 Escape 关闭弹层；不要在禁网录制中声称已经生成了自动标题。

### 录制与安全证据

- 原始真实录制：`out/kodex-recording-probe/short.cast`
- 本任务复用的安全副本：`out/docs-demos/configuration-guide/settings-defaults.cast`
- 目标画面：`out/kodex-recording-probe/frame-settings.txt`，副本为 `out/docs-demos/configuration-guide/frame-settings.txt`
- 原始录制 SHA256：`f527e5dd7c578f5ab3816e4a3e64eba7ebbb147fa183641c091500f0ea3912a1`
- 录制规格：asciicast v3，120×36，约 16.078 秒；保留真实 ANSI 输出，没有拼接假 TUI。
- 已用 `uv run python` 读取安全副本：95 个事件；没有 `/home/stream`、`.kodex/auth`、Bearer 或常见 API key 标记；画面包含 `[Settings]` 与 `[gpt-5.6-sol medium]`。
- 现有 `verification.json` 已记录 10 个画面核对、桌面/窄屏回放和播放器控制验证；本任务没有把这些结果扩写成标题生成证明。

这段旧录制只证明已有 Settings 画面，未实际操作 New session 默认值或 Title generation；上面的步骤是计划，不是已录步骤。当前正式片段和来源见 `../../docs/public/recordings/manifest.json`。

## 场景 B：源码与测试基线

### 作用域来源

- 全局模型与默认值：[KodexGlobalSettings.kt:20-39](../../../Kodex/app/shared/settings/contract/src/commonMain/kotlin/io/github/stream29/kodex/cli/settings/KodexGlobalSettings.kt#L20-L39)、[KodexGlobalSettings.kt:102-122](../../../Kodex/app/shared/settings/contract/src/commonMain/kotlin/io/github/stream29/kodex/cli/settings/KodexGlobalSettings.kt#L102-L122)
- 全局持久化的 `new_session` / `session_title`：[KodexSettingsStore.kt:125-170](../../../Kodex/app/shared/settings/filesystem/src/commonMain/kotlin/io/github/stream29/kodex/cli/settings/KodexSettingsStore.kt#L125-L170)、[KodexSettingsStore.kt:253-304](../../../Kodex/app/shared/settings/filesystem/src/commonMain/kotlin/io/github/stream29/kodex/cli/settings/KodexSettingsStore.kt#L253-L304)
- 新会话默认值由全局快照提供：[Application.kt:511-525](../../../Kodex/app/viewmodel/application/src/commonMain/kotlin/io/github/stream29/kodex/cli/app/Application.kt#L511-L525)；New session Settings 自己更新全局值：[NewSessionSettingsViewModel.kt:31-52](../../../Kodex/app/viewmodel/settings/src/commonMain/kotlin/io/github/stream29/kodex/app/settings/NewSessionSettingsViewModel.kt#L31-L52)、[NewSessionSettingsViewModel.kt:85-99](../../../Kodex/app/viewmodel/settings/src/commonMain/kotlin/io/github/stream29/kodex/app/settings/NewSessionSettingsViewModel.kt#L85-L99)
- 草稿使用初始快照并在物化时捕获一次：[NewSessionViewModel.kt:27-46](../../../Kodex/app/viewmodel/new-session/src/commonMain/kotlin/io/github/stream29/kodex/cli/newsession/NewSessionViewModel.kt#L27-L46)、[NewSessionViewModel.kt:111-140](../../../Kodex/app/viewmodel/new-session/src/commonMain/kotlin/io/github/stream29/kodex/cli/newsession/NewSessionViewModel.kt#L111-L140)
- 当前目标固定绑定、按 revision 更新：[SessionSettingsDataSource.kt:22-35](../../../Kodex/app/viewmodel/application/src/commonMain/kotlin/io/github/stream29/kodex/cli/app/SessionSettingsDataSource.kt#L22-L35)、[SessionSettingsDataSource.kt:49-73](../../../Kodex/app/viewmodel/application/src/commonMain/kotlin/io/github/stream29/kodex/cli/app/SessionSettingsDataSource.kt#L49-L73)

### 入口与自动标题来源

- 状态栏的嵌套 Model / Reasoning / tier 菜单、Questions 与 Settings：[RuntimeStatusBar.kt:60-135](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L60-L135)、[RuntimeStatusBar.kt:202-262](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L202-L262)、[RuntimeStatusBar.kt:377-479](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/RuntimeStatusBar.kt#L377-L479)
- Settings 页面与 Title generation 控件：[SettingsPopup.kt:536-565](../../../Kodex/app/view/settings/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/settings/SettingsPopup.kt#L536-L565)、[SettingsPopup.kt:670-824](../../../Kodex/app/view/settings/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/settings/SettingsPopup.kt#L670-L824)、[SettingsPopup.kt:946-1058](../../../Kodex/app/view/settings/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/settings/SettingsPopup.kt#L946-L1058)
- 设置页入口绑定打开时目标：[ApplicationViewModel.kt:230-243](../../../Kodex/app/viewmodel/application/src/commonMain/kotlin/io/github/stream29/kodex/cli/app/ApplicationViewModel.kt#L230-L243)、[SessionTreeCliScreen.kt:457-525](../../../Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeCliScreen.kt#L457-L525)
- 自动标题的一次性条件与防止手动标题覆盖：[AgentTitleGeneration.kt:31-87](../../../Kodex/app/shared/session-title/src/commonMain/kotlin/io/github/stream29/kodex/cli/sessiontitle/AgentTitleGeneration.kt#L31-L87)、[AgentTitleGeneration.kt:116-160](../../../Kodex/app/shared/session-title/src/commonMain/kotlin/io/github/stream29/kodex/cli/sessiontitle/AgentTitleGeneration.kt#L116-L160)
- 首条提交时读取全局标题设置：[AgentRuntimeViewModel.kt:485-524](../../../Kodex/app/viewmodel/agent/src/commonMain/kotlin/io/github/stream29/kodex/cli/agent/AgentRuntimeViewModel.kt#L485-L524)、应用层 provider：[Application.kt:342-352](../../../Kodex/app/viewmodel/application/src/commonMain/kotlin/io/github/stream29/kodex/cli/app/Application.kt#L342-L352)
- 标题请求使用独立 model / reasoning、`store = false`、无工具：[OpenAiSessionTitleGenerator.kt:24-106](../../../Kodex/app/shared/session-title/src/commonMain/kotlin/io/github/stream29/kodex/cli/sessiontitle/OpenAiSessionTitleGenerator.kt#L24-L106)；未指定模型的 fallback：[SessionTitleGenerator.kt:6-16](../../../Kodex/app/shared/session-title/src/commonMain/kotlin/io/github/stream29/kodex/cli/sessiontitle/SessionTitleGenerator.kt#L6-L16)

### 测试依据

- 新会话设置只在物化时形成一个精确快照，并测试自动标题触发后的结果：[NewSessionViewModelTest.kt:38-114](../../../Kodex/app/viewmodel/new-session/src/commonTest/kotlin/io/github/stream29/kodex/cli/newsession/NewSessionViewModelTest.kt#L38-L114)、[NewSessionViewModelTest.kt:116-189](../../../Kodex/app/viewmodel/new-session/src/commonTest/kotlin/io/github/stream29/kodex/cli/newsession/NewSessionViewModelTest.kt#L116-L189)
- Settings ViewModel 测试分别验证 New session 更新全局默认值，以及 Current session 通过 revision 更新固定目标：[SettingsViewModelTest.kt:168-219](../../../Kodex/app/viewmodel/settings/src/commonTest/kotlin/io/github/stream29/kodex/app/settings/SettingsViewModelTest.kt#L168-L219)、[SettingsViewModelTest.kt:487-528](../../../Kodex/app/viewmodel/settings/src/commonTest/kotlin/io/github/stream29/kodex/app/settings/SettingsViewModelTest.kt#L487-L528)
- 全局 settings 的缺省值、稀疏 YAML 合并与 `session_title` 持久化：[KodexSettingsStoreTest.kt:32-45](../../../Kodex/app/shared/settings/filesystem/src/commonTest/kotlin/io/github/stream29/kodex/cli/settings/KodexSettingsStoreTest.kt#L32-L45)、[KodexSettingsStoreTest.kt:340-404](../../../Kodex/app/shared/settings/filesystem/src/commonTest/kotlin/io/github/stream29/kodex/cli/settings/KodexSettingsStoreTest.kt#L340-L404)
- 标题请求传递 model / reasoning 并使用隔离请求形态：[OpenAiSessionTitleGeneratorTest.kt:23-86](../../../Kodex/app/shared/session-title/src/commonTest/kotlin/io/github/stream29/kodex/cli/sessiontitle/OpenAiSessionTitleGeneratorTest.kt#L23-L86)

## 构建与版本基线

- 原 probe 检查时 HEAD 为 `ab54349003db16e6a59c48f63b8b6caf1745441d`，并非本批草稿检查时的当前 HEAD；旧二进制来源不可追溯。正式片段已另行重建，不能沿用本节作为当前构建证明。
- 复用 CLI：`Kodex/app/cli/build/bin/linuxX64/releaseExecutable/kodex-cli.kexe`
- CLI SHA256：`92539baaa88f4cb78a58ad73c5a23844ef49f65babb4ee968a692c80f26e6720`
- 本批没有重建 CLI，也没有并发重建共享构建目录；录制属于现有隔离探测，不是当前发布版证明。

## 验证结果

- 首批记录的 10/10 属于旧主题检查；该批最终报告为 14/14。两者均不是当前正式站点验收数量。
- 录制安全性：已复用原始 `short.cast`，仅在 `out/docs-demos/configuration-guide/` 保存安全副本和已存在的验证结果；没有访问私人配置、账号或会话。
- 界面证据：`frame-settings.txt` 显示 Settings、Current session、New session、Model behavior、模型、推理、服务层级、Questions 和 Settings 状态栏入口。
- 自动标题：源码与 mock/单元测试已核对；本批未进行联网生成，离线录制不证明真实模型已经生成标题。
- 浏览器验收：本批未把草稿接入 VitePress 路由，未进行正式页面的浏览器验收。

## 阻塞与后续

- 说明书目录仍待总结构任务确认；本批不修改首页、导航、主题或正式 `docs/` 路由。
- 需要标题生成的真实录制必须有安全的可控模型/fixture，并在独立 Home、socket、端口和 CLI 副本下重新验证；不能用禁网设置画面代替。
- 需要正式合入前补做三语言页面接入、浏览器文字/语言切换/窄屏验收，并重新记录可追溯构建基线。
