"""
Download Engine — Simple BFS crawler proven to produce complete GitBook downloads.

This is the engine that produced the 39 MB / 1.6M line download of docs.openalgo.in.
It uses breadth-first crawling: start at the root, follow every internal link,
convert each page to clean markdown. No sitemaps, no threading, no complexity.
Just works.
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urljoin, urlparse


def download_docs(start_url, output_file, max_pages=500, quiet=False):
    """
    Download a complete GitBook documentation site.

    Args:
        start_url: The root URL of the GitBook site (e.g., https://docs.example.com/)
        output_file: Path to save the combined markdown file
        max_pages: Maximum number of pages to download (default 500)
        quiet: Suppress progress output

    Returns:
        Tuple of (pages_downloaded, errors_list)
    """
    def _normalize(u):
        """Remove fragments and trailing slashes for dedup."""
        p = urlparse(u)
        return urljoin(u, p.path.rstrip("/") or "/")

    visited = set()
    to_visit = [start_url]
    all_markdown = []
    base_domain = urlparse(start_url).netloc
    errors = []
    count = 0

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        norm = _normalize(url)
        if norm in visited:
            continue
        visited.add(norm)

        count += 1
        if not quiet:
            print(f"[{count}] Downloading: {url}")

        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code != 200:
                if not quiet:
                    print(f"  ⚠  Skipped (HTTP {resp.status_code})")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            # Clean: remove nav, footer, aside, scripts, styles
            for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
                tag.decompose()

            # Find main content container
            main = (
                soup.find("main")
                or soup.find("article")
                or soup.find("div", class_="content")
                or soup.body
            )
            html = str(main) if main else resp.text

            # Convert HTML to markdown
            markdown = md(html, heading_style="ATX")
            markdown = re.sub(r"\n\s*\n\s*\n", "\n\n", markdown)

            # Extract page title
            title = soup.find("h1")
            title_text = title.get_text().strip() if title else os.path.basename(url.rstrip("/")) or "Home"

            # Format: title + source URL + content + separator
            all_markdown.append(
                f"# {title_text}\n\nSource: {url}\n\n{markdown}\n\n---\n\n"
            )

            # Discover new links to visit
            for link in soup.find_all("a", href=True):
                href = link["href"]
                full_url = urljoin(url, href)
                parsed = urlparse(full_url)

                # Only follow internal links to new pages
                if (
                    parsed.netloc == base_domain
                    and _normalize(full_url) not in visited
                    and full_url not in to_visit
                ):
                    to_visit.append(full_url)

        except requests.Timeout:
            msg = f"Timeout: {url}"
            errors.append(msg)
            if not quiet:
                print(f"  ✕ {msg}")
        except requests.ConnectionError:
            msg = f"Connection failed: {url}"
            errors.append(msg)
            if not quiet:
                print(f"  ✕ {msg}")
        except Exception as e:
            msg = f"Error on {url}: {e}"
            errors.append(msg)
            if not quiet:
                print(f"  ✕ {msg}")

    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(all_markdown))

    if not quiet:
        total_kb = round(os.path.getsize(output_file) / 1024, 1)
        print(f"\n{'═' * 50}")
        print(f"  ✅ Done!")
        print(f"  📄 Pages: {len(visited)}")
        print(f"  📏 Size:  {total_kb} KB ({round(total_kb / 1024, 1)} MB)")
        print(f"  📂 Saved: {output_file}")
        if errors:
            print(f"  ⚠  Errors: {len(errors)}")
            for e in errors[:5]:
                print(f"     - {e}")
            if len(errors) > 5:
                print(f"     ... and {len(errors) - 5} more")
        print(f"{'═' * 50}\n")

    return len(visited), errors
