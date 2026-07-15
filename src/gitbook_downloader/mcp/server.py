"""MCP server for gitbook-downloader — exposes tools for LLMs to download, search, and manage documentation.

Transport: stdio (for Claude Desktop, Cursor, Windsurf, etc.)

Tools:
    download_docs   – Download a documentation site
    search_docs     – Full-text search across downloaded docs
    list_domains    – List all downloaded documentation domains
    get_doc         – Get full doc content for a domain
    diff_versions   – Diff two versions of a domain
    list_versions   – List all available versions
    export_docs     – Export in markdown / JSONL / RAG format
    get_changelog   – Auto-generate changelog from version diffs
"""

from __future__ import annotations

import logging
import tempfile
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from mcp.server.fastmcp import FastMCP

from gitbook_downloader.providers import detect_provider
from gitbook_downloader.storage import StorageManager, VersionManager
from gitbook_downloader.utils import create_session, normalize_url

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

_session = create_session()
_storage = StorageManager()
_versioning = VersionManager(_storage)


# ── Helpers ──────────────────────────────────────────────────────────


def _domain_from_url(url: str) -> str:
    """Extract the domain from *url*, stripping ``www.``."""
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "")


def _emit_progress(data: dict, state: dict) -> None:
    """Accumulate progress events from the engine's callback."""
    phase = data.get("phase", "")
    if phase == "downloaded":
        state["pages"] += 1
        state["size_kb"] += data.get("size_kb", 0)
    elif phase == "error":
        state["errors"] += 1
    elif phase in ("discovered", "discovery"):
        state["discovered"] = data.get("discovered", 0) or data.get("count", 0)


# ── Tools ────────────────────────────────────────────────────────────


@mcp.tool()
async def download_docs(
    url: str,
    max_pages: int = 0,
    workers: int = 5,
) -> dict:
    """Download documentation from a URL.

    Auto-detects the platform (GitBook, Docusaurus, ReadTheDocs, Mintlify,
    or generic), crawls all pages, stores them, and indexes for search.

    Args:
        url: Documentation site root URL (e.g. https://docs.example.com).
        max_pages: Maximum pages to download (0 = unlimited).
        workers: Parallel download workers (default 5).

    Returns:
        Summary dict with domain, pages downloaded, errors, provider, and path.
    """
    try:
        from gitbook_downloader.engine import stream_download

        domain = _domain_from_url(url)
        provider = detect_provider(url, _session)
        logger.info("Detected provider: %s for %s", provider.name, domain)

        # Snapshot previous version if domain already exists
        if _storage.domain_exists(domain):
            try:
                _versioning.snapshot(domain)
                logger.info("Snapshotted previous version for %s", domain)
            except Exception:
                pass

        # Write to a temp file first; save_doc handles the canonical storage
        with tempfile.NamedTemporaryFile(
            suffix=".md", delete=False, mode="w", encoding="utf-8"
        ) as tmp:
            output_path = tmp.name

        progress: dict = {
            "pages": 0,
            "errors": 0,
            "size_kb": 0,
            "discovered": 0,
        }

        def _progress_cb(data: dict) -> None:
            _emit_progress(data, progress)

        result = stream_download(
            url,
            output_file=output_path,
            max_pages=max_pages,
            workers=workers,
            progress_callback=_progress_cb,
        )

        # Read the downloaded content and persist via StorageManager
        content = Path(output_path).read_text(encoding="utf-8")
        title = provider.extract_title(content, url)

        meta = _storage.save_doc(
            domain=domain,
            content=content,
            url=url,
            title=title,
            pages=result.get("total_pages", progress["pages"]),
            provider=provider.name,
            new_pages=result.get("new_pages", progress["pages"]),
            size_kb=result.get("size_kb", progress["size_kb"]),
        )

        # Index for search (if available)
        if _search is not None:
            try:
                _search.index_domain(domain, content, domain_url=url)
            except Exception as exc:
                logger.warning("Search indexing failed: %s", exc)

        # Cleanup temp file
        try:
            Path(output_path).unlink(missing_ok=True)
        except OSError:
            pass

        return {
            "domain": domain,
            "pages": result.get("new_pages", progress["pages"]),
            "total_pages": result.get("total_pages", 0),
            "errors": result.get("errors", progress["errors"]),
            "provider": provider.name,
            "size_kb": result.get("size_kb", progress["size_kb"]),
            "path": str(_storage.latest_path(domain)),
            "metadata": meta,
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
        return [
            {
                "error": (
                    "Search index not available. "
                    "Install with: pip install 'gitbook-downloader[search]'"
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
