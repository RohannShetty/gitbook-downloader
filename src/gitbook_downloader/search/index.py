"""SQLite FTS5 full-text search index for downloaded documentation.

Search database lives at ~/.gitbook-downloader/search.db.
Uses FTS5 (bundled with stdlib sqlite3 since Python 3.6).
"""

import logging
import re
import sqlite3
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

SEARCH_DB_NAME = "search.db"

_FTS_SAFE_TOKEN = re.compile(r"^[A-Za-z0-9_]+$")
_FTS_OPERATORS = frozenset({"AND", "OR", "NOT"})


def _fts_escape(query: str) -> str:
    """Escape a user query into a syntactically valid FTS5 ``MATCH`` expression.

    FTS5 treats most punctuation (``.``, ``(``, ``:`` …) as query syntax, so a
    bare token like ``2.0.0.9`` raises ``fts5: syntax error near "."``. Rules:

    - Tokens that are already FTS5-safe (``[A-Za-z0-9_]+``) pass through
      unchanged, preserving behaviour for plain multi-word queries (implicit
      AND). A safe token with a trailing ``*`` (e.g. ``auth*``) also passes
      through so prefix search keeps working.
    - Upper-case bare ``AND`` / ``OR`` / ``NOT`` pass through as operators;
      they are dropped when orphaned (leading, doubled, or trailing) so a
      malformed query degrades instead of raising.
    - Every other token is wrapped in double quotes as a literal phrase
      (``2.0.0.9`` → ``"2.0.0.9"``) after removing embedded double quotes,
      which would otherwise terminate the phrase early.
    """
    tokens: list[str] = []
    for token in query.split():
        if token in _FTS_OPERATORS or _FTS_SAFE_TOKEN.match(token):
            tokens.append(token)
            continue
        if token.endswith("*") and len(token) > 1 and _FTS_SAFE_TOKEN.match(token[:-1]):
            tokens.append(token)  # valid FTS5 prefix query, e.g. auth*
            continue
        cleaned = token.replace('"', "")
        if cleaned:
            tokens.append(f'"{cleaned}"')
    # Drop orphaned operators so the expression always parses: an operator
    # must sit between two terms.
    result: list[str] = []
    for token in tokens:
        if token in _FTS_OPERATORS and (not result or result[-1] in _FTS_OPERATORS):
            continue
        result.append(token)
    while result and result[-1] in _FTS_OPERATORS:
        result.pop()
    return " ".join(result)


def _strip_unprintable(text: str) -> str:
    """Remove non-printable characters (zero-width marks, BOM, control chars).

    Headings harvested from HTML often carry invisible characters such as
    ``\\u200b``; without normalization, two visually identical headings
    produce distinct ``section_heading`` values and duplicate section URLs.
    """
    return "".join(ch for ch in text if ch.isprintable())


def _get_db_path(base_dir: Optional[Path] = None) -> Path:
    """Return path to the SQLite search database."""
    base = Path(base_dir).expanduser().resolve() if base_dir else Path.home() / ".gitbook-downloader"
    base.mkdir(parents=True, exist_ok=True)
    return base / SEARCH_DB_NAME


def _get_connection(base_dir: Optional[Path] = None) -> sqlite3.Connection:
    """Get a SQLite connection with FTS5 enabled."""
    db_path = _get_db_path(base_dir)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=OFF")  # Faster bulk indexing
    return conn


class SearchIndex:
    """SQLite FTS5 search index for downloaded documentation.

    Provides full-text search with BM25 ranking over downloaded
    documentation sections. The index lives at ``~/.gitbook-downloader/search.db``
    and is rebuilt from stored docs.md files via :meth:`index_domain`.

    Example::

        idx = SearchIndex()
        idx.index_domain("docs.example.com", content, "https://docs.example.com")
        results = idx.search("configuration guide")
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialise the search index.

        Args:
            base_dir: Override the default ``~/.gitbook-downloader``
                      base directory.  Strings are expanded and resolved.
        """
        self.base_dir = base_dir
        self._init_schema()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _init_schema(self):
        """Create FTS5 tables if they don't exist."""
        conn = _get_connection(self.base_dir)
        try:
            # FTS5 virtual table — content is sourced from pages_meta.
            # The 'porter unicode61' tokenizer stems terms and handles
            # unicode, which is ideal for mixed-language documentation.
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
                    title, content, url UNINDEXED,
                    domain UNINDEXED,
                    section_heading,
                    content='pages_meta',
                    content_rowid='rowid',
                    tokenize='porter unicode61'
                )
            """)

            # Underlying content table for the FTS5 external-content setup.
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pages_meta(
                    url             TEXT NOT NULL,
                    title           TEXT NOT NULL,
                    content         TEXT NOT NULL,
                    domain          TEXT NOT NULL,
                    section_heading TEXT DEFAULT '',
                    indexed_at      TEXT DEFAULT (datetime('now')),
                    UNIQUE(url, section_heading)
                )
            """)

            # Domain-level bookkeeping.
            conn.execute("""
                CREATE TABLE IF NOT EXISTS domains(
                    name        TEXT PRIMARY KEY,
                    url         TEXT,
                    pages       INTEGER DEFAULT 0,
                    last_indexed TEXT
                )
            """)
            conn.commit()
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    def index_domain(self, domain: str, docs_content: str, domain_url: str = ""):
        """Index all sections of a domain's documentation.

        Reads the full *docs_content* markdown, splits it into logical
        sections by heading, and inserts each section into the FTS5 index.

        Args:
            domain: Domain name (directory key used by StorageManager).
            docs_content: Full markdown content of docs.md.
            domain_url: Source URL for the domain (used for section anchors).
        """
        conn = _get_connection(self.base_dir)
        try:
            sections = self._parse_sections(docs_content)

            # Clear existing entries for this domain so a re-index is clean.
            conn.execute("DELETE FROM pages_meta WHERE domain = ?", (domain,))
            conn.execute("DELETE FROM domains WHERE name = ?", (domain,))

            for heading, content in sections:
                # Normalize first so headings that differ only by invisible
                # characters collapse onto one URL / section_heading.
                heading = _strip_unprintable(heading)
                # Derive a stable URL for each section.
                if domain_url:
                    slug = heading.lower().replace(" ", "-") if heading else "home"
                    section_url = f"{domain_url}#{slug}"
                else:
                    section_url = f"{domain}/{heading or 'home'}"

                try:
                    conn.execute(
                        """INSERT OR REPLACE INTO pages_meta
                           (url, title, content, domain, section_heading)
                           VALUES (?, ?, ?, ?, ?)""",
                        (section_url, heading or domain, content[:100000], domain, heading or ""),
                    )
                except Exception as exc:
                    # One bad section must not abort the whole indexing pass,
                    # but it must be visible in logs (url + error), not swallowed.
                    logger.warning(
                        "Failed to index section %r of domain %s: %s",
                        section_url,
                        domain,
                        exc,
                    )

            # Page count = distinct section URLs actually indexed for this
            # domain (dedupe by URL), not a marker count from docs.md.
            page_count = conn.execute(
                "SELECT COUNT(DISTINCT url) FROM pages_meta WHERE domain = ?",
                (domain,),
            ).fetchone()[0]

            # Rebuild the FTS5 index from the updated content table.
            conn.execute("INSERT INTO pages_fts(pages_fts) VALUES('rebuild')")

            # Upsert domain record.
            conn.execute(
                """INSERT OR REPLACE INTO domains(name, url, pages, last_indexed)
                   VALUES (?, ?, ?, datetime('now'))""",
                (domain, domain_url, page_count),
            )
            conn.commit()
        finally:
            conn.close()

    def index_domain_from_storage(self, domain: str, storage_manager, domain_url: str = ""):
        """Convenience: load docs.md from a StorageManager and index it.

        Args:
            domain: Domain name.
            storage_manager: A :class:`~gitbook_downloader.storage.StorageManager` instance.
            domain_url: Source URL for the domain.
        """
        docs_content = storage_manager.load_doc(domain)
        if not docs_content:
            raise FileNotFoundError(f"No docs.md found for domain '{domain}'")
        self.index_domain(domain, docs_content, domain_url)

    # ------------------------------------------------------------------
    # Section parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_sections(content: str) -> list:
        """Split markdown content into sections by ``#``/``##`` headings.

        Returns:
            list[tuple[str, str]]: ``(heading_text, section_content)`` pairs.
            The first section may have an empty heading (content before
            the first heading).
        """
        if not content or not content.strip():
            return [("", "")]

        # Match ## or # headings.
        pattern = re.compile(r"^(#{1,2})\s+(.+?)$", re.MULTILINE)
        parts = list(pattern.finditer(content))

        if not parts:
            return [("", content)]

        sections = []
        for i, match in enumerate(parts):
            next_start = parts[i + 1].start() if i + 1 < len(parts) else len(content)
            body = content[match.end():next_start].strip()
            heading = match.group(2).strip()
            sections.append((heading, f"## {heading}\n\n{body}"))

        # Prepend any content that appeared before the first heading.
        preamble = content[: parts[0].start()].strip()
        if preamble:
            sections.insert(0, ("", preamble))

        return sections or [("", content)]

    # ------------------------------------------------------------------
    # Searching
    # ------------------------------------------------------------------

    def search(self, query: str, domain: Optional[str] = None, limit: int = 10) -> list:
        """Full-text search using FTS5 BM25 ranking.

        The query is escaped via :func:`_fts_escape` before it reaches the
        FTS5 ``MATCH`` expression: plain words keep the implicit-AND
        behaviour, bare upper-case ``AND`` / ``OR`` / ``NOT`` act as
        operators, and tokens containing punctuation (version numbers,
        symbols) are matched as quoted literal phrases instead of raising
        ``fts5: syntax error``.

        Args:
            query: User search query.
            domain: Restrict results to a specific domain.
            limit: Maximum number of results.

        Returns:
            list[dict]: Results sorted by BM25 rank (lower = better).
            Each dict has keys: ``url``, ``title``, ``snippet``, ``domain``,
            ``section_heading``, ``rank``.
        """
        if not query or not query.strip():
            return []

        match_expr = _fts_escape(query)
        if not match_expr.strip():
            # Every token was unusable (quotes/punctuation only) — nothing to
            # match, but never a syntax error.
            return []

        conn = _get_connection(self.base_dir)
        try:
            # Build a WHERE clause: always require FTS5 MATCH, optionally
            # restrict by domain.
            if domain:
                sql = """
                    SELECT
                        p.url,
                        p.title,
                        snippet(pages_fts, 1, '<b>', '</b>', '...', 40) AS snippet,
                        p.domain,
                        p.section_heading,
                        pages_fts.rank
                    FROM pages_fts
                    JOIN pages_meta p ON pages_fts.rowid = p.rowid
                    WHERE pages_fts MATCH ? AND p.domain = ?
                    ORDER BY pages_fts.rank
                    LIMIT ?
                """
                params: list = [match_expr, domain, limit]
            else:
                sql = """
                    SELECT
                        p.url,
                        p.title,
                        snippet(pages_fts, 1, '<b>', '</b>', '...', 40) AS snippet,
                        p.domain,
                        p.section_heading,
                        pages_fts.rank
                    FROM pages_fts
                    JOIN pages_meta p ON pages_fts.rowid = p.rowid
                    WHERE pages_fts MATCH ?
                    ORDER BY pages_fts.rank
                    LIMIT ?
                """
                params: list = [match_expr, limit]

            cursor = conn.execute(sql, params)
            return [
                {
                    "url": row[0],
                    "title": row[1],
                    "snippet": row[2],
                    "domain": row[3],
                    "section_heading": row[4],
                    "rank": row[5],
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Domain management
    # ------------------------------------------------------------------

    def list_indexed_domains(self) -> list:
        """List all domains present in the search index.

        Returns:
            list[dict]: Each dict has ``name``, ``url``, ``pages``,
            and ``last_indexed``.
        """
        conn = _get_connection(self.base_dir)
        try:
            cursor = conn.execute(
                "SELECT name, url, pages, last_indexed FROM domains ORDER BY last_indexed DESC"
            )
            return [
                dict(zip(["name", "url", "pages", "last_indexed"], row))
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    def remove_domain(self, domain: str) -> None:
        """Remove a domain's rows from ``pages_meta`` and ``domains``.

        Deletes every row for *domain* and rebuilds the FTS index. This is
        the supported way to purge stale or orphaned domains (domains whose
        ``docs/<domain>/`` directory no longer exists) from the index.
        """
        conn = _get_connection(self.base_dir)
        try:
            conn.execute("DELETE FROM pages_meta WHERE domain = ?", (domain,))
            conn.execute("DELETE FROM domains WHERE name = ?", (domain,))
            conn.execute("INSERT INTO pages_fts(pages_fts) VALUES('rebuild')")
            conn.commit()
        finally:
            conn.close()

    def delete_domain(self, domain: str):
        """Backward-compatible alias for :meth:`remove_domain`."""
        self.remove_domain(domain)

    def rename_domain(self, old_domain: str, new_domain: str):
        """Update domain name in the search index."""
        conn = _get_connection(self.base_dir)
        try:
            conn.execute("UPDATE pages_meta SET domain = ? WHERE domain = ?", (new_domain, old_domain))
            conn.execute("UPDATE domains SET name = ? WHERE name = ?", (new_domain, old_domain))
            conn.commit()
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def get_stats(self) -> dict:
        """Return overall search-index statistics.

        Returns:
            dict with keys ``domains``, ``pages``, ``sections``.
        """
        conn = _get_connection(self.base_dir)
        try:
            total_domains = conn.execute("SELECT COUNT(*) FROM domains").fetchone()[0]
            total_pages = conn.execute("SELECT COALESCE(SUM(pages), 0) FROM domains").fetchone()[0]
            total_sections = conn.execute("SELECT COUNT(*) FROM pages_meta").fetchone()[0]
            return {
                "domains": total_domains,
                "pages": total_pages,
                "sections": total_sections,
            }
        finally:
            conn.close()
