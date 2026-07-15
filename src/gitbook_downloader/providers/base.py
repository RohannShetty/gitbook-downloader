"""
Provider System — Abstract base class + registry for documentation site providers.

Each provider handles detection, link extraction, content extraction,
and optional URL discovery for a specific documentation platform.
"""

from abc import ABC, abstractmethod
import re
from urllib.parse import urljoin, urlparse, urlunparse


# ── URL Helpers ─────────────────────────────────────────────


def normalize_url(url: str) -> str:
    """Normalize a URL: strip fragments, trailing slash, query params, and .md suffix."""
    p = urlparse(url)
    path = p.path.rstrip("/") or "/"
    if path.endswith(".md"):
        path = path[:-3] or "/"
    return urlunparse((p.scheme, p.netloc, path, "", "", ""))


def is_md_url(url: str) -> bool:
    """Return True if the URL ends in .md."""
    return urlparse(url).path.endswith(".md")


def same_domain(url: str, base_url: str) -> bool:
    """Check if *url* is on the same domain as *base_url*."""
    return urlparse(url).netloc == urlparse(base_url).netloc


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

        Falls back to the last-registered provider (Generic) on failure.
        """
        try:
            resp = session.get(url, timeout=20)
            if resp.status_code != 200:
                return cls._providers[-1]()
            html = resp.text
        except Exception:
            return cls._providers[-1]()

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
