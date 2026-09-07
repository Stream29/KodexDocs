# Kodex / 快速上手

Kodex 是 Codex 的 Kotlin Multiplatform 实现。
本指南适用于原生 CLI 发行版 v0.4.3。

## 安装

按操作系统与 CPU 选择归档：

- macOS Apple Silicon：kodex-0.4.3-macos-arm64.tar.gz
- Linux x64：kodex-0.4.3-linux-x64.tar.gz
- Linux ARM64：kodex-0.4.3-linux-arm64.tar.gz
- Windows x64：kodex-0.4.3-windows-x64.zip

下载页面：
https://github.com/Stream29/Kodex/releases/tag/v0.4.3

这些原生发行版不需要 JVM。此版本没有 Intel macOS 归档。

运行前，计算归档的 SHA-256，与同一发行版中的 kodex-0.4.3-SHA256SUMS.txt 对应文件名的值比较。
macOS 使用 `shasum -a 256`，Linux 使用 `sha256sum`，Windows 使用 `Get-FileHash -Algorithm SHA256`。

macOS / Linux：在下载归档所在的文件夹运行。
下面以 Linux x64 为例，macOS 或 ARM64 请替换为对应归档名：

```sh
tar -xzf kodex-0.4.3-linux-x64.tar.gz
chmod +x kodex
./kodex
```

Windows / PowerShell：在下载 ZIP 所在的文件夹运行：

```powershell
Expand-Archive -Path .\kodex-0.4.3-windows-x64.zip -DestinationPath .\kodex
.\kodex\kodex.exe
```

可选：把可执行文件放到 PATH 中的目录，即可在项目目录使用 `kodex` 启动；否则使用完整路径。

## 第一次会话

1. 在交互式终端中运行解压后的可执行文件。
2. 打开 Settings → OpenAI，将 Authentication 设为 Kodex，再点击 Browser sign-in 下的 Sign in。
   也可以选择 Codex，使用 Codex CLI 管理的凭证并点击 Reload。
3. 使用 + 打开新会话，确认工作目录指向你的项目。
4. 选择可用的模型、推理强度与服务层级。
5. 使用输入框显示的提交快捷键发送一个小任务，换行方式可以在设置中调整。

先试一个只读请求：

```text
阅读项目指引，解释目录结构。
不要修改任何文件。建议一个小的后续步骤。
```

Kodex 能执行命令和编辑文件。请在可信项目中使用，保留备份或干净的 Git 基线，并检查改动与测试结果。
提示词是行为指引，不是安全沙箱。不要把凭证粘贴到对话中。

## 会话与历史

- Sessions：重新打开已保存的对话。
- +：开始新会话。
- Close：关闭标签页，不是删除已保存的会话。
- Fork：从已有历史开启独立对话。
- Archive：归档已完成的工作，使用 Show archived 再次查看。
- Delete：确认后删除会话。

分支或回退对话状态前，先检查历史与工具详情。
对话操作不能代替 Git 或文件备份。

## 设置与工具

- OpenAI：管理认证、查看账号用量，可用模型取决于账号。
- Context sources：配置项目指引与 skill 来源。项目指引使用 AGENTS.md，skill 使用 SKILL.md。
- MCP：添加可信服务器，或使用 Import from Codex。使用前检查连接与认证状态。
- Hooks：按需配置自定义自动化，启用前检查命令内容。

MCP 工具可能访问外部系统，hook 会在你的机器上执行。
请检查实际配置，不要假设不同 agent 共用同一个 Home。

## 常见问题

- 找不到命令：
  macOS/Linux 在解压目录执行 `./kodex`，Windows 执行 `.\kodex.exe`。若要在任意目录启动，把所在目录加入 PATH。
- macOS 阻止启动：
  确认来源与校验和，再按系统安全提示处理。不要关闭系统级安全保护。
- 登录没有完成：
  阅读登录对话框；浏览器未打开时使用其中的 URL。检查网络后重试。不要公开回调 URL 或 token。
- 模型请求失败：
  检查认证、所选模型、账号用量和网络连接。先阅读界面错误信息再重试。
- 数据保存位置：
  Kodex Home 位于 `~/.kodex`，Windows 也在用户主目录下。迁移或手动编辑前先备份。目录可能包含凭证和私密对话，不要整体上传。

反馈问题时，请提供版本、操作系统、终端、复现步骤与脱敏后的错误：
https://github.com/Stream29/Kodex/issues
