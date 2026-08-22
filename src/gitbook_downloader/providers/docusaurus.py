"""
Docusaurus provider — detection, link extraction, and content extraction
for Docusaurus-powered documentation sites.

Docusaurus specifics:
  - <meta name="docusaurus"> tag in <head>.
  - CSS class ``theme-doc-markdown`` on content wrapper.
  - Always generates ``/sitemap.xml``.
  - Permalink anchors with ``¶`` character.
"""

import re
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

from bs4 import BeautifulSoup
from markdownify import markdownify as md

from .base import Provider, ProviderRegistry, normalize_url, same_domain, decode_response, looks_like_html, content_probe_url


@ProviderRegistry.register
class DocusaurusProvider(Provider):
    """Provider for Docusaurus-powered documentation."""

    name = "docusaurus"
    priority = 80

    # ── Detection ───────────────────────────────────────────

    @classmethod
    def detect(cls, url: str, html: str, session) -> bool:
        """Detect a Docusaurus site.

        Signals:
          1. ``<meta name="docusaurus">`` in <head>.
          2. CSS class ``theme-doc-markdown`` somewhere in the HTML.
          3. ``docusaurus-theme-`` substring in any class or attribute.
        """
        lower_html = html.lower()
        if '<meta name="docusaurus"' in lower_html:
            return True
        if "theme-doc-markdown" in lower_html:
            return True
        if "docusaurus-theme-" in lower_html:
            return True
        return False

    # ── URL discovery ───────────────────────────────────────

    def discover_urls(self, base_url: str, session) -> set[str]:
        """Discover pages from the Docusaurus ``/sitemap.xml``."""
        from ..utils.discovery import _decode_xml, parse_sitemap_urls, same_site

        urls: set[str] = set()
        sitemap_url = base_url.rstrip("/") + "/sitemap.xml"
        try:
            resp = session.get(sitemap_url, timeout=30)
            if resp.status_code != 200:
                return urls
            pages, _subs = parse_sitemap_urls(_decode_xml(resp))
            for u in pages:
                if same_site(u, base_url):
                    urls.add(normalize_url(u.strip()))
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
        """Extract same-domain links.

        Also scans the sidebar ``<nav class="menu">`` for navigation links.
        """
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
            if path_scope and not parsed.path.startswith(path_scope):
                continue
            if exclude_paths and any(ex in parsed.path for ex in exclude_paths):
                continue
            links.add(full)

        return links

    # ── Content extraction ──────────────────────────────────

    def extract_content(self, url: str, session) -> str:
        """Fetch page content.

        1. Optionally try ``<url>.md`` (works with some Docusaurus configs).
        2. Fallback to HTML: extract ``<article>`` or ``<main role="main">``,
           strip ``¶`` permalink anchors, convert to markdown.
        """
        # Try .md export
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

        # HTML → markdown
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
        """Convert Docusaurus HTML to markdown."""
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
            tag.decompose()

        main = (
            soup.find("article")
            or soup.find("main", attrs={"role": "main"})
            or soup.find("div", class_=lambda c: c and "theme-doc-markdown" in c)
            or soup.find("div", class_=lambda c: c and "markdown" in c)
            or soup.find("main")
            or soup.body
        )
        body = str(main) if main else html
        markdown = md(body, heading_style="ATX")
        return DocusaurusProvider._clean_markdown(markdown)

    @staticmethod
    def _clean_markdown(text: str) -> str:
        """Strip ``¶`` permalink anchors and normalise whitespace."""
        # Hash-link form emitted by markdownify: [¶](#anchor "title")
        text = re.sub(r"\s*\[¶\]\([^)]*\)", "", text)
        text = re.sub(r" ¶\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
