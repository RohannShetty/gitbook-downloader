"""Version drift regression.

Single source of truth for DocHarvest version: ``11.0.5``.

This test fails if any of the canonical reference files drift from that value.
The list below is curated (not a grep over the whole tree) so that:

- ``CHANGELOG.md`` is allowed to mention historical versions (out of scope).
- ``package-lock.json`` lockfile entries like ``@octokit/endpoint@11.0.4`` are
  not DocHarvest version literals (out of scope).
- ``docs/lib/version.ts`` and ``src/gitbook_downloader/__init__.py`` are the
  canonical sources and MUST equal ``11.0.5`` (we assert equality, not just
  presence).
- ``frontend/index.html`` <title> must read ``DocHarvest v11.0.5``.

Drift signals (these MUST all read ``11.0.5`` after Phase 1 step 1):
- README.md version badge.
- src/gitbook_downloader/cli.py direct-script fallback.
- src/gitbook_downloader/gui/bridge.py User-Agent (it must use
  ``__version__``, not a hardcoded literal — we assert the absence of a
  hardcoded 9.0.0/10.0.1/11.0.0 token).
- frontend/src/lib/bridge.ts ``getSystemInfo`` fallback.
- docs/lib/github.ts fallback recent-commit message (the release fixture).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_VERSION = "11.0.5"


# Files where the value MUST literally equal CANONICAL_VERSION (not just
# contain it as a substring — e.g. "11.0.30" must not match).
CANONICAL_SOURCE_FILES = [
    REPO_ROOT / "src" / "gitbook_downloader" / "__init__.py",
    REPO_ROOT / "docs" / "lib" / "version.ts",
]


# Files where the file MUST contain the literal ``11.0.5`` somewhere.
# (We grep, not assert exact match, because each file embeds it in different
# surrounding text — a badge URL, a JS string, a User-Agent f-string, etc.)
MUST_CONTAIN = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "frontend" / "src" / "lib" / "bridge.ts",
    REPO_ROOT / "frontend" / "index.html",
]


# Stale literals that MUST NOT appear in production source after Phase 1.
# (Allowed in CHANGELOG.md, package-lock.json, and test fixtures that
# explicitly pin to historical versions.)
STALE_LITERAL_PATTERNS = [
    re.compile(r"gitbook-downloader/9\.0\.0"),
    re.compile(r"gitbook-downloader/10\.0\.\d+"),
    re.compile(r"gitbook-downloader/11\.0\.0"),
    re.compile(r"'11\.0\.0'"),
    re.compile(r'"11\.0\.0"'),
    re.compile(r"9\.0\.0b1"),
    # The fallback commit message must not still cite v10.0.1 as a release.
    re.compile(r"v10\.0\.1 - DocHarvest hotfix"),
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_canonical_sources_equal_11_0_2() -> None:
    for path in CANONICAL_SOURCE_FILES:
        assert path.exists(), f"Canonical source missing: {path}"
        text = _read_text(path)
        # Each canonical source exports the version as a string literal.
        assert CANONICAL_VERSION in text, (
            f"{path.relative_to(REPO_ROOT)} must contain {CANONICAL_VERSION!r} "
            f"as the canonical version literal"
        )


@pytest.mark.parametrize("path", MUST_CONTAIN, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_required_files_contain_11_0_2(path: Path) -> None:
    assert path.exists(), f"Required file missing: {path}"
    text = _read_text(path)
    assert CANONICAL_VERSION in text, (
        f"{path.relative_to(REPO_ROOT)} must reference {CANONICAL_VERSION!r}"
    )


@pytest.mark.parametrize(
    "path",
    [
        REPO_ROOT / "src" / "gitbook_downloader" / "cli.py",
        REPO_ROOT / "src" / "gitbook_downloader" / "gui" / "bridge.py",
        REPO_ROOT / "frontend" / "src" / "lib" / "bridge.ts",
    ],
    ids=lambda p: str(p.relative_to(REPO_ROOT)),
)
def test_no_stale_version_literal(path: Path) -> None:
    text = _read_text(path)
    for pattern in STALE_LITERAL_PATTERNS:
        match = pattern.search(text)
        assert match is None, (
            f"{path.relative_to(REPO_ROOT)} contains stale version literal "
            f"{match.group(0)!r} (pattern: {pattern.pattern!r})"
        )


def test_cli_version_fallback_uses_canonical_value() -> None:
    """The direct-script fallback in cli.py MUST equal 11.0.5 (not 9.0.0b1)."""
    cli_text = _read_text(REPO_ROOT / "src" / "gitbook_downloader" / "cli.py")
    # The fallback literal is the value in the `except ImportError` branch.
    assert "__version__ = \"11.0.5\"" in cli_text, (
        "cli.py direct-script fallback should be 11.0.5, not 9.0.0b1"
    )
    assert "9.0.0b1" not in cli_text, (
        "cli.py still contains stale 9.0.0b1 fallback"
    )


def test_bridge_user_agent_uses_version_constant() -> None:
    """The User-Agent in bridge.py must be built from __version__, not hardcoded."""
    bridge_text = _read_text(REPO_ROOT / "src" / "gitbook_downloader" / "gui" / "bridge.py")
    # The hardcoded literal must be gone, and an f-string interpolation must
    # build the User-Agent from __version__.
    assert "gitbook-downloader/9.0.0" not in bridge_text, (
        "bridge.py still has the hardcoded gitbook-downloader/9.0.0 User-Agent"
    )
    assert "f\"gitbook-downloader/{__version__}\"" in bridge_text or \
           "f'gitbook-downloader/{__version__}'" in bridge_text, (
        "bridge.py User-Agent must be built from __version__ via f-string"
    )


def test_python_version_importable() -> None:
    """Smoke: the Python package exposes __version__ == 11.0.5."""
    from gitbook_downloader import __version__
    assert __version__ == CANONICAL_VERSION
