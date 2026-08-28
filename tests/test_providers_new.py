"""Tests for new documentation providers: MkDocs, VitePress, Nextra, ReadMe, SPA detection, and renderer."""

import pytest
import requests
from unittest.mock import MagicMock

from gitbook_downloader.providers import (
    ProviderRegistry,
    MkDocsProvider,
    VitePressProvider,
    NextraProvider,
    ReadMeProvider,
    detect_provider,
)
from gitbook_downloader.providers.base import (
    looks_like_spa_shell,
    looks_like_challenge_or_blocked,
)
from gitbook_downloader.utils.renderer import HeadlessRenderer, is_render_available


def test_mkdocs_provider_detection():
    provider = MkDocsProvider()
    assert provider.name == "mkdocs"
    assert provider.priority == 70

    # HTML with MkDocs generator meta tag
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="generator" content="mkdocs-1.5.3, mkdocs-material-9.5.0">
        <title>MkDocs Material Test</title>
    </head>
    <body>
        <div class="md-content">
            <article class="md-content__inner md-typeset">
                <h1>MkDocs Header</h1>
                <p>MkDocs documentation body.</p>
            </article>
        </div>
    </body>
    </html>
    """
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "text/html"}

    mock_sess = MagicMock()
    mock_sess.get.return_value = mock_resp

    detected = provider.detect("https://squidfunk.github.io/mkdocs-material/", html, mock_sess)
    assert detected is True

    content = provider.extract_content("https://squidfunk.github.io/mkdocs-material/", mock_sess)
    assert "MkDocs Header" in content
    assert "MkDocs documentation body." in content


def test_vitepress_provider_detection():
    provider = VitePressProvider()
    assert provider.name == "vitepress"
    assert provider.priority == 72

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>VitePress Documentation</title>
    </head>
    <body>
        <div class="vp-doc _guide_getting-started">
            <div class="VPContent">
                <main class="VPDoc">
                    <div class="content-container">
                        <h1>Getting Started <a class="header-anchor" href="#getting-started">#</a></h1>
                        <p>Welcome to VitePress docs.</p>
                    </div>
                </main>
            </div>
        </div>
    </body>
    </html>
    """
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "text/html"}

    mock_sess = MagicMock()
    mock_sess.get.return_value = mock_resp

    detected = provider.detect("https://vitepress.dev/", html, mock_sess)
    assert detected is True

    content = provider.extract_content("https://vitepress.dev/", mock_sess)
    assert "Getting Started" in content
    assert "Welcome to VitePress docs." in content
    # Ensure header-anchor was stripped
    assert "#getting-started" not in content


def test_nextra_provider_detection():
    provider = NextraProvider()
    assert provider.name == "nextra"
    assert provider.priority == 75

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nextra Docs</title>
    </head>
    <body>
        <div id="__next">
            <div class="nextra-container">
                <main class="nextra-content">
                    <article>
                        <h1>Nextra Guide</h1>
                        <p>Simple, powerful and flexible site generation framework.</p>
                    </article>
                </main>
            </div>
        </div>
    </body>
    </html>
    """
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "text/html"}

    mock_sess = MagicMock()
    mock_sess.get.return_value = mock_resp

    detected = provider.detect("https://nextra.site/", html, mock_sess)
    assert detected is True

    content = provider.extract_content("https://nextra.site/", mock_sess)
    assert "Nextra Guide" in content
    assert "Simple, powerful and flexible" in content


def test_readme_provider_detection():
    provider = ReadMeProvider()
    assert provider.name == "readme"
    assert provider.priority == 65

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Reference &mdash; ReadMe</title>
    </head>
    <body class="theme-readme hub-reference">
        <div id="content" class="rm-Article">
            <header>
                <h1>Authentication Overview</h1>
            </header>
            <div class="rm-Markdown">
                <p>Pass your Bearer token in the Authorization header.</p>
            </div>
        </div>
    </body>
    </html>
    """
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "text/html"}

    mock_sess = MagicMock()
    mock_sess.get.return_value = mock_resp

    detected = provider.detect("https://docs.readme.com/reference", html, mock_sess)
    assert detected is True

    content = provider.extract_content("https://docs.readme.com/reference", mock_sess)
    assert "Authentication Overview" in content
    assert "Bearer token" in content


def test_looks_like_spa_shell():
    # Empty HTML with just root/app div and bundle script
    spa_html = """
    <!DOCTYPE html>
    <html>
    <head><title>SPA App</title></head>
    <body>
        <div id="root"></div>
        <script src="/static/js/bundle.js"></script>
    </body>
    </html>
    """
    assert looks_like_spa_shell(spa_html) is True

    # Real rich HTML
    rich_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Rich Documentation</title></head>
    <body>
        <h1>Documentation Title</h1>
        <p>""" + ("Detailed paragraph with extensive content describing the architecture. " * 10) + """</p>
    </body>
    </html>
    """
    assert looks_like_spa_shell(rich_html) is False


def test_looks_like_challenge_or_blocked():
    challenge_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Just a moment...</title></head>
    <body>
        <h2>Checking your browser before accessing the website.</h2>
        <div id="cf-wrapper">Cloudflare Ray ID: 123456789</div>
    </body>
    </html>
    """
    assert looks_like_challenge_or_blocked(challenge_html, 403) is True
    assert looks_like_challenge_or_blocked(challenge_html, 503) is True
    assert looks_like_challenge_or_blocked("<h1>Normal Doc</h1>", 200) is False


def test_renderer_availability():
    avail = is_render_available()
    assert isinstance(avail, bool)

    renderer = HeadlessRenderer(headless=True)
    assert renderer.headless is True
