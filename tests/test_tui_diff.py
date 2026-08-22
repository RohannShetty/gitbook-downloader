"""Pilot tests — Diff: snapshot pickers, changed-pages table, excerpt panes."""

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

from textual.widgets import DataTable, Select, Static  # noqa: E402

from gitbook_downloader.tui.testing import FakeEngine  # noqa: E402


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


def go_diff(app):
    app.show_surface("diff")
    return app.surface("diff")


async def pick_domain(pilot, surface, domain="docs.example.com"):
    select = surface.query_one("#diff-domain", Select)
    select.value = domain
    assert await wait_until(
        pilot,
        lambda: len(list(surface.query_one("#diff-old", Select)._options)) >= 2
        if hasattr(surface.query_one("#diff-old", Select), "_options")
        else True,
    )
    await pilot.pause()


def test_compare_renders_changed_pages_and_summary():
    async def scenario():
        app, engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            surface = go_diff(app)

            domain_sel = surface.query_one("#diff-domain", Select)
            domain_sel.value = "docs.example.com"
            await pilot.pause()

            # Snapshot selects auto-fill newest and previous.
            old_sel = surface.query_one("#diff-old", Select)
            new_sel = surface.query_one("#diff-new", Select)
            assert old_sel.value == "v1.0.1"
            assert new_sel.value == "v1.1.0"

            await pilot.click("#compare-btn")
            table = surface.query_one("#changes-table", DataTable)
            assert await wait_until(pilot, lambda: table.row_count == 4)

            summary = str(surface.query_one("#diff-summary", Static).content)
            assert "docs.example.com" in summary
            assert "v1.0.1" in summary and "v1.1.0" in summary
            assert "2 changed" in summary and "1 added" in summary
            assert "35 unchanged" in summary

            panes = surface.query_one("#diff-panes")
            assert not panes.has_class("hidden")

            diffs = [c for c in engine.calls if c[0] == "diff_snapshots"]
            assert diffs == [("diff_snapshots", ("docs.example.com", "v1.0.1", "v1.1.0"), {})]

    run_async(scenario())


def test_selecting_a_change_shows_before_after_excerpts():
    async def scenario():
        app, _engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            surface = go_diff(app)
            domain_sel = surface.query_one("#diff-domain", Select)
            domain_sel.value = "docs.example.com"
            await pilot.pause()
            await pilot.click("#compare-btn")

            table = surface.query_one("#changes-table", DataTable)
            assert await wait_until(pilot, lambda: table.row_count == 4)

            # First row is a "changed" page with excerpts.
            table.move_cursor(row=0)
            await pilot.pause()
            old_text = str(surface.query_one("#old-excerpt", Static).content)
            new_text = str(surface.query_one("#new-excerpt", Static).content)
            assert "npm install" in old_text
            assert "uv tool install" in new_text

    run_async(scenario())


def test_identical_snapshots_show_quiet_state():
    async def scenario():
        from gitbook_downloader.tui.engine_protocol import DiffReport

        empty_report = DiffReport(
            domain="docs.example.com",
            old_version="v1.0.0",
            new_version="v1.0.0",
            changes=(),
            unchanged_pages=37,
        )
        app, _engine, _opened = make_app(FakeEngine(diff=empty_report))
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            surface = go_diff(app)
            domain_sel = surface.query_one("#diff-domain", Select)
            domain_sel.value = "docs.example.com"
            await pilot.pause()
            await pilot.click("#compare-btn")

            empty = surface.query_one("#diff-empty")
            assert await wait_until(
                pilot, lambda: not empty.has_class("hidden")
            )
            assert "identical" in str(empty.content)

    run_async(scenario())
