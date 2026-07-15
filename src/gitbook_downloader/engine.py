"""Download engine — orchestrates discovery, downloading, extraction, and storage.

Provides stream_download() as the main entry point for CLI, GUI, and MCP.
"""

import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import requests

from gitbook_downloader.providers import Provider, detect_provider, ProviderRegistry
from gitbook_downloader.providers.base import normalize_url, same_domain
from gitbook_downloader.storage import StorageManager, VersionManager
from gitbook_downloader.utils import create_session
from gitbook_downloader.utils.discovery import discover_from_llms_txt, discover_from_sitemap
from gitbook_downloader.search import SearchIndex

logger = logging.getLogger(__name__)


def stream_download(
    url: str,
    max_pages: int = 0,
    workers: int = 5,
    session: Optional[requests.Session] = None,
    provider: Optional[Provider] = None,
    progress_callback: Optional[callable] = None,
) -> str:
    """Download an entire documentation site.

    Auto-detects the documentation platform, discovers all pages,
    downloads them in parallel, extracts clean markdown, and saves
    to the per-domain storage.

    Args:
        url: Root URL of the documentation site.
        max_pages: Maximum pages to download (0 = unlimited).
        workers: Number of concurrent download threads.
        session: Pre-configured requests Session (created if None).
        provider: Provider instance for the site (auto-detected if None).
        progress_callback: Optional callable receiving progress dicts.

    Returns:
        Combined markdown content of all downloaded pages.
    """
    if session is None:
        session = create_session()

    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")

    # Auto-detect provider
    if provider is None:
        provider = detect_provider(url, session)

    logger.info("Detected provider: %s for %s", provider.name, url)

    if progress_callback:
        progress_callback({"phase": "discovery", "status": "start", "url": url})

    all_content_parts: list[str] = []
    total_size_kb = 0.0
    pages_downloaded = 0
    pages_errored = 0

    # ── Discovery ────────────────────────────────────────────────
    discovered_urls: set[str] = set()

    # Try provider-specific discovery (llms.txt / sitemap)
    try:
        discovered_urls = provider.discover_urls(url, session)
    except Exception as e:
        logger.debug("Provider discovery failed: %s", e)

    # Fallback: try generic discovery methods
    if not discovered_urls:
        try:
            discovered_urls = discover_from_llms_txt(url, session)
        except Exception:
            pass
    if not discovered_urls:
        try:
            discovered_urls = discover_from_sitemap(url, session)
        except Exception:
            pass

    if progress_callback:
        progress_callback({
            "phase": "discovery",
            "status": "done",
            "discovered": len(discovered_urls),
            "url": url,
        })

    logger.info("Discovered %d URLs for %s", len(discovered_urls), domain)

    # ── Prepare crawl frontier ───────────────────────────────────
    if discovered_urls:
        # Discovered URLs are the complete set
        crawl_urls = list(discovered_urls)
    else:
        # No discovery method worked — start BFS from root
        crawl_urls = [url]

    # Apply max_pages limit
    if max_pages > 0:
        crawl_urls = crawl_urls[:max_pages]

    # ── Download ─────────────────────────────────────────────────
    lock = threading.Lock()
    url_content: dict[str, str] = {}

    def download_one(url_to_fetch: str) -> tuple[Optional[str], str, Optional[str]]:
        """Download a single URL, return (content, url, error)."""
        nonlocal pages_downloaded, pages_errored, total_size_kb
        try:
            content = provider.extract_content(url_to_fetch, session)
            if not content or len(content.strip()) < 60:
                return None, url_to_fetch, "Content too short"

            with lock:
                pages_downloaded += 1
                size_kb = len(content.encode("utf-8")) / 1024
                total_size_kb += size_kb

            title = provider.extract_title(content, url_to_fetch)

            if progress_callback:
                progress_callback({
                    "phase": "downloaded",
                    "url": url_to_fetch,
                    "title": title,
                    "size_kb": round(size_kb, 1),
                    "provider": provider.name,
                })

            return content, url_to_fetch, None

        except Exception as e:
            with lock:
                pages_errored += 1
            error_msg = str(e)[:100]
            if progress_callback:
                progress_callback({
                    "phase": "error",
                    "url": url_to_fetch,
                    "error": error_msg,
                })
            return None, url_to_fetch, error_msg

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(download_one, u): u for u in crawl_urls}
        for future in as_completed(futures):
            content, fetched_url, error = future.result()
            if content:
                url_content[fetched_url] = content

    # ── Assemble content ─────────────────────────────────────────
    all_content_parts = list(url_content.values())

    combined = ""
    for i, (u, content) in enumerate(url_content.items()):
        if i > 0:
            combined += "\n\n---\n\n"
        # Add source marker for search indexing
        combined += f"Source: {u}\n\n{content}"

    if not combined.strip():
        if progress_callback:
            progress_callback({
                "phase": "done",
                "pages": 0,
                "errors": pages_errored,
                "total_size_kb": 0,
                "provider": provider.name,
                "error": "No content downloaded",
            })
        return ""

    # ── Save to storage ──────────────────────────────────────────
    storage = StorageManager()
    versioning = None

    # Snapshot previous version if it exists
    if storage.domain_exists(domain):
        try:
            versioning = VersionManager(storage)
            version = versioning.snapshot(domain)
            if progress_callback:
                progress_callback({
                    "phase": "snapshot",
                    "domain": domain,
                    "version": version,
                })
        except Exception as e:
            logger.warning("Snapshot failed: %s", e)

    storage.save_doc(
        domain=domain,
        content=combined,
        url=url,
        title=provider.extract_title(combined, url),
        pages=pages_downloaded,
        provider=provider.name,
        new_pages=pages_downloaded,
        size_kb=round(total_size_kb, 1),
    )

    # ── Index for search ─────────────────────────────────────────
    try:
        search = SearchIndex()
        search.index_domain(domain, combined, domain_url=url)
    except Exception as e:
        logger.warning("Search indexing failed: %s", e)

    if progress_callback:
        progress_callback({
            "phase": "done",
            "pages": pages_downloaded,
            "errors": pages_errored,
            "total_size_kb": round(total_size_kb, 1),
            "provider": provider.name,
        })

    return combined


def download_urls(
    urls: set[str],
    provider: Provider,
    session: requests.Session,
    workers: int = 5,
    progress_callback: Optional[callable] = None,
) -> dict[str, str]:
    """Download multiple URLs in parallel using the given provider.

    Args:
        urls: Set of URLs to download.
        provider: Provider instance for content extraction.
        session: requests.Session to use.
        workers: Number of concurrent download threads.
        progress_callback: Optional progress callback.

    Returns:
        Dict mapping URL → markdown content for successful downloads.
    """
    results: dict[str, str] = {}
    error_count = 0
    lock = threading.Lock()

    def download_one(url_to_fetch: str) -> tuple[Optional[str], str]:
        try:
            content = provider.extract_content(url_to_fetch, session)
            if content and len(content.strip()) >= 60:
                return content, url_to_fetch
            return None, url_to_fetch
        except Exception:
            return None, url_to_fetch

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(download_one, u): u for u in urls}
        for future in as_completed(futures):
            content, fetched_url = future.result()
            if content:
                results[fetched_url] = content
                if progress_callback:
                    progress_callback({
                        "phase": "downloaded",
                        "url": fetched_url,
                        "size_kb": round(len(content.encode("utf-8")) / 1024, 1),
                    })
            else:
                with lock:
                    error_count += 1
                if progress_callback:
                    progress_callback({
                        "phase": "error",
                        "url": fetched_url,
                        "error": "Download failed",
                    })

    return results
