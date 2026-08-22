# gitbook-downloader — Brand Guidelines

Version 1.0 · 2026-08-22
Applies to: README, GitHub social preview, TUI/CLI output styling, website, badges.

---

## 1. Brand essence

**One sentence:** the shortest path from "docs URL" to "my LLM knows this product."

**Personality:** precise · fast · invisible-smart · honest · open-source-friendly.

**Visual idea:** a document flowing into a terminal prompt. Docs go in one side;
something your LLM can read comes out the other. Everything else — near-black
canvas, hairline borders, one amber accent — exists to keep that idea quiet and clear.

---

## 2. Naming & casing

| Context | Form | Example |
|---|---|---|
| Code, commands, package name | `gitbook-downloader` (lowercase, mono) | `pip install gitbook-downloader` |
| Command | `gitbook-dl` (mono) | `gitbook-dl capture <url>` |
| Formal prose (first mention) | gitbook-downloader | "gitbook-downloader is a free, MIT-licensed tool…" |

Never: "GitBook Downloader™", "GBD", or any abbreviation. Never capitalize inside
the compound. The project is *not* affiliated with GitBook the company — the name
describes what it downloads, so always pair first mentions with context.

---

## 3. Logo

### 3.1 Concept

A **page** (rounded rectangle with two text lines) sits left; a **terminal prompt**
(chevron `❯` + cursor underscore) sits right. The page is zinc — the input. The
prompt is amber — the tool and the result. One mark, one story: *docs become a
prompt-ready corpus.*

### 3.2 Geometry spec (redrawable as SVG, 512×512 grid)

Tile (app-icon version only):

| Element | Value |
|---|---|
| Canvas | 512 × 512 |
| Tile rect | x=16, y=16, w=480, h=480, rx=104, fill `#09090b` |
| Tile border | same rect inset 1.5, stroke `#27272a`, width 3 |

Glyph (shared by both versions):

| Element | Geometry | Style |
|---|---|---|
| Page outline | rect x=100, y=142, w=170, h=228, rx=30 | stroke `#d4d4d8`, width 26, no fill |
| Text line 1 | line (148,214) → (222,214) | stroke `#52525b`, width 20, round caps |
| Text line 2 | line (148,270) → (222,270) | stroke `#52525b`, width 20, round caps |
| Prompt chevron | path M288,206 L344,256 L288,306 | stroke `#f59e0b`, width 28, round caps + joins, no fill |
| Prompt cursor | line (374,306) → (412,306) | stroke `#f59e0b`, width 28, round cap |

Proportions to preserve if redrawing: page height ≈ 45% of canvas; chevron apex
touches the page's optical midline (y=256); gap between page and chevron ≈ one
stroke width; cursor baseline aligns with chevron's lower vertex.

### 3.3 Files

| File | Use |
|---|---|
| `assets/logo.svg` | Primary mark: glyph on dark tile. Avatars, OG images, app icons. |
| `assets/logo-icon.svg` | Bare glyph, transparent. Inline in UI, favicons, places that already have a container. |

### 3.4 Clear space & minimum sizes

- **Clear space:** ≥ 25% of the mark's width on all sides. Nothing enters that box.
- **Minimum sizes:** tile mark 16 px (favicon); bare glyph 20 px; lockup height 24 px.
- Below 32 px, always use the tile version — the dark tile keeps the glyph legible.

### 3.5 Wordmark rule

The wordmark is **typeset, never baked into SVG**: `gitbook-downloader` in
JetBrains Mono Medium, sitting right of the icon at ~55% of icon height, zinc-100.
No custom lettering exists; don't create any.

---

## 4. Color

Near-black canvas, zinc scale for everything structural, **one** amber accent.
Amber appears at most once per visual composition (see §7).

| Token | Hex | Usage |
|---|---|---|
| `canvas` | `#09090b` | Backgrounds: social card, TUI theme base, page background |
| `surface` | `#101013` | Cards, terminal/code blocks sitting on canvas |
| `zinc-900` | `#18181b` | Raised surfaces, badge label background |
| `zinc-800` | `#27272a` | Hairline borders (always 1px), dividers |
| `zinc-700` | `#3f3f46` | Secondary borders, disabled states |
| `zinc-600` | `#52525b` | Tertiary text, muted glyphs, page text-lines |
| `zinc-500` | `#71717a` | Metadata text (dates, paths, captions) |
| `zinc-400` | `#a1a1aa` | Secondary body text, URLs in terminals |
| `zinc-300` | `#d4d4d8` | Primary glyph strokes, strong body text |
| `zinc-100` | `#f4f4f5` | Headings on dark |
| `white` | `#fafafa` | Hero text only |
| `amber-500` | `#f59e0b` | **THE accent:** prompt glyph, ✓ checks, one badge per row, link hover |
| `amber-600` | `#d97706` | Hover/pressed state of an amber element |

Rules:

1. Amber is a signal, not a decoration. If removing it doesn't lose meaning, remove it.
2. Never apply a gradient to amber. Never glow it. Never outline text with it.
3. No purple, no blue, no multi-hue palettes. The zinc ramp does all the quiet work.
4. On light backgrounds (rare — print, external docs): invert to white canvas,
   zinc-700 text, keep amber-600 for contrast. Prefer keeping surfaces dark.

---

## 5. Typography

| Role | Font | Weights | Notes |
|---|---|---|---|
| Prose, headings | Inter | 400 / 500 / 600 / 700 | Sentence case headings. No ALL CAPS except tiny labels. |
| Code, commands, numerals, badges | JetBrains Mono | 400 / 500 / 600 | Every command, path, and stat is mono. Always. |

Fallback stacks (use everywhere, including SVG):

- Sans: `Inter, "Segoe UI", system-ui, sans-serif`
- Mono: `"JetBrains Mono", "Cascadia Code", "SF Mono", Consolas, monospace`

Numerals: enable tabular figures in UI and tables —
`font-variant-numeric: tabular-nums`. Numbers align in columns or they're wrong.

Scale (web/README): hero 48–56 px · h2 32 px · h3 20 px · body 16 px · caption 13 px.
Line-height 1.5 body, 1.15 headings. Max prose measure ~72 characters.

---

## 6. Voice

Plain-spoken. Short sentences. Show the command, then the result.

**Words to use:** capture, docs, Markdown, LLM-ready, one command, library, snapshot, detect.
**Words to avoid:** scrape, crawl-jargon, enterprise-speak, hype adjectives
("blazing", "supercharge", "effortless", "revolutionary").

Three hard rules:

1. **Show the command.** Any feature claim within reach of a terminal gets a
   copy-pasteable command next to it.
2. **Capability claims only.** Say what the tool does; never invent a number,
   benchmark, star count, or testimonial. If we haven't measured it, we don't
   publish it. (Past marketing material fabricated these. Never again.)
3. **Layman-readable.** A developer who has never crawled a site should understand
   every sentence on first read.

---

## 7. Badges

Style: **`flat-square` only** (see README.design.md §2 for why). Compact, hairline-
adjacent, reads like a status row instead of a carnival banner.

Recipe: `labelColor=18181b` on every badge; message color from the zinc ramp;
**exactly one amber badge per row** — currently the license badge.

Fixed order: license → python → platform → PyPI.

```
https://img.shields.io/badge/license-MIT-f59e0b?style=flat-square&labelColor=18181b
https://img.shields.io/badge/python-3.10%2B-3f3f46?style=flat-square&labelColor=18181b
https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-3f3f46?style=flat-square&labelColor=18181b
https://img.shields.io/pypi/v/gitbook-downloader?style=flat-square&labelColor=18181b
```

Never: stars/downloads counters until the numbers are real and stable, `for-the-badge`,
`plastic`, `social` styles, or more than one amber badge per row.

---

## 8. Do / Don't

**Do**

- Keep compositions mostly empty; let the amber element be the only loud thing.
- Use hairline 1px `#27272a` borders for every card, table, and terminal block.
- Pair every claim with a runnable command in JetBrains Mono.
- Keep the mark geometric and flat — it must survive 16 px.
- Use snapshots/screenshots of the real TUI when showing the product.

**Don't**

- Don't recolor the mark, add shadows, gradients, bevels, or perspectives to it.
- Don't place the bare glyph on light backgrounds — use the tile version.
- Don't rotate, stretch, or animate the mark (a 150 ms fade is the only allowed motion).
- Don't publish metrics, benchmarks, quotes, or star counts we didn't earn.
- Don't use purple/blue defaults or rainbow badge rows.
- Don't write "scrape" in user-facing copy — the tool *captures*.

---

## 9. Asset inventory & export

| Asset | Notes |
|---|---|
| `assets/logo.svg` | 512×512 tile mark |
| `assets/logo-icon.svg` | Bare glyph, transparent, tight viewBox |
| `assets/social-preview.svg` | 1280×640 social card; export PNG before upload (comment in file) |

Exporting SVG → PNG: open in a browser at native size and screenshot at 2×, or
`resvg --width 1280 --height 640 input.svg output.png`. Install Inter and
JetBrains Mono locally first for faithful rendering; fallbacks are defined but
approximate.
