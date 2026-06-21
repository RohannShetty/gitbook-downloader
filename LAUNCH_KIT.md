# 🚀 Launch Kit — GitBook Downloader v3.1

> Copy-paste ready submissions for every platform. One post per platform.

---

## 📊 Product Hunt

### Tagline (60 chars)
**Download any GitBook docs → split into AI-friendly chunks**

### Description (260 chars)
Download entire GitBook documentation sites as a single markdown file, then split into token-aware chunks for LLMs (ChatGPT, Claude, Gemini). Two-phase engine (sitemap + sidebar discovery → parallel downloads with retries). Ships with a beautiful dark GUI.

### Topics
`Developer Tools` `Open Source` `GitHub` `AI` `Productivity`

### First Comment (post immediately after launch)

Hey makers 👋

I built this because I kept needing to feed documentation into ChatGPT/Claude but hit the context window limit every time. Manually copying pages one by one was painful.

**What it does:**
1. **Downloads** an entire GitBook site into one .md file (finds every page via sitemap + sidebar crawling)
2. **Splits** that file into chunks — but intelligently: respects header boundaries AND counts actual tokens (using tiktoken — same encoding as GPT-4/Claude)

**Why it's different from wget/curl:**
- GitBook-specific: knows how to find ALL pages (sitemap indexes, sidebar `<nav>` trees)
- Retry logic: handles rate limits, 429s, connection failures
- AI-aware splitting: never cuts mid-paragraph, counts tokens not bytes
- Beautiful GUI: if you prefer clicking over typing

**Stack:** Python 3.8+, requests + BeautifulSoup + customtkinter. MIT license.

Would love feedback — especially from people who use docs for RAG or fine-tuning! What other doc platforms should I support next? (Docusaurus? ReadTheDocs?)

### Images to upload
1. `assets/social-preview.html` — open in browser, fullscreen, screenshot → main thumbnail
2. Terminal screenshot showing `gitbook-dl download` + progress
3. GUI screenshot showing the dark dashboard with live stats

### Launch checklist
- [ ] Claim `gitbook-downloader` on Product Hunt (or use GitHub OAuth)
- [ ] Upload 3+ images
- [ ] Set launch time: **Tuesday/Wednesday/Thursday 12:01 AM PST** (best for dev tools)
- [ ] First comment ready to paste
- [ ] Share PH link on Twitter/Reddit to drive upvotes

---

## 🔗 Hacker News — Show HN

### Title
**Show HN: GitBook Downloader — download any GitBook docs and split into AI-ready chunks**

### Body

I built a Python tool that downloads entire GitBook documentation sites and splits them into AI-friendly markdown chunks.

**The problem:** You find a great documentation site on GitBook. You want to feed it to ChatGPT/Claude for context. But the context window is limited, and manually copying pages one by one takes forever.

**What it does:**

```
# Download the entire site (finds EVERY page via sitemap + sidebar)
gitbook-dl download https://docs.example.com/

# Split into 8K-token chunks (uses GPT-4/Claude tokenizer)
gitbook-dl split downloaded_docs.md --max-tokens 8000
```

**How it works:**
- Phase 1: Recursive sitemap parsing + `<nav>` sidebar crawling — finds pages sitemaps miss
- Phase 2: Parallel downloads (configurable workers), retries with exponential backoff, rate-limit handling
- Splitter: Header-boundary-aware (never cuts mid-section), token-counting via tiktoken

It also has a desktop GUI (Linear-inspired dark theme) with live stats — discovered, downloaded, failed, elapsed.

**Stack:** Python, requests, BeautifulSoup, customtkinter. MIT license.

**Repo:** [github.com/RohannShetty/gitbook-downloader](https://github.com/RohannShetty/gitbook-downloader)

Would love feedback on what other documentation platforms to support. Docusaurus? ReadTheDocs?

---

## 🧵 Twitter/X — Thread

### Tweet 1 (main)
```text
I got tired of manually copying GitBook pages into ChatGPT.

So I built a tool that downloads the ENTIRE site + splits it into AI-friendly chunks.

One command:
$ gitbook-dl download https://docs.example.com/
$ gitbook-dl split docs.md --max-tokens 8000

MIT license. 🚀
```

### Tweet 2 (image + features)
```text
What it does:
🔍 Finds ALL pages (sitemaps + sidebar crawling)
📥 Parallel downloads with retries
✂️ Token-aware splitting (GPT-4/Claude encoding)
🖥️ Beautiful dark GUI for clickers

pip install git+https://github.com/RohannShetty/gitbook-downloader.git
```

### Tweet 3 (use cases)
```text
Use it for:
• Feed docs to ChatGPT as knowledge files
• Build RAG pipelines (index chunks in vector DB)
• Create offline doc archives (searchable .md)
• Fine-tuning dataset prep

Pretty much: any time you need docs inside an LLM context window.
```

### Tweet 4 (tech + call to action)
```text
Technical:
→ Python 3.8+
→ Sitemap index recursion
→ Exponential backoff (1s→3s→8s)
→ HTTP 429 auto-handling
→ tiktoken for token counting
→ customtkinter GUI

Repo: github.com/RohannShetty/gitbook-downloader
Stars ★ appreciated!
```

---

## 📝 Dev.to / Hashnode — Article

### Title
**How I Built a GitBook Downloader That Splits Docs into AI-Friendly Chunks**

### Tags
`python` `opensource` `ai` `llm` `tutorial` `productivity`

### Body (outline)

**The Problem**
Feeding documentation to LLMs is painful. Context windows are small. Copy-paste is slow.

**The Solution**
A two-phase Python tool that downloads entire GitBook sites and splits into token-aware chunks.

**How It Works**
1. Discovery phase — sitemap XML recursion + `<nav>` sidebar crawling
2. Download phase — ThreadPoolExecutor, retries, rate limiting
3. Splitter — header boundaries + tiktoken encoding

**Code Deep Dive**
- SmartEngine class architecture
- Sitemap index handling
- Thread-safe session pooling
- Markdownify conversion pipeline

**Results**
- 330+ pages from openalgo.in in under 2 minutes
- Chunks respect markdown structure
- Token counts match GPT-4/Claude encoding

**Try It**
```bash
pip install git+https://github.com/RohannShetty/gitbook-downloader.git
gitbook-dl download https://docs.example.com/
gitbook-dl split downloaded_docs.md -t 8000
```

---

## 🗣️ Reddit — r/Python, r/LocalLLaMA, r/MachineLearning, r/programming

### r/Python + r/programming

**Title:** [Project] GitBook Downloader — download entire GitBook docs and split into AI-ready chunks

**Body:**

Built a Python CLI+GUI tool to solve a personal pain point: feeding documentation into LLMs without hitting context limits.

**What:** Downloads every page from a GitBook site → single .md file → splits into token-counted chunks

**How:**
- `gitbook-dl download <url>` — two-phase engine: sitemap discovery → parallel downloads
- `gitbook-dl split <file> --max-tokens 8000` — header-boundary aware + tiktoken counting
- `gitbook-dl gui` — full dark-themed dashboard with live stats

**Stack:** requests + BeautifulSoup + markdownify + customtkinter

**Why not wget?** GitBook-specific discovery (sitemap indexes, sidebar trees), retry logic, and AI-aware splitting that wget can't do.

[https://github.com/RohannShetty/gitbook-downloader](https://github.com/RohannShetty/gitbook-downloader)

---

### r/LocalLLaMA

**Title:** Tool to download GitBook docs + split into token-aware chunks for local LLMs

**Body:**

Made a tool that downloads entire GitBook documentation sites and splits them into chunks using tiktoken (GPT-4/Claude encoding) — perfect for feeding to local models via RAG or direct context.

```bash
gitbook-dl download https://docs.langchain.com/ -o lc_docs.md
gitbook-dl split lc_docs.md --max-tokens 4096  # or whatever your model supports
```

Features:
- Finds ALL pages (sitemap + sidebar crawl — catches things sitemaps miss)
- Parallel downloads with retries
- Chunks respect markdown headers (never breaks mid-section)
- Works offline once downloaded

[https://github.com/RohannShetty/gitbook-downloader](https://github.com/RohannShetty/gitbook-downloader)

---

### r/MachineLearning

**Title:** [P] GitBook Downloader — turn any documentation site into ML-ready token chunks

**Body:**

Built a tool for ML practitioners who need to feed documentation into LLMs — downloads entire GitBook sites and splits into token-counted chunks using the GPT-4/Claude tokenizer.

Use cases:
- Fine-tuning dataset preparation
- RAG pipeline ingestion
- Offline documentation archives
- Multi-shot prompt construction

MIT licensed, Python 3.8+, CLI + GUI.

---

## 🌐 Aggregator Submissions

### TrendShift
- **URL:** [trendshift.io](https://trendshift.io) — submit as new repository
- **Category:** Developer Tools / AI
- **Description:** Download complete GitBook documentation sites and split into AI-friendly markdown chunks. Token-aware splitting, parallel downloads, dark GUI.

### LibHunt
- **URL:** [python.libhunt.com](https://python.libhunt.com) — add via GitHub topics
- Already tagged with relevant topics — LibHunt auto-indexes

### AlternativeTo
- **URL:** [alternativeto.net](https://alternativeto.net) — submit as new software
- **Category:** Documentation Tools, Web Scraping
- **Alternatives to:** wget (for docs), HTTrack, DocDownloader

### awesome-python
- **Submit PR to:** [github.com/vinta/awesome-python](https://github.com/vinta/awesome-python)
- **Section:** "Documentation" or "Text Processing"
- **Entry:** `gitbook-downloader` — Download GitBook docs and split into AI-friendly chunks.

### awesome-llm
- **Submit PR to relevant awesome-llm list**
- **Section:** "Tools / Data Preparation"

---

## ⭐ Quick Actions You Can Take

| Platform | Action | Time |
|----------|--------|------|
| Product Hunt | Schedule launch for Tue-Thu | 5 min |
| Show HN | Post (best time: weekday morning PST) | 2 min |
| r/Python | Submit link post | 1 min |
| r/LocalLLaMA | Text post with use case | 2 min |
| r/programming | Link post | 1 min |
| Dev.to | Publish article | 20 min |
| Twitter | Post thread | 5 min |
| TrendShift | Submit repo | 2 min |
| awesome-python | Open PR | 5 min |

---

## 📸 Image Checklist

- [ ] Social preview card (open `assets/social-preview.html` → screenshot)
- [ ] Terminal screenshot: `gitbook-dl download` in action
- [ ] GUI screenshot: dark dashboard with live stats
- [ ] Split output: terminal showing chunks with token counts
- [ ] Logo: the ⬡ hexagon icon

---

## 🏷️ Hashtags

```
#OpenSource #Python #AI #LLM #ChatGPT #Claude #DeveloperTools
#Documentation #GitBook #RAG #MachineLearning #Productivity
```
