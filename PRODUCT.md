# Product: DocHarvest (gitbook-downloader)

**Version:** 11.0.0  
**Tagline:** Turn Any Documentation Site into LLM-Ready Markdown, Vector Context & Offline Books  

---

## 1. Overview
DocHarvest is a local-first documentation compiler, vector AI context platform, and FastMCP v2 server. It features an automated 8-provider discovery engine, Playwright headless rendering for dynamic SPAs, SQLite FTS5 BM25 search, semantic concept graph intelligence, and a React + Tailwind CSS + shadcn/ui Desktop GUI.

---

## 2. Target Personas (ICPs)
1. **AI & RAG Engineers**: Need clean, noise-free, token-efficient documentation context for LangChain, LlamaIndex, ChromaDB, Cursor, and Claude Code.
2. **Offline Researchers & Mobile Developers**: Need styled, printable PDF handbooks with table of contents and offline markdown search.
3. **DevOps & Archival Teams**: Require deterministic, reproducible documentation snapshots with version diffing and zero external telemetry.

---

## 3. Core Capabilities
- **8 Dedicated Platform Parsers**: GitBook, Mintlify, Docusaurus, Nextra, VitePress, MkDocs, ReadMe.io, and ReadTheDocs (plus Generic HTML / SPA).
- **Headless SPA Rendering (`--render`)**: Opt-in Playwright renderer to execute client-side JavaScript before markdown extraction.
- **Four-Part Output Contract**: Modular `pages/`, unified `book.md`, standardized `llms.txt`, and cryptographic metadata.
- **Native FastMCP v2 Server**: 10 tools, MCP Resources (`docs://...`), and MCP Prompts for 14 AI IDEs and agent harnesses.
- **Impeccable Studio Desktop GUI**: React 18 + Vite + Tailwind CSS + shadcn/ui interface with in-app doc reader, syntax highlighting, Mermaid diagrams, and real-time logs.
- **Vector RAG & Pure-Python PDF Studio**: Export to JSONL vector chunks and syntax-highlighted printable PDF books via `fpdf2`.

---

## 4. Technical Architecture
- **Core Engine**: Python 3.10+ (requests, beautifulsoup4, markdownify, lxml, fpdf2, sqlite3 FTS5).
- **Desktop GUI**: PyWebView + React 18, Vite 6, Tailwind CSS, shadcn/ui, Radix UI, Mermaid.
- **Showcase Site**: Next.js 16.3.2, React 19, Tailwind CSS v4, Framer Motion.
- **AI Protocols**: Model Context Protocol v2 (FastMCP / MCPServer).