"""Pilot tests — app shell: launch, navigation, theme toggle, nav bar."""

from __future__ import annotations

import asyncio
import time

import pytest

try:
    import textual  # noqa: F401

    HAS_TEXTUAL = True
except ImportError:  # pragma: no cover - depends on environment
    HAS_TEXTUAL = False

pytestmark = pytest.mark.skipif(
    not HAS_TEXTUAL, reason="textual is not installed in this environment"
)

from gitbook_downloader.tui.testing import FakeEngine  # noqa: E402
from gitbook_downloader.tui.widgets import NavBar  # noqa: E402


def run_async(coro):
    return asyncio.run(coro)


def make_app(engine=None):
    from gitbook_downloader.tui.app import GitbookDownloaderApp

    engine = engine or FakeEngine()
    opened: list[str] = []
    app = GitbookDownloaderApp(engine=engine, opener=opened.append)
    return app, engine, opened


async def wait_until(pilot, predicate, timeout=5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        await pilot.pause()
        if predicate():
            return True
    await pilot.pause()
    return predicate()


def test_app_launches_dark_with_five_surfaces():
    async def scenario():
        app, _engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            assert app.theme == "gb-dark"
            tabs = app.query_one("TabbedContent")
            assert tabs.active == "wizard"
            from textual.widgets import TabbedContent

            panes = list(app.query("TabPane"))
            assert len(panes) == 5
            del pilot

    run_async(scenario())


def test_digit_keys_switch_surfaces_when_not_typing():
    async def scenario():
        app, _engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            tabs = app.query_one("TabbedContent")
            app.set_focus(None)
            await pilot.pause()
            await pilot.press("3")
            assert await wait_until(pilot, lambda: tabs.active == "search")
            await pilot.press("5")
            assert await wait_until(pilot, lambda: tabs.active == "diagnostics")
            await pilot.press("1")
            assert await wait_until(pilot, lambda: tabs.active == "wizard")

    run_async(scenario())


def test_digit_keys_type_into_focused_input():
    """Digits must reach an Input, not hijack navigation."""
    async def scenario():
        app, _engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            wizard = app.surface("wizard")
            url_input = wizard.query_one("#url-input")
            url_input.focus()
            await pilot.press(*"https://docs2.example5.com")
            assert url_input.value == "https://docs2.example5.com"
            tabs = app.query_one("TabbedContent")
            assert tabs.active == "wizard"

    run_async(scenario())


def test_theme_toggle_via_key_and_nav_button():
    async def scenario():
        app, _engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            navbar = app.query_one(NavBar)
            toggle = navbar.query_one("#theme-toggle")

            app.set_focus(None)
            await pilot.pause()
            await pilot.press("ctrl+t")
            assert await wait_until(pilot, lambda: app.theme == "gb-light")
            assert toggle.label == "Dark"

            await pilot.click("#theme-toggle")
            assert await wait_until(pilot, lambda: app.theme == "gb-dark")
            assert toggle.label == "Light"

    run_async(scenario())


def test_nav_bar_buttons_switch_surface_and_mark_active():
    async def scenario():
        app, _engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            tabs = app.query_one("TabbedContent")
            await pilot.click("#nav-library")
            assert await wait_until(pilot, lambda: tabs.active == "library")
            active_btn = app.query_one("#nav-library")
            assert active_btn.has_class("active")
            assert not app.query_one("#nav-wizard").has_class("active")

    run_async(scenario())


def test_nav_bar_brand_shows_real_version():
    """The brand badge must show the real package version — the hardcoded
    ``v7`` predates the modular rewrite and never moved."""

    async def scenario():
        from gitbook_downloader import __version__

        app, _engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            await pilot.pause()
            navbar = app.query_one(NavBar)
            brand = navbar.query_one("#brand")
            text = str(brand.render())
            assert f"v{__version__}" in text
            assert "v7" not in text

    run_async(scenario())


def test_show_surface_refreshes_diagnostics_from_state():
    async def scenario():
        app, _engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            # No run yet -> empty state visible.
            app.show_surface("diagnostics")
            await pilot.pause()
            diag = app.surface("diagnostics")
            assert not diag.query_one("#diag-empty").has_class("hidden")

            # Fabricate a run, switch away and back; report must appear.
            from gitbook_downloader.tui.engine_protocol import (
                CaptureOptions,
                CaptureResult,
                Detection,
            )

            app.record_run(
                url="https://docs.example.com",
                options=CaptureOptions(),
                detection=Detection(provider="gitbook", evidence="meta generator"),
                result=CaptureResult(
                    source_url="https://docs.example.com",
                    provider="gitbook",
                    site_versions_found=(),
                    pages_captured=7,
                    skipped=0,
                    warnings=(),
                    library_path=None,
                    local_path=None,
                    book_file=None,
                    manifest_file=None,
                    version_id=None,
                ),
                duration_s=1.0,
                event_counts={},
            )
            app.show_surface("wizard")
            await pilot.pause()
            app.show_surface("diagnostics")
            assert await wait_until(
                pilot,
                lambda: diag.query_one("#diag-cards").has_class("hidden") is False,
            )
            provider_line = str(diag.query_one("#diag-provider-line").content)
            assert "GITBOOK" in provider_line

    run_async(scenario())
