"""Record native Hooks/MCP settings in a disposable, network-isolated Home."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import tempfile
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("scene", choices=["hooks", "mcp"])
parser.add_argument("--cli", type=Path, required=True)
parser.add_argument("--asciinema", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--actions", type=Path, help="Replay checked actions; omit for an interactive rehearsal.")
args = parser.parse_args()
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=True)
cast = output / f"{args.scene}.cast"
if cast.exists():
    raise SystemExit(f"Refusing to overwrite {cast}")
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
fixture = Path(__file__).parent / "fixtures/mcp-demo.py"
frames, snapshots = [], []
with tempfile.TemporaryDirectory(prefix="kodex-docs-integrations-") as directory:
    work = Path(directory)
    for sub in ["home/.kodex", "home/.codex", "recorder-home", "project"]:
        (work / sub).mkdir(parents=True)
    shutil.copy2(args.cli, work / "kodex")
    shutil.copy2(fixture, work / "project/mcp-demo.py")
    (work / "home/.kodex/settings.yml").write_text("session_title:\n  enabled: false\n")
    (work / "home/.codex/config.toml").write_text("""
[mcp_servers.local-tools]
command = "/usr/bin/python3"
args = ["/work/demo/mcp-demo.py"]
env = { DEMO_MODE = "imported-example" }
[mcp_servers.docs-search]
command = "/usr/bin/python3"
args = ["/work/demo/mcp-demo.py"]
""".lstrip())
    sandbox = [
        "bwrap", "--unshare-all", "--die-with-parent",
        "--ro-bind", "/usr", "/usr", "--ro-bind", "/lib", "/lib",
        "--ro-bind", "/lib64", "/lib64", "--symlink", "usr/bin", "/bin",
        "--ro-bind", "/etc/ssl", "/etc/ssl", "--proc", "/proc", "--dev", "/dev",
        "--tmpfs", "/tmp", "--dir", "/opt", "--ro-bind", str(work / "kodex"), "/opt/kodex",
        "--bind", str(work / "home"), "/home/demo",
        "--bind", str(work / "project"), "/work/demo",
        "--clearenv", "--setenv", "HOME", "/home/demo", "--setenv", "USER", "demo",
        "--setenv", "PATH", "/usr/bin:/bin", "--setenv", "SHELL", "/bin/sh",
        "--setenv", "TERM", "xterm-256color", "--setenv", "COLORTERM", "truecolor",
        "--setenv", "LANG", "C.UTF-8", "--chdir", "/work/demo", "/opt/kodex",
    ]
    command = [
        "env", "-i", "PATH=/usr/bin:/bin", f"HOME={work / 'recorder-home'}",
        "SHELL=/bin/sh", "TERM=xterm-256color", "COLORTERM=truecolor", "LANG=C.UTF-8",
        str(args.asciinema.resolve()), "rec", "--window-size", "120x36",
        "--capture-env", "TERM,COLORTERM", "--title", f"Kodex — {args.scene}",
        "--command", shlex.join(sandbox), "--return", str(cast),
    ]
    socket = str(work / "tmux.sock")
    def tm(*parts):
        return subprocess.check_output(["tmux", "-S", socket, *parts], text=True)

    def screen():
        return tm("capture-pane", "-p", "-t", "demo")

    def keys(*parts):
        tm("send-keys", "-t", "demo", *parts)
        time.sleep(.2)

    def mouse(x, y, button=0):
        keys("-l", "--", f"\033[<{button};{x};{y}M" + (f"\033[<{button};{x};{y}m" if button < 3 else ""))

    def locate(label):
        for row, line in enumerate(screen().splitlines()):
            if label in line:
                return line.index(label) + 2, row + 1
        raise AssertionError(f"Missing {label}:\n{screen()}")

    def act(action):
        if "click" in action:
            mouse(*locate(action["click"]))
        if "hover" in action:
            mouse(*locate(action["hover"]), button=35)
        if "field" in action:
            x, y = locate(action["field"])
            mouse(x, y + 1)
            keys("End")
            keys("-N", "240", "BSpace")
            keys("-l", "--", "\033[200~" + action["text"] + "\033[201~")
        if "key" in action:
            keys(action["key"])
        if "paste" in action:
            keys("-l", "--", "\033[200~" + action["paste"] + "\033[201~")
        if "mouse" in action:
            mouse(*action["mouse"])
        if "waitFor" in action:
            until = time.monotonic() + 10
            while action["waitFor"] not in screen():
                if time.monotonic() > until:
                    raise AssertionError(f"Timeout waiting for {action['waitFor']}:\n{screen()}")
                time.sleep(.1)
        if "capture" in action:
            text = screen()
            for required in action.get("contains", []):
                assert required in text, (action["capture"], required, text)
            for forbidden in action.get("absent", []):
                assert forbidden not in text, (action["capture"], forbidden, text)
            frames.append({"label": action["capture"], "time": round(time.monotonic() - start, 3), "text": text})
            snapshots.append({"label": action["capture"], "settings": (work / "home/.kodex/settings.yml").read_text()})
            time.sleep(1.4 if args.actions else .1)
        print(screen(), flush=True)

    pane_pid = None
    start = time.monotonic()
    try:
        tm("-f", "/dev/null", "new-session", "-d", "-x", "120", "-y", "36", "-s", "demo", shlex.join(command))
        tm("set-option", "-g", "remain-on-exit", "on")
        pane_pid = int(tm("display-message", "-p", "-t", "demo", "#{pane_pid}").strip())
        time.sleep(2)
        print(screen(), flush=True)
        if args.actions:
            for action in json.loads(args.actions.read_text()):
                act(action)
        else:
            while True:
                line = input()
                if line == "quit":
                    break
                try:
                    act(json.loads(line))
                except (AssertionError, ValueError) as error:
                    print(error, flush=True)
        keys("Escape")
        keys("C-c")
        time.sleep(.5)
        assert tm("list-panes", "-t", "demo", "-F", "#{pane_dead} #{pane_dead_status}").strip() == "1 0"
        (output / f"{args.scene}.frames.json").write_text(json.dumps(frames, indent=2) + "\n")
        (output / f"{args.scene}.settings.json").write_text(json.dumps(snapshots, indent=2) + "\n")
        for file in (work / "project").glob("mcp-*.jsonl"):
            shutil.copy2(file, output / f"{args.scene}-{file.name}")
        (output / f"{args.scene}.provenance.json").write_text(json.dumps({
            "kind": "native-cli", "cliSha256": digest(args.cli), "castSha256": digest(cast),
            "asciinemaSha256": digest(args.asciinema), "generatorSha256": digest(Path(__file__)),
            "fixtureSha256": digest(fixture), "actionsSha256": digest(args.actions) if args.actions else None,
            "network": False, "personalHome": False, "inputCapture": False,
            "fixture": "Disposable Codex configuration and local MCP server; no personal credentials",
        }, indent=2) + "\n")
    finally:
        # tmux alone did not reap earlier disconnected recorder trees. Terminate
        # only descendants of this dedicated pane before removing its Home.
        if pane_pid:
            processes = [tuple(map(int, line.split())) for line in
                         subprocess.check_output(["ps", "-eo", "pid=,ppid="], text=True).splitlines()]
            owned = {pane_pid}
            for _ in range(len(processes)):
                expanded = owned | {pid for pid, parent in processes if parent in owned}
                if expanded == owned:
                    break
                owned = expanded
            for pid in reversed(sorted(owned)):
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
        subprocess.run(["tmux", "-S", socket, "kill-server"], capture_output=True)
