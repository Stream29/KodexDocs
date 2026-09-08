"""Record an isolated, authenticated CLI using reviewed English history.

Run with uv. Authentication is a read-only bind; original Sessions are never
opened. JSON commands on stdin drive tmux: start, key, paste, mouse, capture,
screen, stop, quit. Review recordings before publishing.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import time
import uuid

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--cli", type=Path, required=True)
parser.add_argument("--asciinema", type=Path, required=True)
parser.add_argument("--auth-file", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=True)
source = root / "Kodex/app/view/application/src/jvmTest/resources/docs/history-index.en.json"
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
auth_digest = digest(args.auth_file)
with tempfile.TemporaryDirectory(prefix="kodex-live-") as temporary:
    work = Path(temporary)
    home = work / "home"
    kodex_home = home / ".kodex"
    project = work / "project"
    for path in (kodex_home, project, work / "recorder-home"):
        path.mkdir(parents=True)
    shutil.copy2(args.cli, work / "kodex")
    (kodex_home / "auth.yml").touch(mode=0o600)
    (kodex_home / "version.json").write_text('"0.4.2"')
    (kodex_home / "settings.yml").write_text(
        "auth_source: kodex\nsession_title:\n  enabled: false\n"
    )
    session = kodex_home / "sessions/0"
    timelines = {name: {} for name in ("index", "work", "settings", "timestamp", "token-count", "unstable")}
    history = json.loads(source.read_text())
    for index, entry in history.items():
        # Keep content/types/answers, not provider response identifiers.
        entry.pop("id", None)
        entry.pop("item_id", None)
        timelines["index"][int(index)] = entry
    timelines["settings"][0] = {
        "model": "gpt-5.6-sol", "reasoning": {"effort": "medium"},
        "cwd": "/work/demo", "threadName": "History Index design",
        "turnId": str(uuid.uuid4()), "windowId": str(uuid.uuid4()),
        "firstWindowId": str(uuid.uuid4()),
    }
    timelines["timestamp"][0] = "2026-09-01T00:00:00Z"
    timelines["token-count"][0] = 0
    timelines["unstable"][0] = []
    for name, entries in timelines.items():
        path = session / name
        path.mkdir(parents=True)
        for index, value in entries.items():
            (path / f"{index}.json").write_text(json.dumps(value))
        (path / "latest.json").write_text(str(max(entries, default=-1)))
    (project / "README.md").write_text(
        "# History Index preview example\n\n"
        "This disposable Python example illustrates the Kodex feature discussion in the loaded history.\n"
        "Implement content-only row summaries for user/assistant messages, questions, and plans.\n"
        "Use the last non-pending plan step. Preserve full content for hover detail.\n"
        "This is not the production Kodex source. Do not read HOME or credentials, call external services,\n"
        "commit, publish, or modify anything outside this directory. Use python3; no dependencies.\n"
    )
    (project / "preview.py").write_text(
        'def summary(event):\n    return event["type"]\n'
    )
    (project / "checks.py").write_text(
        "import time, unittest\nfrom preview import summary\n"
        "print('Checking History Index preview behavior...', flush=True)\n"
        "time.sleep(20)\n"
        "class PreviewTests(unittest.TestCase):\n"
        "    def test_user(self):\n"
        "        self.assertEqual(summary({'type': 'user_message', 'text': 'Keep type labels hidden.'}), 'Keep type labels hidden.')\n"
        "    def test_plan(self):\n"
        "        event = {'type': 'plan_update', 'plan': [{'step': 'Inspect', 'status': 'completed'}, {'step': 'Implement', 'status': 'in_progress'}, {'step': 'Verify', 'status': 'pending'}]}\n"
        "        self.assertEqual(summary(event), 'Implement')\n"
        "    def test_question(self):\n"
        "        self.assertEqual(summary({'type': 'request_user_input', 'questions': [{'question': 'Color nodes too?'}]}), 'Color nodes too?')\n"
        "unittest.main()\n"
    )
    sandbox = [
        "bwrap", "--unshare-all", "--share-net", "--die-with-parent",
        "--ro-bind", "/usr", "/usr", "--ro-bind", "/lib", "/lib",
        "--symlink", "usr/bin", "/bin", "--symlink", "usr/sbin", "/sbin",
        "--ro-bind", "/lib64", "/lib64", "--ro-bind", "/etc/ssl", "/etc/ssl",
        "--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf",
        "--ro-bind", "/etc/hosts", "/etc/hosts",
        "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
        "--dir", "/opt", "--ro-bind", str(work / "kodex"), "/opt/kodex",
        "--bind", str(home), "/home/demo", "--bind", str(project), "/work/demo",
        "--ro-bind", str(args.auth_file.resolve()), "/home/demo/.kodex/auth.yml",
        "--clearenv", "--setenv", "HOME", "/home/demo", "--setenv", "USER", "demo",
        "--setenv", "PATH", "/usr/bin:/bin", "--setenv", "SHELL", "/bin/sh",
        "--setenv", "TERM", "xterm-256color", "--setenv", "COLORTERM", "truecolor",
        "--setenv", "LANG", "C.UTF-8", "--setenv", "TMPDIR", "/tmp",
        "--chdir", "/work/demo", "/opt/kodex",
    ]
    subprocess.run(sandbox[:-1] + [
        "/bin/sh", "-c",
        "test -s README.md && test -s preview.py && test -s checks.py && "
        "python3 -c \"import os; assert os.getcwd() == '/work/demo'\"",
    ], check=True, capture_output=True)
    launcher = work / "launch.sh"
    launcher.write_text("#!/bin/sh\nexec " + shlex.join(sandbox) + "\n")
    launcher.chmod(0o700)
    frames = []
    name = None
    start = 0

    def tm(*parts):
        return subprocess.check_output(["tmux", "-S", str(work / "tmux.sock"), *parts], text=True)

    def screen():
        return tm("capture-pane", "-p", "-t", "demo")

    def stop():
        global name
        if name is None:
            return
        tm("send-keys", "-t", "demo", "C-c")
        for _ in range(50):
            if tm("list-panes", "-t", "demo", "-F", "#{pane_dead}").strip() == "1":
                break
            time.sleep(.1)
        assert tm("list-panes", "-t", "demo", "-F", "#{pane_dead_status}").strip() == "0"
        tm("kill-server")
        (output / f"{name}.frames.json").write_text(json.dumps(frames, indent=2) + "\n")
        (output / f"{name}.provenance.json").write_text(json.dumps({
            "kind": "native-cli-authenticated",
            "cliSha256": digest(args.cli), "asciinemaSha256": digest(args.asciinema),
            "generatorSha256": digest(Path(__file__)), "historySha256": digest(source),
            "castSha256": digest(output / f"{name}.cast"),
            "credentialAccess": "read-only bind; no credential values captured",
            "originalSessionOpened": False, "inputCapture": False,
        }, indent=2) + "\n")
        # Only demo project files and stable history; no auth/settings/log copy.
        evidence = output / f"{name}-evidence"
        shutil.copytree(project, evidence / "project")
        for timeline in ("index", "work"):
            shutil.copytree(session / timeline, evidence / timeline)
        print("STOPPED", name, flush=True)
        name = None

    print("READY; isolated project and translated history prepared", flush=True)
    try:
        for line in iter(input, ""):
            command = json.loads(line)
            action = command["action"]
            if action == "quit":
                stop()
                break
            if action == "start":
                assert name is None
                name = command["name"]
                assert name in ("execution", "results-history", "history-index")
                cast = output / f"{name}.cast"
                assert not cast.exists(), "Refusing to overwrite recording"
                frames = []
                recording = [
                    "env", "-i", "PATH=/usr/bin:/bin", f"HOME={work / 'recorder-home'}",
                    "SHELL=/bin/sh", "TERM=xterm-256color", "COLORTERM=truecolor", "LANG=C.UTF-8",
                    str(args.asciinema.resolve()), "rec", "--window-size", "120x36",
                    "--capture-env", "TERM,COLORTERM", "--title", f"Kodex — {name}",
                    "--command", str(launcher), "--return", str(cast),
                ]
                tm("-f", "/dev/null", "new-session", "-d", "-x", "120", "-y", "36", "-s", "demo", shlex.join(recording))
                tm("set-option", "-g", "remain-on-exit", "on")
                start = time.monotonic()
                time.sleep(2)
            elif action == "key":
                tm("send-keys", "-t", "demo", command["key"])
            elif action == "paste":
                tm("send-keys", "-t", "demo", "-l", "--", "\033[200~" + command["text"] + "\033[201~")
            elif action == "mouse":
                x, y, code = command["x"], command["y"], command.get("code", 0)
                tm("send-keys", "-t", "demo", "-l", "--",
                   f"\033[<{code};{x};{y}M" + (f"\033[<{code};{x};{y}m" if code in (0, 2) else ""))
            elif action == "capture":
                text = screen()
                if command.get("expected", "") in text:
                    frames.append({"label": command["label"], "time": round(time.monotonic() - start, 3), "text": text})
                else:
                    print("CHECKPOINT NOT RECORDED: expected state is not visible", flush=True)
            elif action == "stop":
                stop()
            elif action != "screen":
                raise ValueError(action)
            time.sleep(.4)
            if name:
                print(screen(), flush=True)
    except EOFError:
        stop()
    finally:
        subprocess.run(["tmux", "-S", str(work / "tmux.sock"), "kill-server"], capture_output=True)
        assert digest(args.auth_file) == auth_digest, "Original credential file changed externally"
