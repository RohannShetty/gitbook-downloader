"""URL discovery helpers for GitBook Downloader v6.

Provides methods to discover documentation URLs from *llms.txt* files and
*sitemap.xml* files, plus normalisation and classification utilities.
"""

import logging
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin, urldefrag
from urllib.parse import urlsplit, urlunsplit

import requests

from .retry import retry_get

logger = logging.getLogger(__name__)

# ── URL normalisation ──

def normalize_url(url: str) -> str:
    """Normalise a URL for deduplication.

    Strips the fragment, trailing slash, ``.md`` suffix, and collapses
    consecutive slashes so that ``/docs/intro/#section`` and
    ``/docs/intro`` resolve to the same key.

    Args:
        url: A raw URL string.

    Returns:
        Normalised URL string.
    """
    url, _ = urldefrag(url)             # remove fragment
    parsed = urlparse(url)
    # Collapse consecutive slashes in the path (e.g. //a → /a)
    import re as _re
    path = _re.sub(r'/+', '/', parsed.path)
    path = path.rstrip("/")             # strip trailing slash
    if path.endswith(".md"):
        path = path[:-3]                # strip .md suffix
    return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, ""))


def is_md_url(url: str) -> bool:
    """Return ``True`` if the URL path ends in ``.md`` (case-insensitive).

    Args:
        url: A URL string.

    Returns:
        Whether the URL points to a Markdown resource.
    """
    path = urlparse(url).path.lower()
    return path.endswith(".md")


def _same_domain(url: str, base_url: str) -> bool:
    """Return True if *url* shares the scheme+host of *base_url*."""
    base = urlparse(base_url)
    target = urlparse(url)
    return (target.scheme, target.netloc) == (base.scheme, base.netloc)


def _normalise_relative(href: str, base_url: str) -> str:
    """Resolve a relative href against *base_url*, then normalise."""
    absolute = urljoin(base_url, href)
    return normalize_url(absolute)


# ── llms.txt discovery ──

def discover_from_llms_txt(base_url: str, session: requests.Session) -> set[str]:
    """Discover page URLs from a site's ``/llms.txt`` file.

    The function fetches ``<base_url>/llms.txt``, extracts every
    Markdown-style link ``[text](url)``, keeps only same-domain URLs,
    and returns them as a normalised set.

    Args:
        base_url: Root URL of the documentation site
                  (e.g. ``https://docs.example.com``).
        session:  A ``requests.Session`` (with retry support recommended).

    Returns:
        A set of normalised absolute URL strings.
    """
    base_url = base_url.rstrip("/")
    llms_url = f"{base_url}/llms.txt"
    logger.info("Fetching llms.txt from %s", llms_url)

    resp, err = retry_get(session, llms_url)
    if err or resp is None:
        logger.debug("llms.txt not available: %s", err or "no response")
        return set()
    if resp.status_code != 200:
        logger.debug("llms.txt returned %d", resp.status_code)
        return set()

    text = resp.text
    # Extract markdown links: [text](https://...)
    raw_links = re.findall(r'\]\((https?://[^)]+)\)', text)
    # Also catch plain bare URLs on their own lines (common in llms.txt)
    bare_links = re.findall(r'(?:^|\s)(https?://\S+)', text, re.MULTILINE)

    all_links = set(raw_links) | set(bare_links)

    urls: set[str] = set()
    for href in all_links:
        href = href.strip()
        if not _same_domain(href, base_url):
            continue
        urls.add(normalize_url(href))

    logger.info("Discovered %d URLs from llms.txt", len(urls))
    return urls


# ── Sitemap discovery ──

_SITEMAP_NS = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def _fetch_sitemap_xml(base_url: str, session: requests.Session) -> str | None:
    """Try to fetch /sitemap.xml, falling back to /sitemap.xml.gz."""
    for suffix in ("", ".gz"):
        url = f"{base_url}/sitemap{suffix}"
        resp, err = retry_get(session, url)
        if err or resp is None or resp.status_code != 200:
            continue
        # If gzipped, requests usually decompresses via Accept-Encoding.
        # If the raw bytes still look like gzip, try to decode.
        content = resp.text
        if content.startswith("<?xml") or "<urlset" in content or "<sitemapindex" in content:
            return content
    return None


def _parse_sitemap_urls(xml_text: str) -> set[str]:
    """Parse <loc> entries from a sitemap XML document."""
    urls: set[str] = set()
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        logger.debug("Sitemap XML parse error: %s", exc)
        return urls

    # Handle sitemap index (list of sub-sitemaps)
    for sitemap in root.findall("ns:sitemap", _SITEMAP_NS):
        loc = sitemap.find("ns:loc", _SITEMAP_NS)
        if loc is not None and loc.text:
            urls.add(loc.text.strip())

    # Handle normal urlset
    for url_elem in root.findall("ns:url", _SITEMAP_NS):
        loc = url_elem.find("ns:loc", _SITEMAP_NS)
        if loc is not None and loc.text:
            urls.add(loc.text.strip())

    return urls


def discover_from_sitemap(base_url: str, session: requests.Session) -> set[str]:
    """Discover page URLs from a site's ``/sitemap.xml``.

    Fetches the sitemap (with ``.gz`` fallback), parses all ``<loc>``
    entries, handles sitemap index files by recursively fetching
    sub-sitemaps, and returns normalised same-domain URLs.

    Args:
        base_url: Root URL of the documentation site.
        session:  A ``requests.Session``.

    Returns:
        A set of normalised absolute URL strings.
    """
    base_url = base_url.rstrip("/")
    logger.info("Fetching sitemap from %s", base_url)

    xml_text = _fetch_sitemap_xml(base_url, session)
    if xml_text is None:
        logger.debug("No sitemap found for %s", base_url)
        return set()

    raw_urls = _parse_sitemap_urls(xml_text)

    # If the sitemap was an index (contains sub-sitemap URLs), fetch them.
    sub_urls: set[str] = set()
    for candidate in raw_urls:
        parsed = urlparse(candidate)
        if parsed.path.lower().endswith(".xml") or parsed.path.lower().endswith(".xml.gz"):
            # Treat as sub-sitemap reference
            resp, err = retry_get(session, candidate)
            if not err and resp is not None and resp.status_code == 200:
                sub_urls |= _parse_sitemap_urls(resp.text)

    all_raw = raw_urls | sub_urls

    # Filter to same-domain and normalise
    urls: set[str] = set()
    for url in all_raw:
        url = url.strip()
        if not _same_domain(url, base_url):
            continue
        urls.add(normalize_url(url))

    logger.info("Discovered %d URLs from sitemap", len(urls))
    return urls
