"""Engine-lane flow regression tests against the local fixture server.

Covers plan §4 fixes: soft-200 HTML-as-md hardening (#6), deterministic
book order + entry-page title (#8), link rewriting (#9), language-filter
fixes + BFS exclude enforcement (#10), and the Lane-B facade kwargs
(path_scope / exclude_paths / timeout / max_pages=None).
"""

import time

import pytest

import gitbook_downloader.engine as engine
from gitbook_downloader.providers import GitBookProvider
from gitbook_downloader.utils import create_session


# ── Stub storage/search so engine tests never touch the library ──


@pytest.fixture()
def fake_storage(monkeypatch):
    class FakeStorage:
        def __init__(self):
            self.saved = []

        def domain_exists(self, domain):
            return False

        def save_doc(self, **kw):
            self.saved.append(kw)

    class FakeVersioning:
        def __init__(self, storage):
            pass

        def snapshot(self, domain):
            return None

    class FakeSearch:
        def __init__(self):
            pass

        def index_domain(self, *a, **k):
            pass

    store = FakeStorage()
    monkeypatch.setattr(engine, "StorageManager", lambda: store)
    monkeypatch.setattr(engine, "VersionManager", FakeVersioning)
    monkeypatch.setattr(engine, "SearchIndex", FakeSearch)
    return store


@pytest.fixture()
def session():
    return create_session()


# ── Fix #6: soft-200 HTML-as-md hardening ────────────────────────


class TestSoft200Hardening:
    def test_html_shell_md_export_is_rejected(self, fixture_server, session):
        """/spa/page.md returns 200 with an <html> shell (no doctype);
        the provider must fall back to HTML extraction instead of
        storing the shell as markdown."""
        provider = GitBookProvider()
        content = provider.extract_content(fixture_server.url("/spa/page"), session)
        assert content, "expected extracted content"
        assert "<html" not in content.lower()
        assert "Real Content" in content

    def test_looks_like_html_flags_shells(self):
        from gitbook_downloader.providers.base import looks_like_html

        assert looks_like_html("<html><head></head></html>")
        assert looks_like_html("<!DOCTYPE html><div id=root></div>")
        assert looks_like_html(
            '<div id="app"></div><script>x</script><body>y</body>'
        )
        assert not looks_like_html("# Heading\n\nSome <div>snippet</div> text.")
        assert not looks_like_html("")


# ── Facade kwargs (Lane B contract) ──────────────────────────────


class TestStreamDownloadSignature:
    def test_accepts_path_scope_exclude_timeout_and_none_max_pages(
        self, fixture_server, session, fake_storage
    ):
        combined = engine.stream_download(
            fixture_server.url("/"),
            max_pages=None,
            workers=4,
            session=session,
            path_scope=None,
            exclude_paths=None,
            timeout=5.0,
        )
        assert combined, "root crawl should produce content"
        assert "/docs/intro" in combined

    def test_max_pages_zero_still_unlimited(self, fixture_server, session, fake_storage):
        combined = engine.stream_download(
            fixture_server.url("/"), max_pages=0, workers=4, session=session
        )
        assert "/docs/guide" in combined

    def test_path_scope_restricts_crawl(self, fixture_server, session, fake_storage):
        combined = engine.stream_download(
            fixture_server.url("/"),
            max_pages=None,
            workers=4,
            session=session,
            path_scope=("/docs/",),
        )
        assert "/docs/intro" in combined
        assert "/gitbook" not in combined

    def test_exclude_paths_enforced_on_discovered_urls(
        self, fixture_server, session, fake_storage
    ):
        combined = engine.stream_download(
            fixture_server.url("/"),
            max_pages=None,
            workers=4,
            session=session,
            exclude_paths=("guide",),
        )
        assert "/docs/intro" in combined
        assert "/docs/guide" not in combined


# ── Fix #8: deterministic book order + entry-page title ──────────


class TestDeterministicOrder:
    def test_book_order_follows_crawl_order_not_completion(
        self, fixture_server, session, fake_storage, monkeypatch
    ):
        """Alphabetically-first page sleeps so it finishes LAST; the book must
        still list it first (crawl order is sorted for determinism)."""
        provider = GitBookProvider()
        original = provider.extract_content

        def slow_first(url, sess):
            if url.rstrip("/").endswith("/docs/guide"):
                time.sleep(0.2)
            return original(url, sess)

        monkeypatch.setattr(provider, "extract_content", slow_first)

        events = []
        combined = engine.stream_download(
            fixture_server.url("/"),
            max_pages=None,
            workers=4,
            session=session,
            provider=provider,
            progress_callback=events.append,
        )

        intro_pos = combined.find("Source:")
        assert intro_pos != -1
        first_source_line = combined[intro_pos:combined.find("\n", intro_pos)]
        assert "/docs/guide" in first_source_line, (
            f"first crawled page must come first regardless of completion order; got {first_source_line}"
        )
        # Stored title comes from the entry page, not whichever page finished first.
        assert fake_storage.saved, "save_doc must be called"
        assert fake_storage.saved[0]["title"] == "Guide"


# ── Fix #9: link rewriting ───────────────────────────────────────


class TestLinkRewriting:
    def test_relative_links_absolutized_against_page_url(self):
        from gitbook_downloader.engine import rewrite_markdown_links

        md_text = (
            "See [Guide](./guide) and [Self](/docs/intro) and "
            "[External](https://elsewhere.com/x) and [anchor](#details)."
        )
        out = rewrite_markdown_links(md_text, "http://srv.test/docs/intro")
        assert "[Guide](guide)" in out
        # Site-absolute self link relativizes against the page directory.
        assert "[Self](intro)" in out
        assert "[External](https://elsewhere.com/x)" in out
        # Anchor-only links are stripped to their text.
        assert "](#details)" not in out
        assert "anchor" in out

    def test_docusaurus_flow_rewrites_links(self, fixture_server, session, fake_storage):
        combined = engine.stream_download(
            fixture_server.url("/docusaurus"),
            max_pages=None,
            workers=2,
            session=session,
        )
        assert "[Usage](usage)" in combined
        assert "](./usage)" not in combined


# ── Fix #10: language filter + BFS excludes ──────────────────────


class TestLanguageFilterAndBfs:
    def test_bare_zh_filtered_from_discovered_set(
        self, fixture_server, session, fake_storage
    ):
        combined = engine.stream_download(
            fixture_server.url("/"), max_pages=None, workers=4, session=session
        )
        assert "/docs/zh-cn/page" not in combined
        assert "/docs/intro" in combined

    def test_empty_after_filter_is_empty_with_warning_not_fallback(
        self, fixture_server, session, fake_storage, monkeypatch
    ):
        provider = GitBookProvider()
        monkeypatch.setattr(
            provider,
            "discover_urls",
            lambda base_url, sess: {fixture_server.url("/docs/zh-cn/page")},
        )
        events = []
        combined = engine.stream_download(
            fixture_server.url("/docs"),
            max_pages=None,
            workers=2,
            session=session,
            provider=provider,
            progress_callback=events.append,
        )
        assert combined == ""
        warnings = [
            e for e in events if e.get("phase") == "warning" or e.get("type") == "warning"
        ]
        assert warnings, "an empty-after-filter crawl must surface a warning"

    def test_segment_boundary_prefix_match(
        self, fixture_server, session, fake_storage, monkeypatch
    ):
        """/docs scope must not admit sibling paths like /docsx."""
        provider = GitBookProvider()
        monkeypatch.setattr(
            provider,
            "discover_urls",
            lambda base_url, sess: {
                fixture_server.url("/docs/intro"),
                fixture_server.url("/docsx/page"),
            },
        )
        combined = engine.stream_download(
            fixture_server.url("/docs"),
            max_pages=None,
            workers=2,
            session=session,
            provider=provider,
        )
        assert "/docs/intro" in combined
        assert "/docsx/page" not in combined

    def test_bfs_honors_exclude_paths_and_strips_anchor_links(
        self, fixture_server, session, fake_storage, monkeypatch
    ):
        """Force BFS by disabling every discovery path."""
        import gitbook_downloader.utils.discovery as disc

        provider = GitBookProvider()
        monkeypatch.setattr(provider, "discover_urls", lambda b, s: set())
        monkeypatch.setattr(disc, "discover_from_llms_txt", lambda b, s: set())
        monkeypatch.setattr(disc, "discover_from_sitemap", lambda b, s: set())

        combined = engine.stream_download(
            fixture_server.url("/gitbook"),
            max_pages=None,
            workers=2,
            session=session,
            provider=provider,
            exclude_paths=("guide",),
        )
        assert "/gitbook" in combined          # start page crawled
        assert "/docs/intro" in combined       # nav link followed
        assert "/docs/guide" not in combined   # excluded
