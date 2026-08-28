"""
MkDocs provider — detection, link extraction, and content extraction
for MkDocs and Material for MkDocs documentation sites.

MkDocs specifics:
  - <meta name="generator" content="mkdocs..."> tag in <head>.
  - Material for MkDocs attributes (data-md-color-primary, md-container, md-content).
  - Search index available at /search/search_index.json.
  - Sitemaps at /sitemap.xml.
"""

import json
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from markdownify import markdownify as md

from .base import (
    Provider,
    ProviderRegistry,
    content_probe_url,
    decode_response,
    is_md_url,
    looks_like_html,
    normalize_url,
    same_domain,
)


@ProviderRegistry.register
class MkDocsProvider(Provider):
    """Provider for MkDocs and Material for MkDocs documentation."""

    name = "mkdocs"
    priority = 70

    # ── Detection ───────────────────────────────────────────

    @classmethod
    def detect(cls, url: str, html: str, session) -> bool:
        """Detect an MkDocs site.

        Signals:
          1. ``<meta name="generator" content="mkdocs...">`` in <head>.
          2. Material for MkDocs markers: ``data-md-component``, ``md-content``,
             ``data-md-color-primary``, ``md-main``.
          3. Reference to ``search/search_index.json`` in script tags or assets.
        """
        lower_html = html.lower()
        if '<meta name="generator" content="mkdocs' in lower_html or '<meta name="generator" content="material for mkdocs' in lower_html:
            return True
        soup = BeautifulSoup(html[:5_000], "html.parser")
        gen = soup.find("meta", attrs={"name": "generator"})
        if gen and "mkdocs" in gen.get("content", "").lower():
            return True
        if "data-md-component" in lower_html or "data-md-color-primary" in lower_html:
            return True
        if 'class="md-content' in lower_html or 'class="md-main' in lower_html:
            return True
        if "search_index.json" in lower_html:
            return True
        return False

    # ── URL discovery ───────────────────────────────────────

    def discover_urls(self, base_url: str, session) -> set[str]:
        """Discover pages from /search/search_index.json, /sitemap.xml, or /llms.txt."""
        base = base_url.rstrip("/")
        urls: set[str] = set()

        from ..utils.discovery import _decode_xml, parse_sitemap_urls, same_site

        # 1. Try search/search_index.json (MkDocs built-in index)
        try:
            resp = session.get(f"{base}/search/search_index.json", timeout=20)
            if resp.status_code == 200:
                data = json.loads(decode_response(resp))
                docs = data.get("docs", [])
                for doc in docs:
                    location = doc.get("location", "")
                    if location:
                        full = urljoin(base + "/", location)
                        # Strip hash anchor
                        full = full.split("#")[0]
                        if same_site(full, base_url):
                            urls.add(normalize_url(full))
                if urls:
                    return urls
        except Exception:
            pass

        # 2. Try sitemap.xml
        try:
            resp = session.get(f"{base}/sitemap.xml", timeout=30)
            if resp.status_code == 200:
                pages, _subs = parse_sitemap_urls(_decode_xml(resp))
                for u in pages:
                    if same_site(u, base_url):
                        urls.add(normalize_url(u.strip()))
                if urls:
                    return urls
        except Exception:
            pass

        # 3. Try llms.txt
        try:
            resp = session.get(f"{base}/llms.txt", timeout=20)
            if resp.status_code == 200:
                for match in re.finditer(r"\]\((https?://[^)]+)\)", decode_response(resp)):
                    u = match.group(1)
                    if same_site(u, base_url):
                        urls.add(normalize_url(u))
        except Exception:
            pass

        return urls

    # ── Link extraction ─────────────────────────────────────

    def extract_links(
        self,
        url: str,
        html: str,
        path_scope: str | None = None,
        exclude_paths: list[str] | None = None,
    ) -> set[str]:
        """Extract same-domain links from MkDocs navigation and body."""
        soup = BeautifulSoup(html, "html.parser")
        base_domain = urlparse(url).netloc
        links: set[str] = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith(("javascript:", "mailto:", "tel:")):
                continue
            full = urljoin(url, href)
            parsed = urlparse(full)
            if parsed.netloc != base_domain:
                continue
            if parsed.fragment and not parsed.path and not parsed.query:
                continue
            if is_md_url(full):
                continue
            if path_scope and not parsed.path.startswith(path_scope):
                continue
            if exclude_paths and any(ex in parsed.path for ex in exclude_paths):
                continue
            links.add(full)

        return links

    # ── Content extraction ──────────────────────────────────

    def extract_content(self, url: str, session) -> str:
        """Fetch MkDocs page content and extract clean markdown."""
        md_url = content_probe_url(url) + ".md"
        try:
            resp = session.get(md_url, timeout=20)
            if resp.status_code == 200:
                text = decode_response(resp)
                ctype = resp.headers.get("Content-Type", "")
                if not looks_like_html(text, ctype):
                    return self._clean_markdown(text)
        except Exception:
            pass

        # Fallback: HTML -> markdown
        try:
            resp = session.get(url, timeout=20)
            if resp.status_code != 200:
                return ""
            html = decode_response(resp)
        except Exception:
            return ""

        return self._extract_md_from_html(html)

    # ── Internal helpers ────────────────────────────────────

    @staticmethod
    def _extract_md_from_html(html: str) -> str:
        """Convert MkDocs HTML to clean markdown."""
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
            tag.decompose()

        # Remove MkDocs header & sidebar chrome
        for header in soup.find_all("header", class_=lambda c: c and "md-header" in c):
            header.decompose()
        for div in soup.find_all("div", class_=lambda c: c and "md-sidebar" in c):
            div.decompose()
        for a in soup.find_all("a", class_=lambda c: c and ("headerlink" in c or "md-content__button" in c)):
            a.decompose()

        main = (
            soup.find("article", class_=lambda c: c and "md-content__inner" in c)
            or soup.find("div", class_=lambda c: c and "md-content__inner" in c)
            or soup.find("div", class_=lambda c: c and "md-content" in c)
            or soup.find("main", class_=lambda c: c and "md-main" in c)
            or soup.find("article")
            or soup.find("main")
            or soup.body
        )
        body = str(main) if main else html
        markdown = md(body, heading_style="ATX")
        return MkDocsProvider._clean_markdown(markdown)

    @staticmethod
    def _clean_markdown(text: str) -> str:
        """Normalise whitespace and clean permalinks."""
        text = re.sub(r"\s*\[(?:¶|#|⚓)\]\([^)]*\)", "", text)
        text = re.sub(r" ¶\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
