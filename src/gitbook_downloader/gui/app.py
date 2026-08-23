"""Desktop GUI launcher using PyWebView and Edge WebView2."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from .bridge import ApiBridge


def get_web_dir() -> Path:
    """Return the absolute path to the bundled web assets directory."""
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller onefile extract folder
        base = Path(sys._MEIPASS)
        candidate = base / "gitbook_downloader" / "gui" / "web"
        if candidate.exists():
            return candidate
        return base / "web"
    return Path(__file__).resolve().parent / "web"


def launch_gui(title: str = "GitBook Downloader v9.0 Beta", debug: bool = False) -> None:
    """Open the native Windows Desktop GUI application window."""
    try:
        import webview
    except ImportError as exc:
        raise ImportError(f"pywebview is required for GUI mode: {exc}") from exc


    web_dir = get_web_dir()
    index_file = web_dir / "index.html"
    if not index_file.exists():
        print(
            f"Error: GUI web assets not found at {index_file}. "
            f"Please verify installation.",
            file=sys.stderr,
        )
        sys.exit(1)

    bridge = ApiBridge()

    window = webview.create_window(
        title=title,
        url=index_file.as_uri(),
        js_api=bridge,
        width=1160,
        height=780,
        min_size=(920, 600),
        background_color="#090d16",
        text_select=True,
    )
    bridge.set_window(window)

    # Use Edge Chromium (WebView2) on Windows for highest performance & modern web features
    gui_engine = "edgechromium" if sys.platform == "win32" else None
    webview.start(gui=gui_engine, debug=debug)
