# Project: DocHarvest Repository Transformation

## Architecture
DocHarvest (*Turn Any Documentation Site into LLM-Ready Markdown, Vector Context & Offline Books*) is a universal documentation scraper, transformer, and offline knowledge compiler with CLI, TUI, Desktop GUI, and FastMCP Server interfaces.

### Core Modules & Boundaries
1. **Engine & Scraper**: `src/gitbook_downloader/engine.py`, `providers/` (GitBook, Mintlify, Docusaurus, ReadTheDocs, Generic), `api.py` facade, and `output_contract.py`.
2. **Export & Transformer Studio**: `src/gitbook_downloader/utils/export.py` (JSONL, PDF via `fpdf2`, Markdown, `llms.txt` manifest), `splitter.py` (AST `#` header chunking).
3. **Storage & Concurrency**: `src/gitbook_downloader/storage/manager.py` (DomainLock, atomic writes), `versioning.py` (snapshots, diff, rollback), SQLite FTS5 search index (`search/index.py`).
4. **CI/CD & Release Pipeline**: `.github/workflows/build-release.yml`, `.github/workflows/ci.yml`, `scripts/generate_release_notes.py`.
5. **Brand & Product Marketing**: `.agents/product-marketing.md`, `docs/brand/BRAND.md`.
6. **Frontend Showcase Site**: `docs/` or `frontend/` (React + Tailwind CSS + shadcn/ui interactive showcase, Terminal demo, Doc Selector, Feature Matrix, Export Studio, OpenGraph metadata, `.github/workflows/pages.yml`).
7. **Social Media Launch Playbook**: `marketing/` (X/Twitter 7-tweet thread, 4 native Reddit posts, Hacker News Show HN, Dev.to/Hashnode article, Product Hunt & GitHub trending checklist).
8. **Repository SEO & Discoverability**: Repo description (<350 chars), 18 curated GitHub topics, high-contrast badges in `README.md`, OpenGraph card specs.

---

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Single-job release creation | Refactor `.github/workflows/build-release.yml` with dedicated release job | M1 (R1) | Survey 1 |
| 2 | De-duplicated changelog & notes | Prevent duplicate Full Changelog links across multi-OS matrix runners | M1 (R1) | Survey 1 |
| 3 | Categorized release notes generator | Rich 4-category markdown generator script (`scripts/generate_release_notes.py`) | M1 (R1) | Survey 1 |
| 4 | Checksum manifest generation | Automated SHA-256 table computation for release binaries | M1 (R1) | Survey 1 |
| 5 | DocHarvest brand repositioning | Formulate DocHarvest brand identity and subtitle across all docs | M2 (R2) | Survey 2 |
| 6 | 3-Persona ICP coverage | AI & RAG Engineers, Offline Developers, DevOps/Archival Teams | M2 (R2) | Survey 2 |
| 7 | Full standard product marketing sections | Overview, ICPs, Pain Points, Differentiation, Switching, Voice, Objections | M2 (R2) | Survey 2 |
| 8 | Modern React + shadcn/ui landing site | Responsive showcase website in `docs/` using React, Vite, Tailwind, shadcn | M3 (R3) | Survey 3 |
| 9 | Hero with Terminal Typing demo | Animated terminal demo and 1-click install/download CTAs | M3 (R3) | Survey 3 |
| 10 | Interactive Doc Type Selector | Selector for GitBook, Mintlify, Docusaurus, Nextra, ReadMe, VitePress | M3 (R3) | Survey 3 |
| 11 | Feature Matrix component | Side-by-side comparison: DocHarvest vs raw scrapers/curl | M3 (R3) | Survey 3 |
| 12 | Interactive Export Studio preview | Live preview switching for Markdown, JSONL, PDF, and MCP outputs | M3 (R3) | Survey 3 |
| 13 | SEO headers & OpenGraph meta tags | Complete OG metadata, Twitter cards, favicon, and dark theme | M3 (R3) | Survey 3 |
| 14 | GitHub Pages deployment workflow | `.github/workflows/pages.yml` to build and deploy static site | M3 (R3) | Survey 3 |
| 15 | X / Twitter launch thread | 7-tweet high-hook problem/solution thread with visual cues | M4 (R4) | Survey 3 |
| 16 | Reddit multi-subreddit launch posts | 4 tailored posts for r/LocalLLaMA, r/Python, r/selfhosted, r/OpenAI | M4 (R4) | Survey 3 |
| 17 | Hacker News Show HN post | Technical Show HN post focusing on AST parsing and zero-config desktop/CLI | M4 (R4) | Survey 3 |
| 18 | Dev.to / Hashnode long-form article | Step-by-step tutorial: 30-second doc to clean RAG context | M4 (R4) | Survey 3 |
| 19 | Product Hunt & GitHub Trending kit | Tagline, maker comment, asset dimensions, promotion checklist | M4 (R4) | Survey 3 |
| 20 | Repository SEO & metadata guide | Description (<350 chars), 18 curated topic tags, OpenGraph specs | M5 (R5) | Survey 3 |
| 21 | High-contrast README badges | Refreshed shields.io flat-square badges in README.md | M5 (R5) | Survey 3 |
| 22 | Comprehensive E2E Verification | Automated verification across all deliverables (Tiers 1-5) | M6 (E2E) | All |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Release Workflow & Changelog Automation (R1) | `.github/workflows/build-release.yml`, `scripts/generate_release_notes.py`, unit tests | none | PLANNED |
| M2 | Brand Identity & Product Marketing Context (R2) | `.agents/product-marketing.md` covering 3 personas and all standard sections | none | PLANNED |
| M3 | Modern React + shadcn/ui Landing Site (R3) | `docs/` showcase site (Vite, React, Tailwind, shadcn), components, OG tags, `.github/workflows/pages.yml` | M2 | COMPLETED |
| M4 | Multi-Platform Social Media Launch Playbook (R4) | `marketing/` launch kit (X, Reddit x4, HN, Dev.to, Product Hunt, GitHub Trending) | M2 | PLANNED |
| M5 | Repository SEO & Discoverability Optimization (R5) | `README.md` badge refresh, `docs/SEO_GUIDE.md` / repo metadata specs | M2 | PLANNED |
| M6 | End-to-End Test Suite & Forensic Integrity Audit | Multi-tier test verification (Tiers 1-5), auditor validation, final signoff | M1, M2, M3, M4, M5 | PLANNED |

---

## Interface Contracts

### CI/CD Release Pipeline
- **Input**: Git tag push (`v*`) or manual `workflow_dispatch` with version tag.
- **Stage 1 (build-binaries)**: Matrix runner builds Windows `.exe`, Linux binary, macOS binary; uploads artifacts via `actions/upload-artifact@v4`.
- **Stage 2 (publish-release)**: `ubuntu-latest` runner executes `scripts/generate_release_notes.py --tag <tag> --artifacts-dir <dir> --output notes.md`, computes SHA-256 hashes, creates release with `softprops/action-gh-release@v2` (`generate_release_notes: false`).

### Product Marketing & Brand Alignment
- **Brand**: DocHarvest
- **Subtitle**: *Turn Any Documentation Site into LLM-Ready Markdown, Vector Context & Offline Books*
- **Personas**:
  1. AI & RAG Engineers
  2. Offline Developers & Researchers
  3. DevOps & Archival Teams

### Frontend Landing Site Contract
- **Build Output**: `npm run build` outputs static SPA bundle (`index.html`, assets) ready for GitHub Pages hosting.
- **Routing/Base**: Configured for relative asset paths (`base: './'`) to work seamlessly on custom domains or `owner.github.io/repo/`.

---

## Code Layout
```
d:\gitbook-downloader\
├── .github/
│   └── workflows/
│       ├── build-release.yml       # [M1] Refactored 2-stage release workflow
│       ├── ci.yml                  # Standard test CI
│       └── pages.yml               # [M3] GitHub Pages build & deploy workflow
├── .agents/
│   ├── ORIGINAL_REQUEST.md         # Immutable user request
│   ├── product-marketing.md        # [M2] Canonical DocHarvest marketing context
│   └── teamwork_preview_orchestrator/ # Metadata & orchestration state
├── docs/
│   ├── index.html                  # [M3] Landing page HTML entry
│   ├── src/                        # [M3] React/Tailwind/shadcn showcase app
│   ├── public/                     # [M3] Static assets & favicon
│   ├── package.json                # [M3] Docs site build scripts
│   ├── vite.config.ts              # [M3] Vite configuration
│   ├── tailwind.config.js          # [M3] Tailwind theme tokens
│   ├── SEO_GUIDE.md                # [M5] Repository SEO & settings guide
│   └── brand/                      # Brand assets and guidelines
├── marketing/
│   ├── README.md                   # [M4] Launch kit index & timeline
│   ├── X_TWITTER_LAUNCH_THREAD.md  # [M4] 7-tweet visual launch thread
│   ├── REDDIT_LAUNCH_POSTS.md      # [M4] 4 native subreddit posts
│   ├── HACKER_NEWS_SHOW_HN.md      # [M4] Technical Show HN submission
│   ├── DEVTO_HASHNODE_ARTICLE.md   # [M4] 30-sec doc to RAG tutorial
│   ├── PRODUCT_HUNT_PLAYBOOK.md    # [M4] PH assets, copy, maker comment
│   └── GITHUB_TRENDING_CHECKLIST.md # [M4] Repository optimization checklist
├── scripts/
│   └── generate_release_notes.py   # [M1] Categorized changelog & checksum generator
├── src/gitbook_downloader/         # Core Python engine & CLI
├── tests/
│   ├── test_release_notes.py       # [M1] Release notes generator tests
│   └── ...                         # Core engine test suite
└── README.md                       # [M5] Refreshed README with badges and DocHarvest branding
```
