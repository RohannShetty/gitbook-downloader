"""
ReadTheDocs provider — detection, link extraction, and content extraction
for ReadTheDocs / Sphinx-powered documentation sites.

RTD specifics:
  - Body class or div classes containing ``readthedocs``.
  - docutils-generated HTML with sidebar ``div.sphinxsidebar``.
  - Always generates ``/sitemap.xml``.
  - Breadcrumbs + "Read the Docs" footer text.
"""

import re
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

from bs4 import BeautifulSoup
from markdownify import markdownify as md

from .base import Provider, ProviderRegistry, normalize_url, same_domain


@ProviderRegistry.register
class ReadTheDocsProvider(Provider):
    """Provider for ReadTheDocs / Sphinx-powered documentation."""

    name = "readthedocs"
    priority = 70

    # ── Detection ───────────────────────────────────────────

    @classmethod
    def detect(cls, url: str, html: str, session) -> bool:
        """Detect a ReadTheDocs site.

        Signals:
          1. ``readthedocs`` in body / div class names.
          2. docutils CSS classes (``document``, ``section``).
          3. Footer text "Read the Docs".
        """
        lower_html = html.lower()
        if "readthedocs" in lower_html:
            return True
        # Sphinx/docutils hallmarks
        if 'class="document' in lower_html or "sphinxsidebar" in lower_html:
            return True
        if '<div class="body"' in lower_html or 'role="main"' in lower_html:
            # Could be Sphinx — check for RTD footer
            if "read the docs" in lower_html:
                return True
        return False

    # ── URL discovery ───────────────────────────────────────

    def discover_urls(self, base_url: str, session) -> set[str]:
        """Discover pages from the ReadTheDocs ``/sitemap.xml``."""
        urls: set[str] = set()
        sitemap_url = base_url.rstrip("/") + "/sitemap.xml"
        try:
            resp = session.get(sitemap_url, timeout=30)
            if resp.status_code != 200:
                return urls
            root = ElementTree.fromstring(resp.content)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            for loc in root.findall(".//sm:loc", ns):
                if loc.text:
                    urls.add(normalize_url(loc.text.strip()))
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
        """Extract same-domain links, including from the Sphinx sidebar."""
        soup = BeautifulSoup(html, "html.parser")
        base_domain = urlparse(url).netloc
        links: set[str] = set()

        # Scan sidebar first — it's the primary navigation on RTD
        sidebar = soup.find("div", class_="sphinxsidebar")
        scan_roots = [sidebar, soup] if sidebar else [soup]

        for root in scan_roots:
            if root is None:
                continue
            for a in root.find_all("a", href=True):
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
        """Fetch page content from ReadTheDocs.

        Extracts the main document area (``div.document`` or ``div.body``),
        strips breadcrumbs, RTD footer, permalink anchors, and docutils
        boilerplate, then converts to markdown.
        """
        try:
            resp = session.get(url, timeout=20)
            if resp.status_code != 200:
                return ""
            html = resp.text
        except Exception:
            return ""

        return self._extract_md_from_html(html)

    # ── Internal helpers ────────────────────────────────────

    @staticmethod
    def _extract_md_from_html(html: str) -> str:
        """Convert RTD/Sphinx HTML to clean markdown."""
        soup = BeautifulSoup(html, "html.parser")

        # Remove unwanted elements
        for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
            tag.decompose()

        # Remove RTD header bar
        for div in soup.find_all("div", class_=lambda c: c and "header" in c):
            div.decompose()

        # Remove sidebar
        for div in soup.find_all("div", class_="sphinxsidebar"):
            div.decompose()

        # Remove breadcrumbs
        for div in soup.find_all("div", class_=lambda c: c and "breadcrumb" in c.lower()):
            div.decompose()

        # Remove RTD footer
        for div in soup.find_all("div", class_=lambda c: c and "rst-footer" in c.lower()):
            div.decompose()
        for footer in soup.find_all("footer"):
            footer.decompose()

        # Find main content
        main = (
            soup.find("div", class_="document")
            or soup.find("div", class_="body")
            or soup.find("div", class_=lambda c: c and "section" in c.lower())
            or soup.find("main")
            or soup.body
        )
        body = str(main) if main else html
        markdown = md(body, heading_style="ATX")

        # Strip Sphinx permalink anchors (¶)
        markdown = re.sub(r" ¶\n", "\n", markdown)
        # Normalise whitespace
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)
        return markdown.strip()
