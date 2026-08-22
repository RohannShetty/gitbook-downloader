"""
Provider System — auto-detect, register, and use documentation site providers.

Usage::

    from gitbook_downloader.providers import detect_provider, get_provider, list_providers

    # Auto-detect from a URL (fetches HTML, tries providers by priority)
    provider = detect_provider("https://docs.example.com", session)

    # Use by name
    GitBook = get_provider("gitbook")

    # List available providers
    print(list_providers())  # ['gitbook', 'mintlify', 'docusaurus', 'readthedocs', 'generic']
"""

from .base import Provider, ProviderRegistry, normalize_url, is_md_url, same_domain

# Import all providers — the ``@ProviderRegistry.register`` decorator
# in each module adds them to the registry at import time.
from .gitbook import GitBookProvider
from .docusaurus import DocusaurusProvider
from .readthedocs import ReadTheDocsProvider
from .mintlify import MintlifyProvider
from .generic import GenericProvider


# ── Public API ──────────────────────────────────────────────


def detect_provider(url: str, session) -> Provider:
    """Auto-detect the best provider for *url*.

    Fetches the page HTML, then tries each registered provider
    in priority order.  Falls back to :class:`GenericProvider`.
    """
    return ProviderRegistry.detect(url, session)


def get_provider(name: str) -> type[Provider]:
    """Look up a provider class by name (case-insensitive).

    Raises ``ValueError`` if not found.
    """
    return ProviderRegistry.get_by_name(name)


def list_providers() -> list[str]:
    """Return registered provider names in priority order."""
    return ProviderRegistry.list_names()


__all__ = [
    # Base
    "Provider",
    "ProviderRegistry",
    "normalize_url",
    "is_md_url",
    "same_domain",
    # Providers
    "GitBookProvider",
    "DocusaurusProvider",
    "ReadTheDocsProvider",
    "MintlifyProvider",
    "GenericProvider",
    # Convenience
    "detect_provider",
    "get_provider",
    "list_providers",
]
