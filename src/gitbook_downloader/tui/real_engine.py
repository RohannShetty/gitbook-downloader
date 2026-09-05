"""Real engine adapter — the ONLY place the TUI touches backend modules.

Every backend import happens lazily inside a method body, so importing
this module (or constructing the app) never pulls requests/bs4/api until
the TUI actually launches with no injected engine.
"""

from __future__ import annotations

import difflib
import re
from pathlib import Path

from .engine_protocol import (
    CaptureOptions,
    CaptureResult,
    Detection,
    DiffReport,
    LibraryEntry,
    PageChange,
    ProgressCallback,
    ProgressEvent,
    SearchHit,
    SnapshotInfo,
)


def create_real_engine():
    """Build the production engine (called once, at app launch)."""
    return RealEngine()


def _api():
    """Import the pinned facade; raise a clear error if Lane B hasn't landed."""
    try:
        from gitbook_downloader import api  # noqa: PLC0415 — lazy by design
    except ImportError as exc:  # pragma: no cover - depends on Lane B landing
        raise RuntimeError(
            "The capture facade (gitbook_downloader.api) is not available yet. "
            "This package ships api.capture as the single entry point; update "
            "the package or run the TUI through an injected engine."
        ) from exc
    return api


def _storage_manager():
    from gitbook_downloader.storage.manager import StorageManager

    return StorageManager()


def _search_index():
    from gitbook_downloader.search.index import SearchIndex

    return SearchIndex()


_HEADING_SPLIT = re.compile(r"^(#{1,2})\s+(.+?)$", re.MULTILINE)


def _split_pages(markdown: str) -> list[tuple[str, str]]:
    """Split a book file into (title, body) chunks at #/## headings."""
    if not markdown:
        return []
    matches = list(_HEADING_SPLIT.finditer(markdown))
    if not matches:
        return [("(untitled)", markdown)]
    pages: list[tuple[str, str]] = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        title = match.group(2).strip()
        pages.append((title, markdown[match.end():end].strip()))
    preamble = markdown[: matches[0].start()].strip()
    if preamble:
        pages.insert(0, ("(front matter)", preamble))
    return pages


def _excerpt(text: str, limit: int = 240) -> str:
    text = text.strip().replace("\n", " ")
    return text[:limit] + "…" if len(text) > limit else text


class RealEngine:
    """Production EngineProtocol over api.capture + storage + search."""

    def capture(
        self,
        url: str,
        options: CaptureOptions,
        *,
        progress: ProgressCallback | None = None,
    ) -> CaptureResult:
        api = _api()
        real_options = api.CaptureOptions(
            workers=options.workers,
            max_pages=options.max_pages,
            path_scope=tuple(options.path_scope),
            exclude_paths=tuple(options.exclude_paths),
            site_versions=options.site_versions,
            output_mode=options.output_mode,
            local_dir=options.local_dir,
            snapshot=options.snapshot,
            timeout=options.timeout,
        )
        state = {"done": 0, "total": 0}

        def emit(event) -> None:
            if progress is None:
                return
            kind = str(getattr(event, "kind", ""))
            # The real facade's ProgressEvent carries count/size_kb/title but
            # no running totals; synthesize done/total for the progress bar.
            if kind == "discovered":
                state["total"] = int(getattr(event, "count", 0) or 0)
            elif kind in ("downloaded", "failed"):
                state["done"] += 1
            progress(
                ProgressEvent(
                    kind=kind,
                    url=str(getattr(event, "url", "") or ""),
                    message=str(getattr(event, "message", "") or ""),
                    done=state["done"],
                    total=state["total"],
                )
            )

        result = api.capture(url, real_options, progress=emit)
        return CaptureResult(
            source_url=result.source_url,
            provider=result.provider,
            site_versions_found=tuple(result.site_versions_found),
            pages_captured=result.pages_captured,
            skipped=result.skipped,
            warnings=tuple(result.warnings),
            library_path=result.library_path,
            local_path=result.local_path,
            book_file=result.book_file,
            manifest_file=result.manifest_file,
            version_id=result.version_id,
        )

    def detect(self, url: str) -> Detection:
        """Pre-flight probe. Reuses the provider registry's detector so the
        Wizard can show a live hint; capture() remains the authority."""
        try:
            import requests  # noqa: PLC0415

            from gitbook_downloader.providers import detect_provider
        except Exception:  # noqa: BLE001 — detection is best-effort UI sugar
            return Detection(provider="generic")
        try:
            session = requests.Session()
            provider = detect_provider(url, session)
            return Detection(provider=getattr(provider, "name", "") or "generic")
        except Exception:  # noqa: BLE001 — network hiccups must not crash the TUI
            return Detection(provider="generic")

    def list_library(self) -> list[LibraryEntry]:
        storage = _storage_manager()
        entries: list[LibraryEntry] = []
        for meta in storage.list_domains():
            versions = meta.get("versions") or []
            entries.append(
                LibraryEntry(
                    domain=meta.get("domain", ""),
                    title=meta.get("title") or meta.get("domain", ""),
                    url=meta.get("url", ""),
                    provider=meta.get("provider", ""),
                    pages=int(meta.get("total_pages", 0) or 0),
                    size_bytes=int(meta.get("total_size_kb", 0) or 0) * 1024,
                    last_crawled=meta.get("last_scraped", ""),
                    local_path=storage._domain_dir(meta.get("domain", "")),
                    snapshot_count=len(versions),
                )
            )
        entries.sort(key=lambda e: e.last_crawled, reverse=True)
        return entries

    def delete_domain(self, domain: str) -> bool:
        removed = _storage_manager().delete_domain(domain)
        try:
            _search_index().delete_domain(domain)
        except Exception:  # noqa: BLE001 — index cleanup is best-effort
            pass
        return removed

    def search(
        self, query: str, domain: str | None = None, limit: int = 20
    ) -> list[SearchHit]:
        rows = _search_index().search(query, domain=domain, limit=limit)
        return [
            SearchHit(
                title=row["title"],
                snippet=row["snippet"],
                url=row["url"],
                domain=row["domain"],
                section_heading=row.get("section_heading", ""),
                rank=float(row.get("rank", 0.0)),
            )
            for row in rows
        ]

    def list_snapshots(self, domain: str) -> list[SnapshotInfo]:
        meta = _storage_manager().get_metadata(domain)
        if not meta:
            return []
        snapshots = [
            SnapshotInfo(
                version_id=v.get("version", "?"),
                created_at=v.get("timestamp", ""),
                pages=int(v.get("pages", 0) or 0),
                size_bytes=int(v.get("size_kb", 0) or 0) * 1024,
            )
            for v in reversed(meta.get("versions") or [])
        ]
        return snapshots

    def diff_snapshots(self, domain: str, old_version: str, new_version: str) -> DiffReport:
        storage = _storage_manager()
        old_text = storage.load_doc_version(domain, old_version) or ""
        new_text = storage.load_doc_version(domain, new_version) or ""
        old_pages = dict(_split_pages(old_text))
        new_pages = dict(_split_pages(new_text))

        changes: list[PageChange] = []
        unchanged = 0
        for title, old_body in old_pages.items():
            if title not in new_pages:
                changes.append(
                    PageChange(page=title, status="removed", lines_removed=len(old_body.splitlines()))
                )
                continue
            new_body = new_pages[title]
            if old_body == new_body:
                unchanged += 1
                continue
            diff = list(
                difflib.unified_diff(
                    old_body.splitlines(), new_body.splitlines(), lineterm="", n=1
                )
            )
            added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
            removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))
            changes.append(
                PageChange(
                    page=title,
                    status="changed",
                    lines_added=added,
                    lines_removed=removed,
                    old_excerpt=_excerpt(old_body),
                    new_excerpt=_excerpt(new_body),
                )
            )
        for title, new_body in new_pages.items():
            if title not in old_pages:
                changes.append(
                    PageChange(
                        page=title,
                        status="added",
                        lines_added=len(new_body.splitlines()),
                        new_excerpt=_excerpt(new_body),
                    )
                )

        order = {"changed": 0, "added": 1, "removed": 2}
        changes.sort(key=lambda c: (order.get(c.status, 3), c.page))
        return DiffReport(
            domain=domain,
            old_version=old_version,
            new_version=new_version,
            changes=tuple(changes),
            unchanged_pages=unchanged,
        )
