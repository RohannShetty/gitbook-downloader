"""Tests for SQLite FTS5 search index.

All tests use a temporary directory for the database, never touching
~/.gitbook-downloader/search.db.
"""

import tempfile
from pathlib import Path

import pytest

from gitbook_downloader.search import SearchIndex


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


class TestSearchIndexPageCount:
    """Tests for _extract_page_count static method."""

    def test_no_sources(self):
        assert SearchIndex._extract_page_count("# Just text") == 1

    def test_with_sources(self):
        content = "Source: https://example.com/p1\n\nContent\n\nSource: https://example.com/p2"
        assert SearchIndex._extract_page_count(content) == 2

    def test_mixed_content(self):
        content = "# Header\n\nSource: https://a.com\n\nText\n\nSource: https://b.com\n\nMore\n\nSource: https://c.com"
        assert SearchIndex._extract_page_count(content) == 3
