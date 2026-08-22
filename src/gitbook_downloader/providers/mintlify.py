"""Mintlify provider — detection, link extraction, and content extraction
for Mintlify-powered documentation sites.

Mintlify specifics:
- /llms.txt available for URL discovery (like GitBook).
- .md export available (like GitBook).
- Detected via "mintlify" in window.__MINTLIFY or meta generator tag.
"""

import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from markdownify import markdownify as md

from .base import Provider, ProviderRegistry, normalize_url, same_domain, decode_response, looks_like_html, content_probe_url


@ProviderRegistry.register
class MintlifyProvider(Provider):
    """Provider for Mintlify-powered documentation."""

    name = "mintlify"
    priority = 90

    # ── Detection ───────────────────────────────────────────

    @classmethod
    def detect(cls, url: str, html: str, session) -> bool:
        """Detect a Mintlify site.

        Signals (strict):
          1. ``window.__MINTLIFY`` present in JavaScript.
          2. ``<meta name="generator" content="...Mintlify...">`` tag.

        A prose mention of "mintlify" is deliberately NOT a signal.
        """
        lower_html = html.lower()
        if "window.__mintlify" in lower_html:
            return True
        soup = BeautifulSoup(html[:3_000], "html.parser")
        gen = soup.find("meta", attrs={"name": "generator"})
        if gen and "mintlify" in gen.get("content", "").lower():
            return True
        return False

    # ── URL discovery ───────────────────────────────────────

    def discover_urls(self, base_url: str, session) -> set[str]:
        """Discover pages from /llms.txt (preferred) or /sitemap.xml."""
        base = base_url.rstrip("/")
        urls: set[str] = set()

        from ..utils.discovery import _decode_xml, parse_sitemap_urls, same_site

        # Try /llms.txt first (Mintlify supports it like GitBook)
        try:
            resp = session.get(f"{base}/llms.txt", timeout=30)
            if resp.status_code == 200:
                for match in re.finditer(r"\]\((https?://[^)]+)\)", decode_response(resp)):
                    u = match.group(1)
                    if same_site(u, base_url):
                        urls.add(normalize_url(u))
                if urls:
                    return urls
        except Exception:
            pass

        # Fallback to sitemap — pages only, same-site only.
        try:
            resp = session.get(f"{base}/sitemap.xml", timeout=30)
            if resp.status_code == 200:
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
        """Extract same-domain links from Mintlify HTML."""
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
        """Fetch page content, preferring .md export over HTML→markdown.

        1. Try ``<url>.md``.
        2. Fallback to HTML fetch + ``<article>`` / ``<main>`` extraction.
        """
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
        """Convert Mintlify HTML to markdown."""
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
            tag.decompose()

        main = (
            soup.find("article")
            or soup.find("main")
            or soup.find("div", class_=lambda c: c and "content" in c)
            or soup.body
        )
        body = str(main) if main else html
        markdown = md(body, heading_style="ATX")
        return MintlifyProvider._clean_markdown(markdown)

    @staticmethod
    def _clean_markdown(text: str) -> str:
        """Normalise whitespace and strip excessive blank lines."""
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
