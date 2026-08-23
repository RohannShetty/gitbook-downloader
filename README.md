<div align="center">

<img src="assets/logo-icon.svg" alt="gitbook-downloader logo — modern documentation downloader" width="96" />

# `gitbook-downloader`

### Turn Any Documentation Site into Clean, LLM-Ready Markdown.

**Native Desktop GUI · High-Performance CLI · AI Agent MCP Server**

[![Version: 9.0.1](https://img.shields.io/badge/version-9.0.1-06b6d4?style=flat-square&labelColor=090d16)](CHANGELOG.md)
[![UI: shadcn/ui](https://img.shields.io/badge/UI-shadcn%2Fui-zinc?style=flat-square&labelColor=090d16)](https://ui.shadcn.com)
[![License: MIT](https://img.shields.io/badge/license-MIT-10b981?style=flat-square&labelColor=090d16)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3b82f6?style=flat-square&labelColor=090d16)](pyproject.toml)
[![Platform: Windows | Linux | macOS](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-8b5cf6?style=flat-square&labelColor=090d16)](#)

<br />

<img src="assets/capture_studio.png" alt="GitBook Downloader v9 Desktop GUI — Capture Studio with shadcn/ui, 60fps motion progress, radial gauge, and live terminal logs" width="920" />

</div>

---

## ✨ What's New in v9.0 Stable

- 🎨 **shadcn/ui Design System**: Re-engineered desktop frontend built with React 18, Vite, Tailwind CSS, Lucide icons, and adaptive light/dark theme tokens.
- 📂 **Collapsible Modern Sidebar**: Clean navigation with quick status pills, badge telemetry, and theme toggles.
- ⚡ **Global Command Palette (`Ctrl+K` / `Cmd+K`)**: Keyboard-driven launcher for instant view switching, document search, and storage actions.
- 📥 **Batch Capture Queue**: Queue multiple documentation websites to crawl sequentially in the background.
- 📄 **Pure-Python PDF Generation**: Styled documentation books with syntax highlighting, clean margins, and TOC (`fpdf2`).
- 🚀 **AI / RAG Export Studio**: Export documentation sets directly to **JSONL** (for LangChain, LlamaIndex, OpenAI embeddings, ChromaDB), **PDF**, or unified **book.md**.
- 🔍 **Universal Doc-Root Auto-Expansion**: Intelligently handles subpage links like `https://ui.shadcn.com/docs/installation` by capturing the entire doc suite.
- 📖 **Split Document Reader**: In-app reader modal with page filtering, table of contents, and syntax highlighting.
- 📦 **Zero-Config Standalone Executable**: Single standalone `gitbook-dl.exe` with bundled React frontend assets.

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
