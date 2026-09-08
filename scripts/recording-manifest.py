"""Generate provenance for the reviewed docs recordings, not arbitrary recordings."""
import hashlib
import argparse
import json
import subprocess
from pathlib import Path
from recording_timing import collapse_preparation

root = Path(__file__).resolve().parents[2]
assets = root / "KodexDocs/docs/public/recordings"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source-revision", required=True, help="Kodex revision used for the recorded CLI build")
args = parser.parse_args()
source = subprocess.check_output(["git", "-C", str(root / "Kodex"), "rev-parse", args.source_revision], text=True).strip()
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
native_script = root / "KodexDocs/scripts/record-native.py"
live_script = root / "KodexDocs/scripts/record-live.py"
integrations_script = root / "KodexDocs/scripts/record-integrations.py"
translated_history = root / "Kodex/app/view/application/src/jvmTest/resources/docs/history-index.en.json"
test_path = root / "Kodex/app/view/application/src/jvmTest/kotlin/io/github/stream29/kodex/cli/app"
exporters = {
    "history-actions": "DocsHistoryRecordingTest.kt", "history-index": "DocsHistoryRecordingTest.kt",
    "terminal-sessions": "DocsWorkspaceRecordingTest.kt", "session-tabs": "DocsWorkspaceRecordingTest.kt",
}
shell = root / "Kodex/app/view/application/src/mosaicMain/kotlin/io/github/stream29/kodex/cli/app/SessionTreeCliScreen.kt"
manifest = {
    "sourceRevision": source, "release": False,
    "productionChange": {
        "file": str(shell.relative_to(root)), "sha256": digest(shell),
        "description": "AgentHistoryRevertDialog visibility private -> internal for direct component tests; behavior unchanged",
    },
    "recordings": {},
}
for name in ("workspace", "input", "configuration", "execution", "questions", "suggestions",
             "results-history", "history-index", "terminal-sessions", "session-tabs", "hooks", "mcp"):
    live = name in ("execution", "results-history", "history-index")
    integrations = name in ("hooks", "mcp")
    native = live or integrations or name in ("workspace", "input", "configuration")
    generator = integrations_script if integrations else live_script if live else native_script
    exporter = test_path / exporters.get(name, "DocsRecordingTest.kt")
    cast = assets / f"{name}.cast"
    events = [json.loads(line) for line in cast.read_text().splitlines()]
    assert all(event[1] == "o" or event[1:] == ["x", "0"] for event in events[1:])
    record = {
        "kind": "native-cli" if native else "production-components-offline-fixture",
        "castSha256": digest(cast),
        "format": events[0]["version"],
        "size": [120, 36] if native else [80, 18],
        "durationSeconds": round(sum(e[0] for e in events[1:]) if native else events[-1][0], 3),
        "timing": "PTY wall-clock" if native else "editorial: two seconds per asserted frame",
        "generator": str((generator if native else exporter).relative_to(root)),
        "generatorSha256": digest(generator if native else exporter),
        "inputCaptured": False,
        "originalHomeMounted": False,
        "modelCalled": name == "execution",
    }
    if not native:
        record["sharedExporterSha256"] = digest(test_path / "DocsRecordingTest.kt")
    if native:
        directory = "docs-integrations/final" if integrations else "docs-live-current" if live else "docs-native-current"
        provenance = json.loads((root / f"out/{directory}/{name}.provenance.json").read_text())
        if name == "results-history":
            original = root / "out/docs-live-current/results-history.cast"
            original_events = [json.loads(line) for line in original.read_text().splitlines()]
            assert digest(original) == provenance["castSha256"]
            assert events == collapse_preparation(original_events, 190.1)
            record["sourceCastSha256"] = provenance["castSha256"]
            record["sourceOutputSha256"] = hashlib.sha256(
                "".join(event[2] for event in original_events[1:] if event[1] == "o").encode()
            ).hexdigest()
            record["preparationSecondsCollapsed"] = 190.1
            record["timing"] = "editorial: preparation outputs at t=0; subsequent recorded intervals preserved"
            record["timingEditor"] = "KodexDocs/scripts/recording_timing.py"
            record["timingEditorSha256"] = digest(root / record["timingEditor"])
        else:
            assert provenance["castSha256"] == record["castSha256"]
        assert provenance["generatorSha256"] == record["generatorSha256"]
        record["cliSha256"] = provenance["cliSha256"]
        record["asciinemaSha256"] = provenance["asciinemaSha256"]
        record["networkIsolated"] = not live
        if integrations:
            fixture = root / "KodexDocs/scripts/fixtures/mcp-demo.py"
            actions = root / f"KodexDocs/scripts/fixtures/{name}-actions.json"
            assert provenance["fixtureSha256"] == digest(fixture)
            assert provenance["actionsSha256"] == digest(actions)
            record["demoFixture"] = provenance["fixture"]
            record["fixtureSha256"] = digest(fixture)
            record["actionsSha256"] = digest(actions)
            record["actions"] = str(actions.relative_to(root))
        if live:
            assert provenance["historySha256"] == digest(translated_history)
            record["translatedHistory"] = {
                "file": str(translated_history.relative_to(root)),
                "sha256": digest(translated_history),
                "description": "User-authorized English translation of a local Kodex feature discussion excerpt; original session unchanged",
            }
            record["credentialAccess"] = "read-only authentication file bind; credentials excluded from recordings"
            record["originalSessionOpened"] = False
            if "controllerSha256" in provenance:
                record["controllerSha256"] = provenance["controllerSha256"]
    manifest["recordings"][name] = record
(assets / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
