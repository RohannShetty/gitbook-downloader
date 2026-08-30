"""InstallModal invisible-text regression.

The install panel used to render the command at ``text-cyan/10`` which is
effectively invisible (10% opacity on a near-black background). This test
fails if the invisible token sneaks back in.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALL_MODAL = REPO_ROOT / "docs" / "components" / "InstallModal.tsx"


def test_install_modal_exists() -> None:
    assert INSTALL_MODAL.exists()


def test_install_modal_no_invisible_cyan_text() -> None:
    """The wrapping <div> and the <pre> must NOT use ``text-cyan/10``."""
    text = INSTALL_MODAL.read_text(encoding="utf-8")
    # The invisible token must not appear anywhere in the install panel.
    assert "text-cyan/10" not in text, (
        f"{INSTALL_MODAL.name} still uses the invisible `text-cyan/10` token "
        f"on the install command panel. Use `text-cyan/90` (or higher) so the "
        f"command is actually readable."
    )


def test_install_modal_uses_readable_cyan_text() -> None:
    """The install panel must use a readable cyan token (>= /80 opacity)."""
    text = INSTALL_MODAL.read_text(encoding="utf-8")
    # Match the readable tokens: text-cyan/80, text-cyan/90, text-cyan, or
    # text-cyan-XXX (the solid color). At least one must appear on the
    # command panel rendering.
    readable = re.search(r"text-cyan(?:-[0-9]+)?(?:/(?:[8-9]\d|100))?", text)
    assert readable is not None, (
        f"{INSTALL_MODAL.name} should use a readable `text-cyan*` token on "
        f"the install command panel"
    )
