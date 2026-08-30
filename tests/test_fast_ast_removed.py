"""--fast-ast dead-flag regression.

The ``--fast-ast`` argparse argument was registered but never read and there
is no slow alternative. This test fails if the flag returns to argparse.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CLI = REPO_ROOT / "src" / "gitbook_downloader" / "cli.py"


def test_cli_no_fast_ast_flag() -> None:
    text = CLI.read_text(encoding="utf-8")
    # Look for the argparse add_argument line for --fast-ast.
    assert "--fast-ast" not in text, (
        f"{CLI.name} still registers the dead --fast-ast flag. The flag is "
        f"never read and has no slow alternative — remove it from argparse."
    )


def test_cli_help_does_not_mention_fast_ast() -> None:
    """Smoke: running the CLI's help must not list --fast-ast."""
    proc = subprocess.run(
        [sys.executable, "-m", "gitbook_downloader", "capture", "--help"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=30,
    )
    # The help output should not contain --fast-ast.
    assert "--fast-ast" not in proc.stdout, (
        "`gitbook-dl capture --help` still lists --fast-ast; remove it.\n"
        f"stdout: {proc.stdout[:1000]}"
    )
