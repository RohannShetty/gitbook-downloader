<div align="center">

<img src="assets/logo-icon.svg" alt="gitbook-downloader logo — modern documentation downloader" width="96" />

# `gitbook-downloader`

### Turn Any Documentation Site into Clean, LLM-Ready Markdown.

**Native Desktop GUI · High-Performance CLI · AI Agent MCP Server**

[![Version: 8.0.0](https://img.shields.io/badge/version-8.0.0-06b6d4?style=flat-square&labelColor=090d16)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-10b981?style=flat-square&labelColor=090d16)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3b82f6?style=flat-square&labelColor=090d16)](pyproject.toml)
[![Platform: Windows | Linux | macOS](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-8b5cf6?style=flat-square&labelColor=090d16)](#)

<br />

<img src="assets/capture_studio.png" alt="GitBook Downloader v8 Desktop GUI — Capture Studio with 60fps motion progress, radial gauge, and live terminal logs" width="920" />

</div>

---

## ✨ What's New in v8.0

- 🖥️ **Modern Windows Desktop GUI**: Native Edge WebView2 application featuring 60fps motion progress bars, glowing SVG radial gauges, syntax-highlighted live crawl streaming, and dark glassmorphic styling.
- ⚡ **Direct Enter-to-Download**: Instant URL detection and one-click capture with active in-flight cancellation.
- 📖 **In-App Document Reader & Library**: Explore captured sites in a split-screen Markdown modal or jump directly to files in Windows Explorer.
- 🔍 **Search Studio**: Fast SQLite FTS5 full-text search across all downloaded documentation.
- 📊 **Snapshot Diff Visualizer**: Side-by-side comparison tracking documentation changes over time.
- 📦 **Zero-Config Standalone Executable**: Single 23.5 MB `gitbook-dl.exe` binary with zero prerequisites.

---

## 🚀 Quick Start

### Option 1: Standalone Windows Binary (Zero Setup)
Download **[`gitbook-dl.exe`](https://github.com/RohannShetty/gitbook-downloader/releases)** from the latest release:
- **Double-click** to launch the **Desktop GUI Application**.
- Or run in terminal: `.\gitbook-dl.exe capture https://docs.openalgo.in/`

### Option 2: Install via pip / uv
```bash
pip install git+https://github.com/RohannShetty/gitbook-downloader.git
```

Launch the GUI or CLI:
```bash
# Launch Desktop GUI
gitbook-dl

# Or run CLI capture
gitbook-dl capture https://docs.example.com
```

---

## 📸 Desktop GUI Experience

<div align="center">

### Real-Time Capture Studio
*Glowing radial progress gauge, 60fps motion stripes, live color-coded crawl terminal, and instant completion feedback.*

<img src="assets/capture_studio.png" alt="Capture Studio Interface" width="880" />

<br /><br />

### Document Library & In-App Markdown Reader
*Explore all indexed documentation sites, view disk usage, inspect versions, and read pages directly inside the app.*

<img src="assets/document_library.png" alt="Document Library Interface" width="880" />

</div>

---

## 📦 The Output Contract

Every capture produces four standardized, deterministic artifacts:

```text
docs.example.com-docs/
├── pages/
│   ├── getting-started/
│   │   ├── introduction.md      ← YAML frontmatter: url, title, date, hash
│   │   └── installation.md
│   └── api/
│       └── authentication.md
├── book.md                      ← Full documentation set with deterministic Table of Contents
└── llms.txt                     ← Standardized LLM manifest listing all captured pages
```

- **`pages/**/*.md`**: Clean, individual Markdown files ready for RAG chunking and vector databases.
- **`book.md`**: Combined single file ready to paste into ChatGPT, Claude, Gemini, or local LLMs.
- **`llms.txt`**: Standard manifest for AI agent discovery and context ingestion.

---

## 💻 CLI Commands & Automations

| Command | Description |
|---|---|
| `gitbook-dl` | Launch the modern Desktop GUI application (falls back to TUI if headless) |
| `gitbook-dl gui` | Explicitly launch the Desktop GUI window |
| `gitbook-dl capture <url>` | Capture an entire doc site to clean Markdown (`alias: dl`) |
| `gitbook-dl capture <url> --max-pages 50` | Limit crawl depth to N pages |
| `gitbook-dl capture <url> --scope /v2/api` | Restrict crawler to specific path prefixes |
| `gitbook-dl search "rate limit"` | Full-text SQLite search across your entire documentation library |
| `gitbook-dl ls` | List all saved documentation sites in your library |
| `gitbook-dl diff <domain> <v1> <v2>` | Compare changes between two snapshot versions |
| `gitbook-dl split <file.md> --max-mb 5` | Split large Markdown documents into AI-friendly chunks |
| `gitbook-dl mcp` | Start Model Context Protocol server for AI coding agents |

---

## 🤖 AI Agent Integration (MCP)

`gitbook-downloader` provides a native **Model Context Protocol (MCP)** server so Claude Code, Cursor, Codex, and other AI agents can search and download documentation autonomously:

```json
{
  "mcpServers": {
    "gitbook-downloader": {
      "command": "gitbook-dl",
      "args": ["mcp"]
    }
  }
}
```

Available MCP tools:
- `download_docs(url, max_pages, scope)` — Capture full documentation sites.
- `search_docs(query, domain)` — Search across local documentation library.
- `read_doc_page(domain, path)` — Read specific Markdown documentation pages.
- `list_library()` — Inspect downloaded documentation catalog.

---

## 🛠️ Supported Providers

Auto-detection works automatically without manual configuration:
- 🟢 **GitBook** (space indexing, multi-version trees, JSON sitemaps)
- 🟢 **Docusaurus** (sitemap hierarchy, navbar routing)
- 🟢 **Mintlify** (docs routing, OpenAPI specs)
- 🟢 **ReadTheDocs** (Sphinx TOC trees, version selectors)
- 🟢 **Generic HTML Sites** (heuristic content extraction with readability scoring)

---

## 🧪 Testing & Verification

Run the comprehensive test suite with `pytest`:
```bash
uv run pytest
# 487 passed in 86s (100% pass rate)
```

Build the standalone Windows executable:
```bash
uv run python build_exe.py
# Produces dist/gitbook-dl.exe (23.5 MB)
```

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
