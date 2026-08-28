"""
Nextra provider — detection, link extraction, and content extraction
for Nextra (Next.js docs framework) documentation sites.

Nextra specifics:
  - <meta name="generator" content="Nextra..."> in <head>.
  - Class names: nextra-content, nextra-body, nextra-breadcrumb, nextra-callout.
  - Built on Next.js (__NEXT_DATA__ contains nextra metadata).
  - Sitemaps at /sitemap.xml and /llms.txt.
"""

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
class NextraProvider(Provider):
    """Provider for Nextra-powered documentation."""

    name = "nextra"
    priority = 75

    # ── Detection ───────────────────────────────────────────

    @classmethod
    def detect(cls, url: str, html: str, session) -> bool:
        """Detect a Nextra site.

        Signals:
          1. ``<meta name="generator" content="Nextra...">`` in <head>.
          2. Class names containing ``nextra-content``, ``nextra-body``, or ``nextra-``.
          3. Nextra indicators inside ``__NEXT_DATA__`` script payload.
        """
        lower_html = html.lower()
        if '<meta name="generator" content="nextra' in lower_html:
            return True
        soup = BeautifulSoup(html[:5_000], "html.parser")
        gen = soup.find("meta", attrs={"name": "generator"})
        if gen and "nextra" in gen.get("content", "").lower():
            return True
        if "nextra-content" in lower_html or "nextra-body" in lower_html or "nextra-breadcrumb" in lower_html:
            return True
        if "nextra" in lower_html and "__next_data__" in lower_html:
            return True
        return False

    # ── URL discovery ───────────────────────────────────────

    def discover_urls(self, base_url: str, session) -> set[str]:
        """Discover pages from /sitemap.xml or /llms.txt."""
        base = base_url.rstrip("/")
        urls: set[str] = set()

        from ..utils.discovery import _decode_xml, parse_sitemap_urls, same_site

        # 1. Try /sitemap.xml
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

        # 2. Try /llms.txt
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
        """Extract same-domain links from Nextra navigation and body."""
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
        """Fetch Nextra page content, trying .md probe then HTML."""
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
        """Convert Nextra HTML to clean markdown."""
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
            tag.decompose()

        # Remove Nextra breadcrumb / search / edit links
        for el in soup.find_all(class_=lambda c: c and any(x in c for x in ["nextra-breadcrumb", "nextra-nav", "nextra-toc"])):
            el.decompose()

        main = (
            soup.find("article", class_=lambda c: c and "nextra-content" in c)
            or soup.find("div", class_=lambda c: c and "nextra-content" in c)
            or soup.find("main", class_=lambda c: c and "nextra-content" in c)
            or soup.find("article", class_=lambda c: c and "nextra-body" in c)
            or soup.find("div", class_=lambda c: c and "nextra-body" in c)
            or soup.find("article")
            or soup.find("main")
            or soup.body
        )
        body = str(main) if main else html
        markdown = md(body, heading_style="ATX")
        return NextraProvider._clean_markdown(markdown)

    @staticmethod
    def _clean_markdown(text: str) -> str:
        """Normalise whitespace."""
        text = re.sub(r"\s*\[(?:#|¶)\]\([^)]*\)", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
