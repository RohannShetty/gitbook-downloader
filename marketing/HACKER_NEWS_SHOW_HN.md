# DocHarvest — Hacker News "Show HN" Technical Submission & Playbook

> **Target Platform:** Hacker News (`https://news.ycombinator.com/show`)  
> **Submission Window:** Tuesday or Wednesday at 07:00 AM PST (15:00 UTC)  
> **HN Post Style:** High engineering depth, honest trade-offs, reproducible benchmarks, zero marketing fluff.

---

## 1. Submission Details

- **Title:** `Show HN: DocHarvest – Turn any doc site into LLM-ready Markdown, JSONL, and PDF`
- **URL / Target Link:** `https://github.com/RohannShetty/gitbook-downloader`
- **Canonical Landing Page:** `https://rohannshetty.github.io/gitbook-downloader/`
- **Submitter:** Rohan Shetty (`RohannShetty`)

---

## 2. Show HN First Comment (The Engineering Breakdown)

*Post this comment immediately after submitting the link to provide context and anchor the discussion.*

```text
Hi HN,

I built DocHarvest (https://github.com/RohannShetty/gitbook-downloader) to solve a problem I kept running into: preparing clean, accurate documentation context for LLMs, local RAG pipelines, and offline reference.

When you point wget or generic web scrapers at modern documentation portals (GitBook, Mintlify, Docusaurus, Nextra, ReadMe), you usually hit four major technical bottlenecks:

1. SPA Link Leakage: Unscoped BFS crawlers follow navbar links into landing pages, pricing grids, blog archives, and changelogs.
2. Duplicate Fragment Storms: Anchor fragments (#section-1) cause scrapers to repeatedly fetch the same underlying page dozens of times under different URLs.
3. Token Bloat & Scrambled ASTs: 80–85% of raw HTML bytes are navigation sidebars, search modals, and cookie banners. Converting raw HTML naively often splits code blocks, loses indentation in Python/YAML examples, and strips tables.
4. Heavy Dependencies: Headless browser automation (Playwright/Puppeteer) consumes hundreds of MBs of RAM per tab and frequently hangs in headless CI runners.

DocHarvest approaches this with an engine tailored specifically for technical documentation:

• Provider Auto-Detection & Direct Probing:
Instead of treating documentation as generic HTML, DocHarvest detects the underlying documentation platform (GitBook, Mintlify, Docusaurus, ReadTheDocs, Generic) using heuristic inspection. Where available, it probes native raw markdown endpoints (e.g. `<url>.md`) to fetch the exact author markdown directly from the origin server, bypassing HTML conversion loss entirely.

• Bounded BFS Crawling & Subpath Locking:
If you supply a URL with a path (e.g. `https://example.com/docs/v2/`), the crawler automatically bounds discovery to that subpath unless explicitly configured otherwise. It deduplicates permalink anchor fragments (`¶`), strips 60+ language path prefixes (e.g. `/zh/`, `/es/`) to avoid duplicate localized pages, and rewrites absolute internal links to relative markdown paths for offline browsing.

• AST '#' Header Chunking:
Our markdown splitter (`splitter.py`) parses the document syntax tree and chunks strictly along `#`, `##`, and `###` heading boundaries. It wraps each chunk in a metadata envelope containing the document domain, section hierarchy, and cryptographic SHA-256 hash. This guarantees that code blocks and markdown tables are never split mid-block across chunk boundaries.

• Four-Part Output Contract:
Every capture produces a deterministic file tree:
  ├── pages/                 # Modular Markdown files with SHA-256 YAML frontmatter
  ├── book.md                # Single consolidated handbook with generated Table of Contents
  ├── llms.txt               # Standardized agent discovery manifest
  └── exports/
      ├── rag.jsonl          # Pre-chunked RAG vector dataset (ChromaDB/Pinecone ready)
      └── handbook.pdf       # Styled printable PDF (pure-Python fpdf2, zero C-libraries)

• Crash-Resilient Concurrency & Storage:
We implemented cross-platform process-aware domain locks (`DomainLock`). By inspecting active PIDs via `ctypes.windll.kernel32.OpenProcess` on Windows and `os.kill(pid, 0)` on POSIX, the tool detects abandoned lockfiles from killed processes and reclaims them automatically. File operations use atomic temporary file staging with `os.replace` and `os.fsync` barriers to prevent corrupted writes.

• Embedded SQLite FTS5 Full-Text Search:
All captured documentation is automatically indexed into an embedded SQLite database using FTS5 virtual tables with `porter unicode61` stemming, giving you sub-10ms BM25 ranking across your entire offline documentation library.

• Model Context Protocol (FastMCP) & Desktop GUI:
DocHarvest includes a built-in FastMCP server (`gitbook-dl mcp`) exposing 8 tools over stdio for coding assistants like Cursor and Claude Code. For non-terminal workflows, we also bundle a standalone desktop application built with PyWebView, React 18, and shadcn/ui.

---

### Real-World Benchmark:
Crawling the complete OpenAlgo documentation suite (673 pages):
- Crawl & Extraction Time: 18.2 seconds (5 streaming workers)
- Raw HTML Size: ~28.4 MB (estimated ~7.1M tokens)
- DocHarvest Clean Markdown Size: 5.0 MB (estimated ~1.2M tokens)
- Token Reduction: ~82.8% reduction in context window footprint
- Output: 673 modular pages, 1 unified `book.md`, 1 `llms.txt`, 1 RAG JSONL dataset, 1 styled PDF.

The project is 100% free, MIT-licensed, and runs completely locally on your hardware with zero telemetry or external API keys.

GitHub: https://github.com/RohannShetty/gitbook-downloader
Web Showcase: https://rohannshetty.github.io/gitbook-downloader/

I’d love to hear feedback from the HN community on our extraction edge cases, chunking strategies, or suggestions for additional doc frameworks to support!
```

---

## 3. Anticipated HN Technical Questions & Prepared Responses

### Q1: "Why build a custom parser instead of using Playwright / Puppeteer with Mozilla Readability?"
> **Prepared Answer:**  
> Playwright/Chromium is fantastic for dynamic single-page applications, but it introduces significant overhead: 200MB+ RAM per browser context, heavy binary dependencies, and slow execution when crawling 1,000+ pages. 
> 
> Technical documentation platforms (GitBook, Mintlify, Docusaurus) follow structured architectural conventions. By probing native `.md` endpoints, parsing sitemaps, and applying AST-level clean selectors, DocHarvest achieves 10x higher throughput (~35–50 pages/sec) with an ultra-lightweight memory footprint (<50MB RAM in CI/CD) and zero browser automation dependencies.

---

### Q2: "How do you handle rate limiting, CAPTCHAs, or bot protection like Cloudflare?"
> **Prepared Answer:**  
> DocHarvest is specifically designed for public technical documentation sites that encourage developer access. We implement polite, respectful crawling:
> 1. Configurable concurrency workers (`--concurrency 5` default) and optional delay intervals.
> 2. Sitemap-first discovery to minimize unnecessary GET requests.
> 3. Configurable custom User-Agent strings.
> 4. Socket connect timeouts via a custom `TimeoutHTTPAdapter` to prevent hung connections.
> 
> If a target site requires authenticated sessions, DocHarvest allows passing custom HTTP request headers and authorization cookies (`--headers '{"Authorization": "Bearer ..."}')`.

---

### Q3: "How does the pure-Python PDF generation work without WeasyPrint or wkhtmltopdf?"
> **Prepared Answer:**  
> Most Python PDF generation tools rely on heavy external C-libraries (WeasyPrint requires Pango/Cairo, wkhtmltopdf requires Qt/WebKit), which creates massive installation friction on Windows and minimal Docker containers.
> 
> In `src/gitbook_downloader/utils/export.py`, we implemented a custom layout engine built on top of `fpdf2` (pure Python). It parses the Markdown AST, converts headers into a hierarchical Table of Contents, calculates page breaks, draws syntax-highlighted code block boxes with background fills, and numbers pages cleanly with zero external C-dependencies.

---

### Q4: "What makes the AST header chunker better than LangChain's RecursiveCharacterTextSplitter?"
> **Prepared Answer:**  
> `RecursiveCharacterTextSplitter` relies on character counts and regex separators (`\n\n`, `\n`, ` `). On technical documentation containing nested code blocks, tables, and lists, it frequently splits code blocks in half or disconnects a method signature from its docstring.
> 
> DocHarvest's `splitter.py` inspects the Markdown AST:
> 1. It only splits on top-level heading boundaries (`#`, `##`, `###`).
> 2. It treats code blocks (` ```python ... ``` `) and markdown tables as atomic tokens that can never be partitioned across chunks.
> 3. It prepends an HTML comment wrapper (`<!-- domain: ..., source: ..., chunk: 1/N -->`) containing the full section hierarchy path so the retrieval embedding retains section context.

---

### Q5: "How does the Model Context Protocol (FastMCP) server work?"
> **Prepared Answer:**  
> DocHarvest implements the Model Context Protocol specification over standard input/output (stdio JSON-RPC). When you add DocHarvest as an MCP server in Cursor (`.cursor/mcp.json`) or Claude Desktop (`claude_desktop_config.json`), the agent is given 8 tools:
> - `download_docs(url)`: Harvests a documentation site in the background.
> - `search_docs(query)`: Performs BM25 full-text search against the local SQLite FTS5 index.
> - `read_doc_page(domain, path)`: Retrieves the clean markdown content of a specific page.
> - `list_libraries()`: Lists all locally indexed documentation suites.
> 
> This allows the AI agent to autonomously look up exact SDK documentation without human intervention.

---

## 4. Hacker News Discussion Moderation Rules

1. **Be humble and receptive:** Acknowledge edge cases openly. If someone shows an exotic documentation format where extraction broke, thank them, create a reproducible test case, and commit a fix.
2. **Never downvote or argue:** Answer criticism with code, benchmarks, and architecture explanations.
3. **Keep replies concise and readable:** Format code snippets in mono; avoid marketing jargon.
4. **Active monitoring:** Keep the HN tab open and refresh every 5–10 minutes for the first 6 hours of the submission.
