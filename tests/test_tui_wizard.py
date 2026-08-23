"""Pilot tests — Wizard: detection, version checkboxes, capture, summary."""

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

from textual.widgets import Checkbox, Input, Static  # noqa: E402

from gitbook_downloader.tui.testing import FakeEngine  # noqa: E402


def run_async(coro):
    return asyncio.run(coro)


def make_app(engine=None):
    from gitbook_downloader.tui.app import GitbookDownloaderApp

    engine = engine or FakeEngine()
    opened: list[str] = []
    app = GitbookDownloaderApp(engine=engine, opener=opened.append)
    return app, engine, opened


async def wait_until(pilot, predicate, timeout=6.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        await pilot.pause()
        if predicate():
            return True
    await pilot.pause()
    return predicate()


async def detect_url(pilot, wizard, url="https://docs.example.com"):
    url_input = wizard.query_one("#url-input", Input)
    url_input.focus()
    await pilot.press(*url)
    wizard._run_detect()
    assert await wait_until(
        pilot,
        lambda: "Detected" in str(wizard.query_one("#detect-line", Static).content),
    )


def start_capture_via_keyboard(pilot, wizard):
    """Focus the primary action and press Enter (deterministic press)."""
    btn = wizard.query_one("#start-btn")
    btn.focus()
    return pilot.press("enter")


def test_wizard_happy_path_detection_to_summary():
    async def scenario():
        app, engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            wizard = app.surface("wizard")

            await detect_url(pilot, wizard)
            line = str(wizard.query_one("#detect-line", Static).content)
            assert "Detected:" in line
            assert "mintlify" in line
            assert "generator meta tag" in line

            # Multiple site versions detected -> checkboxes appear, all on.
            box = wizard.query_one("#versions-box")
            assert not box.has_class("hidden")
            boxes = list(box.query(Checkbox))
            assert [str(b.label) for b in boxes] == ["v1", "v2"]
            assert all(b.value for b in boxes)

            await start_capture_via_keyboard(pilot, wizard)

            summary = wizard.query_one("#summary-card")
            assert await wait_until(pilot, lambda: not summary.has_class("hidden"))

            head = str(wizard.query_one("#summary-head", Static).content)
            assert "MINTLIFY" in head
            assert "42" in head and "pages captured" in head

            status = str(wizard.query_one("#status-line", Static).content)
            assert "Captured 42 pages" in status

            paths = str(wizard.query_one("#summary-paths", Static).content)
            assert "docs.example.com" in paths
            assert "llms.txt" in paths

            warnings = str(wizard.query_one("#summary-warnings", Static).content)
            assert "soft-200" in warnings

            run = app.state.last_run
            assert run is not None and run.result is not None
            assert run.result.provider == "mintlify"
            assert run.detection is not None
            # Scripted timeline: 6 pages found, one fails mid-run.
            assert run.event_counts.get("downloaded") == 5
            assert run.event_counts.get("failed") == 1

            captures = [c for c in engine.calls if c[0] == "capture"]
            assert len(captures) == 1
            options_used = captures[0][1][1]
            assert options_used.snapshot is True
            assert options_used.path_scope == ()
            assert options_used.site_versions is None  # all versions == no filter

    run_async(scenario())


def test_wizard_enter_in_url_input_immediately_starts_capture():
    async def scenario():
        app, engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            wizard = app.surface("wizard")

            url_input = wizard.query_one("#url-input", Input)
            url_input.focus()
            await pilot.press(*"https://docs.example.com")
            await pilot.press("enter")

            summary = wizard.query_one("#summary-card")
            assert await wait_until(pilot, lambda: not summary.has_class("hidden"))

            captures = [c for c in engine.calls if c[0] == "capture"]
            assert len(captures) == 1
            assert captures[0][1][0] == "https://docs.example.com"

    run_async(scenario())


def test_wizard_scope_and_exclude_patterns_reach_the_engine():
    async def scenario():
        app, engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            wizard = app.surface("wizard")
            await detect_url(pilot, wizard)

            wizard.query_one("#scope-input", Input).value = "/api/, /guides/"
            wizard.query_one("#exclude-input", Input).value = "/blog/, /forum/"

            await start_capture_via_keyboard(pilot, wizard)
            summary = wizard.query_one("#summary-card")
            assert await wait_until(pilot, lambda: not summary.has_class("hidden"))

            captures = [c for c in engine.calls if c[0] == "capture"]
            options_used = captures[0][1][1]
            assert options_used.path_scope == ("/api/", "/guides/")
            assert options_used.exclude_paths == ("/blog/", "/forum/")

    run_async(scenario())


def test_wizard_unchecking_a_version_filters_site_versions():
    async def scenario():
        app, engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            wizard = app.surface("wizard")
            await detect_url(pilot, wizard)

            boxes = list(wizard.query_one("#versions-box").query(Checkbox))
            boxes[0].value = False  # uncheck v1 -> keep only v2

            await start_capture_via_keyboard(pilot, wizard)
            summary = wizard.query_one("#summary-card")
            assert await wait_until(pilot, lambda: not summary.has_class("hidden"))

            captures = [c for c in engine.calls if c[0] == "capture"]
            options_used = captures[0][1][1]
            assert options_used.site_versions == ("v2",)

    run_async(scenario())


def test_wizard_capture_failure_shows_error_banner_and_records_run():
    async def scenario():
        app, _engine, _opened = make_app(
            FakeEngine(capture_error=RuntimeError("connection refused"))
        )
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            wizard = app.surface("wizard")
            await detect_url(pilot, wizard)

            await start_capture_via_keyboard(pilot, wizard)
            banner = wizard.query_one("#error-banner", Static)
            assert await wait_until(
                pilot,
                lambda: not banner.has_class("hidden")
                and "connection refused" in str(banner.content),
            )
            # Form is usable again.
            assert wizard.query_one("#form-region").disabled is False
            run = app.state.last_run
            assert run is not None and run.result is None
            assert run.error == "connection refused"

    run_async(scenario())


def test_wizard_invalid_url_is_rejected_before_any_engine_call():
    async def scenario():
        app, engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            wizard = app.surface("wizard")
            url_input = wizard.query_one("#url-input", Input)
            url_input.focus()
            await pilot.press(*"not a url")
            await pilot.press("enter")  # triggers detection attempt -> rejected

            line = str(wizard.query_one("#detect-line", Static).content)
            assert "http(s)" in line

            await start_capture_via_keyboard(pilot, wizard)
            await pilot.pause()
            assert not any(name == "capture" for name, _, _ in engine.calls)
            assert not any(name == "detect" for name, _, _ in engine.calls)

    run_async(scenario())


def test_library_recrawl_prefills_wizard_url():
    async def scenario():
        app, _engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            library = app.surface("library")
            wizard = app.surface("wizard")
            library.action_recrawl()
            tabs = app.query_one("TabbedContent")
            assert tabs.active == "wizard"
            assert (
                wizard.query_one("#url-input", Input).value
                == "https://docs.example.com/"
            )
            assert await wait_until(
                pilot,
                lambda: "Detected"
                in str(wizard.query_one("#detect-line", Static).content),
            )

    run_async(scenario())


def test_wizard_cancel_capture_resets_form():
    async def scenario():
        app, _engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            wizard = app.surface("wizard")
            wizard._capture_running = True
            wizard.action_cancel_capture()
            assert wizard._capture_running is False
            banner = wizard.query_one("#error-banner", Static)
            assert "cancelled" in str(banner.content).lower()

    run_async(scenario())
