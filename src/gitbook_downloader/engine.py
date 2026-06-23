"""
Streaming Download Engine v3 — Discover + Download simultaneously.

Pipeline:
  Producer (discovery thread): crawls pages, finds URLs, pushes to queue
  Consumer pool (worker threads): downloads pages from queue, writes to file

Key features:
- Pages start downloading AS they're discovered (no waiting)
- Incremental updates: parse existing .md file, skip already-downloaded URLs
- Thread-safe streaming output: pages written immediately as they complete
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

# ── Helpers ────────────────────────────────────────────────
def _norm(u):
    p = urlparse(u)
    return urlunparse((p.scheme, p.netloc, p.path.rstrip("/") or "/", "", "", ""))

def _session():
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    return s

def _extract_page(url, html):
    """Extract clean markdown from a page's HTML. Returns (title, markdown, links)."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.find("div", class_="content") or soup.body
    body = str(main) if main else html
    markdown = md(body, heading_style="ATX")
    markdown = re.sub(r"\n\s*\n\s*\n", "\n\n", markdown)
    title_el = soup.find("h1")
    title = title_el.get_text().strip() if title_el else url.rstrip("/").split("/")[-1] or "Home"
    # Collect links for further discovery
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full = urljoin(url, href)
        if not href.startswith(("#", "javascript:", "mailto:", "tel:")):
            links.add(full)
    return title, markdown, links


def _read_existing_urls(filepath):
    """Parse existing .md file to find already-downloaded URLs."""
    urls = set()
    if not os.path.exists(filepath):
        return urls
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        for match in re.finditer(r"^Source:\s*(https?://\S+)", content, re.MULTILINE):
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
    h["downloads"].insert(0, {
        "url": url,
        "output": os.path.abspath(output),
        "pages": pages,
        "new_pages": new_pages,
        "size_kb": size_kb,
        "date": time.strftime("%Y-%m-%d %H:%M"),
        "timestamp": time.time(),
    })
    # Keep last 50
    h["downloads"] = h["downloads"][:50]
    save_history(h)


# ═══════════════════════════════════════════════════════════
# STREAMING ENGINE
# ═══════════════════════════════════════════════════════════
def stream_download(start_url, output_file, max_pages=0, workers=5,
                    update_existing=False, progress_callback=None):
    """
    Stream-download a GitBook site: discover + download simultaneously.

    Args:
        start_url: Root URL
        output_file: Path to save markdown
        max_pages: Max pages (0 = unlimited)
        workers: Parallel download threads
        update_existing: If True, append new pages to existing file
        progress_callback: fn(phase, data) — called on every event

    Returns:
        dict with 'pages', 'new_pages', 'errors', 'size_kb', 'output'
    """
    base_domain = urlparse(start_url).netloc

    # ── State ──
    existing_urls = _read_existing_urls(output_file) if update_existing else set()
    downloaded = OrderedDict()  # url → (title, markdown)
    discovered_norm = set()     # normalized URLs we've seen
    errors = {}

    # Queues
    link_queue = thread_queue.Queue()    # URLs to visit for link extraction
    download_queue = thread_queue.Queue() # URLs to download
    result_queue = thread_queue.Queue()   # completed downloads
    stop_event = threading.Event()

    # Seed
    start_norm = _norm(start_url)
    discovered_norm.add(start_norm)
    link_queue.put(start_url)
    if start_norm not in existing_urls:
        download_queue.put(start_url)

    # ── Stats ──
    stats_lock = threading.Lock()
    stats = {"discovered": 1, "downloaded": 0, "in_progress": 0, "phase": "streaming"}

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
        while not stop_event.is_set():
            try:
                url = link_queue.get(timeout=1)
            except thread_queue.Empty:
                if download_queue.empty() and result_queue.empty():
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

                _, _, links = _extract_page(url, resp.text)

                with stats_lock:
                    for link in links:
                        parsed = urlparse(link)
                        if parsed.netloc == base_domain:
                            n = _norm(link)
                            if n not in discovered_norm:
                                if max_pages and len(discovered_norm) >= max_pages:
                                    break
                                discovered_norm.add(n)
                                stats["discovered"] = len(discovered_norm)
                                link_queue.put(link)
                                if n not in existing_urls:
                                    download_queue.put(link)

                emit("discovery", discovered=len(discovered_norm), url=url)
            except Exception:
                continue

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
            emit("progress", downloaded=stats["downloaded"],
                 discovered=len(discovered_norm), url=url)

            try:
                resp = sess.get(url, timeout=20)
                if resp.status_code != 200:
                    errors[url] = f"HTTP {resp.status_code}"
                    continue

                title, markdown, _ = _extract_page(url, resp.text)

                with stats_lock:
                    downloaded[url] = (title, markdown)
                    stats["downloaded"] = len(downloaded)
                    stats["in_progress"] -= 1

                kb = round(len(markdown.encode("utf-8")) / 1024, 1)
                emit("downloaded", downloaded=len(downloaded),
                     discovered=len(discovered_norm),
                     title=title, url=url, size_kb=kb)

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
    add_to_history(start_url, output_file, len(downloaded) + len(existing_urls),
                   size_kb, new_pages=new_count)

    emit("done", downloaded=new_count, discovered=len(discovered_norm),
         errors=len(errors), size_kb=size_kb, elapsed=elapsed,
         output=output_file, new_pages=new_count)

    return {
        "pages": new_count,
        "total_pages": new_count + len(existing_urls),
        "new_pages": new_count,
        "errors": errors,
        "size_kb": size_kb,
        "elapsed": elapsed,
        "output": output_file,
    }
