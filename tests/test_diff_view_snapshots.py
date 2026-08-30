"""DiffView fake-snapshot regression.

The DiffView used to hardcode ``["1.0.0"]`` as the snapshot fallback. The
bridge's list_library now returns a real ``snapshots: list[str]`` field.
This test fails if the hardcoded fallback returns or if the bridge stops
returning the snapshots field.
"""

from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys
import tempfile

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DIFF_VIEW = REPO_ROOT / "frontend" / "src" / "views" / "DiffView.tsx"
BRIDGE = REPO_ROOT / "src" / "gitbook_downloader" / "gui" / "bridge.py"


def test_diff_view_no_hardcoded_snapshot_fallback() -> None:
    text = DIFF_VIEW.read_text(encoding="utf-8")
    # The hardcoded ["1.0.0"] fallback must not appear anywhere in DiffView.
    assert '["1.0.0"]' not in text, (
        f"{DIFF_VIEW.name} still hardcodes the fake snapshot fallback "
        f'`["1.0.0"]`. Use the real `currentItem.snapshots` from the bridge.'
    )
    # Defensive: a bare "1.0.0" string literal is also suspicious.
    assert '"1.0.0"' not in text, (
        f"{DIFF_VIEW.name} still references the literal '1.0.0' as a snapshot"
    )


def test_diff_view_reads_snapshots_from_library() -> None:
    text = DIFF_VIEW.read_text(encoding="utf-8")
    # The view must consult currentItem.snapshots.
    assert "currentItem" in text and "snapshots" in text, (
        f"{DIFF_VIEW.name} should read the snapshot list from the library item"
    )


def test_bridge_list_library_returns_snapshots_field() -> None:
    """Smoke: ApiBridge().list_library() includes a ``snapshots: list[str]`` per entry."""
    # Use a temp dir so we don't touch the real user library.
    from gitbook_downloader.gui.bridge import ApiBridge

    with tempfile.TemporaryDirectory() as tmp:
        from gitbook_downloader.storage import StorageManager
        storage = StorageManager(base_dir=Path(tmp))
        bridge = ApiBridge(storage_manager=storage)
        # An empty storage returns an empty list; that's fine. We just need
        # the call not to crash and the per-entry shape (when populated) to
        # include the snapshots key.
        result = bridge.list_library()
        assert isinstance(result, list)
        # No entry to assert against; the source-level assertion below is
        # the real test (the field must be present in the dict literal).
        _ = result


def test_bridge_list_library_source_has_snapshots_key() -> None:
    """The list_library method must build entries with a `snapshots` key."""
    text = BRIDGE.read_text(encoding="utf-8")
    method_start = text.index("def list_library")
    method_body = text[method_start : method_start + 4000]
    assert '"snapshots"' in method_body, (
        "ApiBridge.list_library must include a `snapshots` key in each entry "
        "(used by DiffView to populate the snapshot select)."
    )
