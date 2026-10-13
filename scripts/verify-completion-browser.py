"""Check the current UI showcase and reviewed completion frames in headless Chrome."""

import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--base", required=True, help="VitePress preview base ending in /KodexDocs/")
parser.add_argument("--output", required=True, type=Path)
parser.add_argument("--chrome", default="/usr/bin/google-chrome")
args = parser.parse_args()
base = args.base.rstrip("/") + "/"
assets = root / "KodexDocs/docs/public/recordings"
frames = root / "out/docs-completion"
clips = ("suggestions-accepted", "session-management", "history-invalidation")
result = {"pages": [], "clips": {}, "pageErrors": [], "failedRequests": []}

test_page = """<!doctype html><html><head><link rel="icon" href="data:,">
<link rel="stylesheet" href="/replay-player.css"></head><body>
<div id="terminal"></div><script src="/replay-player.js"></script><script>
const p = new URLSearchParams(location.search);
window.player = AsciinemaPlayer.create('/KodexDocs/recordings/'+p.get('clip')+'.cast',
  document.getElementById('terminal'), {preload:true, autoPlay:true, loop:true,
  controls:false, fit:'width', speed:50});
window.wraps = 0; window.previous = 0;
setInterval(() => {const t=player.getCurrentTime(); if(t+0.05<previous) wraps++; previous=t;}, 10);
</script></body></html>"""

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=args.chrome, headless=True, args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 1440, "height": 1100})
    page.on("pageerror", lambda error: result["pageErrors"].append(str(error)))
    page.on("requestfailed", lambda request: result["failedRequests"].append(request.url))
    for locale, prefix in (("en-US", ""), ("zh-CN", "zh-CN/"), ("zh-TW", "zh-TW/")):
        page.goto(base + prefix)
        page.wait_for_selector(".ap-player")
        page.wait_for_function("document.querySelectorAll('.ap-player').length === 15")
        assert page.locator(".terminal-player__mount[inert]").count() == 15
        assert page.locator(".ap-control-bar,.ap-playback-button,.ap-progressbar").count() == 0
        assert page.locator(".contents a").count() == 15
        source = (root / "KodexDocs/docs" / prefix / "index.md").read_text()
        assert "".join(page.locator("pre.markdown").all_text_contents()) == source
        for width in (1440, 1024, 768, 390, 320):
            page.set_viewport_size({"width": width, "height": 1100})
            page.wait_for_timeout(150)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            assert page.locator(".ap-control-bar").count() == 0
        result["pages"].append({"locale": locale, "players": 15, "widths": 5, "inert": True})
        page.set_viewport_size({"width": 1440, "height": 1100})

    bundle = root / "KodexDocs/node_modules/asciinema-player/dist/bundle"
    replay = browser.new_page(viewport={"width": 1440, "height": 1100})
    replay.on("pageerror", lambda error: result["pageErrors"].append(str(error)))
    replay.on("requestfailed", lambda request: result["failedRequests"].append(request.url))
    for extension, content_type in (("js", "text/javascript"), ("css", "text/css")):
        file = bundle / f"asciinema-player{'.min' if extension == 'js' else ''}.{extension}"
        replay.route(
            f"**/replay-player.{extension}",
            lambda route, request, body=file.read_text(), content_type=content_type:
                route.fulfill(body=body, content_type=content_type),
        )
    replay.route("**/completion-replay.html*", lambda route:
                 route.fulfill(body=test_page, content_type="text/html"))
    for name in clips:
        cast = [json.loads(line) for line in (assets / f"{name}.cast").read_text().splitlines()]
        height = cast[0]["height"]
        replay.goto(base + f"completion-replay.html?clip={name}")
        replay.wait_for_function("player.getDuration() > 0")
        replay.wait_for_function("wraps >= 2", timeout=60000)
        assert replay.locator(".ap-control-bar,.ap-playback-button").count() == 0
        for index in range(len(cast) - 2):
            replay.evaluate("index => { player.pause(); player.seek(index * 2 + 0.1) }", index)
            replay.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
            actual = replay.locator(".ap-line").evaluate_all(
                "rows => rows.map(row => row.textContent.trimEnd())",
            )
            source = (frames / f"{name}-{index}.txt").read_text().split("\n")
            expected = ([line.rstrip() for line in source] + [""] * height)[:height]
            assert actual == expected, f"{name} frame {index}"
        result["clips"][name] = {"frames": len(cast) - 2, "wraps": replay.evaluate("wraps")}
    browser.close()

args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
assert not result["pageErrors"], result["pageErrors"]
assert not result["failedRequests"], result["failedRequests"]
print(f"Validated {len(result['pages'])} locale pages and {sum(c['frames'] for c in result['clips'].values())} completion frames.")
