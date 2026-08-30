"""CLI --rag/--pdf path-conditional regression.

The ``--rag`` and ``--pdf`` post-capture export blocks used a path-conditional
ternary that mixed ``(base_out / "exports").exists()`` with ``result.local_path``
on the right-hand side of ``or`` — making the right-hand branch dead. The
fixed form is a straight ``if exports_dir.exists()`` choice.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CLI = REPO_ROOT / "src" / "gitbook_downloader" / "cli.py"


def _read_cli() -> str:
    return CLI.read_text(encoding="utf-8")


def test_cli_no_broken_or_local_path_ternary() -> None:
    """The broken pattern ``(...).exists() or result.local_path`` must be gone."""
    text = _read_cli()
    # The original bug pattern: a path `.exists()` chained with `or result.local_path`
    assert 'exists() or result.local_path' not in text, (
        f"{CLI.name} still has the broken path-conditional: "
        f"`(base_out / 'exports').exists() or result.local_path`. "
        f"Rewrite as a straight `if exports_dir.exists()`."
    )


def test_cli_rag_block_uses_straight_assignment() -> None:
    text = _read_cli()
    # The --rag block must use an `if exports_dir.exists():` pattern.
    # Find the --rag block by searching for `if getattr(args, "rag"`.
    rag_start = text.index('if getattr(args, "rag"')
    # Slice to the next blank line at column 0 (defensive).
    rag_block = text[rag_start : rag_start + 2000]
    assert "if exports_dir.exists():" in rag_block, (
        "The --rag block must use `if exports_dir.exists(): rag_dest = ...` "
        "as a straight conditional, not a one-line ternary with `or`."
    )


def test_cli_pdf_block_uses_straight_assignment() -> None:
    text = _read_cli()
    pdf_start = text.index('if getattr(args, "pdf"')
    pdf_block = text[pdf_start : pdf_start + 2000]
    assert "if exports_dir.exists():" in pdf_block, (
        "The --pdf block must use `if exports_dir.exists(): pdf_dest = ...` "
        "as a straight conditional, not a one-line ternary with `or`."
    )


def test_cli_rag_and_pdf_both_present() -> None:
    """Regression: ensure both blocks are not accidentally deleted."""
    text = _read_cli()
    assert 'if getattr(args, "rag"' in text, "--rag block is missing"
    assert 'if getattr(args, "pdf"' in text, "--pdf block is missing"
