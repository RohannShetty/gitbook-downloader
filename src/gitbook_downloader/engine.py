"""
Streaming Download Engine v5 — Discover + Download simultaneously.
Fixed for modern GitBook (React/Next.js) sites.

Pipeline:
  Producer (discovery thread): crawls pages (HTML), finds URLs, pushes to queue
  Consumer pool (worker threads): downloads pages (.md preferred), writes to file

v5 fixes:
  - .md URL duplication: pages ending in .md are excluded from crawl/discovery
  - .md content preference: consumer fetches URL.md for clean markdown instead of
    converting HTML to markdown (markdownify is poor on GitBook React HTML)
  - Link extraction before nav stripping: sidebar links in CSS-classed divs survive
  - Agent Instructions boilerplate removed from .md output
  - llms.txt discovery: optional, seeds the page list from GitBook's /llms.txt
"""

import os
import re
import json
import time
import threading
import queue as thread_queue
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# ── Agent Instructions boilerplate (GitBook adds this to .md exports) ───
_AGENT_BOILERPLATE = re.compile(
    r"---\s*\n# Agent Instructions\s*\n.*?(?=\n---\s*\n|\Z)",
    re.DOTALL,
)
_AGENT_BOILERPLATE_SIMPLE = re.compile(
    r"# Agent Instructions\s*\n.*?(?=\n---\s*\n|\Z)",
    re.DOTALL,
)
_LLM_REF_LINE = re.compile(
    r"^(>?\s*For the complete documentation index, see \[llms\.txt\].*)$",
    re.MULTILINE,
)

# ── Helpers ────────────────────────────────────────────────


def _norm(u):
    """Normalize a URL: strip fragments, trailing slash, and .md suffix."""
    p = urlparse(u)
    path = p.path.rstrip("/") or "/"
    # Normalise .md suffix — strip it so HTML and .md versions resolve to the same key
    if path.endswith(".md"):
        path = path[:-3] or "/"
    return urlunparse((p.scheme, p.netloc, path, "", "", ""))


def _is_md_url(u):
    """Return True if the URL ends in .md."""
    p = urlparse(u)
    return p.path.endswith(".md")


def _strip_agent_boilerplate(markdown_text):
    """Remove GitBook Agent Instructions boilerplate from .md content."""
    text = _AGENT_BOILERPLATE.sub("", markdown_text)
    text = _AGENT_BOILERPLATE_SIMPLE.sub("", text)
    text = _LLM_REF_LINE.sub("", text)
    # Clean up excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _session():
    s = requests.Session()
    s.headers.update(
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    return s


def _extract_links(url, html, path_scope=None):
    """Extract same-domain links from HTML for crawling/discovery.

    Does NOT strip nav/footer/etc. before extracting — we need sidebar links.
    If path_scope is set, only links whose path starts with path_scope are kept.
    Returns a set of absolute URLs.
    """
    soup = BeautifulSoup(html, "html.parser")
    base_domain = urlparse(url).netloc
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Skip javascript, mailto, tel
        if href.startswith(("javascript:", "mailto:", "tel:")):
            continue
        full = urljoin(url, href)
        parsed = urlparse(full)
        # Only keep same-domain links
        if parsed.netloc != base_domain:
            continue
        # Skip hash-only links
        if parsed.fragment and not parsed.path and not parsed.query:
            continue
        # Skip GitBook internal asset links
        if parsed.path.startswith("/~gitbook"):
            continue
        # Skip .md URLs from the crawl queue (will be derived for content)
        if _is_md_url(full):
            continue
        # Path scope filter — stay within the documentation prefix
        if path_scope and not parsed.path.startswith(path_scope):
            continue
        links.add(full)
    return links


def _fetch_md_content(url, sess):
    """Fetch the .md version of a page, returning clean markdown.

    Falls back to HTML→markdown extraction if .md is not available (404/403).
    """
    md_url = url.rstrip("/") + ".md"
    try:
        resp = sess.get(md_url, timeout=20)
        if resp.status_code == 200:
            text = resp.text
            # Parse from BeautifulSoup if it returned HTML (e.g. redirect to HTML)
            if text.strip().startswith("<!") or "data-dpl-id" in text[:500]:
                # It returned HTML, fall through to HTML extraction
                pass
            else:
                # Clean markdown — strip agent boilerplate
                return _strip_agent_boilerplate(text)
    except Exception:
        pass

    # Fallback: extract from HTML
    return _extract_md_from_html(url, sess)


def _extract_md_from_html(url, sess):
    """Fallback: download HTML and convert to markdown.

    Handles GitBook (React/Next.js), MkDocs Material, and generic doc sites.
    """
    try:
        resp = sess.get(url, timeout=20)
        if resp.status_code != 200:
            return ""
        html = resp.text
    except Exception:
        return ""

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
        tag.decompose()

    # Try multiple content selectors — GitBook first, then MkDocs, then generic
    main = (
        soup.find("main")
        or soup.find("article")
        # MkDocs Material content area
        or soup.find("div", class_=lambda c: c and ("md-content" in c or "rst-content" in c))
        or soup.find("div", class_="content")
        or soup.body
    )
    body = str(main) if main else html
    markdown = md(body, heading_style="ATX")
    # Clean up: normalize whitespace, strip MkDocs permalink noise
    markdown = re.sub(r"\n\s*\n\s*\n", "\n\n", markdown)
    # Strip MkDocs Material "¶" permalink anchors
    markdown = re.sub(r" ¶\n", "\n", markdown)
    return markdown.strip()


def _extract_page(url, html):
    """Extract page info for the CONSUMER (legacy path, kept for direct-HTML mode).

    Returns (title, markdown, links).
    Links are extracted BEFORE stripping for use by the producer path.
    This is still called by the direct-HTML path (no .md available).
    """
    soup = BeautifulSoup(html, "html.parser")
    # Extract links first (before stripping)
    links = _extract_links(url, html)
    # Now strip nav for content
    for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
        tag.decompose()
    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find("div", class_="content")
        or soup.body
    )
    body = str(main) if main else html
    markdown = md(body, heading_style="ATX")
    markdown = re.sub(r"\n\s*\n\s*\n", "\n\n", markdown)
    title_el = soup.find("h1")
    title = (
        title_el.get_text().strip()
        if title_el
        else url.rstrip("/").split("/")[-1] or "Home"
    )
    return title, markdown, links


def _read_existing_urls(filepath):
    """Parse existing .md file to find already-downloaded URLs."""
    urls = set()
    if not os.path.exists(filepath):
        return urls
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        for match in re.finditer(
            r"^Source:\s*(https?://\S+)", content, re.MULTILINE
        ):
            urls.add(_norm(match.group(1).strip()))
    except Exception:
        pass
    return urls


# ── History ────────────────────────────────────────────────
HISTORY_DIR = os.path.join(os.path.expanduser("~"), ".gitbook-downloader")
HISTORY_FILE = os.path.join(HISTORY_DIR, "history.json")


def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"downloads": []}


def save_history(history):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def add_to_history(url, output, pages, size_kb, new_pages=0):
    h = load_history()
    h["downloads"].insert(
        0,
        {
            "url": url,
            "output": os.path.abspath(output),
            "pages": pages,
            "new_pages": new_pages,
            "size_kb": size_kb,
            "date": time.strftime("%Y-%m-%d %H:%M"),
            "timestamp": time.time(),
        },
    )
    h["downloads"] = h["downloads"][:50]
    save_history(h)


# ── llms.txt discovery ────────────────────────────────────
def discover_from_llms_txt(start_url, sess=None):
    """Discover all pages from GitBook's /llms.txt.

    Returns a set of normalized URLs.
    """
    if sess is None:
        sess = _session()
    base = start_url.rstrip("/")
    llms_url = f"{base}/llms.txt"
    urls = set()
    try:
        resp = sess.get(llms_url, timeout=30)
        if resp.status_code != 200:
            return urls
        # Parse markdown links from llms.txt
        for match in re.finditer(r"\]\((https?://[^)]+)\)", resp.text):
            u = match.group(1)
            # Only keep same-domain links and strip .md
            parsed = urlparse(u)
            if parsed.netloc == urlparse(start_url).netloc:
                urls.add(_norm(u))
    except Exception:
        pass
    return urls


# ═══════════════════════════════════════════════════════════
# STREAMING ENGINE
# ═══════════════════════════════════════════════════════════
def stream_download(
    start_url,
    output_file,
    max_pages=0,
    workers=5,
    update_existing=False,
    progress_callback=None,
    use_llms_txt=True,
    prefer_md=True,
    path_scope=None,
    min_content_chars=60,
):
    """
    Stream-download a documentation site: discover + download simultaneously.

    Args:
        start_url: Root URL
        output_file: Path to save markdown
        max_pages: Max pages (0 = unlimited)
        workers: Parallel download threads
        update_existing: If True, append new pages to existing file
        progress_callback: fn(phase, data) — called on every event
        use_llms_txt: If True, try to discover pages from /llms.txt first
        prefer_md: If True, fetch .md versions for content (cleaner)
        path_scope: Optional path prefix — only crawl URLs starting with this
                    (e.g., '/docs/connect/v3/'). Filters out forum, blog, etc.
        min_content_chars: Skip pages with fewer characters of real content

    Returns:
        dict with 'pages', 'new_pages', 'errors', 'size_kb', 'output'
    """
    base_domain = urlparse(start_url).netloc

    # ── State ──
    existing_urls = _read_existing_urls(output_file) if update_existing else set()
    downloaded = OrderedDict()  # url → (title, markdown)
    discovered_norm = set()  # normalized URLs we've seen
    errors = {}

    # Queues
    link_queue = thread_queue.Queue()  # URLs to visit for link extraction
    download_queue = thread_queue.Queue()  # URLs to download
    result_queue = thread_queue.Queue()  # completed downloads
    stop_event = threading.Event()

    # ── Seed discovery ──
    start_norm = _norm(start_url)
    discovered_norm.add(start_norm)
    link_queue.put(start_url)
    if start_norm not in existing_urls:
        download_queue.put(start_url)

    # Try llms.txt for complete page list
    if use_llms_txt:
        sess = _session()
        llms_urls = discover_from_llms_txt(start_url, sess)
        if llms_urls:
            for u in llms_urls:
                # Apply path scope to llms.txt results too
                if path_scope and not urlparse(u).path.startswith(path_scope):
                    continue
                if u not in discovered_norm:
                    discovered_norm.add(u)
                    link_queue.put(u)
                    if u not in existing_urls and u not in downloaded:
                        download_queue.put(u)

    # ── Stats ──
    stats_lock = threading.Lock()
    stats = {"discovered": len(discovered_norm), "downloaded": 0, "in_progress": 0, "phase": "streaming"}

    def emit(phase, **kwargs):
        with stats_lock:
            d = dict(stats, phase=phase, **kwargs)
        if progress_callback:
            try:
                progress_callback(d)
            except Exception:
                pass

    # ── Producer: extract links from downloaded pages ──────
    def producer():
        processed = set()
        sess = _session()

        # Track idle time — if no new URLs discovered and downloads are done, exit
        last_new_discovery = time.time()
        idle_timeout = 15  # seconds without discovery before producer stops

        while not stop_event.is_set():
            try:
                url = link_queue.get(timeout=1)
            except thread_queue.Empty:
                # Check idle timeout
                if time.time() - last_new_discovery > idle_timeout:
                    if download_queue.empty() and link_queue.empty():
                        break
                continue

            norm = _norm(url)
            if norm in processed:
                continue
            processed.add(norm)

            if max_pages and len(discovered_norm) >= max_pages:
                continue

            try:
                resp = sess.get(url, timeout=15)
                if resp.status_code != 200:
                    continue

                # Extract links from FULL HTML (nav intact for sidebar discovery)
                links = _extract_links(url, resp.text, path_scope=path_scope)

                new_found = False
                with stats_lock:
                    for link in links:
                        n = _norm(link)
                        if n not in discovered_norm:
                            if max_pages and len(discovered_norm) >= max_pages:
                                break
                            discovered_norm.add(n)
                            stats["discovered"] = len(discovered_norm)
                            link_queue.put(link)
                            if n not in existing_urls:
                                download_queue.put(link)
                            new_found = True

                if new_found:
                    last_new_discovery = time.time()

                emit("discovery", discovered=len(discovered_norm), url=url)
            except Exception:
                continue

            # Check if we should stop early: all discovered pages downloaded
            with stats_lock:
                all_downloaded = (
                    stats["downloaded"] >= len(discovered_norm)
                    and download_queue.empty()
                )
            if all_downloaded and max_pages == 0:
                # All discovered pages are downloaded — stop exploring
                break

    # ── Consumer: download pages ───────────────────────────
    def download_worker():
        sess = _session()
        while not stop_event.is_set():
            try:
                url = download_queue.get(timeout=2)
            except thread_queue.Empty:
                continue  # Keep waiting, producer may still be discovering

            if url == "__DONE__":
                break  # Producer finished, no more URLs coming

            norm = _norm(url)
            if norm in existing_urls:
                continue

            with stats_lock:
                stats["in_progress"] += 1
            emit(
                "progress",
                downloaded=stats["downloaded"],
                discovered=len(discovered_norm),
                url=url,
            )

            try:
                if prefer_md:
                    # Fetch .md version for clean markdown
                    markdown = _fetch_md_content(url, sess)
                    # Derive title from the first H1 in the markdown
                    title_match = re.search(r"^# (.+)", markdown, re.MULTILINE)
                    title = title_match.group(1).strip() if title_match else (url.rstrip("/").split("/")[-1] or "Home")
                else:
                    # Legacy: fetch HTML and convert
                    resp = sess.get(url, timeout=20)
                    if resp.status_code != 200:
                        errors[url] = f"HTTP {resp.status_code}"
                        continue
                    title, markdown, _ = _extract_page(url, resp.text)

                if not markdown.strip():
                    # Skip empty pages
                    with stats_lock:
                        stats["in_progress"] -= 1
                    continue

                # Skip trivial pages with negligible content
                if min_content_chars and len(markdown) < min_content_chars:
                    with stats_lock:
                        stats["in_progress"] -= 1
                    continue

                with stats_lock:
                    downloaded[url] = (title, markdown)
                    stats["downloaded"] = len(downloaded)
                    stats["in_progress"] -= 1

                kb = round(len(markdown.encode("utf-8")) / 1024, 1)
                emit(
                    "downloaded",
                    downloaded=len(downloaded),
                    discovered=len(discovered_norm),
                    title=title,
                    url=url,
                    size_kb=kb,
                )

            except requests.Timeout:
                errors[url] = "Timeout"
            except requests.ConnectionError:
                errors[url] = "Connection failed"
            except Exception as e:
                errors[url] = str(e)[:80]
            finally:
                with stats_lock:
                    stats["in_progress"] -= 1

    # ── Run pipeline ──────────────────────────────────────
    t0 = time.time()

    # Start producer
    prod_thread = threading.Thread(target=producer, daemon=True)
    prod_thread.start()

    # Start consumer pool
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for _ in range(workers):
            futures.append(executor.submit(download_worker))

        # Wait for producer to finish discovering
        prod_thread.join(timeout=600)

        # Signal: no more URLs will be added to download_queue
        for _ in range(workers):
            download_queue.put("__DONE__")  # Sentinel value

        # Wait for all consumers to finish
        for f in futures:
            try:
                f.result(timeout=300)
            except Exception:
                pass

    stop_event.set()

    elapsed = round(time.time() - t0, 1)

    # ── Write output ──────────────────────────────────────
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

    if update_existing and os.path.exists(output_file):
        # Append mode: add new pages to existing file
        new_entries = []
        for url, (title, markdown) in downloaded.items():
            new_entries.append(f"# {title}\n\nSource: {url}\n\n{markdown}\n\n---\n\n")
        if new_entries:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write("\n".join(new_entries))
    else:
        # Fresh write
        all_md = []
        for url, (title, markdown) in downloaded.items():
            all_md.append(f"# {title}\n\nSource: {url}\n\n{markdown}\n\n---\n\n")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(all_md))

    size_kb = round(os.path.getsize(output_file) / 1024, 1)
    new_count = len(downloaded)

    # ── History ───────────────────────────────────────────
    add_to_history(
        start_url,
        output_file,
        len(downloaded) + len(existing_urls),
        size_kb,
        new_pages=new_count,
    )

    emit(
        "done",
        downloaded=new_count,
        discovered=len(discovered_norm),
        errors=len(errors),
        size_kb=size_kb,
        elapsed=elapsed,
        output=output_file,
        new_pages=new_count,
    )

    return {
        "pages": new_count,
        "total_pages": new_count + len(existing_urls),
        "new_pages": new_count,
        "errors": errors,
        "size_kb": size_kb,
        "elapsed": elapsed,
        "output": output_file,
        "discovered": len(discovered_norm),
    }
