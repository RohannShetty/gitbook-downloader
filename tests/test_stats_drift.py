"""Stats drift regression.

Single source of truth for DocHarvest marketing stats: ``docs/lib/stats.ts``.

This test fails if any of the hardcoded magic numbers that previously appeared
across Hero, AgentEcosystemShowcase, PersonaShowcase, or ExportStudioPreview
are re-introduced.

After Phase 1 step 2:
- All copy using ``15+``, ``12+``, ``11+``, ``89%``, ``364``, ``18.2``,
  ``20.0`` must read from ``STATS.*``.
- ``docs/lib/stats.ts`` is the only file that defines these numbers; any
  duplicate literal in the components is a regression.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = REPO_ROOT / "docs" / "components"
STATS_FILE = REPO_ROOT / "docs" / "lib" / "stats.ts"


# Magic-number literals that MUST NOT appear hardcoded in component files.
# The values (15, 12, 11, 89, 364, 18.2, 20.0) are tied to STATS fields.
# We allow them to appear in:
#   - docs/lib/stats.ts (the source of truth)
#   - tests, fixtures, and lockfiles (out of scope)
# We also allow them in CHANGELOG.md and AGENTS.md (historical notes).
DRIFT_PATTERNS = [
    re.compile(r"15\+ Harnesses"),
    re.compile(r"11\+ Modern Coding Harnesses"),
    re.compile(r"All 12\+ Harnesses"),
    re.compile(r"89% Reduction"),
    re.compile(r"89% prompt token reduction"),
    re.compile(r"364/364 HARVESTED"),
    re.compile(r"18\.2s"),
    re.compile(r"20\.0 pgs/sec"),
    # The combined terminal line uses spaces in `20.0 pages/sec` AND
    # `20.0 pgs/sec` — block both, including the dynamic one that would only
    # be valid if it's not from STATS.speedPagesPerSec.
    re.compile(r"20\.0 pages/sec"),
    # The STATUS footer in Hero.tsx uses `364` directly; that's a STATS value.
    # We grep for the pattern in terminal log lines by context.
    re.compile(r"364 pages harvested"),
    re.compile(r"Extracted 364 articles"),
    re.compile(r"total_pages: 364"),
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_stats_file_exists() -> None:
    assert STATS_FILE.exists(), (
        f"Expected {STATS_FILE.relative_to(REPO_ROOT)} to exist as the central "
        f"stats source of truth"
    )


def test_stats_file_exports_starts_object() -> None:
    text = _read_text(STATS_FILE)
    assert "export const STATS" in text, (
        f"{STATS_FILE.relative_to(REPO_ROOT)} must export a STATS object"
    )
    for field in (
        "agentsShipped",
        "harnesses",
        "pagesCaptured",
        "reductionPct",
        "speedPagesPerSec",
        "captureTimeSec",
    ):
        assert field in text, (
            f"STATS must include the {field!r} field"
        )


@pytest.mark.parametrize(
    "component",
    sorted(p for p in COMPONENTS_DIR.glob("*.tsx") if p.is_file()),
    ids=lambda p: p.name,
)
def test_no_hardcoded_stats_in_components(component: Path) -> None:
    text = _read_text(component)
    for pattern in DRIFT_PATTERNS:
        match = pattern.search(text)
        assert match is None, (
            f"{component.relative_to(REPO_ROOT)} contains hardcoded stat "
            f"literal {match.group(0)!r} (pattern: {pattern.pattern!r}). "
            f"Import STATS from '../lib/stats' instead."
        )


def test_hero_uses_stats_in_terminal_logs() -> None:
    """TERMINAL_LOGS in Hero.tsx must reference STATS (via template literals)."""
    text = _read_text(COMPONENTS_DIR / "Hero.tsx")
    assert "STATS" in text, (
        "Hero.tsx must import and use STATS — the live numbers should come "
        "from docs/lib/stats.ts, not from inline literals"
    )
    # Each STATS field should appear at least once in Hero.
    for field in (
        "STATS.pagesCaptured",
        "STATS.captureTimeSec",
        "STATS.speedPagesPerSec",
        "STATS.reductionPct",
        "STATS.harnesses",
    ):
        assert field in text, f"Hero.tsx should reference {field!r}"


def test_hero_no_legacy_hardcoded_harnesses_label() -> None:
    """Defence-in-depth: no `15+ Harnesses` literal can sneak back in."""
    text = _read_text(COMPONENTS_DIR / "Hero.tsx")
    assert "15+ Harnesses" not in text
    assert "12+ Harnesses" not in text
    assert "11+ Harnesses" not in text
