"""Disposable local MCP server for recording real connection-management UI."""
import json
import os
from pathlib import Path
import sys

root = Path("/work/demo")
with (root / "mcp-starts.jsonl").open("a") as log:
    log.write(json.dumps({"pid": os.getpid(), "arguments": sys.argv[1:]}) + "\n")
if "--fail-once" in sys.argv and not (root / ".mcp-retry-ready").exists():
    (root / ".mcp-retry-ready").touch()
    raise SystemExit(1)

for line in sys.stdin:
    request = json.loads(line)
    with (root / "mcp-requests.jsonl").open("a") as log:
        log.write(json.dumps(request) + "\n")
    if "id" not in request:
        continue
    method = request["method"]
    if method == "initialize":
        result = {"protocolVersion": "2025-11-25", "capabilities": {"tools": {}},
                  "serverInfo": {"name": "docs-local-demo", "version": "1.0.0"}}
    elif method == "tools/list":
        result = {"tools": [{"name": name, "description": description,
                             "inputSchema": {"type": "object", "properties": {}}}
                            for name, description in (
                                ("demo_status", "Read the disposable demo status"),
                                ("demo_notes", "Read the disposable demo notes"))]}
    elif method == "ping":
        result = {}
    else:
        print(json.dumps({"jsonrpc": "2.0", "id": request["id"],
                          "error": {"code": -32601, "message": "Method not found"}}), flush=True)
        continue
    print(json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": result}), flush=True)
