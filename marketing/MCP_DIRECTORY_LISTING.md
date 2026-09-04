# DocHarvest — MCP Directory Listing Kit

> **Purpose:** Ready-to-paste listings for MCP server directories (Smithery, Glama, PulseMCP, mcp.so, Cursor Directory, and similar registries).
> **Copy rules applied:** verb-first one-liners, loss-framed hooks, specific numbers over adjectives, zero-friction install lines. No scarcity/urgency tactics — this audience reads those as SaaS-pattern noise.

---

## 1. Canonical Fields (use these everywhere for consistency)

| Field | Value |
|---|---|
| **Name** | `docharvest` |
| **Display name** | DocHarvest — LLM-Ready Documentation for AI Agents |
| **Package** | `gitbook-downloader` (PyPI) |
| **Category** | Documentation · Search · Developer Tools · Knowledge Infrastructure |
| **License** | MIT (100% free & open source) |
| **Repository** | https://github.com/RohannShetty/gitbook-downloader |
| **Homepage / Showcase** | https://rohannshetty.github.io/gitbook-downloader/ |
| **Install** | `pip install gitbook-downloader` |
| **Run (MCP stdio)** | `docharvest mcp` |
| **Platforms** | Windows · Linux · macOS (100% local, zero telemetry) |

### One-liner (≤80 characters — directories truncate here, so the hook must land first)

```text
Turn any docs site into a local, searchable knowledge base for Cursor & Claude.
```

**Alternate (loss-frame, for directories that allow punchier copy):**

```text
Your AI agent reads cookie banners instead of docs. Fix that locally in one command.
```

### Short description (≤160 characters)

```text
Give your AI agent real docs instead of cookie banners. Turns any documentation site into clean markdown, RAG JSONL & llms.txt — 100% local, MIT, free.
```

### Long description

```text
AI coding assistants hallucinate APIs because the documentation they need isn't in their training data — and when you feed them scraped web pages, up to 85% of raw page bytes are navbars, cookie banners, and scripts instead of documentation.

DocHarvest fixes this locally. It auto-detects the documentation platform (GitBook, Mintlify, Docusaurus, Nextra, VitePress, MkDocs, ReadMe, ReadTheDocs, generic SPAs), probes native .md endpoints where available, and compiles a deterministic knowledge corpus: per-page markdown with SHA-256 frontmatter, a consolidated book.md with table of contents, an llms.txt manifest, RAG-ready JSONL, and an embedded SQLite FTS5 search index.

As an MCP server, DocHarvest exposes 12 tools to Cursor, Claude Code/Desktop, Windsurf, VS Code, OpenCode, and 14 documented client configs: your agent can harvest new docs on demand, run sub-second BM25 searches over everything you've captured, traverse the concept graph to find related API sections, and diff documentation versions to catch upstream API deprecations.

Runs 100% on your hardware. No cloud API keys, no per-page fees, no telemetry — air-gap ready.
```

### Keywords / tags

```text
mcp, documentation, rag, llms-txt, markdown, chunking, bm25, fts5, local-first,
air-gapped, cursor, claude, claude-code, windsurf, vscode, opencode, pdf, jsonl
```

---

## 2. Tool Inventory (paste into directory "tools" fields)

| Tool | One-line purpose |
|---|---|
| `download_docs(url)` | Harvest any documentation site into the local library |
| `search_docs(query)` | Sub-second BM25 full-text search across all captured docs |
| `find_docs(query)` | Resolve a library name ("react", "nextjs") to indexed domains |
| `read_doc(domain, path, topic, max_tokens)` | Read a page or topic section with AST-safe token bounding |
| `query_doc_graph(domain, query)` | Discover connected API endpoints & sections via the concept graph |
| `get_related_concepts(domain, concept)` | 1-hop/2-hop related concepts & prerequisite sections |
| `list_domains()` | List all harvested documentation portals |
| `get_doc(domain)` | Read the compiled handbook / page content |
| `diff_versions(domain, v1, v2)` | Unified diff between two documentation snapshots |
| `list_versions(domain)` | Available snapshots & timestamps per domain |
| `export_docs(domain, format)` | Export as markdown, JSONL, or RAG metadata format |
| `get_changelog(domain)` | Auto-generated changelog across captured snapshots |

**Resources:** `docs://{domain}/book` (full handbook) · `docs://{domain}/manifest` (`llms.txt` index)
**Prompts:** `prompt://search-docset` · `prompt://summarize-library`

---

## 3. Ready-to-Paste Config Snippets (the friction killer)

Directories that show a config card should display the Claude Desktop / Cursor snippet — the fewer seconds between "sounds useful" and "pasted into my config," the higher the adoption.

### Claude Desktop (`claude_desktop_config.json`)

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

### Cursor (`.cursor/mcp.json`)

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

**Suggested caption under the snippet:**

```text
One-time setup. After that, just ask your agent: "Search the OpenAlgo docs for OAuth token refresh."
```

---

## 4. Per-Directory Field Mapping

### Smithery (smithery.ai)
- **Display name / description:** use the canonical fields above.
- **Start command (stdio):** `uvx gitbook-downloader mcp`
- **Tools:** paste the 10-tool inventory table (Smithery renders each tool with its schema).
- **Emphasis:** the config-card snippet — Smithery users are one "Install" click away.

### Glama (glama.ai)
- **Server listing fields:** name, description, tools (auto-discovered via stdio probe), license, repository.
- **Emphasis:** MIT license + "runs locally, zero telemetry" badges — Glama surfaces license/hosting filters, and "local" is a primary filter there.

### PulseMCP (pulsemcp.com)
- **Tagline:** the canonical one-liner.
- **Category:** Documentation / Knowledge Management.
- **Emphasis:** the 10-tool inventory + "works with Cursor & Claude Desktop" — PulseMCP readers scan tool counts and client compatibility first (Bandwagon: compatibility lists signal adoption).

### mcp.so
- **Fields:** name, description, GitHub link, install command.
- **Emphasis:** keep the description loss-framed and specific; mcp.so listings are directory-scanned quickly, so the first 80 characters carry the entire decision.

### Cursor Directory (cursor.directory)
- **Format:** community submission — lead with the Cursor-specific payoff: *instant BM25 doc search inside Agent Mode without burning context tokens on HTML*.
- **Include:** the `.cursor/mcp.json` snippet verbatim (readers copy-paste directly from the listing).

---

## 5. Why Each Line Is Written This Way (operator notes)

1. **One-liner leads with the outcome verb ("Turn any docs site into…"), not the product name** — in directory feeds, the reader's job-to-be-done ("make docs available to my agent") is the scan target, not your brand (Jobs to Be Done).
2. **"Cookie banners" appears in the alt hook and the long description** — the single most vivid, universally-experienced pain symbol (Availability Heuristic + Loss Aversion). "~83% measured" is the concrete magnitude; stating it as a measured capture result (not a ceiling) keeps it honest (Authority requires precision).
3. **Numbers everywhere a claim appears** — 12 tools, 8 frameworks, 14 documented clients, sub-second search. Specific numbers read as evidence; adjectives read as marketing (Authority Bias).
4. **"100% local, MIT, no API key, no telemetry" closes every listing** — this is regret-aversion + zero-price framing: the reader's total cost of trying is one pip install, and we say so (Regret Aversion, Zero-Price Effect).
5. **Compatibility lists (Cursor, Claude Code, Windsurf, VS Code, OpenCode, 14 documented clients)** —Bandwagon/mimetic signal: "your tool is already in the list" removes the "will it work with my setup?" pause (Mimetic Desire, Status-Quo Bias).
6. **No urgency or scarcity language anywhere** — directories are reference surfaces, not campaigns; a fake "limited" claim would permanently damage the quietly-confident brand voice (Pratfall Effect works only when the admission is genuine).
