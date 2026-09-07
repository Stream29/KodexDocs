# Kodex / Quickstart

Kodex is a Kotlin Multiplatform implementation for Codex.
This guide covers the native CLI release v0.4.3.

## Installation

Download the archive matching your OS and CPU:

- macOS Apple Silicon: kodex-0.4.3-macos-arm64.tar.gz
- Linux x64: kodex-0.4.3-linux-x64.tar.gz
- Linux ARM64: kodex-0.4.3-linux-arm64.tar.gz
- Windows x64: kodex-0.4.3-windows-x64.zip

Downloads:
https://github.com/Stream29/Kodex/releases/tag/v0.4.3

No JVM is needed for these native releases. There is no Intel macOS archive in this release.

Before running, compare the archive's SHA-256 with the matching filename in kodex-0.4.3-SHA256SUMS.txt, available in the same release.
Use `shasum -a 256` on macOS, `sha256sum` on Linux, or `Get-FileHash -Algorithm SHA256` on Windows.

macOS / Linux — run in the download folder.
This example is for Linux x64; substitute your archive name for macOS or ARM64:

```sh
tar -xzf kodex-0.4.3-linux-x64.tar.gz
chmod +x kodex
./kodex
```

Windows / PowerShell — run in the download folder:

```powershell
Expand-Archive -Path .\kodex-0.4.3-windows-x64.zip -DestinationPath .\kodex
.\kodex\kodex.exe
```

Optional: put the executable in a directory on PATH to run `kodex` from your project folder. Otherwise use its full path.

## First session

1. Run the extracted executable in an interactive terminal.
2. Open Settings → OpenAI. Set Authentication to Kodex, then choose Sign in under Browser sign-in.
   Alternatively select Codex to use credentials managed by Codex CLI, then Reload.
3. Use + to open a new session. Confirm its working directory points to your project.
4. Choose an available model, reasoning effort, and service tier.
5. Send a small task using the composer's displayed submit shortcut. Newline behavior is configurable.

Try a read-only request first:

```text
Read the project instructions and explain the directory structure.
Do not modify any files. Suggest one small next step.
```

Kodex can run commands and edit files. Work in a trusted project, keep a backup or a clean Git baseline, and review changes and test results.
A prompt is guidance, not a security sandbox. Never paste credentials into a conversation.

## Sessions & history

- Sessions: reopen saved conversations.
- +: start another session.
- Close: close a tab, rather than delete its saved session.
- Fork: start a separate conversation from existing history.
- Archive: put completed work aside. Show archived makes it visible again.
- Delete: remove a session after confirmation.

Inspect history and tool details before branching or reverting conversation state.
Conversation operations do not replace Git or file backups.

## Settings & tools

- OpenAI: manage authentication and view account usage. Available models depend on your account.
- Context sources: configure project-instruction and skill sources. Use AGENTS.md for project guidance and SKILL.md for a skill.
- MCP: add trusted servers or use Import from Codex. Check connection and authentication status before use.
- Hooks: configure custom automation only when needed. Review commands before enabling them.

MCP tools can access external systems. Hooks execute on your machine.
Check configured sources rather than assuming every agent shares the same Home.

## Troubleshooting

- Command not found:
  Run `./kodex` from the extracted directory on macOS/Linux, or `.\kodex.exe` on Windows. For a global command, add its directory to PATH.
- macOS blocks startup:
  Verify the download source and checksum, then follow the system security prompts. Do not disable system-wide protections.
- Sign-in does not finish:
  Read the login dialog; use its URL if the browser did not open. Check network access and retry. Do not share callback URLs or tokens.
- Model request fails:
  Check authentication, the selected model, account usage, and network access. Read the visible error before retrying.
- Data location:
  Kodex Home is `~/.kodex`, under your user home on Windows too. Back it up before migration or manual edits. It can contain credentials and private conversations; never upload the entire directory.

Report a problem with your version, OS, terminal, reproduction steps, and a redacted error:
https://github.com/Stream29/Kodex/issues
