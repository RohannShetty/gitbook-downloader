# DocHarvest — Hacker News "Show HN" Technical Submission & Playbook

> **Target Platform:** Hacker News (`https://news.ycombinator.com/show`)  
> **Submission Window:** Tuesday or Wednesday at 07:00 AM PST (15:00 UTC)  
> **HN Post Style:** High engineering depth, honest trade-offs, reproducible benchmarks, zero marketing fluff.

---

## 1. Submission Details

- **Title:** `Show HN: DocHarvest – Turn any doc site into clean LLM context (local, MIT)`
- **URL / Target Link:** `https://github.com/RohannShetty/gitbook-downloader`
- **Canonical Landing Page:** `https://rohannshetty.github.io/gitbook-downloader/`
- **Submitter:** Rohan Shetty (`RohannShetty`)

---

## 2. Show HN First Comment (The Engineering Breakdown)

*Post this comment immediately after submitting the link to provide context and anchor the discussion.*

```text
Hi HN,

The short version first, so you can decide whether the rest is worth your time: pointed at a 673-page documentation portal, DocHarvest captured, cleaned, and exported the entire corpus in 18.2 seconds, cutting ~83% of the context-window footprint. Full benchmark below.

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

• Model Context Protocol (FastMCP v2) & Coding Agent Support:
DocHarvest includes a built-in FastMCP v2 server (`docharvest mcp`) exposing 12 native tools over stdio for coding assistants like Cursor, Claude Code, OpenCode, Pi Coding Agent, and Windsurf. For non-terminal workflows, we also bundle a standalone desktop application built with PyWebView, React 18, and shadcn/ui.

---

### What DocHarvest deliberately does not do

Honest scope, because a tool that claims everything has earned none of your trust:

- It will not bypass logins, paywalls, or CAPTCHAs. It targets public technical documentation that welcomes developer access.
- It is not for e-commerce catalogs, social feeds, or internet-scale crawling. It is a documentation compiler, not a search-engine crawler.
- On unknown platforms it falls back to generic heuristics (`main`/`article` selector chains + readability-style cleaning). That is good, but not platform-perfect — if you hit an extraction edge case, I want the URL.

---

### Real-World Benchmark:
Crawling the complete OpenAlgo documentation suite (673 pages):
- Crawl & Extraction Time: 18.2 seconds (5 streaming workers)
- Raw HTML Size: ~28.4 MB (estimated ~7.1M tokens)
- DocHarvest Clean Markdown Size: 5.0 MB (estimated ~1.2M tokens)
- Token Reduction: ~82.8% (≈83%) reduction in context window footprint
- Output: 673 modular pages, 1 unified `book.md`, 1 `llms.txt`, 1 RAG JSONL dataset, 1 styled PDF.

The project is 100% free, MIT-licensed, and runs completely locally on your hardware with zero telemetry or external API keys.

GitHub: https://github.com/RohannShetty/gitbook-downloader
Web Showcase: https://rohannshetty.github.io/gitbook-downloader/

Two specific asks for the HN crowd:

1. Point it at the gnarliest public docs portal you know and tell me exactly what extraction got wrong — edge-case URLs become test fixtures, and prior edge cases are why the language-code filtering (60+ locales) and permalink dedup exist.
2. If you run RAG pipelines, tell me your chunking strategy — I want to benchmark the AST header splitter against it rather than assert it is better.
```

---

## 3. Anticipated HN Technical Questions & Prepared Responses

### Q1: "Why build a custom parser instead of using Playwright / Puppeteer with Mozilla Readability?"
> **Prepared Answer:**  
> Playwright/Chromium is fantastic for dynamic single-page applications, but it introduces significant overhead: 200MB+ RAM per browser context, heavy binary dependencies, and slow execution when crawling 1,000+ pages. 
> 
> Technical documentation platforms (GitBook, Mintlify, Docusaurus) follow structured architectural conventions. By probing native `.md` endpoints, parsing sitemaps, and applying AST-level clean selectors, DocHarvest achieves ~37 pages/sec sustained (673 pages / 18.2 s) with an ultra-lightweight memory footprint (<50MB RAM in CI/CD) and zero browser automation dependencies.

---

### Q2: "How do you handle rate limiting, CAPTCHAs, or bot protection like Cloudflare?"
> **Prepared Answer:**  
> DocHarvest is specifically designed for public technical documentation sites that encourage developer access. We implement polite, respectful crawling:
> 1. Bounded parallelism via `--workers N` (8 by default), with socket connect timeouts through a custom `TimeoutHTTPAdapter` so connections neither hang nor hammer.
> 2. Sitemap-first discovery to minimize unnecessary GET requests.
> 3. A configurable custom User-Agent via `create_session(user_agent=...)` in the Python API.
>
> It deliberately does not handle authenticated sessions or bypass bot protection — if a portal sits behind a login wall, it is outside DocHarvest's scope by design.

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
> DocHarvest implements the Model Context Protocol specification over standard input/output (stdio JSON-RPC). When you add DocHarvest as an MCP server in Cursor (`.cursor/mcp.json`) or Claude Desktop (`claude_desktop_config.json`), the agent gets 12 tools plus resources and prompts, including:
> - `download_docs(url)`: Harvests a documentation site in the background.
> - `search_docs(query)`: Performs BM25 full-text search against the local SQLite FTS5 index.
> - `read_doc(domain, path, topic, max_tokens)`: Retrieves a specific page or topic section with AST-safe token bounding — code blocks are never split.
> - `find_docs(query)`: Resolves a library name like "react" or "nextjs" to indexed domains.
> - `diff_versions(domain, v1, v2)`: Unified diff between two documentation snapshots.
>
> (Full inventory: `download_docs`, `search_docs`, `find_docs`, `read_doc`, `get_doc`, `list_domains`, `query_doc_graph`, `get_related_concepts`, `diff_versions`, `list_versions`, `export_docs`, `get_changelog`.)
>
> This allows the AI agent to autonomously look up exact SDK documentation without human intervention.

### Q6: "Why not just use r.jina.ai or the site's llms.txt directly?"
> **Prepared Answer:**  
> Three gaps. `r.jina.ai` is single-page and cloud-hosted — every lookup needs a network round trip and sends your browsing to a third party; DocHarvest compiles an entire hierarchy once and serves it locally forever after. `llms.txt` only exists if the site publishes it, and it's a link index, not content — you still have to fetch and clean every page. And neither provides provenance (SHA-256 hashes, source URLs in frontmatter), snapshot diffing, or a local BM25 index. DocHarvest probes a site's `llms.txt`/sitemap when present and goes further: it compiles, hashes, versions, indexes, and serves the result to agents over MCP.

---

### Q7: "How is this different from Crawl4AI?"
> **Prepared Answer:**  
> Crawl4AI is a solid general-purpose LLM crawler, and I'd recommend it for arbitrary sites. The differences are in defaults and deliverables: Crawl4AI leans on Playwright/Chromium (heavy in CI), needs per-site extraction rules written by you, and returns raw dicts. DocHarvest ships platform heuristics for 8 documentation frameworks out of the box, probes native `.md` endpoints where they exist, and every capture produces the same deterministic output contract — `pages/` with hashed frontmatter, `book.md`, `llms.txt`, RAG JSONL, PDF — plus semver snapshots with unified diffs and a local FTS5 search index. Different tools for different jobs; I optimize for "point at a docs portal, get a finished corpus."

---

## 4. Hacker News Discussion Moderation Rules

1. **Be humble and receptive:** Acknowledge edge cases openly. If someone shows an exotic documentation format where extraction broke, thank them, create a reproducible test case, and commit a fix.
2. **Never downvote or argue:** Answer criticism with code, benchmarks, and architecture explanations.
3. **Keep replies concise and readable:** Format code snippets in mono; avoid marketing jargon.
4. **Active monitoring:** Keep the HN tab open and refresh every 5–10 minutes for the first 6 hours of the submission.

---

## 5. Psychology Notes (Why the Copy Is Structured This Way)

For the operator, not for posting:

1. **Number-first opening (Anchoring):** "18.2 seconds, ~83% cut" in line 1 frames every subsequent claim. HN readers decide in the first two sentences whether to keep reading.
2. **Vivid loss framing (Loss Aversion / Availability Heuristic):** The four bottlenecks are written as failures the reader has personally experienced (cookie banners, scrambled indentation), not as abstract feature categories.
3. **"Deliberately does not do" section (Pratfall Effect):** Admitting scope limits before critics find them measurably increases trust in the remaining claims — and preempts the inevitable "can it scrape my Instagram?" thread.
4. **Specific asks at the end (Peak-End Rule + Commitment):** "Give me your worst docs URL" converts readers into contributors and seeds test fixtures — the comment thread ends on an action, not a thank-you.
5. **No scarcity, no urgency tactics:** On HN these read as SaaS-pattern noise and would contradict the "quietly confident" voice. Credibility is the only currency here.
