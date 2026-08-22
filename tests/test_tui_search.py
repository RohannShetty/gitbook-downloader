"""Pilot tests — Search: ranked hits, highlighted snippets, filters."""

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

from textual.widgets import Input, Select, Static  # noqa: E402

from gitbook_downloader.tui.screens.search import HitCard  # noqa: E402
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


def go_search(app):
    app.show_surface("search")
    return app.surface("search")


async def search_for(pilot, search_surface, query):
    box = search_surface.query_one("#search-query", Input)
    box.focus()
    box.value = ""
    await pilot.pause()
    await pilot.press(*query)
    await pilot.press("enter")
    return search_surface


def test_search_renders_ranked_hits_with_highlighted_snippets():
    async def scenario():
        app, _engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            surface = go_search(app)
            await search_for(pilot, surface, "workers")

            count_line = surface.query_one("#result-count", Static)
            assert await wait_until(
                pilot,
                lambda: "3 results" in str(count_line.content),
            )

            cards = list(surface.query(HitCard))
            assert len(cards) == 3
            first_plain = str(cards[0].content)
            assert "Configuration" in first_plain
            assert "score" in first_plain  # mono meta line present

            # Highlight markers survive as reverse-video spans in the
            # raw markup string (Static.content keeps the source markup).
            assert "[reverse]" in str(cards[0].content)

    run_async(scenario())


def test_search_domain_filter_narrows_results():
    async def scenario():
        app, engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            surface = go_search(app)
            select = surface.query_one("#search-domain", Select)
            select.value = "api.other.dev"
            await pilot.pause()
            await search_for(pilot, surface, "workers")

            count_line = surface.query_one("#result-count", Static)
            assert await wait_until(
                pilot,
                lambda: 'in api.other.dev' in str(count_line.content),
            )
            cards = list(surface.query(HitCard))
            assert len(cards) == 1
            searches = [c for c in engine.calls if c[0] == "search"]
            assert searches[-1][1][1] == "api.other.dev"

    run_async(scenario())


def test_search_no_results_and_empty_query_states():
    async def scenario():
        app, _engine, _opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            surface = go_search(app)

            # Empty query -> hint state.
            box = surface.query_one("#search-query", Input)
            box.focus()
            await pilot.press("enter")
            assert await wait_until(
                pilot,
                lambda: "Type a query"
                in str(surface.query_one("#results").children[0].content),
            )

            # No matches -> recovery hint.
            await search_for(pilot, surface, "zzznothingmatches")
            count_line = surface.query_one("#result-count", Static)
            assert await wait_until(
                pilot,
                lambda: '0 results' in str(count_line.content),
            )
            empty_child = surface.query_one("#results").children[0]
            assert "Nothing matched" in str(empty_child.content)

    run_async(scenario())


def test_hit_card_enter_opens_source_url_via_injected_opener():
    async def scenario():
        app, _engine, opened = make_app()
        async with app.run_test(size=(120, 42)) as pilot:
            for _ in range(5):
                await pilot.pause()
            surface = go_search(app)
            await search_for(pilot, surface, "workers")

            cards = list(surface.query(HitCard))
            assert await wait_until(pilot, lambda: len(cards) > 0)
            cards[0].focus()
            await pilot.press("enter")
            await pilot.pause()
            assert opened, "Enter on a hit card should open its URL"
            assert opened[0].startswith("https://docs.example.com/")

    run_async(scenario())
