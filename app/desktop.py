"""Оконное приложение для аналитика: локальный сервер в фоновом потоке и нативное окно."""

from __future__ import annotations

import importlib.util
import os
import socket
import subprocess
import threading
import time
from pathlib import Path

import uvicorn

PORT = int(os.getenv("DESKTOP_PORT", "8011"))
URL = f"http://127.0.0.1:{PORT}"
TITLE = "1С · Портфель решений — рабочее место аналитика"
WIDTH = 1460
HEIGHT = 940
MIN_SIZE = (1080, 720)
BROWSERS = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
)


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _port():
    return int(os.getenv("DESKTOP_PORT", "0")) or _free_port()


def _listening(port):
    with socket.socket() as sock:
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _poll(port, moment):
    time.sleep(0.4)
    return _listening(port)


def wait_for(port):
    return any(_poll(port, moment) for moment in range(100))


def _server(port):
    return uvicorn.Server(uvicorn.Config("app.main:app", host="127.0.0.1", port=port, log_level="warning"))


def _start(server):
    threading.Thread(target=server.run, daemon=True).start()
    return wait_for(server.config.port)


def _has_native():
    return importlib.util.find_spec("webview") is not None


def _webview():
    import webview

    return webview


def _window(api, url, title):
    return api.create_window(title, url, width=WIDTH, height=HEIGHT, min_size=MIN_SIZE)


def _run_window(api, url, title):
    _window(api, url, title)
    return api.start()


def _native(url, title):
    return _run_window(_webview(), url, title)


def _browser():
    return next((path for path in BROWSERS if path.exists()), BROWSERS[0])


def _app_window(url):
    return subprocess.run([str(_browser()), f"--app={url}", f"--window-size={WIDTH},{HEIGHT}"], check=False).returncode


def _show(url, title):
    return _native(url, title) if _has_native() else _app_window(url)


def _stop(server):
    server.should_exit = True
    return 0


def _finish(server, url):
    _show(url, TITLE)
    return _stop(server)


def _launch(server, url):
    _start(server)
    return _finish(server, url)


def main():
    port = _port()
    return _launch(_server(port), f"http://127.0.0.1:{port}")


if __name__ == "__main__":
    raise SystemExit(main())
