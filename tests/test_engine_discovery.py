"""Engine-lane discovery regression tests against the local fixture server.

Covers plan §4 fixes: /sitemap.xml suffix bug (#2), netloc filtering (#4),
sitemap-index sub-locs never treated as pages (#5), namespace-flexible
parsing (#11).
"""

import requests

from gitbook_downloader.utils import create_session
import gitbook_downloader.utils.discovery as discovery

FIXTURES_DIR = None  # set lazily to avoid duplicate constant


def _fixtures():
    from pathlib import Path

    return Path(__file__).parent / "fixtures"


# ── Fix #2: /sitemap.xml must actually be requested ──────────────


class TestFetchSitemapXml:
    def test_requests_canonical_sitemap_xml_path(self, fixture_server):
        """The old code requested /sitemap and /sitemap.gz, never /sitemap.xml."""
        requested = []

        class RecordingSession(requests.Session):
            def get(self, url, **kwargs):
                requested.append(url)
                return super().get(url, **kwargs)

        xml = discovery._fetch_sitemap_xml(fixture_server.base_url, RecordingSession())
        assert xml is not None, "no sitemap found"
        assert f"{fixture_server.base_url}/sitemap.xml" in requested

    def test_discover_from_sitemap_returns_pages(self, fixture_server):
        session = create_session()
        urls = discovery.discover_from_sitemap(fixture_server.base_url, session)
        normalized = {u.rstrip("/") for u in urls}
        assert fixture_server.url("/docs/intro") in normalized
        assert fixture_server.url("/docs/guide") in normalized


# ── Fix #5: sitemap-index sub-locs are not pages ─────────────────


class TestSitemapIndex:
    def test_index_subsitemaps_expanded_not_returned_as_pages(
        self, fixture_server, monkeypatch
    ):
        index_xml = (
            (_fixtures() / "sitemap_index.xml")
            .read_text(encoding="utf-8")
            .replace("{{BASE}}", fixture_server.base_url)
        )
        monkeypatch.setattr(
            discovery, "_fetch_sitemap_xml", lambda base_url, session: index_xml
        )
        session = create_session()
        urls = discovery.discover_from_sitemap(fixture_server.base_url, session)
        # Pages from the expanded sub-sitemap are present…
        normalized = {u.rstrip("/") for u in urls}
        assert fixture_server.url("/docs/intro") in normalized
        assert fixture_server.url("/docs/guide") in normalized
        # …but no .xml reference itself leaks in as a page.
        assert not any(u.split("?")[0].lower().endswith(".xml") for u in urls)


# ── Namespace-flexible parsing ───────────────────────────────────


class TestParseSitemapUrls:
    def test_namespace_free_urlset_parses(self):
        xml = (
            '<?xml version="1.0"?><urlset>'
            "<url><loc>https://x.com/a</loc></url>"
            "<url><loc>https://x.com/b</loc></url>"
            "</urlset>"
        )
        assert discovery._parse_sitemap_urls(xml) == {
            "https://x.com/a",
            "https://x.com/b",
        }

    def test_namespaced_urlset_parses(self):
        xml = (
            '<?xml version="1.0"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<url><loc>https://x.com/a</loc></url></urlset>"
        )
        assert discovery._parse_sitemap_urls(xml) == {"https://x.com/a"}

    def test_separates_pages_from_subsitemap_refs(self):
        xml = (
            '<?xml version="1.0"?>'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<sitemap><loc>https://x.com/sub.xml</loc></sitemap></sitemapindex>"
        )
        pages, subs = discovery.parse_sitemap_urls(xml)
        assert pages == set()
        assert subs == {"https://x.com/sub.xml"}
