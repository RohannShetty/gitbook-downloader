# How I Turn Any Documentation into Clean RAG Context for Cursor & Claude in 30 Seconds

*Stop burning 60% of your LLM context window on HTML navigation noise. Here is how to harvest, chunk, and index technical docs locally for AI coding assistants and vector databases.*

---

**Author:** Rohan Shetty  
**Published on:** Dev.to / Hashnode / Medium  
**Tags:** `#ai` `#rag` `#python` `#opensource` `#cursor` `#llm`  
**GitHub Repository:** [https://github.com/RohannShetty/gitbook-downloader](https://github.com/RohannShetty/gitbook-downloader)  
**Interactive Web Showcase:** [https://rohannshetty.github.io/gitbook-downloader/](https://rohannshetty.github.io/gitbook-downloader/)  

---

## 1. The Silent Context Killer in Modern AI Engineering

If you use AI coding assistants like **Cursor**, **Claude Code**, **Windsurf**, or **GitHub Copilot**, you have likely experienced this frustrating scenario:

You are working with a newly released library or a fast-evolving framework (e.g. Next.js 15, LangGraph, PyTorch 2.4, or a niche cloud SDK). You ask your AI assistant to implement a method, and it confidently writes code using **deprecated functions from 2022**.

Why? Because the library's latest documentation is past the model's training cutoff.

```
┌────────────────────────────────────────────────────────────────────────┐
│                     THE NAIVE SCRAPING TRAP                            │
├────────────────────────────────────────────────────────────────────────┤
│  Raw Webpage (100% of bytes)                                           │
│  ├── Navbars, search modals, breadcrumbs (45%)  ──► WASTED TOKENS      │
│  ├── Cookie banners, footer links, CSS (35%)    ──► CONTEXT POLLUTION  │
│  └── Actual Code & Documentation Text (20%)     ──► USABLE KNOWLEDGE   │
└────────────────────────────────────────────────────────────────────────┘
```

The standard workaround is pointing a web scraper or `wget` at the documentation website to feed it into a local RAG (Retrieval-Augmented Generation) pipeline or IDE context.

**And that is where everything breaks.**

---

## 2. Why `wget` and Generic Scrapers Fail on Technical Docs

When you run `wget -r` or use basic Python scraping scripts on modern documentation portals (built with GitBook, Mintlify, Docusaurus, Nextra, or ReadTheDocs), you inevitably hit four crippling issues:

### 1. The Token Bloat Penalty
Raw HTML is 80–90% noise. Navigation headers, SVG icons, mobile menu drawers, and tracking scripts overwhelm your model's context window. You end up spending $15 on an API prompt just to feed an LLM 40 pages of cookie policy and sidebar links.

### 2. Broken Code Indentation
In languages like Python, YAML, and Rust, whitespace and indentation are syntactic requirements. Naive HTML-to-Markdown converters frequently flatten indentation inside `<pre><code>` blocks, turning valid code snippets into unparseable gibberish that confuses LLMs.

### 3. Single-Page App (SPA) Link Sprawl
Unbounded crawlers follow navbar links out of `/docs/` and wander across blogs, pricing pages, marketing landing pages, and community forums. A 50-page documentation portal suddenly turns into a 2,000-page crawl of junk data.

### 4. Fragment Duplication
Anchor links (`#section-1`, `#params`) cause basic scrapers to re-download the exact same webpage dozens of times under different URLs, polluting your vector database with duplicate embeddings.

---

## 3. Enter DocHarvest: Architecture & The Four-Part Output Contract

To solve this, I built **DocHarvest** (formerly `gitbook-downloader`) — a 100% free, MIT-licensed open-source tool written in Python that automatically harvests, sanitizes, and structures technical documentation for AI models, vector databases, and offline reading.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              DOCHARVEST PIPELINE                                       │
├──────────────────────┬─────────────────────────────┬───────────────────────────────────┤
│ 1. DISCOVERY         │ 2. SANITIZATION             │ 3. THE OUTPUT CONTRACT            │
├──────────────────────┼─────────────────────────────┼───────────────────────────────────┤
│ • Provider Registry  │ • Direct .md Probing        │ 📁 pages/**/*.md (Frontmatter)    │
│ • Bounded BFS Scope  │ • Permalinks Stripped (¶)   │ 📖 book.md (Consolidated + TOC)   │
│ • Sitemap / llms.txt │ • Relative Link Rewriting   │ 📄 llms.txt (Agent Manifest)      │
│ • Locale Filtering   │ • AST # Header Chunking     │ 📊 exports/*.jsonl & *.pdf        │
└──────────────────────┴─────────────────────────────┴───────────────────────────────────┘
```

### The Four-Part Output Contract
Every time DocHarvest captures a documentation portal, it outputs a deterministic, mathematically verifiable directory structure:

1. **Modular Page Tree (`pages/**/*.md`):** Individual Markdown files mirroring the documentation hierarchy, each equipped with cryptographic YAML frontmatter (source URL, title, crawl timestamp, and SHA-256 content hash).
2. **Consolidated Handbook (`book.md`):** A single concatenated Markdown file compiling the entire documentation tree in natural reading order with auto-demoted `#` headings and a generated Table of Contents.
3. **Agent Discovery Manifest (`llms.txt`):** A standardized index following the `llms.txt` specification, listing all endpoints, topics, and source URLs.
4. **Structured Exports (`exports/`):** Pre-chunked RAG datasets (`rag.jsonl`) ready for vector databases, and publication-grade printable PDFs (`handbook.pdf`) generated with pure Python (`fpdf2`).

---

## 4. Step-by-Step Tutorial: Ingesting 600+ Pages of API Docs in 30 Seconds

Let's walk through harvesting a real-world, production documentation suite: **OpenAlgo** (a financial algorithmic trading documentation portal with 673 pages).

### Step 1: Install DocHarvest
DocHarvest requires Python 3.10+ and can be installed in seconds via `pip`:

```bash
pip install gitbook-downloader
```

*(Note: Pre-compiled standalone `.exe` binaries for Windows and Linux are also available on [GitHub Releases](https://github.com/RohannShetty/gitbook-downloader/releases).)*

### Step 2: Run a 1-Command Capture
To capture the entire documentation site and export RAG JSONL plus a printable PDF:

```bash
gitbook-dl capture https://docs.openalgo.in/ --export jsonl,pdf
```

### What Happens in the Terminal:
```bash
❯ gitbook-dl capture https://docs.openalgo.in/ --export jsonl,pdf
[16:42:01] ⚡ Probing documentation framework...
[16:42:02] ✓ Provider detected: GitBook (direct .md endpoint probing active)
[16:42:03] 🔒 Bounded BFS crawler locked to root: https://docs.openalgo.in/
[16:42:05] 📥 Downloading clean Markdown (5 streaming workers)...
[16:42:18] ✓ 673/673 pages captured (5.0 MB clean Markdown)
[16:42:19] 📦 Compiling Four-Part Output Contract:
           ├── docs.openalgo.in-docs/pages/ (673 clean .md files)
           ├── docs.openalgo.in-docs/book.md (unified handbook with TOC)
           ├── docs.openalgo.in-docs/llms.txt (standardized agent manifest)
           ├── docs.openalgo.in-docs/exports/openalgo_rag.jsonl (vector dataset)
           └── docs.openalgo.in-docs/exports/openalgo_handbook.pdf (styled PDF)
[16:42:20] ✨ Indexed 673 pages into local SQLite FTS5 search engine in 18.2s!
```

**Benchmark Result:** 673 pages crawled, cleaned, converted, chunked, and indexed into SQLite in **18.2 seconds** with zero configuration.

---

## 5. Under the Hood: AST Section Chunking & Token Economy

Why is DocHarvest Markdown so much better for LLM retrieval than raw HTML or naive text splitters?

### The Problem with Character-Based Chunking
Standard chunkers (like LangChain's `RecursiveCharacterTextSplitter`) slice text after a fixed number of characters (e.g. 1,000 characters). This frequently splits a Python function signature away from its docstring, or cuts a JSON payload right in the middle:

```python
# Naive chunk boundary: cuts mid-codeblock!
def authenticate_user(api_key: str, secret: str):
    """Authenticates the client session"""
--- CHUNK BOUNDARY SPLIT HERE ---
    payload = {"key": api_key, "timestamp": time.time()}
    return requests.post("/auth", json=payload)
```

### The AST Header Chunking Solution (`splitter.py`)
DocHarvest uses an Abstract Syntax Tree (AST) splitter that parses Markdown heading structures (`#`, `##`, `###`):
1. **Atomic Code Blocks:** Code blocks (` ```python ... ``` `) and tables are treated as atomic tokens that can never be split across chunks.
2. **Context Envelopes:** Each chunk is wrapped in an HTML comment metadata envelope containing the section path and source citation:

```markdown
<!-- domain: docs.openalgo.in, path: /api/auth, section: Authentication > REST API, chunk: 1/2 -->
---
source_url: https://docs.openalgo.in/api/auth
title: REST API Authentication
content_hash: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Authentication Endpoints

To authenticate your API requests, pass your API key in the `X-Algo-Key` header:

```python
import requests

headers = {"X-Algo-Key": "your_api_key_here"}
response = requests.get("https://api.openalgo.in/v1/user/profile", headers=headers)
print(response.json())
```
```

### Benchmark: Token Economy Comparison

| Metric | Raw HTML Scrape (`wget`) | Generic Markdown Scraper | DocHarvest Clean AST |
|---|:---:|:---:|:---:|
| **Total Corpus Size** | 28.4 MB | 11.2 MB | **5.0 MB** |
| **Estimated Token Count** | ~7,100,000 tokens | ~2,800,000 tokens | **~1,250,000 tokens** |
| **Token Reduction vs Raw** | 0% | 60.5% | **82.4% Savings** |
| **Code Block Indentation** | ❌ Broken / Corrupted | ⚠️ Partial | **✅ 100% Preserved** |
| **Cryptographic Provenance** | ❌ None | ❌ None | **✅ SHA-256 YAML Headers** |

---

## 6. Connecting DocHarvest to Claude Code & Cursor via FastMCP

DocHarvest includes a native **Model Context Protocol (MCP)** server (`mcp/server.py`). This allows AI coding agents in **Cursor**, **Claude Desktop**, or **Claude Code** to search and read external documentation dynamically.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   MODEL CONTEXT PROTOCOL (FastMCP)                     │
├────────────────────────────────────────────────────────────────────────┤
│  AI Coding Agent (Cursor / Claude Code)                                │
│       │                                                                │
│       ├── (JSON-RPC stdio) ──►  `gitbook-dl mcp`                       │
│       │                              │                                 │
│       │                              ├── `search_docs("query")`        │
│       │                              ├── `read_doc_page("path")`       │
│       │                              └── `download_docs("url")`        │
│       ▼                                                                │
│  Instant, fresh technical context without leaving the IDE!             │
└────────────────────────────────────────────────────────────────────────┘
```

### How to Configure Cursor / Claude Desktop

Add DocHarvest to your `claude_desktop_config.json` or `.cursor/mcp.json`:

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

### What This Unlocks:
Now, when you ask Cursor or Claude:
> *"How do I initialize the websocket stream in OpenAlgo SDK v2?"*

Your AI assistant will autonomously call `search_docs("websocket stream")`, retrieve the exact markdown page from your local SQLite FTS5 index, and write accurate code based on the latest documentation.

---

## 7. Building a Local Vector RAG Pipeline with ChromaDB & LangChain

Here is a complete, runnable Python script showing how to take the exported `exports/openalgo_rag.jsonl` dataset and build an offline semantic search RAG pipeline:

```python
import json
import chromadb
from sentence_transformers import SentenceTransformer

# 1. Initialize local persistent ChromaDB client
client = chromadb.PersistentClient(path="./chroma_rag_db")
collection = client.get_or_create_collection(name="technical_docs")

# 2. Load lightweight local embedding model
print("Loading embedding model (all-MiniLM-L6-v2)...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# 3. Ingest DocHarvest RAG JSONL dataset
jsonl_file = "docs.openalgo.in-docs/exports/openalgo_rag.jsonl"

documents, metadatas, ids = [], [], []

print(f"Ingesting {jsonl_file}...")
with open(jsonl_file, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        ids.append(item["id"])
        documents.append(item["text"])
        metadatas.append({
            "title": item["title"],
            "url": item["url"],
            "domain": item["domain"],
            "hash": item["content_hash"]
        })

# Compute embeddings and store in ChromaDB in batches
batch_size = 64
for i in range(0, len(documents), batch_size):
    batch_docs = documents[i:i+batch_size]
    batch_meta = metadatas[i:i+batch_size]
    batch_ids = ids[i:i+batch_size]
    embeddings = embedder.encode(batch_docs).tolist()
    
    collection.add(
        ids=batch_ids,
        embeddings=embeddings,
        documents=batch_docs,
        metadatas=batch_meta
    )

print(f"Successfully indexed {len(documents)} clean document chunks!")

# 4. Perform a semantic similarity query
query = "How to handle rate limits and retry requests?"
query_embedding = embedder.encode([query]).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=2
)

print("\n--- TOP RETRIEVAL RESULTS ---")
for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"\n[Source: {meta['url']}] (SHA-256: {meta['hash'][:12]}...)")
    print(doc[:300] + "...\n")
```

---

## 8. Offline Productivity: Generating Pure-Python Printable PDFs

For developers traveling on flights or working in air-gapped secure facilities, having an entire documentation suite in a single printable PDF handbook is invaluable.

Most tools require heavyweight C-libraries like **WeasyPrint** (which requires Pango/Cairo) or **wkhtmltopdf** (which requires Qt/WebKit).

DocHarvest implements a custom layout engine built on `fpdf2` (pure Python):

```bash
# Generate a formatted PDF handbook from any captured docs
gitbook-dl export docs.openalgo.in --format pdf
```

**Features of the Generated PDF:**
- Hierarchical Table of Contents with page link navigation.
- Shaded, monospace code blocks with syntax styling.
- Clean header margins, running footers, and automatic pagination.
- 100% pure Python execution with zero external OS dependencies.

---

## 9. Tracking Documentation Drift with Semver Snapshots & Diffs

When an upstream vendor silently alters an API endpoint without a changelog, integrations break in production.

DocHarvest includes an automated version manager (`versioning.py`):

```bash
# Snapshot current version before re-crawling
gitbook-dl capture https://docs.openalgo.in/ --snapshot

# Compare two versions of documentation
gitbook-dl diff docs.openalgo.in v1.0.0 v1.0.1
```

**Output:**
```diff
--- docs.openalgo.in (v1.0.0)
+++ docs.openalgo.in (v1.0.1)
@@ -42,7 +42,7 @@
- def place_order(symbol: str, qty: int, price: float):
+ def place_order(symbol: str, qty: int, price: float, order_type: str = "LIMIT"):
```
You get immediate visibility into upstream schema changes and API deprecations.

---

## 10. Conclusion & Open-Source Roadmap

By treating documentation as **structured technical knowledge** instead of raw HTML, DocHarvest eliminates context bloat, prevents AI hallucinations, and provides a dependable offline knowledge base.

### Summary of What You Get:
- ⚡ **1-Command Execution:** `gitbook-dl capture <url>`
- 🧹 **Pristine Markdown:** Zero HTML chrome, preserved code indentation.
- 🤖 **FastMCP Server:** Dynamic agent doc exploration for Cursor & Claude.
- 🔍 **SQLite FTS5 Search:** Instant BM25 search across your entire offline library.
- 📄 **Pure-Python PDF:** Zero-dependency printable handbooks.
- 💯 **100% Free & Local:** Open-source (MIT), zero telemetry, zero fees.

### Getting Involved
- ⭐ **Star the project on GitHub:** [https://github.com/RohannShetty/gitbook-downloader](https://github.com/RohannShetty/gitbook-downloader)
- 🌐 **Interactive Showcase:** [https://rohannshetty.github.io/gitbook-downloader/](https://rohannshetty.github.io/gitbook-downloader/)
- 📦 **PyPI:** `pip install gitbook-downloader`

What documentation framework or feature should we support next? Leave a comment below or open an issue on GitHub!
