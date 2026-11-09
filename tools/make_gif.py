"""Снимает экраны через Playwright (CDP-порт локального Chrome) и собирает два GIF."""

from __future__ import annotations

import socket
import subprocess
import tempfile
import time
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

APP = "http://127.0.0.1:8010"
CDP_PORT = 9333
DOCS = Path(__file__).resolve().parents[1] / "docs"
SHOTS = DOCS / "shots"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
VIEWPORT = {"width": 1440, "height": 980}
WIDTH = 1180
COLORS = 128
DURATION = 1500

PAGES = (
    ("01-landing", "/"),
    ("02-p1", "/p1"),
    ("03-p2", "/p2"),
    ("04-p3", "/p3"),
    ("05-p4", "/p4"),
    ("06-p5", "/p5"),
    ("07-p6", "/p6"),
    ("08-p7", "/p7"),
    ("09-p8", "/p8"),
)

ACTIONS = (
    ("10-p1-host", "/p1", "select#p1-host", "select"),
    ("11-p3-recount", "/p3", "#p3-recount", "click"),
    ("12-p5-analyze", "/p5", "#p5-analyze", "click"),
    ("13-p6-route", "/p6", "#p6-route", "click"),
    ("14-p8-classify", "/p8", "#p8-run", "click"),
)


def _listening(port):
    with socket.socket() as sock:
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _poll(port, moment):
    time.sleep(0.5)
    return _listening(port)


def _wait(port):
    return any(_poll(port, moment) for moment in range(60))


def _spawn():
    return subprocess.Popen([CHROME, "--headless=new", f"--remote-debugging-port={CDP_PORT}", f"--user-data-dir={tempfile.mkdtemp(prefix='pw-gif-')}", "--no-first-run", "--no-default-browser-check", "--hide-scrollbars", "--disable-gpu", "about:blank"])


def _connect(api):
    _wait(CDP_PORT)
    return api.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")


def _viewport(page):
    page.set_viewport_size(VIEWPORT)
    return page


def _sized(context):
    return _viewport(context.new_page())


def _page(browser):
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    return _sized(context)


def _shot_path(name):
    return str(SHOTS / f"{name}.png")


def _save(page, target):
    page.screenshot(path=target)
    return target


def _shot(page, name):
    page.wait_for_timeout(500)
    return _save(page, _shot_path(name))


def _open(page, name, path):
    page.goto(APP + path, wait_until="networkidle")
    return _shot(page, name)


def _visit(page, flow):
    name, path = flow
    return _open(page, name, path)


def _act(page, selector, action):
    return page.select_option(selector, index=1) if action == "select" else page.click(selector)


def _finish(page, name, selector, action):
    _act(page, selector, action)
    return _shot(page, name)


def _prepare(page, name, path, selector, action):
    page.goto(APP + path, wait_until="networkidle")
    return _finish(page, name, selector, action)


def _interact(page, flow):
    return _prepare(page, *flow)


def _palette(image, width):
    small = image.resize((width, max(1, round(image.height * width / image.width))), Image.LANCZOS)
    return small.convert("P", palette=Image.ADAPTIVE, colors=COLORS)


def _frame(path):
    return _palette(Image.open(path).convert("RGB"), WIDTH)


def _save_gif(frames, target):
    frames[0].save(target, save_all=True, append_images=frames[1:], duration=DURATION, loop=0, optimize=True)
    return f"{target.name}: {len(frames)} кадров, {target.stat().st_size // 1024} КБ"


def _gif(paths, target):
    return _save_gif([_frame(path) for path in paths], target)


def _walk(page):
    return [_visit(page, flow) for flow in PAGES], [_interact(page, flow) for flow in ACTIONS]


def _report(pages, actions):
    return [_gif(pages, DOCS / "demo.gif"), _gif(actions, DOCS / "interactions.gif")]


def _collect(page):
    pages, actions = _walk(page)
    return _report(pages, actions)


def _capture(browser):
    return _collect(_page(browser))


def _with_api():
    with sync_playwright() as api:
        return _capture(_connect(api))


def _run():
    proc = _spawn()
    try:
        return _with_api()
    finally:
        proc.terminate()


def _output(lines):
    print("\n".join(lines))
    return 0


def _missing():
    print("Сначала поднимите приложение: python -m uvicorn app.main:app --port 8010")
    return 1


def main(_argv):
    return _output(_run()) if _listening(8010) else _missing()


if __name__ == "__main__":
    raise SystemExit(main([]))
