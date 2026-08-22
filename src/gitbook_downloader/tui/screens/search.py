"""Search surface — FTS5 query box, ranked hits, highlighted snippets."""

from __future__ import annotations

from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, Input, Select, Static

from ..engine_protocol import SearchHit
from ..theme import format_count
from ..widgets import EmptyState, Kicker, PasteInput, esc, highlight_snippet


class HitCard(Static, can_focus=True):
    """One ranked result. Enter/click opens the source URL."""

    DEFAULT_CSS = """
    HitCard {
        background: $surface;
        border: solid $hairline;
        padding: 1 2;
        height: auto;
        margin-bottom: 1;
    }
    HitCard:hover {
        border: solid $hairline-strong;
    }
    HitCard:focus {
        border: solid $primary;
    }
    """
    BINDINGS = [("enter", "open_hit", "Open")]

    def __init__(self, hit: SearchHit, position: int, **kwargs) -> None:
        super().__init__(
            "\n".join(
                [
                    f"[dim]{position:02d}[/dim]  [b]{esc(hit.title)}[/b]",
                    highlight_snippet(hit.snippet),
                    f"[dim]{esc(hit.domain)}"
                    + (
                        f" · {esc(hit.section_heading)}"
                        if hit.section_heading
                        else ""
                    )
                    + f" · score {abs(hit.rank):.2f}[/dim]",
                ]
            ),
            markup=True,
            **kwargs,
        )
        self.hit = hit

    def action_open_hit(self) -> None:
        self.app.opener(self.hit.url)

    def on_click(self) -> None:
        self.action_open_hit()


class SearchSurface(VerticalScroll):
    DEFAULT_CSS = """
    SearchSurface {
        padding: 1 2;
        align-horizontal: center;
    }
    #search-controls {
        height: auto;
        margin-bottom: 1;
    }
    #search-query {
        width: 1fr;
    }
    #search-domain {
        width: 32;
        margin-left: 1;
    }
    #search-go {
        margin-left: 1;
    }
    #result-count {
        color: $ink-faint;
        margin-bottom: 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._domain_options: list[tuple[str, str]] = []

    def compose(self):
        yield Kicker("Search the Library")
        with Horizontal(id="search-controls"):
            yield PasteInput(
                placeholder='FTS5 query — e.g. workers OR timeout, "exact phrase"',
                id="search-query",
                classes="mono",
            )
            yield Select([], prompt="All domains", id="search-domain", allow_blank=True)
            yield Button("Search", variant="primary", id="search-go")
        yield Static("", id="result-count")
        yield VerticalScroll(id="results")

    def on_mount(self) -> None:
        # No autofocus here: the Wizard owns initial focus at launch.
        self.refresh_domains()

    def refresh_domains(self) -> None:
        select = self.query_one("#search-domain", Select)
        current = select.value
        options: list[tuple[str, str]] = []
        try:
            for entry in self.app.engine.list_library():
                options.append((entry.domain, entry.domain))
        except Exception:  # noqa: BLE001 — search still works without a filter
            options = []
        self._domain_options = options
        select.set_options(options)
        if current in {value for _, value in options}:
            select.value = current

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-query":
            self.run_search()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "search-go":
            self.run_search()

    def on_select_changed(self, event: Select.Changed) -> None:
        del event  # re-run only on explicit search to keep queries intentional

    def run_search(self) -> None:
        query = self.query_one("#search-query", Input).value.strip()
        results = self.query_one("#results", VerticalScroll)
        count_line = self.query_one("#result-count", Static)
        if not query:
            results.remove_children()
            count_line.update("")
            results.mount(
                EmptyState(
                    "Type a query",
                    "Full-text search across every captured page and section.",
                )
            )
            return
        domain_select = self.query_one("#search-domain", Select)
        raw_domain = domain_select.value
        # Blank selects hold a sentinel (Select.NULL), never a real string.
        domain = raw_domain if isinstance(raw_domain, str) and raw_domain else None
        try:
            hits = self.app.engine.search(query, domain=domain, limit=50)
        except Exception as exc:  # noqa: BLE001
            self.app.notify(f"Search failed: {exc}", severity="error")
            return
        results.remove_children()
        if not hits:
            count_line.update(f'0 results for "{esc(query)}"')
            results.mount(
                EmptyState(
                    "Nothing matched",
                    "Try fewer words, an OR query, or a prefix like config*.",
                )
            )
            return
        scope = f" · in {domain}" if domain else ""
        count_line.update(
            f'{format_count(len(hits))} results for "{esc(query)}"{scope}'
        )
        for i, hit in enumerate(hits, start=1):
            results.mount(HitCard(hit, i))

    def reset(self) -> None:
        self.query_one("#search-query", Input).value = ""
        self.query_one("#result-count", Static).update("")
        results = self.query_one("#results", VerticalScroll)
        results.remove_children()
        results.mount(
            EmptyState(
                "Type a query",
                "Full-text search across every captured page and section.",
            )
        )
        self.refresh_domains()
