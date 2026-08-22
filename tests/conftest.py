"""Shared test configuration and fixtures.

Provides a local HTTP fixture server (random port, no live network) that
serves the frozen pages under ``tests/fixtures/``. ``{{BASE}}`` placeholders
inside fixture files are substituted with the server's own base URL so
absolute links in sitemaps/llms.txt always point back at the live server.
"""

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Request path -> (fixture filename, Content-Type)
ROUTES = {
    "/": ("landing.html", "text/html"),
    "/docs/intro": ("docs_intro.html", "text/html"),
    "/docs/guide": ("docs_guide.html", "text/html"),
    "/docs/excluded": ("docs_guide.html", "text/html"),
    "/docs/zh-cn/page": ("docs_guide.html", "text/html"),
    "/gitbook": ("gitbook_page.html", "text/html"),
    "/gitbook.md": ("gitbook_export.md", "text/plain; charset=utf-8"),
    "/mintlify": ("mintlify_page.html", "text/html"),
    "/docusaurus": ("docusaurus_page.html", "text/html"),
    "/readthedocs": ("readthedocs_page.html", "text/html"),
    "/sitemap.xml": ("sitemap.xml", "application/xml"),
    "/sub_sitemap.xml": ("sub_sitemap.xml", "application/xml"),
    "/sitemaps/index.xml": ("sitemap_index.xml", "application/xml"),
    "/llms.txt": ("llms.txt", "text/plain; charset=utf-8"),
    # Soft-200 trap: <url>.md returns 200 with an HTML shell (no doctype).
    "/spa/page": ("spa_page.html", "text/html"),
    "/spa/page.md": ("spa_page.md", "text/plain"),
    # Charset trap: UTF-8 bytes declared as iso-8859-1.
    "/charset": ("charset_page.html", "text/html; charset=iso-8859-1"),
}

# Paths whose responses carry deliberately wrong metadata.
_HEADER_OVERRIDES = {
    "/charset": {"Content-Type": "text/html; charset=iso-8859-1"},
}


class FixtureServer:
    """Tiny routing HTTP server over tests/fixtures/."""

    def __init__(self):
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), self._make_handler())
        self._server.daemon_threads = True
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    @property
    def base_url(self) -> str:
        host, port = self._server.server_address
        return f"http://{host}:{port}"

    def url(self, path: str) -> str:
        return self.base_url + path

    def _make_handler(self):
        def resolve(path: str):
            route = ROUTES.get(path)
            if route is None and path.endswith("/"):
                route = ROUTES.get(path.rstrip("/"))
            if route is None and path != "/" :
                route = ROUTES.get(path.rstrip("/") or "/")
            return route

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):  # silence test noise
                pass

            def _serve(self):
                path = self.path.split("?", 1)[0]
                route = resolve(path)
                if route is None:
                    self.send_response(404)
                    self.end_headers()
                    return
                filename, content_type = route
                raw = (FIXTURES_DIR / filename).read_bytes()
                base = f"http://{self.headers.get('Host', '127.0.0.1')}"
                text = raw.decode("utf-8").replace("{{BASE}}", base)
                body = text.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            do_GET = _serve
            do_HEAD = _serve

        return Handler

    def stop(self):
        self._server.shutdown()
        self._server.server_close()


@pytest.fixture(scope="session")
def fixture_server():
    """Session-scoped local doc-site fixture. Use ``server.url(path)``."""
    server = FixtureServer()
    yield server
    server.stop()
