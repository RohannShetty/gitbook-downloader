"""
Provider System — Abstract base class + registry for documentation site providers.

Each provider handles detection, link extraction, content extraction,
and optional URL discovery for a specific documentation platform.
"""

from abc import ABC, abstractmethod
import re
from urllib.parse import urljoin, urlparse, urlunparse, urldefrag


# ── URL Helpers ─────────────────────────────────────────────


def normalize_url(url: str) -> str:
    """Canonical dedup key for page URLs.

    Strips the fragment, collapses consecutive path slashes, removes the
    trailing slash and any ``.md`` suffix. The query string is KEPT so that
    distinct pages like ``/docs/api?page=2`` do not collapse into one
    (audit Critical #10). This is the single source of truth;
    ``utils.discovery.normalize_url`` delegates here.
    """
    url, _ = urldefrag(url)
    p = urlparse(url)
    path = re.sub(r"/+", "/", p.path)
    path = path.rstrip("/") or "/"
    if path.endswith(".md"):
        path = path[:-3] or "/"
    return urlunparse((p.scheme, p.netloc, path, p.query, "", ""))


def content_probe_url(url: str) -> str:
    """Path-only form of *url* for ``<url>.md`` content probes.

    Query strings are part of page identity but not of the content export
    path, so probes must never carry them.
    """
    p = urlparse(normalize_url(url))
    return urlunparse((p.scheme, p.netloc, p.path, "", "", ""))


def is_md_url(url: str) -> bool:
    """Return True if the URL ends in .md."""
    return urlparse(url).path.endswith(".md")


def same_domain(url: str, base_url: str) -> bool:
    """Check if *url* is on the same domain as *base_url*."""
    return urlparse(url).netloc == urlparse(base_url).netloc


# ── Response decoding ───────────────────────────────────────


_WEAK_ENCODINGS = {"", "iso-8859-1", "latin-1", "ascii", "us-ascii"}


def decode_response(resp) -> str:
    """Return the response body as text, correcting missing/mislabeled charsets.

    ``requests`` defaults ``text/*`` responses without a ``charset`` parameter
    to ISO-8859-1, so UTF-8 bodies become mojibake. When the declared encoding
    is one of those weak defaults, re-decode using ``apparent_encoding``
    (content sniffing) instead.
    """
    declared = (getattr(resp, "encoding", None) or "").lower()
    if declared in _WEAK_ENCODINGS:
        apparent = getattr(resp, "apparent_encoding", None)
        if apparent:
            resp.encoding = apparent
    return resp.text


# ── Soft-200 sniffing ───────────────────────────────────────

_HTML_SNIFF_MARKERS = ("<html", "<head", "<body", "<div", "<script", "<meta ", "<iframe")


def looks_like_html(text: str, content_type: str = "") -> bool:
    """Heuristic: does this ``.md`` payload actually contain HTML?

    Some SPA hosts answer ``<url>.md`` with a 200 and their HTML shell
    instead of markdown or a 404. Structural sniffing catches shells that
    skip the doctype.
    """
    if not text:
        return False
    if content_type and "text/html" in content_type.lower():
        return True
    head = text.lstrip()[:1000].lower()
    if head.startswith(("<!doctype html", "<html")):
        return True
    hits = sum(1 for marker in _HTML_SNIFF_MARKERS if marker in head)
    return hits >= 3


# ── Abstract Provider ───────────────────────────────────────


class Provider(ABC):
    """Abstract base for documentation site providers."""

    name: str = ""
    priority: int = 0  # Higher = tried first during auto-detect

    # ── Detection ───────────────────────────────────────────

    @classmethod
    @abstractmethod
    def detect(cls, url: str, html: str, session) -> bool:
        """Detect if this provider handles the given site.

        Args:
            url:   The page URL.
            html:  The fetched HTML of that page.
            session: A ``requests.Session`` for any follow-up fetches.
        """
        ...

    # ── Link extraction ─────────────────────────────────────

    @abstractmethod
    def extract_links(
        self,
        url: str,
        html: str,
        path_scope: str | None = None,
        exclude_paths: list[str] | None = None,
    ) -> set[str]:
        """Extract same-domain links for crawling / discovery.

        Args:
            url:           Page URL (used to resolve relative links).
            html:          HTML content of the page.
            path_scope:    Only keep links whose path starts with this prefix.
            exclude_paths: Skip links whose path contains any of these substrings.

        Returns:
            Set of absolute, same-domain URLs.
        """
        ...

    # ── Content extraction ──────────────────────────────────

    @abstractmethod
    def extract_content(self, url: str, session) -> str:
        """Fetch and extract clean markdown content from a URL.

        Args:
            url:     The page URL.
            session: A ``requests.Session`` to use for fetching.

        Returns:
            Clean markdown text, or ``""`` on failure.
        """
        ...

    # ── Optional overrides ──────────────────────────────────

    def discover_urls(self, base_url: str, session) -> set[str]:
        """Discover all URLs without BFS-crawling (llms.txt, sitemap, etc.).

        Returns empty set by default — engine falls back to BFS.
        """
        return set()

    def extract_title(self, content: str, url: str) -> str:
        """Extract a human-readable title from markdown content or URL."""
        m = re.search(r"^# (.+)", content, re.MULTILINE)
        if m:
            return m.group(1).strip()
        return url.rstrip("/").split("/")[-1] or "Home"


# ── Registry ────────────────────────────────────────────────


class ProviderRegistry:
    """Registry for auto-detecting and retrieving providers by name."""

    _providers: list[type[Provider]] = []

    @classmethod
    def register(cls, provider_cls: type[Provider]):
        """Register a provider class (keeps list sorted by priority descending)."""
        cls._providers.append(provider_cls)
        cls._providers.sort(key=lambda p: p.priority, reverse=True)
        return provider_cls

    @classmethod
    def detect(cls, url: str, session) -> Provider:
        """Fetch *url*, try each registered provider, return first match.

        On root-fetch failure every provider still gets a chance to decide
        from its own signals before the Generic fallback wins.
        """
        html = ""
        try:
            resp = session.get(url, timeout=20)
            if resp.status_code == 200:
                html = decode_response(resp)
        except Exception:
            html = ""

        for p_cls in cls._providers:
            try:
                if p_cls.detect(url, html, session):
                    return p_cls()
            except Exception:
                continue
        return cls._providers[-1]()  # Generic fallback

    @classmethod
    def get_by_name(cls, name: str) -> type[Provider]:
        """Look up a provider class by its ``name`` attribute."""
        for p_cls in cls._providers:
            if p_cls.name.lower() == name.lower():
                return p_cls
        raise ValueError(f"Unknown provider: {name}")

    @classmethod
    def list_names(cls) -> list[str]:
        """Return provider names in priority order."""
        return [p.name for p in cls._providers]
