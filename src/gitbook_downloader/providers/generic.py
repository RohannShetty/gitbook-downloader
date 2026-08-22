"""
Generic fallback provider — handles any documentation site that doesn't
match a specific provider.

This provider always returns True from detect(), so it sits at the bottom
of the priority list as a catch-all.
"""

import re
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

from bs4 import BeautifulSoup
from markdownify import markdownify as md

from .base import Provider, ProviderRegistry, normalize_url, same_domain, decode_response


@ProviderRegistry.register
class GenericProvider(Provider):
    """Catch-all provider for any documentation site."""

    name = "generic"
    priority = 0  # Lowest — only used when nothing else matches

    # ── Detection ───────────────────────────────────────────

    @classmethod
    def detect(cls, url: str, html: str, session) -> bool:
        """Always returns True — this is the catch-all fallback."""
        return True

    # ── URL discovery ───────────────────────────────────────

    def discover_urls(self, base_url: str, session) -> set[str]:
        """Try sitemap.xml walking up path hierarchy, then llms.txt, then return empty (triggers BFS)."""
        urls: set[str] = set()
        parsed_base = urlparse(base_url)

        # Walk up the path hierarchy looking for sitemap.xml
        path = parsed_base.path.rstrip("/")
        parts = [p for p in path.split("/") if p]
        for i in range(len(parts), -1, -1):
            sub = "/".join(parts[:i])
            sitemap_base = f"{parsed_base.scheme}://{parsed_base.netloc}" + (f"/{sub}" if sub else "")
            sitemap_url = sitemap_base + "/sitemap.xml"
            try:
                resp = session.get(sitemap_url, timeout=30)
                if resp.status_code == 200:
                    from ..utils.discovery import _decode_xml, parse_sitemap_urls, same_site
                    pages, _subs = parse_sitemap_urls(_decode_xml(resp))
                    for u in pages:
                        if same_site(u, base_url):
                            urls.add(normalize_url(u.strip()))
                    if urls:
                        return urls
            except Exception:
                pass

        # Try llms.txt
        llms_url = base_url.rstrip("/") + "/llms.txt"
        try:
            resp = session.get(llms_url, timeout=30)
            if resp.status_code == 200:
                from ..utils.discovery import same_site
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
        """Extract all same-domain ``<a href>`` links from HTML."""
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
        """Fetch page and extract markdown using standard content selectors.

        Selector chain:
          ``<main>`` → ``<article>`` → ``div.md-content`` → ``div.rst-content``
          → ``div.content`` → ``<body>``
        """
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
        """Convert generic documentation HTML to markdown."""
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
            tag.decompose()

        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_=lambda c: c and "md-content" in c)
            or soup.find("div", class_=lambda c: c and "rst-content" in c)
            or soup.find("div", class_="content")
            or soup.body
        )
        body = str(main) if main else html
        markdown = md(body, heading_style="ATX")

        # Strip common permalink anchors (¶)
        markdown = re.sub(r" ¶\n", "\n", markdown)
        # Normalise whitespace
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)
        return markdown.strip()
