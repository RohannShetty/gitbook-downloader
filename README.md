<div align="center">

<img src="assets/logo-icon.svg" alt="DocHarvest Logo" width="96" />

# DocHarvest

### Turn Any Documentation Site into LLM-Ready Markdown, Vector Context & Offline Books

**Zero-Config CLI · React Desktop GUI · Native FastMCP Server · Pure-Python PDF Studio**

[![Version: 10.0.1](https://img.shields.io/badge/version-10.0.1-06b6d4?style=flat-square&labelColor=090d16)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-10b981?style=flat-square&labelColor=090d16)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3b82f6?style=flat-square&labelColor=090d16)](pyproject.toml)
[![UI: shadcn/ui](https://img.shields.io/badge/UI-shadcn%2Fui-27272a?style=flat-square&labelColor=090d16)](https://ui.shadcn.com)
[![MCP: Enabled](https://img.shields.io/badge/MCP-FastMCP%20Ready-8b5cf6?style=flat-square&labelColor=090d16)](#-ai-agent-integration-fastmcp-server)
[![Platform: Windows | Linux | macOS](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-64748b?style=flat-square&labelColor=090d16)](#)
[![PyPI](https://img.shields.io/pypi/v/gitbook-downloader?style=flat-square&labelColor=090d16&color=f59e0b)](https://pypi.org/project/gitbook-downloader/)
[![Showcase Website](https://img.shields.io/badge/website-Live%20Showcase-06b6d4?style=flat-square&labelColor=090d16)](https://rohannshetty.github.io/gitbook-downloader/)

<br />

<img src="assets/capture_studio.png" alt="DocHarvest Desktop GUI — Capture Studio with shadcn/ui, 60fps motion progress, radial gauge, and live terminal logs" width="920" />

</div>

---

## ⚡ Overview

**DocHarvest** (formerly `gitbook-downloader`) is a high-performance, local-first documentation compiler and AI context platform. It automatically detects documentation platforms (**GitBook**, **Mintlify**, **Docusaurus**, **Nextra**, **ReadMe.io**, **VitePress**, **MkDocs**, and custom HTML), bounds crawls strictly to documentation subpaths, extracts pristine markdown via direct `.md` endpoint probing and AST-based cleaning, and compiles structured output corpora.

Whether you are feeding 500-page API manuals to **Cursor / Claude Code**, building vector RAG pipelines with **LangChain & LlamaIndex**, reading offline on an airplane, or archiving technical libraries, DocHarvest delivers a deterministic, noise-free knowledge corpus in seconds.

---

## 🌟 Key Capabilities

- 🤖 **Zero-Noise LLM Context**: Probes native `.md` endpoints and cleans DOM trees, eliminating up to 89% of token-wasting navigation boilerplate, scripts, and cookie banners.
- 📦 **Four-Part Output Contract**: Every capture generates a modular `pages/` tree with SHA-256 YAML frontmatter, a consolidated `book.md` with TOC, a standardized `llms.txt` manifest, and search index records.
- 🚀 **AI Export Studio**: One-click export to **RAG JSONL** (for vector databases), **Pure-Python PDF** (syntax-highlighted printable handbooks via `fpdf2`), and **AST Markdown chunks**.
- 🔌 **Native FastMCP Server**: Built-in Model Context Protocol server exposing 8 tools for Cursor, Claude Code, Windsurf, and Claude Desktop.
- 🎨 **Modern Desktop GUI**: React + Tailwind CSS + shadcn/ui desktop application featuring real-time radial progress, in-app doc reader, document library renaming, and batch queues.
- 🔍 **SQLite FTS5 Full-Text Search**: Embedded BM25 search engine with `porter unicode61` stemming across all downloaded documentation.
- 🔒 **Process-Safe Storage & Diffs**: Active PID-validated `DomainLock`, atomic file staging (`os.replace` + `os.fsync`), and semver snapshot version diffing.
- 🛡️ **100% Local, Private & Free**: Zero cloud API fees, zero telemetry, air-gap ready, and MIT-licensed.

---

## 🖥️ Desktop GUI: Document Library & Management

<div align="center">
  <img src="assets/document_library.png" alt="DocHarvest Desktop GUI — Document Library with search, rename, open folder, and multi-format exports" width="920" />
</div>

The desktop application includes a dedicated **Document Library** for managing all harvested technical docs:
- **Instant Search**: Real-time filtering across downloaded portals.
- **In-App Renaming**: Organize project labels without breaking file paths.
- **1-Click Export Studio**: Export selected docsets to Markdown, Vector JSONL, or PDF handbooks directly from the GUI.
- **Direct Finder/Explorer Integration**: Open raw markdown source folders with a single click.

---

## 📋 The Four-Part Output Contract

Every crawl produces a standardized, deterministic directory structure:

```
data/
└── docs.openalgo.in/
    ├── pages/                     # Modular individual markdown files
    │   ├── 001_quickstart.md
    │   └── 002_api_reference.md
    ├── book.md                    # Consolidated single handbook with hierarchical TOC
    ├── llms.txt                   # Standardized AI discovery manifest
    ├── exports/
    │   ├── openalgo_rag.jsonl     # Tokenized vector chunks + SHA-256 metadata
    │   └── openalgo_handbook.pdf  # Publication-grade printable PDF (pure Python)
    └── .manifest.json             # Crawl metadata, engine version & cryptographic hashes
```

---

## 🚀 Quick Start

### Option 1: Standalone Desktop Application (Zero Setup)
Download **[`docharvest-windows-latest.exe`](https://github.com/RohannShetty/gitbook-downloader/releases/latest)** from the latest release:
- **Double-click** to launch the **Desktop GUI Application**.
- Or execute directly in terminal:
  ```powershell
  .\docharvest-windows-latest.exe crawl https://docs.openalgo.in/v/v2.0 --rag --pdf
  ```

### Option 2: Install via pip / PyPI
```bash
pip install gitbook-downloader

# Launch the desktop GUI:
docharvest --gui

# Or run a CLI crawl:
docharvest crawl https://docs.openalgo.in/ --rag --pdf
```

### Option 3: Ultra-Fast One-Liner via uv / uvx
```bash
# Launch GUI instantly without permanent installation:
uvx gitbook-downloader --gui

# Or install as a global tool:
uv tool install gitbook-downloader
```

### Option 4: Docker Container
```bash
docker run --rm -v $(pwd)/data:/app/data rohanshetty/docharvest crawl https://docs.openalgo.in/
```

---

## 🔌 AI Agent Integration (FastMCP Server)

DocHarvest includes a native **FastMCP (Model Context Protocol)** server over `stdio`, giving Cursor, Claude Code, and Windsurf direct documentation search and retrieval capabilities:

### Cursor IDE Configuration (`.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "docharvest": {
      "command": "python",
      "args": ["-m", "gitbook_downloader.mcp_server"]
    }
  }
}
```

### Claude Desktop Configuration (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "docharvest": {
      "command": "uvx",
      "args": ["gitbook-downloader", "--mcp"]
    }
  }
}
```

### Available Native MCP Tools
- `@docharvest_search(query, domain)` — Sub-15ms BM25 full-text keyword query across harvested docs.
- `@docharvest_read_page(url_or_path)` — Returns clean Markdown content for an article.
- `@docharvest_list_domains()` — Lists all local documentation portals and page counts.
- `@docharvest_crawl(url, max_pages)` — Dispatches an AST crawler on a documentation portal.
- `@docharvest_export_rag(domain)` — Generates vector chunks for LangChain/ChromaDB embedding.

---

## 📊 Feature Comparison Matrix

| Feature | DocHarvest v10.0.1 | Raw Scrapers (curl/Scrapy) | Cloud Reader APIs |
| :--- | :---: | :---: | :---: |
| **Native AST Platform Detection** (GitBook, Mintlify, Docusaurus, Nextra) | **✓ Yes** | ❌ No | Partial |
| **Direct `.md` Raw Endpoint Probing** | **✓ Yes** | ❌ No | ❌ No |
| **Zero HTML / Cookie Banner Noise** (89% token reduction) | **✓ Yes** | ❌ No | ✓ Yes |
| **Consolidated `book.md` with Auto TOC** | **✓ Yes** | ❌ No | ❌ No |
| **Standard `llms.txt` Generation** | **✓ Yes** | ❌ No | ❌ No |
| **Vector RAG JSONL Chunks** (cl100k/o200k compatible) | **✓ Yes** | ❌ No | ❌ No |
| **Pure-Python PDF Generation** (Zero C-deps) | **✓ Yes** | ❌ No | ❌ No |
| **Built-in FastMCP Server** (Cursor / Claude) | **✓ Yes** | ❌ No | Requires API Key |
| **Embedded SQLite FTS5 BM25 Search** | **✓ Yes** | ❌ No | ❌ No |
| **100% Free & Local Privacy** (Zero API cost) | **✓ Free (MIT)** | ✓ Free | ❌ Paid / Per-Page |

---

## 💻 CLI Command Reference

```bash
# Basic Documentation Crawl
docharvest crawl https://docs.openalgo.in/

# Full Compilation (Markdown + RAG JSONL + llms.txt + PDF)
docharvest crawl https://docs.openalgo.in/v/v2.0 --rag --pdf --fast-ast

# Search Downloaded Documentation via FTS5 BM25
docharvest search "OAuth 2.0 authentication token"

# Launch FastMCP Stdio Server for AI IDEs
docharvest --mcp

# Launch Desktop GUI Application
docharvest --gui
```

---

## 🐍 Python SDK Example

```python
from gitbook_downloader import DocHarvestEngine

# Initialize the harvester
engine = DocHarvestEngine(output_dir="./data")

# Crawl and compile documentation
result = engine.crawl(
    url="https://docs.openalgo.in/v/v2.0",
    export_rag=True,
    export_pdf=True
)

print(f"Harvested {result.total_pages} pages in {result.elapsed_seconds}s")
print(f"Consolidated handbook: {result.book_path}")
print(f"RAG JSONL dataset: {result.rag_jsonl_path}")
```

---

## 👨‍💻 Author & Connect

Created with ❤️ by **Rohan Shetty**.

- 🌐 **Website**: [rohannshetty.github.io/gitbook-downloader](https://rohannshetty.github.io/gitbook-downloader/)
- 🐙 **GitHub**: [@RohannShetty](https://github.com/RohannShetty)
- 💼 **LinkedIn**: [linkedin.com/in/rohan-shettyy](https://www.linkedin.com/in/rohan-shettyy/)
- 🐦 **X (Twitter)**: [@rohan__shetty](https://x.com/rohan__shetty)
- 📧 **Email**: [shettyrohan2@gmail.com](mailto:shettyrohan2@gmail.com)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
