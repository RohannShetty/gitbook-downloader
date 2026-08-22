"""GitbookDownloaderApp — the v7 TUI shell.

Five surfaces stay mounted in a tabbed shell so a running capture keeps
ticking while you browse the Library. Screens consume ONLY the injected
EngineProtocol; the real facade is imported lazily at launch.
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Footer, TabbedContent, TabPane

from .engine_protocol import (
    CaptureOptions,
    CaptureResult,
    Detection,
    EngineProtocol,
)
from .theme import BASE_TOKENS, DEFAULT_THEME, THEMES
from .widgets import NavBar, SURFACES


def _platform_open(target) -> None:
    """Open a folder or URL with the OS default handler."""
    target = str(target)
    if os.name == "nt":
        os.startfile(target)  # type: ignore[attr-defined]  # noqa: S606
    elif sys.platform == "darwin":
        subprocess.run(["open", target], check=False)
    else:
        subprocess.run(["xdg-open", target], check=False)


@dataclass
class AppState:
    """Shared state across surfaces; survives tab switches."""

    last_run: object | None = None  # CaptureRun | None (avoids import cycle)


class GitbookDownloaderApp(App[None]):
    TITLE = "gitbook-downloader"
    SUB_TITLE = "capture documentation sites as markdown"

    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("1", "show('wizard')", "Wizard"),
        Binding("2", "show('library')", "Library"),
        Binding("3", "show('search')", "Search"),
        Binding("4", "show('diff')", "Diff"),
        Binding("5", "show('diagnostics')", "Diagnostics"),
        Binding("ctrl+t", "toggle_theme", "Toggle theme"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(
        self,
        engine: EngineProtocol | None = None,
        opener=None,
    ) -> None:
        super().__init__()
        for theme in THEMES:
            self.register_theme(theme)
        self._engine = engine
        self.opener = opener or _platform_open
        self.state = AppState()

    def get_css_variables(self) -> dict[str, str]:
        """Guarantee design tokens exist at stylesheet parse time."""
        variables = super().get_css_variables()
        variables.update(BASE_TOKENS)
        return variables

    # ── engine seam: lazy real facade ────────────────────────────────

    @property
    def engine(self) -> EngineProtocol:
        if self._engine is None:
            from .real_engine import create_real_engine

            self._engine = create_real_engine()
        return self._engine

    # ── layout ───────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with Vertical(id="shell"):
            yield NavBar()
            with TabbedContent(initial="wizard"):
                for name, label in SURFACES:
                    with TabPane(label, id=name):
                        yield _surface_widget(name)
        yield Footer()

    def on_mount(self) -> None:
        self.theme = DEFAULT_THEME
        navbar = self.query_one(NavBar)
        navbar.mark_active("wizard")
        navbar.set_theme_label(self.theme)

    # ── surface plumbing ─────────────────────────────────────────────

    def surface(self, name: str):
        """Return a mounted surface widget by name."""
        return self.query_one(f"TabPane#{name} > *")

    def action_show(self, name: str) -> None:
        self.show_surface(name)

    def show_surface(self, name: str) -> None:
        tabs = self.query_one(TabbedContent)
        tabs.active = name
        self.query_one(NavBar).mark_active(name)
        if name == "diagnostics":
            self.surface("diagnostics").refresh_from_state()

    def action_toggle_theme(self) -> None:
        self.theme = "gb-light" if self.theme == "gb-dark" else "gb-dark"
        self.query_one(NavBar).set_theme_label(self.theme)

    # ── run bookkeeping ──────────────────────────────────────────────

    def record_run(
        self,
        *,
        url: str,
        options: CaptureOptions,
        detection: Detection | None,
        result: CaptureResult | None,
        duration_s: float,
        event_counts: dict[str, int],
        error: str | None = None,
    ):
        from .engine_protocol import CaptureRun

        run = CaptureRun(
            url=url,
            options=options,
            detection=detection,
            result=result,
            error=error,
            duration_s=duration_s,
            event_counts=event_counts,
        )
        self.state.last_run = run
        return run


def _surface_widget(name: str):
    """Instantiate the surface widget for a TabPane (local imports keep
    startup cheap and avoid circulars)."""
    if name == "wizard":
        from .screens.wizard import WizardSurface

        return WizardSurface(id="wizard-surface")
    if name == "library":
        from .screens.library import LibrarySurface

        return LibrarySurface(id="library-surface")
    if name == "search":
        from .screens.search import SearchSurface

        return SearchSurface(id="search-surface")
    if name == "diff":
        from .screens.diff import DiffSurface

        return DiffSurface(id="diff-surface")
    if name == "diagnostics":
        from .screens.diagnostics import DiagnosticsSurface

        return DiagnosticsSurface(id="diagnostics-surface")
    raise ValueError(f"unknown surface: {name}")


def run() -> None:
    """Entry point used by `gitbook-dl` (bare) and `python -m …tui`."""
    GitbookDownloaderApp().run()
