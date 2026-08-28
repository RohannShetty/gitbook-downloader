# Product: DocHarvest (gitbook-downloader)

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

- **Web Showcase**: Next.js 16.3.2 (App Router), React 19, Tailwind CSS v4, Framer Motion, Lucide React (deployed to GitHub Pages at `/gitbook-downloader`)
- **Desktop Studio**: PyWebView, React 18, Vite 6, Tailwind CSS, shadcn/ui, Radix UI
- **Core Engine**: Python 3.10+, requests, beautifulsoup4, markdownify, lxml, fpdf2, sqlite3 (FTS5), FastMCP v2

## Users

- **AI & RAG Engineers**: Building autonomous agents, RAG pipelines, or fine-tuning models requiring clean, token-efficient, noise-free markdown, vector JSONL chunks, and structured concept graphs.
- **Offline Researchers & Software Engineers**: Developing without reliable internet access, requiring offline searchable books, hierarchical table-of-contents navigation, and syntax-highlighted PDF handbooks.
- **DevOps & Archival Teams**: Capturing deterministic documentation snapshots, diffing version-to-version changes across releases, and eliminating vendor lock-in with zero cloud telemetry.

## Product Purpose

DocHarvest turns any online documentation site (GitBook, Mintlify, Docusaurus, Nextra, VitePress, MkDocs, ReadMe.io, ReadTheDocs, and generic JavaScript SPAs) into high-quality, LLM-ready markdown (`llms.txt`, `book.md`, `pages/`), vector RAG datasets, printable PDF books, and serves it through a FastMCP v2 server.

## Positioning

The only documentation compiler engineered with native AST extractors across 8 major documentation frameworks (plus Playwright headless rendering for dynamic SPAs), an integrated SQLite FTS5 BM25 search database, a non-linear DocGraph concept graph, and a native Model Context Protocol (MCP v2) server for 14+ AI agent harnesses with zero cloud telemetry.

## Operating Context

- **CLI Engine**: `uv run docharvest crawl <url>` with flags for `--rag`, `--pdf`, `--render`, `--jsonl`, `--scope`.
- **MCP Server**: Stdio FastMCP server (`python -m gitbook_downloader.mcp` or `uv run docharvest mcp`) providing 10 tools, resources (`docs://...`), and agent prompts.
- **Desktop Studio**: PyWebView + React 18 / Tailwind GUI for visual documentation inspection and harvesting.
- **Web Showcase**: Next.js 16 (App Router), React 19, Tailwind CSS v4, Framer Motion deployed statically to GitHub Pages at `https://rohannshetty.github.io/gitbook-downloader/`.

## Capabilities and Constraints

- **8 Dedicated Platform AST Scrapers**: Pure content extraction stripping navigation chrome, headers, footers, search dialogs, and cookie consent overlays.
- **Client-Side SPA Headless Renderer (`--render`)**: Automated Playwright engine to crawl client-hydrated sites.
- **Deterministic 4-Part Output Contract**: `pages/` (modular markdown with YAML frontmatter), `book.md` (unified hierarchical handbook), `llms.txt` (standardized AI context manifest), `.manifest.json` (SHA-256 hashes and crawl metadata).
- **FastMCP v2 Protocol Server**: 10 tools (`download_docs`, `search_docs`, `query_doc_graph`, `get_related_concepts`, `get_doc`, `list_domains`, `diff_versions`, `list_versions`, `export_docs`, `get_changelog`).
- **Offline RAG & PDF Studio**: Chunking engine for embeddings + pure-Python syntax-highlighted PDF generation via `fpdf2`.
- **Local-First Zero Telemetry**: Operates 100% on local disk (`~/.gitbook-downloader/`) with SQLite FTS5; no remote telemetry or cloud dependencies.

## Brand Commitments

- **Name**: DocHarvest (`gitbook-downloader`)
- **Tagline**: Turn Any Documentation Site into LLM-Ready Markdown, Vector Context & Offline Books
- **Voice**: Authoritative, precise, developer-first, high-density, no fluff.
- **Visual Identity**: Premium dark-mode engineering aesthetic, deep slate surfaces, amber/warm accents, crisp typography, avoiding generic purple SaaS gradients and artificial card nesting.

## Evidence on Hand

- Core Python engine in `src/gitbook_downloader/`
- Full test suite passing in `tests/`
- GitHub Pages live showcase code in `docs/` (`rohannshetty.github.io/gitbook-downloader`)
- Desktop GUI in `frontend/`
- Documentation in `AGENTS.md`, `README.md`, `CONTEXT.md`

## Product Principles

1. **Local-First & Private**: Documentation and indexes stay strictly on the user's machine; zero data leaves the environment.
2. **Signal Over Chrome**: Aggressively strip navigation, banners, cookies, and boilerplate to maximize token efficiency for LLMs.
3. **Deterministic & Reproducible**: Cryptographic hashing and structured manifests ensure exact reproducibility and version diffing.
4. **Agent-Native First Class**: First-class MCP server support so AI coding agents can search, traverse, and cite docs without context flooding.

## Accessibility & Inclusion

- WCAG AA minimum 4.5:1 contrast across all text and code blocks.
- Comprehensive keyboard navigation with distinct `:focus-visible` outlines.
- Reduced motion support honoring `prefers-reduced-motion`.