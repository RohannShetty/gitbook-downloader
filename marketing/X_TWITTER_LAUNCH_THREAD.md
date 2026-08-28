# DocHarvest v11 — X (Twitter) Viral Launch Thread

> **Launch Day Thread Copy for @X / Twitter**  
> **Posting Schedule:** Tuesday / Wednesday at 06:00 AM PST (14:00 UTC)  
> **Target Audience:** AI Engineers, Cursor & Claude Code Users, OpenCode/Pi Devs, RAG Architects, Open Source Practitioners  
> **Goal:** Drive GitHub Stars, PyPI installations, and showcase site traffic.

---

## Thread Overview & Visual Asset Map

| Tweet # | Theme / Objective | Key Content Hook | Media / Visual Asset Attached |
|---|---|---|---|
| **Tweet 1** | The Hook & Solution | Your AI agent burns 89% of its context on HTML noise. Meet DocHarvest. | `assets/demo-capture.gif` (15s terminal recording) |
| **Tweet 2** | The Token Economy Pain | Why `curl` & raw scrapers fail (40KB HTML soup vs 2KB clean AST markdown). | `assets/comparison-html-vs-markdown.png` (Side-by-side) |
| **Tweet 3** | Supported Agent Ecosystem | 1-Click FastMCP v2 for Cursor, Claude Code, OpenCode, Pi, Windsurf & Codex. | `assets/cursor-mcp-demo.png` (Agent integration grid) |
| **Tweet 4** | 8 Dedicated AST Frameworks | GitBook, Mintlify, Docusaurus, Nextra, VitePress, MkDocs, ReadMe & JS SPAs. | Framework detection logs |
| **Tweet 5** | The Four-Part Output Contract | Deterministic outputs: `pages/`, `book.md`, `llms.txt`, and vector `dataset.jsonl`. | ASCII tree diagram |
| **Tweet 6** | Local-First vs Cloud Scraper APIs | Why pay Firecrawl/Jina per page when you can run 100% free locally with SQLite BM25? | Comparison chart |
| **Tweet 7** | Desktop GUI & Printable PDFs | React 18 + shadcn Desktop GUI, pure-Python PDF handbook (zero C-deps). | `assets/capture_studio.png` |
| **Tweet 8** | CTA & GitHub Star Callout | Free, MIT, `pip install gitbook-downloader` or Windows `.exe`, GitHub link. | `assets/social-preview.png` |

---

## Complete Thread Copy

### 🧵 Tweet 1: The Hook & Problem Framing

```tweet
Your AI coding agent is burning 89% of its context window on navigation HTML, cookie banners, and React hydration scripts.

When you ask Cursor, Claude Code, or OpenCode to read documentation with curl, it receives 40KB of noise instead of code.

Meet DocHarvest (package: gitbook-downloader): The local-first doc compiler & FastMCP v2 server.

Turn any documentation portal into pure LLM context, vector RAG datasets & offline books in seconds.

100% local. Free. MIT. 🚀👇
```

---

### 🧵 Tweet 2: The Context Token Waste Comparison

```tweet
Why scraping docs with basic web scrapers ruins agent accuracy:

❌ curl/wget dumps 40KB+ HTML boilerplate (exhausts 128k context windows)
❌ Broken indentation in multi-language code snippets
❌ Client-rendered JavaScript SPAs return blank white shells
❌ Paid cloud scraper APIs charge $0.05/page and send private docs to third parties

DocHarvest uses 8 dedicated AST extractors to isolate article content and probe author-original .md endpoints directly.
```

---

### 🧵 Tweet 3: Plug-and-Play FastMCP v2 for 15+ Coding Agents

```tweet
DocHarvest runs a native FastMCP v2 server over stdio. 

One config snippet gives your favorite agent 10 native tools to crawl, index, and query documentation on demand:

⚡ @cursor_run
⚡ @ClaudeAI Code & Desktop
⚡ OpenCode
⚡ Pi Coding Agent & Oh My Pi (omp.sh)
⚡ @codeiumdev Windsurf
⚡ VS Code (Cline / Roo Code / Copilot)
⚡ OpenAI Codex CLI & CommandCode
⚡ Kilo Code & Grok Build

Your agent searches indexed docs via BM25 in <15ms without copy-pasting.
```

---

### 🧵 Tweet 4: Invisible AST Intelligence Across Frameworks

```tweet
DocHarvest auto-detects documentation platforms with zero manual regex scripts:

⚡ GitBook — Traverses multi-version dropdowns (/v/v2.0/) & probes raw .md endpoints
⚡ Mintlify — Filters MDX components (<Accordion>, <ParamField>) to clean markdown
⚡ Docusaurus — Isolates <article> DOM, expands React tabs & callouts
⚡ Nextra & VitePress — Extracts navigation trees and code group tabs
⚡ MkDocs & ReadTheDocs — Unfolds search indices and Sphinx directives
⚡ Dynamic SPAs — Opt-in Playwright headless engine (--render)
```

---

### 🧵 Tweet 5: The Four-Part Output Contract

```tweet
Every crawl outputs a predictable four-part matrix:

1️⃣ pages/**/*.md — Modular markdown with SHA-256 YAML frontmatter
2️⃣ book.md — Consolidated single handbook with auto-generated TOC
3️⃣ llms.txt — Standardized AI agent context discovery manifest
4️⃣ dataset.jsonl & handbook.pdf — Vector RAG chunks + pure-Python printable PDF

Direct drop-in for LangChain, LlamaIndex, ChromaDB, and Claude Project Knowledge.
```

---

### 🧵 Tweet 6: The Local-First Firecrawl Powerhouse

```tweet
Stop paying cloud reader APIs per-page scraping subscriptions.

DocHarvest runs entirely on your machine:
🔒 100% Local & Private (Zero cloud telemetry)
⚡ 20 pages/sec parallel throughput
🔍 Embedded SQLite FTS5 BM25 search database
📄 Pure-Python PDF handbook generator (zero WeasyPrint/wkhtmltopdf C-deps)
🔄 Semver snapshot diffing across crawls (gitbook-dl diff)
```

---

### 🧵 Tweet 7: Desktop GUI & Standalone Binaries

```tweet
Prefer a visual desktop interface?

DocHarvest includes a standalone Desktop GUI:
✨ Live radial crawl progress gauge & real-time telemetry
📊 Visual document library with sub-15ms search
⚙️ 1-click FastMCP config installer for Cursor and Claude
💻 Portable Windows .exe, macOS & Linux standalone binaries
```

---

### 🧵 Tweet 8: CTA, Links & Community Callout

```tweet
DocHarvest is 100% free and open source under the MIT license.

📦 Install via pip:
pip install gitbook-downloader

⚡ Run via uvx:
uvx gitbook-downloader --gui

⭐ Star on GitHub: https://github.com/RohannShetty/gitbook-downloader
🌐 Interactive Showcase: https://rohannshetty.github.io/gitbook-downloader/

What documentation site should we test next? Drop your favorite library in the replies! 👇
```

---

## Launch Day Engagement & Reply Playbook

### 1. Immediate Follow-up Quote Tweet (Post at T+30 mins)
> *"P.S. If you're building local RAG with LangChain, LlamaIndex, or Ollama, the exported JSONL chunks include token counts (cl100k_base compatible) and cryptographic content hashes so your embeddings are always cited back to exact source URLs. Star the repo on GitHub to support open-source tooling!"*

### 2. Community Tagging Strategy (Post in Reply Thread)
- Tag relevant ecosystems: `@cursor_run`, `@LangChainAI`, `@llama_index`, `@AnthropicAI`, `@OpenAI`, `@MistralAI`.
- Include relevant hashtags: `#RAG #LocalLLM #OpenSource #Python #DevTools #CursorAI #ClaudeCode #FastMCP #OpenCode`

