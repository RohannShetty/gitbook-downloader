"""Visual anchor regression for the showcase.

This test asserts static invariants on the showcase source files. It does
NOT spin up Playwright (the test infra uses static text inspection so it
runs on plain pytest without browser dependencies).

After Phase 3:
- Hero.tsx: STATUS: and TIME: are collapsed into a single line.
- InstallModal.tsx: install command renders at text-cyan/90 (readable).
- CaptureStudio.tsx: Batch tab has a button with text "Run Batch".
- DiffView.tsx: snapshot select lists only real snapshot IDs (no ["1.0.0"]
  hardcoded fallback; uses currentItem.snapshots from the bridge).
- Hero.tsx terminal logs and persona stats read from STATS (no hardcoded
  364, 18.2, 89, 15, 11, 12 literals).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
HERO = REPO_ROOT / "docs" / "components" / "Hero.tsx"
INSTALL_MODAL = REPO_ROOT / "docs" / "components" / "InstallModal.tsx"
CAPTURE_STUDIO = REPO_ROOT / "frontend" / "src" / "views" / "CaptureStudio.tsx"
DIFF_VIEW = REPO_ROOT / "frontend" / "src" / "views" / "DiffView.tsx"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── Hero.tsx ────────────────────────────────────────────────────────────


def test_hero_uses_stats_for_status_line() -> None:
    """The collapsed terminal footer line should reference STATS, not literals."""
    text = _read_text(HERO)
    # The collapsed line should mention pages, time, and pgs/sec via STATS.
    assert "STATS.pagesCaptured" in text, (
        "Hero.tsx must read the page count from STATS"
    )
    assert "STATS.captureTimeSec" in text, (
        "Hero.tsx must read the capture time from STATS"
    )
    assert "STATS.speedPagesPerSec" in text, (
        "Hero.tsx must read the speed from STATS"
    )


def test_hero_no_legacy_status_time_labels() -> None:
    """After Phase 3 edit 3, STATUS: and TIME: labels should be gone."""
    text = _read_text(HERO)
    assert "STATUS:" not in text, (
        "Hero.tsx still uses the redundant 'STATUS:' label in the terminal footer"
    )
    assert "TIME:" not in text, (
        "Hero.tsx still uses the redundant 'TIME:' label in the terminal footer"
    )


# ── InstallModal.tsx ─────────────────────────────────────────────────────


def test_install_modal_command_uses_readable_cyan() -> None:
    """The install command must be at text-cyan/90 (readable)."""
    text = _read_text(INSTALL_MODAL)
    # The wrapping <div> and the <pre> on the install panel must use the
    # readable token (>= /80 opacity).
    assert "text-cyan/90" in text, (
        f"{INSTALL_MODAL.name} should render the install command at "
        f"text-cyan/90 — anything dimmer (e.g. text-cyan/10) is invisible."
    )


# ── CaptureStudio.tsx ────────────────────────────────────────────────────


def test_capture_studio_batch_has_run_button() -> None:
    text = _read_text(CAPTURE_STUDIO)
    assert "Run Batch" in text, (
        f"{CAPTURE_STUDIO.name} must have a 'Run Batch' button in the Batch tab"
    )


def test_capture_studio_batch_has_cancel_button() -> None:
    text = _read_text(CAPTURE_STUDIO)
    assert "Cancel Batch" in text, (
        f"{CAPTURE_STUDIO.name} must have a 'Cancel Batch' button"
    )


# ── DiffView.tsx ─────────────────────────────────────────────────────────


def test_diff_view_uses_real_snapshots_field() -> None:
    text = _read_text(DIFF_VIEW)
    # The view must consult currentItem.snapshots (the new bridge field).
    assert "currentItem" in text and "snapshots" in text, (
        f"{DIFF_VIEW.name} must read snapshots from currentItem.snapshots"
    )


def test_diff_view_no_hardcoded_fallback() -> None:
    text = _read_text(DIFF_VIEW)
    assert '["1.0.0"]' not in text, (
        f"{DIFF_VIEW.name} still has the hardcoded ['1.0.0'] snapshot fallback"
    )
