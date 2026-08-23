<div align="center">

<img src="assets/logo-icon.svg" alt="DocHarvest logo — universal documentation harvester" width="96" />

# DocHarvest

### Turn Any Documentation Site into LLM-Ready Markdown, Vector Context & Offline Books

**Zero-Config CLI · React Desktop GUI · Native FastMCP Server · Pure-Python PDF Studio**

[![Version: 10.0.1](https://img.shields.io/badge/version-10.0.1-06b6d4?style=flat-square&labelColor=090d16)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-10b981?style=flat-square&labelColor=090d16)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3b82f6?style=flat-square&labelColor=090d16)](pyproject.toml)
[![UI: shadcn/ui](https://img.shields.io/badge/UI-shadcn%2Fui-27272a?style=flat-square&labelColor=090d16)](https://ui.shadcn.com)
[![MCP: Enabled](https://img.shields.io/badge/MCP-Enabled-8b5cf6?style=flat-square&labelColor=090d16)](#-ai-agent-integration-fastmcp-server)
[![Platform: Windows | Linux | macOS](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-64748b?style=flat-square&labelColor=090d16)](#)
[![PyPI](https://img.shields.io/pypi/v/gitbook-downloader?style=flat-square&labelColor=090d16&color=f59e0b)](https://pypi.org/project/gitbook-downloader/)
[![CI Status](https://img.shields.io/github/actions/workflow/status/RohannShetty/gitbook-downloader/ci.yml?branch=main&style=flat-square&labelColor=090d16)](https://github.com/RohannShetty/gitbook-downloader/actions)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-06b6d4?style=flat-square&labelColor=090d16)](https://rohannshetty.github.io/gitbook-downloader/)

<br />

<img src="assets/capture_studio.png" alt="DocHarvest Desktop GUI — Capture Studio with shadcn/ui, 60fps motion progress, radial gauge, and live terminal logs" width="920" />

</div>

---

## ⚡ Overview

**DocHarvest** (formerly `gitbook-downloader`) is a high-performance, local-first documentation compiler and AI context platform. It automatically detects documentation platforms (GitBook, Mintlify, Docusaurus, ReadTheDocs, Nextra, VitePress, and custom HTML), bounds crawls strictly to documentation roots, extracts pristine markdown via direct `.md` endpoint probing and AST-based cleaning, and compiles structured output corpora.

Whether you are feeding 500-page API manuals to **Cursor / Claude Code**, building vector RAG pipelines with **LangChain & LlamaIndex**, reading offline on an airplane, or archiving technical libraries, DocHarvest delivers a deterministic, noise-free knowledge corpus in seconds.

---

## 🌟 Key Capabilities

- 🤖 **Zero-Noise LLM Context**: Probes native `.md` endpoints and cleans DOM trees, eliminating up to 85% of token-wasting navigation boilerplate, scripts, and cookie banners.
- 📦 **Four-Part Output Contract**: Every capture generates a modular `pages/` tree with SHA-256 YAML frontmatter, a consolidated `book.md` with TOC, a standardized `llms.txt` manifest, and search index records.
- 🚀 **AI Export Studio**: One-click export to **RAG JSONL** (for vector databases), **Pure-Python PDF** (syntax-highlighted printable handbooks via `fpdf2`), and **AST Markdown chunks** (`splitter.py`).
- 🔌 **Native FastMCP Server**: Built-in Model Context Protocol server exposing 8 tools for Cursor, Claude Code, Windsurf, and Claude Desktop.
- 🎨 **Modern Desktop GUI**: React 18 + Tailwind CSS + shadcn/ui desktop application featuring real-time radial progress, in-app doc reader, and batch queue.
- 🔍 **SQLite FTS5 Full-Text Search**: Embedded BM25 search engine with `porter unicode61` stemming across all downloaded documentation.
- 🔒 **Process-Safe Storage & Diffs**: Active PID-validated `DomainLock`, atomic file staging (`os.replace` + `os.fsync`), and semver snapshot version diffing (`gitbook-dl diff domain v1.0.0 v1.0.1`).
- 🛡️ **100% Local, Private & Free**: Zero cloud API fees, zero telemetry, air-gap ready, and MIT-licensed.

---

## 🚀 Quick Start

### Option 1: Standalone Desktop Application (Zero Setup)
Download **[`gitbook-dl.exe`](https://github.com/RohannShetty/gitbook-downloader/releases)** from the latest release:
- **Double-click** to launch the **Desktop GUI Application**.
- Or execute directly in terminal:
  ```bash
  .\gitbook-dl.exe capture https://docs.openalgo.in/ --export jsonl,pdf
  ```

### Option 2: Install via pip / uv
```bash
# Install via PyPI
pip install gitbook-downloader

# Or install latest directly from GitHub
pip install git+https://github.com/RohannShetty/gitbook-downloader.git
```

Launch the GUI or CLI:
```bash
# Launch Modern Desktop GUI
gitbook-dl

# Or run terminal capture with RAG & PDF exports
gitbook-dl capture https://docs.example.com --export jsonl,pdf
```

---

## 📦 The Four-Part Output Contract

Every capture adheres to a deterministic four-part directory structure:

```text
~/.gitbook-downloader/library/docs.example.com/
├── pages/                                 # 1. Modular Markdown Page Tree
│   ├── getting-started/
│   │   ├── overview.md                    # Prepend SHA-256 YAML frontmatter
│   │   └── installation.md
│   └── api/
│       ├── authentication.md
│       └── endpoints.md
├── book.md                                # 2. Consolidated Book with TOC
├── llms.txt                               # 3. Standardized LLM Agent Manifest
├── search.db                              # 4. SQLite FTS5 BM25 Search Index
└── exports/                               # Optional Export Studio Artifacts
    ├── docs.example.com_rag.jsonl         # Chunked RAG Vector Dataset
    └── docs.example.com_handbook.pdf      # Styled Printable PDF Handbook
```

### Artifact Details
1. **`pages/**/*.md`**: Hierarchical Markdown files with cryptographic YAML frontmatter (`source_url`, `title`, `crawl_date`, `content_hash: sha256:...`).
2. **`book.md`**: Single consolidated handbook with auto-demoted heading levels (`#` -> `##`) and a natural-order Table of Contents.
3. **`llms.txt`**: Standard discovery manifest listing all endpoints and topics according to the `llms.txt` specification.
4. **SQLite FTS5 Index**: Embedded local full-text search index for sub-second query retrieval.

---

## 🛠️ Export Studio (RAG JSONL, PDF & AST Chunker)

DocHarvest includes a built-in transformation pipeline to prepare documentation for AI pipelines and human reading:

```bash
# Export RAG JSONL and pure-Python PDF during capture
gitbook-dl capture https://docs.example.com --export jsonl,pdf

# Split an existing large markdown file strictly along heading boundaries
gitbook-dl split ~/.gitbook-downloader/library/docs.example.com/book.md --max-mb 2
```

### 1. Vector RAG JSONL Format
Generates structured JSON lines with section headers and chunk provenance ready for **LangChain**, **LlamaIndex**, **ChromaDB**, and **Pinecone**:
```json
{"id": "docs.example.com-001", "url": "https://docs.example.com/api/auth", "title": "Authentication", "tokens": 420, "text": "<!-- source: https://docs.example.com/api/auth -->\n# Authentication\nUse Bearer tokens..."}
```

### 2. Pure-Python Printable PDF (`fpdf2`)
Compiles documentation into publication-ready PDFs with syntax-highlighted code blocks, page numbers, and custom margins using pure Python (`fpdf2`). **Zero external C-libraries** (no WeasyPrint or wkhtmltopdf dependencies required).

### 3. AST Markdown Splitter (`splitter.py`)
Intelligently divides oversized markdown documents strictly along `#` heading boundaries without splitting code blocks or paragraph tokens.

---

## 🤖 AI Agent Integration (FastMCP Server)

DocHarvest includes a built-in **Model Context Protocol (MCP)** server over `stdio`, allowing coding agents (Cursor, Claude Code, Windsurf, Claude Desktop) to autonomously search, index, and read documentation:

### Configuration for Cursor & Claude Desktop
Add DocHarvest to your `claude_desktop_config.json` or Cursor MCP settings:

```json
{
  "mcpServers": {
    "docharvest": {
      "command": "gitbook-dl",
      "args": ["mcp"]
    }
  }
}
```

### Exposed MCP Tools
| MCP Tool | Parameters | Description |
|---|---|---|
| `download_docs` | `url`, `max_pages`, `scope` | Capture and index an entire documentation portal on demand |
| `search_docs` | `query`, `domain`, `limit` | Execute BM25 full-text search across local documentation |
| `read_doc_page` | `domain`, `path` | Retrieve the pristine Markdown content of a specific page |
| `list_library` | *(none)* | Inspect all captured documentation domains and versions |
| `get_doc_tree` | `domain` | Retrieve the complete hierarchy tree and page index |
| `diff_versions` | `domain`, `v1`, `v2` | Compare changes and API drift between two snapshots |
| `export_corpus` | `domain`, `format` | Trigger JSONL, PDF, or combined markdown exports |
| `get_doc_status` | `domain` | Inspect capture progress, page count, and storage stats |

---

## 📸 Modern Desktop GUI

The DocHarvest desktop interface is built with **React 18, Vite, Tailwind CSS, Lucide Icons, and shadcn/ui tokens**, encapsulated in a lightweight Python PyWebView shell:

<div align="center">

### Real-Time Capture Studio
*Radial progress gauge, animated motion bars, live terminal logs, and instant post-capture export actions.*

<img src="assets/capture_studio.png" alt="Capture Studio Interface" width="880" />

<br /><br />

### Document Library & In-App Markdown Reader
*Explore all indexed documentation sites, view disk usage, inspect versions, and read pages directly inside the app.*

<img src="assets/document_library.png" alt="Document Library Interface" width="880" />

</div>

### Key Desktop Features
- ⚡ **Global Command Palette (`Ctrl+K` / `Cmd+K`)**: Rapid navigation, search, and storage management.
- 📥 **Batch Capture Queue**: Queue multiple documentation websites to crawl sequentially in the background.
- 📖 **Split Document Reader**: In-app reader modal with live TOC navigation and syntax highlighting.
- 🔍 **Unified Search View**: Search across your entire local documentation library with highlighted snippets.
- 📊 **Snapshot Diff Inspector**: Side-by-side visual diffing across documentation versions.

---

## 🔒 Concurrency, Locking & Storage Safety

DocHarvest is architected for enterprise-grade reliability and CI/CD automation:

```
┌────────────────────────────────────────────────────────────────────────┐
│                     STORAGE & CONCURRENCY ENGINE                       │
├────────────────────────────────────────────────────────────────────────┤
│  1. Process-Aware DomainLock                                           │
│     • Active PID validation (Windows Kernel32 / POSIX os.kill)         │
│     • Auto-reclaims abandoned or stale locks from terminated processes │
├────────────────────────────────────────────────────────────────────────┤
│  2. Atomic File I/O Barrier                                            │
│     • Writes staged in temporary files (.tmp)                          │
│     • Atomic replacement via os.replace with os.fsync sync barriers    │
│     • Zero partial or corrupted files during unexpected interrupts     │
├────────────────────────────────────────────────────────────────────────┤
│  3. Semver Snapshotting & Version Diffing                              │
│     • Automatically versions existing crawls (v1.0.0 → v1.0.1)         │
│     • Generates instant unified diffs on API drift and doc changes     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Supported Documentation Platforms

DocHarvest includes prioritized platform heuristics (`ProviderRegistry`) that detect and adapt to documentation frameworks:

| Provider | Priority | Detection Heuristics & Capabilities |
|---|:---:|---|
| 🟢 **GitBook** | `100` | Space indexing, direct `.md` endpoint probing, nested summary trees, JSON sitemaps. |
| 🟢 **Mintlify** | `90` | Component-aware MDX, tabbed code block extraction, OpenAPI schema parsing. |
| 🟢 **Docusaurus** | `80` | Version-scoped sidebars (`/docs/next/`), admonitions (`:::tip`), TOC anchors. |
| 🟢 **ReadTheDocs** | `70` | Sphinx toctree hierarchies, multi-version dropdowns, clean article body extraction. |
| 🟢 **Generic / Nextra / VitePress / ReadMe** | `0` | Bounded BFS crawling, readability DOM scoring, automatic cookie banner/nav stripping. |

---

## 💻 CLI Reference & Commands

```bash
# General Syntax
gitbook-dl [COMMAND] [OPTIONS]
```

### Command Matrix
| Command | Alias | Arguments / Options | Description |
|---|---|---|---|
| `gitbook-dl` | *(none)* | *(none)* | Launch Desktop GUI (falls back to TUI if headless) |
| `gitbook-dl gui` | *(none)* | *(none)* | Explicitly launch the Desktop GUI window |
| `gitbook-dl capture <url>` | `dl` | `--export jsonl,pdf`<br>`--max-pages 100`<br>`--scope /v2/api`<br>`--workers 5` | Capture an entire doc site into clean Markdown, book.md, and llms.txt |
| `gitbook-dl search "<query>"` | `find` | `--domain example.com`<br>`--limit 20` | Full-text SQLite FTS5 search across local documentation |
| `gitbook-dl ls` | `list` | *(none)* | List all saved documentation sites, page counts, and sizes |
| `gitbook-dl read <domain>` | `view` | `--path getting-started/intro.md` | Read a specific page in terminal |
| `gitbook-dl diff <domain>` | *(none)* | `<v1> <v2>` | Compare changes between two snapshot versions |
| `gitbook-dl split <file.md>` | *(none)* | `--max-mb 2` | Split large Markdown documents into AI-friendly chunks |
| `gitbook-dl mcp` | `server` | *(none)* | Start FastMCP server over stdio for AI coding agents |

---

## 🧪 Testing & Verification

Run the full automated test suite with `pytest`:
```bash
uv run pytest
# 487 passed in 86s (100% pass rate)
```

Build the standalone Windows executable:
```bash
uv run python build_exe.py
# Produces dist/gitbook-dl.exe with embedded React frontend
```

---

## 📄 License & Community

DocHarvest is 100% free and open source, distributed under the **[MIT License](LICENSE)**.

- **Author**: Rohan Shetty ([@RohannShetty](https://github.com/RohannShetty))
- **Documentation & Showcase**: [rohannshetty.github.io/gitbook-downloader](https://rohannshetty.github.io/gitbook-downloader/)
- **Issues & Feature Requests**: [GitHub Issues](https://github.com/RohannShetty/gitbook-downloader/issues)
- **Contributing**: Pull requests and new platform provider extractors are welcome!
