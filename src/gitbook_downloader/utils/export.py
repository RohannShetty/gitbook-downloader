"""Export utilities for different output formats.

Provides helpers for adding RAG metadata to chunks, exporting stored
pages to JSONL, and converting markdown to PDF (with graceful fallback).
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def wrap_with_rag_metadata(
    content: str,
    domain: str,
    url: str,
    headings: list[str] | None = None,
    chunk_num: int = 1,
    total_chunks: int = 1,
) -> str:
    """Prepend an HTML-comment metadata block to *content* for RAG pipelines.

    The metadata block is machine-readable and invisible in rendered HTML/
    Markdown.  Format::

        <!-- domain: docs.example.com, source: https://..., chunk: 1/3, headings: [H1, H2] -->
        <actual content>

    Args:
        content:      The text/markdown content to wrap.
        domain:       The documentation domain (e.g. ``docs.example.com``).
        url:          Source URL of the page.
        headings:     Optional list of heading strings from the page.
        chunk_num:    1-based index of this chunk within the page.
        total_chunks: Total number of chunks the page was split into.

    Returns:
        The content with a prepended metadata comment.
    """
    headings_str = ", ".join(headings) if headings else "none"
    meta = (
        f"<!-- domain: {domain}, source: {url}, "
        f"chunk: {chunk_num}/{total_chunks}, "
        f"headings: [{headings_str}] -->"
    )
    return f"{meta}\n{content}"


def export_to_jsonl(
    domain: str,
    storage_manager: Any,
    output_path: str | Path,
) -> None:
    """Export all stored pages for *domain* to a JSONL file.

    Each line is a JSON object::

        {"id": url, "title": title, "text": content, "metadata": {"domain": domain, ...}}

    Args:
        domain:         The documentation domain key.
        storage_manager: An object with a ``get_pages(domain)`` method that
                         yields dicts with at least ``url``, ``title``, and
                         ``content`` keys.  If it exposes a ``close()`` method
                         it will be called when done.
        output_path:    Destination file path for the JSONL output.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    try:
        pages = storage_manager.get_pages(domain)
    except AttributeError:
        logger.error("storage_manager has no get_pages() method")
        return
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to fetch pages for domain %s: %s", domain, exc)
        return

    with open(output_path, "w", encoding="utf-8") as fh:
        for page in pages:
            record = {
                "id": page.get("url", ""),
                "title": page.get("title", ""),
                "text": page.get("content", ""),
                "metadata": {
                    "domain": domain,
                    "source": page.get("url", ""),
                },
            }
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    # Cleanup if the storage_manager supports it
    close_fn = getattr(storage_manager, "close", None)
    if callable(close_fn):
        close_fn()

    logger.info("Exported %d pages to %s", count, output_path)


def export_to_pdf(md_path: str | Path, output_path: str | Path) -> str:
    """Convert a markdown file to PDF (with HTML fallback).

    Attempts to use **weasyprint** for real PDF rendering.  If weasyprint is
    not installed the function saves a standalone HTML file instead and returns
    an informational message.

    Args:
        md_path:     Path to the source markdown file.
        output_path: Destination path.  The ``.pdf`` / ``.html`` extension
                     will be applied automatically if missing.

    Returns:
        A status message string.  On success with PDF: the output path.
        On HTML fallback: a note that weasyprint is required.
    """
    md_path = Path(md_path)
    output_path = Path(output_path)

    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    raw_md = md_path.read_text(encoding="utf-8")

    # ── Build a minimal HTML page from the markdown ──
    # We do a lightweight conversion here to avoid a heavy dependency;
    # the caller can preprocess with markdownify if richer rendering is wanted.
    import re as _re

    html_body = raw_md
    # Headings
    html_body = _re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_body, flags=_re.MULTILINE)
    html_body = _re.sub(r'^## (.+)$',  r'<h2>\1</h2>', html_body, flags=_re.MULTILINE)
    html_body = _re.sub(r'^# (.+)$',   r'<h1>\1</h1>', html_body, flags=_re.MULTILINE)
    # Bold / italic
    html_body = _re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_body)
    html_body = _re.sub(r'\*(.+?)\*',     r'<em>\1</em>', html_body)
    # Code blocks
    html_body = _re.sub(r'```(\w*)\n(.*?)```', r'<pre><code>\2</code></pre>', html_body, flags=_re.DOTALL)
    # Inline code
    html_body = _re.sub(r'`([^`]+)`', r'<code>\1</code>', html_body)
    # Paragraphs (double newline)
    html_body = _re.sub(r'\n\n+', '</p><p>', html_body)
    html_body = f'<p>{html_body}</p>'
    # Single newlines → <br>
    html_body = _re.sub(r'\n', '<br>\n', html_body)

    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{md_path.stem}</title>
<style>
  body {{ font-family: sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; }}
  pre {{ background: #f4f4f4; padding: 1rem; overflow-x: auto; border-radius: 4px; }}
  code {{ background: #f4f4f4; padding: 0.15em 0.3em; border-radius: 3px; }}
  pre code {{ background: none; padding: 0; }}
  h1, h2, h3 {{ margin-top: 1.5em; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

    # ── Try to render PDF with weasyprint ──
    try:
        import weasyprint  # type: ignore[import-untyped]
        pdf_path = output_path.with_suffix(".pdf")
        weasyprint.HTML(string=html).write_pdf(str(pdf_path))
        logger.info("PDF exported to %s", pdf_path)
        return str(pdf_path)
    except ImportError:
        # Save as HTML fallback
        html_path = output_path.with_suffix(".html")
        html_path.write_text(html, encoding="utf-8")
        msg = (
            f"PDF export requires weasyprint (pip install weasyprint). "
            f"HTML file saved instead: {html_path}"
        )
        logger.warning(msg)
        return msg
    except Exception as exc:  # noqa: BLE001
        # weasyprint installed but failed (missing system libs, etc.)
        html_path = output_path.with_suffix(".html")
        html_path.write_text(html, encoding="utf-8")
        msg = (
            f"PDF rendering failed ({exc}). "
            f"HTML file saved instead: {html_path}"
        )
        logger.warning(msg)
        return msg
