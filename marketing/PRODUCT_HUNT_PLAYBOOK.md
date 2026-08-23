# DocHarvest — Product Hunt Launch Playbook & Maker Kit

> **Official Product Hunt Launch Campaign Blueprint**  
> **Launch Day:** Tuesday / Wednesday at 12:01 AM PST (08:01 UTC)  
> **Goal:** Secure Top 3 Product of the Day, drive 500+ upvotes, and establish DocHarvest as the premier open-source documentation capture tool for AI.

---

## 1. Product Listing Metadata

| Field | Value / Specification | Character Count / Validation |
|---|---|---|
| **Product Name** | `DocHarvest` (formerly `gitbook-downloader`) | Exact Brand Name |
| **Tagline** | `Turn any doc site into LLM-ready Markdown, JSONL & PDF` | 55 / 60 max chars |
| **Primary Category** | `Developer Tools` | Core Product Hunt Category |
| **Secondary Categories** | `Artificial Intelligence`, `Open Source`, `Productivity` | Tag taxonomy |
| **Pricing** | `Free / 100% Open Source (MIT)` | No paywalls, no subscriptions |
| **Website URL** | `https://rohannshetty.github.io/gitbook-downloader/` | Canonical GitHub Pages Showcase |
| **GitHub Repository** | `https://github.com/RohannShetty/gitbook-downloader` | Source Code |
| **Makers** | Rohan Shetty (`@rohannshetty`) | Verified Maker Profile |

---

## 2. Product Description (Short & Long)

### Short Description (For Directory Listings)
```text
Free, open-source tool to capture entire documentation websites (GitBook, Mintlify, Docusaurus, ReadTheDocs) into pristine Markdown, vector RAG JSONL, and offline PDF books. Available as a Python CLI, React desktop GUI, and FastMCP server for Cursor and Claude Code.
```

### Long Description (For Product Details Tab)
```text
DocHarvest turns complex, multi-hundred-page technical documentation websites into clean, structured knowledge ready for AI coding assistants, vector databases, and offline reading.

🚀 Key Capabilities:
• Provider Auto-Detection: Automatically detects GitBook, Mintlify, Docusaurus, ReadTheDocs, and generic doc sites.
• Direct .md Probing: Probes raw markdown endpoints directly to retrieve pristine author formatting without HTML conversion loss.
• Four-Part Output Contract: Every capture outputs modular pages/ with SHA-256 YAML headers, a single book.md handbook with auto-generated Table of Contents, an llms.txt discovery manifest, and vector-ready JSONL.
• Model Context Protocol (FastMCP): Connect directly to Cursor and Claude Code so your AI agent can search and read external documentation autonomously.
• Pure-Python PDF Generation: Generates publication-grade printable PDFs with styled code blocks using pure Python (fpdf2) with zero external C-dependencies.
• Local SQLite FTS5 Full-Text Search: Embedded BM25 search engine across all downloaded documentation libraries.
• 100% Free & Local: Runs completely offline on your hardware with zero telemetry, zero per-page fees, and zero cloud lock-in.
```

---

## 3. Gallery Asset Specifications & Wireframes (1270 × 760 px)

All gallery images must be high-contrast, dark-mode (`#09090b` canvas), with 1px hairline borders (`#27272a`) and amber accent accents (`#f59e0b`).

```
┌────────────────────────────────────────────────────────────────────────┐
│ SLIDE 1: HERO / THE VALUE PROPOSITION                                  │
├────────────────────────────────────────────────────────────────────────┤
│ [Left 50%]                                  [Right 50%]                │
│ • DocHarvest Tile Mark (512x512)            • Terminal Demo Window:    │
│ • H1: Turn Any Documentation Site into      • `gitbook-dl capture ...` │
│       LLM-Ready Markdown & RAG Datasets     • 673 pages in 18.2s       •
│ • Subtitle: 100% Local, Free & Open Source  • Four-Part Output Tree    │
│ • Badges: MIT | Python 3.10+ | FastMCP      • Amber prompt cursor      │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ SLIDE 2: THE CAPTURE STUDIO (REACT 18 DESKTOP GUI)                     │
├────────────────────────────────────────────────────────────────────────┤
│ • Full-screen high-res screenshot of `assets/capture_studio.png`       │
│ • Highlights: Animated radial progress ring, live download speed       │
│ • Color-coded real-time terminal output with log level filters         │
│ • Active process-aware domain lock badge (PID inspection)              │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ SLIDE 3: THE FOUR-PART OUTPUT CONTRACT                                 │
├────────────────────────────────────────────────────────────────────────┤
│ • Visual split of 4 generated artifacts:                              │
│   1. `pages/**/*.md` (YAML frontmatter + SHA-256 content hashes)       │
│   2. `book.md` (Unified handbook with auto-generated TOC)              │
│   3. `llms.txt` (Standardized agent discovery index)                   │
│   4. `exports/*.jsonl` & `*.pdf` (Vector datasets & styled PDF)        │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ SLIDE 4: FAST-MCP INTEGRATION (CURSOR & CLAUDE CODE)                   │
├────────────────────────────────────────────────────────────────────────┤
│ • Split view:                                                          │
│   - Left: `gitbook-dl mcp` configuration JSON                          │
│   - Right: Cursor IDE chat window invoking `search_docs` and           │
│     retrieving accurate, fresh documentation context autonomously      │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ SLIDE 5: FEATURE MATRIX (DOCHARVEST VS WGET / CLOUD SCRAPERS)          │
├────────────────────────────────────────────────────────────────────────┤
│ • Clean tabular comparison: DocHarvest vs curl vs Firecrawl vs Crawl4AI│
│ • Key row highlights: Zero cloud fees, pure-Python PDF, SQLite FTS5    │
│ • Bottom CTA: `pip install gitbook-downloader`                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Maker First Comment (The Launch Story)

*Post this comment immediately after the submission is published (12:05 AM PST).*

```text
Hey Product Hunt! 👋 

I'm Rohan, creator of DocHarvest (formerly gitbook-downloader).

Like many developers building AI applications and coding with assistants like Cursor and Claude Code, I ran into a massive wall: **modern documentation websites are terrible for LLM context windows**.

Whenever a new framework releases a major update, AI models hallucinate because the docs are past their training cutoff. But when you try to scrape documentation portals with wget or standard scrapers, you end up with:
❌ 80%+ of tokens wasted on navigation sidebars, headers, and cookie popups.
❌ Broken code block indentation that ruins Python, YAML, and Rust code.
❌ Scrapers wandering across entire websites instead of staying within /docs/.
❌ Hosted scraping APIs charging expensive per-page fees to put your docs in the cloud.

I built DocHarvest to be the definitive, 100% local, one-command solution:

✨ What makes DocHarvest different:
1. Provider Auto-Detection: Automatically detects GitBook, Mintlify, Docusaurus, ReadTheDocs, and generic doc sites.
2. Direct .md Probing: Probes raw markdown endpoints directly to get pristine author markdown straight from the source.
3. The Four-Part Output Contract: Every capture gives you modular pages with SHA-256 YAML frontmatter, a single book.md handbook with auto-generated TOC, an llms.txt manifest, and RAG JSONL datasets.
4. Native FastMCP Server: Wire it straight into Cursor or Claude Desktop so your AI agent can search and read external documentation on its own.
5. Pure-Python PDF Studio: Compiles entire multi-hundred page doc sites into publication-grade printable PDFs with zero external C-dependencies.
6. Embedded SQLite FTS5 Search: Instant BM25 full-text search across your entire offline documentation library.

DocHarvest is 100% free and open-source under the MIT license. No cloud subscriptions, no API keys, and zero telemetry.

Install via pip: `pip install gitbook-downloader`
Or grab the standalone desktop application from GitHub: https://github.com/RohannShetty/gitbook-downloader

Check out our interactive showcase: https://rohannshetty.github.io/gitbook-downloader/

I'd love to hear your thoughts, feedback, and what documentation platforms you'd like us to support next! 🚀
```

---

## 5. Hour-by-Hour Launch Day Runbook (PST)

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PRODUCT HUNT LAUNCH DAY RUNBOOK (PST)                │
├───────────────┬────────────────────────────────────────────────────────┤
│ 12:01 AM PST  │ 🚀 Product Hunt submission goes live                   │
│ 12:05 AM PST  │ 💬 Post Maker First Comment with origin story          │
│ 06:00 AM PST  │ 🧵 Launch 7-Tweet visual thread on X/Twitter           │
│ 07:00 AM PST  │ ⚡ Submit Hacker News "Show HN" submission             │
│ 08:30 AM PST  │ 💬 Post r/LocalLLaMA native launch guide               │
│ 09:15 AM PST  │ 🐍 Post r/Python technical architecture breakdown      │
│ 10:00 AM PST  │ 🏠 Post r/selfhosted documentation archiver guide      │
│ 10:45 AM PST  │ 🤖 Post r/OpenAI context optimization guide            │
│ 11:30 AM PST  │ 📝 Publish long-form tutorial on Dev.to & Hashnode     │
│ 13:00 PM PST  │ 📊 Midday progress audit & respond to all PH comments  │
│ 17:00 PM PST  │ 🔄 Second wave social push on LinkedIn & Discord       │
│ 21:00 PM PST  │ 🎉 Day 1 thank you comment & wrap-up on Product Hunt   │
└───────────────┴────────────────────────────────────────────────────────┘
```

---

## 6. Product Hunt FAQ for Hunters & Commenters

### Q1: Is DocHarvest completely free?
**A:** Yes, 100% Free & Open Source under the MIT License. There are no paid tiers, no per-page charges, and no hidden subscriptions.

### Q2: Does DocHarvest send my data or scraped URLs to the cloud?
**A:** No. DocHarvest is strictly local-first and self-hosted. It performs all crawling, parsing, PDF generation, and SQLite search indexing locally on your machine with zero network telemetry.

### Q3: What documentation platforms are currently supported?
**A:** DocHarvest includes dedicated extractors for **GitBook**, **Mintlify**, **Docusaurus**, **ReadTheDocs**, **Nextra**, **ReadMe**, **VitePress**, **MkDocs**, and a robust generic fallback extractor that handles custom HTML documentation.

### Q4: How does the FastMCP integration work with Cursor?
**A:** Simply add DocHarvest to your Cursor MCP settings (`.cursor/mcp.json`) pointing to `gitbook-dl mcp`. Cursor's AI agent can then autonomously call `search_docs` and `read_doc_page` to retrieve fresh documentation while writing code.

### Q5: How fast is it?
**A:** On a standard broadband connection with 5 streaming concurrency workers, DocHarvest captures and compiles 670+ pages of documentation into clean Markdown, RAG JSONL, and PDF in **18.2 seconds**.

### Q6: Can I run this in CI/CD or as a scheduled backup job?
**A:** Yes! DocHarvest includes a headless CLI mode and process-aware active-PID domain locks (`DomainLock`), making it safe and reliable to run in GitHub Actions or cron jobs. You can even use `gitbook-dl diff` to automatically detect upstream documentation changes.
