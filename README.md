<p align="center">
  <img src="https://img.shields.io/badge/version-3.2.0-blue?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="license">
  <img src="https://img.shields.io/badge/python-3.8%2B-steelblue?style=flat-square" alt="python">
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey?style=flat-square" alt="platform">
  <a href="https://github.com/RohannShetty/gitbook-downloader/releases"><img src="https://img.shields.io/badge/download-.exe-orange?style=flat-square" alt="download"></a>
</p>

<h1 align="center">⬡ GitBook Downloader</h1>

<p align="center">
  <strong>Download entire GitBook documentation sites → single markdown file → AI-ready chunks.</strong><br>
  Built for developers who feed docs to LLMs. Download the .exe and run — no Python required.
</p>

---

## ⚡ One-Click Download

> **No Python. No pip. No terminal.** Download the `.exe`, unzip, double-click.

| Platform | Download |
|----------|----------|
| 🪟 **Windows** | **[GitBook-Downloader-v3.2.0.zip](https://github.com/RohannShetty/gitbook-downloader/releases/latest)** (35 MB) |

```text
1. Download GitBook-Downloader-v3.2.0.zip
2. Unzip anywhere (Desktop, Documents, USB drive)
3. Double-click GitBook-Downloader.exe
4. Paste a GitBook URL → click Start
```

<p align="center"><em>That's it. The GUI handles everything — discovery, download, splitting.</em></p>

---

## 🖥️ What It Looks Like

Modern sidebar design with three views:

| 📥 **Download** | ✂️ **Splitter** | ⚙️ **Settings** |
|---|---|---|
| Paste URL → Start | Pick a .md file → Split | About + version info |
| Live stats + progress | Choose chunk size (MB) | |
| Activity log | See all chunk files | |

---

## 🚀 What It Does

```
┌─────────────────────────────────────────────────────┐
│              🌐 GitBook Site (any URL)               │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│         🔍 BFS Discovery (find every page)           │
│         📥 Parallel Download (5 workers, fast)       │
│         🧹 Clean Markdown (strip nav/footer)         │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
              📄 Single .md file
          (title + source URL + content)
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│      ✂️ Header-Boundary Splitter (1 MB chunks)      │
│      Never breaks mid-section or mid-code-block     │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
              🧩 AI-ready chunks
        (doc_part_01.md … doc_part_NN.md)
```

---

## 🎯 Use Cases

- **Feed docs to ChatGPT / Claude** — download, split, upload as knowledge
- **Local RAG pipelines** — index chunks in your vector database
- **Offline archives** — single searchable .md file
- **Fine-tuning datasets** — clean, sectioned training data

---

## 🛠️ For Developers (CLI + pip)

Prefer the terminal?

```bash
# Install
pip install git+https://github.com/RohannShetty/gitbook-downloader.git

# Download
gitbook-dl download https://docs.example.com/ -p 500 -w 5

# Split
gitbook-dl split downloaded_docs.md -s 1.0

# Or launch the GUI
gitbook-dl gui
```

---

## 📦 Project Structure

```
gitbook-downloader/
├── src/gitbook_downloader/
│   ├── engine.py          # BFS discovery + parallel downloads
│   ├── splitter.py        # Header-boundary chunking
│   ├── dashboard.py       # Modern GUI (customtkinter)
│   └── cli.py             # Terminal interface
├── .github/workflows/     # Auto-build .exe on release
├── build_exe.py           # Local PyInstaller build
├── LAUNCH_KIT.md          # Product Hunt, HN, Reddit copy
└── README.md
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome — especially:
- macOS / Linux support
- Docusaurus / ReadTheDocs support
- Custom headers/cookies for private sites

---

## 📄 License

MIT © [Rohan Shetty](https://github.com/RohannShetty)

---

<p align="center">
  <sub>⭐ Star the repo if this helps you feed docs to your LLM!</sub>
</p>
