"""Output contract writer for gitbook-downloader v7.

Turns a list of captured pages into the four output artifacts promised by
the v7 output contract (plan §1):

1. **Page tree** — per-page ``.md`` files mirroring the site's URL paths,
   each with YAML frontmatter (source_url / title / crawl_date /
   content_hash / site_version).
2. **Book file** — one combined ``book.md`` with a table of contents, in
   deterministic page order.
3. **Manifest** — ``llms.txt`` index at the output root.
4. **Frontmatter** — on every page file.

Output routing (plan §1): a capture goes to BOTH the project-local
``./<domain>-docs/`` folder AND the Library at
``~/.gitbook-downloader/docs/<domain>/``, unless ``output_mode`` opts out.

All writes are atomic (temp file + rename) via
:func:`gitbook_downloader.storage.manager.atomic_write_text`.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from .storage.manager import atomic_write_text

__all__ = [
    "CapturedPage",
    "PublishOutcome",
    "content_hash",
    "render_frontmatter",
    "page_relpath",
    "sort_pages",
    "write_page_tree",
    "assemble_book",
    "build_manifest",
    "publish",
]


# ── Data model ──────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CapturedPage:
    """One unit of documentation content, ready to be written to disk."""

    url: str
    title: str
    content: str                 # Markdown body WITHOUT frontmatter
    site_version: str = ""       # e.g. "v2", "" when the site has no versions


@dataclass
class PublishOutcome:
    """Where the output contract artifacts were written."""

    local_path: Path | None = None
    library_path: Path | None = None
    book_file: Path | None = None
    manifest_file: Path | None = None
    page_files: list[Path] = field(default_factory=list)
    bytes_written: int = 0


# ── Helpers ─────────────────────────────────────────────────────────────


def utc_now_iso() -> str:
    """Current UTC time as an ISO-8601 string with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def content_hash(text: str) -> str:
    """SHA-256 hex digest of *text* (UTF-8)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _yaml(value: str) -> str:
    """Render a Python string as a double-quoted YAML scalar."""
    escaped = (
        str(value)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", " ")
        .replace("\r", " ")
    )
    return f'"{escaped}"'


def render_frontmatter(page: CapturedPage, crawl_date: str) -> str:
    """Render the YAML frontmatter block for one page.

    Fields (pinned): source_url, title, crawl_date, content_hash,
    site_version.
    """
    lines = [
        "---",
        f"source_url: {_yaml(page.url)}",
        f"title: {_yaml(page.title)}",
        f"crawl_date: {_yaml(crawl_date)}",
        f"content_hash: {_yaml(content_hash(page.content))}",
        f"site_version: {_yaml(page.site_version)}",
        "---",
        "",
    ]
    return "\n".join(lines)


_WINDOWS_RESERVED = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)

_SEGMENT_RE = re.compile(r"[^A-Za-z0-9._-]+")
_EXT_STRIP_RE = re.compile(r"\.(md|html?|php|aspx?)$", re.IGNORECASE)


def _sanitize_segment(segment: str) -> str:
    cleaned = _SEGMENT_RE.sub("-", segment.strip())
    cleaned = cleaned.strip(".-")
    if not cleaned:
        return "page"
    if cleaned.upper() in _WINDOWS_RESERVED:
        cleaned = f"_{cleaned}"
    return cleaned[:80]


def page_relpath(url: str) -> str:
    """Map a page URL to its relative path inside the page tree.

    ``https://docs.example.com/api/v2/auth`` → ``api/v2/auth.md``
    ``https://docs.example.com/``            → ``index.md``

    Query strings and fragments are ignored; every path segment is
    sanitised to a safe filename component; ``..`` segments are dropped so
    a hostile URL can never escape the output directory.
    """
    path = urlparse(url).path
    raw_segments = [s for s in path.split("/") if s]
    segments: list[str] = []
    for seg in raw_segments:
        if seg in ("..", "."):
            continue  # traversal guard
        seg = _EXT_STRIP_RE.sub("", seg)
        segments.append(_sanitize_segment(seg))
    if not segments:
        return "index.md"
    return "/".join(segments) + ".md"


def sort_pages(pages: list[CapturedPage]) -> list[CapturedPage]:
    """Deterministic page order: site version (natural), then URL path."""

    def key(p: CapturedPage):
        version = p.site_version or ""
        numbers = tuple(int(n) for n in re.findall(r"\d+", version))
        return ((0,) if not version else (1,) + numbers,
                version, urlparse(p.url).path.lower())

    return sorted(pages, key=key)


def dedupe_pages(pages: list[CapturedPage]) -> list[CapturedPage]:
    """Drop duplicate URLs, keeping the first occurrence of each."""
    seen: set[str] = set()
    unique: list[CapturedPage] = []
    for p in pages:
        if p.url in seen:
            continue
        seen.add(p.url)
        unique.append(p)
    return unique


def derive_site_title(pages: list[CapturedPage], domain: str) -> str:
    """Pick a human title for the site: first non-empty page title, else domain."""
    for p in sort_pages(pages):
        if p.title and p.title.strip():
            return p.title.strip()
    return domain


# ── Writers ─────────────────────────────────────────────────────────────


def write_page_tree(
    root: Path,
    pages: list[CapturedPage],
    *,
    crawl_date: str,
) -> tuple[list[Path], int]:
    """Write every page under ``root/pages/<relpath>.md`` with frontmatter.

    Pages are processed in deterministic (:func:`sort_pages`) order and
    filename collisions are resolved with ``-2``, ``-3`` … suffixes.

    Returns:
        ``(written_paths, bytes_written)``
    """
    pages_dir = root / "pages"
    used: set[str] = set()
    written: list[Path] = []
    total_bytes = 0

    for page in sort_pages(dedupe_pages(pages)):
        rel = page_relpath(page.url)
        stem, dot, ext = rel.rpartition(".")
        candidate = rel
        n = 2
        while candidate.replace("\\", "/") in used:
            candidate = f"{stem}-{n}{dot}{ext}"
            n += 1
        used.add(candidate.replace("\\", "/"))

        text = render_frontmatter(page, crawl_date) + "\n" + page.content.rstrip() + "\n"
        dest = pages_dir / candidate
        atomic_write_text(dest, text)
        written.append(dest)
        total_bytes += len(text.encode("utf-8"))

    return written, total_bytes


def assemble_book(
    pages: list[CapturedPage],
    *,
    site_title: str,
    source_url: str,
    crawl_date: str,
) -> str:
    """Assemble the single-file book: header + TOC + all pages.

    Page order is deterministic (:func:`sort_pages`), so two captures of
    identical content produce byte-identical books.
    """
    ordered = sort_pages(dedupe_pages(pages))
    lines: list[str] = [f"# {site_title}", "", f"> Source: {source_url}", f"> Captured: {crawl_date}", ""]

    lines.append("## Table of Contents")
    lines.append("")
    for i, page in enumerate(ordered, 1):
        title = page.title or page.url
        lines.append(f"{i}. [{title}](pages/{page_relpath(page.url)})")
    lines.append("")

    for page in ordered:
        title = page.title or page.url
        lines.append("---")
        lines.append("")
        lines.append(f"# {title}")
        lines.append("")
        body = page.content.strip()
        # Demote the page's own leading H1 so it doesn't fight the section heading.
        body = re.sub(r"^#\s+.+\n+", "", body)
        lines.append(body)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_manifest(
    pages: list[CapturedPage],
    *,
    site_title: str,
    source_url: str,
    provider: str,
    crawl_date: str,
    book_name: str = "book.md",
) -> str:
    """Build the ``llms.txt`` manifest listing what was captured and where."""
    ordered = sort_pages(dedupe_pages(pages))
    lines = [
        f"# {site_title}",
        "",
        f"> Markdown capture of {source_url}",
        f"> Provider: {provider or 'unknown'} · Captured: {crawl_date} · Pages: {len(ordered)}",
        "> Generated by gitbook-downloader.",
        "",
        "## How to use",
        "",
        f"- `{book_name}` — the whole site in one file (TOC included).",
        "- `pages/` — one Markdown file per page, mirroring the site's URL tree.",
        "",
        "## Pages",
        "",
    ]
    for page in ordered:
        title = (page.title or page.url).replace("\n", " ").strip()
        lines.append(f"- [{title}](pages/{page_relpath(page.url)}): {page.url}")
    return "\n".join(lines) + "\n"


# ── Routing ─────────────────────────────────────────────────────────────


def publish(
    pages: list[CapturedPage],
    *,
    domain: str,
    source_url: str,
    provider: str,
    output_mode: str = "both",
    local_dir: Path | None = None,
    library_dir: Path | None = None,
    crawl_date: str | None = None,
) -> PublishOutcome:
    """Write the full output contract to the configured destinations.

    Args:
        pages: Captured pages (must be non-empty).
        domain: Site domain (used for the default title fallback).
        source_url: Root URL of the source.
        provider: Provider identifier reported in the manifest.
        output_mode: ``"both"``, ``"library"`` or ``"local"``.
        local_dir: Project-local root (e.g. ``./docs.example.com-docs``).
        library_dir: Library root (e.g. ``~/.gitbook-downloader/docs/<domain>``).

    In the library the book copy is named ``docs.md`` (legacy-compatible
    latest dump); project-local captures get ``book.md``.
    """
    if not pages:
        raise ValueError("publish() requires at least one page")
    if output_mode not in ("both", "library", "local"):
        raise ValueError(f"Invalid output_mode: {output_mode!r}")

    crawl_date = crawl_date or utc_now_iso()
    site_title = derive_site_title(pages, domain)
    outcome = PublishOutcome()

    targets: list[tuple[str, Path]] = []
    if output_mode in ("both", "local") and local_dir is not None:
        targets.append(("book.md", Path(local_dir)))
        outcome.local_path = Path(local_dir)
    if output_mode in ("both", "library") and library_dir is not None:
        targets.append(("docs.md", Path(library_dir)))
        outcome.library_path = Path(library_dir)

    for book_name, root in targets:
        page_files, nbytes = write_page_tree(root, pages, crawl_date=crawl_date)
        book_text = assemble_book(
            pages, site_title=site_title, source_url=source_url, crawl_date=crawl_date
        )
        manifest_text = build_manifest(
            pages,
            site_title=site_title,
            source_url=source_url,
            provider=provider,
            crawl_date=crawl_date,
            book_name=book_name,
        )
        book_file = atomic_write_text(root / book_name, book_text)
        manifest_file = atomic_write_text(root / "llms.txt", manifest_text)

        outcome.page_files.extend(page_files)
        outcome.bytes_written += nbytes + len(book_text.encode("utf-8")) \
            + len(manifest_text.encode("utf-8"))
        if outcome.book_file is None:
            outcome.book_file = book_file
        if outcome.manifest_file is None:
            outcome.manifest_file = manifest_file

    return outcome
