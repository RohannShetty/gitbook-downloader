"""
Headless browser rendering module for client-rendered documentation sites (SPAs).

Optional dependency: playwright (``pip install gitbook-downloader[render]``).
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger("gitbook_downloader.render")


def is_render_available() -> bool:
    """Return True if Playwright is installed and importable."""
    try:
        import playwright.sync_api  # noqa: F401
        return True
    except ImportError:
        return False


class HeadlessRenderer:
    """Headless browser renderer using Playwright for client-rendered documentation."""

    def __init__(self, headless: bool = True, browser_type: str = "chromium") -> None:
        self.headless = headless
        self.browser_type = browser_type

    def render_url(
        self,
        url: str,
        timeout_ms: int = 25000,
        wait_selector: Optional[str] = None,
    ) -> str:
        """Render a URL using headless Chromium and return fully populated DOM HTML.

        Args:
            url: Page URL to fetch and render.
            timeout_ms: Maximum wait time in milliseconds.
            wait_selector: Optional CSS selector to wait for (e.g. "main, article").

        Returns:
            Rendered HTML string from the page.
        """
        if not is_render_available():
            raise RuntimeError(
                "Headless rendering requires Playwright. Install it with: "
                'pip install "gitbook-downloader[render]" && playwright install chromium'
            )

        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser_launcher = getattr(p, self.browser_type, p.chromium)
            browser = browser_launcher.launch(headless=self.headless)
            try:
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1280, "height": 800},
                )
                page = context.new_page()
                page.set_default_timeout(timeout_ms)

                # Navigate with domcontentloaded
                page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)

                # Wait for network idle state (essential for client-rendered React/Vite SPAs)
                try:
                    page.wait_for_load_state("networkidle", timeout=min(timeout_ms, 8000))
                except Exception:
                    pass

                # Wait for main content selector or populated text
                if wait_selector:
                    try:
                        page.wait_for_selector(wait_selector, timeout=min(timeout_ms, 6000))
                    except Exception:
                        pass
                else:
                    try:
                        page.wait_for_function(
                            "() => (document.querySelector('main, article, div.content, div.md-content, [role=\"main\"], div#root')?.innerText?.trim().length || 0) > 60",
                            timeout=min(timeout_ms, 6000),
                        )
                    except Exception:
                        pass

                return page.content()
            finally:
                browser.close()
