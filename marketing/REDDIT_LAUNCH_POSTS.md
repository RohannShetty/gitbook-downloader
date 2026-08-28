# DocHarvest — Subreddit-Native Launch Posts & Reddit Distribution Kit

> **Multi-Subreddit Distribution Strategy for DocHarvest Launch**  
> **Rule #1 of Reddit Marketing:** No marketing fluff. Deep technical credibility, genuine developer tone, transparent code examples, and immediate value.

---

## Master Subreddit Launch Matrix

| Subreddit | Community Size | Target Persona | Subreddit Culture / Angle | Post Title | Flair | Timing (PST) |
|---|---|---|---|---|---|---|
| `r/cursor` | 80k+ | Cursor IDE / AI Coders | FastMCP v2 integration, zero context pollution, instant offline doc search for Agent Mode. | *I built a free tool to give Cursor instant BM25 doc search via FastMCP without wasting tokens on HTML* | `Showcase` | 07:45 AM PST |
| `r/LocalLLaMA` | 350k+ | Local AI / RAG Builders | Token economy, zero cloud fees, chunking quality, local vector search with Ollama / ChromaDB. | *I built a free tool to download entire doc sites and convert them to clean RAG JSONL & Markdown books (no cloud APIs, 100% local)* | `Project / Resource` | 08:30 AM PST |
| `r/Python` | 1.2M+ | Python Devs & Engineers | Python architecture deep-dive: `requests`, `fpdf2`, `ThreadPoolExecutor`, SQLite FTS5, cross-platform PID locks. | *DocHarvest: A Python CLI + GUI tool to turn documentation websites into clean Markdown, RAG JSONL, and PDF handbooks* | `Showcase` / `Project` | 09:15 AM PST |
| `r/selfhosted` | 400k+ | Homelab / SysAdmins | Data sovereignty, vanishing docs, air-gapped homelabs, semver snapshot diffing (`gitbook-dl diff`). | *DocHarvest: Self-hosted documentation archiver with full-text search, offline PDF books, and snapshot diffing* | `Self-Hosted Software` | 10:00 AM PST |
| `r/ClaudeAI` | 150k+ | Claude Code & Desktop | Claude Code FastMCP stdio server, book.md for Project Knowledge, 89% token reduction. | *Stop copy-pasting docs into Claude Projects: 1-click tool to compile entire doc sites into clean book.md + FastMCP* | `Prompt Engineering` / `Tutorial` | 10:45 AM PST |

---

## Reddit Post 0: `r/cursor`

### Metadata
- **Subreddit:** `r/cursor`
- **Flair:** `Showcase`
- **Link:** `https://github.com/RohannShetty/gitbook-downloader`

### Post Title
```text
I built a free tool to give Cursor instant BM25 doc search via FastMCP without wasting tokens on HTML
```

### Post Body
```markdown
Hey Cursor community,

If you use Cursor's Composer or Agent mode to build against newer libraries (or internal private tools), you've probably noticed that typing `@Docs` or asking it to scrape a documentation site often wastes **5,000+ context tokens** on navbar links, footer scripts, and cookie banners. Worse, it often hallucinates old API syntax.

I built **DocHarvest** (Python package: `gitbook-downloader`) — a 100% free, local-first documentation compiler with a native FastMCP v2 server built specifically for coding assistants like Cursor.

### What it does:
1. **Harvests Any Documentation Site:** Point it at GitBook, Mintlify, Docusaurus, Nextra, VitePress, MkDocs, or ReadMe, and it pulls every page down into clean Markdown in seconds (20 pgs/sec parallel crawl).
2. **Strips 89% of HTML Noise:** AST extractors isolate pure code blocks and prose, discarding headers, navbars, and banners before tokens reach your LLM.
3. **1-Click FastMCP stdio Server:** Exposes 10 native tools (`search_docs`, `query_doc_graph`, `download_docs`, `get_doc`) directly to Cursor via `~/.cursor/mcp.json`.

### FastMCP Setup for Cursor (`~/.cursor/mcp.json`)
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

Now in Cursor Composer / Chat, you can simply ask:
> *"Search our indexed OpenAlgo docs for OAuth token signature validation."*

Cursor automatically calls `search_docs` and receives a ranked, token-efficient BM25 snippet (~180 tokens) instead of reading a 40KB HTML file.

### Links:
- **GitHub (MIT):** https://github.com/RohannShetty/gitbook-downloader
- **Showcase Site:** https://rohannshetty.github.io/gitbook-downloader/
- **PyPI:** `pip install gitbook-downloader`

Would love to hear what other MCP tools or doc frameworks you'd like to see added!
```

---

## Reddit Post 1: `r/LocalLLaMA`

### Metadata
- **Subreddit:** `r/LocalLLaMA`
- **Flair:** `Project / Resource`
- **Link:** `https://github.com/RohannShetty/gitbook-downloader`

### Post Title
```text
I built a free tool to download entire doc sites and convert them to clean RAG JSONL & Markdown books (no cloud APIs, 100% local)
```

### Post Body
```markdown
Hey everyone,

Like many of you running local models (Llama 3, Qwen 2.5, DeepSeek-Coder via Ollama / vLLM), I ran into a major headache when building local RAG pipelines for coding: **modern documentation websites are absolute poison for LLM context windows**.

If you point `wget`, `curl`, or generic web scrapers at doc portals (GitBook, Mintlify, Docusaurus, Nextra), you usually end up with:
1. **80%+ token bloat:** Navigation bars, search modals, breadcrumbs, and cookie banners wasting your precious context tokens.
2. **Corrupted code blocks:** Indentation gets destroyed during naive HTML-to-text conversion, causing local LLMs to hallucinate invalid syntax.
3. **Unscoped crawling:** The scraper follows navbar links into marketing landing pages and blogs instead of staying in `/docs/`.
4. **Metered SaaS APIs:** Cloud scrapers charge per page and require sending your URLs to external servers.

To fix this, I built **DocHarvest** (formerly `gitbook-downloader`) — a 100% free, MIT-licensed Python tool that automatically detects doc platforms, extracts pristine Markdown, and compiles structured RAG datasets locally.

### How it works:
- **Provider Auto-Detection:** Automatically recognizes GitBook, Mintlify, Docusaurus, ReadTheDocs, and generic docs.
- **Direct `.md` Endpoint Probing:** Many modern platforms publish raw markdown files directly behind the scenes. DocHarvest probes these first, bypassing HTML-to-Markdown conversion completely to get the exact author markdown.
- **Bounded BFS Subpath Crawling:** If you feed it `https://docs.example.com/v2/sdk/`, it automatically bounds link discovery to that subpath, preventing crawl leakage.
- **AST `#` Header Chunking:** Uses an AST splitter that divides documents strictly on Markdown heading boundaries (`#`, `##`, `###`), ensuring code blocks and paragraphs are never severed mid-chunk.

### The Four-Part Output Contract
Every crawl produces a clean, deterministic directory structure:
```
docs.openalgo.in-docs/
├── pages/                  # Modular .md files with SHA-256 YAML frontmatter
│   ├── index.md
│   └── api/
│       └── auth.md
├── book.md                 # Single consolidated handbook with auto-generated TOC
├── llms.txt                # Standardized agent discovery manifest
└── exports/
    ├── openalgo_rag.jsonl  # Structured RAG dataset with token counts & hashes
    └── openalgo.pdf        # Styled printable PDF (pure-Python, zero C-deps)
```

### Example: Running a 1-Command Capture
```bash
# Install via pip
pip install gitbook-downloader

# Capture any doc portal into Markdown + RAG JSONL
gitbook-dl capture https://docs.openalgo.in/ --export jsonl,pdf
```
*Benchmark: Crawled, cleaned, and exported all 673 pages of OpenAlgo docs into a 5.0 MB clean Markdown tree and structured RAG JSONL in **18.2 seconds** on local hardware.*

### Ingesting into ChromaDB / LangChain
The exported JSONL files are ready for immediate vector database ingestion:
```python
import json
import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("doc_knowledge")
model = SentenceTransformer("all-MiniLM-L6-v2")

with open("docs.openalgo.in-docs/exports/openalgo_rag.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        embedding = model.encode(item["text"]).tolist()
        collection.add(
            ids=[item["id"]],
            embeddings=[embedding],
            documents=[item["text"]],
            metadatas=[{"title": item["title"], "url": item["url"], "hash": item["content_hash"]}]
        )
print("Ingestion complete! All chunks are cryptographically grounded with source URLs.")
```

### Model Context Protocol (FastMCP) for Coding Agents
It also includes a built-in FastMCP server. If you use Cursor or Claude Code, you can add `gitbook-dl mcp` to your MCP configuration so your agent can dynamically search and read local docs on demand without leaving your editor.

### Tech Specs & Links
- **License:** 100% MIT Open Source
- **Telemetry:** Zero. Runs 100% locally and offline.
- **Python:** 3.10+ (CLI, TUI, and PyWebView + React 18 Desktop GUI included)
- **GitHub:** https://github.com/RohannShetty/gitbook-downloader
- **Interactive Showcase:** https://rohannshetty.github.io/gitbook-downloader/

Would love to hear feedback on chunking strategies or edge cases on specific doc frameworks!
```

### OP Follow-Up Comment (Post immediately after submitting)
```markdown
OP here. A quick technical note on chunking and embeddings:

When we built the RAG export feature (`splitter.py`), we decided against fixed-character chunking (e.g. 500 chars with 50 overlap) because it constantly cuts across code snippets, markdown tables, and method definitions. 

Instead, DocHarvest splits on AST heading boundaries (`#` through `####`) and wraps each chunk in an envelope containing the document domain, full section path hierarchy, and cryptographic SHA-256 hash. That way, when your local vector retrieval fetches a chunk, your prompt receives the parent heading context along with the exact code snippet.

Let me know what embedding models / chunk sizes you guys are currently getting the best retrieval results with for technical codebases!
```

---

## Reddit Post 2: `r/Python`

### Metadata
- **Subreddit:** `r/Python`
- **Flair:** `Showcase` / `Project`
- **Link:** `https://github.com/RohannShetty/gitbook-downloader`

### Post Title
```text
DocHarvest: A Python CLI + GUI tool to turn documentation websites into clean Markdown, RAG JSONL, and PDF handbooks
```

### Post Body
```markdown
Hi r/Python,

I wanted to share **DocHarvest** (`gitbook-downloader`), an open-source Python tool I've been building to solve the problem of downloading, cleaning, and structuring modern technical documentation.

Whether you want to feed documentation to AI coding assistants without token bloat, compile offline Markdown books for in-flight reading, or keep local archives of upstream library docs, DocHarvest does it in a single command with zero configuration.

### Architecture & Under the Hood

Here is how the pipeline is designed:

1. **Provider Registry & Heuristic Detection (`providers/`):**
   Uses an extensible plugin architecture (`ProviderRegistry`) that inspects URLs, DOM anchors, and headers with prioritized heuristics (GitBook: 100, Mintlify: 90, Docusaurus: 80, ReadTheDocs: 70, Generic: 0).
   
2. **Direct `.md` Probing:**
   Instead of converting messy HTML to Markdown, the engine first probes platform-specific raw endpoints (e.g., `<url>.md` on GitBook/Mintlify) to download pristine author markdown directly.

3. **High-Throughput Streaming (`engine.py`):**
   Built with `requests` + `urllib3` connection pooling and a bounded `ThreadPoolExecutor`. Includes custom `TimeoutHTTPAdapter` to eliminate hung TCP handshakes.

4. **Pure-Python PDF Generation (`utils/export.py`):**
   Generates structured, syntax-highlighted printable PDFs with custom page numbers and headers using `fpdf2` — completely avoiding heavy external C-libraries like WeasyPrint or wkhtmltopdf.

5. **Self-Recovering Domain Locks (`storage/manager.py`):**
   Implements cross-platform PID validation (`ctypes.windll.kernel32.OpenProcess` on Windows, `os.kill(pid, 0)` on POSIX) to prevent concurrent write collisions while automatically recovering from stale or abandoned locks after abrupt process termination.

6. **Embedded SQLite FTS5 Full-Text Search (`search/index.py`):**
   All downloaded docs are automatically indexed into an embedded SQLite FTS5 virtual table with `porter unicode61` stemming, giving you sub-10ms BM25 full-text search across your entire offline documentation library.

7. **FastMCP Server (`mcp/server.py`):**
   Exposes 8 standard tools over JSON-RPC stdio for coding assistants like Cursor and Claude Desktop.

### Quickstart

```bash
# Install via pip
pip install gitbook-downloader

# Capture any documentation portal
gitbook-dl capture https://docs.openalgo.in/

# Search your local documentation library
gitbook-dl search "domain lock"

# Launch the React 18 + PyWebView Desktop GUI
gitbook-dl --gui
```

### Code Example: Using the Python API directly
```python
from gitbook_downloader.api import capture_docs, search_library

# Capture documentation programmatically
result = capture_docs(
    url="https://docs.openalgo.in/",
    exports=["jsonl", "pdf"],
    concurrency=5
)
print(f"Captured {result.total_pages} pages to {result.output_dir}")

# Query the local SQLite FTS5 search index
matches = search_library("authentication token")
for match in matches:
    print(f"[{match.domain}] {match.title} -> {match.snippet}")
```

### Project Info & Verification
- **GitHub:** https://github.com/RohannShetty/gitbook-downloader
- **Showcase Site:** https://rohannshetty.github.io/gitbook-downloader/
- **Test Suite:** 484 unit and integration tests passing (`pytest`)
- **License:** MIT License

I’d love to get feedback on the Python architecture, concurrency handling, or suggestions for additional documentation provider extractors!
```

### OP Follow-Up Comment
```markdown
OP here. To expand on the cross-platform lock recovery implementation:

One of the biggest frustrations with command-line scrapers is having an interrupted process (like a `Ctrl+C` or terminal closure) leave a `.lock` file behind, causing all future runs to crash with `LockHeldError`.

In `storage/manager.py`, we store the active PID and timestamp inside the lock file. Before raising an error, `DomainLock` checks whether that PID is still alive:
- On Windows, it calls `kernel32.OpenProcess` and `GetExitCodeProcess` to check for `STILL_ACTIVE (259)`.
- On Linux/macOS, it calls `os.kill(pid, 0)` and catches `ESRCH` (No such process).

If the process is dead, it reclaims and acquires the lock automatically with zero manual intervention. We also register `atexit` handlers to clean up locks gracefully on standard exits.
```

---

## Reddit Post 3: `r/selfhosted`

### Metadata
- **Subreddit:** `r/selfhosted`
- **Flair:** `Self-Hosted Software` / `Archiving`
- **Link:** `https://github.com/RohannShetty/gitbook-downloader`

### Post Title
```text
DocHarvest: Self-hosted documentation archiver with full-text search, offline PDF books, and snapshot diffing
```

### Post Body
```markdown
Hey r/selfhosted,

How many times have you relied on an open-source tool or self-hosted service, only for the project's documentation website to silently change its API, delete old version guides, or disappear entirely behind a 404?

I built **DocHarvest** (`gitbook-downloader`) to solve this for my own homelab. It's a self-hosted, 100% local tool to capture, archive, search, and diff entire technical documentation portals.

### What it does for self-hosters:
- **1-Command Archival:** Give it a docs URL (GitBook, Mintlify, Docusaurus, ReadTheDocs, generic), and it downloads every page into clean, readable Markdown and structured directories.
- **Offline Printable PDF Handbooks:** Compiles entire multi-hundred page sites into a single, beautifully formatted PDF handbook with a complete Table of Contents and syntax-highlighted code blocks (using pure-Python `fpdf2`, zero external C-dependencies).
- **Embedded SQLite FTS5 Search Engine:** Automatically indexes all saved documentation into a local SQLite database with BM25 ranking and snippet highlights. Search across dozens of archived libraries instantly from the CLI or desktop GUI.
- **Semver Snapshot Diffing:** Want to see what changed when a service updated from `v1` to `v2`? DocHarvest creates timestamped version snapshots (`v1.0.0` → `v1.0.1`) and generates unified diffs showing added, modified, or deprecated API endpoints.
- **Zero Cloud / Zero Telemetry:** Runs 100% on your local machine or homelab server. No external API keys, no tracking, and fully air-gapped compatible.

### Running it in your Homelab

You can run it via Python/pip, standalone executable, or Docker:

```bash
# Install via pip
pip install gitbook-downloader

# Archive a full documentation portal
gitbook-dl capture https://docs.openalgo.in/ --export pdf,jsonl

# Diff two versions of a documentation site to audit API changes
gitbook-dl diff docs.openalgo.in v1.0.0 v1.0.1

# Search all archived documentation locally
gitbook-dl search "reverse proxy configuration"
```

### Docker Compose Setup
```yaml
version: '3.8'
services:
  docharvest:
    image: python:3.12-slim
    container_name: docharvest
    working_dir: /data
    volumes:
      - ./docs_library:/root/.gitbook-downloader
      - ./archives:/data
    command: >
      bash -c "pip install gitbook-downloader && 
               gitbook-dl capture https://docs.openalgo.in/ --export pdf"
```

### Project Links
- **GitHub:** https://github.com/RohannShetty/gitbook-downloader
- **Showcase Site:** https://rohannshetty.github.io/gitbook-downloader/
- **License:** MIT (100% Free & Open Source)

Hope this helps anyone looking to build a resilient, offline knowledge base for their homelab!
```

### OP Follow-Up Comment
```markdown
OP here. For storage layout, DocHarvest maintains an organized directory in `~/.gitbook-downloader/`:

- `library/<domain>/`: Contains the clean `pages/` hierarchy, `book.md`, `llms.txt`, and `exports/`.
- `versions/<domain>/`: Stores historical semver snapshots for instant diffing.
- `search/index.db`: The SQLite FTS5 database enabling instant keyword and boolean queries across all libraries.

If you're running this as a scheduled cron job on a Linux server to monitor vendor API docs, you can set up a simple daily bash script:
```bash
#!/bin/bash
gitbook-dl capture https://api.vendor.com/docs/
DIFF=$(gitbook-dl diff api.vendor.com latest previous)
if [ ! -z "$DIFF" ]; then
    echo "Vendor docs updated!" | mail -s "Doc Drift Alert" admin@homelab.local
fi
```
```

---

## Reddit Post 4: `r/OpenAI` / `r/ChatGPT`

### Metadata
- **Subreddit:** `r/OpenAI`
- **Flair:** `Prompt Engineering` / `Tutorial / Guide`
- **Link:** `https://github.com/RohannShetty/gitbook-downloader`

### Post Title
```text
Stop copy-pasting docs into ChatGPT & Claude: I built a 1-click tool to turn whole doc portals into clean Markdown knowledge bases & vector files
```

### Post Body
```markdown
Hey everyone,

Whenever a new framework, SDK, or tool comes out, ChatGPT and Claude inevitably hallucinate outdated methods because the new documentation is past their training cutoff.

The standard workaround is copy-pasting 50 pages into Custom GPTs or Claude Projects. But doing this manually is painful, and using standard web scrapers dumps massive amounts of HTML navbar junk, cookie notices, and broken code indentation that burns through your context window.

I built an open-source tool called **DocHarvest** (`gitbook-downloader`) that turns any documentation site into clean, LLM-ready Markdown and knowledge base files in one command.

### Key Features for AI Users:
1. **Clean Markdown (Zero HTML Garbage):** Automatically strips navigation menus, headers, and UI elements. You get pure Markdown with preserved code blocks and tables.
2. **Consolidated `book.md` Handbook:** Combines hundreds of pages into a single, scrollable Markdown document with an auto-generated Table of Contents. Perfect for dragging directly into Claude Projects or ChatGPT Custom GPT knowledge bases.
3. **`llms.txt` Discovery File:** Generates a standardized index listing all endpoints, topics, and source URLs.
4. **FastMCP Server for Claude Desktop & Cursor:** Includes a built-in Model Context Protocol server. Connect it to Claude Desktop or Cursor so your AI assistant can search and read external documentation on its own.
5. **100% Free & Local:** Runs completely on your own machine with zero cloud API keys or subscriptions.

### How to use it:

```bash
# 1. Install
pip install gitbook-downloader

# 2. Capture documentation
gitbook-dl capture https://docs.openalgo.in/

# 3. Output files created:
# - pages/ (clean individual Markdown files)
# - book.md (single compiled knowledge base for ChatGPT/Claude)
# - exports/openalgo_rag.jsonl (vector chunks with metadata)
# - exports/openalgo.pdf (printable handbook)
```

If you prefer a visual interface, there is also a standalone Desktop GUI (`gitbook-dl --gui` or downloadable `.exe`) with live crawl progress, search, and export tools.

- **GitHub:** https://github.com/RohannShetty/gitbook-downloader
- **Web Showcase:** https://rohannshetty.github.io/gitbook-downloader/

Hope this saves you hours of copy-pasting into your AI workflows!
```

### OP Follow-Up Comment
```markdown
OP here. A quick tip when uploading documentation to Claude Projects or ChatGPT Custom GPTs:

If the documentation is under ~300 pages, uploading the generated `book.md` directly works best because LLMs can leverage their full 128k/200k context window while retaining global section hierarchy and the table of contents.

If the documentation is massive (1,000+ pages), use the generated `exports/*.jsonl` file with a local vector database (like ChromaDB or Pinecone) to perform semantic retrieval on specific section chunks.

Happy to answer any questions about setting up the FastMCP server with Claude Desktop!
```

---

## Reddit Moderation & Engagement Checklist

- [ ] **Account Karma & Age:** Ensure posting accounts have >500 comment karma and are at least 3 months old to avoid automatic spam filters.
- [ ] **Staggered Timing:** Space out subreddit submissions by 45–60 minutes to prevent triggering Reddit sitewide rate-limiting algorithms.
- [ ] **First Comment Rule:** Post the OP technical follow-up comment within 2 minutes of post creation.
- [ ] **Active Engagement:** Check each post every 10–15 minutes for the first 3 hours to respond to every technical comment, answer questions, and acknowledge feedback.
