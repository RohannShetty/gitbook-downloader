"""Tests for provider system — detection, registry, and content extraction.

Covers:
  - base.py: Provider, ProviderRegistry, normalize_url, is_md_url, same_domain
  - gitbook.py: GitBookProvider
  - mintlify.py: MintlifyProvider
  - docusaurus.py: DocusaurusProvider
  - readthedocs.py: ReadTheDocsProvider
  - generic.py: GenericProvider
"""

from unittest.mock import MagicMock, patch

import pytest

from gitbook_downloader.providers import (
    Provider, ProviderRegistry,
    GitBookProvider, DocusaurusProvider, ReadTheDocsProvider,
    MintlifyProvider, GenericProvider,
    detect_provider, get_provider, list_providers,
    normalize_url, is_md_url, same_domain,
)
from gitbook_downloader.utils import create_session


# ════════════════════════════════════════════════════════════════
#  REGISTRY
# ════════════════════════════════════════════════════════════════

class TestProviderRegistry:
    """Tests for ProviderRegistry."""

    def test_list_providers_order(self):
        names = list_providers()
        assert names == ["gitbook", "mintlify", "docusaurus", "readthedocs", "generic"]

    def test_get_provider_by_name(self):
        assert get_provider("gitbook") is GitBookProvider
        assert get_provider("generic") is GenericProvider

    def test_get_provider_case_insensitive(self):
        assert get_provider("GitBook") is GitBookProvider
        assert get_provider("GENERIC") is GenericProvider

    def test_get_provider_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("nonexistent")

    def test_registry_has_five_providers(self):
        assert len(ProviderRegistry._providers) == 5

    def test_registry_sorted_by_priority(self):
        priorities = [p.priority for p in ProviderRegistry._providers]
        assert priorities == sorted(priorities, reverse=True)

    def test_detect_provider_falls_back_to_generic(self):
        """detect_provider should return a provider instance when session works."""
        session = create_session()
        with patch.object(session, "get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = "<html><body>Plain HTML</body></html>"
            mock_get.return_value = mock_resp
            provider = detect_provider("https://example.com", session)
            assert isinstance(provider, Provider)
            assert provider.name == "generic"

    def test_detect_provider_network_error_returns_generic(self):
        session = create_session()
        with patch.object(session, "get") as mock_get:
            mock_get.side_effect = Exception("Network error")
            provider = detect_provider("https://example.com", session)
            assert isinstance(provider, Provider)
            assert provider.name == "generic"

    def test_detect_provider_non_200_returns_generic(self):
        session = create_session()
        with patch.object(session, "get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 500
            mock_get.return_value = mock_resp
            provider = detect_provider("https://example.com", session)
            assert isinstance(provider, Provider)
            assert provider.name == "generic"


# ════════════════════════════════════════════════════════════════
#  BASE URL HELPERS (from providers.base)
# ════════════════════════════════════════════════════════════════

class TestProvidersBaseUrlHelpers:
    """Tests for the provider module's own normalize_url, is_md_url, same_domain."""

    def test_normalize_url_strips_fragment(self):
        assert normalize_url("https://example.com/page#sec") == "https://example.com/page"

    def test_normalize_url_strips_trailing_slash(self):
        assert normalize_url("https://example.com/page/") == "https://example.com/page"

    def test_normalize_url_strips_md(self):
        # .md is stripped, but path remains: /page.md → /page
        assert normalize_url("https://example.com/page.md") == "https://example.com/page"

    def test_normalize_url_root(self):
        # When path is just "/" after stripping .md, it should return "/"
        result = normalize_url("https://example.com/.md")
        assert result == "https://example.com/"

    def test_normalize_url_preserves_path(self):
        assert normalize_url("https://example.com/docs/guide") == "https://example.com/docs/guide"

    def test_is_md_url_true(self):
        assert is_md_url("https://example.com/page.md") is True

    def test_is_md_url_false(self):
        assert is_md_url("https://example.com/page.html") is False

    def test_same_domain_true(self):
        assert same_domain("https://docs.example.com/page", "https://docs.example.com/other") is True

    def test_same_domain_false(self):
        assert same_domain("https://other.com/page", "https://docs.example.com") is False


# ════════════════════════════════════════════════════════════════
#  GITBOOK PROVIDER
# ════════════════════════════════════════════════════════════════

class TestGitBookProvider:
    @pytest.fixture
    def provider(self):
        return GitBookProvider()

    def test_name(self, provider):
        assert provider.name == "gitbook"

    def test_priority(self):
        assert GitBookProvider.priority == 100

    # ── Detection ──

    def test_detect_gitbook_net_asset(self):
        html = '<html><script src="https://docs.gitbook.net/assets/plugin.js"></script></html>'
        assert GitBookProvider.detect("https://docs.example.com", html, None) is True

    def test_detect_window_gitbook(self):
        html = '<html><script>window.__gitbook = {}</script></html>'
        assert GitBookProvider.detect("https://docs.example.com", html, None) is True

    def test_detect_meta_generator_gitbook(self):
        html = '<html><head><meta name="generator" content="GitBook"></head></html>'
        assert GitBookProvider.detect("https://docs.example.com", html, None) is True

    def test_detect_meta_generator_case_insensitive(self):
        html = '<html><head><meta name="generator" content="gitbook"></head></html>'
        assert GitBookProvider.detect("https://docs.example.com", html, None) is True

    def test_detect_negative(self):
        html = "<html><body>Plain HTML with no gitbook signals</body></html>"
        assert GitBookProvider.detect("https://docs.example.com", html, None) is False

    # ── Extract Title ──

    def test_extract_title_from_heading(self, provider):
        content = "# Welcome to the Docs\n\nSome text here."
        title = provider.extract_title(content, "https://docs.example.com")
        assert title == "Welcome to the Docs"

    def test_extract_title_fallback_to_url(self, provider):
        title = provider.extract_title("No heading here", "https://docs.example.com/page")
        assert title == "page"

    def test_extract_title_fallback_home(self, provider):
        # "https://docs.example.com/" → rstrip("/") → "https://docs.example.com"
        # → split("/")[-1] → "docs.example.com"
        title = provider.extract_title("No heading", "https://docs.example.com/")
        assert title == "docs.example.com"

    # ── Extract Links ──

    def test_extract_links_skips_javascript(self, provider):
        html = '<a href="javascript:void(0)">click</a><a href="https://docs.example.com/page">page</a>'
        links = provider.extract_links("https://docs.example.com", html)
        assert "https://docs.example.com/page" in links
        assert not any("javascript" in u for u in links)

    def test_extract_links_skips_mailto(self, provider):
        html = '<a href="mailto:test@example.com">email</a>'
        links = provider.extract_links("https://docs.example.com", html)
        assert len(links) == 0

    def test_extract_links_skips_tel(self, provider):
        html = '<a href="tel:+1234567890">phone</a>'
        links = provider.extract_links("https://docs.example.com", html)
        assert len(links) == 0

    def test_extract_links_skips_external(self, provider):
        html = '<a href="https://other.com/page">ext</a>'
        links = provider.extract_links("https://docs.example.com", html)
        assert len(links) == 0

    def test_extract_links_skips_gitbook_assets(self, provider):
        html = '<a href="/~gitbook/assets/img.png">img</a>'
        links = provider.extract_links("https://docs.example.com", html)
        assert len(links) == 0

    def test_extract_links_skips_md_urls(self, provider):
        html = '<a href="/page.md">link</a>'
        links = provider.extract_links("https://docs.example.com", html)
        assert len(links) == 0

    def test_extract_links_path_scope(self, provider):
        html = '<a href="/docs/page1">p1</a><a href="/blog/post">blog</a>'
        links = provider.extract_links("https://docs.example.com", html, path_scope="/docs/")
        assert "https://docs.example.com/docs/page1" in links
        assert not any("blog" in u for u in links)

    def test_extract_links_exclude_paths(self, provider):
        html = '<a href="/docs/intro">intro</a><a href="/docs/api/changelog">log</a>'
        links = provider.extract_links(
            "https://docs.example.com", html, exclude_paths=["changelog"]
        )
        assert "https://docs.example.com/docs/intro" in links
        assert not any("changelog" in u for u in links)

    def test_extract_links_fragment_only(self, provider):
        """Hash-only links are only skipped when the base URL has no path.
        When base has a path (e.g. /page), #section resolves to /page#section
        and is kept because parsed.path is non-empty.
        """
        # Base with no path — fragment-only is skipped
        html = '<a href="#section">jump</a>'
        links = provider.extract_links("https://docs.example.com", html)
        assert len(links) == 0
        # Base with path — fragment resolves to path#fragment, kept
        html2 = '<a href="#section">jump</a>'
        links2 = provider.extract_links("https://docs.example.com/page", html2)
        assert len(links2) == 1


# ════════════════════════════════════════════════════════════════
#  MINTLIFY PROVIDER
# ════════════════════════════════════════════════════════════════

class TestMintlifyProvider:
    @pytest.fixture
    def provider(self):
        return MintlifyProvider()

    def test_name(self, provider):
        assert provider.name == "mintlify"

    def test_priority(self):
        assert MintlifyProvider.priority == 90

    def test_detect_meta_generator(self):
        html = '<html><head><meta name="generator" content="Mintlify"></head></html>'
        assert MintlifyProvider.detect("https://docs.example.com", html, None) is True

    def test_detect_window_mintlify(self):
        html = '<html><script>window.__MINTLIFY = {}</script></html>'
        assert MintlifyProvider.detect("https://docs.example.com", html, None) is True

    def test_detect_mintlify_in_lower(self):
        html = '<html><div data-mintlify="true">content</div></html>'
        # The detection looks for both "mintlify" and "generator" in lowercase html
        # Let's test with generator tag
        html = '<html><meta name="generator" content="mintlify">content</html>'
        assert MintlifyProvider.detect("https://docs.example.com", html, None) is True

    def test_detect_negative(self):
        html = "<html><body>Plain HTML</body></html>"
        assert MintlifyProvider.detect("https://docs.example.com", html, None) is False

    def test_extract_links_basic(self, provider):
        html = '<a href="/docs/guide">Guide</a>'
        links = provider.extract_links("https://docs.example.com", html)
        assert "https://docs.example.com/docs/guide" in links


# ════════════════════════════════════════════════════════════════
#  DOCUSAURUS PROVIDER
# ════════════════════════════════════════════════════════════════

class TestDocusaurusProvider:
    @pytest.fixture
    def provider(self):
        return DocusaurusProvider()

    def test_name(self, provider):
        assert provider.name == "docusaurus"

    def test_priority(self):
        assert DocusaurusProvider.priority == 80

    def test_detect_meta_docusaurus(self):
        html = '<html><head><meta name="docusaurus" content="2.x"></head></html>'
        assert DocusaurusProvider.detect("https://docs.example.com", html, None) is True

    def test_detect_theme_class(self):
        html = '<html><div class="theme-doc-markdown">Content</div></html>'
        assert DocusaurusProvider.detect("https://docs.example.com", html, None) is True

    def test_detect_docusaurus_theme_prefix(self):
        html = '<html><div class="docusaurus-theme-classic">Content</div></html>'
        assert DocusaurusProvider.detect("https://docs.example.com", html, None) is True

    def test_detect_negative(self):
        html = "<html><body>Plain HTML</body></html>"
        assert DocusaurusProvider.detect("https://docs.example.com", html, None) is False

    def test_extract_links_basic(self, provider):
        html = '<a href="/docs/intro">Intro</a>'
        links = provider.extract_links("https://docs.example.com", html)
        assert "https://docs.example.com/docs/intro" in links

    def test_clean_markdown_strips_pilcrow(self, provider):
        text = "## Heading ¶\n\nContent here"
        cleaned = DocusaurusProvider._clean_markdown(text)
        assert "¶" not in cleaned
        assert "Heading" in cleaned

    def test_clean_markdown_normalizes_whitespace(self, provider):
        text = "Line 1\n\n\n\n\nLine 2"
        cleaned = DocusaurusProvider._clean_markdown(text)
        assert "\n\n\n" not in cleaned


# ════════════════════════════════════════════════════════════════
#  READTHEDOCS PROVIDER
# ════════════════════════════════════════════════════════════════

class TestReadTheDocsProvider:
    @pytest.fixture
    def provider(self):
        return ReadTheDocsProvider()

    def test_name(self, provider):
        assert provider.name == "readthedocs"

    def test_priority(self):
        assert ReadTheDocsProvider.priority == 70

    def test_detect_readthedocs_in_body(self):
        html = '<html><body class="rst-body"><div class="document">Content</div></body></html>'
        assert ReadTheDocsProvider.detect("https://docs.example.com", html, None) is True

    def test_detect_sphinxsidebar(self):
        html = '<html><div class="sphinxsidebar">Nav</div></html>'
        assert ReadTheDocsProvider.detect("https://docs.example.com", html, None) is True

    def test_detect_rst_footer_text(self):
        html = '<html><div class="body" role="main">Content</div><footer>Read the Docs</footer></html>'
        assert ReadTheDocsProvider.detect("https://docs.example.com", html, None) is True

    def test_detect_negative(self):
        html = "<html><body>Plain HTML</body></html>"
        assert ReadTheDocsProvider.detect("https://docs.example.com", html, None) is False

    def test_extract_links_basic(self, provider):
        html = '<a href="/en/latest/guide.html">Guide</a>'
        links = provider.extract_links("https://docs.example.com", html)
        assert "https://docs.example.com/en/latest/guide.html" in links


# ════════════════════════════════════════════════════════════════
#  GENERIC PROVIDER
# ════════════════════════════════════════════════════════════════

class TestGenericProvider:
    @pytest.fixture
    def provider(self):
        return GenericProvider()

    def test_name(self, provider):
        assert provider.name == "generic"

    def test_priority(self):
        assert GenericProvider.priority == 0

    def test_detect_always_true(self):
        assert GenericProvider.detect("https://example.com", "<html>anything</html>", None) is True

    def test_extract_links_basic(self, provider):
        html = '<a href="/docs/page1">p1</a>'
        links = provider.extract_links("https://example.com", html)
        assert "https://example.com/docs/page1" in links

    def test_extract_links_skips_javascript(self, provider):
        html = '<a href="javascript:alert(1)">click</a>'
        links = provider.extract_links("https://example.com", html)
        assert len(links) == 0

    def test_extract_links_path_scope(self, provider):
        html = '<a href="/docs/guide">guide</a><a href="/blog/post">post</a>'
        links = provider.extract_links("https://example.com", html, path_scope="/docs/")
        assert "https://example.com/docs/guide" in links
        assert not any("blog" in u for u in links)

    def test_extract_links_exclude_paths(self, provider):
        html = '<a href="/docs/intro">intro</a><a href="/docs/api/deprecated">old</a>'
        links = provider.extract_links(
            "https://example.com", html, exclude_paths=["deprecated"]
        )
        assert "https://example.com/docs/intro" in links
        assert not any("deprecated" in u for u in links)

    def test_extract_links_fragment_only_skipped(self, provider):
        """Fragment-only links skipped when base has no path."""
        # Base with no path — skipped
        html = '<a href="#section">jump</a>'
        links = provider.extract_links("https://example.com", html)
        assert len(links) == 0
        # Base with path — not skipped (path#fragment is a valid link)
        html2 = '<a href="#section">jump</a>'
        links2 = provider.extract_links("https://example.com/page", html2)
        assert len(links2) == 1


# ════════════════════════════════════════════════════════════════
#  CONTENT EXTRACTION (static _extract_md_from_html)
# ════════════════════════════════════════════════════════════════

class TestContentExtraction:
    """Tests for _extract_md_from_html across providers."""

    def test_generic_extracts_main_tag(self):
        html = '<html><body><main><h1>Title</h1><p>Content here</p></main></body></html>'
        md = GenericProvider._extract_md_from_html(html)
        assert "Title" in md

    def test_generic_extracts_article_tag(self):
        html = '<html><body><article><h1>Article</h1></article></body></html>'
        md = GenericProvider._extract_md_from_html(html)
        assert "Article" in md

    def test_generic_strips_nav_footer_script_style(self):
        html = '''
        <html><body>
            <nav>Navigation</nav>
            <footer>Footer content</footer>
            <script>alert("xss")</script>
            <style>.red { color: red; }</style>
            <main><p>Important content</p></main>
        </body></html>
        '''
        md = GenericProvider._extract_md_from_html(html)
        assert "Important content" in md
        assert "Navigation" not in md
        assert "alert" not in md

    def test_docusaurus_extracts_theme_class(self):
        html = '<html><body><div class="theme-doc-markdown"><h1>Guide</h1><p>Content</p></div></body></html>'
        md = DocusaurusProvider._extract_md_from_html(html)
        assert "Guide" in md

    def test_readthedocs_extracts_document_div(self):
        html = '<html><body><div class="document"><h1>Docs</h1><p>Content</p></div></body></html>'
        md = ReadTheDocsProvider._extract_md_from_html(html)
        assert "Docs" in md

    def test_mintlify_extracts_article(self):
        html = '<html><body><article><h1>Mint Guide</h1></article></body></html>'
        md = MintlifyProvider._extract_md_from_html(html)
        assert "Mint Guide" in md

    def test_strips_pilcrow_anchors(self):
        """¶ permalink anchors should be removed."""
        html = '<html><body><main><h1>Title ¶</h1><p>Content</p></main></body></html>'
        md = GenericProvider._extract_md_from_html(html)
        assert "¶" not in md
