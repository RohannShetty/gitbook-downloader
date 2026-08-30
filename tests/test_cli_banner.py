"""CLI banner dedupe regression.

After Phase 4 step 1, the ``cli._banner(title, char, width)`` helper yields
the three lines of a section banner. The previous 8 inline ``"─" * 60`` /
``"=" * 50`` blocks must be gone, replaced by ``_banner()`` calls.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CLI = REPO_ROOT / "src" / "gitbook_downloader" / "cli.py"


def _read_cli() -> str:
    return CLI.read_text(encoding="utf-8")


def test_banner_helper_exists() -> None:
    text = _read_cli()
    assert "def _banner(" in text, (
        f"{CLI.name} must define a `def _banner(...)` helper"
    )


def test_banner_helper_signature() -> None:
    text = _read_cli()
    # The signature must accept at least (title, char, width).
    m = re.search(r"def _banner\(([^)]+)\)", text)
    assert m is not None, "_banner() must be defined"
    params = [p.strip().split("=")[0].split(":")[0].strip() for p in m.group(1).split(",")]
    assert "title" in params, "_banner must accept a `title` parameter"
    assert "char" in params, "_banner must accept a `char` parameter"
    assert "width" in params, "_banner must accept a `width` parameter"


def test_no_inline_banner_literals() -> None:
    """The 8 inline ``"─" * 60`` / ``"=" * 50`` blocks must be gone."""
    text = _read_cli()
    # The exact patterns the plan called out:
    forbidden_patterns = [
        re.compile(r"print\(\"─\"\s*\*\s*\d+\)"),
        re.compile(r"print\(\"=\"\s*\*\s*\d+\)"),
        re.compile(r"print\(f?\"\{\s*'─'\s*\*\s*\d+\s*\}\"\)"),
        re.compile(r"print\(f?\"\{\s*\"─\"\s*\*\s*\d+\s*\}\"\)"),
        re.compile(r"print\(f?\"\{\s*\"=\"\s*\*\s*\d+\s*\}\"\)"),
        re.compile(r"print\(f\"\\n\{\s*'─'\s*\*"),
    ]
    matches = []
    for pattern in forbidden_patterns:
        for m in pattern.finditer(text):
            matches.append((pattern.pattern, m.group(0)))
    assert not matches, (
        f"{CLI.name} still has inline banner literals:\n"
        + "\n".join(f"  {p} → {m!r}" for p, m in matches)
    )


def test_banner_called_in_each_command() -> None:
    """The five commands (search/list/history/diff/config) should each call _banner()."""
    text = _read_cli()
    # Each command function should reference _banner. The capture command
    # also uses _banner for its top header.
    for cmd in ("cmd_search", "cmd_list", "cmd_history", "cmd_diff", "cmd_config", "cmd_capture", "_print_capture_result"):
        # Find the function definition and search the body for _banner(.
        idx = text.index(f"def {cmd}(")
        # 4000 chars is enough to cover each body.
        body = text[idx : idx + 4000]
        assert "_banner(" in body, (
            f"{cmd}() should use _banner() for its section header"
        )


def test_banner_returns_three_lines() -> None:
    """Smoke: _banner('hello') returns a 3-tuple of strings."""
    from gitbook_downloader.cli import _banner
    result = _banner("hello")
    assert isinstance(result, tuple)
    assert len(result) == 3
    top, title, bottom = result
    # The title line is "  hello" (the helper indents by 2 spaces).
    assert title == "  hello"
    # The top and bottom are the same character repeated `width` times.
    assert top == bottom
    assert len(top) >= 10  # at least 10 chars of rule
