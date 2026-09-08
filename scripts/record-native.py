"""Record real, network-isolated Linux Kodex UI. Run with uv run python."""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("scene", choices=["workspace", "input", "configuration"])
parser.add_argument("--cli", type=Path, required=True)
parser.add_argument("--asciinema", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=True)
cast = output / f"{args.scene}.cast"
if cast.exists():
    raise SystemExit(f"Refusing to overwrite {cast}")

with tempfile.TemporaryDirectory(prefix="kodex-manual-") as temporary:
    work = Path(temporary)
    shutil.copy2(args.cli, work / "kodex")
    for name in ["home", "recorder-home", "project/docs", "project/src", "project/tests"]:
        (work / name).mkdir(parents=True, exist_ok=True)
    sandbox = [
        "bwrap", "--unshare-all", "--die-with-parent",
        "--ro-bind", "/usr", "/usr", "--ro-bind", "/lib", "/lib",
        "--ro-bind", "/lib64", "/lib64", "--ro-bind", "/etc/ssl", "/etc/ssl",
        "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
        "--dir", "/opt", "--ro-bind", str(work / "kodex"), "/opt/kodex",
        "--bind", str(work / "home"), "/home/demo",
        "--bind", str(work / "project"), "/work/demo",
        "--clearenv", "--setenv", "HOME", "/home/demo", "--setenv", "USER", "demo",
        "--setenv", "PATH", "/usr/bin:/bin", "--setenv", "SHELL", "/bin/sh",
        "--setenv", "TERM", "xterm-256color", "--setenv", "COLORTERM", "truecolor",
        "--setenv", "LANG", "C.UTF-8", "--setenv", "TMPDIR", "/tmp",
        "--chdir", "/work/demo", "/opt/kodex",
    ]
    command = [
        "env", "-i", "PATH=/usr/bin:/bin", f"HOME={work / 'recorder-home'}",
        "SHELL=/bin/sh", "TERM=xterm-256color", "COLORTERM=truecolor", "LANG=C.UTF-8",
        str(args.asciinema.resolve()), "rec", "--window-size", "120x36",
        "--capture-env", "TERM,COLORTERM", "--title", f"Kodex — {args.scene}",
        "--command", shlex.join(sandbox), "--return", str(cast),
    ]
    def tm(*parts):
        return subprocess.check_output(
            ["tmux", "-S", str(work / "tmux.sock"), *parts], text=True,
        )

    def screen():
        return tm("capture-pane", "-p", "-t", "demo")

    def send(sequence):
        tm("send-keys", "-t", "demo", "-l", "--", sequence)
        time.sleep(.7)

    def key(name):
        tm("send-keys", "-t", "demo", name)
        time.sleep(.7)

    def mouse(x, y, code=0):
        send(f"\033[<{code};{x};{y}M" + (f"\033[<{code};{x};{y}m" if code == 0 else ""))

    def click(label, field=False):
        for row, line in enumerate(screen().splitlines()):
            if label in line:
                start = line.index(label)
                column = line.find("[", start + len(label)) + 1 if field else start + 1
                if column < 1:
                    continue
                mouse(column + 1, row + 1)
                return
        raise AssertionError(f"Missing {label}:\n{screen()}")

    frames = []
    start = time.monotonic()

    def capture(label, expected=None):
        text = screen()
        if expected:
            assert expected in text, f"{label}: expected {expected}\n{text}"
        frames.append({"label": label, "time": round(time.monotonic() - start, 3), "text": text})

    try:
        tm("-f", "/dev/null", "new-session", "-d", "-x", "120", "-y", "36", "-s", "demo", shlex.join(command))
        tm("set-option", "-g", "remain-on-exit", "on")
        time.sleep(2)
        capture("Start", "[Settings]")
        if args.scene == "workspace":
            mouse(2, 2, 35); capture("Hover left", "History Index")
            mouse(60, 10, 35); capture("Leave unpinned left", "[→]")
            mouse(2, 2, 35)
            mouse(2, 2); mouse(60, 10, 35); capture("Pin left", "History Index")
            mouse(117, 2, 35); capture("Hover right", "Terminal sessions")
            mouse(60, 10, 35); capture("Leave unpinned right")
            mouse(117, 2, 35)
            mouse(117, 2); mouse(60, 10, 35); capture("Pin both", "Terminal sessions")
            send("\033[<0;28;10M\033[<32;38;10M\033[<0;38;10m")
            capture("Resize left")
            click("History Index"); capture("Choose content", "None")
            click("[None "); capture("None", "[None]")
            send("\033[<0;92;10M\033[<32;82;10M\033[<0;82;10m")
            capture("Resize right")
            mouse(2, 2); mouse(60, 10, 35); capture("Unpin left")
            mouse(117, 2); mouse(60, 10, 35); capture("Unpin both")
            mouse(2, 2, 35); click("[None]")
            mouse(60, 10, 35); capture("Menu keeps unpinned sidebar open", "Terminal sessions")
            key("Escape"); mouse(60, 10, 35); capture("Dismiss menu and sidebar", "[→]")
        elif args.scene == "input":
            mouse(3, 34)
            send("\033[200~" + "中文 / English — " * 10 + "\n第二行 / second line\033[201~")
            capture("Paste and wrap", "第二行")
            key("Home"); key("Right"); send("|")
            capture("Wide-character cursor", "第|二行")
            key("C-z"); key("End"); capture("Undo insertion", "第二行")
            key("C-w"); capture("Delete word")
            key("C-z"); capture("Undo", "second line")
            key("C-y"); capture("Redo")
            click("[Settings]"); click("Working directory", field=True)
            capture("Choose directory", "[docs/]")
            send("d"); send("o"); capture("Filter", "Filter: do")
            key("Enter"); capture("Enter directory", "/work/demo/docs")
            send("\033[<128;25;10M"); capture("Parent directory", "/work/demo")
            send("d"); capture("Filter again", "Filter: d")
            key("Escape"); capture("Escape clears filter", "Filter: type letters")
            assert "Select directory" in screen()
            send("do"); key("Enter"); click("[Select]")
            capture("Confirm directory", "/work/demo/docs")
            assert "Select directory" not in screen()
            click("Working directory", field=True)
            key("Escape"); capture("Escape closes picker", "Settings")
            assert "Select directory" not in screen()
            key("Escape"); capture("Escape closes settings")
            assert "Current session" not in screen()
        else:
            click("[Settings]"); capture("Current session", "Current session")
            click("[General]"); capture("Input settings", "New line key")
            click("New line key", field=True); capture("Newline choices", "Shift+Enter")
            click("[Enter"); capture("Enter inserts newline", "New line key [Enter]")
            click("[New session]"); capture("New-session defaults", "Title generation")
            click("Model", field=True); capture("Default model choices", "gpt-5.4")
            click("[gpt-5.4 "); capture("Changed default model", "Model [gpt-5.4]")
            click("[Current session]"); capture("Existing draft unchanged", "Model [gpt-5.6-sol]")
            click("[New session]")
            click("Title model", field=True); capture("Title model")
            click("[gpt-5.5 "); capture("Independent title model", "Title model [gpt-5.5]")
            click("Title reasoning", field=True); capture("Title reasoning")
            click("[high "); capture("Independent title reasoning", "Title reasoning [high]")
            click("Automatic session title"); capture("Title switch", "Automatic session title")
            assert "Available when automatic session titles are enabled." in screen()
            click("Title model", field=True); capture("Disabled title model", "Available when")
            click("Automatic session title"); capture("Re-enable titles", "Title model [gpt-5.5]")
            key("Escape")
            click("[+]"); capture("Next draft copies new defaults", "[gpt-5.4 medium]")
            click("[gpt-5.4 medium]"); capture("Status-bar model menu", "gpt-5.4")
            click("[gpt-5.4 "); capture("Status-bar reasoning menu", "high")
            click("[high"); capture("Status-bar service-tier menu", "default")
            click("[default"); capture("Current draft reasoning changed", "[gpt-5.4 high]")
            click("[ask user]"); capture("Question modes", "no question")
            click("[no question"); capture("Current draft question mode", "[no question]")
            click("[Settings]"); capture("Current draft settings", "Reasoning [high]")
            assert "Questions [no question]" in screen()
            click("[New session]"); capture("Defaults remain unchanged", "Reasoning [medium]")
            assert "Questions [ask user]" in screen()
            key("Escape")
        capture("Finish")
        key("C-c")
        assert tm("list-panes", "-t", "demo", "-F", "#{pane_dead} #{pane_dead_status}").strip() == "1 0"
    finally:
        subprocess.run(["tmux", "-S", str(work / "tmux.sock"), "kill-server"], capture_output=True)
    (output / f"{args.scene}.frames.json").write_text(json.dumps(frames, ensure_ascii=False, indent=2) + "\n")
    (output / f"{args.scene}.provenance.json").write_text(json.dumps({
        "kind": "native-cli", "cliSha256": hashlib.sha256(args.cli.read_bytes()).hexdigest(),
        "castSha256": hashlib.sha256(cast.read_bytes()).hexdigest(),
        "asciinemaSha256": hashlib.sha256(args.asciinema.read_bytes()).hexdigest(),
        "generatorSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "network": False, "personalHome": False, "inputCapture": False,
    }, indent=2) + "\n")
    print(cast)
