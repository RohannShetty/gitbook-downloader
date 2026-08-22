"""Capture facade — the ONLY entry point for CLI, TUI, and MCP (plan §2).

``capture(url, options) -> CaptureResult`` orchestrates the whole capture
lifecycle around the engine:

1. Validate options.
2. Take the per-domain lockfile.
3. **Snapshot BEFORE download starts** (single snapshot point).
4. Call ``engine.stream_download`` with the v7 signature
   ``(url, path_scope=…, exclude_paths=…, timeout=…, max_pages=…)``.
5. Normalise whatever the engine returns into :class:`CapturedPage` records.
6. Filter by detected site versions when requested.
7. Write the output contract (page tree + book + ``llms.txt``) to the
   project-local folder and/or the Library.
8. Refresh library metadata and the search index.

Detection happens ONCE inside this call tree and is reported in the result —
the facade never runs a second detection pass.

Progress is reported as :class:`ProgressEvent` dataclasses with kinds
``discovered | downloaded | failed | written``.

For testing, the engine and storage seams are module-level loaders that can
be monkeypatched:

- ``gitbook_downloader.api._load_stream_download``
- ``gitbook_downloader.api._default_storage``
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal
from urllib.parse import urlparse

from .output_contract import CapturedPage, PublishOutcome, utc_now_iso, publish
from .storage.manager import LockHeldError, StorageManager, parse_semver
from .storage.versioning import VersionManager

__all__ = [
    "CaptureError",
    "CaptureOptions",
    "CaptureResult",
    "ProgressEvent",
    "LATEST_ONLY",
    "capture",
]


class CaptureError(RuntimeError):
    """Raised when a capture cannot start (bad options, lock held, …)."""


#: Sentinel for ``site_versions`` meaning "only the newest detected version".
LATEST_ONLY = "@latest"


# ── Contract types ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class CaptureOptions:
    """Everything a capture needs besides the URL."""

    workers: int = 8                      # parallel fetches
    max_pages: int | None = None          # None = unlimited (0 is INVALID)
    path_scope: tuple[str, ...] = ()      # URL path prefixes to include
    exclude_paths: tuple[str, ...] = ()   # path patterns to skip inside scope
    site_versions: tuple[str, ...] | None = None  # None=all; subset filters
    output_mode: Literal["both", "library", "local"] = "both"
    local_dir: Path | None = None         # default ./<domain>-docs/
    snapshot: bool = True                 # snapshot previous before overwrite
    timeout: float = 20.0


@dataclass(frozen=True)
class ProgressEvent:
    """One progress update from inside a running capture."""

    kind: str                       # discovered | downloaded | failed | written
    url: str | None = None
    title: str | None = None
    count: int | None = None
    size_kb: float | None = None
    message: str | None = None


@dataclass(frozen=True)
class CaptureResult:
    """Outcome of one capture run."""

    source_url: str
    provider: str                  # gitbook|mintlify|docusaurus|readthedocs|mkdocs|generic
    site_versions_found: tuple[str, ...]
    pages_captured: int
    skipped: int                   # filtered/excluded/duplicate count
    warnings: tuple[str, ...]      # non-fatal issues surfaced to user/diagnostics
    library_path: Path | None
    local_path: Path | None
    book_file: Path | None
    manifest_file: Path | None     # llms.txt
    version_id: str | None         # snapshot id created, if snapshotting


# ── Seams (monkeypatch targets for tests) ───────────────────────────────


def _load_stream_download():
    """Resolve the engine entry point lazily so tests can inject a fake."""
    from .engine import stream_download

    return stream_download


def _default_storage() -> StorageManager:
    """Resolve the library storage manager (monkeypatch target)."""
    return StorageManager()


# ── Validation ──────────────────────────────────────────────────────────


def _validate_url(url: str) -> str:
    if not isinstance(url, str) or not url.strip():
        raise CaptureError("A source URL is required.")
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise CaptureError(
            f"Not a documentation URL: {url!r}. Expected http(s)://…"
        )
    return url.strip()


def _validate_options(options: CaptureOptions) -> None:
    if options.max_pages is not None:
        if not isinstance(options.max_pages, int) or options.max_pages <= 0:
            raise CaptureError(
                "max_pages must be a positive integer or None "
                f"(got {options.max_pages!r}; 0 is invalid — use None for unlimited)."
            )
    if not isinstance(options.workers, int) or options.workers < 1:
        raise CaptureError(f"workers must be >= 1 (got {options.workers!r}).")
    if options.timeout <= 0:
        raise CaptureError(f"timeout must be > 0 (got {options.timeout!r}).")
    if options.output_mode not in ("both", "library", "local"):
        raise CaptureError(
            f"output_mode must be 'both', 'library' or 'local' "
            f"(got {options.output_mode!r})."
        )


# ── Site-version helpers ────────────────────────────────────────────────

_VERSION_SEG_RE = re.compile(r"^v\d+(?:\.\d+)*$", re.IGNORECASE)
_LOCALE_SEG_RE = re.compile(r"^[a-z]{2}(?:-[a-z]{2})?$", re.IGNORECASE)


def _version_prefix_of(url: str) -> str:
    """Return the site-version prefix a URL belongs to ('' when none).

    Recognised shapes: ``/v1/``, ``/v2.3/`` and two-segment locale releases
    like ``/en/latest/`` or ``/de/stable/``.
    """
    segments = [s for s in urlparse(url).path.split("/") if s]
    for i, seg in enumerate(segments[:4]):
        if _VERSION_SEG_RE.match(seg):
            return seg.lower()
        if (
            _LOCALE_SEG_RE.match(seg)
            and i + 1 < len(segments)
            and segments[i + 1].lower() in ("latest", "stable")
        ):
            return f"{seg.lower()}/{segments[i + 1].lower()}"
    return ""


def detect_site_versions(urls) -> tuple[str, ...]:
    """Detect which site versions exist across *urls* (sorted)."""
    found = {_version_prefix_of(u) for u in urls}
    found.discard("")
    return tuple(sorted(found))


def _natural_version_key(version: str):
    nums = re.findall(r"\d+", version)
    return tuple(int(n) for n in nums) or (0,)


def _apply_site_version_filter(
    pages: list[CapturedPage],
    selected: tuple[str, ...] | None,
    warnings: list[str],
) -> list[CapturedPage]:
    """Filter pages down to the selected site versions.

    An empty result after filtering stays empty — never an unfiltered
    fallback (a warning explains why instead).
    """
    if selected is None:
        return pages

    wanted = {v.lower().strip("/") for v in selected}
    if LATEST_ONLY in wanted:
        found = sorted(
            {p.site_version for p in pages if p.site_version},
            key=_natural_version_key,
        )
        if not found:
            warnings.append(
                "--latest-only was set but no site versions were detected; "
                "nothing matches."
            )
            return []
        wanted = {found[-1]}

    tagged_any = any(p.site_version for p in pages)
    if not tagged_any:
        warnings.append(
            "Site versions were requested but the site exposes none; "
            "treating the whole capture as unversioned."
        )
        return []

    kept = [p for p in pages if p.site_version.lower() in wanted]
    if not kept:
        warnings.append(
            f"None of the requested site versions ({', '.join(sorted(wanted))}) "
            f"matched what was captured "
            f"(found: {', '.join(sorted({p.site_version for p in pages if p.site_version})) or 'none'})."
        )
    return kept


# ── Engine-result normalisation ─────────────────────────────────────────


def _coerce_page(item, fallback_url: str) -> CapturedPage | None:
    """Coerce one engine page record (dict or object) into a CapturedPage."""
    if isinstance(item, CapturedPage):
        return item
    if isinstance(item, dict):
        content = item.get("content") or ""
        url = item.get("url") or fallback_url
        title = item.get("title") or ""
        version = item.get("site_version") or ""
    else:
        content = getattr(item, "content", "") or ""
        url = getattr(item, "url", None) or fallback_url
        title = getattr(item, "title", "") or ""
        version = getattr(item, "site_version", "") or ""
    if not content.strip():
        return None
    if not title:
        m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = m.group(1).strip() if m else url.rstrip("/").split("/")[-1] or "Home"
    return CapturedPage(url=url, title=title, content=content,
                        site_version=str(version))


def normalize_engine_result(raw, source_url: str):
    """Normalise the engine's return value into ``(pages, provider, discovered, failed)``.

    Accepted shapes (Lane A's final return type may be any of these):

    - ``str`` — legacy combined markdown blob → single pseudo-page.
    - ``list`` of dicts/objects with ``url``/``content`` keys.
    - ``dict`` mapping ``url → markdown``.
    - ``dict`` with a ``"pages"`` key plus optional ``provider`` /
      ``discovered`` / ``failed`` metadata.
    """
    provider = None
    discovered = None
    failed = None
    items = raw

    if isinstance(raw, str):
        items = [{"url": source_url, "title": "", "content": raw}]
    elif isinstance(raw, dict):
        if "pages" in raw:
            items = raw.get("pages") or []
            provider = raw.get("provider")
            discovered = raw.get("discovered")
            failed = raw.get("failed")
        else:
            items = [
                {"url": u, "title": "", "content": c} for u, c in raw.items()
            ]

    pages: list[CapturedPage] = []
    seen_urls: set[str] = set()
    for item in items or []:
        page = _coerce_page(item, source_url)
        if page is None:
            continue
        if page.url in seen_urls:
            continue
        seen_urls.add(page.url)
        pages.append(page)

    # Tag each page with its site-version prefix when the engine didn't.
    # CapturedPage is frozen, so rebuild the ones that need a tag.
    pages = [
        p if p.site_version else
        CapturedPage(p.url, p.title, p.content, _version_prefix_of(p.url))
        for p in pages
    ]

    return pages, provider, discovered, failed


# ── The facade ──────────────────────────────────────────────────────────


def capture(
    url: str,
    options: CaptureOptions,
    *,
    progress: Callable[[ProgressEvent], None] | None = None,
) -> CaptureResult:
    """Capture a documentation site and write the full output contract."""
    url = _validate_url(url)
    _validate_options(options)
    emit = progress or (lambda event: None)

    parsed = urlparse(url)
    domain = parsed.netloc.removeprefix("www.") or "unknown"

    warnings: list[str] = []
    storage = _default_storage()
    versioning = VersionManager(storage)

    # ── Per-domain lockfile ─────────────────────────────────────────
    lock = storage.domain_lock(domain)
    try:
        lock.acquire()
    except LockHeldError as exc:
        raise CaptureError(str(exc)) from exc

    try:
        # ── Single snapshot point BEFORE download starts ────────────
        version_id: str | None = None
        if options.snapshot and storage.domain_exists(domain):
            try:
                version_id = versioning.snapshot(domain)
            except Exception as exc:  # noqa: BLE001 — snapshot is best-effort
                warnings.append(f"Snapshot of previous capture failed: {exc}")

        # ── Download via the engine ─────────────────────────────────
        engine_counts = {"discovered": None, "failed": 0}

        def on_engine_event(data: dict) -> None:
            phase = data.get("phase")
            if phase == "discovery" and data.get("status") == "done":
                engine_counts["discovered"] = data.get("discovered", 0)
                emit(ProgressEvent(kind="discovered",
                                   count=data.get("discovered", 0)))
            elif phase == "downloaded":
                emit(ProgressEvent(kind="downloaded",
                                   url=data.get("url"),
                                   title=data.get("title"),
                                   size_kb=data.get("size_kb")))
            elif phase == "error":
                engine_counts["failed"] += 1
                emit(ProgressEvent(kind="failed",
                                   url=data.get("url"),
                                   message=data.get("error")))

        stream_download = _load_stream_download()
        try:
            raw = stream_download(
                url,
                path_scope=list(options.path_scope),
                exclude_paths=list(options.exclude_paths),
                timeout=options.timeout,
                max_pages=options.max_pages,
                workers=options.workers,
                progress_callback=on_engine_event,
            )
        except TypeError as exc:
            raise CaptureError(
                f"Engine rejected the v7 stream_download signature: {exc}. "
                f"Update gitbook_downloader.engine.stream_download to accept "
                f"(url, *, path_scope, exclude_paths, timeout, max_pages, "
                f"workers, progress_callback)."
            ) from exc

        pages, provider_name, discovered_hint, failed_hint = \
            normalize_engine_result(raw, url)

        provider = (provider_name or "generic").lower()
        site_versions_found = detect_site_versions([p.url for p in pages])
        before_filter = len(pages)
        pages = _apply_site_version_filter(pages, options.site_versions, warnings)
        skipped = max(0, before_filter - len(pages))

        if not pages:
            warnings.append("No content was captured for this source.")
            emit(ProgressEvent(kind="written", count=0,
                               message="nothing written"))
            return CaptureResult(
                source_url=url,
                provider=provider,
                site_versions_found=site_versions_found,
                pages_captured=0,
                skipped=skipped,
                warnings=tuple(warnings),
                library_path=None,
                local_path=None,
                book_file=None,
                manifest_file=None,
                version_id=version_id,
            )

        # ── Output routing ──────────────────────────────────────────
        local_dir = options.local_dir or (Path.cwd() / f"{domain}-docs")
        library_dir = storage._domain_dir(domain)

        outcome: PublishOutcome = publish(
            pages,
            domain=domain,
            source_url=url,
            provider=provider,
            output_mode=options.output_mode,
            local_dir=local_dir,
            library_dir=library_dir,
        )

        # ── Library metadata + search index (library mode only) ────
        book_text = outcome.book_file.read_text(encoding="utf-8") \
            if outcome.book_file else ""
        total_kb = round(outcome.bytes_written / 1024, 1)
        if outcome.library_path is not None:
            try:
                storage.save_doc(
                    domain=domain,
                    content=book_text,
                    url=url,
                    title=(pages[0].title if pages else domain),
                    pages=len(pages),
                    provider=provider,
                    new_pages=len(pages),
                    size_kb=total_kb,
                )
            except Exception as exc:  # noqa: BLE001 — metadata is best-effort
                warnings.append(f"Library metadata update failed: {exc}")

            try:
                from .search import SearchIndex

                SearchIndex(base_dir=storage.base).index_domain(
                    domain, book_text, url
                )
            except Exception as exc:  # noqa: BLE001 — indexing is best-effort
                warnings.append(f"Search indexing failed: {exc}")

        emit(ProgressEvent(kind="written", count=len(pages),
                           message=str(outcome.local_path or outcome.library_path)))

        discovered = discovered_hint if discovered_hint is not None \
            else engine_counts["discovered"]
        if discovered is not None:
            unaccounted = max(0, int(discovered) - len(pages)
                              - (failed_hint or engine_counts["failed"]))
            skipped += unaccounted

        return CaptureResult(
            source_url=url,
            provider=provider,
            site_versions_found=site_versions_found,
            pages_captured=len(pages),
            skipped=skipped,
            warnings=tuple(warnings),
            library_path=outcome.library_path,
            local_path=outcome.local_path,
            book_file=outcome.book_file,
            manifest_file=outcome.manifest_file,
            version_id=version_id,
        )
    finally:
        lock.release()
