# DocHarvest — GitHub Trending Tactical Playbook & Optimization Checklist

> **Target Objective:** Achieve **#1 Daily Trending in Python** (150–250 stars in 24 hours) and **Top 10 Overall GitHub Trending** on Launch Day.

---

## 1. GitHub Trending Algorithm Breakdown & Star Velocity Mechanics

GitHub's Trending page algorithm is not a simple cumulative star counter; it evaluates a weighted time-decay velocity function:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   GITHUB TRENDING VELOCITY ALGORITHM                   │
├────────────────────────────────────────────────────────────────────────┤
│  Score = f( Star Velocity, Fork Velocity, Issue/PR Activity,           │
│             Unique Referrers, Global Timezone Spread )                 │
│                                                                        │
│  Key Velocity Thresholds:                                              │
│  • Daily Trending (Python):   150 – 250 stars in 24h (~8-12 stars/hr)  │
│  • Daily Trending (Overall):  300 – 500 stars in 24h (~15-25 stars/hr) │
│  • Weekly Trending (Python):  600 – 1,000 stars over 7 days            │
└────────────────────────────────────────────────────────────────────────┘
```

### Critical Algorithm Signals
1. **Star Velocity & Acceleration:** Rapid burst of stars within a 12-to-24 hour window.
2. **Referrer Domain Diversity:** Inbound traffic originating from diverse domains (X/Twitter, Hacker News, Reddit, Product Hunt, Dev.to) rather than a single source.
3. **Engagement Depth:** Repository forks, issues opened, release downloads, and wiki/discussion visits.
4. **Continuous Global Activity:** Steady star additions across US, European, and Asian timezone peaks preventing artificial single-hour spikes.

---

## 2. Pre-Launch Repository Presentation Checklist

### 2.1 Hero Section & First Impressions
- [x] **Clear Brand Title & Subtitle:** `DocHarvest — Turn Any Documentation Site into LLM-Ready Markdown, Vector Context & Offline Books`.
- [x] **High-Contrast `flat-square` Shields:**
  ```markdown
  [![Version: 9.0.1](https://img.shields.io/badge/version-9.0.1-06b6d4?style=flat-square&labelColor=090d16)](CHANGELOG.md)
  [![License: MIT](https://img.shields.io/badge/license-MIT-10b981?style=flat-square&labelColor=090d16)](LICENSE)
  [![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-3b82f6?style=flat-square&labelColor=090d16)](pyproject.toml)
  [![UI: shadcn/ui](https://img.shields.io/badge/UI-shadcn%2Fui-zinc?style=flat-square&labelColor=090d16)](https://ui.shadcn.com)
  [![MCP: Enabled](https://img.shields.io/badge/MCP-Enabled-8b5cf6?style=flat-square&labelColor=090d16)](#-ai-agent-integration-mcp)
  [![PyPI](https://img.shields.io/pypi/v/gitbook-downloader?style=flat-square&labelColor=090d16&color=f59e0b)](https://pypi.org/project/gitbook-downloader/)
  ```
- [x] **Visual Media Asset:** High-resolution OpenGraph preview banner (`assets/social-preview.png`) and 15-second terminal capture animation GIF.
- [x] **Frictionless 3-Line Quickstart:**
  ```bash
  pip install gitbook-downloader
  gitbook-dl capture https://docs.openalgo.in/
  ```

### 2.2 Core Content Architecture in README
- [x] **Four-Part Output Contract Diagram:** Visual ASCII tree explaining `pages/`, `book.md`, `llms.txt`, and `exports/`.
- [x] **Honest Feature Comparison Matrix:** Tabular comparison of DocHarvest vs `wget`/`curl` vs Firecrawl vs Crawl4AI.
- [x] **Model Context Protocol (FastMCP) Section:** Clear JSON copy-paste snippets for Cursor and Claude Desktop.
- [x] **Standalone Desktop GUI Showcase:** Screenshots of Capture Studio, Document Library, Export Studio, and SQLite FTS5 search.

---

## 3. GitHub Repository Settings & Discoverability Optimization

### 3.1 Repository Description (259 / 350 max characters)
```text
Turn any documentation site (GitBook, Mintlify, Docusaurus, ReadTheDocs) into clean, LLM-ready Markdown, vector JSONL & offline PDF books. Includes high-performance CLI, React desktop GUI & AI agent MCP server. Free, open-source & 100% local.
```

### 3.2 Canonical Website URL
```text
https://rohannshetty.github.io/gitbook-downloader/
```

### 3.3 Curated GitHub Topics (18 High-Traffic Tags)
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
vector-database
llm-tools
langchain
llamaindex
cursor-ide
claude-code
python
react
shadcn-ui
```

### 3.4 GitHub Social Preview Card
- Asset: `assets/social-preview.png` (Exported from `assets/social-preview.svg` at 1280 × 640 px).
- Text contrast: `> 11:1` WCAG AAA compliant.

---

## 4. Cross-Platform Traffic Synchronizer (Launch Day Wave Plan)

To maintain consistent star velocity throughout the 24-hour cycle, stagger external traffic waves across global timezones:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   24-HOUR TRAFFIC SYNCHRONIZATION MAP                  │
├───────────────┬────────────────────────────────────────────────────────┤
│ 00:01 PST     │ Wave 1: Product Hunt Launch (Early European Traffic)   │
│ 06:00 PST     │ Wave 2: X/Twitter 7-Tweet Visual Thread (US East Coast)│
│ 07:00 PST     │ Wave 3: Hacker News "Show HN" Submission (Tech Core)   │
│ 08:30–10:45   │ Wave 4: 4x Subreddit Blitz (r/LocalLLaMA, r/Python)    │
│ 11:30 PST     │ Wave 5: Dev.to & Hashnode Long-Form Tutorial Launch    │
│ 16:00 PST     │ Wave 6: Second Social Push (US West Coast / APAC Morn) │
│ 20:00 PST     │ Wave 7: Daily Wrap-up & Community Thank You            │
└───────────────┴────────────────────────────────────────────────────────┘
```

---

## 5. In-Tool Conversion Triggers (Turning CLI Users into Stargazers)

Developers who test the tool via CLI or Desktop GUI are the highest-intent stargazers. Embed polite, non-intrusive conversion triggers:

### 5.1 CLI Successful Capture Footer
When a capture finishes successfully:
```text
[16:42:20] ✨ Indexed 673 pages into local SQLite FTS5 search engine in 18.2s!
[16:42:21] ⭐ Enjoying DocHarvest? Star us on GitHub: https://github.com/RohannShetty/gitbook-downloader
```

### 5.2 Desktop GUI Status Bar
Include a subtle, clean GitHub star button with a live star count in the header navigation bar of the React Desktop GUI.

---

## 6. Post-Trending Retention & Contributor Onboarding Plan

Once Trending status is achieved, maintain momentum through proactive community management:

### 6.1 Community & Issue SLAs (Launch Week)
- **Response Time for Issues:** < 30 minutes during waking hours.
- **Triage Protocol:** Apply labels immediately (`bug`, `enhancement`, `good first issue`, `documentation-provider`).
- **Edge-Case Patching:** Release patch versions (`v9.0.2`, `v9.0.3`) within 12–24 hours when users submit new doc framework selector rules.

### 6.2 Pre-Seeded "Good First Issue" Backlog
1. `Add MkDocs Material Admonition Extractor rule in providers/`
2. `Add export to EPUB format alongside PDF in export.py`
3. `Add dark/light theme toggle in Desktop GUI reader`
4. `Support custom cookies file for private enterprise doc portals`

### 6.3 Contributor Welcome Template
```markdown
Thank you for opening this issue / pull request! 🎉

DocHarvest is driven by the developer community. We review and merge community PRs quickly.
Please make sure all tests pass (`pytest`) and format compliance is maintained.
```
