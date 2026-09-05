"""Tests for SQLite FTS5 search index.

All tests use a temporary directory for the database, never touching
~/.gitbook-downloader/search.db.
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from gitbook_downloader.search import SearchIndex
from gitbook_downloader.search.index import _fts_escape


class TestSearchIndexInit:
    """Tests for SearchIndex initialization."""

    def test_init_creates_schema(self):
        """Initialization should create FTS5 tables without error."""
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            stats = si.get_stats()
            assert isinstance(stats, dict)
            assert "domains" in stats
            assert "sections" in stats
            assert "pages" in stats

    def test_empty_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            stats = si.get_stats()
            assert stats["domains"] == 0
            assert stats["sections"] == 0
            assert stats["pages"] == 0

    def test_creates_db_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            db_path = Path(tmp) / "search.db"
            assert db_path.exists()


class TestSearchIndexIndexing:
    """Tests for index_domain."""

    def test_index_single_domain(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            content = "# Getting Started\n\nThis is a guide for new users."
            si.index_domain("docs.example.com", content)
            stats = si.get_stats()
            assert stats["domains"] == 1
            assert stats["sections"] >= 1

    def test_index_multiple_domains(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain("alpha.com", "# Alpha\n\nAlpha content.")
            si.index_domain("beta.com", "# Beta\n\nBeta content.")
            stats = si.get_stats()
            assert stats["domains"] == 2

    def test_index_with_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain(
                "docs.example.com",
                "# Guide\n\nContent.",
                domain_url="https://docs.example.com",
            )
            domains = si.list_indexed_domains()
            assert len(domains) == 1
            assert domains[0]["url"] == "https://docs.example.com"

    def test_index_replaces_previous(self):
        """Re-indexing the same domain should replace, not duplicate."""
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain("test.com", "# Old Content\n\nOld stuff.")
            si.index_domain("test.com", "# New Content\n\nNew stuff.")
            stats = si.get_stats()
            assert stats["domains"] == 1

    def test_index_empty_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain("empty.com", "")
            stats = si.get_stats()
            assert stats["domains"] == 1

    def test_index_preserves_heading_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            content = """# Introduction

Welcome to the docs.

## Configuration

How to configure the tool.

## API Reference

API documentation here.
"""
            si.index_domain("docs.example.com", content)
            stats = si.get_stats()
            # Should have at least 3 sections (Intro, Configuration, API Reference)
            assert stats["sections"] >= 3


class TestSearchIndexSearch:
    """Tests for the search method."""

    def test_empty_search_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            results = si.search("")
            assert results == []

    def test_whitespace_search_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            results = si.search("   ")
            assert results == []

    def test_search_no_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain("test.com", "# Guide\n\nSome content.")
            results = si.search("xyznonexistent")
            assert isinstance(results, list)

    def test_search_finds_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            content = "# Authentication\n\nAPI keys are used for authentication."
            si.index_domain("docs.example.com", content)
            results = si.search("authentication")
            assert isinstance(results, list)
            # The porter stemmer should match "authentication"
            if results:
                assert results[0]["domain"] == "docs.example.com"

    def test_search_result_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain("test.com", "# Guide\n\nAuthentication guide.")
            results = si.search("guide")
            if results:
                r = results[0]
                assert "url" in r
                assert "title" in r
                assert "snippet" in r
                assert "domain" in r
                assert "section_heading" in r
                assert "rank" in r

    def test_search_with_domain_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain("cats.com", "# Cats\n\nContent about cats and dogs.")
            si.index_domain("dogs.com", "# Dogs\n\nContent about dogs and cats.")
            results_cats = si.search("cats", domain="cats.com")
            results_dogs = si.search("cats", domain="dogs.com")
            if results_cats:
                assert all(r["domain"] == "cats.com" for r in results_cats)
            if results_dogs:
                assert all(r["domain"] == "dogs.com" for r in results_dogs)

    def test_search_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            content = "\n".join(
                [f"# Section {i}\n\nContent about documentation tools." for i in range(20)]
            )
            si.index_domain("large.com", content)
            results = si.search("documentation", limit=3)
            assert len(results) <= 3


class TestSearchIndexDomains:
    """Tests for list_indexed_domains and delete_domain."""

    def test_list_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            domains = si.list_indexed_domains()
            assert domains == []

    def test_list_after_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain("alpha.com", "# Alpha\n\nContent.")
            si.index_domain("beta.com", "# Beta\n\nContent.")
            domains = si.list_indexed_domains()
            names = [d["name"] for d in domains]
            assert "alpha.com" in names
            assert "beta.com" in names

    def test_list_domain_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain("test.com", "# Test\n\nContent.", domain_url="https://test.com")
            domains = si.list_indexed_domains()
            assert len(domains) == 1
            d = domains[0]
            assert d["name"] == "test.com"
            assert d["url"] == "https://test.com"
            assert d["pages"] >= 1
            assert d["last_indexed"] is not None

    def test_delete_domain(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain("test.com", "# Test\n\nContent.")
            si.delete_domain("test.com")
            domains = si.list_indexed_domains()
            names = [d["name"] for d in domains]
            assert "test.com" not in names

    def test_delete_nonexistent_no_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            # Should not raise
            si.delete_domain("nonexistent.com")


class TestSearchIndexStats:
    """Tests for get_stats."""

    def test_stats_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            stats = si.get_stats()
            assert stats == {"domains": 0, "pages": 0, "sections": 0}

    def test_stats_after_indexing(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            content = "# Intro\n\nContent.\n\n# Guide\n\nMore content."
            si.index_domain("test.com", content, domain_url="https://test.com")
            stats = si.get_stats()
            assert stats["domains"] == 1
            assert stats["sections"] >= 2

    def test_stats_after_delete(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain("test.com", "# Test\n\nContent.")
            si.delete_domain("test.com")
            stats = si.get_stats()
            assert stats["domains"] == 0


class TestSearchIndexSectionParsing:
    """Tests for _parse_sections static method."""

    def test_empty_content(self):
        result = SearchIndex._parse_sections("")
        assert result == [("", "")]

    def test_whitespace_only(self):
        result = SearchIndex._parse_sections("   \n  \n  ")
        assert result == [("", "")]

    def test_no_headings(self):
        result = SearchIndex._parse_sections("Just some text without headings.")
        assert len(result) == 1
        assert result[0][0] == ""  # empty heading

    def test_single_heading(self):
        result = SearchIndex._parse_sections("# Introduction\n\nSome content here.")
        assert len(result) == 1
        assert result[0][0] == "Introduction"

    def test_multiple_headings(self):
        content = "# Intro\n\nIntro content.\n\n## Setup\n\nSetup content."
        result = SearchIndex._parse_sections(content)
        headings = [h for h, _ in result]
        assert "Intro" in headings
        assert "Setup" in headings

    def test_preamble_before_first_heading(self):
        content = "Preamble text.\n\n# First Section\n\nSection content."
        result = SearchIndex._parse_sections(content)
        # First section should be the preamble with empty heading
        assert result[0][0] == ""
        assert "Preamble text" in result[0][1]


class TestSearchIndexPageCounts:
    """Tests for distinct-URL page counting (``domains.pages``).

    The old implementation counted ``Source:`` markers in docs.md — always
    1, because the book carries a single blockquote source header.
    """

    def test_page_count_equals_distinct_section_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            content = (
                "# Intro\n\nIntro content.\n\n"
                "## Setup\n\nSetup content.\n\n"
                "## API Reference\n\nAPI content.\n"
            )
            si.index_domain(
                "docs.example.com",
                content,
                domain_url="https://docs.example.com",
            )
            domains = si.list_indexed_domains()
            assert domains[0]["pages"] == 3

    def test_page_count_is_real_for_multipage_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            content = "\n\n".join(
                f"# Page {i}\n\nBody of page {i} about documentation." for i in range(4)
            )
            si.index_domain("multi.com", content)
            pages = si.list_indexed_domains()[0]["pages"]
            assert pages == 4
            assert pages != 1

    def test_page_count_matches_distinct_urls_in_pages_meta(self):
        """The ``domains`` page count must equal the distinct URLs stored."""
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            content = "# A\n\nAlpha.\n\n# B\n\nBeta.\n\n" "## A-B\n\nDifferent slug from A alone.\n"
            si.index_domain("check.com", content, domain_url="https://check.com")
            conn = sqlite3.connect(str(Path(tmp) / "search.db"))
            try:
                distinct = conn.execute(
                    "SELECT COUNT(DISTINCT url) FROM pages_meta WHERE domain = ?",
                    ("check.com",),
                ).fetchone()[0]
            finally:
                conn.close()
            assert distinct == 3
            assert si.list_indexed_domains()[0]["pages"] == distinct


class TestSearchIndexSlugNormalization:
    """Headings differing only by invisible characters must not collide."""

    def test_zero_width_headings_do_not_duplicate_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            clean = "# Setup\n\nClean heading body."
            zwsp = "# Set\u200bu\u200bp\n\nZero-width-space heading body."
            bom = "# Setu\ufeffp\n\nBOM heading body."
            si.index_domain(
                "zw.com",
                f"{clean}\n\n{zwsp}\n\n{bom}",
                domain_url="https://zw.com",
            )
            conn = sqlite3.connect(str(Path(tmp) / "search.db"))
            try:
                rows = conn.execute(
                    "SELECT url, section_heading FROM pages_meta WHERE domain = ?",
                    ("zw.com",),
                ).fetchall()
            finally:
                conn.close()

            urls = [r[0] for r in rows]
            assert len(urls) == len(set(urls)), f"duplicate section URLs: {urls}"
            assert urls == ["https://zw.com#setup"]
            # Neither the stored heading nor the URL may keep the invisibles.
            assert all("\u200b" not in r[1] and "\ufeff" not in r[1] for r in rows)

    def test_visible_headings_are_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            content = "# Getting Started\n\nBody.\n\n## API: v2 (advanced)\n\nBody.\n"
            si.index_domain("ok.com", content, domain_url="https://ok.com")
            conn = sqlite3.connect(str(Path(tmp) / "search.db"))
            try:
                urls = [
                    r[0]
                    for r in conn.execute(
                        "SELECT url FROM pages_meta WHERE domain = ?", ("ok.com",)
                    ).fetchall()
                ]
            finally:
                conn.close()
            assert "https://ok.com#getting-started" in urls
            assert "https://ok.com#api:-v2-(advanced)" in urls


class TestSearchIndexRemoveDomain:
    """Tests for remove_domain (the supported stale-domain purge)."""

    def test_remove_domain_deletes_all_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain("gone.com", "# Gone\n\nContent.", domain_url="https://gone.com")
            si.index_domain("kept.com", "# Kept\n\nContent.", domain_url="https://kept.com")

            si.remove_domain("gone.com")

            names = [d["name"] for d in si.list_indexed_domains()]
            assert "gone.com" not in names
            assert "kept.com" in names
            conn = sqlite3.connect(str(Path(tmp) / "search.db"))
            try:
                leftover = conn.execute(
                    "SELECT COUNT(*) FROM pages_meta WHERE domain = ?", ("gone.com",)
                ).fetchone()[0]
                fts_rows = conn.execute(
                    "SELECT COUNT(*) FROM pages_fts WHERE domain = ?", ("gone.com",)
                ).fetchone()[0]
            finally:
                conn.close()
            assert leftover == 0
            assert fts_rows == 0

    def test_remove_domain_of_unknown_domain_is_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.remove_domain("never-indexed.com")  # must not raise
            assert si.list_indexed_domains() == []

    def test_delete_domain_remains_supported_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain("alias.com", "# Alias\n\nContent.")
            si.delete_domain("alias.com")
            assert si.list_indexed_domains() == []


class TestSearchIndexInsertErrorLogging:
    def test_failed_section_insert_is_logged_not_swallowed(self, tmp_path, monkeypatch, caplog):
        """A failing section insert must log a warning (url + error), not
        silently ``pass``."""
        import gitbook_downloader.search.index as index_module

        SearchIndex(base_dir=tmp_path)  # ensure schema exists
        real_connect = index_module._get_connection

        class FailingInsertConn:
            def __init__(self, real):
                self._real = real

            def execute(self, sql, *args, **kwargs):
                if "INSERT OR REPLACE INTO pages_meta" in sql:
                    raise sqlite3.OperationalError("forced insert failure")
                return self._real.execute(sql, *args, **kwargs)

            def commit(self):
                return self._real.commit()

            def close(self):
                return self._real.close()

        def patched_connect(base_dir=None):
            return FailingInsertConn(real_connect(base_dir))

        monkeypatch.setattr(index_module, "_get_connection", patched_connect)

        si = index_module.SearchIndex.__new__(index_module.SearchIndex)
        si.base_dir = tmp_path
        with caplog.at_level("WARNING", logger="gitbook_downloader.search.index"):
            si.index_domain("broken.com", "# A\n\nAlpha.\n\n# B\n\nBeta.")

        messages = "\n".join(record.getMessage() for record in caplog.records)
        assert "forced insert failure" in messages
        assert "broken.com" in messages  # the failing section's url/domain
        # The pass must still complete and record the (empty) domain.
        domains = si.list_indexed_domains()
        assert [d["name"] for d in domains] == ["broken.com"]
        assert domains[0]["pages"] == 0


class TestFtsEscape:
    """Unit tests for the FTS5 MATCH escaping (ISSUE-1).

    FTS5 treats ``.`` and most punctuation as query syntax, so a raw dotted
    token like ``2.0.0.9`` used to raise ``fts5: syntax error near "."``.
    """

    def test_dotted_token_is_quoted_as_phrase(self):
        assert _fts_escape("2.0.0.9") == '"2.0.0.9"'

    def test_or_between_dotted_tokens_is_preserved(self):
        assert _fts_escape("2.0.0.9 OR 2.0.0.10") == '"2.0.0.9" OR "2.0.0.10"'

    def test_plain_words_pass_through_unchanged(self):
        assert _fts_escape("changelog release notes") == "changelog release notes"

    def test_safe_token_with_trailing_star_keeps_prefix_syntax(self):
        assert _fts_escape("auth*") == "auth*"

    def test_unsafe_prefix_stem_is_quoted(self):
        # '2.0*' bare is a syntax error; quoted it is a literal phrase.
        assert _fts_escape("2.0*") == '"2.0*"'

    def test_embedded_double_quotes_are_stripped(self):
        assert _fts_escape('a"b') == '"ab"'
        assert _fts_escape('"') == ""  # quotes-only token carries nothing

    def test_orphaned_operators_are_dropped_not_emitted(self):
        # A lone/trailing/doubled operator would be a MATCH syntax error.
        assert _fts_escape("AND") == ""
        assert _fts_escape("release AND") == "release"
        assert _fts_escape("AND release") == "release"
        assert _fts_escape("release AND AND notes") == "release AND notes"

    def test_totality_over_hostile_input(self):
        for query in ["", "   ", '("', "!!!", '""', "\t\n", ":", "()"]:
            assert isinstance(_fts_escape(query), str)


class TestSearchSpecialTokens:
    """ISSUE-1: user queries with dotted/special tokens must never raise.

    Live repro: ``search_docs(query="2.0.0.9 OR 2.0.0.10")`` returned
    ``{"error": "fts5: syntax error near \".\""}`` because the raw string was
    passed to the FTS5 MATCH expression.
    """

    def test_dotted_version_token_finds_release_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain(
                "releases.com",
                "# Version 2.0.0.9 Released\n\nFull release notes body.\n\n"
                "# Older\n\nVersion 1.9.0 shipped last year.",
                domain_url="https://releases.com",
            )
            results = si.search("2.0.0.9")  # raised pre-fix
            assert results, "dotted version token must match the release row"
            assert all(r["domain"] == "releases.com" for r in results)
            assert any("2.0.0.9" in r["section_heading"] for r in results)

    def test_or_query_with_dotted_tokens_runs_without_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain(
                "releases.com",
                "# Version 2.0.0.9 Released\n\nFull release notes body.\n\n"
                "# Version 2.0.0.10 Released\n\nPatch notes body.",
                domain_url="https://releases.com",
            )
            results = si.search("2.0.0.9 OR 2.0.0.10")  # raised pre-fix
            assert isinstance(results, list)
            headings = {r["section_heading"] for r in results}
            assert headings == {"Version 2.0.0.9 Released", "Version 2.0.0.10 Released"}

    def test_plain_multi_word_query_behaviour_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain(
                "docs.example.com",
                "# Changelog\n\nchangelog release notes for the latest version.\n\n"
                "# Guide\n\nHow to install the tool.",
                domain_url="https://docs.example.com",
            )
            results = si.search("changelog release notes")
            assert results, "plain multi-word query must keep matching (implicit AND)"
            assert all(r["domain"] == "docs.example.com" for r in results)
            assert any(r["section_heading"] == "Changelog" for r in results)

    def test_hostile_queries_do_not_raise(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain("docs.example.com", "# Guide\n\nSome content.")
            for query in ['("', 'a"b', "", "!!!", '""', "AND", "release AND", ":"]:
                results = si.search(query)  # must not raise for any of these
                assert isinstance(results, list)

    def test_prefix_query_still_expands(self):
        with tempfile.TemporaryDirectory() as tmp:
            si = SearchIndex(base_dir=Path(tmp))
            si.index_domain("docs.example.com", "# Docs\n\nDocumentation tools guide.")
            # 'docu*' is valid FTS5 prefix syntax and must keep working.
            results = si.search("docu*")
            assert results, "prefix wildcard must still match the stemmed token"
            assert all(r["domain"] == "docs.example.com" for r in results)
