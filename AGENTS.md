# AGENTS.md — Agent & Harness Instructions for DocHarvest v11

**DocHarvest** (package: `gitbook-downloader`) is a high-performance, local-first documentation compiler and Model Context Protocol (MCP v2) server.

---

## 🧠 Architectural Mental Model

```
Documentation URL (GitBook, Mintlify, Docusaurus, Nextra, VitePress, MkDocs, ReadMe, ReadTheDocs, Generic)
         │
         ├── [Optional: Headless Playwright Renderer if client-rendered SPA (`--render`)]
         │
         ▼
[Provider AST Scraper] ──> Extracts pure content (strips nav, headers, footers, cookie banners)
         │
         ▼
[Output Contract]
  ├── pages/            (Modular markdown files with YAML frontmatter)
  ├── book.md           (Consolidated handbook with hierarchical TOC)
  ├── llms.txt          (Standardized AI context manifest)
  ├── exports/          (RAG JSONL chunks & Pure-Python PDF handbooks)
  └── .manifest.json    (Crawl metadata & cryptographic hashes)
         │
         ▼
[Storage & Indexing]
  ├── DomainLock & Atomic Write Staging (`~/.gitbook-downloader/`)
  ├── SQLite FTS5 Full-Text Search Database (`search.db` with BM25)
  └── DocGraph Semantic Entity & Concept Graph (`query_doc_graph`)
```

---

## ⚡ Token-Efficient Context Management

When assisting users with technical questions using DocHarvest MCP tools:

1. **Never Load Entire Handbooks Blindly**:
   - Do NOT call `get_doc` on a 50,000-word docset unless the user explicitly requests the entire file.
   - Use `search_docs(query="...", domain="...")` to fetch ranked, token-efficient BM25 snippets (~200 tokens).
   - Use `query_doc_graph(domain="...", query="...")` to discover prerequisite concepts and connected API endpoints without reading every page.

2. **On-Demand Crawling vs Local Library**:
   - Use `list_domains()` first to see if documentation for the library is already cached locally.
   - If not present, call `download_docs(url="https://...")` once. The engine will download, clean, index, and cache it.

3. **Diffing & Changelogs**:
   - Use `diff_versions` and `get_changelog` to investigate breaking changes or version migrations without diffing entire file trees manually.

---

## 🔌 MCP v2 Tools, Resources & Prompts

### Registered MCP Tools (10 Tools)

| Tool | Purpose | Primary Inputs |
|---|---|---|
| `download_docs` | Harvest any doc site into Markdown + `llms.txt` + `book.md` | `url`, `workers`, `max_pages`, `path_scope` |
| `search_docs` | Full-text BM25 search across indexed documentation | `query`, `domain`, `limit` |
| `query_doc_graph` | Query non-linear semantic entity & concept graph | `domain`, `query`, `limit` |
| `get_related_concepts` | Get connected concepts, symbols & endpoints | `domain`, `concept` |
| `get_doc` | Read full compiled documentation or preview | `domain`, `version` |
| `list_domains` | List all cached documentation portals | (none) |
| `diff_versions` | Compute unified diffs between two snapshots | `domain`, `v1`, `v2` |
| `list_versions` | List captured snapshot history | `domain` |
| `export_docs` | Export docset to `"markdown"`, `"jsonl"`, or `"rag"` | `domain`, `format` |
| `get_changelog` | Auto-generate changelog from snapshot diffs | `domain` |

### MCP Resources
- `docs://{domain}/book`: Full unified markdown handbook.
- `docs://{domain}/manifest`: The `llms.txt` AI discovery index.

### MCP Prompts
- `search_docset`: Pre-structured prompt for querying and synthesizing docsets.
- `summarize_library`: Pre-structured prompt for inspecting local knowledge vaults.

---

## 🛠️ CLI & Development Workflow

```bash
# Run CLI crawl:
uv run docharvest crawl https://docs.openalgo.in/ --rag --pdf

# Crawl client-rendered JavaScript SPA:
uv run docharvest crawl https://omp.sh/docs --render

# Run full test suite:
uv run pytest

# Launch FastMCP server over stdio:
uv run docharvest mcp
# or:
python -m gitbook_downloader.mcp

# Launch Desktop GUI:
uv run docharvest --gui
```
