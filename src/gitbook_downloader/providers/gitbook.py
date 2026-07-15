"""
GitBook provider — detection, link extraction, and content extraction
for GitBook-hosted documentation sites.

GitBook specifics:
  - React / Next.js front-end (HTML is sparse; .md exports are preferred).
  - Asset URLs include ``gitbook.net``.
  - Agent Instructions boilerplate appended to .md exports.
  - /llms.txt available for URL discovery.
"""

import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from markdownify import markdownify as md

from .base import Provider, ProviderRegistry, normalize_url, is_md_url, same_domain


# ── Agent Instructions boilerplate ──────────────────────────

_AGENT_BOILERPLATE = re.compile(
    r"---\s*\n# Agent Instructions\s*\n.*?(?=\n---\s*\n|\Z)",
    re.DOTALL,
)
_AGENT_BOILERPLATE_SIMPLE = re.compile(
    r"# Agent Instructions\s*\n.*?(?=\n---\s*\n|\Z)",
    re.DOTALL,
)
_LLM_REF_LINE = re.compile(
    r"^(>?\\s*For the complete documentation index, see \\[llms\\.txt\\].*)$",
    re.MULTILINE,
)


def strip_agent_boilerplate(text: str) -> str:
    """Remove GitBook Agent Instructions boilerplate from .md content."""
    text = _AGENT_BOILERPLATE.sub("", text)
    text = _AGENT_BOILERPLATE_SIMPLE.sub("", text)
    text = _LLM_REF_LINE.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ── Provider ────────────────────────────────────────────────


@ProviderRegistry.register
class GitBookProvider(Provider):
    """Provider for GitBook-hosted documentation."""

    name = "gitbook"
    priority = 100

    # ── Detection ───────────────────────────────────────────

    @classmethod
    def detect(cls, url: str, html: str, session) -> bool:
        """Detect a GitBook site.

        Signals:
          1. ``gitbook.net`` in any asset URL within the first 5 000 chars of HTML.
          2. ``window.__gitbook`` in a <script> tag.
          3. ``<meta name="generator" content="...gitbook...">`` tag.
        """
        lower_html = html[:5_000].lower()
        if "gitbook.net" in lower_html:
            return True
        if "window.__gitbook" in html:
            return True
        soup = BeautifulSoup(html[:5_000], "html.parser")
        gen = soup.find("meta", attrs={"name": "generator"})
        if gen and gen.get("content", "").lower().find("gitbook") != -1:
            return True
        return False

    # ── URL discovery ───────────────────────────────────────

    def discover_urls(self, base_url: str, session) -> set[str]:
        """Discover pages from GitBook's /llms.txt."""
        base = base_url.rstrip("/")
        llms_url = f"{base}/llms.txt"
        urls: set[str] = set()
        try:
            resp = session.get(llms_url, timeout=30)
            if resp.status_code != 200:
                return urls
            parsed_base = urlparse(base_url)
            for match in re.finditer(r"\]\((https?://[^)]+)\)", resp.text):
                u = match.group(1)
                if urlparse(u).netloc == parsed_base.netloc:
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
        """Extract same-domain links from GitBook HTML.

        Skips ``javascript:``/``mailto:``/``tel:``, ``/~gitbook`` asset paths,
        ``.md`` URLs (derived at download time), hash-only links, and honours
        ``path_scope`` / ``exclude_paths``.
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
            if parsed.path.startswith("/~gitbook"):
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
        """Fetch page content, preferring .md export over HTML→markdown.

        1. Try ``<url>.md`` — strip Agent Instructions boilerplate.
        2. Fallback to HTML fetch + ``<main>`` → ``<article>`` →
           ``div.md-content`` → ``div.content`` → ``<body>`` extraction.
        """
        md_url = url.rstrip("/") + ".md"
        try:
            resp = session.get(md_url, timeout=20)
            if resp.status_code == 200:
                text = resp.text
                # If it returned HTML (redirect), fall through
                if not text.strip().startswith("<!") and "data-dpl-id" not in text[:500]:
                    return strip_agent_boilerplate(text)
        except Exception:
            pass

        # Fallback: HTML → markdown
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
        """Convert GitBook HTML to markdown using standard content selectors."""
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
            tag.decompose()
        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_=lambda c: c and "md-content" in c)
            or soup.find("div", class_="content")
            or soup.body
        )
        body = str(main) if main else html
        markdown = md(body, heading_style="ATX")
        markdown = re.sub(r"\n\s*\n\s*\n", "\n\n", markdown)
        return markdown.strip()
