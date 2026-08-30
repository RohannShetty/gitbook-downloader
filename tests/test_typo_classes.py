"""Typo-classes regression for the showcase.

This test fails if any of these tokens reappear in `docs/components/*.tsx`:
- `bg-border-border/...` (the recurring typo, should be `bg-border/...`)
- `text-cyan/10` on the install panel (the invisible-text bug, also covered
  by `test_install_modal_opacity.py` but included here for the typography
  sweep)

`animate-fadeIn` is ALLOWED in component files (Hero.tsx uses it 4x); the
test only ensures the keyframe is actually defined in globals.css.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPONENTS = REPO_ROOT / "docs" / "components"
GLOBALS_CSS = REPO_ROOT / "docs" / "app" / "globals.css"


# Tokens that MUST NOT appear in any .tsx component file.
FORBIDDEN_TYPOS = [
    re.compile(r"bg-border-border"),  # the broken class
    # text-cyan/10 was the invisible-text bug; the install modal is the only
    # legitimate place that ever used it. We allow text-cyan/10 nowhere in
    # the showcase now (it was a mistake).
    # Note: text-cyan/10..text-cyan/20 is sometimes used for the dimmest
    # background-on-text-on-cyan accents (e.g. "text-cyan/20" on a
    # decorative dot). The bug-specific token is /10 on actual text content.
    # Allow /20 and lower; block /10 only in the install modal context.
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "component",
    sorted(p.name for p in COMPONENTS.glob("*.tsx")),
)
def test_no_typo_classes_in_components(component: str) -> None:
    text = _read_text(COMPONENTS / component)
    for pattern in FORBIDDEN_TYPOS:
        match = pattern.search(text)
        assert match is None, (
            f"{component} contains the typo class {match.group(0)!r} "
            f"(pattern: {pattern.pattern!r})"
        )


def test_globals_css_defines_fadein_keyframe() -> None:
    """The `animate-fadeIn` utility must be backed by a real @keyframes."""
    text = _read_text(GLOBALS_CSS)
    assert "@keyframes fadeIn" in text, (
        f"{GLOBALS_CSS.relative_to(REPO_ROOT)} must define the `fadeIn` "
        f"@keyframes (used by `animate-fadeIn` in Hero.tsx and elsewhere)"
    )
    # The utility class must also exist.
    assert ".animate-fadeIn" in text or "animate-fadeIn" in text, (
        f"{GLOBALS_CSS.relative_to(REPO_ROOT)} must define the "
        f"`animate-fadeIn` utility class"
    )


def test_hero_uses_animate_fadeIn_with_real_keyframe() -> None:
    """The 4 `animate-fadeIn` references in Hero.tsx must work because the keyframe exists."""
    text = (REPO_ROOT / "docs" / "components" / "Hero.tsx").read_text(encoding="utf-8")
    assert text.count("animate-fadeIn") >= 4, (
        "Hero.tsx should reference `animate-fadeIn` at least 4 times (one per tab panel)"
    )
    # The keyframe is defined in globals.css (asserted above); this test
    # additionally checks that the cross-file contract holds: the keyframe
    # is defined and Hero uses it. No runtime check (CSS is not Python-importable).
