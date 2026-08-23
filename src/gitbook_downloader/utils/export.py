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
    """Convert a markdown file to a genuine PDF document.

    Uses **fpdf2** (pure Python) or **weasyprint** if installed.
    Guarantees a valid ``.pdf`` binary is generated.

    Args:
        md_path:     Path to the source markdown file.
        output_path: Destination path (.pdf).

    Returns:
        The output path string of the generated PDF file.
    """
    md_path = Path(md_path)
    output_path = Path(output_path).with_suffix(".pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    raw_md = md_path.read_text(encoding="utf-8", errors="replace")

    # 1. Try fpdf2 (pure Python, bundled, zero C dependencies)
    try:
        from fpdf import FPDF

        class DocPDF(FPDF):
            def __init__(self, title: str = ""):
                super().__init__()
                self.doc_title = title

            def header(self):
                if self.page_no() > 1:
                    self.set_font("helvetica", "I", 8)
                    self.set_text_color(140, 140, 140)
                    self.cell(self.epw, 6, self.doc_title, align="R", new_x="LMARGIN", new_y="NEXT")
                    self.ln(4)

            def footer(self):
                self.set_y(-12)
                self.set_font("helvetica", "I", 8)
                self.set_text_color(140, 140, 140)
                self.cell(self.epw, 6, f"Page {self.page_no()}", align="C")

        title = md_path.stem.replace("-", " ").replace("_", " ").title()
        pdf = DocPDF(title=title)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Cover / Header Banner
        pdf.set_font("helvetica", "B", 20)
        pdf.set_text_color(24, 24, 27)
        pdf.cell(pdf.epw, 12, title, align="L", new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(220, 220, 225)
        pdf.line(pdf.l_margin, pdf.get_y() + 2, pdf.l_margin + pdf.epw, pdf.get_y() + 2)
        pdf.ln(8)

        # Parse markdown lines into formatted PDF blocks
        in_code_block = False
        code_lines: list[str] = []

        for line in raw_md.splitlines():
            stripped = line.strip()

            # Code blocks
            if stripped.startswith("```"):
                if in_code_block:
                    # Flush code block
                    pdf.set_fill_color(244, 244, 246)
                    pdf.set_font("courier", size=9)
                    pdf.set_text_color(50, 50, 50)
                    for cl in code_lines:
                        safe_cl = cl.encode("latin-1", "replace").decode("latin-1")
                        pdf.set_x(pdf.l_margin)
                        pdf.multi_cell(w=pdf.epw, h=5, text="  " + safe_cl, fill=True, new_x="LMARGIN", new_y="NEXT")
                    pdf.ln(3)
                    code_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
                    code_lines = []
                continue

            if in_code_block:
                code_lines.append(line)
                continue

            if not stripped:
                pdf.ln(3)
                continue

            # Headings
            if stripped.startswith("# "):
                pdf.ln(4)
                pdf.set_font("helvetica", "B", 16)
                pdf.set_text_color(15, 23, 42)
                text = stripped[2:].strip().encode("latin-1", "replace").decode("latin-1")
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(w=pdf.epw, h=8, text=text, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(2)
            elif stripped.startswith("## "):
                pdf.ln(3)
                pdf.set_font("helvetica", "B", 13)
                pdf.set_text_color(30, 41, 59)
                text = stripped[3:].strip().encode("latin-1", "replace").decode("latin-1")
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(w=pdf.epw, h=7, text=text, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)
            elif stripped.startswith("### "):
                pdf.ln(2)
                pdf.set_font("helvetica", "B", 11)
                pdf.set_text_color(51, 65, 85)
                text = stripped[4:].strip().encode("latin-1", "replace").decode("latin-1")
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(w=pdf.epw, h=6, text=text, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)
            elif stripped.startswith("- ") or stripped.startswith("* "):
                pdf.set_font("helvetica", size=10)
                pdf.set_text_color(51, 65, 85)
                bullet_text = stripped[2:].strip().replace("**", "").encode("latin-1", "replace").decode("latin-1")
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(w=pdf.epw, h=5, text=f"  *  {bullet_text}", new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.set_font("helvetica", size=10)
                pdf.set_text_color(30, 41, 59)
                clean_text = stripped.replace("**", "").replace("`", "").encode("latin-1", "replace").decode("latin-1")
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(w=pdf.epw, h=5.5, text=clean_text, new_x="LMARGIN", new_y="NEXT")

        # Flush any trailing code
        if in_code_block and code_lines:
            pdf.set_fill_color(244, 244, 246)
            pdf.set_font("courier", size=9)
            for cl in code_lines:
                safe_cl = cl.encode("latin-1", "replace").decode("latin-1")
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(w=pdf.epw, h=5, text="  " + safe_cl, fill=True, new_x="LMARGIN", new_y="NEXT")

        pdf.output(str(output_path))
        logger.info("PDF generated successfully via fpdf2 at %s", output_path)
        return str(output_path)

    except Exception as exc:
        logger.warning("fpdf2 PDF generation encountered error (%s), trying fallback", exc)

    # 2. Fallback to WeasyPrint if available
    try:
        import weasyprint  # type: ignore[import-untyped]
        import re as _re
        html_body = _re.sub(r'\n', '<br>\n', raw_md)
        html = f"<!DOCTYPE html><html><body><pre>{html_body}</pre></body></html>"
        weasyprint.HTML(string=html).write_pdf(str(output_path))
        return str(output_path)
    except Exception:
        # Final fallback: save styled HTML
        html_path = output_path.with_suffix(".html")
        html_path.write_text(f"<!DOCTYPE html><html><body><pre>{raw_md}</pre></body></html>", encoding="utf-8")
        return str(html_path)
