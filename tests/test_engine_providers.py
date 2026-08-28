"""Engine-lane provider regression tests against the local fixture server.

Covers plan §4 fixes: GitBook boilerplate stripping (#1), soft-200
HTML-as-md hardening (#6), charset correction (#7), and baseline
extraction parity for every provider.
"""

from pathlib import Path

import pytest

from gitbook_downloader.providers import (
    DocusaurusProvider,
    GitBookProvider,
    MintlifyProvider,
    ReadTheDocsProvider,
)
from gitbook_downloader.utils import create_session

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _expected(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8").replace("\r\n", "\n").strip()


@pytest.fixture()
def session():
    return create_session()


# ── Fix #1: GitBook .md export boilerplate ────────────────────────


class TestGitBookBoilerplate:
    def test_md_export_strips_agent_instructions_and_trailer(self, fixture_server, session):
        """The llms.txt trailer regex was double-escaped and never matched;
        stray \\n---\\n lookaheads left horizontal rules behind."""
        provider = GitBookProvider()
        content = provider.extract_content(fixture_server.url("/gitbook"), session)
        assert content.strip() == _expected("gitbook_page.expected.md")

    def test_llm_ref_line_regex_matches_real_line(self):
        from gitbook_downloader.providers.gitbook import _LLM_REF_LINE

        line = "For the complete documentation index, see [llms.txt](https://docs.example.com/llms.txt)"
        assert _LLM_REF_LINE.search(line), "regex must match a real trailer line"
        assert _LLM_REF_LINE.search("> " + line)

    def test_strip_leaves_no_stray_horizontal_rule(self):
        from gitbook_downloader.providers.gitbook import strip_agent_boilerplate

        raw = "# Title\n\nBody text.\n\n---\n# Agent Instructions\n\nBlurb.\n\nFor the complete documentation index, see [llms.txt](https://x.com/llms.txt)\n\n---\n"
        cleaned = strip_agent_boilerplate(raw)
        assert cleaned == "# Title\n\nBody text."
        assert "---" not in cleaned


# ── Fix #11: detection hardening ─────────────────────────────────


class TestDetectionHardening:
    def test_mintlify_prose_mention_does_not_detect(self):
        """A comparison post mentioning Mintlify must not be classified as
        Mintlify — only the generator meta tag (or window.__MINTLIFY) counts."""
        html = (
            "<html><head><meta name='viewport' content='width=device-width'></head>"
            "<body><p>We compared Mintlify vs GitBook generators.</p></body></html>"
        )
        assert MintlifyProvider.detect("https://x.com/blog", html, None) is False

    def test_mintlify_generator_meta_still_detects(self):
        html = '<html><head><meta name="generator" content="Mintlify"></head></html>'
        assert MintlifyProvider.detect("https://x.com/docs", html, None) is True

    def test_rtd_prose_mention_does_not_detect(self):
        """A credit link or blog mention of readthedocs must not classify."""
        html = (
            "<html><body><p>This tool is like readthedocs but different.</p>"
            '<a href="https://readthedocs.io/some-article">article</a></body></html>'
        )
        assert ReadTheDocsProvider.detect("https://x.com/post", html, None) is False

    def test_rtd_host_asset_reference_detects(self):
        html = (
            '<html><head><link rel="stylesheet" '
            'href="https://assets.readthedocs.org/theme.css"></head><body></body></html>'
        )
        assert ReadTheDocsProvider.detect("https://x.com/docs", html, None) is True

    def test_registry_chain_runs_on_root_fetch_failure(self, monkeypatch):
        """When the root fetch fails, every provider still gets to decide
        from its own signals before Generic wins."""
        from gitbook_downloader.providers.base import Provider as BaseProvider
        from gitbook_downloader.providers.base import ProviderRegistry

        calls = []

        class Probe(BaseProvider):
            name = "probe"
            priority = 50

            @classmethod
            def detect(cls, url, html, session):
                calls.append(html)
                return html == ""

            def extract_links(self, url, html, path_scope=None, exclude_paths=None):
                return set()

            def extract_content(self, url, session):
                return ""

        class Never(BaseProvider):
            name = "never"
            priority = 40

            @classmethod
            def detect(cls, url, html, session):
                return False

            def extract_links(self, url, html, path_scope=None, exclude_paths=None):
                return set()

            def extract_content(self, url, session):
                return ""

        class BoomSession:
            def get(self, *a, **k):
                raise IOError("down")

        monkeypatch.setattr(ProviderRegistry, "_providers", [Probe, Never])
        p = ProviderRegistry.detect("http://x.test/", BoomSession())
        assert calls == [""], "probe must run even though the root fetch failed"
        assert p.name == "probe"


class TestProviderExtractionParity:
    def test_mintlify_html_extraction(self, fixture_server, session):
        provider = MintlifyProvider()
        content = provider.extract_content(fixture_server.url("/mintlify"), session)
        assert content.strip() == _expected("mintlify_page.expected.md")

    def test_docusaurus_html_extraction(self, fixture_server, session):
        provider = DocusaurusProvider()
        content = provider.extract_content(fixture_server.url("/docusaurus"), session)
        assert content.strip() == _expected("docusaurus_page.expected.md")

    def test_readthedocs_html_extraction_keeps_page_header_content(
        self, fixture_server, session
    ):
        """div.page-header holds real content; only RTD chrome may be removed."""
        provider = ReadTheDocsProvider()
        content = provider.extract_content(fixture_server.url("/readthedocs"), session)
        assert content.strip() == _expected("readthedocs_page.expected.md")
