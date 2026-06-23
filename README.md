<p align="center">
  <img src="https://img.shields.io/badge/version-4.0.0-533afd?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-15be53?style=flat-square" alt="license">
  <img src="https://img.shields.io/badge/python-3.8+-273951?style=flat-square" alt="python">
  <img src="https://img.shields.io/badge/download-.exe-533afd?style=flat-square" alt="download">
  <img src="https://img.shields.io/badge/stars-⭐⭐⭐⭐⭐-f59e0b?style=flat-square" alt="stars">
</p>

<h1 align="center">⬡ GitBook Downloader</h1>

<p align="center">
  <strong>Download any GitBook documentation site. Split it into AI-ready chunks. Feed your LLM.</strong><br>
  <em>673 pages of docs.openalgo.in → 5 MB of clean markdown → 5 perfect chunks. In 2 minutes.</em>
</p>

---

## 📖 The Story

I was building a trading bot using [OpenAlgo](https://docs.openalgo.in/). Their documentation is excellent — 673 pages covering every API endpoint, every SDK method, every configuration option. I needed all of it inside ChatGPT's context window.

**The problem:** ChatGPT can't browse 673 pages. And copy-pasting 673 pages one-by-one would take hours.

I tried `wget`. It downloaded HTML garbage — navigation bars, sidebars, footers, cookie banners — completely useless for an LLM.

I tried `curl | pandoc`. Same problem. 90% of what it captured wasn't documentation — it was UI chrome.

So I built a tool that does exactly what I needed:

```
1. Find every page on the site (even the ones buried in submenus)
2. Download just the content — clean markdown, no navigation junk
3. Split it into chunks that fit inside an LLM's context window
4. Never cut a sentence in half. Never break a code block.
```

**The result:** 673 pages → 5 MB → 5 chunks. Uploaded to ChatGPT in 30 seconds. My trading bot was built that afternoon.

This tool is for everyone who's ever thought *"I wish I could just feed this entire documentation site to my AI."*

---

## ⚡ One Click. No Python. No Terminal.

<p align="center">
  <a href="https://github.com/RohannShetty/gitbook-downloader/releases/latest">
    <img src="https://img.shields.io/badge/⬇%20Download%20.exe-Windows-533afd?style=for-the-badge&logo=windows&logoColor=white" alt="Download">
  </a>
</p>

```text
1. Download GitBook-Downloader.exe
2. Double-click
3. Paste a GitBook URL → Start
4. Click "Split" for AI-ready chunks
```

**That's it.** The app handles everything — finding every page, downloading in parallel, converting to clean markdown, and splitting into chunks that respect headings and code blocks.

---

## 🎯 Who Is This For?

| You are... | You need to... | This tool... |
|---|---|---|
| 🤖 **AI Developer** | Feed docs to ChatGPT, Claude, Gemini | Downloads the entire site, splits into context-sized chunks |
| 🔍 **RAG Builder** | Index documentation in a vector database | Produces clean, sectioned markdown ready for embedding |
| 📚 **Researcher** | Read docs offline during commutes/flights | Single searchable `.md` file — no internet needed |
| 🛠️ **Open Source Dev** | Understand a project's full API surface | Downloads every endpoint doc in one pass |
| 🎓 **Student** | Study a framework's documentation | Offline reference that fits in your notes app |
| 🏢 **Enterprise Dev** | Work behind a firewall with limited internet | Download once, reference forever |

---

## 🚀 What Makes It Different

| | `wget` | `curl \| pandoc` | **GitBook Downloader** |
|---|---|---|---|
| Finds all pages | ❌ Only linked | ❌ Single page | ✅ BFS crawler — every page |
| Clean markdown | ❌ Full HTML | ⚠️ Messy | ✅ Strips nav/footer/sidebar |
| Header-boundary split | ❌ | ❌ | ✅ Never breaks mid-section |
| Fragment dedup | ❌ Downloads #anchors | ❌ | ✅ Strips #fragments |
| Parallel downloads | ❌ Sequential | ❌ | ✅ 5x faster |
| Streaming pipeline | ❌ | ❌ | ✅ Download as you discover |
| Incremental updates | ❌ | ❌ | ✅ Only fetch new pages |
| Desktop GUI | ❌ | ❌ | ✅ One-click .exe |

---

## 📊 Real-World Result

```
                    docs.openalgo.in
                    ────────────────
                          │
                    ┌─────▼─────┐
                    │  BFS Crawl │  Finds 673 pages
                    │  5 workers │  in parallel
                    └─────┬─────┘
                          │
                    ┌─────▼─────┐
                    │  Markdown  │  5.0 MB clean
                    │  Convert   │  138,000 lines
                    └─────┬─────┘
                          │
                    ┌─────▼─────┐
                    │  Splitter  │  5 chunks
                    │  1 MB each │  Header-aligned
                    └─────┬─────┘
                          │
                    ┌─────▼─────┐
                    │  Upload to │  30 seconds
                    │  ChatGPT   │  Full context
                    └───────────┘
```

---

## 🖥️ The App

<p align="center"><em>Stripe-inspired design — clean white surface, navy headings, purple accent. Dashboard with download history, one-click updates, and auto-split.</em></p>

**Three views, zero clutter:**

| 📥 Download | 🔄 Update | ✂️ Split |
|---|---|---|
| Paste URL → Start | Click on any past download | Pick file → choose chunk size |
| Live streaming progress | Only new pages fetched | Results in seconds |
| "Split into chunks" prompt | Appended to existing file | 5 clean, header-aligned files |

---

## 🛠️ For Developers

```bash
# Install
pip install git+https://github.com/RohannShetty/gitbook-downloader.git

# Download an entire site
gitbook-dl download https://docs.example.com/

# Update a previous download (only new pages)
gitbook-dl download https://docs.example.com/ -o existing_docs.md --update

# Split into 1 MB chunks
gitbook-dl split downloaded_docs.md -s 1.0

# Launch the GUI
gitbook-dl gui
```

---

## 🧩 Use Cases That Actually Matter

### 1. "I need to build with this API but don't want to keep 20 browser tabs open"

```bash
gitbook-dl download https://docs.stripe.com/api -o stripe_api.md
# → 1 file. Searchable. No tabs.
```

### 2. "My LLM keeps hallucinating API parameters"

```bash
gitbook-dl download https://docs.langchain.com/ -o lc_docs.md
gitbook-dl split lc_docs.md -s 1.0
# → Upload chunks as knowledge files. Zero hallucinations.
```

### 3. "I'm on a 12-hour flight and need to study this framework"

```bash
gitbook-dl download https://docs.astral.sh/uv/ -o uv_docs.md
# → Offline. Searchable. Battery-friendly.
```

### 4. "I want to fine-tune a model on this project's documentation"

```bash
gitbook-dl download https://docs.example.com/ -o training_data.md
gitbook-dl split training_data.md -s 0.5
# → 0.5 MB chunks. Perfect for fine-tuning.
```

### 5. "The docs updated last week — I need the new content only"

```bash
gitbook-dl download https://docs.example.com/ -o existing.md
# → Only 12 new pages downloaded. Appended to your file.
```

---

## 📦 Project Structure

```
gitbook-downloader/
├── src/gitbook_downloader/
│   ├── engine.py          # Streaming BFS + parallel downloads
│   ├── splitter.py        # Header-boundary chunking
│   ├── dashboard.py       # Stripe-themed GUI
│   └── cli.py             # Terminal interface
├── .github/workflows/     # Auto-build .exe on release
├── LAUNCH_KIT.md          # Social media launch plan
└── README.md              # You are here
```

---

## 🤝 Contributing

This tool was born from frustration. If you've ever copy-pasted docs into ChatGPT one page at a time, you get it.

**Ways to help:**
- 🐛 Found a bug? [Open an issue](https://github.com/RohannShetty/gitbook-downloader/issues)
- 💡 Have an idea? [Start a discussion](https://github.com/RohannShetty/gitbook-downloader/discussions)
- 🔧 Want to code? Pick from [open issues](https://github.com/RohannShetty/gitbook-downloader/issues)
- ⭐ Star the repo — it helps others discover the tool

---

## 📄 License

MIT © [Rohan Shetty](https://github.com/RohannShetty)

---

<p align="center">
  <sub>Built with frustration. Shared with love. ⬡</sub>
</p>
