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
# Single source of truth lives in providers.base (audit Critical #10: the two
# implementations disagreed on query strings, producing split-brain dedup).

from ..providers.base import normalize_url, content_probe_url  # noqa: E402,F401

__all__ = ["normalize_url", "content_probe_url"]


def is_md_url(url: str) -> bool:
    """Return ``True`` if the URL path ends in ``.md`` (case-insensitive).

    Args:
        url: A URL string.

    Returns:
        Whether the URL points to a Markdown resource.
    """
    path = urlparse(url).path.lower()
    return path.endswith(".md")


def _host(url: str) -> str:
    """Lowercased hostname of *url*, with a leading ``www.`` stripped."""
    return urlparse(url).netloc.lower().removeprefix("www.")


def _same_domain(url: str, base_url: str) -> bool:
    """Return True if *url* lives on the same site as *base_url*.

    Scheme-insensitive and ``www``-insensitive so mirrors listed in
    llms.txt/sitemaps are not dropped wholesale.
    """
    target, base = _host(url), _host(base_url)
    return bool(target) and target == base


#: Public alias for cross-module use (providers filter <loc> entries).
same_site = _same_domain


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
_SITEMAP_CANDIDATE_PATHS = ("/sitemap.xml", "/sitemap.xml.gz")


def _decode_xml(resp) -> str:
    """Decode a sitemap response body, transparently gunzipping payloads."""
    import gzip

    content = getattr(resp, "content", None)
    if not isinstance(content, (bytes, bytearray)):
        # Non-bytes body (e.g. mocked responses) — use the decoded text.
        text = getattr(resp, "text", "") or ""
        return str(text)
    if content[:2] == b"\x1f\x8b":  # gzip magic bytes
        try:
            content = gzip.decompress(content)
        except OSError:
            return ""
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return content.decode("latin-1", errors="replace")


def _fetch_sitemap_xml(base_url: str, session: requests.Session) -> str | None:
    """Try ``/sitemap.xml``, falling back to ``/sitemap.xml.gz``."""
    base_url = base_url.rstrip("/")
    for path in _SITEMAP_CANDIDATE_PATHS:
        resp, err = retry_get(session, f"{base_url}{path}")
        if err or resp is None or resp.status_code != 200:
            continue
        text = _decode_xml(resp)
        stripped = text.lstrip()
        if (
            stripped.startswith("<?xml")
            or "<urlset" in text
            or "<sitemapindex" in text
        ):
            return text
    return None


def _local_tag(elem) -> str:
    """Element tag without any XML namespace prefix."""
    return elem.tag.rsplit("}", 1)[-1].lower() if isinstance(elem.tag, str) else ""


def parse_sitemap_urls(xml_text: str) -> tuple[set[str], set[str]]:
    """Parse a sitemap document into ``(page_urls, subsitemap_refs)``.

    Namespace-flexible: documents with or without the standard sitemap
    xmlns both parse. Sub-sitemap references are returned separately so
    callers never treat index entries as pages.
    """
    pages: set[str] = set()
    subs: set[str] = set()
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        logger.debug("Sitemap XML parse error: %s", exc)
        return pages, subs

    if _local_tag(root) == "sitemapindex":
        containers, dest = root.findall("{*}sitemap"), subs
    else:
        containers, dest = root.findall("{*}url"), pages
        if not containers:
            # Non-standard urlset with <loc> directly under the root.
            for elem in root.iter():
                if _local_tag(elem) == "loc" and elem.text:
                    dest.add(elem.text.strip())
            return pages, subs

    for container in containers:
        loc = container.find("{*}loc")
        if loc is not None and loc.text:
            dest.add(loc.text.strip())

    return pages, subs


# Backwards-compatible alias (older callers expected a flat set).
def _parse_sitemap_urls(xml_text: str):
    pages, subs = parse_sitemap_urls(xml_text)
    return pages | subs


def _walk_up_sitemaps(base_url: str, session: requests.Session) -> str | None:
    """Walk up the URL path hierarchy looking for sitemap.xml.

    E.g. for ``https://example.com/docs/intro/`` it tries:
      1. ``https://example.com/docs/intro/sitemap.xml``
      2. ``https://example.com/docs/sitemap.xml``
      3. ``https://example.com/sitemap.xml``

    Returns the XML text of the first sitemap found, or ``None``.
    """
    from urllib.parse import urlunsplit
    parsed = urlparse(base_url)
    # Build list of candidate base paths, longest → shortest
    path = parsed.path.rstrip("/")
    parts = [p for p in path.split("/") if p]
    candidates = []
    for i in range(len(parts), -1, -1):
        sub = "/".join(parts[:i])
        candidate = urlunsplit((parsed.scheme, parsed.netloc, f"/{sub}" if sub else "/", "", ""))
        candidates.append(candidate.rstrip("/") or f"{parsed.scheme}://{parsed.netloc}")

    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        xml_text = _fetch_sitemap_xml(candidate, session)
        if xml_text is not None:
            logger.info("Found sitemap at %s", candidate)
            return xml_text
    return None


def discover_from_sitemap(base_url: str, session: requests.Session) -> set[str]:
    """Discover page URLs from a site's ``/sitemap.xml``.

    Fetches the sitemap (with ``.gz`` fallback), parses all ``<loc>``
    entries, handles sitemap index files by recursively fetching
    sub-sitemaps, and returns normalised same-domain URLs.

    Walks up the URL path hierarchy if the immediate sitemap is not found
    (e.g. tries ``/sitemap.xml`` when ``/docs/sitemap.xml`` 404s).

    Args:
        base_url: Root URL of the documentation site.
        session:  A ``requests.Session``.

    Returns:
        A set of normalised absolute URL strings.
    """
    base_url = base_url.rstrip("/")
    logger.info("Fetching sitemap from %s", base_url)

    # Try the base URL directly first
    xml_text = _fetch_sitemap_xml(base_url, session)
    if xml_text is None:
        # Walk up path hierarchy (e.g. /docs/ → /)
        xml_text = _walk_up_sitemaps(base_url, session)
    if xml_text is None:
        logger.debug("No sitemap found for %s", base_url)
        return set()

    pages, subs = parse_sitemap_urls(xml_text)

    # Expand sub-sitemap references — index entries are never pages.
    # Depth-limited and cycle-guarded.
    seen_refs: set[str] = set()
    frontier = [s.strip() for s in subs if _same_domain(s, base_url)]
    depth = 0
    while frontier and depth < 3:
        next_frontier: list[str] = []
        for ref in frontier:
            if ref in seen_refs:
                continue
            seen_refs.add(ref)
            resp, err = retry_get(session, ref)
            if err or resp is None or resp.status_code != 200:
                continue
            ref_pages, ref_subs = parse_sitemap_urls(_decode_xml(resp))
            pages |= ref_pages
            next_frontier.extend(
                s.strip() for s in ref_subs if _same_domain(s, base_url)
            )
        frontier = next_frontier
        depth += 1

    # Filter to same-site and normalise.
    urls: set[str] = set()
    for url in pages:
        url = url.strip()
        if not url or not _same_domain(url, base_url):
            continue
        urls.add(normalize_url(url))

    logger.info("Discovered %d URLs from sitemap", len(urls))
    return urls
