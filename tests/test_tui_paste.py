"""Regression tests for the v7.0.1 TUI fixes: clipboard paste + layout.

Paste: Ctrl+V must insert OS-clipboard text into the focused Input even on
Windows console hosts that swallow the keystroke before Textual sees it
(app-owned binding reading pyperclip). Layout: capped content columns must
not drag their scrollbar away from the screen edge.
"""

import pytest

from gitbook_downloader.tui.app import GitbookDownloaderApp
from gitbook_downloader.tui.testing import FakeEngine


@pytest.fixture()
def app():
    return GitbookDownloaderApp(engine=FakeEngine())


@pytest.mark.asyncio
async def test_ctrl_v_pastes_into_focused_url_input(app):
    async with app.run_test() as pilot:
        app._read_clipboard = lambda: "https://docs.example.com/guide"  # type: ignore[method-assign]
        url_input = app.query_one("#url-input")
        url_input.focus()
        await pilot.press("ctrl+v")
        assert url_input.value == "https://docs.example.com/guide"


@pytest.mark.asyncio
async def test_paste_collapses_whitespace(app):
    async with app.run_test() as pilot:
        app._read_clipboard = lambda: "https://x.com/a\n\nb"  # type: ignore[method-assign]
        url_input = app.query_one("#url-input")
        url_input.focus()
        await pilot.press("ctrl+v")
        assert url_input.value == "https://x.com/a b"


@pytest.mark.asyncio
async def test_paste_without_clipboard_notifies_but_does_not_crash(app):
    async with app.run_test() as pilot:
        app._read_clipboard = lambda: None  # type: ignore[method-assign]
        url_input = app.query_one("#url-input")
        url_input.focus()
        await pilot.press("ctrl+v")  # must not raise
        assert url_input.value == ""


def test_capped_surfaces_are_full_width_with_capped_children():
    """The scrollable surface itself must NOT be width-capped — a capped
    scroll widget drags its scrollbar to mid-screen on wide terminals."""
    from gitbook_downloader.tui.screens.diagnostics import DiagnosticsSurface
    from gitbook_downloader.tui.screens.search import SearchSurface
    from gitbook_downloader.tui.screens.wizard import WizardSurface

    for surface in (WizardSurface, SearchSurface, DiagnosticsSurface):
        assert "max-width" not in surface.DEFAULT_CSS, (
            f"{surface.__name__} must be full-width; cap children instead"
        )
