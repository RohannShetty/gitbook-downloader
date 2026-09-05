<div align="center">

<img src="assets/logo-icon.svg" alt="DocHarvest Logo" width="96" />

# DocHarvest

### Turn Any Documentation Site into LLM-Ready Markdown, Vector Context & Offline Books

**Zero-Config CLI · React Desktop GUI · Native FastMCP Server · Pure-Python PDF Studio**

[![Version: 11.0.5](https://img.shields.io/badge/version-11.0.5-06b6d4?style=flat-square&labelColor=090d16)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-10b981?style=flat-square&labelColor=090d16)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3b82f6?style=flat-square&labelColor=090d16)](pyproject.toml)
[![UI: shadcn/ui](https://img.shields.io/badge/UI-shadcn%2Fui-27272a?style=flat-square&labelColor=090d16)](https://ui.shadcn.com)
[![Tests: 665 Passing](https://img.shields.io/badge/tests-665%20passing-10b981?style=flat-square&labelColor=090d16)](CHANGELOG.md)
[![PyPI](https://img.shields.io/pypi/v/gitbook-downloader?style=flat-square&labelColor=090d16&color=f59e0b)](https://pypi.org/project/gitbook-downloader/)
[![Showcase Website](https://img.shields.io/badge/website-Live%20Showcase-06b6d4?style=flat-square&labelColor=090d16)](https://rohannshetty.github.io/gitbook-downloader/)

<br />

<img src="assets/capture_studio.png" alt="DocHarvest Desktop GUI — Capture Studio with shadcn/ui, 60fps motion progress, radial gauge, and live terminal logs" width="920" />

</div>

---

## ⚡ Overview

**Your coding agent doesn't read documentation — it reads web pages.** Navbars, cookie banners, search modals, and footer scripts can make up 80–85% of a raw page's bytes before a single API fact arrives. Chunks captured without source URLs make hallucinations unfalsifiable, and per-page cloud API bills spike the moment you index a real docs portal.

**DocHarvest** (package: `gitbook-downloader`) fixes that locally, in one command. It detects the documentation platform, bounds the crawl strictly to documentation subpaths, extracts clean markdown via direct `.md` endpoint probing and AST-based DOM cleaning, and compiles a deterministic, noise-free knowledge corpus — measured at **~83% token reduction** on a real portal (full-suite reference capture: **673 pages in 18.2 seconds**).

Whether you are feeding 500-page API manuals to **Cursor / Claude Code**, building vector RAG pipelines with **LangChain & LlamaIndex**, reading offline on an airplane, or archiving technical libraries — every capture ends in the same verifiable shape: clean markdown with SHA-256 provenance, ready for your agent or your bookshelf.

---

## ⏱️ 30-Second Start

```bash
pip install gitbook-downloader
docharvest capture https://docs.openalgo.in/ --rag --pdf
```

No API key. No account. No telemetry. When the command finishes you own a `book.md`, an `llms.txt`, a RAG JSONL dataset, and a printable PDF — all local, all MIT. Full install paths (standalone `.exe`, uvx, optional extras) are in [Quick Start](#-quick-start).

---

## 🧩 Supported Documentation Platforms (8 Real Providers)

DocHarvest features dedicated, priority-ordered parsers that extract clean article content and strip headers, footers, sidebars, anchor hashes, and cookie banners:

| Provider | Priority | Discovery Method | Clean Content Target |
| :--- | :---: | :--- | :--- |
| **GitBook** | `100` | `.md` endpoint probing, sitemap, space discovery | Native markdown or `.page-inner` / `article` |
| **Mintlify** | `90` | `mintlify.json`, OpenAPI specs, CDN asset anchors | `#content`, `#main-content`, `article` |
| **Docusaurus** | `80` | `sitemap.xml`, `docusaurus.config.js`, sidebars | `article`, `.markdown`, `main .theme-doc-markdown` |
| **Nextra** | `75` | `sitemap.xml`, Next.js app routes, nextra scripts | `main.nextra-content`, `article` |
| **VitePress** | `72` | Sitemap, VitePress theme anchors, route index | `div.vp-doc`, `div.VPContent`, `main.VPDoc` |
| **MkDocs** | `70` | `search/search_index.json`, sitemap | `article.md-content__inner`, `div.md-typeset` |
| **ReadMe.io** | `65` | `sitemap.xml`, `/llms.txt`, developer hub routes | `div.rm-Article`, `div.rm-Markdown`, `#content` |
| **ReadTheDocs** | `60` | Sphinx `sitemap.xml`, `div.sphinxsidebar` | `div.document[role="main"]`, `div.body` |
| **Generic HTML / SPA** | `0` | BFS link crawl, `llms.txt`, `sitemap.xml` | `main`, `article`, `[role="main"]`, `#content` |

> [!TIP]
> **Dynamic JavaScript SPAs**: If a site is rendered entirely client-side via JavaScript (such as `omp.sh/docs`), install the optional Playwright extra (`pip install "gitbook-downloader[render]" && playwright install chromium`) and run with `--render` to execute JavaScript before extracting markdown.

---

## 🌟 Key Capabilities

- 🤖 **Zero-Noise LLM Context**: Auto-detects 8 documentation frameworks, probes native `.md` endpoints, and cleans DOM trees — measured at ~83% token reduction vs raw pages.
- 📦 **Four-Part Output Contract**: Every capture yields a modular `pages/` tree with SHA-256 YAML frontmatter, a consolidated `book.md` with TOC, a standardized `llms.txt` manifest, and search index records.
- 🚀 **Export Studio & Local Search**: RAG JSONL for vector databases, pure-Python PDF handbooks (`fpdf2`, zero C-dependencies), and AST markdown chunks — all indexed into embedded SQLite FTS5 BM25 search.
- 🔌 **Native FastMCP v2 Server**: 12 MCP tools plus resources and prompts over stdio, with ready-made configs for 14 AI clients (Cursor, Claude Code/Desktop, Windsurf, VS Code & more). Crash-safe atomic storage and semver snapshot diffing included.

### What DocHarvest Is *Not* For

A tool that claims to do everything has earned none of your trust. Honest scope:

- **Not for login-walled, paywalled, or CAPTCHA-protected content.** DocHarvest is built for public technical documentation and will not bypass access controls.
- **Not for internet-scale crawling.** Millions of arbitrary URLs is Common Crawl / Scrapy territory; this is a documentation compiler, not a search-engine crawler.
- **Not for e-commerce or social feeds.** Product catalogs and social streams are out of scope by design.
- **Not a cloud service.** No dashboard, no subscription, no telemetry — because nothing of yours ever leaves your machine.

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

**What a generic crawler hands your LLM** (every page, every time):

```html
<nav class="sidebar">…47 links…</nav>
<div class="cookie-banner">We value your privacy…</div>
<main>
  <h1>OAuth 2.0<a class="anchor" href="#oauth2">¶</a></h1>
  <pre><code><span class="token-keyword">import</span> <span class="token-variable">requests</span>…</code></pre>
</main>
```

**What DocHarvest delivers** — the same page, with cryptographic provenance:

````markdown
---
source_url: https://docs.openalgo.in/v/v2.0/api-reference/oauth
title: "OAuth 2.0 Authentication"
content_hash: "sha256-2fa9ca2a57c4e974f1725657f88f757e25b90adee3e18ef809f65932d283746c"
---

# OAuth 2.0 Authentication

## Request Signature

```python
import requests

response = requests.post(
    "https://api.openalgo.in/oauth/token",
    json={"client_id": "pk_live_..."},
)
```
````

The `content_hash` is the real SHA-256 of the markdown body shown above — paste it into any SHA-256 tool and it verifies.

Every crawl produces the same standardized, deterministic directory structure:

```
~/.gitbook-downloader/docs/
└── docs.openalgo.in/
    ├── pages/                     # Modular individual markdown files
    │   ├── 001_quickstart.md
    │   └── 002_api_reference.md
    ├── book.md                    # Consolidated single handbook with hierarchical TOC
    ├── llms.txt                   # Standardized AI discovery manifest
    ├── exports/
    │   ├── openalgo_rag.jsonl     # Tokenized vector chunks + metadata
    │   └── openalgo_handbook.pdf  # Publication-grade printable PDF (pure Python)
    └── .manifest.json             # Crawl metadata, engine version & cryptographic hashes
```

---

## 🚀 Quick Start

### Option 1: Standalone Executable (Zero Setup)
Download **[`docharvest-windows-latest.exe`](https://github.com/RohannShetty/gitbook-downloader/releases/latest)** from the latest release:
- **Double-click** to launch the **Desktop GUI Application**.
- Or execute directly in your terminal:
  ```powershell
  .\docharvest-windows-latest.exe crawl https://docs.openalgo.in/ --rag --pdf
  ```

### Option 2: Install via pip / PyPI
```bash
# Standard installation (100% local, zero C-dependencies)
pip install gitbook-downloader

# Optional headless browser rendering for dynamic JavaScript SPAs
pip install "gitbook-downloader[render]"
playwright install chromium

# MCP server: the FastMCP SDK ships in the base install — nothing extra needed.
# (The [mcp] extra is a backward-compatibility no-op; this line still resolves.)
pip install "gitbook-downloader[mcp]"

# Launch desktop GUI:
docharvest --gui

# Or run a CLI crawl:
docharvest capture https://docs.openalgo.in/ --rag --pdf
```

### Option 3: Ultra-Fast One-Liner via uv / uvx
```bash
# Launch GUI instantly without permanent installation:
uvx gitbook-downloader --gui

# Or install as a global CLI tool:
uv tool install gitbook-downloader
```

---

## 💻 CLI Command Reference

```bash
# Basic Documentation Crawl (aliases: capture, dl, crawl)
# `docharvest capture` is the canonical verb; `crawl` remains as a documented alias.
docharvest capture https://docs.openalgo.in/

# Full Compilation (Markdown + RAG JSONL + llms.txt + PDF Handbook)
docharvest capture https://docs.openalgo.in/ --rag --pdf

# Crawl Dynamic Client-Rendered SPAs (Playwright Headless Browser)
docharvest capture https://omp.sh/docs --render

# Restrict Crawl to Specific Path Prefix & Limit Depth
docharvest capture https://docs.example.com/ --scope /api/ --max-pages 50

# Full-Text BM25 Search across Harvested Docs
docharvest search "OAuth 2.0 authentication token"

# List Harvested Document Domains in Local Library
docharvest ls

# Show Snapshot History & Diff Versions
docharvest history docs.example.com
docharvest diff docs.example.com v1.0.0 v1.0.1

# Start FastMCP Server over Stdio for AI IDEs
docharvest --mcp

# Launch Desktop GUI Application
docharvest --gui
```

---

## 🔌 AI Agent Integration: Native FastMCP v2 Server

DocHarvest includes a native **FastMCP (Model Context Protocol v2)** server that exposes 12 high-level tools, **MCP Resources**, and **MCP Prompts** over standard input/output (`stdio`). It is compatible with both `mcp<2` and `mcp>=2.1`.

> **The `mcp` SDK ships in the base install.** `pip install gitbook-downloader` (or `uvx gitbook-downloader mcp`) is enough — no extras required. The `gitbook-downloader[mcp]` extra is still accepted for backward compatibility but is now a no-op.

### All 12 Native MCP Tools

1. `download_docs(url, max_pages=None, workers=8, path_scope=[], exclude_paths=[], site_versions=None, output_mode="both")`
   Captures any documentation URL into Markdown, `book.md`, and `llms.txt`.
2. `search_docs(query, domain=None, limit=10)`
   Full-text search across downloaded documentation via SQLite FTS5 BM25.
3. `find_docs(query, limit=10)`
   Resolves library/framework names ("react", "nextjs") to indexed domains in the local library.
4. `read_doc(domain, path=None, topic=None, max_tokens=4000, version=None)`
   Reads a specific page or topic section with AST-safe token bounding — code blocks and tables are never split.
5. `get_doc(domain, version=None)`
   Retrieves the compiled documentation content or preview for a domain.
6. `list_domains()`
   Returns metadata for all harvested documentation portals in local storage.
7. `query_doc_graph(domain, query, limit=10)`
   Queries the semantic entity & concept graph to discover connected API endpoints and sections without reading full files.
8. `get_related_concepts(domain, concept)`
   Returns 1-hop and 2-hop connected concepts and prerequisite sections.
9. `diff_versions(domain, v1, v2)`
   Computes unified diffs and line change statistics between two snapshots.
10. `list_versions(domain)`
    Lists available captured snapshots and timestamps for a domain.
11. `export_docs(domain, format="markdown")`
    Exports documentation into `"markdown"`, `"jsonl"`, or `"rag"` metadata formats.
12. `get_changelog(domain)`
    Auto-generates version changelogs across captured snapshot iterations.

### MCP v2 Resources & Prompts
- **Resources**: `docs://{domain}/book` (full handbook), `docs://{domain}/manifest` (`llms.txt` index).
- **Prompts**: `prompt://search-docset` (guided docset synthesis), `prompt://summarize-library` (library overview).

---

### IDE & Agent Configuration Matrix (14 Clients)

*The three most common clients are shown inline — expand the list for all 14.*

#### 1. Claude Code
```bash
claude mcp add docharvest docharvest mcp
```
Or in `~/.claude.json`:
```json
{
  "mcpServers": {
    "docharvest": {
      "command": "docharvest",
      "args": ["mcp"]
    }
  }
}
```

#### 2. Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "docharvest": {
      "command": "uvx",
      "args": ["gitbook-downloader", "mcp"]
    }
  }
}
```

#### 3. Cursor (`.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "docharvest": {
      "command": "python",
      "args": ["-m", "gitbook_downloader.mcp"]
    }
  }
}
```

<details>
<summary><strong>11 more client configs — Windsurf · VS Code · JetBrains · Zed · Cline · Continue · Kiro · OpenCode · Pi/Oh My Pi · Gemini CLI · Codex CLI</strong></summary>

#### 4. Windsurf (`~/.codeium/windsurf/mcp_config.json`)
```json
{
  "mcpServers": {
    "docharvest": {
      "command": "docharvest",
      "args": ["mcp"]
    }
  }
}
```

#### 5. VS Code (`.vscode/mcp.json`)
```json
{
  "servers": {
    "docharvest": {
      "type": "stdio",
      "command": "docharvest",
      "args": ["mcp"]
    }
  }
}
```

#### 6. JetBrains AI Assistant / PyCharm / IntelliJ
Configure via **Settings → Tools → Model Context Protocol (MCP)**:
- **Server Name**: `docharvest`
- **Command**: `docharvest`
- **Arguments**: `mcp`

#### 7. Zed (`settings.json`)
```json
{
  "context_servers": {
    "docharvest": {
      "command": "docharvest",
      "args": ["mcp"]
    }
  }
}
```

#### 8. Cline (`cline_mcp_settings.json`)
```json
{
  "mcpServers": {
    "docharvest": {
      "command": "docharvest",
      "args": ["mcp"],
      "disabled": false,
      "autoApprove": ["search_docs", "get_doc", "list_domains", "query_doc_graph"]
    }
  }
}
```

#### 9. Continue.dev (`config.json`)
```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "docharvest",
          "args": ["mcp"]
        }
      }
    ]
  }
}
```

#### 10. Kiro (`.kiro/settings/mcp.json`)
```json
{
  "mcp": {
    "servers": {
      "docharvest": {
        "command": "docharvest",
        "args": ["mcp"]
      }
    }
  }
}
```

#### 11. OpenCode (`opencode.json`)
```json
{
  "mcp": {
    "docharvest": {
      "command": "docharvest",
      "args": ["mcp"]
    }
  }
}
```

#### 12. Pi (`pi.dev`) / Oh My Pi (`omp.sh`) (`~/.omp/config.json`)
```json
{
  "mcp_servers": {
    "docharvest": {
      "command": "docharvest",
      "args": ["mcp"]
    }
  }
}
```

#### 13. Antigravity / Gemini CLI (`mcp/docharvest.json`)
```json
{
  "name": "docharvest",
  "command": "docharvest",
  "args": ["mcp"]
}
```

#### 14. OpenAI Codex CLI (`codex_config.json`)
```json
{
  "mcp_servers": {
    "docharvest": {
      "command": "docharvest",
      "args": ["mcp"]
    }
  }
}
```

</details>

---

## 🐍 Python SDK Example

```python
from gitbook_downloader.api import capture, CaptureOptions

# Configure capture options
options = CaptureOptions(
    workers=8,
    output_mode="both",   # "both", "library", or "local"
    render=False,         # set True for dynamic JavaScript SPAs
)

# Execute deterministic capture
result = capture("https://docs.openalgo.in/", options=options)

print(f"Captured {result.pages_captured} pages using provider: {result.provider}")
print(f"Book file: {result.book_file}")
print(f"Manifest:  {result.manifest_file}")
```

---

## 🧪 Test Suite & Quality Benchmarks

DocHarvest is continuously tested across Windows, Linux, and macOS:

- **686 Automated Tests**: 100% pass rate across engine discovery, BFS crawling, provider extraction, storage safety, DocGraph semantic search, and MCP v2 tools (verified on this release).
- **73%+ Statement Coverage**: Rigorous test suites covering error recovery, invalid signatures, domain locks, and AST link normalization.
- **Windows CRLF Safe**: All link and boilerplate stripping routines are cross-platform normalized against Windows CRLF and Unix LF linebreaks.

To run the test suite locally:
```bash
uv run pytest --cov=gitbook_downloader
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
