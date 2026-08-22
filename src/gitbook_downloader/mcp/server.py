"""MCP server for gitbook-downloader — exposes tools for LLMs to download, search, and manage documentation.

Transport: stdio (for Claude Desktop, Cursor, Windsurf, etc.)

Tools:
    download_docs   – Download a documentation site (via the capture facade)
    search_docs     – Full-text search across downloaded docs
    list_domains    – List all downloaded documentation domains
    get_doc         – Get full doc content for a domain
    diff_versions   – Diff two versions of a domain
    list_versions   – List all available versions
    export_docs     – Export in markdown / JSONL / RAG format
    get_changelog   – Auto-generate changelog from version diffs

``download_docs`` delegates the entire capture lifecycle (provider detection,
snapshotting, page-tree + book + manifest writing, library storage) to
``gitbook_downloader.api.capture``. This module owns no download logic: it maps
tool parameters onto ``CaptureOptions`` and reports ``CaptureResult`` fields.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import urlparse

from mcp.server.fastmcp import FastMCP

# ── Capture facade (the ONLY entry into the engine) ──────────────────
#
# Imported lazily-tolerantly so this module stays importable if the facade
# is missing (broken install); download_docs then reports the problem
# instead of crashing the whole server at import time.

try:
    from gitbook_downloader.api import CaptureOptions, capture as _default_capture
except ImportError:  # pragma: no cover - api.py ships with the v7 shell
    CaptureOptions = None  # type: ignore[assignment,misc]
    _default_capture = None  # type: ignore[assignment]

# ── Search import (graceful fallback if module not yet built) ────────

try:
    from gitbook_downloader.search import SearchIndex

    _search = SearchIndex()
except Exception:
    _search = None  # type: ignore[assignment]

# ── Logger ───────────────────────────────────────────────────────────

logger = logging.getLogger("gitbook_downloader.mcp")

# ── MCP server instance ─────────────────────────────────────────────

mcp = FastMCP(
    "gitbook-downloader",
    instructions=(
        "Download documentation sites (GitBook, Docusaurus, ReadTheDocs, "
        "Mintlify, or generic), search across downloaded docs, manage "
        "versions, and export in multiple formats."
    ),
)

# ── Shared singletons ───────────────────────────────────────────────

from gitbook_downloader.storage import StorageManager, VersionManager  # noqa: E402

_storage = StorageManager()
_versioning = VersionManager(_storage)


# ── Helpers ──────────────────────────────────────────────────────────


def _domain_from_url(url: str) -> str:
    """Extract the domain from *url*, stripping ``www.``."""
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "")


def _run_capture(url: str, options_kwargs: dict) -> Any:
    """Single seam between MCP tools and the capture facade.

    Builds ``CaptureOptions`` from already-validated keyword arguments and
    invokes ``capture`` with a logging progress callback. Returns a
    ``CaptureResult`` (contract in docs/superpowers/plans/ §2). Tests replace
    this function (monkeypatch ``gitbook_downloader.mcp.server._run_capture``)
    to inject a fake facade; nothing else in this module talks to the engine.
    """
    if _default_capture is None or CaptureOptions is None:
        raise RuntimeError(
            "Capture facade not available: gitbook_downloader.api could not be "
            "imported. Reinstall the package: pip install --force-reinstall gitbook-downloader"
        )

    options = CaptureOptions(**options_kwargs)

    def _log_progress(event: object) -> None:
        logger.debug("capture %s: %s", url, event)

    return _default_capture(url, options, progress=_log_progress)


def _path_or_none(p: Optional[Path]) -> Optional[str]:
    return str(p) if p is not None else None


# ── Tools ────────────────────────────────────────────────────────────


@mcp.tool()
async def download_docs(
    url: str,
    max_pages: Optional[int] = None,
    workers: int = 8,
    path_scope: Optional[list[str]] = None,
    exclude_paths: Optional[list[str]] = None,
    site_versions: Optional[list[str]] = None,
    output_mode: str = "both",
) -> dict:
    """Download documentation from a URL.

    Auto-detects the platform (GitBook, Docusaurus, ReadTheDocs, Mintlify,
    or generic), crawls the pages, writes the output contract (page tree +
    book file + llms.txt manifest, with YAML frontmatter), stores it in the
    Library, and indexes it for search.

    Args:
        url: Documentation site root URL (e.g. https://docs.example.com).
        max_pages: Maximum pages to crawl. Omit for unlimited (0 is invalid).
        workers: Parallel fetch workers (default 8).
        path_scope: URL path prefixes to include (e.g. ["/api/"]). Empty = whole site.
        exclude_paths: Path patterns to skip even inside the path scope.
        site_versions: Site versions to capture (e.g. ["v1", "v2"]).
                       Omit to capture all detected versions.
        output_mode: Where output goes — "both" (Library + project-local),
                     "library", or "local".

    Returns:
        Summary dict with provider, pages captured, skipped count, warnings,
        site versions found, and the paths written (library/local/book/manifest).
    """
    try:
        options_kwargs: dict = {
            "workers": workers,
            "max_pages": max_pages,
            "path_scope": tuple(path_scope or ()),
            "exclude_paths": tuple(exclude_paths or ()),
            "site_versions": tuple(site_versions) if site_versions is not None else None,
            "output_mode": output_mode,
        }

        result = _run_capture(url, options_kwargs)

        domain = _domain_from_url(url)

        # Best-effort re-index from storage for full-text search.
        if _search is not None:
            try:
                _search.index_domain_from_storage(domain, _storage, domain_url=url)
            except Exception as exc:
                logger.warning("Search indexing failed for %s: %s", domain, exc)

        return {
            "url": result.source_url,
            "domain": domain,
            "provider": result.provider,
            "site_versions_found": list(result.site_versions_found),
            "pages_captured": result.pages_captured,
            "skipped": result.skipped,
            "warnings": list(result.warnings),
            "output_mode": output_mode,
            "library_path": _path_or_none(result.library_path),
            "local_path": _path_or_none(result.local_path),
            "book_file": _path_or_none(result.book_file),
            "manifest_file": _path_or_none(result.manifest_file),
            "version_id": result.version_id,
        }
    except Exception as exc:
        logger.exception("download_docs failed")
        return {"error": str(exc)}


@mcp.tool()
async def search_docs(
    query: str,
    domain: Optional[str] = None,
    limit: int = 10,
) -> list[dict]:
    """Full-text search across downloaded documentation.

    Uses SQLite FTS5 with BM25 ranking when the search index is available.
    Supports AND, OR, NOT, quoted phrases, and prefix* syntax.

    Args:
        query: Search query (e.g. "authentication" or "api rate limit").
        domain: Optional domain to restrict search (e.g. "docs.example.com").
        limit: Maximum results to return (default 10, max 50).

    Returns:
        List of matching sections with title, url, snippet, domain, and rank.
    """
    if _search is None:
        # FTS5 ships in Python's stdlib sqlite3 on all supported platforms;
        # reaching this means the installed package itself is broken/incomplete.
        return [
            {
                "error": (
                    "Search index not available. The search module failed to "
                    "import — reinstall the package: "
                    "pip install --force-reinstall gitbook-downloader "
                    "(no extra needed; FTS5 is stdlib SQLite)"
                )
            }
        ]
    try:
        results = _search.search(query, domain=domain, limit=min(limit, 50))
        return results
    except Exception as exc:
        return [{"error": str(exc)}]


@mcp.tool()
async def list_domains() -> list[dict]:
    """List all downloaded documentation domains.

    Returns metadata for each domain including name, url, pages, size,
    provider, last scraped timestamp, and available versions.
    """
    try:
        return _storage.list_domains()
    except Exception as exc:
        return [{"error": str(exc)}]


@mcp.tool()
async def get_doc(
    domain: str,
    version: Optional[str] = None,
) -> dict:
    """Get documentation content for a domain.

    Args:
        domain: Domain name (e.g. "docs.example.com").
        version: Optional version string (e.g. "1.0.0" or "v1.0.1").
                 If omitted, returns the latest version.

    Returns:
        Dict with domain, version, content length, and a 2 000-char preview.
    """
    try:
        if version:
            content = _versioning.get_version_content(domain, version)
            v = version
        else:
            content = _storage.load_doc(domain)
            meta = _storage.get_metadata(domain)
            v = meta.get("latest_version", "latest") if meta else "latest"

        if content is None:
            msg = f"No content found for {domain}"
            if version:
                msg += f" version {version}"
            return {"error": msg}

        return {
            "domain": domain,
            "version": v,
            "length": len(content),
            "preview": content[:2000],
        }
    except Exception as exc:
        return {"error": str(exc)}


@mcp.tool()
async def diff_versions(
    domain: str,
    v1: str,
    v2: str,
) -> dict:
    """Show the unified diff between two versions of downloaded documentation.

    Args:
        domain: Domain name.
        v1: First (older) version (e.g. "1.0.0").
        v2: Second (newer) version (e.g. "1.0.1").

    Returns:
        Dict with diff text, added lines count, and removed lines count.
    """
    try:
        diff_text = _versioning.diff(domain, v1, v2)
        added = sum(
            1 for l in diff_text.split("\n") if l.startswith("+") and not l.startswith("+++")
        )
        removed = sum(
            1 for l in diff_text.split("\n") if l.startswith("-") and not l.startswith("---")
        )
        return {
            "domain": domain,
            "v1": v1,
            "v2": v2,
            "diff": diff_text,
            "added_lines": added,
            "removed_lines": removed,
        }
    except Exception as exc:
        return {"error": str(exc)}


@mcp.tool()
async def list_versions(domain: str) -> list[dict]:
    """List all available versions for a domain.

    Args:
        domain: Domain name.

    Returns:
        List of version dicts with version, timestamp, pages, size, and is_latest.
    """
    try:
        versions = _versioning.get_versions(domain)
        if not versions:
            meta = _storage.get_metadata(domain)
            if meta:
                versions = meta.get("versions", [])
        return versions
    except Exception as exc:
        return [{"error": str(exc)}]


@mcp.tool()
async def export_docs(
    domain: str,
    format: str = "markdown",
) -> dict:
    """Export downloaded documentation in different formats.

    Args:
        domain: Domain name.
        format: Export format — "markdown", "jsonl", or "rag".

    Returns:
        Dict with export path (if applicable), format, and content preview.
    """
    try:
        content = _storage.load_doc(domain)
        if content is None:
            return {"error": f"No content found for {domain}"}

        if format == "jsonl":
            export_path = _storage._domain_dir(domain) / f"{domain}_export.jsonl"
            from gitbook_downloader.utils.export import export_to_jsonl

            export_to_jsonl(domain, _storage, str(export_path))
            preview = ""
            try:
                with open(export_path, encoding="utf-8") as fh:
                    preview = fh.read()[:1000]
            except OSError:
                pass
            return {
                "path": str(export_path),
                "format": "jsonl",
                "preview": preview,
            }

        if format == "rag":
            from gitbook_downloader.utils.export import wrap_with_rag_metadata

            rag_content = wrap_with_rag_metadata(
                content,
                domain,
                url=domain,
                headings=[],
                chunk_num=1,
                total_chunks=1,
            )
            return {
                "format": "rag",
                "content": rag_content[:2000],
                "length": len(rag_content),
            }

        # Default: markdown
        return {
            "path": str(_storage.latest_path(domain)),
            "format": "markdown",
            "length": len(content),
            "preview": content[:2000],
        }
    except Exception as exc:
        return {"error": str(exc)}


@mcp.tool()
async def get_changelog(domain: str) -> dict:
    """Auto-generate a changelog from all version diffs of a domain.

    Iterates over consecutive version pairs (newest first) and counts
    added / removed lines to produce a concise change summary.

    Args:
        domain: Domain name.

    Returns:
        Dict with domain and a list of changelog entries, each containing
        version, timestamp, added_lines, removed_lines, and diff text.
    """
    try:
        entries = _versioning.changelog(domain)
        return {
            "domain": domain,
            "entries": entries,
            "total_versions": len(entries) + 1,
        }
    except Exception as exc:
        return {"error": str(exc)}


# ── Entry point ──────────────────────────────────────────────────────


def main() -> None:
    """Run the MCP server over stdio (for Claude Desktop, Cursor, etc.)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
