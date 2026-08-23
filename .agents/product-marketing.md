# Product Marketing Context

**Document version:** v1  
**Last updated:** 2026-08-23  

---

## Product Overview

**One-liner:**  
Turn Any Documentation Site into LLM-Ready Markdown, Vector Context & Offline Books.

**What it does:**  
DocHarvest is a high-performance, open-source documentation harvesting and AI context preparation platform available as a scriptable CLI, desktop GUI (React 18 + shadcn/ui), and autonomous Model Context Protocol (MCP) server. It automatically detects documentation platforms (GitBook, Mintlify, Docusaurus, ReadTheDocs, and generic doc sites), bounds crawls strictly to documentation roots, extracts pristine markdown via direct `.md` endpoint probing and AST-based cleaning, and compiles structured output corpora. Every capture yields a deterministic Four-Part Output Contract: clean per-page Markdown trees with cryptographic SHA-256 YAML frontmatter, a consolidated `book.md` handbook with auto-generated Table of Contents, an `llms.txt` agent manifest, and structured exports (RAG JSONL, pure-Python printable PDF via `fpdf2`, and SQLite FTS5 BM25 search indexing).

**Product category:**  
Developer Tools · AI & LLM Infrastructure · Knowledge Engineering · Offline Documentation & Archival

**Product type:**  
Open-source developer tool & local application (CLI / TUI / Desktop GUI / FastMCP Server)

**Business model:**  
100% Free & Open Source Software (MIT License); self-hosted, air-gapped, zero cloud dependencies, zero telemetry.

---

## Target Audience

**Target companies:**  
- **AI Startups & LLM Labs:** Teams building RAG applications, autonomous agents, and domain-adapted code assistants requiring clean, token-efficient technical corpora.
- **Enterprise Engineering Organizations:** Companies maintaining large internal developer portals, managing complex third-party software dependencies, or enforcing air-gapped development environments.
- **Developer Tools & Infrastructure Companies:** Teams needing to mirror, monitor, and index upstream documentation from partners and dependencies.
- **Security, Defense & Field Engineering:** Organizations operating in isolated networks, SCADA environments, and offline research facilities requiring reliable local technical documentation.

**Decision-makers & Champions:**  
- AI/ML Engineers & RAG Architects (Champions / Primary Users)
- Senior Software Engineers & Tech Leads (Users & Champions)
- DevOps, SRE & Platform Engineers (Implementers)
- Engineering Managers & Directors of Engineering (Decision-Makers)

**Primary use case:**  
Automated extraction, sanitization, and structured compilation of entire technical documentation websites into noise-free Markdown, vector-ready JSONL datasets, offline PDF handbooks, and agent-queryable MCP servers.

**Jobs to be done:**  
1. *AI & Vector Ingestion:* "Feed entire multi-hundred-page documentation portals into vector databases (ChromaDB, Pinecone, Qdrant) and AI coding assistants (Cursor, Claude Code, Windsurf) without burning 50% of our context window on HTML navigation noise, cookie banners, and malformed code snippets."
2. *Offline Knowledge Compilation:* "Convert dynamic, JavaScript-heavy web documentation into a single, cohesive, offline Markdown book or beautifully formatted PDF handbook with a complete Table of Contents for air-gapped research or travel."
3. *Documentation Mirroring & Change Auditing:* "Automate scheduled snapshots of critical vendor documentation in CI/CD pipelines to track API deprecations, schema shifts, and breaking changes with semver diffs and zero-maintenance lockfiles."

**Specific use cases & scenarios:**  
- **Zero-Friction RAG Datasets:** Generating pre-chunked JSONL datasets and `llms.txt` files for LangChain and LlamaIndex knowledge retrieval pipelines in 30 seconds.
- **Autonomous Coding Agent Context:** Connecting Cursor or Claude Desktop to DocHarvest's built-in FastMCP server so the agent can autonomously discover, search, and read external library docs on demand.
- **In-Flight & Offline Development:** Downloading full documentation suites (e.g., Next.js, PyTorch, Kubernetes) into consolidated `book.md` handbooks and querying them instantly via local SQLite FTS5 BM25 search.
- **API Deprecation & Drift Tracking:** Running automated daily GitHub Actions jobs with DocHarvest to snapshot partner API documentation and generate unified diff reports on changes.

---

## Personas

| Persona | Cares About | Core Challenge | Value We Promise |
|---|---|---|---|
| **AI & RAG Engineers** | Token economy, AST chunk boundary integrity, citation grounding, zero HTML noise, agent interoperability (`llms.txt`, MCP). | Raw web scrapers produce messy HTML soup, scrambled code blocks, and lack cryptographic metadata, leading to high token costs and LLM hallucinations. | Zero-noise Markdown with YAML frontmatter (SHA-256 hashes, source URLs), RAG JSONL export, AST header chunking, and instant FastMCP agent integration. |
| **Offline Developers & Researchers** | Portability, readability, unified search, zero-dependency PDF generation, single-file handbooks, offline access. | Modern doc portals require active JavaScript and break browser "Save Page As", while `wget` creates unnavigable directories of broken HTML assets. | Single consolidated `book.md` with TOC, pure-Python styled PDF export (`fpdf2`), local SQLite FTS5 search across all docs, and an in-app reader. |
| **DevOps & Archival Teams** | CI/CD automation, atomic writes, lockfile safety, process recovery, version control, semver diffing. | Custom scraping scripts frequently crash, hang on dynamic SPAs, leave stale lockfiles, and lack automated diffing for documentation drift. | Headless CLI/presets, self-recovering process-aware domain locks, atomic file replacement, automated semver snapshotting (`v1.0.0` → `v1.0.1`), and unified diffs. |

---

### Persona 1: AI & RAG Engineers

- **Profile & Roles:** AI Engineers, LLM Application Developers, RAG Architects, Agentic Workflow Builders.
- **Tech Stack:** LangChain, LlamaIndex, ChromaDB, Pinecone, Weaviate, Qdrant, Cursor, Claude Code, Windsurf, Ollama, vLLM, OpenAI Embeddings.
- **Daily Workflows:**
  - Ingesting upstream SDK, library, and framework documentation into vector databases for semantic search.
  - Chunking markdown technical content at semantic section boundaries for retrieval pipelines.
  - Providing fresh, accurate documentation context to AI coding agents to eliminate outdated API hallucinations.
- **Trigger Events:**
  - Upgrading to a major framework version whose documentation is not yet included in standard LLM training cutoffs.
  - LLMs hallucinating deprecated functions because context chunks contain corrupted or incomplete code examples.
  - Need to quickly index 500+ pages of vendor documentation for a retrieval evaluation benchmark.
- **Success Metrics:**
  - 100% clean markdown without HTML tags, cookie notices, or navigation headers.
  - Context token savings of 40–60% compared to raw HTML dumps.
  - Zero severed code blocks or mid-paragraph chunk splits.
  - Sub-second vector retrieval with verifiable citation source URLs and content hashes.

---

### Persona 2: Offline Developers & Researchers

- **Profile & Roles:** Software Engineers, Systems Architects, Mobile Developers, Field Researchers, Air-Gapped Security Engineers.
- **Tech Stack:** Local IDEs (VS Code, Neovim, JetBrains), Python, Rust, Go, SQLite, local terminal environments.
- **Daily Workflows:**
  - Writing code during long flights, commutes, or remote field assignments without internet connectivity.
  - Referencing complex architecture manuals and API specs in secure, isolated development environments.
  - Reading technical books and documentation on e-readers or tablets as formatted PDFs.
- **Trigger Events:**
  - Preparing for international travel or working from locations with unreliable connectivity.
  - Transitioning into an air-gapped, zero-trust network environment where external web requests are blocked.
  - Frustration with opening 50 browser tabs to cross-reference documentation chapters.
- **Success Metrics:**
  - One consolidated `book.md` containing the entire documentation hierarchy in natural reading order.
  - Beautifully formatted printable PDFs with syntax-highlighted code blocks and page numbers generated with zero C-dependencies.
  - Instant BM25 full-text search across downloaded docs directly from the terminal or desktop GUI.

---

### Persona 3: DevOps & Archival Teams

- **Profile & Roles:** DevOps Engineers, Platform Engineers, Site Reliability Engineers (SREs), Compliance Officers.
- **Tech Stack:** GitHub Actions, GitLab CI, Docker, Kubernetes, Linux servers, Bash/Python automation scripts.
- **Daily Workflows:**
  - Running automated scheduled pipelines to mirror and back up third-party documentation.
  - Auditing changes in vendor APIs, cloud documentation, and regulatory frameworks.
  - Maintaining immutable documentation archives with cryptographic verification.
- **Trigger Events:**
  - A vendor silently alters an API endpoint schema or deprecates an integration without a changelog entry.
  - Compliance audit requiring historical snapshots of external documentation as it existed on a specific date.
  - Fragile bespoke scraping scripts failing in CI due to network timeouts or stale process locks.
- **Success Metrics:**
  - 100% reliable CI execution with zero-dependency standalone binaries or lightweight Python packages.
  - Automatic semver snapshotting (`v1.0.0` → `v1.0.1`) with instant unified diff reports.
  - Crash-resilient file I/O with atomic file writes and self-recovering active-PID domain locks.

---

## Problems & Pain Points

### Core Problem
Developers and AI engineers cannot reliably capture, clean, and structure modern web documentation. Current approaches produce either raw HTML noise that overwhelms LLM context windows, fragmented directory structures with broken links, or costly reliance on metered, cloud-hosted scraper APIs that compromise data privacy.

### Why Alternatives Fall Short
- **Raw `curl` / `wget` / BeautifulSoup Scripts:** Output raw HTML with massive CSS/JS navigation boilerplate, broken relative links, and zero platform-specific metadata extraction.
- **Headless Browser Frameworks (Puppeteer / Playwright):** Require heavy runtime dependencies, consume hundreds of megabytes of RAM per crawl, and frequently crash or hang in CI environments.
- **Hosted Cloud Scrapers (Firecrawl / Spider API / Jina Reader):** Metered per-page pricing that gets expensive quickly, potential rate limits, and exfiltration of proprietary or internal documentation URLs to third-party cloud servers.
- **Browser "Save Page As" & Print-to-PDF:** Only saves single pages, fails on dynamic Single-Page Applications (SPAs), and generates unreadable, poorly paginated PDFs with missing code block styling.
- **Manual Copy-Pasting:** Inefficient, human-error prone, impossible to maintain over multi-hundred-page sites, and lacks version history.

### What It Costs Them
- **Wasted AI Spend:** 40–60% of LLM context window tokens consumed by boilerplate HTML navigation, footers, and scripts instead of actual documentation content.
- **Engineering Time Loss:** Hours wasted manually cleaning markdown, fixing broken code indentations, and reorganizing page hierarchies.
- **Hallucination Risk:** Vector retrieval pipelines returning ungrounded chunks without source URLs or section context, leading to inaccurate AI code generation.
- **Operational Blindness:** Undetected upstream API breakages that cause production outages because teams had no automated way to diff documentation changes.

### Emotional Tension
- **Frustration:** Watching expensive LLMs hallucinate incorrect code because the fed documentation was scrambled or polluted with UI noise.
- **Anxiety:** Fear of boarding a 10-hour flight or entering an air-gapped facility only to discover that saved documentation is missing critical chapters or broken.
- **Apprehension:** Worrying about passing proprietary internal documentation links to third-party cloud scraping services.

---

## Feature Breakdown & Capabilities Matrix

| Functional Category | Capability / Feature | Technical Implementation | Benefit to User |
|---|---|---|---|
| **Extraction & Intelligence** | **Provider Auto-Detection** | `ProviderRegistry` with prioritized heuristic inspection (GitBook: 100, Mintlify: 90, Docusaurus: 80, ReadTheDocs: 70, Generic: 0). | Zero configuration required; automatically applies platform-tailored extraction logic. |
| | **Direct `.md` Endpoint Probing** | Probes `<url>.md` endpoints on modern platforms (GitBook, Mintlify, Docusaurus). | Retrieves pristine, author-formatted Markdown directly from the source without HTML conversion loss. |
| | **Doc-Root Auto-Scoping** | Path inspection detecting documentation anchors (`/docs`, `/guide`, `/v2`) and walking hierarchy. | Deep link input automatically scopes to the full documentation root without manual path setting. |
| | **Clean-Crawl Safeguards** | Language-code filtering (60+ locales: `/zh/`, `/es/`, `/ja/`), anchor stripping (`¶`), and breadcrumb removal. | Eliminates duplicate localized pages and navigational UI debris from final corpora. |
| | **Relative Link Rewriting** | AST-based link transformation rewriting absolute URLs to relative markdown paths. | Complete offline navigation across markdown files without dead external links. |
| **Output Contract** | **Page Tree (`pages/`)** | Structured directory hierarchy mirroring site URL paths with traversal sanitization. | Clean, modular markdown structure matching the original documentation architecture. |
| | **Cryptographic YAML Frontmatter** | Prepend headers: `source_url`, `title`, `crawl_date`, `content_hash` (SHA-256), `site_version`. | Deterministic provenance, perfect citation grounding, and instant content integrity verification. |
| | **Consolidated Handbook (`book.md`)** | Natural sort order concatenation with demoted `#` headings and generated Table of Contents. | Single searchable, scrollable handbook ideal for offline reading and global LLM ingestion. |
| | **LLM Manifest (`llms.txt`)** | Standardized index listing all captured pages and corresponding source URLs. | Direct compatibility with AI agents adhering to the `llms.txt` discovery specification. |
| **Export Studio** | **Pure-Python PDF Generation** | Custom layout engine built on `fpdf2` with syntax-highlighted code cells and page numbers. | Generates publication-quality printable PDFs without requiring WeasyPrint, wkhtmltopdf, or C-libraries. |
| | **RAG JSONL Export** | JSON lines serialization (`id`, `domain`, `title`, `path`, `text`, `length`). | 1-click dataset preparation ready for LangChain, LlamaIndex, and vector database ingestion. |
| | **RAG Metadata Wrapper** | HTML comment envelope (`<!-- domain: ..., source: ..., chunk: 1/N -->`). | Preserves section heading context and source citations directly inside vector chunks. |
| | **AST Markdown Splitter** | `splitter.py` header-aware chunker splitting strictly on `#` section boundaries. | Partitions oversized files into manageable chunks without splitting code blocks or paragraphs. |
| **Storage & Reliability** | **Atomic File Operations** | Temporary file staging with `os.replace` and `os.fsync` barriers. | Guarantees zero partially written or corrupted files during unexpected interruptions. |
| | **Process-Aware Domain Locks** | Active PID validation (Windows `Kernel32.OpenProcess` / POSIX `kill(pid, 0)`). | Prevents concurrent write collisions while automatically recovering from abandoned or stale locks. |
| | **Semver Snapshotting & Diff** | Pre-capture snapshots (`v1.0.0` → `v1.0.1`), unified diffing, and automated changelogs. | Immediate visibility into upstream documentation updates, additions, and deprecations. |
| | **SQLite FTS5 BM25 Search** | Embedded SQLite full-text search with `porter unicode61` stemming and snippet highlights. | Instant sub-second search across all harvested documentation libraries from CLI or GUI. |
| **Interfaces** | **FastMCP Server** | stdio JSON-RPC server exposing 8 tools (`download_docs`, `search_docs`, `read_doc_page`, etc.). | Empowers Cursor, Claude Desktop, and autonomous agents to harvest and query docs dynamically. |
| | **Desktop GUI** | PyWebView desktop shell with React 18, Vite, Tailwind CSS, shadcn/ui, and live crawl terminal. | Beautiful visual workflow with radial progress gauges, in-app doc reader, and batch capture queue. |
| | **Scriptable CLI / TUI** | Ergonomic argparse CLI with bare URL sugar (`gitbook-dl <url>`) and curses TUI. | Effortless integration into terminal workflows, shell scripts, and CI/CD pipelines. |

---

## Competitive Landscape

### Direct Competitors
- **Firecrawl / Spider API:** Cloud-hosted, metered API services that scrape websites and return markdown.  
  *Falls short because:* Requires paid subscriptions for volume, routes sensitive documentation URLs through third-party servers, lacks local SQLite FTS5 search libraries, and cannot run in air-gapped environments.
- **Crawl4AI:** Python-based open-source crawler tailored for LLMs.  
  *Falls short because:* Requires heavy Playwright/Chromium dependencies, lacks automatic doc-platform heuristics (GitBook/Mintlify/Docusaurus direct `.md` probing), lacks built-in semver snapshot diffing, and requires custom coding to produce clean book/PDF outputs.
- **Jina Reader (`r.jina.ai`):** Cloud proxy prepending URLs to fetch markdown.  
  *Falls short because:* Single-page oriented, lacks full-site hierarchical compilation (`pages/`, `book.md`, `llms.txt`), provides no local search indexing, and requires active internet access for every lookup.

### Secondary Competitors
- **HTTrack / `wget` / `curl` Scripts:** Legacy offline website mirror tools.  
  *Falls short because:* Dumps raw HTML, broken CSS, and Javascript assets; provides zero markdown conversion; fails on modern Single-Page Applications; and creates massive, unsearchable directory trees.
- **SingleFile / Monolith Browser Extensions:** Extensions that bundle a webpage into a self-contained HTML file.  
  *Falls short because:* Manual, single-page process with no batch crawling, no markdown/JSONL/PDF conversion, no frontmatter metadata, and no integration with AI agent workflows.

### Indirect Competitors
- **Manual Copy-Paste / Notion Import:** Copying documentation text manually into personal note-taking apps.  
  *Falls short because:* Unmaintainable for large documentation suites, loses code block formatting, lacks synchronization with upstream updates, and takes hours of manual labor.

---

### In-Depth Competitive Comparison Matrix

| Capability / Dimension | **DocHarvest** | **Raw curl / wget** | **Firecrawl / Spider API** | **Crawl4AI** | **Jina Reader** |
|---|:---:|:---:|:---:|:---:|:---:|
| **Cost & License** | **Free / MIT Open Source** | Free (Built-in) | Paid SaaS ($/page) | Free / Apache 2.0 | Paid / Freemium Cloud |
| **Execution Model** | **100% Local / Air-Gap** | Local | Hosted Cloud Service | Local (Heavy Engine) | Hosted Cloud Proxy |
| **Data Privacy** | **Zero Telemetry / Private** | 100% Private | Data sent to Cloud | 100% Private | Data sent to Cloud |
| **Provider Heuristics** | **Automatic (5 Platforms)** | None | Generic Heuristics | Manual Rule Writing | Generic Heuristics |
| **Direct `.md` Endpoint Probing** | **Yes (GitBook, Mintlify, Docusaurus)** | No | No | No | No |
| **Output Contract (`pages/`, `book.md`, `llms.txt`)** | **Standardized & Deterministic** | Raw HTML Soup | Single Markdown String | Raw Python Dict | Markdown String |
| **Cryptographic YAML Frontmatter** | **Yes (SHA-256 Hashes)** | No | No | No | No |
| **Export Studio (JSONL, PDF, Markdown)** | **Yes (Built-in `fpdf2` Engine)** | No | No | Custom code needed | No |
| **External C-Dependencies for PDF** | **Zero (Pure Python)** | N/A | Cloud-generated | Requires WeasyPrint | No PDF export |
| **Local SQLite FTS5 BM25 Search** | **Yes (Persistent Library)** | No | No | No | No |
| **Semver Snapshotting & Diffs** | **Yes (`v1.0.0` → `v1.0.1`)** | No | No | No | No |
| **Model Context Protocol (MCP)** | **Yes (8 native tools)** | No | Limited REST API | No | No |
| **Desktop GUI (React + shadcn/ui)** | **Yes (Built-in)** | No | Web Dashboard | No | No |
| **Subpath Doc-Root Auto-Expansion** | **Yes (Automatic)** | No (Crawls everything) | No | No | No |
| **Memory Footprint in CI** | **Ultra-Light (<50MB)** | Ultra-Light | Cloud-delegated | Heavy (Playwright / Chromium) | Cloud-delegated |

---

## Differentiation

### Key Differentiators
1. **The Four-Part Output Contract:** Every download produces a standardized, deterministic corpus: modular `pages/**/*.md` with YAML frontmatter (SHA-256 hash, source URL, crawl date), a consolidated `book.md` with auto-generated TOC, an `llms.txt` manifest, and search index entries.
2. **Platform-Aware Extraction Pipeline:** Detects GitBook, Mintlify, Docusaurus, and ReadTheDocs to probe native `.md` endpoints directly—bypassing HTML conversion entirely and capturing author-intended formatting.
3. **Pure-Python Printable PDF Studio:** Generates publication-grade PDFs with custom headers, styled code blocks, and page numbers using pure Python (`fpdf2`) with zero external C-libraries (no WeasyPrint or wkhtmltopdf headaches).
4. **Local Knowledge Infrastructure:** Built-in SQLite FTS5 search index with BM25 ranking and unified semver diffing (`gitbook-dl diff domain v1.0.0 v1.0.1`) for instant change tracking.
5. **Universal Interface Ecosystem:** Seamlessly operate via ergonomic CLI, visual React 18 Desktop GUI, or connect coding assistants directly via the 8-tool FastMCP server.
6. **100% Private, Free & Air-Gapped:** Zero cloud API keys, zero per-page fees, zero network telemetry. Runs entirely on your local hardware.

### How We Do It Differently
Instead of treating documentation as generic web pages to be blindly scraped with a headless browser, DocHarvest treats documentation as **structured technical knowledge**. It understands documentation hierarchy, platform conventions, code block formatting, section anchoring, and LLM context requirements.

### Why That's Better
- **Context Efficiency:** Eliminates token-wasting HTML chrome, navigation menus, and footers before content reaches the LLM.
- **Deterministic Reliability:** Cryptographic SHA-256 hashes in YAML frontmatter guarantee that vector embeddings are always grounded in verified source content.
- **Operational Simplicity:** Standalone single-binary execution without managing headless browser drivers, Docker containers, or third-party cloud subscriptions.

### Why Customers Choose DocHarvest
- AI developers choose DocHarvest because it transforms 500-page doc sites into clean RAG datasets and `llms.txt` files in 30 seconds.
- Offline engineers choose DocHarvest because it delivers a single, searchable `book.md` and high-quality PDF with zero broken links.
- DevOps teams choose DocHarvest because it runs reliably in CI with atomic writes, self-recovering locks, and automated snapshot diffs.

---

## Objections & Objection Handling Matrix

| Objection | Customer Perception | DocHarvest Reality & Response |
|---|---|---|
| *"Isn't this just another scraper? I can write a 10-line Python script with BeautifulSoup or curl."* | "Scraping is trivial; a basic script is good enough." | A 10-line script produces messy HTML soup with broken navigation, corrupted code indentation, missing images, and dead relative links. DocHarvest gives you an **engineered knowledge corpus**: platform detection, direct `.md` endpoint extraction, doc-root scoping, relative link resolution, SHA-256 YAML frontmatter, `llms.txt` generation, pure-Python PDF export, and SQLite FTS5 search. |
| *"Why not just use Firecrawl, Jina Reader, or a hosted cloud API?"* | "Hosted APIs are easier and require no local maintenance." | Hosted APIs charge per-page fees that escalate quickly on large documentation suites, require internet connectivity, send your proprietary documentation URLs to external clouds, and do not provide a local searchable library, PDF generator, or semver diff engine. DocHarvest is **100% free, open-source, private, and runs entirely offline**. |
| *"Does it work on JavaScript Single-Page Applications (SPAs) like React or Nextra docs?"* | "Static crawlers get empty `div id=root` shells on SPAs." | Modern documentation SPAs (GitBook, Mintlify, Docusaurus) publish underlying `.md` raw endpoints, `/llms.txt`, and `/sitemap.xml` manifests that DocHarvest probes first. For client-rendered pages, its heuristic content selector chain extracts the structured article DOM cleanly without running heavy browser engines. |
| *"Will it crash, hang, or exhaust memory on massive 2,000-page doc portals?"* | "Python crawlers balloon memory and get blocked." | DocHarvest uses a bounded `ThreadPoolExecutor` with socket connect timeouts, cooperative cancellation, atomic disk streaming, and memory-safe AST chunking. It streams content directly to atomic disk files with minimal RAM consumption. |
| *"How do I know the captured LLM context is complete and faithful?"* | "Scrapers silently drop pages or scramble headings." | Every single page includes a cryptographic SHA-256 content hash and exact `source_url` in its YAML frontmatter. The `llms.txt` manifest provides a verified inventory, and the `diff` command makes upstream modifications immediately visible. |
| *"What about rate limits, CAPTCHAs, or IP blocking during large crawls?"* | "Target sites will ban my IP if I crawl too fast." | DocHarvest crawls respectfully with configurable concurrency, polite delay intervals, custom User-Agents, and sitemap-first discovery that avoids aggressive recursive link discovery. |
| *"What about copyright and terms of service for downloading docs?"* | "Is it legally safe to harvest public documentation?" | Public documentation is intended for developer consumption. DocHarvest operates as a client-side user agent for local offline reading and private context indexing, retaining all original copyright headers, author attributes, and source URLs. |

### Anti-Personas (Who Is NOT a Good Fit)
- **E-Commerce & Social Media Web Scrapers:** Users looking to scrape dynamic e-commerce catalogs, price scrapers, or social media feeds behind CAPTCHAs, Cloudflare turnstiles, or login walls. DocHarvest is purpose-built for public technical documentation.
- **Raw Web Crawling at Internet Scale:** Users seeking to crawl millions of arbitrary websites across the open internet (use Common Crawl, Scrapy, or Apache Nutch).
- **Users Needing Managed Cloud Webhooks:** Teams wanting a hosted SaaS dashboard with credit card billing to manage web scraping tasks on someone else's servers.

---

## Switching Dynamics

The Jobs-to-be-Done (JTBD) Four Forces driving adoption of DocHarvest:

```
                  PUSH of Current Frustrations
   (Messy HTML soup, token bloat, paid API bills, broken PDF prints)
                              │
                              ▼
        ┌───────────────────────────────────────────┐
        │        SWITCH TO DOCHARVEST               │
        └───────────────────────────────────────────┘
                              ▲
                              │
                   PULL of New Possibilities
  (1-click RAG JSONL, FastMCP server, book.md, SQLite FTS5, 100% free)

   ─────────────────────────────────────────────────────────────────

                      HABIT of the Present
          ("I'll just copy-paste these 5 pages manually",
           "I already have a hacky Python script")
                              │
                              ▼
        ┌───────────────────────────────────────────┐
        │        STAY WITH CURRENT APPROACH         │
        └───────────────────────────────────────────┘
                              ▲
                              │
                    ANXIETY of the Unknown
           ("Will it miss dynamic React pages?",
            "Will it take long to learn a new tool?")
```

### Push (Frustrations with Current Solutions)
- Burning monthly OpenAI/Anthropic API budgets on token-heavy HTML navigation boilerplate.
- Frustration when AI coding assistants hallucinate syntax because of scrambled code indentation in scraped docs.
- Getting hit with surprise credit-card charges from cloud scraping SaaS APIs on large crawls.
- Inability to read or search developer documentation while traveling or working offline.

### Pull (Attractions of DocHarvest)
- Instant generation of `llms.txt`, RAG-ready JSONL, and consolidated `book.md` with one command.
- Autonomous FastMCP integration allowing Cursor and Claude Code to search and read documentation directly.
- Pure-Python printable PDF generation with zero external C-dependencies.
- 100% free, private, local, and open-source execution with zero cloud telemetry.

### Habit (Friction to Overcome)
- The inertia of writing one-off BeautifulSoup scripts or manually copy-pasting pages into notes.  
  *Overcome by:* Zero-config CLI (`gitbook-dl <url>`) and standalone Desktop GUI that works instantly with no setup.

### Anxiety (Fears of Switching)
- Fear that local crawlers will miss client-rendered pages or consume massive disk space.  
  *Overcome by:* Automatic provider heuristics, doc-root scoping, direct `.md` probing, and atomic write safety.

---

## Customer Language

### How Customers Describe the Problem (Verbatim)
- *"I'm spending half my prompt tokens on HTML navbars, footer links, and cookie popups instead of actual API docs."*
- *"I tried using curl and pandoc, but the code indentation got completely destroyed and Python examples fail to parse."*
- *"I have a 10-hour flight tomorrow and need the complete documentation for three new libraries, but browser 'Save Page As' only saves the landing page."*
- *"Our cloud scraping API bill tripled this month just because we indexed a 1,500-page framework documentation site."*
- *"The vendor updated their API documentation without writing a changelog, and our integration silently broke in staging."*

### How Customers Describe DocHarvest (Verbatim)
- *"DocHarvest gave me a clean, chunked JSONL file with SHA-256 hashes ready for ChromaDB in 30 seconds."*
- *"It compiled 400 pages of online docs into a single, perfectly formatted PDF handbook with a table of contents that I can read anywhere."*
- *"The FastMCP server let my Cursor agent look up fresh documentation on its own without me copying links."*
- *"The snapshot diff feature caught a breaking API deprecation before we shipped our quarterly release."*

### Words & Phrases to Use
- **Capture / Harvest** (instead of "scrape")
- **LLM-Ready Markdown**
- **Four-Part Output Contract**
- **Vector Context & RAG Datasets**
- **Consolidated Handbook (`book.md`)**
- **Cryptographic YAML Frontmatter**
- **AST Header Chunking**
- **Model Context Protocol (FastMCP)**
- **Semver Snapshot Diffing**
- **SQLite FTS5 BM25 Search**
- **Deterministic & Local-First**

### Words & Phrases to Avoid
- *Scrape / Scraper* (implies brittle, dirty, spammy crawling)
- *Supercharge / Revolutionary / Blazing-fast* (unsubstantiated marketing fluff)
- *Headless Browser Automation* (DocHarvest is lightweight and AST/HTTP-driven)
- *Cloud-native / SaaS* (DocHarvest is strictly local-first and self-hosted)

---

### Product Glossary

| Term | Technical Meaning in DocHarvest |
|---|---|
| **Provider Registry** | The prioritized heuristic pipeline (`ProviderRegistry`) that inspects URLs and HTML signals to select the optimal platform extractor (GitBook, Mintlify, Docusaurus, ReadTheDocs, Generic). |
| **Output Contract** | The deterministic 4-part directory structure produced by every capture: `pages/**/*.md` with YAML frontmatter, `book.md` with TOC, `llms.txt` manifest, and search index entries. |
| **Consolidated Book (`book.md`)** | A single concatenated Markdown file compiling the entire documentation tree in natural reading order with auto-demoted `#` headings and a generated Table of Contents. |
| **AST Splitter** | The chunking engine (`splitter.py`) that divides markdown files strictly along `#` section header boundaries without splitting code blocks or paragraph tokens. |
| **FastMCP Server** | The Model Context Protocol implementation (`mcp/server.py`) exposing 8 JSON-RPC tools over stdio for AI coding assistants like Cursor and Claude. |
| **DomainLock** | The cross-platform, process-aware concurrency lock (`StorageManager`) that validates active PIDs (Windows Kernel32 / POSIX `os.kill`) and reclaims dead locks. |
| **Semver Snapshot** | An automated pre-capture backup mechanism (`VersionManager`) that archives existing documentation to `versions/v1.0.X.md` and generates unified diffs. |
| **FTS5 BM25 Index** | The embedded SQLite full-text search index (`search/index.py`) providing sub-second token matching with `porter unicode61` stemming. |

---

## Brand Voice & Positioning

### Brand Personality & Tone
- **Precise & Pragmatic:** We explain technical realities accurately without hand-waving or hype. We show the exact CLI command and the resulting file tree.
- **Quietly Confident:** We demonstrate superiority through clean code output, zero-dependency PDFs, and verified test suites rather than marketing superlatives.
- **Developer-Centric & Open:** We respect developer privacy, local computing resources, and the open-source ethos. No telemetry, no upsells, no artificial paywalls.

### Messaging Pillars

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                DOCHARVEST MESSAGING PILLARS                            │
├─────────────────────────┬─────────────────────────────┬────────────────────────────────┤
│   1. CLEAN & LLM-READY  │   2. LOCAL & INDEPENDENT    │    3. DETERMINISTIC & SAFE     │
├─────────────────────────┼─────────────────────────────┼────────────────────────────────┤
│ • Zero HTML/CSS chrome  │ • 100% free & open-source   │ • Four-Part Output Contract    │
│ • AST-aware code blocks │ • No cloud API fees or keys │ • SHA-256 YAML frontmatter     │
│ • RAG JSONL & llms.txt  │ • Air-gap & offline ready   │ • Atomic write guarantees      │
│ • Native FastMCP server │ • Pure-Python PDF (fpdf2)   │ • Semver snapshotting & diffs  │
└─────────────────────────┴─────────────────────────────┴────────────────────────────────┘
```

1. **Pillar 1: Clean & LLM-Ready**  
   Documentation should be captured as clean, structured knowledge. We eliminate token waste, protect code block indentation, inject cryptographic frontmatter, and deliver pre-chunked datasets ready for vector search and AI coding agents.
2. **Pillar 2: Local & Independent**  
   Your data and documentation workflows belong on your machine. DocHarvest runs 100% locally with zero cloud subscriptions, zero telemetry, pure-Python PDF generation, and embedded SQLite FTS5 search.
3. **Pillar 3: Deterministic & Safe**  
   Documentation tooling must never produce corrupted files or unpredictable layouts. DocHarvest enforces a strict Four-Part Output Contract, atomic file replacement, active-PID concurrency locks, and automated semver version diffing.

### Taglines & Value Propositions
- **Primary Tagline:** *Turn Any Documentation Site into LLM-Ready Markdown, Vector Context & Offline Books.*
- **Secondary / Developer Tagline:** *From Web Docs to Clean Context in One Command.*
- **AI / RAG Tagline:** *Feed Clean Technical Knowledge to LLMs Without Token Bloat or Hallucinations.*
- **Offline / Research Tagline:** *Your Entire Technical Library, Searchable and Offline.*

---

## Proof Points & Technical Evidence

| Value Theme | Technical Evidence & Codebase Proof Points |
|---|---|
| **Pristine Markdown Quality** | Direct `.md` raw endpoint probing in `GitBookProvider`, `MintlifyProvider`, and `DocusaurusProvider` retrieves pristine source files directly; AST HTML selector chain in `GenericProvider` cleans UI boilerplate and strips permalink anchors (`¶`). |
| **Zero-Dependency PDF Generation** | Custom PDF compilation engine built directly on `fpdf2` (`utils/export.py`) generates styled, syntax-highlighted PDF handbooks with zero external C-libraries (no WeasyPrint or wkhtmltopdf requirements). |
| **Instant Full-Text Search** | Persistent SQLite database using the FTS5 virtual table engine with `porter unicode61` tokenizers (`search/index.py`) delivers sub-10ms BM25 ranking across thousands of captured pages. |
| **Crash & Concurrency Safety** | Atomic file replacement (`atomic_write_text` with `tempfile` + `os.replace` + `os.fsync`) and cross-platform PID inspection (`StorageManager.acquire_domain_lock`) guarantees zero corrupted files or hung locks. |
| **Comprehensive Test Coverage** | 484 unit and integration tests passing with 0 failures across crawler engine, providers, version manager, splitter, search index, and output contracts. |
| **Broad Locale Filtering** | Automated detection and filtering of 60+ language path segments (`/zh-cn/`, `/es/`, `/ja/`, `/de/`) ensures English corpora remain clean and deduplicated. |

---

## Goals & Conversion Metrics

**Primary business goal:**  
Establish DocHarvest as the premier open-source developer standard for documentation capture, RAG context preparation, and offline technical compilation.

**Key conversion action:**  
- Install via pip: `pip install docharvest` (or `pip install gitbook-downloader`)
- Download the standalone Desktop GUI / CLI binary from GitHub Releases
- Connect the FastMCP server to Cursor (`gitbook-dl mcp`) or Claude Desktop

**Current product metrics:**  
- Product Version: `v9.0.1`
- Test Suite: 484 automated unit and integration tests passing
- Supported Platform Providers: 5 (GitBook, Mintlify, Docusaurus, ReadTheDocs, Generic/Nextra/ReadMe/VitePress)
- Interfaces: 4 (CLI, TUI, React 18 Desktop GUI, FastMCP Server)

---

## Changelog

*Newest first. One line per revision: what changed and why.*

- v1 (2026-08-23) — Initial authoritative product marketing context for DocHarvest; transitioned brand identity from gitbook-downloader, established 3-persona ICP matrix (AI/RAG Engineers, Offline Developers, DevOps/Archival Teams), defined Four-Part Output Contract, complete feature breakdown, competitive differentiation matrix, switching dynamics, brand voice pillars, and zero-placeholder technical proof points.
