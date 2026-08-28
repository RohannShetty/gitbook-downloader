"""Download engine — orchestrates discovery, downloading, extraction, and storage.

Provides stream_download() as the main entry point for CLI, GUI, and MCP.
"""

import logging
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests

from gitbook_downloader.providers import Provider, detect_provider, ProviderRegistry
from gitbook_downloader.providers.base import (
    decode_response,
    looks_like_challenge_or_blocked,
    looks_like_spa_shell,
    normalize_url,
    same_domain,
)
from gitbook_downloader.storage import StorageManager, VersionManager
from gitbook_downloader.utils import create_session
from gitbook_downloader.utils.discovery import discover_from_llms_txt, discover_from_sitemap
from gitbook_downloader.search import SearchIndex

logger = logging.getLogger(__name__)

# Language codes that appear as URL path segments on multi-language docs
# sites. Pages under any of these segments are treated as translations and
# excluded from English crawls.
_LANG_CODES = frozenset({
    "zh", "zh-cn", "zh-tw", "zh-hans", "zh-hant",
    "ko", "ja", "de", "es", "fr", "it", "da", "pl", "ru",
    "uk", "ar", "nb", "pt", "pt-br", "th", "tr", "vi", "id", "hi",
    "nl", "sv", "cs", "hu", "ro", "el", "he", "fa", "bn",
    "ta", "te", "mr", "gu", "kn", "ml", "pa", "ur", "sw",
    "fi", "no", "ca", "eu", "gl", "af", "sq", "am", "az",
    "be", "bg", "bs", "cy", "et", "ga", "hy", "is", "ka",
    "kk", "km", "ky", "lo", "lt", "lv", "mk", "mn", "my",
    "ne", "ps", "si", "sk", "sl", "sr", "tl", "uz", "yo",
    "zu", "ha", "ig", "mg", "sn", "st", "xh",
})


def _as_prefixes(value) -> tuple[str, ...]:
    """Normalise a scope/exclude argument (str | iterable | None) to a tuple."""
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(value)


def _matches_prefix(path: str, prefix: str) -> bool:
    """Segment-boundary prefix match: ``/docs`` matches ``/docs`` and
    ``/docs/x`` but never ``/docsx``."""
    prefix = prefix.rstrip("/")
    if prefix == "":
        return True  # "/" or "" scopes everything
    return path == prefix or path.startswith(prefix + "/")


def _within_scope(path: str, prefixes: tuple[str, ...]) -> bool:
    if not prefixes:
        return True
    return any(_matches_prefix(path, p) for p in prefixes)


def _is_excluded(path: str, patterns: tuple[str, ...]) -> bool:
    return any(pat in path for pat in patterns)


def _segment_is_lang(u: str) -> bool:
    """True if any path segment of *u* is a language code."""
    segments = [s.replace("_", "-").lower() for s in urlparse(u).path.split("/") if s]
    return any(seg in _LANG_CODES for seg in segments)


_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")


def rewrite_markdown_links(md_text: str, page_url: str) -> str:
    """Rewrite markdown links for the downloaded book.

    - Relative hrefs are resolved against *page_url*.
    - Same-site links become relative markdown paths between pages.
    - Anchor-only links are stripped down to their link text.
    - External links are left absolute.
    """
    from gitbook_downloader.providers.base import same_domain

    def _rel_site_path(target_path: str, page_path: str) -> str:
        import posixpath

        target = "/" + target_path.lstrip("/")
        page_dir = posixpath.dirname("/" + page_path.lstrip("/"))
        if page_dir == "/":
            return target.lstrip("/")
        return posixpath.relpath(target, page_dir)

    def _sub(m: re.Match) -> str:
        text, href = m.group(1), m.group(2)
        if href.startswith(("mailto:", "javascript:", "tel:", "data:")):
            return m.group(0)
        parsed = urlparse(href)
        if not parsed.scheme and not parsed.netloc and href.startswith("#"):
            return text  # anchor-only → keep the text
        absolute = urljoin(page_url, href)
        if same_domain(absolute, page_url):
            t_parsed = urlparse(absolute)
            suffix = ("?" + t_parsed.query) if t_parsed.query else ""
            if t_parsed.fragment:
                suffix += "#" + t_parsed.fragment
            return f"[{text}]({_rel_site_path(t_parsed.path, urlparse(page_url).path)}{suffix})"
        return f"[{text}]({absolute})"

    return _MD_LINK_RE.sub(_sub, md_text)


def _bfs_crawl(
    start_url: str,
    provider,
    session: requests.Session,
    max_pages: int | None = 500,
    path_scope: str | tuple[str, ...] | list[str] | None = None,
    exclude_paths: str | tuple[str, ...] | list[str] | None = None,
    timeout: float = 20.0,
    cancel_check: Optional[callable] = None,
    progress_callback: Optional[callable] = None,
) -> list[str]:
    """BFS crawl from *start_url*, extracting same-domain ``<a>`` links.

    Uses the provider's ``extract_links`` method when available, otherwise
    falls back to generic ``<a href>`` extraction via BeautifulSoup.
    Anchor-only links are stripped before enqueueing; ``path_scope`` and
    ``exclude_paths`` are enforced on every enqueued link.

    Args:
        start_url:     The root URL to begin crawling.
        provider:      Provider instance (used for ``extract_links`` if available).
        session:       A ``requests.Session``.
        max_pages:     Safety cap on pages to enqueue; ``None`` = unlimited.
        path_scope:    Optional path prefix(es) to restrict URLs to.
        exclude_paths: Path substrings to skip.
        timeout:       Per-request timeout in seconds.
        cancel_check:  Optional callback returning True when crawl is aborted.
        progress_callback: Optional progress update callback.

    Returns:
        A de-duplicated list of discovered URLs (normalised), in crawl order.
    """
    from collections import deque
    from urllib.parse import urlunparse
    from bs4 import BeautifulSoup

    from gitbook_downloader.providers.base import is_md_url, looks_like_html

    scope_prefixes = _as_prefixes(path_scope)
    # If no explicit scope was given but the start URL has a subpath (e.g. /docs/latest),
    # default to the start URL's path so generic crawler doesn't wander to homepage/news.
    if not scope_prefixes and not path_scope:
        start_path = urlparse(start_url).path.rstrip("/")
        if start_path and start_path != "/":
            scope_prefixes = (start_path,)

    exclude_patterns = _as_prefixes(exclude_paths)

    base_domain = urlparse(start_url).netloc
    visited: set[str] = set()
    queue: deque[str] = deque()
    result: list[str] = []

    start_norm = normalize_url(start_url)
    visited.add(start_norm)
    queue.append(start_url)

    while queue and (max_pages is None or len(result) < max_pages):
        if cancel_check and cancel_check():
            logger.info("BFS crawl cancelled by user")
            break
        current = queue.popleft()
        result.append(current)

        if progress_callback:
            progress_callback({
                "phase": "discovered",
                "url": current,
                "count": len(visited),
                "message": f"Crawling frontier: {current}",
            })

        try:
            resp = session.get(current, timeout=timeout)
            if resp.status_code != 200:
                continue
            html = decode_response(resp)
        except Exception:
            continue

        # Extract links
        try:
            if hasattr(provider, "extract_links"):
                links = provider.extract_links(
                    current,
                    html,
                    path_scope=path_scope if not scope_prefixes else None,
                    exclude_paths=list(exclude_patterns) or None,
                )
                if scope_prefixes:
                    # Provider call got no scope — enforce segment-boundary here.
                    links = {
                        u for u in links
                        if _within_scope(urlparse(u).path, scope_prefixes)
                        and not _is_excluded(urlparse(u).path, exclude_patterns)
                    }
            else:
                soup = BeautifulSoup(html, "html.parser")
                links = set()
                current_norm = normalize_url(current)
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith(("javascript:", "mailto:", "tel:", "data:")):
                        continue
                    full = urljoin(current, href)
                    parsed = urlparse(full)
                    if parsed.netloc != base_domain:
                        continue
                    if is_md_url(full):
                        continue
                    if parsed.path.startswith("/~gitbook"):
                        continue
                    # Strip fragments; drop pure-anchor self-links.
                    stripped = urlunparse(
                        (parsed.scheme, parsed.netloc, parsed.path, "", parsed.query, "")
                    )
                    if parsed.fragment and normalize_url(stripped) == current_norm:
                        continue
                    if not _within_scope(parsed.path, scope_prefixes):
                        continue
                    if _is_excluded(parsed.path, exclude_patterns):
                        continue
                    links.add(stripped)
        except Exception:
            continue

        for link in links:
            norm = normalize_url(link)
            if norm not in visited:
                visited.add(norm)
                queue.append(link)
                if progress_callback and len(visited) % 5 == 0:
                    progress_callback({
                        "phase": "discovered",
                        "url": link,
                        "count": len(visited),
                        "message": f"Discovered URL #{len(visited)}: {link}",
                    })

    return result


def stream_download(
    url: str,
    max_pages: int | None = 0,
    workers: int = 5,
    session: Optional[requests.Session] = None,
    provider: Optional[Provider] = None,
    progress_callback: Optional[callable] = None,
    path_scope: str | tuple[str, ...] | list[str] | None = None,
    exclude_paths: str | tuple[str, ...] | list[str] | None = None,
    timeout: float = 20.0,
    cancel_check: Optional[callable] = None,
    render: bool = False,
) -> str:
    """Download an entire documentation site.

    Auto-detects the documentation platform, discovers all pages,
    downloads them in parallel, extracts clean markdown, and saves
    to the per-domain storage.

    Args:
        url: Root URL of the documentation site.
        max_pages: Maximum pages to download (``None`` or ``0`` = unlimited).
        workers: Number of concurrent download threads.
        session: Pre-configured requests Session (created if None).
        provider: Provider instance for the site (auto-detected if None).
        progress_callback: Optional callable receiving progress dicts.
        path_scope: URL path prefix(es) to restrict the crawl to.
        exclude_paths: Path substrings to skip even inside the scope.
        timeout: Per-request timeout in seconds.
        cancel_check: Optional callable returning True when cancellation is requested.

    Returns:
        Combined markdown content of all downloaded pages.
    """
    if session is None:
        session = create_session(timeout=timeout)

    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")

    scope_prefixes = _as_prefixes(path_scope)
    exclude_patterns = _as_prefixes(exclude_paths)

    # Auto-detect provider
    if provider is None:
        provider = detect_provider(url, session)

    logger.info("Detected provider: %s for %s", provider.name, url)

    if progress_callback:
        progress_callback({"phase": "discovery", "status": "start", "url": url})

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

    # ── Filter discovered URLs by scope + exclusions + language ──
    # Explicit path_scope prefixes win; otherwise a sub-page input URL
    # auto-expands to its documentation root (e.g., /docs/installation -> /docs).
    # Language segments (/zh-cn/, /pt/…) are always filtered out.
    input_path = urlparse(url).path.rstrip("/")
    implicit_scope = input_path

    _DOC_ROOT_NAMES = {
        "docs", "doc", "documentation", "guide", "guides",
        "manual", "handbook", "tutorial", "tutorials", "learn",
        "api", "reference", "help",
    }
    if not scope_prefixes and input_path:
        parts = [p for p in input_path.split("/") if p]
        for i, seg in enumerate(parts):
            if seg.lower() in _DOC_ROOT_NAMES:
                implicit_scope = "/" + "/".join(parts[:i + 1])
                break
        else:
            if len(parts) > 1 and (parts[-1].endswith((".html", ".htm", ".md")) or len(parts) >= 2):
                implicit_scope = "/" + "/".join(parts[:-1])

    def _is_english_url(u: str) -> bool:
        """True if *u* is inside scope, not excluded, and not a translation."""
        p = urlparse(u).path.rstrip("/")
        if not _within_scope(p, scope_prefixes):
            return False
        if not scope_prefixes and implicit_scope and not _matches_prefix(p, implicit_scope):
            return False
        if _is_excluded(p, exclude_patterns):
            return False
        # A language-code segment at ANY depth marks a translation page.
        segments = [s.lower() for s in p.split("/") if s]
        return not any(seg in _LANG_CODES for seg in segments)

    if discovered_urls:
        filtered = {u for u in discovered_urls if _is_english_url(u)}
        if len(filtered) < len(discovered_urls):
            logger.info(
                "Filtered %d → %d URLs (scope=%s excludes=%s, English only)",
                len(discovered_urls), len(filtered),
                scope_prefixes or implicit_scope or "/", exclude_patterns,
            )
        if not filtered:
            # Never fall back to the unfiltered set — surface the mismatch.
            logger.warning(
                "All %d discovered URLs were filtered out for %s "
                "(scope=%s); nothing to download.",
                len(discovered_urls), url, scope_prefixes or implicit_scope or "/",
            )
            if progress_callback:
                progress_callback({
                    "phase": "warning",
                    "type": "warning",
                    "message": (
                        f"All {len(discovered_urls)} discovered URLs were filtered "
                        f"out by scope/exclusions; nothing to download."
                    ),
                    "url": url,
                })
        discovered_urls = filtered

    # ── Prepare crawl frontier ───────────────────────────────────
    if discovered_urls:
        # Discovered URLs are the complete set — sorted for deterministic
        # book order (sets have no stable iteration order).
        crawl_urls = sorted(discovered_urls)
    else:
        # No discovery method worked — BFS crawl from root, extracting
        # same-domain <a> links up to a safety cap.
        logger.info("No discovery data; starting BFS crawl from %s", url)
        crawl_urls = _bfs_crawl(
            url,
            provider,
            session,
            max_pages=max_pages if max_pages else None,
            path_scope=path_scope,
            exclude_paths=exclude_paths,
            timeout=timeout,
            cancel_check=cancel_check,
            progress_callback=progress_callback,
        )
        # Language filter applies to BFS output too.
        if crawl_urls:
            bfs_filtered = [u for u in crawl_urls if not _segment_is_lang(u)]
            if len(bfs_filtered) != len(crawl_urls):
                logger.info(
                    "Language filter removed %d BFS URL(s)",
                    len(crawl_urls) - len(bfs_filtered),
                )
            crawl_urls = bfs_filtered

    if cancel_check and cancel_check():
        raise RuntimeError("Capture aborted by user")

    # Apply max_pages limit (None/0 = unlimited)
    if max_pages:
        crawl_urls = crawl_urls[:max_pages]

    # ── Download ─────────────────────────────────────────────────
    lock = threading.Lock()
    url_content: dict[str, str] = {}

    def download_one(url_to_fetch: str) -> tuple[Optional[str], str, Optional[str]]:
        """Download a single URL, return (content, url, error)."""
        nonlocal pages_downloaded, pages_errored, total_size_kb
        if cancel_check and cancel_check():
            return None, url_to_fetch, "Cancelled"
        try:
            content = ""
            if render:
                try:
                    from .utils.renderer import HeadlessRenderer, is_render_available
                    if not is_render_available():
                        raise RuntimeError(
                            "Headless rendering requires Playwright. Install with: "
                            "pip install \"gitbook-downloader[render]\" && playwright install chromium"
                        )
                    renderer = HeadlessRenderer()
                    html = renderer.render_url(url_to_fetch)
                    if hasattr(provider, "_extract_md_from_html"):
                        content = provider._extract_md_from_html(html)
                    else:
                        from markdownify import markdownify as md
                        content = md(html, heading_style="ATX").strip()
                except Exception as exc:
                    logger.warning("Render failed for %s: %s; falling back to provider extract", url_to_fetch, exc)
                    if progress_callback:
                        progress_callback({
                            "phase": "error",
                            "url": url_to_fetch,
                            "error": f"Render failed: {exc}",
                        })
                    content = provider.extract_content(url_to_fetch, session)
            else:
                content = provider.extract_content(url_to_fetch, session)

            if cancel_check and cancel_check():
                return None, url_to_fetch, "Cancelled"
            if not content or len(content.strip()) < 60:
                # Diagnostic check for thin content
                err_detail = "Content too short"
                try:
                    r = session.get(url_to_fetch, timeout=10)
                    h = decode_response(r)
                    if looks_like_challenge_or_blocked(h, r.status_code):
                        err_detail = "Anti-bot challenge / blocked"
                    elif looks_like_spa_shell(h):
                        err_detail = "Client-rendered SPA shell (try --render)"
                except Exception:
                    pass
                return None, url_to_fetch, err_detail

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
            if cancel_check and cancel_check():
                executor.shutdown(wait=False, cancel_futures=True)
                raise RuntimeError("Capture aborted by user")
            content, fetched_url, error = future.result()
            if content:
                url_content[fetched_url] = content

    # ── Assemble content ─────────────────────────────────────────
    # Deterministic order: follow crawl_urls order (discovery/BFS order),
    # never thread-completion order, so snapshot diffs stay stable.
    ordered_pages: list[tuple[str, str]] = []
    for u in crawl_urls:
        content = url_content.get(u)
        if content:
            ordered_pages.append((u, content))

    entry_title = ""
    combined_parts: list[str] = []
    for i, (u, raw_content) in enumerate(ordered_pages):
        if i == 0:
            entry_title = provider.extract_title(raw_content, u)
        rewritten = rewrite_markdown_links(raw_content, u)
        combined_parts.append(f"Source: {u}\n\n{rewritten}")

    combined = "\n\n---\n\n".join(combined_parts)

    if not combined.strip():
        # Diagnostic detection for empty crawl
        err_msg = "No content downloaded"
        try:
            root_resp = session.get(url, timeout=10)
            root_html = decode_response(root_resp)
            if looks_like_challenge_or_blocked(root_html, root_resp.status_code):
                err_msg = "Anti-bot challenge detected (Cloudflare/DataDome blocked static requests)"
            elif looks_like_spa_shell(root_html):
                err_msg = "Client-rendered SPA detected (no readable content in static HTML — try --render)"
        except Exception:
            pass

        if progress_callback:
            progress_callback({
                "phase": "done",
                "pages": 0,
                "errors": pages_errored,
                "total_size_kb": 0,
                "provider": provider.name,
                "error": err_msg,
            })
        logger.warning("Download produced 0 pages for %s: %s", url, err_msg)
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
        title=entry_title or provider.extract_title(combined, url),
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
