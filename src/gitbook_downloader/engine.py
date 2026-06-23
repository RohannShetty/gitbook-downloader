"""
Download Engine v2 — BFS discovery + parallel downloads for speed.

Phase 1 (Discovery): Sequential BFS crawl to find ALL pages.
Phase 2 (Download): ThreadPoolExecutor downloads pages concurrently.

This gives the completeness of BFS with the speed of parallel fetching.
"""

import os
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import OrderedDict
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md


def _normalize_url(u):
    """Strip fragments and trailing slashes for dedup."""
    p = urlparse(u)
    path = p.path.rstrip("/") or "/"
    return urlunparse((p.scheme, p.netloc, path, "", "", ""))


def _get_session():
    """Thread-local requests session."""
    sess = requests.Session()
    sess.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    })
    return sess


def _download_one(url, timeout=20):
    """Download a single page, return (url, title, markdown, error)."""
    try:
        sess = _get_session()
        resp = sess.get(url, timeout=timeout)
        if resp.status_code != 200:
            return (url, None, None, f"HTTP {resp.status_code}")

        soup = BeautifulSoup(resp.text, "html.parser")

        # Strip noise
        for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
            tag.decompose()

        # Find main content
        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_="content")
            or soup.body
        )
        html = str(main) if main else resp.text

        # Convert to markdown
        markdown = md(html, heading_style="ATX")
        markdown = re.sub(r"\n\s*\n\s*\n", "\n\n", markdown)

        # Extract title
        title_el = soup.find("h1")
        title = title_el.get_text().strip() if title_el else url.rstrip("/").split("/")[-1] or "Home"

        return (url, title, markdown, None)

    except requests.Timeout:
        return (url, None, None, "Timeout")
    except requests.ConnectionError:
        return (url, None, None, "Connection failed")
    except Exception as e:
        return (url, None, None, str(e)[:80])


def download_docs(start_url, output_file, max_pages=500, workers=5,
                  progress_callback=None, quiet=False):
    """
    Download a complete GitBook documentation site.

    Phase 1: BFS discovery — find all unique page URLs.
    Phase 2: Parallel download — fetch all pages concurrently.

    Args:
        start_url: Root URL of the GitBook site
        output_file: Path to save the combined markdown
        max_pages: Maximum pages to download
        workers: Number of parallel download threads (1-10)
        progress_callback: Optional fn(phase, current, total, message)
        quiet: Suppress console output

    Returns:
        Tuple of (pages_downloaded, errors_dict)
    """
    base_domain = urlparse(start_url).netloc

    # ── Phase 1: Discovery ───────────────────────────────
    if not quiet:
        print("🔍 Phase 1: Discovering pages…")

    discovered = set()
    to_visit = [start_url]
    visited = set()  # Normalized URLs we've crawled for links

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        norm = _normalize_url(url)
        if norm in visited:
            continue
        visited.add(norm)

        if not quiet:
            print(f"  [{len(visited)}] Scanning: {url}")

        if progress_callback:
            progress_callback("discovery", len(visited), max_pages,
                              f"Scanning {url}")

        try:
            sess = _get_session()
            resp = sess.get(url, timeout=15)
            if resp.status_code != 200:
                continue

            discovered.add(norm)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Find all internal links
            for link in soup.find_all("a", href=True):
                href = link["href"]
                full = urljoin(url, href)
                parsed = urlparse(full)

                if parsed.netloc == base_domain:
                    n = _normalize_url(full)
                    if n not in visited and full not in to_visit:
                        to_visit.append(full)

        except Exception:
            continue

    if not quiet:
        print(f"  ✓ Found {len(discovered)} unique pages\n")

    if progress_callback:
        progress_callback("discovery_done", len(discovered), len(discovered),
                          f"Found {len(discovered)} pages")

    # ── Phase 2: Parallel Download ───────────────────────
    if not quiet:
        print(f"📥 Phase 2: Downloading {len(discovered)} pages ({workers} workers)…")

    urls = sorted(discovered)
    results = OrderedDict()
    errors = {}
    done = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_download_one, u): u for u in urls}

        for future in as_completed(futures):
            url, title, markdown, error = future.result()
            done += 1

            if error:
                errors[url] = error
                if not quiet:
                    print(f"  ✕ [{done}/{len(urls)}] {url} — {error}")
            else:
                results[url] = (title, markdown)
                if not quiet:
                    kb = round(len(markdown.encode("utf-8")) / 1024, 1)
                    print(f"  ✓ [{done}/{len(urls)}] {title} ({kb} KB)")

            if progress_callback:
                progress_callback("download", done, len(urls),
                                  f"{title if title else url}")

    # ── Write Output ─────────────────────────────────────
    if not quiet:
        print("  Writing output file…")

    all_md = []
    for url, (title, markdown) in results.items():
        all_md.append(f"# {title}\n\nSource: {url}\n\n{markdown}\n\n---\n\n")

    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(all_md))

    total_kb = round(os.path.getsize(output_file) / 1024, 1)

    if not quiet:
        print(f"\n{'═' * 50}")
        print(f"  ✅ Done!")
        print(f"  📄 Pages: {len(results)}")
        print(f"  ✕ Errors: {len(errors)}")
        print(f"  📏 Size:  {total_kb} KB ({round(total_kb / 1024, 1)} MB)")
        print(f"  📂 Saved: {output_file}")
        if errors:
            print(f"\n  Failed URLs:")
            for u, e in list(errors.items())[:5]:
                print(f"    {u} → {e}")
            if len(errors) > 5:
                print(f"    … and {len(errors) - 5} more")
        print(f"{'═' * 50}")

    return len(results), errors
