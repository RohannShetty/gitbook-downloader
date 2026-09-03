"""Tests for advanced MCP tools (find_docs, read_doc) and AST topic extraction.

Follows TDD discipline: verifies library resolution, granular page reading,
AST-safe token budget extraction, and error handling.
"""

from __future__ import annotations

import asyncio
import pytest
from pathlib import Path

from gitbook_downloader.splitter import extract_topic_context
from gitbook_downloader.storage.manager import StorageManager


def test_extract_topic_context_basic():
    markdown = """# React Documentation

## Quickstart
Get started with React by installing it.
```bash
npm install react react-dom
```

## Hooks
Hooks let you use state and other React features.

### useState
`useState` is a React Hook that lets you add a state variable to your component.
```jsx
const [state, setState] = useState(initialState);
```
Here is an explanation of useState.

## Components
Components are the building blocks of any React application.
"""
    # Filter by topic "useState"
    result = extract_topic_context(markdown, topic="useState", max_tokens=1000)
    assert "useState" in result
    assert "npm install" not in result  # Should prioritize the matching topic section
    assert "```jsx\nconst [state, setState] = useState(initialState);\n```" in result


def test_extract_topic_context_never_slices_code_blocks():
    markdown = """# Long Topic

## Details
Some intro text before the block.

```python
def very_long_function():
    # line 1
    # line 2
    # line 3
    # line 4
    return True
```

Footer text after block.
"""
    # Constrain tokens so it must cut, but ensure code fence is never broken mid-block
    result = extract_topic_context(markdown, topic="Details", max_tokens=40)
    # Either the full block is kept or omitted cleanly; if opening fence exists, closing fence must exist
    if "```" in result:
        assert result.count("```") % 2 == 0


def test_storage_load_and_list_pages(tmp_path: Path):
    storage = StorageManager(base_dir=tmp_path)
    domain = "test-lib.dev"
    domain_dir = storage._domain_dir(domain)
    pages_dir = domain_dir / "pages"
    pages_dir.mkdir(parents=True)

    page1 = pages_dir / "index.md"
    page1.write_text("# Home Page\nWelcome to docs.", encoding="utf-8")

    sub_dir = pages_dir / "guide"
    sub_dir.mkdir()
    page2 = sub_dir / "setup.md"
    page2.write_text("# Setup\nRun setup steps.", encoding="utf-8")

    pages = storage.list_pages(domain)
    assert "index.md" in pages
    assert "guide/setup.md" in [p.replace("\\", "/") for p in pages]

    content = storage.load_page(domain, "guide/setup.md")
    assert content is not None
    assert "Run setup steps" in content

    # Nonexistent page
    assert storage.load_page(domain, "nonexistent.md") is None


@pytest.mark.asyncio
async def test_find_docs_and_read_doc_mcp_tools(tmp_path: Path, monkeypatch):
    import gitbook_downloader.mcp.server as mcp_server

    fake_storage = StorageManager(base_dir=tmp_path)
    monkeypatch.setattr(mcp_server, "_storage", fake_storage)

    # Populate a fake domain in storage
    domain = "zustand.pmnd.rs"
    domain_dir = fake_storage._domain_dir(domain)
    pages_dir = domain_dir / "pages"
    pages_dir.mkdir(parents=True)

    book = domain_dir / "docs.md"
    book.write_text(
        "# Zustand Docs\n\n## Getting Started\nInstall zustand.\n\n## Hooks\nUse create for stores.\n```ts\nconst useStore = create(...)\n```",
        encoding="utf-8"
    )

    page = pages_dir / "intro.md"
    page.write_text("# Intro to Zustand\nState management simplified.", encoding="utf-8")

    fake_storage._write_metadata(domain, {
        "domain": domain,
        "title": "Zustand State Library",
        "pages": 2,
        "last_crawled": "2026-09-01T10:00:00Z"
    })

    # Test find_docs
    matches = await mcp_server.find_docs("zustand")
    assert len(matches) >= 1
    assert matches[0]["domain"] == "zustand.pmnd.rs"

    # Test read_doc by path
    page_res = await mcp_server.read_doc("zustand.pmnd.rs", path="intro.md")
    assert page_res.get("found") is True
    assert "State management simplified" in page_res.get("content", "")

    # Test read_doc by topic
    topic_res = await mcp_server.read_doc("zustand.pmnd.rs", topic="Hooks")
    assert topic_res.get("found") is True
    assert "const useStore = create" in topic_res.get("content", "")

    # Test read_doc nonexistent
    missing_res = await mcp_server.read_doc("nonexistent.com")
    assert missing_res.get("found") is False
    assert "error" in missing_res
