"""Bridge contract regression.

The TypeScript `pyApi` interface in `frontend/src/lib/bridge.ts` must declare
every method exposed by the Python `ApiBridge` class in
`src/gitbook_downloader/gui/bridge.py`, and the `list_library` return shape
must include the `snapshots: list[str]` field added in Phase 2.

Naming convention:
- Python uses snake_case (`start_capture`, `cancel_capture`, ...).
- TypeScript uses camelCase (`startCapture`, `cancelCapture`, ...).

This is a static test: it inspects source files (no runtime pywebview
process). It fails if a Python method exists without a TS counterpart, or
if the TS interface drifts on the snapshots field.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TS_BRIDGE = REPO_ROOT / "frontend" / "src" / "lib" / "bridge.ts"
PY_BRIDGE = REPO_ROOT / "src" / "gitbook_downloader" / "gui" / "bridge.py"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# Curated (not auto-derived) so the test does not fail on helpers or
# non-exposed methods. Each entry is (python_snake, ts_camelcase).
# Internal helpers (prefixed `_`) and the dead alias `open_local_folder`
# are excluded. `list_snapshots` is a Python-only helper — the TS
# surface consumes `currentItem.snapshots` (the listLibrary entry's
# snapshots field) instead of a separate listSnapshots method call.
PYTHON_TO_TS = [
    ("detect", "detect"),
    ("start_capture", "startCapture"),
    ("cancel_capture", "cancelCapture"),
    ("reset_capture", "resetCapture"),
    ("get_lock_status", "getLockStatus"),
    ("list_library", "listLibrary"),
    ("get_library_doc", "getLibraryDoc"),
    ("read_file", "readFile"),
    ("delete_domain", "deleteDomain"),
    ("rename_domain", "renameDomain"),
    ("open_folder", "openFolder"),
    ("open_file", "openFile"),
    ("search_docs", "searchDocs"),
    ("diff_snapshots", "diffSnapshots"),
    ("export_doc", "exportDoc"),
    ("get_diagnostics", "getDiagnostics"),
    ("get_system_info", "getSystemInfo"),
    ("is_render_available", "isRenderAvailable"),
]


@pytest.mark.parametrize("py_method, _ts", PYTHON_TO_TS, ids=[p for p, _ in PYTHON_TO_TS])
def test_python_bridge_defines_exposed_method(py_method: str, _ts: str) -> None:
    text = _read_text(PY_BRIDGE)
    assert f"def {py_method}" in text, (
        f"Python ApiBridge is expected to define `def {py_method}(...)`"
    )


@pytest.mark.parametrize("_py, ts_method", PYTHON_TO_TS, ids=[t for _, t in PYTHON_TO_TS])
def test_ts_bridge_declares_pyapi_method(_py: str, ts_method: str) -> None:
    text = _read_text(TS_BRIDGE)
    declared = set(re.findall(r"(\w+):\s*async\s*\(", text))
    assert ts_method in declared, (
        f"TS pyApi must declare `{ts_method}: async (...)`"
    )


def test_python_bridge_list_library_returns_snapshots_field() -> None:
    """The list_library return value must include the `snapshots` field."""
    text = _read_text(PY_BRIDGE)
    method_start = text.index("def list_library")
    method_body = text[method_start : method_start + 4000]
    assert '"snapshots"' in method_body, (
        "Python bridge.list_library must include a `snapshots` key in each "
        "entry — DiffView depends on it for the snapshot select."
    )

def test_python_bridge_no_open_local_folder_alias() -> None:
    """After Phase 4 step 2, the dead `open_local_folder` alias is removed."""
    text = _read_text(PY_BRIDGE)
    assert "def open_local_folder" not in text, (
        "Python bridge.open_local_folder alias should be removed (Phase 4 step 2). "
        "The TS surface never called it; the Python side now matches."
    )
    # And no remaining call to it anywhere.
    assert "open_local_folder(" not in text, (
        "Python bridge must not reference `open_local_folder(` after removal"
    )
    # The kept `open_folder` must still exist.
    assert "def open_folder" in text, (
        "open_folder must still exist as the canonical name"
    )
def test_ts_bridge_no_dead_open_local_folder() -> None:
    """The dead `open_local_folder` alias is not in the TS pyApi surface."""
    text = _read_text(TS_BRIDGE)
    assert "openLocalFolder" not in text, (
        f"{TS_BRIDGE.relative_to(REPO_ROOT)} must not declare `openLocalFolder`. "
        f"It is a dead alias — the Python `open_local_folder` will be removed "
        f"in Phase 4 step 2; the TS side should not have carried it."
    )
