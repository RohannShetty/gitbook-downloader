"""CommandMenu fake-shortcuts regression.

The CommandMenu used to display ``Tab 1``..``Tab 6`` as CommandShortcut
values. The real key bindings in the app are ``Ctrl+K`` (command palette),
``1``..``5`` (TUI-style tab switch), ``Ctrl+T`` (theme), and ``Ctrl+R``
(diagnostics refresh). This test fails if the fake ``Tab N`` strings return.
"""

from __future__ import annotations

from pathlib import Path
import re

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMAND_MENU = REPO_ROOT / "frontend" / "src" / "components" / "CommandMenu.tsx"


def test_command_menu_no_tab_n_shortcut() -> None:
    """None of the fake ``Tab 1``..``Tab 6`` shortcut strings may remain."""
    text = COMMAND_MENU.read_text(encoding="utf-8")
    for n in range(1, 7):
        token = f"Tab {n}"
        assert token not in text, (
            f"{COMMAND_MENU.name} still contains the fake shortcut {token!r}. "
            f"Replace with the real binding (1..5 for tabs, no binding for "
            f"the 6th)."
        )


def test_command_menu_documents_real_bindings() -> None:
    """The real keybindings must be visible in the menu or the file."""
    text = COMMAND_MENU.read_text(encoding="utf-8")
    for binding in ("Ctrl+K", "Ctrl+T", "Ctrl+R"):
        assert binding in text, (
            f"{COMMAND_MENU.name} should document the real binding {binding!r}"
        )


def test_command_menu_tab_shortcuts_are_digits() -> None:
    """The five tab CommandShortcut values must be 1..5 (not fake Tab N)."""
    text = COMMAND_MENU.read_text(encoding="utf-8")
    # Locate the CommandShortcut chips. There should be at least 5 of them
    # with values 1..5 for the navigation items.
    chips = re.findall(r"<CommandShortcut[^>]*>([^<]+)</CommandShortcut>", text)
    digit_chips = [c for c in chips if c.strip() in {"1", "2", "3", "4", "5"}]
    assert len(digit_chips) >= 5, (
        f"Expected at least 5 CommandShortcut chips with values 1..5 in "
        f"{COMMAND_MENU.name}, got {len(digit_chips)} (all chips: {chips!r})"
    )
