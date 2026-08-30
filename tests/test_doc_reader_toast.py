"""DocReaderModal PDF-export toast regression.

The bridge returns ``res.path``, not ``res.file``. The modal used to read
``res.file`` so every PDF-export toast printed ``"undefined"``. This test
fails if that mistake returns.
"""

from __future__ import annotations

from pathlib import Path
import re

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_READER = REPO_ROOT / "frontend" / "src" / "components" / "DocReaderModal.tsx"
BRIDGE = REPO_ROOT / "frontend" / "src" / "lib" / "bridge.ts"
PY_BRIDGE = REPO_ROOT / "src" / "gitbook_downloader" / "gui" / "bridge.py"


def test_doc_reader_no_res_file_reference() -> None:
    """The PDF-export success toast must read ``res.path``, not ``res.file``."""
    text = DOC_READER.read_text(encoding="utf-8")
    # We allow `res.file` in OTHER contexts (e.g. res.success, res.format),
    # but the success-toast for PDF export must NOT use it.
    assert "res.file" not in text, (
        f"{DOC_READER.name} still references `res.file` in the PDF export "
        f"toast. The bridge returns `res.path` — using `res.file` produces "
        f"the literal string 'undefined' in the toast."
    )


def test_doc_reader_pdf_toast_uses_path() -> None:
    """Find the success-toast block and assert it interpolates ``res.path``."""
    text = DOC_READER.read_text(encoding="utf-8")
    # Locate the PDF export success toast context.
    match = re.search(
        r"pyApi\.exportDoc\([^)]*\)\.then\(\(res\)\s*=>\s*\{[^}]*toast\.success\(`PDF exported to: \$\{res\.(\w+)\}`",
        text,
        re.DOTALL,
    )
    assert match is not None, (
        f"{DOC_READER.name} should toast `PDF exported to: ${{res.path}}` on success"
    )
    assert match.group(1) == "path", (
        f"PDF export toast must read `res.path` (got `res.{match.group(1)}`)"
    )


def test_bridge_export_doc_returns_path_field() -> None:
    """The Python bridge's exportDoc must include a ``path`` field."""
    text = PY_BRIDGE.read_text(encoding="utf-8")
    # Find the export_doc method and look for "path" in its return dict.
    assert "def export_doc" in text, "Python bridge must define export_doc"
    # The contract is documented as a dict with `path`; the file should
    # contain at least one `"path"` literal within the export_doc method.
    method_start = text.index("def export_doc")
    # Use a generous slice to cover the whole method body.
    method_body = text[method_start : method_start + 4000]
    assert '"path"' in method_body or "'path'" in method_body, (
        "Python bridge.export_doc must return a dict that includes a `path` "
        "field (the frontend toast reads `res.path`)"
    )
