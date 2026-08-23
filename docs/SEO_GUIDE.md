# DocHarvest — Repository SEO & Discoverability Guide

**Version:** 1.0.0  
**Target Repository:** `RohannShetty/gitbook-downloader` (Brand: **DocHarvest**)  
**Last Updated:** 2026-08-23  

---

## 1. Executive Summary

This guide provides the canonical repository configuration, search engine optimization (SEO), GitHub metadata parameters, and social preview assets for **DocHarvest** (*Turn Any Documentation Site into LLM-Ready Markdown, Vector Context & Offline Books*).

Optimizing repository discoverability ensures maximum visibility across search engines, GitHub search queries, AI engineer workflows, and developer communities searching for documentation scrapers, RAG context builders, `llms.txt` generators, and offline handbook compilers.

---

## 2. Repository Metadata Specification

### 2.1 Repository Description (Character Count: 201 / 350 max)

```text
Turn any documentation portal (GitBook, Mintlify, Docusaurus, ReadTheDocs) into LLM-ready Markdown, vector RAG JSONL, llms.txt, and styled offline PDFs. Zero-config CLI, desktop GUI & FastMCP server.
```

#### Keyword Analysis & Intent Mapping
| Keyword Segment | Target Search Intent | Persona Targeted |
|---|---|---|
| `GitBook, Mintlify, Docusaurus, ReadTheDocs` | Platform-specific documentation scraping queries | All Developers & Archival Teams |
| `LLM-ready Markdown` | AI context prep & cleaning without HTML boilerplate | AI & RAG Engineers |
| `vector RAG JSONL` | Vector ingestion for LangChain, LlamaIndex, ChromaDB | AI / Vector DB Developers |
| `llms.txt` | Standardized agent manifest compliance | AI Agents & Autonomous Workflows |
| `styled offline PDFs` | Single-file printable books with table of contents | Offline Researchers & Mobile Devs |
| `Zero-config CLI, desktop GUI & FastMCP server` | Diverse user interfaces (Terminal, Desktop, MCP) | SREs, General Devs, Cursor/Claude Users |

#### Alternative Approved Variations (< 350 chars)
- **Compact (178 chars):**
  ```text
  Turn any documentation site into clean LLM-ready Markdown, vector RAG JSONL, llms.txt, and styled offline PDFs. Features a zero-config CLI, React desktop GUI, and FastMCP server.
  ```
- **Extended Technical (274 chars):**
  ```text
  Universal documentation harvesting and AI context platform. Automatically captures GitBook, Mintlify, Docusaurus, and ReadTheDocs sites into clean Markdown trees, RAG JSONL, llms.txt, and pure-Python PDFs. Includes CLI, React 18 desktop GUI, and FastMCP server. 100% local & free.
  ```

---

### 2.2 Canonical GitHub Topic Tags (18 Curated Topics)

The following 18 topic tags are curated for GitHub search indexing and topic graph clustering:

```text
rag
llms-txt
documentation-scraper
mcp-server
offline-docs
pdf-generator
gitbook
mintlify
docusaurus
vitepress
readme-io
nextra
local-ai
vector-database
sqlite-fts5
fpdf2
cli
desktop-app
```

#### Topic Category Breakdown
```
┌────────────────────────────────────────────────────────────────────────┐
│                     18 CURATED GITHUB TOPIC TAGS                       │
├──────────────────────┬──────────────────────┬──────────────────────────┤
│   AI & RAG ECOSYSTEM │ DOCUMENTATION SITES  │ ARCHITECTURE & TOOLING   │
├──────────────────────┼──────────────────────┼──────────────────────────┤
│ • rag                │ • gitbook            │ • sqlite-fts5            │
│ • llms-txt           │ • mintlify           │ • fpdf2                  │
│ • mcp-server         │ • docusaurus         │ • cli                    │
│ • local-ai           │ • vitepress          │ • desktop-app            │
│ • vector-database    │ • readme-io          │ • offline-docs           │
│                      │ • nextra             │ • pdf-generator          │
│                      │                      │ • documentation-scraper  │
└──────────────────────┴──────────────────────┴──────────────────────────┘
```

---

### 2.3 Repository Homepage URL

```text
https://rohannshetty.github.io/gitbook-downloader/
```

---

## 3. GitHub Configuration Commands & Web UI Instructions

### 3.1 Step-by-Step GitHub CLI (`gh`) Execution

Run the following command using the GitHub CLI (`gh`) to update repository metadata instantly:

```bash
gh repo edit RohannShetty/gitbook-downloader \
  --description "Turn any documentation portal (GitBook, Mintlify, Docusaurus, ReadTheDocs) into LLM-ready Markdown, vector RAG JSONL, llms.txt, and styled offline PDFs. Zero-config CLI, desktop GUI & FastMCP server." \
  --homepage "https://rohannshetty.github.io/gitbook-downloader/" \
  --add-topic "rag" \
  --add-topic "llms-txt" \
  --add-topic "documentation-scraper" \
  --add-topic "mcp-server" \
  --add-topic "offline-docs" \
  --add-topic "pdf-generator" \
  --add-topic "gitbook" \
  --add-topic "mintlify" \
  --add-topic "docusaurus" \
  --add-topic "vitepress" \
  --add-topic "readme-io" \
  --add-topic "nextra" \
  --add-topic "local-ai" \
  --add-topic "vector-database" \
  --add-topic "sqlite-fts5" \
  --add-topic "fpdf2" \
  --add-topic "cli" \
  --add-topic "desktop-app" \
  --enable-issues=true \
  --enable-wiki=false \
  --enable-discussions=true
```

### 3.2 GitHub Web UI Configuration Procedure

If updating via the GitHub Web interface:

1. Navigate to **`https://github.com/RohannShetty/gitbook-downloader`**.
2. Click the ⚙️ **Settings icon** next to **About** in the right-hand sidebar of the repository root.
3. In the **Edit repository details** modal:
   - **Description**: Paste: `Turn any documentation portal (GitBook, Mintlify, Docusaurus, ReadTheDocs) into LLM-ready Markdown, vector RAG JSONL, llms.txt, and styled offline PDFs. Zero-config CLI, desktop GUI & FastMCP server.`
   - **Website**: Enter `https://rohannshetty.github.io/gitbook-downloader/`
   - **Topics**: Add each of the 18 tags individually:
     - `rag`, `llms-txt`, `documentation-scraper`, `mcp-server`, `offline-docs`, `pdf-generator`, `gitbook`, `mintlify`, `docusaurus`, `vitepress`, `readme-io`, `nextra`, `local-ai`, `vector-database`, `sqlite-fts5`, `fpdf2`, `cli`, `desktop-app`
   - **Include in the home page**:
     - Check: **Releases**
     - Check: **Packages**
     - Check: **Environments**
4. Click **Save changes**.

---

## 4. OpenGraph Social Preview Asset Specifications

### 4.1 Asset Metadata & Canvas Dimensions

| Property | Value / Specification | Rationale & Standards |
|---|---|---|
| **File Location** | `assets/social-preview.svg` / `assets/social-preview.png` | Standard repository asset location |
| **Canvas Dimensions** | `1280 × 640 px` (2:1 aspect ratio) | GitHub social preview & Twitter `summary_large_image` |
| **Background Fill** | `#09090b` (Zinc-950) | High-contrast dark palette |
| **Texture Overlay** | Dot-grid pattern (`#1b1b20`, `r=1.4`, `step=44px`) | Subtle depth without noise |
| **Outer Border** | `1px` stroke `#27272a`, `rx=24px` | Premium hairline card boundary |
| **Primary Accent** | `#06b6d4` (Cyan-500) & `#f59e0b` (Amber-500) | High visibility against dark background |
| **Typography** | `Inter` (Sans) & `JetBrains Mono` (Monospace) | Developer aesthetic & high legibility |
| **Contrast Ratio** | Text-to-canvas ratio `> 12:1` | Full WCAG AAA compliance |

### 4.2 Card Layout & Composition Diagram

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [1280 x 640] OpenGraph Social Preview Card                                             │
│                                                                                        │
│  ┌──────────────────────────────────────────┐  ┌────────────────────────────────────┐  │
│  │ [Logo Lockup]                            │  │ [Live Interactive Terminal Card]   │  │
│  │ ❖ DocHarvest                             │  │ ┌────────────────────────────────┐ │  │
│  │   MIT · Python 3.10+ · Win/Linux/macOS   │  │ │ ● ● ●  bash                    │ │  │
│  │                                          │  │ ├────────────────────────────────┤ │  │
│  │ [Headline]                               │  │ │ $ gitbook-dl capture \         │ │  │
│  │ Any Docs Site →                          │  │ │     https://docs.example.com   │ │  │
│  │ LLM-Ready Markdown                       │  │ │                                │ │  │
│  │                                          │  │ │ ✓ provider: mintlify           │ │  │
│  │ [Subline]                                │  │ │ ✓ wrote docs/pages/ + llms.txt │ │  │
│  │ Bounded crawler, AST cleaner,            │  │ │ ✓ exported vector RAG JSONL    │ │  │
│  │ JSONL RAG & styled PDF books.            │  │ │ ✓ generated styled PDF book    │ │  │
│  │                                          │  │ └────────────────────────────────┘ │  │
│  │ [Badges Row]                             │  └────────────────────────────────────┘  │
│  │ [Version 9.0.1] [MCP Enabled] [fpdf2]    │                                          │
│  └──────────────────────────────────────────┘                                          │
│                                                                                        │
│  github.com/RohannShetty/gitbook-downloader                                            │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Exporting SVG to PNG for GitHub Upload

GitHub requires PNG or JPEG for repository social preview cards:

```bash
# Option 1: Export via resvg CLI (recommended)
resvg --width 1280 --height 640 assets/social-preview.svg assets/social-preview.png

# Option 2: Render in headless browser (Playwright / Puppeteer)
npx playwright screenshot --viewport-size="1280,640" assets/social-preview.svg assets/social-preview.png
```

To upload in GitHub Web UI:
1. Go to **Settings** > **General** > **Social preview**.
2. Click **Edit** > **Upload an image**.
3. Select `assets/social-preview.png`.

---

## 5. Header Badges Palette & Configuration

All badges in `README.md` follow a unified **flat-square** design with high-contrast `labelColor=090d16` (or `18181b`) and crisp status tones:

| Badge Target | Label | Message | Color Hex | Badge URL |
|---|---|---|---|---|
| **Version** | `version` | `9.0.1` | `#06b6d4` (Cyan) | `https://img.shields.io/badge/version-9.0.1-06b6d4?style=flat-square&labelColor=090d16` |
| **License** | `license` | `MIT` | `#10b981` (Emerald) | `https://img.shields.io/badge/license-MIT-10b981?style=flat-square&labelColor=090d16` |
| **Python** | `python` | `3.10+` | `#3b82f6` (Blue) | `https://img.shields.io/badge/python-3.10%2B-3b82f6?style=flat-square&labelColor=090d16` |
| **UI** | `UI` | `shadcn/ui` | `#27272a` (Zinc) | `https://img.shields.io/badge/UI-shadcn%2Fui-27272a?style=flat-square&labelColor=090d16` |
| **MCP** | `MCP` | `Enabled` | `#8b5cf6` (Purple) | `https://img.shields.io/badge/MCP-Enabled-8b5cf6?style=flat-square&labelColor=090d16` |
| **Platform** | `platform` | `Win \| Linux \| macOS` | `#64748b` (Slate) | `https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-64748b?style=flat-square&labelColor=090d16` |
| **PyPI** | `pypi` | `v9.0.1` | `#f59e0b` (Amber) | `https://img.shields.io/pypi/v/gitbook-downloader?style=flat-square&labelColor=090d16&color=f59e0b` |
| **CI** | `build` | `passing` | `#10b981` (Emerald) | `https://img.shields.io/github/actions/workflow/status/RohannShetty/gitbook-downloader/ci.yml?branch=main&style=flat-square&labelColor=090d16` |
| **Docs** | `docs` | `GitHub Pages` | `#06b6d4` (Cyan) | `https://img.shields.io/badge/docs-GitHub%20Pages-06b6d4?style=flat-square&labelColor=090d16` |

---

## 6. Verification & Invalidation Criteria

### 6.1 Independent Verification Checks
1. **Description Length Check**: Run `python -c "assert len('<description>') <= 350"`.
2. **Topic Tag Count**: Ensure all 18 tags are present and alphanumeric with hyphen format.
3. **Badge Validation**: Validate that all badge URLs return HTTP 200 without broken image icons.
4. **Contrast Verification**: Ensure WCAG AAA contrast ratio on all typography in social cards and landing pages.

### 6.2 Invalidation Conditions
- Description exceeds 350 characters.
- Topics contain spaces, uppercase letters, or unsupported characters.
- Badge styles differ from `flat-square`.
- Missing any of the 18 curated topic tags.
