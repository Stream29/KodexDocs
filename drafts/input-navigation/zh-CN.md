# 输入编辑与目录导航

> 草稿：目录和播放器接入尚未确认。本页只记录已核对的功能、真实终端演示和边界。

## 输入编辑

Kodex 的 Composer 是终端输入框，不会把显示上的折行写成文本换行。

1. 聚焦输入框。
2. 粘贴包含中文、英文、数字和多行内容的文本。
3. 在较窄的输入区域中，长行会按终端 cell 宽度软换行；粘贴中的 `CRLF` / `CR` 会规范化为 `LF`。
4. 用方向键移动光标，再继续编辑。光标位置映射到原始文本边界，中文等宽字符按终端 cell 计算。

软换行只是显示布局：它不会在文本中插入 `\n`。真正的换行由当前配置的换行键产生。默认配置是 `Shift+Enter` 换行、`Enter` 提交；也可以把换行改为 `Enter`，此时提交键成对改为 `Ctrl+Enter`。文案和演示不应把某一个组合说成永远固定的提交键。

### 编辑历史

- `Ctrl+W` 删除光标前的一个词组；词、空白和标点按输入组件的分组规则处理。
- `Ctrl+Z` 撤销最近的编辑事务，`Ctrl+Y` 重做。
- 一次粘贴作为原子编辑处理；连续输入和删除按组件的历史合并规则记录。

源码与测试依据：

- `Kodex/app/view/components/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/components/TextInput.kt:102-156,221-305`
- `Kodex/app/view/components/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/components/TextInputTest.kt:83-103,181-249,251-364,366-395`
- `Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeUiPrimitives.kt:31-70,194-202`
- `Kodex/app/shared/settings/contract/src/commonMain/kotlin/io/github/stream29/kodex/cli/settings/KodexGlobalSettings.kt:124-147`
- `Kodex/app/view/application/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/app/ComposerInputTest.kt:24-59,89-127`

## 目录选择

从设置中的工作目录入口打开选择器后：

1. 直接输入字母过滤当前目录的子目录；过滤不区分大小写，文件不会显示为可选目录。
2. `Enter` 进入过滤结果的首项；再次按 `Enter` 确认当前目录。也可以聚焦 `[Select]` 按钮确认。
3. 鼠标 `Button8` 返回父目录，同时清除过滤条件。
4. `Escape` 分层处理：有过滤时先清除过滤；再次按下关闭目录弹层；若设置仍打开，再按一次关闭设置。

`Button8` 是真实终端鼠标事件，不是播放器中的文字选择。播放器选字也不能证明真实终端的 `Shift+拖拽` 选择；本轮尚未验证终端原生文本选择，故不把它写成已支持的 Kodex 应用功能。

源码与测试依据：

- `Kodex/app/view/path-picker/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/pathpicker/DirectoryPickerPopup.kt:46-134,154-229`
- `Kodex/app/contract/path-picker/src/commonMain/kotlin/io/github/stream29/kodex/app/pathpicker/contract/DirectoryPickerState.kt:67-91`
- `Kodex/app/viewmodel/path-picker/src/commonMain/kotlin/io/github/stream29/kodex/app/pathpicker/DirectoryPickerViewModel.kt:45-88`
- `Kodex/app/view/path-picker/src/mosaicTest/kotlin/io/github/stream29/kodex/cli/pathpicker/DirectoryPickerPopupTest.kt:31-182,184-233`

## 演示边界

本批真实演示使用 **原生 CLI → asciinema → asciinema-player**，不是模拟 TUI，也不是网页端在线操作。录制采用独立临时 Home、tmux socket、CLI 副本和无网络沙箱。正式内容仍需在确认后的目录合入；当前草稿不代表 Pages 已接入。
