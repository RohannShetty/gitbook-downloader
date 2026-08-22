"""Pilot tests — Library: table render, detail strip, delete modal, empty state."""

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

from textual.widgets import DataTable, Static  # noqa: E402

from gitbook_downloader.tui.testing import FakeEngine  # noqa: E402
from gitbook_downloader.tui.widgets import ConfirmModal  # noqa: E402


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


def go_library(app):
    app.show_surface("library")
    return app.surface("library")


def test_library_lists_domains_with_tabular_data():
    async def scenario():
        app, _engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            library = go_library(app)
            table = library.query_one("#domains-table", DataTable)
            assert await wait_until(pilot, lambda: table.row_count == 2)

            # First row is the most recently crawled domain.
            first_domain_cell = str(table.get_row_at(0)[0])
            assert "docs.example.com" in first_domain_cell

            detail = str(library.query_one("#library-detail", Static).content)
            assert "Example Product Docs" in detail
            assert "4 snapshots" in detail

    run_async(scenario())


def test_delete_flow_requires_confirmation_then_removes_row():
    async def scenario():
        app, engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            library = go_library(app)
            table = library.query_one("#domains-table", DataTable)
            assert await wait_until(pilot, lambda: table.row_count == 2)

            library.action_delete()
            assert await wait_until(
                pilot,
                lambda: any(isinstance(s, ConfirmModal) for s in app.screen_stack),
            )
            modal = next(
                s for s in app.screen_stack if isinstance(s, ConfirmModal)
            )
            body = str(modal.query_one("#confirm-body").content)
            assert "docs.example.com" in body
            assert "cannot be undone" in body.lower()

            # Cancel keeps everything.
            await pilot.click("#confirm-cancel")
            assert await wait_until(
                pilot,
                lambda: not any(
                    isinstance(s, ConfirmModal) for s in app.screen_stack
                ),
            )
            assert table.row_count == 2

            # Confirm deletes.
            library.action_delete()
            assert await wait_until(
                pilot,
                lambda: any(isinstance(s, ConfirmModal) for s in app.screen_stack),
            )
            await pilot.click("#confirm-ok")
            assert await wait_until(pilot, lambda: table.row_count == 1)
            deletes = [c for c in engine.calls if c[0] == "delete_domain"]
            assert deletes and deletes[0][1][0] == "docs.example.com"

    run_async(scenario())


def test_open_folder_uses_injected_opener():
    async def scenario():
        app, _engine, opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            library = go_library(app)
            table = library.query_one("#domains-table", DataTable)
            assert await wait_until(pilot, lambda: table.row_count == 2)
            library.action_open_folder()
            await pilot.pause()
            assert len(opened) == 1
            assert "docs.example.com" in str(opened[0])

    run_async(scenario())


def test_empty_library_shows_empty_state():
    async def scenario():
        app, _engine, _opened = make_app(FakeEngine(library=[]))
        async with app.run_test(size=(120, 42)) as pilot:
            library = go_library(app)
            table = library.query_one("#domains-table", DataTable)
            empty = library.query_one("#library-empty")
            assert await wait_until(pilot, lambda: table.has_class("hidden"))
            assert not empty.has_class("hidden")
            text = str(empty.content)
            assert "No sources yet" in text
            assert "Press 1" in text  # keycap hint toward the Wizard

    run_async(scenario())
