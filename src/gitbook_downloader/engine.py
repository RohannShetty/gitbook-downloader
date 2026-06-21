"""
Smart Download Engine — Two-phase GitBook documentation downloader.

Phase 1: Discover ALL URLs via sitemaps + sidebar crawling.
Phase 2: Download all pages with retries, parallel workers, and rate limiting.
"""

import os
import re
import sys
import time
import json
import queue
import threading
import concurrent.futures
from collections import deque, OrderedDict
from datetime import timedelta
from urllib.parse import urljoin, urlparse, urlunparse
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md


class SmartEngine:
    """Two-phase: (1) discover ALL URLs via sitemaps + sidebar, (2) download with retries."""

    MAX_RETRIES = 3
    CONCURRENCY = 5
    RETRY_DELAY = [1, 3, 8]  # seconds — exponential backoff

    def __init__(self, start_url, output_file, max_pages=5000, progress_callback=None):
        self.start_url = start_url.rstrip("/")
        self.output_file = output_file
        self.max_pages = max_pages
        self.base_domain = urlparse(start_url).netloc

        self._stop = threading.Event()
        self.done = threading.Event()
        self.log = queue.Queue()
        self.stats = {
            "phase": "discovery",
            "discovered": 0,
            "downloaded": 0,
            "failed": 0,
            "retries": 0,
            "elapsed": 0,
        }
        self._lock = threading.Lock()
        self._failed_urls = {}
        self._session_local = threading.local()
        self.progress_callback = progress_callback

    def emit(self, level, msg):
        entry = {"level": level, "msg": msg, "stats": dict(self.stats)}
        self.log.put(entry)
        if self.progress_callback:
            try:
                self.progress_callback(entry)
            except Exception:
                pass

    def _get_session(self):
        if not hasattr(self._session_local, "session"):
            sess = requests.Session()
            sess.headers.update({
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
                )
            })
            self._session_local.session = sess
        return self._session_local.session

    def _normalize_url(self, url):
        p = urlparse(url)
        netloc = p.netloc.replace("www.", "")
        path = p.path.rstrip("/") or "/"
        return urlunparse((p.scheme, netloc, path, "", "", ""))

    def _is_internal(self, url):
        p = urlparse(url)
        return p.netloc in (self.base_domain, f"www.{self.base_domain}") or not p.netloc

    # ── PHASE 1: DISCOVER ALL URLs ───────────────────────────
    def _fetch_sitemap_urls(self, sitemap_url, depth=0):
        """Recursively fetch URLs from sitemap XML. Handles sitemap indexes."""
        if depth > 3 or self._stop.is_set():
            return set()

        urls = set()
        try:
            resp = self._get_session().get(sitemap_url, timeout=15)
            if resp.status_code != 200:
                return urls

            root = ET.fromstring(resp.text)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

            # Check if this is a sitemap INDEX
            sitemaps = root.findall("sm:sitemap", ns)
            if not sitemaps:
                sitemaps = root.findall("sitemap")
            if sitemaps:
                self.emit("info", f"  ↳ Sitemap index: {sitemap_url} → {len(sitemaps)} sub-sitemaps")
                for sm in sitemaps:
                    loc = sm.find("sm:loc", ns)
                    if loc is None:
                        loc = sm.find("loc")
                    if loc is not None and loc.text:
                        sub_urls = self._fetch_sitemap_urls(loc.text.strip(), depth + 1)
                        urls.update(sub_urls)
                return urls

            # Regular sitemap: extract <url><loc> entries
            url_els = root.findall("sm:url", ns)
            if not url_els:
                url_els = root.findall("url")
            for url_el in url_els:
                loc = url_el.find("sm:loc", ns)
                if loc is None:
                    loc = url_el.find("loc")
                if loc is not None and loc.text:
                    u = self._normalize_url(loc.text.strip())
                    if self._is_internal(u):
                        urls.add(u)

        except ET.ParseError:
            # Fallback: BeautifulSoup XML parser
            try:
                soup = BeautifulSoup(resp.text, "lxml-xml")
                sitemaps = soup.find_all("sitemap")
                if sitemaps:
                    for sm in sitemaps:
                        loc = sm.find("loc")
                        if loc:
                            sub_urls = self._fetch_sitemap_urls(loc.text.strip(), depth + 1)
                            urls.update(sub_urls)
                else:
                    for url_el in soup.find_all("url"):
                        loc = url_el.find("loc")
                        if loc:
                            u = self._normalize_url(loc.text.strip())
                            if self._is_internal(u):
                                urls.add(u)
            except Exception:
                pass
        except Exception:
            pass

        return urls

    def _discover_phase(self):
        """Phase 1: Find every page using sitemaps + sidebar crawling."""
        self.emit("highlight", "🔍 PHASE 1: Discovering all pages…")
        found = set()

        # ── 1. Try sitemaps ──
        sitemap_candidates = [
            urljoin(self.start_url, "/sitemap.xml"),
            urljoin(self.start_url, "/sitemap-index.xml"),
            self.start_url + "/sitemap.xml",
        ]

        for sm_url in sitemap_candidates:
            if self._stop.is_set():
                break
            sm_urls = self._fetch_sitemap_urls(sm_url)
            if sm_urls:
                found.update(sm_urls)
                self.emit("success", f"  ✓ Sitemap: {sm_url} → {len(sm_urls)} URLs (total: {len(found)})")
                break

        if found:
            self.emit("info", f"  Sitemap provided {len(found)} canonical URLs")
        else:
            self.emit("info", "  No sitemap found — crawling sidebar for links")

        # ── 2. Crawl sidebar/nav for additional links ──
        pages_for_nav = deque([self.start_url])
        crawled_for_nav = set()
        no_new_streak = 0

        while pages_for_nav and not self._stop.is_set():
            page_url = pages_for_nav.popleft()
            norm = self._normalize_url(page_url)
            if norm in crawled_for_nav:
                continue
            if len(crawled_for_nav) >= 200:
                break

            try:
                resp = self._get_session().get(page_url, timeout=15)
                if resp.status_code != 200:
                    continue
                crawled_for_nav.add(norm)
                soup = BeautifulSoup(resp.text, "html.parser")

                new_links = set()
                # Primary: nav elements (GitBook sidebar TOC)
                for nav in soup.find_all("nav"):
                    for a in nav.find_all("a", href=True):
                        full = self._normalize_url(urljoin(page_url, a["href"]))
                        if self._is_internal(full):
                            new_links.add(full)

                # Secondary: all internal links on the page
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    if href.startswith(("#", "javascript:", "mailto:", "tel:")):
                        continue
                    full = self._normalize_url(urljoin(page_url, href))
                    if self._is_internal(full):
                        new_links.add(full)

                truly_new = new_links - found
                found.update(new_links)
                self.stats["discovered"] = len(found)

                if truly_new:
                    no_new_streak = 0
                    self.emit("info", f"  +{len(truly_new)} links from {page_url} (total: {len(found)})")
                    for link in list(truly_new)[:30]:
                        if link not in crawled_for_nav and link not in pages_for_nav:
                            pages_for_nav.append(link)
                else:
                    no_new_streak += 1
                    if no_new_streak >= 5:
                        self.emit("info", "  No new links in last 5 pages — discovery saturated")
                        break

            except Exception as e:
                self.emit("error", f"  Discovery error: {page_url} — {e}")

        self.stats["discovered"] = len(found)
        self.emit("highlight", f"✓ Discovery complete: {len(found)} unique pages found")
        return found

    # ── PHASE 2: DOWNLOAD ONE PAGE ───────────────────────────
    def _download_one(self, url, retries_left=MAX_RETRIES):
        """Download + convert to markdown. Returns (url, title, md, error, size_kb)."""
        for attempt in range(retries_left + 1):
            if self._stop.is_set():
                return (url, None, None, "Stopped", 0)

            try:
                resp = self._get_session().get(url, timeout=20)
                if resp.status_code == 429:
                    wait = 15 * (attempt + 1)
                    time.sleep(wait)
                    continue
                if resp.status_code in (403, 401):
                    return (url, None, None, f"HTTP {resp.status_code}", 0)
                if resp.status_code == 404:
                    return (url, None, None, "404", 0)
                if resp.status_code >= 500:
                    if attempt < retries_left:
                        time.sleep(self.RETRY_DELAY[min(attempt, len(self.RETRY_DELAY) - 1)])
                        continue
                    return (url, None, None, f"HTTP {resp.status_code}", 0)
                if resp.status_code != 200:
                    return (url, None, None, f"HTTP {resp.status_code}", 0)

                soup = BeautifulSoup(resp.text, "html.parser")
                title_el = soup.find("h1")
                title = title_el.get_text().strip() if title_el else url.rstrip("/").split("/")[-1] or "Home"

                for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
                    tag.decompose()

                main = soup.find("main") or soup.find("article") or soup.find("div", class_="content") or soup.body
                html = str(main) if main else resp.text
                markdown = md(html, heading_style="ATX")
                markdown = re.sub(r"\n\s*\n\s*\n+", "\n\n", markdown)

                size_kb = round(len(markdown.encode("utf-8")) / 1024, 1)
                return (url, title, markdown, None, size_kb)

            except requests.Timeout:
                if attempt < retries_left:
                    time.sleep(self.RETRY_DELAY[min(attempt, len(self.RETRY_DELAY) - 1)])
                    continue
                return (url, None, None, "Timeout", 0)
            except requests.ConnectionError:
                if attempt < retries_left:
                    time.sleep(self.RETRY_DELAY[min(attempt, len(self.RETRY_DELAY) - 1)] * 2)
                    continue
                return (url, None, None, "Connection failed", 0)
            except Exception as e:
                if attempt < retries_left:
                    time.sleep(self.RETRY_DELAY[min(attempt, len(self.RETRY_DELAY) - 1)])
                    continue
                return (url, None, None, str(e)[:60], 0)

    # ── PHASE 2: DOWNLOAD ALL PAGES ─────────────────────────
    def _download_phase(self, urls):
        url_list = sorted(urls)
        if len(url_list) > self.max_pages:
            url_list = url_list[:self.max_pages]
            self.emit("info", f"  Clamped to {self.max_pages} pages")

        total = len(url_list)
        self.emit("highlight", f"📥 PHASE 2: Downloading {total} pages ({self.CONCURRENCY} parallel)…")
        self.stats["phase"] = "download"
        self.stats["discovered"] = total

        results = OrderedDict()
        failed = {}
        downloaded_count = 0
        in_flight = 0
        pending = deque(url_list)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.CONCURRENCY) as executor:
            futures = {}

            def fill():
                nonlocal in_flight
                while pending and in_flight < self.CONCURRENCY and not self._stop.is_set():
                    u = pending.popleft()
                    futures[executor.submit(self._download_one, u)] = u
                    in_flight += 1

            fill()
            while futures and not self._stop.is_set():
                done, _ = concurrent.futures.wait(
                    futures, timeout=0.5, return_when=concurrent.futures.FIRST_COMPLETED
                )
                for fut in done:
                    url_key = futures.pop(fut)
                    in_flight -= 1
                    try:
                        _, title, markdown, error, size_kb = fut.result()
                    except Exception as e:
                        error, title, markdown, size_kb = str(e), None, None, 0

                    if error:
                        self.stats["failed"] += 1
                        self.emit("error", f"  ✕ [{downloaded_count + 1}/{total}] {url_key} — {error}")
                        failed[url_key] = error
                    else:
                        results[url_key] = (title, markdown)
                        self.stats["downloaded"] += 1
                        ts = self.stats["downloaded"]
                        self.emit("success", f"  ✓ [{ts}/{total}] {title} ({size_kb} KB)")

                    downloaded_count += 1
                fill()

        # ── Write output ──
        self.emit("info", "  Writing output file…")
        all_md = []
        for url, (title, markdown) in results.items():
            all_md.append(f"# {title}\n\nSource: {url}\n\n{markdown}\n\n---\n\n")

        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(all_md))
            total_kb = round(sum(len(p.encode("utf-8")) for p in all_md) / 1024, 1)
            self.emit("info", f"  📄 {os.path.basename(self.output_file)}: {total_kb} KB ({round(total_kb / 1024, 1)} MB)")
        except Exception as e:
            self.emit("error", f"Write error: {e}")

        return results, failed

    # ── Main runner ──────────────────────────────────────────
    def run(self):
        t0 = time.time()
        try:
            urls = self._discover_phase()
            if self._stop.is_set():
                self.emit("error", "Cancelled")
                self.done.set()
                return

            if not urls:
                self.emit("error", "No pages discovered — check URL")
                self.done.set()
                return

            results, failed = self._download_phase(urls)
            elapsed = round(time.time() - t0, 1)
            self.stats["elapsed"] = elapsed

            self.emit("highlight", f"\n{'═' * 60}")
            self.emit("highlight", "  DOWNLOAD COMPLETE")
            self.emit("highlight", f"  ✓ Downloaded:  {len(results)} pages")
            self.emit("highlight", f"  ✕ Failed:      {len(failed)} pages")
            self.emit("highlight", f"  ⏱  Time:        {timedelta(seconds=int(elapsed))}")
            self.emit("highlight", f"  📄 Output:      {os.path.basename(self.output_file)}")
            self.emit("highlight", f"{'═' * 60}")

            if failed:
                fail_path = self.output_file.replace(".md", "_failed.json")
                try:
                    with open(fail_path, "w") as f:
                        json.dump(dict(failed), f, indent=2)
                    self.emit("info", f"  Failed URLs saved to: {os.path.basename(fail_path)}")
                except Exception:
                    pass

        except Exception as e:
            self.emit("error", f"Fatal: {e}")
        finally:
            self.done.set()

    def stop(self):
        self._stop.set()
