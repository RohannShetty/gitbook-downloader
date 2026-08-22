"""TUI-side mirror of the pinned facade contract (plan §2) + read views.

The TUI never imports backend modules directly. Every screen talks to an
object satisfying :class:`EngineProtocol`, injected at app construction:

* ``capture`` mirrors ``api.capture(url, options, progress=...) -> CaptureResult``
  exactly as pinned in the master plan §2 (field names, order, defaults).
* The remaining methods are read views over the Library (list/search/
  snapshots/diff/delete) shaped after ``storage.manager.StorageManager`` and
  ``search.index.SearchIndex``, so the real adapter is a thin translation
  layer and pilot tests can inject :class:`tui.testing.FakeEngine`.

This module imports NOTHING from the backend and NOTHING from textual —
it is pure contract, safe to import in any environment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol, runtime_checkable

# ── Mirrored facade contract (PINNED — do not edit casually) ────────────


@dataclass(frozen=True)
class CaptureOptions:
    """Mirror of ``api.CaptureOptions`` (pinned §2)."""

    workers: int = 8                      # parallel fetches
    max_pages: int | None = None          # None = unlimited (0 is INVALID)
    path_scope: tuple[str, ...] = ()      # URL path prefixes to include
    exclude_paths: tuple[str, ...] = ()   # path patterns to skip inside scope
    site_versions: tuple[str, ...] | None = None  # None=all detected
    output_mode: str = "both"             # "both" | "library" | "local"
    local_dir: Path | None = None         # default ./<domain>-docs/
    snapshot: bool = True                 # snapshot previous before overwrite
    timeout: float = 20.0


@dataclass(frozen=True)
class CaptureResult:
    """Mirror of ``api.CaptureResult`` (pinned §2)."""

    source_url: str
    provider: str                  # gitbook|mintlify|docusaurus|readthedocs|mkdocs|generic
    site_versions_found: tuple[str, ...]
    pages_captured: int
    skipped: int                   # filtered/excluded/duplicate count
    warnings: tuple[str, ...]      # non-fatal issues surfaced to user
    library_path: Path | None
    local_path: Path | None
    book_file: Path | None
    manifest_file: Path | None     # llms.txt
    version_id: str | None         # snapshot id created, if snapshotting


@dataclass(frozen=True)
class ProgressEvent:
    """Mirror of the pinned progress-event vocabulary.

    ``kind`` is one of ``discovered | downloaded | failed | written``.
    Payload fields are intentionally permissive so the real facade's
    richer payloads translate losslessly.
    """

    kind: str
    url: str = ""
    message: str = ""
    done: int = 0
    total: int = 0


PROGRESS_KINDS = ("discovered", "downloaded", "failed", "written")

ProgressCallback = Callable[[ProgressEvent], None]

# ── Read-view value types ────────────────────────────────────────────────


@dataclass(frozen=True)
class Detection:
    """Pre-flight provider probe shown live in the Wizard."""

    provider: str                       # gitbook|mintlify|…|generic
    evidence: str = ""                  # e.g. "generator meta tag"
    site_versions: tuple[str, ...] = () # e.g. ("v1", "v2"); empty = single


@dataclass(frozen=True)
class LibraryEntry:
    """One downloaded source, as shown in the Library table."""

    domain: str
    title: str
    url: str
    provider: str
    pages: int
    size_bytes: int
    last_crawled: str                   # ISO-ish date string from metadata
    local_path: Path | None = None      # folder to "open"
    snapshot_count: int = 0


@dataclass(frozen=True)
class SearchHit:
    """One ranked FTS5 result. ``snippet`` may contain ``<b>…</b>`` marks."""

    title: str
    snippet: str
    url: str
    domain: str
    section_heading: str = ""
    rank: float = 0.0


@dataclass(frozen=True)
class SnapshotInfo:
    """One dated snapshot of a domain."""

    version_id: str                     # e.g. "v1.0.1"
    created_at: str
    pages: int
    size_bytes: int


@dataclass(frozen=True)
class PageChange:
    """One changed page between two snapshots."""

    page: str                           # page title or path
    status: str                         # "added" | "removed" | "changed"
    lines_added: int = 0
    lines_removed: int = 0
    old_excerpt: str | None = None      # short before-context, if any
    new_excerpt: str | None = None      # short after-context, if any


@dataclass(frozen=True)
class DiffReport:
    """Result of comparing two snapshots of one domain."""

    domain: str
    old_version: str
    new_version: str
    changes: tuple[PageChange, ...] = ()
    unchanged_pages: int = 0


@dataclass(frozen=True)
class CaptureRun:
    """Everything Diagnostics needs about one finished capture attempt."""

    url: str
    options: CaptureOptions
    detection: Detection | None
    result: CaptureResult | None        # None when the run failed
    error: str | None = None
    duration_s: float = 0.0
    event_counts: dict[str, int] = field(default_factory=dict)


# ── The seam ─────────────────────────────────────────────────────────────


@runtime_checkable
class EngineProtocol(Protocol):
    """The ONLY thing TUI screens know about the outside world.

    Implemented by :class:`tui.real_engine.RealEngine` (production,
    constructed lazily at app launch) and :class:`tui.testing.FakeEngine`
    (pilot tests).
    """

    def capture(
        self,
        url: str,
        options: CaptureOptions,
        *,
        progress: ProgressCallback | None = None,
    ) -> CaptureResult:
        """Crawl one source. Blocking; run it from a worker thread."""
        ...

    def detect(self, url: str) -> Detection:
        """Cheap provider probe for the Wizard's live detect line."""
        ...

    def list_library(self) -> list[LibraryEntry]:
        """All downloaded sources, most recently crawled first."""
        ...

    def delete_domain(self, domain: str) -> bool:
        """Remove a source and its snapshots from the Library."""
        ...

    def search(
        self, query: str, domain: str | None = None, limit: int = 20
    ) -> list[SearchHit]:
        """FTS5-ranked search over indexed pages."""
        ...

    def list_snapshots(self, domain: str) -> list[SnapshotInfo]:
        """Snapshots for a domain, newest first."""
        ...

    def diff_snapshots(self, domain: str, old_version: str, new_version: str) -> DiffReport:
        """Compare two snapshots page-by-page."""
        ...
