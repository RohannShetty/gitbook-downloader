# DocHarvest — Multi-Platform Social Media Launch Playbook & Campaign Master Guide

> **Official Campaign Runbook for the Global Launch of DocHarvest**  
> *Turn Any Documentation Site into LLM-Ready Markdown, Vector Context & Offline Books*

---

## 1. Campaign Overview & Strategic Vision

### 1.1 The Mission
Establish **DocHarvest** as the premier open-source developer standard for documentation capture, RAG context preparation, and offline technical compilation. 

Developers and AI engineers are currently forced to choose between:
1. **Raw scrapers (`wget`, `curl`, BeautifulSoup)** that dump token-wasting HTML chrome, broken code indentation, and unnavigable directory trees.
2. **Expensive, metered cloud scraping APIs** that charge per page and exfiltrate proprietary documentation URLs to third-party servers.
3. **Heavy headless browser frameworks (Playwright, Puppeteer)** that consume 200MB+ RAM per tab, crash in CI, and wander across entire domains.

**DocHarvest solves this with zero configuration:** an intelligent, 100% local, AST-driven engine with provider auto-detection (GitBook, Mintlify, Docusaurus, ReadTheDocs, Generic), direct `.md` endpoint probing, deterministic Four-Part Output Contracts, pure-Python PDF compilation (`fpdf2`), embedded SQLite FTS5 search, and native FastMCP agent integration.

---

### 1.2 Core Messaging Pillars

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                DOCHARVEST MESSAGING PILLARS                            │
├─────────────────────────┬─────────────────────────────┬────────────────────────────────┤
│   1. CLEAN & LLM-READY  │   2. LOCAL & INDEPENDENT    │    3. DETERMINISTIC & SAFE     │
├─────────────────────────┼─────────────────────────────┼────────────────────────────────┤
│ • Zero HTML/CSS chrome  │ • 100% free & open-source   │ • Four-Part Output Contract    │
│ • AST-aware code blocks │ • No cloud API fees or keys │ • Cryptographic YAML headers   │
│ • RAG JSONL & llms.txt  │ • Air-gap & offline ready   │ • Atomic write guarantees      │
│ • Native FastMCP server │ • Pure-Python PDF (fpdf2)   │ • Semver snapshotting & diffs  │
└─────────────────────────┴─────────────────────────────┴────────────────────────────────┘
```

1. **Clean & LLM-Ready:** Eliminates 40–80% of token waste before content reaches the model. Protects code block syntax indentation and structures knowledge into vector-ready chunks.
2. **Local & Independent:** Runs entirely on local hardware with zero network telemetry, zero per-page fees, and zero cloud lock-in.
3. **Deterministic & Safe:** Enforces a rigid 4-part output contract with SHA-256 content hashes, process-aware concurrency locks (`DomainLock`), and automated snapshot diffs.

---

## 2. Target Personas & Channel Distribution Matrix

| Persona | Core Pain Point | Primary Channels | Key Value Hook | Primary Deliverable |
|---|---|---|---|---|
| **AI & RAG Engineers** | LLMs hallucinating on outdated docs; burning 50% of context window on HTML boilerplate; broken code snippets in vector chunks. | • X / Twitter<br>• `r/LocalLLaMA`<br>• `r/OpenAI`<br>• Dev.to / Hashnode | *"Feed 500-page doc sites to Cursor, Claude, or ChromaDB in 30 seconds with zero token waste."* | RAG JSONL, `llms.txt`, FastMCP Server, AST `#` Splitter |
| **Offline Developers & Researchers** | In-flight coding with broken docs; browser "Save Page As" failing on dynamic SPAs; unreadable PDF prints. | • Hacker News (Show HN)<br>• `r/Python`<br>• Dev.to / Hashnode | *"Your entire technical library, searchable and offline in one single handbook or PDF."* | Consolidated `book.md`, Pure-Python PDF (`fpdf2`), SQLite FTS5 Search |
| **DevOps & Archival Teams** | Upstream API deprecations breaking production without changelog notice; fragile scraping scripts hanging in CI. | • `r/selfhosted`<br>• Hacker News<br>• GitHub Trending | *"Self-hosted documentation archiver with active PID locking and automated semver diffing."* | Headless CLI, Semver Snapshots (`v1.0.0` → `v1.0.1`), Atomic Writes |

---

## 3. Master Launch Kit Index & Asset Directory

All ready-to-publish launch assets are located in this `marketing/` directory:

| Asset File | Target Channel / Platform | Purpose & Format | Key Highlights |
|---|---|---|---|
| [`X_TWITTER_LAUNCH_THREAD.md`](./X_TWITTER_LAUNCH_THREAD.md) | **X (Twitter)** | 7-tweet high-hook visual launch thread with visual cues & code snippets. | Problem demo, 4-part output contract, FastMCP demo, React GUI preview, CTA. |
| [`REDDIT_LAUNCH_POSTS.md`](./REDDIT_LAUNCH_POSTS.md) | **Reddit** (`r/LocalLLaMA`, `r/Python`, `r/selfhosted`, `r/OpenAI`) | 4 tailored, authentic, subreddit-native technical posts with OP first comments. | No PR fluff, deep technical credibility, code examples, architecture breakdowns. |
| [`HACKER_NEWS_SHOW_HN.md`](./HACKER_NEWS_SHOW_HN.md) | **Hacker News** (`Show HN`) | Deep-dive engineering submission & first comment explaining technical trade-offs. | AST `#` header chunking, edge-case crawl handling, SQLite FTS5, benchmarks. |
| [`DEVTO_HASHNODE_ARTICLE.md`](./DEVTO_HASHNODE_ARTICLE.md) | **Dev.to / Hashnode / Medium** | Long-form technical tutorial & benchmark article (~2,500 words). | Step-by-step RAG guide, ChromaDB integration, FastMCP setup for Cursor/Claude. |
| [`PRODUCT_HUNT_PLAYBOOK.md`](./PRODUCT_HUNT_PLAYBOOK.md) | **Product Hunt** | Complete PH launch kit: tagline, maker comment, gallery asset specs, FAQ. | Hour-by-hour launch schedule, hunter engagement strategy, 100% free positioning. |
| [`GITHUB_TRENDING_CHECKLIST.md`](./GITHUB_TRENDING_CHECKLIST.md) | **GitHub Trending** | Tactical repository optimization checklist and cross-channel traffic scheduler. | Star velocity mechanics, topic optimization, README badge refresh, conversion triggers. |

---

## 4. Chronological Distribution Timeline (T-7 to T+7)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                CHRONOLOGICAL LAUNCH TIMELINE                                    │
├───────────────┬─────────────────┬─────────────────┬───────────────────┬─────────────────────────┤
│ T-7 to T-2    │ T-1             │ T-DAY (LAUNCH)  │ T+1 to T+3        │ T+4 to T+7              │
│ Preparation   │ Final Staging   │ Blitz & Deploy  │ Deep Engagement   │ Community Scaling       │
├───────────────┼─────────────────┼─────────────────┼───────────────────┼─────────────────────────┤
│ • Build tests │ • Smoke test    │ • Product Hunt  │ • Respond to all  │ • Publish Dev.to series │
│ • Binary pack │   release .exe  │ • X/Twitter     │   HN/Reddit Qs    │ • Triage GitHub issues  │
│ • Showcase UI │ • Verify docs   │ • Hacker News   │ • Monitor GitHub  │ • Release v9.0.2 patch  │
│ • Assets prep │ • Pre-seed PRs  │ • 4x Subreddits │   star velocity   │ • Community provider PRs│
└───────────────┴─────────────────┴─────────────────┴───────────────────┴─────────────────────────┘
```

### Phase 1: Pre-Launch Staging & Hardening (T-7 to T-1)
- **T-7 (Engineering & Quality Gate):**
  - Run full test suite (`pytest`) to verify all 484 unit and integration tests pass with 0 failures.
  - Verify standalone binary compilation (`python build_exe.py` → `dist/gitbook-dl.exe`).
  - Test PyPI package installation in fresh virtual environments across Python 3.10, 3.11, and 3.12.
- **T-5 (Showcase Site & OpenGraph Verification):**
  - Deploy GitHub Pages showcase site (`https://rohannshetty.github.io/gitbook-downloader/`).
  - Validate OpenGraph preview cards (`assets/social-preview.svg` exported to 1280x640 PNG).
  - Verify social card rendering on Twitter Card Validator and OpenGraph.xyz.
- **T-3 (Visual Asset Production):**
  - Record 15-second terminal typing capture demo GIF on real 600+ page docs (`https://docs.openalgo.in/`).
  - Capture high-resolution screenshots of the React Desktop GUI (Capture Studio, Library View, Export Studio, SQLite Search).
  - Package Product Hunt gallery assets (5 slides at 1270x760).
- **T-1 (Final Readiness & Sanity Check):**
  - Stage GitHub Release `v9.0.1` with pre-compiled binaries and SHA-256 verification checksums.
  - Pre-format all markdown copy for target platforms into clipboard-ready snippets.
  - Set up monitoring dashboard for GitHub traffic, PyPI download stats, and social mentions.

---

### Phase 2: Launch Day Execution (T-Day Hour-by-Hour Blitz)
*Target Launch Day: Tuesday or Wednesday (Optimal for HN, Product Hunt, and Reddit traffic).*

| Time (PST) | Time (UTC) | Action Item | Channel / Platform | Owner / Focus |
|---|---|---|---|---|
| **00:01 PST** | 08:01 UTC | **Product Hunt Listing Goes Live** | Product Hunt | Submit listing, verify gallery images, tagline, and links. |
| **00:05 PST** | 08:05 UTC | **Post Maker Comment on Product Hunt** | Product Hunt | Post personal origin story and invite technical feedback. |
| **06:00 PST** | 14:00 UTC | **Broadcast Main Launch Thread** | X / Twitter | Publish 7-tweet visual launch thread with terminal demo GIF. |
| **06:30 PST** | 14:30 UTC | **First Quote Tweet & Tech Tagging** | X / Twitter | Retweet from personal account; tag relevant ecosystems (`@cursor_run`, `@AnthropicAI`). |
| **07:00 PST** | 15:00 UTC | **Submit Show HN Post** | Hacker News | Submit `Show HN: DocHarvest – Turn any doc site into LLM-ready Markdown, JSONL, and PDF`. |
| **07:05 PST** | 15:05 UTC | **Post HN Technical First Comment** | Hacker News | Post comprehensive architecture breakdown and engineering trade-offs. |
| **08:30 PST** | 16:30 UTC | **Submit `r/LocalLLaMA` Post** | Reddit | Post native RAG dataset & local inference guide; post OP follow-up comment. |
| **09:15 PST** | 17:15 UTC | **Submit `r/Python` Post** | Reddit | Post Python architecture & concurrency deep-dive; post OP follow-up comment. |
| **10:00 PST** | 18:00 UTC | **Submit `r/selfhosted` Post** | Reddit | Post documentation archiving & snapshot diffing guide; post OP follow-up. |
| **10:45 PST** | 18:45 UTC | **Submit `r/OpenAI` Post** | Reddit | Post Custom GPT / Claude Project context optimization guide; post OP follow-up. |
| **11:30 PST** | 19:30 UTC | **Publish Dev.to & Hashnode Articles** | Dev.to / Hashnode | Publish long-form step-by-step tutorial *"How I Turn Any Documentation into Clean RAG Context"*. |
| **13:00 PST** | 21:00 UTC | **Midday Traffic & Star Velocity Review** | Internal Dashboard | Audit GitHub stars, issue submissions, and comment threads. Respond to all queries. |
| **16:00 PST** | 00:00 UTC | **Second Wave Social Amplification** | X / Twitter | Share benchmark comparison chart and highlight community-submitted doc URLs. |
| **20:00 PST** | 04:00 UTC | **Day 1 Recap & Acknowledgments** | X / Twitter / PH | Thank community for feedback, summarize stats, and highlight top feature requests. |

---

### Phase 3: Post-Launch Amplification & Community Scaling (T+1 to T+7)
- **T+1 (Day 2 — Deep Engagement & Triage):**
  - Respond to every GitHub issue and discussion thread within 30 minutes.
  - Push quick hotfix release (`v9.0.2`) if community reports edge cases on exotic doc platforms.
  - Cross-post Dev.to article to Medium (Towards Data Science / Better Programming) with canonical URL.
- **T+2 (Day 3 — Developer Ecosystem Outreach):**
  - Share MCP server integration guide in Cursor Community Forum and Claude Developers Discord.
  - Share RAG JSONL export integration examples with LangChain and LlamaIndex maintainers.
- **T+4 (Day 5 — Video & Interactive Demos):**
  - Record a 3-minute YouTube walkthrough: *"From URL to Claude Code MCP in 60 Seconds"*.
  - Share snippet clips on LinkedIn and Twitter targeting AI engineers and developer advocates.
- **T+7 (Day 8 — Weekly Retrospective & Roadmap Reveal):**
  - Publish public retrospective on GitHub Discussions: stars gained, pages harvested, top feature requests.
  - Announce next milestone (e.g., automated cloud crawler agent, new platform extractors).

---

## 5. Campaign KPI Scorecards & Conversion Goals

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              CAMPAIGN TARGET BENCHMARKS                                │
├────────────────────────────────┬───────────────────────────┬───────────────────────────┤
│ METRIC / PLATFORM              │ DAY 1 TARGET (T-DAY)      │ WEEK 1 TARGET (T+7)       │
├────────────────────────────────┼───────────────────────────┼───────────────────────────┤
│ GitHub Stars                   │ 150 – 250 Stars           │ 600 – 1,000 Stars         │
│ GitHub Trending Status         │ Top 3 Trending in Python  │ #1 Python / Top 10 Overall│
│ Product Hunt Ranking           │ Top 3 Product of the Day  │ Product of the Week Nom.  │
│ Hacker News Ranking            │ Front Page (Top 10, >4h)  │ 100+ Upvotes, 50+ Comments│
│ Reddit Aggregate Upvotes       │ 300+ Upvotes (across 4)   │ 800+ Upvotes, 150+ Comms  │
│ PyPI Package Installs          │ 500+ Installs             │ 2,500+ Installs           │
│ GitHub Pages Showcase Traffic  │ 2,000+ Unique Visitors    │ 10,000+ Unique Visitors   │
└────────────────────────────────┴───────────────────────────┴───────────────────────────┘
```

---

## 6. Community Engagement Guidelines & Crisis Management

### 6.1 Tone & Etiquette Rules
1. **Zero PR Fluff:** Speak developer-to-developer. Use precise technical terminology (AST parsing, BFS subpath locking, SQLite FTS5 BM25, atomic file writes).
2. **Extreme Transparency:** If someone finds a bug or an unsupported doc site, never get defensive. Acknowledge the edge case immediately, explain why it occurred, and link to an issue/PR or push a fix within hours.
3. **No Fabricated Benchmarks:** Every capability claim must be backed by reproducible code in the repository.
4. **Active Attribution:** Emphasize that DocHarvest respects site copyrights and authorship by injecting source URLs, timestamps, and cryptographic hashes into every generated markdown document.

### 6.2 Rapid Response Scripts

#### Scenario A: A user posts a doc site that fails to crawl properly
> *"Thanks for sharing this URL! That site uses a custom dynamic hydration setup that bypassed our standard BFS subpath detection. I've just filed issue #XX to add dedicated selector rules for that framework. In the meantime, you can capture it immediately by passing `--path-scope /docs/` and `--extract-selectors 'article.content'`. We'll have a native patch out in `v9.0.2` today!"*

#### Scenario B: Someone asks "Why not just use Firecrawl or Jina Reader?"
> *"Great question! Firecrawl and Jina Reader are great cloud services, but DocHarvest is designed for a fundamentally different workflow: (1) It is 100% free, open-source, and runs entirely locally on your machine with zero cloud API keys or per-page bills; (2) It enforces a strict Four-Part Output Contract (`pages/`, `book.md`, `llms.txt`, and vector JSONL) with SHA-256 hashes; (3) It includes a pure-Python PDF compiler and embedded SQLite FTS5 search index; and (4) It works completely offline in air-gapped environments."*

#### Scenario C: Someone asks "Isn't scraping against the Terms of Service of some doc sites?"
> *"DocHarvest is a local developer tool designed for reading and indexing public technical documentation that is openly published for developer consumption. It operates strictly as an automated client-side user agent for local reference and private RAG context, preserving all original author attributions, source URLs, and copyright notices in YAML frontmatter."*

---

## 7. Execution Sign-off

- **Campaign Lead:** Rohan Shetty (`RohannShetty/gitbook-downloader`)
- **Product:** DocHarvest (v9.0.1)
- **Status:** **Ready to Publish**
