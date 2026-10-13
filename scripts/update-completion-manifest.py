"""Add reviewed current-source completion clips without rewriting older provenance."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[2]
assets = root / "KodexDocs/docs/public/recordings"
manifest_path = assets / "manifest.json"
test_root = root / "Kodex/app/impl/view/src/jvmTest/kotlin/io/github/stream29/kodex/cli/app"
exporter = test_root / "DocsRecordingTest.kt"
clips = {
    "suggestions-accepted": ("DocsCompletionRecordingTest.kt", [120, 36], 7),
    "session-management": ("DocsSessionManagementRecordingTest.kt", [120, 36], 20),
    "history-invalidation": ("DocsHistoryInvalidationRecordingTest.kt", [120, 36], 6),
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source-revision", required=True, help="Kodex revision tested on the isolated build host")
args = parser.parse_args()
source = subprocess.check_output(
    ["git", "-C", str(root / "Kodex"), "rev-parse", args.source_revision],
    text=True,
).strip()
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
manifest = json.loads(manifest_path.read_text())

for name, (test_file, size, frames) in clips.items():
    cast = assets / f"{name}.cast"
    events = [json.loads(line) for line in cast.read_text().splitlines()]
    assert events[0]["version"] == 2
    assert [events[0]["width"], events[0]["height"]] == size
    assert len(events) == frames + 2
    assert all(event[1] == "o" for event in events[1:])
    assert events[-1] == [frames * 2.0, "o", ""]
    generator = test_root / test_file
    record = {
        "kind": "full-application-offline-fixture",
        "sourceRevision": source,
        "castSha256": digest(cast),
        "format": 2,
        "size": size,
        "durationSeconds": frames * 2,
        "timing": "editorial: two seconds per asserted frame",
        "generator": str(generator.relative_to(root)),
        "generatorSha256": digest(generator),
        "sharedExporterSha256": digest(exporter),
        "inputCaptured": False,
        "originalHomeMounted": False,
        "modelCalled": False,
        "modelClient": "offline mock",
        "testBackend": "disposable filesystem Home and in-memory RPC; full application shell",
    }
    if name == "suggestions-accepted":
        record["pendingSuggestion"] = "mocked model tool call; production approval and automatic Session tab opening"
    if name == "history-invalidation":
        record["invalidation"] = "running dismisses menu; selecting another tab dismisses stale confirmation"
    manifest["recordings"][name] = record

manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
