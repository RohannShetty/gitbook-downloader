# DocHarvest — X (Twitter) 7-Tweet Visual Launch Thread

> **Launch Day Thread Copy for @X / Twitter**  
> **Posting Schedule:** Tuesday / Wednesday at 06:00 AM PST (14:00 UTC)  
> **Target Audience:** AI Engineers, LLM Developers, RAG Practitioners, Open Source Enthusiasts  
> **Goal:** Drive GitHub Stars, PyPI installations, and showcase site traffic.

---

## Thread Overview & Visual Asset Map

| Tweet # | Theme / Objective | Key Content Hook | Media / Visual Asset Attached |
|---|---|---|---|
| **Tweet 1** | The Hook & Solution | The 3-hour copy-paste pain; Meet DocHarvest (1-click docs to RAG/PDF). | `assets/demo-capture.gif` (15s terminal recording) |
| **Tweet 2** | The Core Problem | Why `wget` & raw web scrapers fail (85% token waste, broken code). | `assets/comparison-html-vs-markdown.png` (Side-by-side) |
| **Tweet 3** | Invisible Intelligence | Auto-detection (GitBook, Mintlify, Docusaurus) & direct `.md` probing. | Code snippet / Provider detection diagram |
| **Tweet 4** | Four-Part Output Contract | Deterministic outputs: `pages/`, `book.md`, `llms.txt`, and vector `jsonl`. | ASCII tree diagram / Screenshot of output folder |
| **Tweet 5** | AI Agent FastMCP Server | Wire directly to Cursor & Claude Code via Model Context Protocol. | `assets/cursor-mcp-demo.png` (Cursor IDE integration) |
| **Tweet 6** | Desktop GUI & SQLite FTS5 | React 18 + shadcn Desktop GUI, radial telemetry, pure-Python PDF. | `assets/capture_studio.png` (Capture Studio UI) |
| **Tweet 7** | CTA & Community Question | Free, MIT, `pip install gitbook-downloader` or `.exe`, GitHub link. | `assets/social-preview.png` (Brand card) |

---

## Complete Thread Copy

### 🧵 Tweet 1: The Hook & Announcement

```tweet
I spent 3 hours copy-pasting API docs into Cursor.

Page 40 of 673, I gave up and built a tool instead.

Meet DocHarvest (formerly gitbook-downloader): Turn ANY documentation site into LLM-ready Markdown, vector RAG datasets & offline PDF books in 1 command.

100% local. Free. Open source. 🚀👇

[VISUAL: Attach assets/demo-capture.gif — 15-second high-speed recording of terminal running `gitbook-dl capture https://docs.openalgo.in/` showing 673 pages captured in 18s and generating book.md, llms.txt, and exports/]
```

---

### 🧵 Tweet 2: The Core Problem with Web Scraping Docs

```tweet
Why feeding web docs to LLMs is broken today:

❌ wget/curl dumps raw HTML (80% wasted tokens on navbars, headers & cookie popups)
❌ Fragile scrapers break code indentation & drop tables
❌ Dynamic SPAs fool basic crawlers into link loops
❌ Cloud scraping APIs charge $/page and keep your data

[VISUAL: Attach assets/comparison-html-vs-markdown.png — High-contrast graphic showing 45KB of messy HTML boilerplate with red highlights vs 2.1KB of pristine DocHarvest Markdown with green highlights]
```

---

### 🧵 Tweet 3: Invisible Intelligence & Platform Auto-Detection

```tweet
DocHarvest requires ZERO custom scraping scripts:

⚡ Auto-detects GitBook, Mintlify, Docusaurus, ReadTheDocs, Nextra & generic docs
⚡ Direct .md probing retrieves pristine author markdown straight from the source
⚡ Bounded BFS crawler locks strictly onto the doc root (no link bleeding)

[VISUAL: Code snippet box showing auto-detection logs:]
❯ gitbook-dl capture https://docs.anthropic.com/
[14:02:01] ⚡ Probing documentation framework...
[14:02:02] ✓ Provider detected: Mintlify (MDX direct probe active)
[14:02:03] 🔒 BFS crawler locked to subpath: /en/docs/
```

---

### 🧵 Tweet 4: The Four-Part Output Contract

```tweet
Every capture produces a deterministic Four-Part Output Contract:

📁 pages/**/*.md: Clean modular markdown with SHA-256 YAML frontmatter
📖 book.md: Single consolidated handbook with auto-generated TOC
📄 llms.txt: Standardized AI agent discovery manifest
📊 exports/*.jsonl: Pre-chunked RAG datasets ready for ChromaDB/Pinecone

[VISUAL: ASCII Output Tree Diagram showing deterministic artifact structure]
```

---

### 🧵 Tweet 5: Native FastMCP Server for Cursor & Claude Code

```tweet
DocHarvest includes a native Model Context Protocol (FastMCP) server.

You can connect it directly to @cursor_run or @ClaudeAI Code:
Your AI agent can autonomously discover, search, and read external documentation on the fly without leaving your editor.

Just run:
`gitbook-dl mcp`

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

[VISUAL: Attach assets/cursor-mcp-demo.png — Screenshot of Cursor IDE invoking the `search_docs` tool and reading a local doc page]
```

---

### 🧵 Tweet 6: Standalone Desktop GUI & Offline Knowledge Base

```tweet
Don't want to use the CLI? 

DocHarvest comes with a standalone Desktop GUI (React 18 + shadcn/ui):
✨ Live radial progress ring & crawl logs
🔍 Embedded SQLite FTS5 full-text search (BM25 ranking)
📄 Pure-Python printable PDF compiler (fpdf2, zero C-deps)
📊 Version snapshot diffing (`gitbook-dl diff`)

[VISUAL: Attach assets/capture_studio.png & assets/document_library.png — Crisp screenshot of the dark-mode Desktop GUI with radial progress gauge]
```

---

### 🧵 Tweet 7: CTA, Links & Community Question

```tweet
DocHarvest is 100% free, MIT-licensed, and runs completely offline.

📦 Install via pip:
pip install gitbook-downloader

💻 Or download standalone Windows .exe / Linux binaries:
⭐ GitHub: https://github.com/RohannShetty/gitbook-downloader
🌐 Showcase: https://rohannshetty.github.io/gitbook-downloader/

What documentation platform should we add native extractors for next? Let me know below! 👇
```

---

## Launch Day Engagement & Reply Playbook

### 1. Immediate Follow-up Quote Tweet (Post at T+30 mins)
> *"P.S. If you're building local RAG with LangChain, LlamaIndex, or Ollama, the exported JSONL chunks include section anchors and cryptographic content hashes so your embeddings are always cited back to exact source URLs. Star the repo on GitHub to support open-source AI tooling!"*

### 2. Community Tagging Strategy (Post in Reply Thread)
- Tag relevant ecosystems: `@cursor_run`, `@LangChainAI`, `@llama_index`, `@AnthropicAI`, `@OpenAI`, `@MistralAI`.
- Include relevant hashtags: `#RAG #LocalLLM #OpenSource #Python #DevTools #CursorAI #ClaudeCode #FastMCP`

### 3. Rapid Reply Templates for Common Inquiries
- **"Does it support JS-rendered SPAs?"**  
  *Yes! DocHarvest probes raw `.md` endpoints first, reads `/sitemap.xml` and `/llms.txt`, and uses fallback DOM selector chains to extract structured article content without spinning up heavy browser engines.*
- **"How does PDF generation work?"**  
  *It uses a custom pure-Python engine built on `fpdf2`. It formats code blocks with syntax styling, headers, and page numbering with zero external C-dependencies (no WeasyPrint or wkhtmltopdf).*
- **"Can I run this in CI/CD?"**  
  *Yes, DocHarvest is a lightweight CLI with process-aware atomic domain locks. You can easily script nightly scrapes to track documentation drift via `gitbook-dl diff`.*
