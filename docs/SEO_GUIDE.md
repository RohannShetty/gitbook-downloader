# DocHarvest — Repository SEO & Discoverability Guide

**Version:** 2.0.0
**Target Repository:** `RohannShetty/gitbook-downloader` (Brand: **DocHarvest**)
**Last Updated:** 2026-09-05

> **v2.0 changelog:** Resolved the "scraper keywords vs compiler positioning" tension with a two-layer keyword strategy (§2). Added the implemented on-site technical SEO layer — sitemap, robots, canonical URL, JSON-LD `SoftwareApplication` + `FAQPage` structured data, OG image, `llms.txt` (§5). Added the canonical metrics table (§3) so no SEO surface ever quotes a stale number again. Added the engagement/time-on-site playbook (§7). Refreshed all badge/version references (v11.0.4, 665 tests, 12 MCP tools, 14 client configs). Recorded the startupbar.co widget decision (§7.4).

---

## 1. Executive Summary

This guide is the canonical SEO configuration for DocHarvest (*Turn Any Documentation Site into LLM-Ready Markdown, Vector Context & Offline Books*). It covers repository discoverability (GitHub metadata, topics, social preview), on-site technical SEO (the Next.js showcase at `docs/`), structured data for rich results, and the engagement mechanics that convert search traffic into installs.

Goals, in priority order: (1) more qualified traffic from high-intent documentation-capture queries, (2) longer on-site dwell via FAQ rich results and in-page flow, (3) zero claim drift between search snippets and on-page copy.

---

## 2. Keyword & Positioning Decision (the "scraper" resolution)

**The tension:** the brand rule says DocHarvest is a *documentation compiler, not a scraper* — but the highest-volume search queries in this space literally contain "scraper" (`documentation scraper`, `mintlify scraper`, `gitbook scraper`).

**The decision (v2.0): two-layer keyword strategy.**

| Layer | Where it appears | Language |
|---|---|---|
| **Discovery layer** | `<meta keywords>`, GitHub topics, ad/search queries, directory tags | Scraper-adjacent terms ARE used — that's where the traffic is. Metadata is invisible on the page, so it cannot contradict on-page positioning. |
| **Positioning layer** | Headlines, body copy, OG text, README, listings | DocHarvest is always a *compiler / harvester*; "scraper" only ever describes alternatives ("cloud scraping APIs charge per page…"). |

**Rule for all future copy:** you may *capture* a scraper query; you may never *self-describe* as a scraper. A HN commenter quoting `meta keywords` at the honest-scope section is expected and harmless — the keywords tag is not rendered content. If this ever feels uncomfortable, the fallback is dropping only `documentation-scraper` from GitHub topics (the highest-cost keyword to lose) and keeping the rest.

### Long-tail queries to win (mapped to on-page sections)

| Query pattern | Landing element |
|---|---|
| "alternative to firecrawl/jina for docs" | FAQ Q2 (cloud API comparison) |
| "turn docs into llms.txt" | Output Contract section + `llms.txt` card |
| "cursor mcp documentation server" | MCP showcase + 14-client configs |
| "scrape docs for RAG / chromadb" | RAG JSONL card + benchmark numbers |
| "download documentation offline pdf" | PDF handbook card + GUI section |
| "watch vendor docs for changes" | Snapshot diffing feature rows |

---

## 3. Canonical Metrics (single source for any SEO copy)

**Never write a number in a snippet, topic, listing, or ad that isn't in this table.** Sources: `docs/lib/stats.ts` (site), README (repo), `src/gitbook_downloader/api.py` (contract).

| Metric | Canonical value | Source of truth |
|---|---|---|
| Reference capture | **673 pages in 18.2s** (full OpenAlgo suite) | User-confirmed 2026-09-04 |
| Token reduction | **~83%** (82.8% measured) | HN benchmark |
| Throughput | **~37 pages/sec** (673 / 18.2) | Derived |
| Raw-page noise share | **80–85% of raw page bytes** | HN bottleneck analysis |
| MCP tools | **12** (+2 resources, 2 prompts) | `mcp/server.py` |
| Documented AI clients | **14** | README config matrix |
| Doc platforms | **8 dedicated + generic** | `providers/` |
| Test suite | **665 passing** | `uv run pytest` (2026-09-04) |
| Version | **v11.0.4** | `pyproject.toml` |
| License / price | **MIT / $0** | LICENSE |

---

## 4. GitHub Repository Metadata

### 4.1 Repository Description (154 / 350 chars)

```text
Turn any documentation site into LLM-ready Markdown, RAG JSONL, llms.txt & offline PDFs. 12-tool FastMCP server, zero-config CLI, desktop GUI. 100% local & MIT.
```

### 4.2 GitHub Topic Tags (20 curated — GitHub max is 20)

```text
rag
llms-txt
documentation-scraper
documentation-compiler
mcp-server
ai-agents
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

(New in v2.0: `documentation-compiler` and `ai-agents` — the compiler term claims the positioning query, `ai-agents` rides the fastest-growing adjacent topic graph. This replaces the guide's previous 18-tag set.)

### 4.3 Apply via GitHub CLI

```bash
gh repo edit RohannShetty/gitbook-downloader \
  --description "Turn any documentation site into LLM-ready Markdown, RAG JSONL, llms.txt & offline PDFs. 12-tool FastMCP server, zero-config CLI, desktop GUI. 100% local & MIT." \
  --homepage "https://rohannshetty.github.io/gitbook-downloader/" \
  --add-topic documentation-compiler \
  --add-topic ai-agents \
  --enable-issues=true \
  --enable-wiki=false \
  --enable-discussions=true
```

(Existing 18 topics stay; the two above are additive.)

### 4.4 Header Badge Palette (README — current set)

| Badge | Message | Color |
|---|---|---|
| Version | `11.0.4` | `#06b6d4` Cyan |
| License | `MIT` | `#10b981` Emerald |
| Python | `3.10+` | `#3b82f6` Blue |
| Tests | `665 passing` | `#10b981` Emerald |
| PyPI | live `pypi/v/gitbook-downloader` | `#f59e0b` Amber |
| Showcase | `Live Showcase` | `#06b6d4` Cyan |

All badges: `style=flat-square&labelColor=090d16`. The v2.0 README audit deliberately trimmed the UI/Platform/MCP badges (distill pass) — do not re-add them; the badge row is a first-impression surface, not an inventory.

---

## 5. On-Site Technical SEO (implemented 2026-09-05)

All of the following ship with the Next.js static export (`cd docs && npm run build` → `out/`):

| Artifact | Implementation | What it earns |
|---|---|---|
| **sitemap.xml** | `docs/app/sitemap.ts` → emits at build | Full-site crawl eligibility; auto-submitted via robots.txt |
| **robots.txt** | `docs/app/robots.ts` → points at sitemap | Crawler directive + sitemap discovery |
| **Canonical URL** | `metadataBase` + `alternates.canonical` in `app/layout.tsx` | Consolidates ranking to `rohannshetty.github.io/gitbook-downloader/` (GitHub Pages also serves the site without trailing content variants) |
| **SoftwareApplication JSON-LD** | Injected in `layout.tsx` `<head>` | Rich result eligibility: price ($0), license, platform, feature list, author |
| **FAQPage JSON-LD** | Generated from `data/showcaseData.ts:FAQ_ITEMS` — the same questions are visible on-page, as Google requires | FAQ rich results expand SERP real estate; the comparison answer ("vs Firecrawl/Jina") is the conversion moment |
| **OG/Twitter image** | `public/assets/og-capture-studio.png` (1024×576, real product screenshot) wired into `openGraph.images` + `twitter.images` | Link shares render a real product visual instead of a blank card |
| **llms.txt** | `public/llms.txt` — the product's own manifest standard, applied to itself | AI-agent discovery surface; on-brand linkable asset |

**Title & meta (v2.0):**
- Title: `DocHarvest — Documentation Compiler for LLMs, RAG & MCP` (55 chars — fits Google's ~60px truncation; "compiler" is the positioning keyword, "MCP" is the rising query)
- Description: loss-framed, verb-first, front-loaded (see `app/layout.tsx`)
- `og:title` and `twitter:title` match the title exactly

**Outstanding (tool-blocked):** exporting the branded `public/assets/social-preview.svg` (1280×640 spec in §6) to PNG — `resvg`/`cairosvg` unavailable and Playwright browsers not installed in this environment. Run once, anywhere with browsers:

```bash
cd docs && npx playwright install chromium && \
  npx playwright screenshot --viewport-size="1280,640" \
  "$(pwd)/public/assets/social-preview.svg" public/assets/social-preview.png
```

…then swap `og-capture-studio.png` → `social-preview.png` in `layout.tsx` (both `openGraph` and `twitter`) and upload the same PNG as the GitHub social preview (Settings → General → Social preview).

---

## 6. OpenGraph Social Preview Asset Specification

| Property | Value |
|---|---|
| Canvas | 1280 × 640 px (2:1) |
| Background | `#09090b` (Zinc-950) + dot-grid texture (`#1b1b20`, r=1.4, 44px step) |
| Border | `1px #27272a`, rx=24 |
| Accents | `#06b6d4` (Cyan) + `#f59e0b` (Amber) |
| Typography | Inter + JetBrains Mono, contrast > 12:1 |
| Source | `docs/public/assets/social-preview.svg` (spec card: logo lockup, headline "Any Docs Site → LLM-Ready Markdown", live terminal mock, badges) |

Export procedure in §5. Until then the product screenshot carries OG duty.

---

## 7. Engagement / Time-on-Site Playbook

Traffic without dwell is wasted — these are the mechanics that keep the audience the keywords bring in.

### 7.1 In-page flow (implemented)
- **Hero → proof in one viewport:** loss-framed headline, agent pills that swap *real config snippets* (functional since 2026-09-04), pip copy-bar, and the 673/18.2/83% metric strip.
- **Simulated terminal as demo:** four tabs (Crawl Logs / AST Filter / Vector JSONL / MCP stdio) let visitors "run" the product without installing — ending on the peak line ("✨ Done — book.md, llms.txt … ready to open").
- **FAQ anchors:** the five FAQ items are the objection-handling sequence; FAQPage rich results land searchers directly on answers, and each answer links back into feature sections.

### 7.2 Next dwell levers (recommended, not yet built)
1. **Anchor-linked section nav in the header** (Output Contract · Agents · FAQ) — gives scrolling a skeleton instead of a wall.
2. **"Try it in 30 seconds" strip on the showcase** mirroring the README's — currently the install modal is the first command a visitor sees; surfacing the two-line command earlier shortens time-to-value.
3. **Real capture sample** — link the actual `book.md`/`llms.txt` output of the reference capture as downloadable artifacts ("see the real output") — strongest possible proof and a natural link magnet.

### 7.3 Performance posture
Static export, zero client-side data fetching, fonts self-hosted via `next/font`. Core Web Vitals headroom is large; keep it that way — any new third-party script needs the §7.4 justification bar.

### 7.4 Third-party widget decision (recorded 2026-09-05)
**`startupbar.co` widget: KEEP.** Owner decision. It loads with `async` so it cannot block first paint. Note for future audits: this is a known, accepted third-party script on a page marketing "zero telemetry" (the product is telemetry-free; the *showcase site* carries this widget by choice). Do not flag it as a defect in copy reviews — it is documented policy, and the distinction above is the approved answer if a visitor asks.

---

## 8. Verification & Invalidation Criteria

1. **Canonical metrics rule:** every number in any SEO surface must exist in §3. Run `grep -rn "89%\|364\|531\|484\|20 pgs" docs/ README.md marketing/` before publishing — expect zero hits.
2. **Positioning rule:** `grep -rn "we scrape\|our scraper" docs/ README.md` — expect zero hits (scraper terms only in metadata/topics/alternative descriptions).
3. **Description length:** `python -c "assert len('<description>') <= 350"`.
4. **Topic tags:** ≤ 20, lowercase, hyphenated.
5. **Structured data:** validate `out/index.html` JSON-LD at `validator.schema.org` after each build; FAQPage entries must match visible FAQ text exactly.
6. **Rich-result eligibility:** re-test after every FAQ copy change (Google invalidates mismatched FAQPage markup).
7. **Sitemap/robots:** after `npm run build`, confirm `out/sitemap.xml`, `out/robots.txt`, `out/llms.txt` exist.
8. **OG image:** confirm `out/assets/og-capture-studio.png` exists and `layout.tsx` references resolve against `https://rohannshetty.github.io/gitbook-downloader/`.
