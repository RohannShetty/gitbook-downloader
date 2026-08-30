"""Dead alias removal regression.

After Phase 4 step 2, the Python ``open_local_folder`` alias (which was
never typed in the frontend and never called) must be removed from
``src/gitbook_downloader/gui/bridge.py``. The TS side already had it
removed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PY_BRIDGE = REPO_ROOT / "src" / "gitbook_downloader" / "gui" / "bridge.py"
TS_BRIDGE = REPO_ROOT / "frontend" / "src" / "lib" / "bridge.ts"


def test_python_bridge_no_open_local_folder() -> None:
    text = PY_BRIDGE.read_text(encoding="utf-8")
    assert "def open_local_folder" not in text, (
        f"{PY_BRIDGE.name} still defines `def open_local_folder(...)` — "
        f"this was a dead alias of `open_folder`. Phase 4 step 2 removes it."
    )


def test_python_bridge_no_open_local_folder_call() -> None:
    """No remaining call to the removed method anywhere in the repo."""
    text = PY_BRIDGE.read_text(encoding="utf-8")
    assert "open_local_folder(" not in text, (
        f"{PY_BRIDGE.name} still references `open_local_folder(`. "
        f"All callers should use `open_folder` directly."
    )


def test_ts_bridge_no_open_local_folder() -> None:
    text = TS_BRIDGE.read_text(encoding="utf-8")
    assert "openLocalFolder" not in text, (
        f"{TS_BRIDGE.name} must not declare `openLocalFolder`"
    )


def test_open_folder_still_works() -> None:
    """Smoke: the kept `open_folder` method is still present and callable."""
    text = PY_BRIDGE.read_text(encoding="utf-8")
    assert "def open_folder" in text, "open_folder must still exist after alias removal"
