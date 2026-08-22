"""Shared TUI widgets: nav bar, kickers, empty states, confirm modal.

All chrome is flat surfaces + hairlines; the amber accent appears only on
the active nav marker, primary actions, and the theme toggle's current
state. No emoji, no gradients.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

# Surfaces in shell order; keys 1..5 map onto these.
SURFACES = (
    ("wizard", "Wizard"),
    ("library", "Library"),
    ("search", "Search"),
    ("diff", "Diff"),
    ("diagnostics", "Diagnostics"),
)


class PasteInput(Input):
    """Input whose Ctrl+V / Shift+Insert read the OS clipboard.

    Textual's stock Input paste reads the terminal's OSC-52 clipboard,
    which most Windows console hosts never populate — so pasting appeared
    dead (v7.0.1 fix). This subclass overrides the binding and delegates
    to the app's pyperclip-backed action.
    """

    BINDINGS = [
        Binding("ctrl+v", "app_paste", "Paste", show=False),
        Binding("shift+insert", "app_paste", "Paste", show=False),
    ]

    def action_app_paste(self) -> None:
        self.app.action_paste_clipboard()


class NavBar(Horizontal):
    """Persistent top bar: brand · surface switcher · theme toggle."""

    DEFAULT_CSS = """
    NavBar {
        height: auto;
        background: $panel;
        border-bottom: solid $hairline;
        padding: 0 1;
        align-vertical: middle;
    }
    #brand {
        width: auto;
        margin-right: 2;
        padding: 1 0 0 0;
    }
    #nav-spacer {
        width: 1fr;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._active = "wizard"

    def compose(self) -> ComposeResult:
        yield Static(
            "[b]gitbook-downloader[/b] [dim]v7[/dim]",
            id="brand",
            markup=True,
        )
        for i, (name, label) in enumerate(SURFACES, start=1):
            yield Button(f"{i} {label}", id=f"nav-{name}", classes="nav-btn")
        yield Static("", id="nav-spacer")
        yield Button("Dark", id="theme-toggle", classes="theme-btn")

    def mark_active(self, name: str) -> None:
        """Highlight the active surface button with the amber marker."""
        self._active = name
        for btn in self.query(".nav-btn"):
            btn.remove_class("active")
        active = self.query_one(f"#nav-{name}", Button)
        active.add_class("active")

    def set_theme_label(self, theme_name: str) -> None:
        self.query_one("#theme-toggle", Button).label = (
            "Light" if theme_name == "gb-dark" else "Dark"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid.startswith("nav-"):
            self.app.show_surface(bid.removeprefix("nav-"))
        elif bid == "theme-toggle":
            self.app.action_toggle_theme()


class Kicker(Static):
    """Uppercase dim section label — the quiet wayfinding device."""

    DEFAULT_CSS = """
    Kicker {
        color: $ink-faint;
        text-style: bold;
        padding: 0 0 0 0;
    }
    """

    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(text.upper(), markup=True, **kwargs)


class EmptyState(Static):
    """Centered quiet panel for empty/no-result states."""

    DEFAULT_CSS = """
    EmptyState {
        border: solid $hairline;
        background: transparent;
        padding: 2 4;
        content-align: center middle;
        color: $ink-muted;
    }
    """

    def __init__(self, title: str, hint: str = "", **kwargs) -> None:
        body = f"[b]{title}[/b]"
        if hint:
            body += f"\n[dim]{hint}[/dim]"
        super().__init__(body, markup=True, **kwargs)


class ConfirmModal(ModalScreen[bool]):
    """Destructive-action confirmation. dismiss(True) to proceed."""

    DEFAULT_CSS = """
    ConfirmModal {
        align: center middle;
        background: $background 60%;
    }
    #confirm-box {
        width: 64;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: solid $hairline-strong;
        padding: 1 2;
    }
    #confirm-title {
        text-style: bold;
        color: $error;
        margin-bottom: 1;
    }
    #confirm-actions {
        height: auto;
        margin-top: 1;
        align-horizontal: right;
    }
    #confirm-actions Button {
        margin-left: 1;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, title: str, body: str, confirm_label: str = "Delete") -> None:
        super().__init__()
        self._title = title
        self._body = body
        self._confirm_label = confirm_label

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="confirm-box"):
            yield Static(self._title, id="confirm-title", markup=True)
            yield Static(self._body, id="confirm-body", markup=True)
            with Horizontal(id="confirm-actions"):
                yield Button("Cancel", id="confirm-cancel", flat=True)
                yield Button(self._confirm_label, id="confirm-ok", variant="error")

    def action_cancel(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm-ok")


# ── Markup helpers (escape user text before injecting Rich markup) ───────


def esc(text: str) -> str:
    """Escape Rich markup brackets in arbitrary text."""
    return str(text).replace("[", "\\[")


def highlight_snippet(snippet: str) -> str:
    """Turn FTS5 ``<b>term</b>`` marks into terminal highlight marks.

    Uses ``[reverse]`` — theme-agnostic, reads as a true highlight block
    on both dark and light canvases.
    """
    text = esc(snippet)
    out: list[str] = []
    i = 0
    while i < len(text):
        if text.startswith("<b>", i):
            out.append("[reverse]")
            i += 3
        elif text.startswith("</b>", i):
            out.append("[/reverse]")
            i += 4
        else:
            out.append(text[i])
            i += 1
    return "".join(out)
