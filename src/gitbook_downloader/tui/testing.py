"""FakeEngine — canned engine for Textual pilot tests and offline dev.

Implements :class:`tui.engine_protocol.EngineProtocol` with deterministic
canned data and a scripted progress timeline, so pilot tests never touch
the network or the real facade.
"""

from __future__ import annotations

import time
from pathlib import Path

from .engine_protocol import (
    CaptureOptions,
    CaptureResult,
    Detection,
    DiffReport,
    LibraryEntry,
    PageChange,
    ProgressEvent,
    SearchHit,
    SnapshotInfo,
)

FIXTURE_DIR = Path("~/.gitbook-downloader").expanduser()


def _default_result(url: str, options: CaptureOptions) -> CaptureResult:
    return CaptureResult(
        source_url=url,
        provider="mintlify",
        site_versions_found=("v1", "v2"),
        pages_captured=42,
        skipped=3,
        warnings=(
            "2 pages returned soft-200 HTML instead of markdown; used structural fallback",
            "sitemap.xml listed 1 URL outside the path scope; ignored",
        ),
        library_path=FIXTURE_DIR / "docs" / "docs.example.com",
        local_path=Path("./docs.example.com-docs").resolve(),
        book_file=FIXTURE_DIR / "docs" / "docs.example.com" / "book.md",
        manifest_file=FIXTURE_DIR / "docs" / "docs.example.com" / "llms.txt",
        version_id="v1.0.4" if options.snapshot else None,
    )


def _scripted_events(done_total: int = 6) -> list[ProgressEvent]:
    events = [
        ProgressEvent("discovered", url="https://docs.example.com/", done=0, total=done_total),
    ]
    for i in range(1, done_total + 1):
        kind = "failed" if i == 5 else "downloaded"
        message = "503 after 3 retries; skipped" if kind == "failed" else ""
        events.append(
            ProgressEvent(
                kind,
                url=f"https://docs.example.com/page-{i}",
                message=message,
                done=i,
                total=done_total,
            )
        )
    events.append(ProgressEvent("written", url="docs.example.com", done=done_total, total=done_total))
    return events


class FakeEngine:
    """Deterministic in-memory engine.

    Args mirror the protocol; every call is recorded in ``self.calls`` so
    tests can assert exactly what the UI sent to the seam.
    """

    def __init__(
        self,
        *,
        result: CaptureResult | None = None,
        detection: Detection | None = None,
        library: list[LibraryEntry] | None = None,
        hits: list[SearchHit] | None = None,
        snapshots: list[SnapshotInfo] | None = None,
        diff: DiffReport | None = None,
        capture_error: Exception | None = None,
        detect_error: Exception | None = None,
        event_delay: float = 0.0,
    ) -> None:
        self.result = result
        self.detection = detection or Detection(
            provider="mintlify",
            evidence="generator meta tag",
            site_versions=("v1", "v2"),
        )
        self.library = library if library is not None else _default_library()
        self.hits = hits if hits is not None else _default_hits()
        self.snapshots = snapshots if snapshots is not None else _default_snapshots()
        self.diff = diff if diff is not None else _default_diff()
        self.capture_error = capture_error
        self.detect_error = detect_error
        self.event_delay = event_delay
        self.calls: list[tuple[str, tuple, dict]] = []

    # ── protocol surface ─────────────────────────────────────────────

    def capture(self, url, options, *, progress=None):
        self.calls.append(("capture", (url, options), {}))
        if self.event_delay:
            time.sleep(self.event_delay)
        if progress is not None:
            for event in _scripted_events():
                progress(event)
                if self.event_delay:
                    time.sleep(self.event_delay)
        if self.capture_error is not None:
            raise self.capture_error
        return self.result or _default_result(url, options)

    def detect(self, url):
        self.calls.append(("detect", (url,), {}))
        if self.detect_error is not None:
            raise self.detect_error
        return self.detection

    def list_library(self):
        self.calls.append(("list_library", (), {}))
        return list(self.library)

    def delete_domain(self, domain):
        self.calls.append(("delete_domain", (domain,), {}))
        if not any(e.domain == domain for e in self.library):
            return False
        self.library = [e for e in self.library if e.domain != domain]
        return True

    def search(self, query, domain=None, limit=20):
        self.calls.append(("search", (query, domain, limit), {}))
        hits = [
            h
            for h in self.hits
            if query.lower() in h.title.lower()
            or query.lower() in h.snippet.lower()
            or not query.strip()
        ]
        if domain:
            hits = [h for h in hits if h.domain == domain]
        return hits[:limit]

    def list_snapshots(self, domain):
        self.calls.append(("list_snapshots", (domain,), {}))
        return list(self.snapshots)

    def diff_snapshots(self, domain, old_version, new_version):
        self.calls.append(("diff_snapshots", (domain, old_version, new_version), {}))
        return DiffReport(
            domain=domain,
            old_version=old_version,
            new_version=new_version,
            changes=self.diff.changes,
            unchanged_pages=self.diff.unchanged_pages,
        )


# ── Canned fixtures ──────────────────────────────────────────────────────


def _default_library() -> list[LibraryEntry]:
    return [
        LibraryEntry(
            domain="docs.example.com",
            title="Example Product Docs",
            url="https://docs.example.com/",
            provider="mintlify",
            pages=42,
            size_bytes=1_240_000,
            last_crawled="2026-08-21T14:02:00",
            local_path=FIXTURE_DIR / "docs" / "docs.example.com",
            snapshot_count=4,
        ),
        LibraryEntry(
            domain="api.other.dev",
            title="Other API Reference",
            url="https://api.other.dev/",
            provider="docusaurus",
            pages=118,
            size_bytes=8_920_000,
            last_crawled="2026-08-19T09:41:00",
            local_path=FIXTURE_DIR / "docs" / "api.other.dev",
            snapshot_count=2,
        ),
    ]


def _default_hits() -> list[SearchHit]:
    return [
        SearchHit(
            title="Configuration",
            snippet="Set <b>workers</b> to control parallel fetches during a capture run.",
            url="https://docs.example.com/configuration",
            domain="docs.example.com",
            section_heading="Configuration",
            rank=-3.21,
        ),
        SearchHit(
            title="CLI reference",
            snippet="Pass <b>workers</b> as --workers N to override the preset value.",
            url="https://docs.example.com/cli",
            domain="docs.example.com",
            section_heading="capture",
            rank=-2.87,
        ),
        SearchHit(
            title="Rate limits",
            snippet="Lower <b>workers</b> when a site throttles repeated requests.",
            url="https://api.other.dev/rate-limits",
            domain="api.other.dev",
            section_heading="Limits",
            rank=-1.44,
        ),
    ]


def _default_snapshots() -> list[SnapshotInfo]:
    return [
        SnapshotInfo("v1.1.0", "2026-08-21", 42, 1_240_000),
        SnapshotInfo("v1.0.1", "2026-07-30", 39, 1_102_000),
        SnapshotInfo("v1.0.0", "2026-07-12", 37, 986_000),
    ]


def _default_diff() -> DiffReport:
    return DiffReport(
        domain="docs.example.com",
        old_version="v1.0.1",
        new_version="v1.1.0",
        changes=(
            PageChange(
                page="Getting started",
                status="changed",
                lines_added=12,
                lines_removed=4,
                old_excerpt="Install the CLI with npm install -g gitbook-downloader.",
                new_excerpt="Install the CLI with uv tool install gitbook-downloader.",
            ),
            PageChange(page="Webhooks", status="added", lines_added=48),
            PageChange(page="Legacy OAuth flow", status="removed", lines_removed=96),
            PageChange(
                page="Rate limits",
                status="changed",
                lines_added=2,
                lines_removed=2,
                old_excerpt="Default limit: 60 requests/min.",
                new_excerpt="Default limit: 120 requests/min.",
            ),
        ),
        unchanged_pages=35,
    )
