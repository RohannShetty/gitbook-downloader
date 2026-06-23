# 🚀 Launch Plan — GitBook Downloader v4.0

> Complete social media strategy. Copy-paste ready. Timeline included.

---

## 📋 Pre-Launch Checklist

- [ ] Star the repo yourself (social proof — people follow early stars)
- [ ] Add repo to your GitHub profile README pin
- [ ] Screenshot the app (dashboard, download progress, split results)
- [ ] Record a 15-second demo GIF (URL → download → split → ChatGPT upload)
- [ ] Open `assets/social-preview.html` → screenshot → set as repo's Social Preview image in Settings

---

## 🎯 Target Audiences

| Audience | Pain Point | Hook |
|----------|-----------|------|
| **AI/LLM devs** | Context window limits | "Feed entire docs to your LLM in 30 seconds" |
| **RAG builders** | Manual chunking is tedious | "Header-boundary splitter that never breaks code blocks" |
| **Open source devs** | Can't keep 20 docs tabs open | "One .md file. Searchable. Offline." |
| **Indie hackers** | Building with unfamiliar APIs | "Download any API docs → feed to Cursor/Claude" |
| **Students** | Need offline study materials | "Download docs before your flight" |
| **Enterprise devs** | Behind firewalls, no internet | "Download once, reference forever" |

---

## 🗓️ Launch Timeline

| Day | Time | Platform | Action |
|-----|------|----------|--------|
| **Mon** | 9 AM EST | GitHub | Set up repo, star, pin to profile |
| **Mon** | 12 PM | Twitter | Teaser tweet: "Building something for AI devs..." |
| **Tue** | 12:01 AM PST | **Product Hunt** | 🚀 LAUNCH (best time for dev tools) |
| **Tue** | 7 AM EST | Hacker News | Show HN post |
| **Tue** | 9 AM EST | r/Python | Project post |
| **Tue** | 10 AM EST | r/LocalLLaMA | Text post (this audience LOVES doc-to-LLM tools) |
| **Tue** | 12 PM | Twitter | Main launch thread (4 tweets) |
| **Tue** | 2 PM | r/programming | Link post |
| **Wed** | 9 AM | Dev.to | Long-form article |
| **Wed** | 12 PM | LinkedIn | Professional post |
| **Wed** | 2 PM | r/MachineLearning | [P] post |
| **Thu** | Anytime | YouTube Shorts | 60-second demo |
| **Fri** | Anytime | Newsletter pitches | Submit to TLDR, Changelog, Python Weekly |

---

## 🦄 PRODUCT HUNT

### Tagline
**Download any GitBook docs site → split into AI-ready chunks in 2 minutes**

### Description
Stop copy-pasting documentation into ChatGPT one page at a time. GitBook Downloader finds every page on a GitBook site, downloads clean markdown (no nav bars, no cookie banners), and splits it into perfectly-sized chunks that respect headers and code blocks. 673 pages of docs.openalgo.in → 5 MB → 5 chunks. Desktop app, one click. No Python required.

### Topics
`Developer Tools` `AI` `Open Source` `Productivity` `GitHub`

### Maker Comment (post immediately after launch)

Hey Product Hunt! 👋

I built this after spending 3 hours copy-pasting OpenAlgo's documentation into ChatGPT one page at a time. There are 673 pages. I made it to page 40 before giving up.

**The problem:** AI tools like ChatGPT, Claude, and Cursor are incredible — but they can't browse entire documentation sites. Their context windows are limited, and manually feeding them pages is painful.

**What GitBook Downloader does:**

1. **Finds every page** — BFS crawler that discovers pages buried in submenus and sidebars
2. **Downloads clean markdown** — strips navigation, footers, cookie banners. Just the content.
3. **Splits intelligently** — chunks aligned to markdown headers. Never breaks mid-sentence or mid-code-block.
4. **Updates incrementally** — docs changed? One click fetches only new pages.

**Real-world test: docs.openalgo.in**
- 673 pages found
- 5.0 MB of clean markdown (the old wget approach produced 38 MB of garbage)
- 5 perfect chunks
- Uploaded to ChatGPT in 30 seconds

**Why it's better than wget/curl:**
- wget downloads HTML with nav bars, sidebars, scripts — useless for LLMs
- curl gets one page at a time
- Neither handles GitBook's sidebar navigation
- Neither splits output into AI-friendly chunks

**Tech stack:** Python 3.8+, requests, BeautifulSoup, markdownify, customtkinter. MIT license.

**I'd love feedback on:**
- What other doc platforms should I support? (Docusaurus? ReadTheDocs? MkDocs?)
- What chunk sizes work best for your LLM workflows?
- Would a web UI version be useful?

Thanks for checking it out! 🚀

---

## 🧠 HACKER NEWS — Show HN

### Title
**Show HN: GitBook Downloader — download any GitBook docs site and split into AI-ready chunks**

### Body

I built a tool that downloads entire GitBook documentation sites and splits them into LLM-friendly markdown chunks.

**The problem I was solving:** I needed OpenAlgo's full API documentation inside ChatGPT to build a trading bot. The docs have 673 pages. Copy-pasting them one-by-one was going to take hours. wget downloaded HTML garbage — navigation bars, cookie banners, sidebars — 90% of the bytes weren't documentation.

**What it does:**

```bash
# Step 1: Download the entire site (finds all 673 pages)
gitbook-dl download https://docs.openalgo.in/

# → 5.0 MB of clean markdown, 673 pages, 2 minutes

# Step 2: Split into AI-friendly chunks
gitbook-dl split downloaded_docs.md

# → 5 chunks, each ~1 MB, aligned to markdown headers
# → Never breaks mid-sentence, never cuts a code block
```

**How it works:**
- BFS crawler starts at the root and follows every internal link
- Parallel downloads (5 workers) with streaming pipeline — pages download as they're discovered
- URL normalization strips #fragments so you don't get 13 copies of the same page
- markdownify converts HTML → clean markdown
- Header-boundary splitter respects document structure

**Interesting finding:** The old approach (wget following #anchor links) produced a 38 MB file that was 92% duplicate content — the same pages repeated 13x with different fragment URLs. The new engine produces 5 MB with 18x more unique pages and zero duplicates.

**It also has:**
- Desktop GUI (Stripe-themed, one-click .exe, no Python required)
- Incremental updates (only fetch new/changed pages)
- Download history dashboard

**Repo:** https://github.com/RohannShetty/gitbook-downloader

Curious what other documentation platforms people would want supported. Docusaurus? ReadTheDocs?

---

## 🐦 TWITTER/X — Launch Thread

### Tweet 1 (Hook)
```
I spent 3 hours copy-pasting docs into ChatGPT.

Page 40 of 673, I gave up and built a tool instead.

Now it takes 2 minutes.

🧵
```

### Tweet 2 (The Problem)
```
The problem:
• AI tools can't browse entire doc sites
• Context windows are limited
• Copy-pasting 673 pages = hours of pain
• wget downloads HTML garbage (nav bars, cookies, scripts)

I needed a better way.
```

### Tweet 3 (The Solution)
```
What I built:
⬡ GitBook Downloader

1. Finds EVERY page (BFS crawler, no missed pages)
2. Downloads CLEAN markdown (no nav, no footer, no junk)
3. Splits into AI-ready chunks (never breaks a sentence)
4. Updates incrementally (only new pages)

Python CLI + .exe GUI. MIT license.
```

### Tweet 4 (Results + CTA)
```
Real-world test: docs.openalgo.in
• 673 pages → 5.0 MB → 5 chunks
• 2 minutes, zero copy-paste
• Uploaded to ChatGPT in 30 seconds

Repo: github.com/RohannShetty/gitbook-downloader

Stars appreciated ⭐
```

---

## 📝 REDDIT — r/LocalLLaMA

### Title
**I built a tool to download entire GitBook doc sites and split them into LLM-ready chunks — sharing it here because this community will actually use it**

### Body

You know the pain: you find great documentation for a framework, and you want your local LLM to understand it. But you need to feed it the docs first. And the docs are 600+ pages spread across a GitBook site.

I built a tool that:
1. Downloads every page from any GitBook site (BFS crawler, finds pages buried in sidebars)
2. Converts to clean markdown (strips nav bars, footers, cookie banners)
3. Splits into chunks aligned to markdown headers (never breaks mid-code-block)

**Real result:** 673 pages from docs.openalgo.in → 5 MB → 5 chunks. Works with Ollama, LM Studio, llama.cpp — any local setup.

```bash
pip install git+https://github.com/RohannShetty/gitbook-downloader.git
gitbook-dl download https://docs.example.com/
gitbook-dl split downloaded_docs.md -s 1.0
```

There's also a Windows .exe if you prefer GUIs.

**Repo:** https://github.com/RohannShetty/gitbook-downloader

Question for this community: what chunk sizes do you find work best for your local models? I default to 1 MB but curious what others use.

---

## 📝 REDDIT — r/Python

### Title
**I built a Python tool to download entire GitBook doc sites as clean markdown — sharing the code and architecture**

### Body

Built a Python CLI + GUI tool that downloads complete GitBook documentation sites and splits them into markdown chunks optimized for LLM context windows.

**Architecture:**
- BFS crawler for page discovery
- ThreadPoolExecutor for parallel downloads (streaming pipeline)
- markdownify for HTML → markdown conversion
- customtkinter for the GUI (Stripe-themed)
- PyInstaller for single .exe distribution

**Key design decisions:**
- URL normalization to strip #fragments (saved 92% file size vs naive approach)
- Streaming pipeline: pages download as they're discovered
- Header-boundary splitter: never breaks mid-section

**Repo:** https://github.com/RohannShetty/gitbook-downloader

Would love code review and PRs — especially for supporting other doc platforms.

---

## 📝 REDDIT — r/programming

### Title
**GitBook Downloader: Download any GitBook docs site → AI-ready chunks (open source, MIT)**

### Body

https://github.com/RohannShetty/gitbook-downloader

Built this because I was tired of copy-pasting documentation into ChatGPT. It downloads entire GitBook sites as clean markdown and splits them into chunks that respect document structure.

673 pages of docs.openalgo.in → 5 MB → 5 chunks in 2 minutes. Desktop GUI or CLI. Single .exe for Windows.

---

## ✍️ DEV.TO — Long-Form Article

### Title
**How I Built a GitBook Downloader That Turned 673 Pages Into 5 AI-Ready Chunks**

### Tags
`python` `opensource` `ai` `tutorial` `productivity` `llm`

### Outline

**The 3-Hour Copy-Paste Nightmare**
- Building a trading bot, needed full API docs
- 673 pages of documentation
- Made it to page 40 before mental breakdown
- wget, curl, pandoc — all failed

**Why Existing Tools Don't Work**
- wget: downloads HTML with nav, footer, cookies — 90% junk
- curl: one page at a time
- pandoc: doesn't handle site structure
- None respect LLM context windows

**Building the Solution**
- BFS crawler: start at root, follow every link
- URL normalization: strip #fragments (saved 92% file size)
- Parallel downloads: ThreadPoolExecutor, streaming pipeline
- Clean markdown: strip nav/footer/sidebar/scripts
- Header-boundary splitter: never break mid-code-block

**The Architecture**
```python
# Simplified engine flow
Producer (discovery thread) → url_queue → Consumer pool (download threads)
                                          ↓
                                    OrderedDict[url] = (title, markdown)
                                          ↓
                                    Single .md file
                                          ↓
                                    Header-boundary splitter
                                          ↓
                                    AI-ready chunks
```

**The Stripe UI**
- Why I chose Stripe's design language
- Clean white, navy headings, purple accent
- Dashboard with download history

**Results**
- 673 pages → 5 MB → 5 chunks
- Old approach: 38 MB (92% duplicate from fragments)
- New approach: 18x more unique pages in 1/8th the size

**Try It**
```bash
pip install git+https://github.com/RohannShetty/gitbook-downloader.git
gitbook-dl download https://docs.example.com/
gitbook-dl split downloaded_docs.md
```

**What's Next**
- Docusaurus, ReadTheDocs, MkDocs support
- Web UI version
- Docker image

---

## 💼 LINKEDIN

### Post

🚀 **I open-sourced a tool that solves one of the most annoying problems in AI-assisted development.**

You know the drill: you find great documentation for an API or framework. You want ChatGPT or Claude to understand it. But the docs are 600+ pages across a GitBook site. You start copy-pasting. Page 40, you give up.

**I built GitBook Downloader to solve this.**

It downloads every page from any GitBook site, converts it to clean markdown, and splits it into chunks that respect document structure — ready for your LLM's context window.

**Real results from docs.openalgo.in:**
• 673 pages found
• 5.0 MB of clean markdown
• 5 perfect chunks
• 2 minutes end-to-end

**Why this matters:**
• AI tools are incredible — but they can't browse docs
• Context windows are limited — you need smart chunking
• Manual copy-paste doesn't scale — automation does

**For developers:** `pip install` + 2 commands.
**For everyone else:** Download the .exe, double-click, paste a URL.

MIT license. PRs welcome.

🔗 github.com/RohannShetty/gitbook-downloader

#OpenSource #AI #Python #Developer #Productivity #LLM

---

## 📊 ADDITIONAL PROMOTION CHANNELS

### TrendShift
- Submit at: https://trendshift.io
- Category: Developer Tools
- Tag: `gitbook-downloader`

### AlternativeTo
- Submit as alternative to: wget, HTTrack, SiteSucker
- Category: Documentation Tools
- URL: https://alternativeto.net

### Newsletter Pitches

**TLDR Newsletter** (tldr.tech)
- Subject: "Tool: Download any GitBook docs site for AI"
- One-liner: "GitBook Downloader turns 673-page doc sites into 5 clean markdown chunks — ready for ChatGPT, Claude, or local LLMs. Free, open source, MIT."

**Python Weekly**
- Submit via: https://www.pythonweekly.com/submit

**Changelog Weekly**
- Submit via: https://changelog.com/submit

### YouTube Shorts / TikTok
- 60-second demo: "How to feed 673 pages of docs to ChatGPT in 30 seconds"
- Show: URL paste → download progress → split → ChatGPT upload

### Discord Communities
- Post in: r/LocalLLaMA Discord, LangChain Discord, OpenAI Discord
- Format: "Hey everyone, built a free tool to download GitBook docs for LLM context..."

---

## 🏷️ Hashtag Strategy

**Primary:** #OpenSource #Python #AI #DeveloperTools
**Secondary:** #LLM #ChatGPT #Claude #Productivity #Documentation
**Platform-specific:** #ShowHN (HN), #BuildingInPublic (Twitter)

---

## 📈 Success Metrics

| Metric | Target (Week 1) |
|--------|----------------|
| GitHub stars | 100+ |
| Product Hunt upvotes | 50+ |
| HN points | 20+ |
| Total downloads | 500+ |
| Twitter impressions | 5K+ |

---

## 🔗 All Links

- **GitHub:** https://github.com/RohannShetty/gitbook-downloader
- **Download .exe:** https://github.com/RohannShetty/gitbook-downloader/releases/latest
- **Issues:** https://github.com/RohannShetty/gitbook-downloader/issues
- **Discussions:** https://github.com/RohannShetty/gitbook-downloader/discussions
