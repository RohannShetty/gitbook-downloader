"""Pilot tests — Diagnostics: per-capture explanation, empty + failure states."""

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

from textual.widgets import Static  # noqa: E402

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


async def run_capture(app, pilot):
    wizard = app.surface("wizard")
    url_input = wizard.query_one("#url-input")
    url_input.focus()
    await pilot.press(*"https://docs.example.com")
    await pilot.press("enter")
    assert await wait_until(
        pilot,
        lambda: "Detected" in str(wizard.query_one("#detect-line", Static).content),
    )
    btn = wizard.query_one("#start-btn")
    btn.focus()
    await pilot.press("enter")
    summary = wizard.query_one("#summary-card")
    assert await wait_until(pilot, lambda: not summary.has_class("hidden"))


def test_diagnostics_starts_empty():
    async def scenario():
        app, _engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            app.show_surface("diagnostics")
            await pilot.pause()
            diag = app.surface("diagnostics")
            empty = diag.query_one("#diag-empty")
            assert not empty.has_class("hidden")
            text = str(empty.content)
            assert "No capture yet" in text
            assert diag.query_one("#diag-cards").has_class("hidden")

    run_async(scenario())


def test_diagnostics_explains_provider_scope_warnings_and_output():
    async def scenario():
        app, _engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            await run_capture(app, pilot)

            app.show_surface("diagnostics")
            await pilot.pause()
            diag = app.surface("diagnostics")
            assert await wait_until(
                pilot, lambda: not diag.query_one("#diag-cards").has_class("hidden")
            )

            provider_line = str(diag.query_one("#diag-provider-line", Static).content)
            assert "MINTLIFY" in provider_line
            evidence = str(diag.query_one("#diag-evidence", Static).content)
            assert "generator meta tag" in evidence

            scoping = str(diag.query_one("#diag-scoping", Static).content)
            assert "whole site" in scoping
            assert "all detected" in scoping
            assert "8" in scoping  # workers row

            activity = str(diag.query_one("#diag-activity", Static).content)
            assert "42" in activity
            assert "3" in activity  # skipped

            warnings = str(diag.query_one("#diag-warnings", Static).content)
            assert "soft-200" in warnings

            output = str(diag.query_one("#diag-output", Static).content)
            assert "llms.txt" in output
            assert "v1.0.4" in output  # snapshot id from the canned result

    run_async(scenario())


def test_diagnostics_reports_failed_runs():
    async def scenario():
        app, _engine, _opened = make_app(
            FakeEngine(capture_error=RuntimeError("dns lookup failed"))
        )
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            wizard = app.surface("wizard")
            url_input = wizard.query_one("#url-input")
            url_input.focus()
            await pilot.press(*"https://docs.example.com")
            await pilot.press("enter")
            assert await wait_until(
                pilot,
                lambda: "Detected"
                in str(wizard.query_one("#detect-line", Static).content),
            )
            btn = wizard.query_one("#start-btn")
            btn.focus()
            await pilot.press("enter")
            banner = wizard.query_one("#error-banner")
            assert await wait_until(pilot, lambda: not banner.has_class("hidden"))

            app.show_surface("diagnostics")
            await pilot.pause()
            diag = app.surface("diagnostics")
            assert await wait_until(
                pilot, lambda: not diag.query_one("#diag-cards").has_class("hidden")
            )
            activity = str(diag.query_one("#diag-activity", Static).content)
            assert "dns lookup failed" in activity
            warnings = str(diag.query_one("#diag-warnings", Static).content)
            assert "Not applicable" in warnings

    run_async(scenario())
