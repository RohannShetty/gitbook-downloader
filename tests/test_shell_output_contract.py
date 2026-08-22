"""Shell-lane tests — the output contract writer (output_contract.py).

Pure filesystem assertions on temp dirs. No network, no engine.
"""

from __future__ import annotations

import re

import pytest

from gitbook_downloader.output_contract import (
    CapturedPage,
    assemble_book,
    build_manifest,
    content_hash,
    page_relpath,
    publish,
    render_frontmatter,
    sort_pages,
    write_page_tree,
)


def make_pages():
    return [
        CapturedPage(url="https://docs.example.com/api/auth",
                     title="Auth", content="# Auth\n\nTokens."),
        CapturedPage(url="https://docs.example.com/",
                     title="Home", content="# Home\n\nWelcome."),
        CapturedPage(url="https://docs.example.com/v2/intro",
                     title="V2 Intro", content="# V2 Intro\n\nNew.",
                     site_version="v2"),
    ]


# ── Frontmatter ─────────────────────────────────────────────────────────


class TestFrontmatter:
    def test_all_pinned_fields_present(self):
        page = CapturedPage(url="https://x.com/a", title="T & C \"q\"",
                            content="body")
        fm = render_frontmatter(page, "2026-08-22T00:00:00Z")
        assert fm.startswith("---\n")
        assert 'source_url: "https://x.com/a"' in fm
        assert 'title: "T & C \\"q\\""' in fm
        assert 'crawl_date: "2026-08-22T00:00:00Z"' in fm
        assert f'content_hash: "{content_hash("body")}"' in fm
        assert 'site_version: ""' in fm
        assert fm.rstrip().endswith("---")

    def test_content_hash_is_sha256_hex(self):
        h = content_hash("hello")
        assert re.fullmatch(r"[0-9a-f]{64}", h)

    def test_site_version_field(self):
        page = CapturedPage(url="u", title="t", content="c",
                            site_version="v2")
        assert 'site_version: "v2"' in render_frontmatter(page, "d")

    def test_newlines_in_title_are_flattened(self):
        page = CapturedPage(url="u", title="bad\ntitle", content="c")
        fm = render_frontmatter(page, "d")
        assert "bad\ntitle" not in fm
        assert '"bad title"' in fm


# ── URL → path mapping ──────────────────────────────────────────────────


class TestPageRelpath:
    def test_root_maps_to_index(self):
        assert page_relpath("https://docs.example.com/") == "index.md"
        assert page_relpath("https://docs.example.com") == "index.md"

    def test_nested_path_mirrored(self):
        assert page_relpath(
            "https://docs.example.com/api/v2/auth"
        ) == "api/v2/auth.md"

    def test_html_extension_stripped(self):
        assert page_relpath("https://x.com/guide.html") == "guide.md"

    def test_query_and_fragment_ignored(self):
        assert page_relpath("https://x.com/p?x=1#frag") == "p.md"

    def test_unsafe_characters_sanitised(self):
        rel = page_relpath("https://x.com/héllo wörld/page name")
        assert " " not in rel
        assert rel == "h-llo-w-rld/page-name.md"

    def test_traversal_segments_dropped(self):
        rel = page_relpath("https://x.com/../../etc/passwd")
        assert ".." not in rel
        assert not rel.startswith("/")

    def test_windows_reserved_names_prefixed(self):
        assert page_relpath("https://x.com/con").startswith("_")


# ── Page tree ───────────────────────────────────────────────────────────


class TestWritePageTree:
    def test_writes_every_page_with_frontmatter(self, tmp_path):
        pages = make_pages()
        written, nbytes = write_page_tree(tmp_path, pages,
                                          crawl_date="2026-08-22T00:00:00Z")
        assert len(written) == 3
        assert nbytes > 0
        home = tmp_path / "pages" / "index.md"
        auth = tmp_path / "pages" / "api" / "auth.md"
        assert home.exists() and auth.exists()
        text = auth.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert "# Auth" in text

    def test_deterministic_order(self, tmp_path):
        pages = make_pages()
        w1, _ = write_page_tree(tmp_path / "a", pages, crawl_date="D")
        w2, _ = write_page_tree(tmp_path / "b", list(reversed(pages)),
                                crawl_date="D")
        assert [p.relative_to(tmp_path / "a") for p in w1] == \
               [p.relative_to(tmp_path / "b") for p in w2]

    def test_collision_gets_numeric_suffix(self, tmp_path):
        pages = [
            CapturedPage(url="https://x.com/a?one=1", title="A1",
                         content="first"),
            CapturedPage(url="https://x.com/a?two=2", title="A2",
                         content="second"),
        ]
        written, _ = write_page_tree(tmp_path, pages, crawl_date="D")
        names = sorted(p.name for p in written)
        assert names == ["a-2.md", "a.md"]

    def test_duplicate_urls_deduped(self, tmp_path):
        pages = [
            CapturedPage(url="https://x.com/dup", title="1", content="one"),
            CapturedPage(url="https://x.com/dup", title="2", content="two"),
        ]
        written, _ = write_page_tree(tmp_path, pages, crawl_date="D")
        assert len(written) == 1
        # First occurrence wins.
        assert "one" in written[0].read_text(encoding="utf-8")


# ── Book file ───────────────────────────────────────────────────────────


class TestAssembleBook:
    def test_contains_toc_and_all_pages(self):
        book = assemble_book(make_pages(), site_title="Example Docs",
                             source_url="https://docs.example.com/",
                             crawl_date="2026-08-22T00:00:00Z")
        assert book.startswith("# Example Docs")
        assert "## Table of Contents" in book
        assert "[Auth](pages/api/auth.md)" in book
        assert "[Home](pages/index.md)" in book
        assert "# Auth" in book and "# Home" in book

    def test_deterministic_byte_identical_output(self):
        a = assemble_book(make_pages(), site_title="S",
                          source_url="u", crawl_date="D")
        b = assemble_book(list(reversed(make_pages())), site_title="S",
                          source_url="u", crawl_date="D")
        assert a == b

    def test_leading_h1_demoted_not_duplicated(self):
        pages = [CapturedPage(url="https://x.com/p", title="My Title",
                              content="# My Title\n\nBody.")]
        book = assemble_book(pages, site_title="S", source_url="u",
                             crawl_date="D")
        section = book.split("# My Title\n")
        # Section heading appears once as the separator heading; the page's
        # own H1 line was stripped from its body.
        body_after_heading = section[-1]
        assert not body_after_heading.lstrip().startswith("# My Title")


# ── Manifest (llms.txt) ─────────────────────────────────────────────────


class TestBuildManifest:
    def test_lists_site_and_pages(self):
        manifest = build_manifest(
            make_pages(), site_title="Example Docs",
            source_url="https://docs.example.com/",
            provider="gitbook", crawl_date="2026-08-22T00:00:00Z",
        )
        assert manifest.startswith("# Example Docs")
        assert "Provider: gitbook" in manifest
        assert "Pages: 3" in manifest
        assert "- [Auth](pages/api/auth.md): https://docs.example.com/api/auth" \
            in manifest

    def test_manifest_is_deterministic(self):
        a = build_manifest(make_pages(), site_title="S", source_url="u",
                           provider="p", crawl_date="D")
        b = build_manifest(list(reversed(make_pages())), site_title="S",
                           source_url="u", provider="p", crawl_date="D")
        assert a == b


# ── Routing ─────────────────────────────────────────────────────────────


class TestPublishRouting:
    def test_both_writes_two_trees(self, tmp_path):
        local = tmp_path / "local"
        library = tmp_path / "library"
        outcome = publish(make_pages(), domain="docs.example.com",
                          source_url="https://docs.example.com/",
                          provider="gitbook", output_mode="both",
                          local_dir=local, library_dir=library)
        assert outcome.local_path == local
        assert outcome.library_path == library
        assert (local / "book.md").exists()
        assert (library / "docs.md").exists()
        assert outcome.book_file is not None
        assert outcome.manifest_file.name == "llms.txt"

    def test_local_only(self, tmp_path):
        outcome = publish(make_pages(), domain="d", source_url="u",
                          provider="p", output_mode="local",
                          local_dir=tmp_path / "l",
                          library_dir=tmp_path / "lib")
        assert (tmp_path / "l" / "book.md").exists()
        assert not (tmp_path / "lib").exists()

    def test_library_only(self, tmp_path):
        outcome = publish(make_pages(), domain="d", source_url="u",
                          provider="p", output_mode="library",
                          local_dir=tmp_path / "l",
                          library_dir=tmp_path / "lib")
        assert (tmp_path / "lib" / "docs.md").exists()
        assert not (tmp_path / "l").exists()
        assert outcome.local_path is None

    def test_empty_pages_rejected(self, tmp_path):
        with pytest.raises(ValueError):
            publish([], domain="d", source_url="u", provider="p",
                    output_mode="both", local_dir=tmp_path / "l",
                    library_dir=tmp_path / "lib")

    def test_invalid_mode_rejected(self, tmp_path):
        with pytest.raises(ValueError):
            publish(make_pages(), domain="d", source_url="u", provider="p",
                    output_mode="everywhere", local_dir=tmp_path / "l",
                    library_dir=tmp_path / "lib")

    def test_bytes_written_counts_all_artifacts(self, tmp_path):
        outcome = publish(make_pages(), domain="d", source_url="u",
                          provider="p", output_mode="local",
                          local_dir=tmp_path / "l")
        on_disk = sum(f.stat().st_size
                      for f in (tmp_path / "l").rglob("*") if f.is_file())
        assert outcome.bytes_written > 0
        # LF endings keep our count within rounding distance of disk size.
        assert abs(outcome.bytes_written - on_disk) < len(make_pages()) * 4 + 8


class TestSortPages:
    def test_sorted_by_version_then_path(self):
        pages = [
            CapturedPage(url="https://x.com/v2/b", title="", content="c",
                         site_version="v2"),
            CapturedPage(url="https://x.com/a", title="", content="c"),
            CapturedPage(url="https://x.com/v10/z", title="", content="c",
                         site_version="v10"),
            CapturedPage(url="https://x.com/v2/a", title="", content="c",
                         site_version="v2"),
        ]
        ordered = sort_pages(pages)
        assert [p.url for p in ordered] == [
            "https://x.com/a",
            "https://x.com/v2/a",
            "https://x.com/v2/b",
            "https://x.com/v10/z",
        ]
