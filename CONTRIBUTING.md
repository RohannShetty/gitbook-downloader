# Contributing to GitBook Downloader

First off — thank you for considering contributing! This project exists to help developers feed documentation to LLMs more efficiently. Every improvement helps.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Pull Request Process](#pull-request-process)
- [Style Guide](#style-guide)
- [Testing](#testing)

---

## Code of Conduct

Be respectful. Be constructive. Assume good intent. This is a small project — let's keep it friendly.

---

## How Can I Contribute?

### 🐛 Report a Bug

1. **Check existing issues** — someone might have already reported it
2. **Use the bug report template** — include:
   - Your OS and Python version
   - The GitBook URL you tried to download
   - The exact command you ran
   - What you expected to happen
   - What actually happened (include error messages)
   - Any relevant log output

### 💡 Suggest a Feature

1. **Check existing discussions** — the idea might already be there
2. **Open a Discussion** (not an Issue) for feature requests
3. **Describe the use case** — what problem does this solve? how would you use it?

### 🔧 Contribute Code

Great! Here's how to get started:

---

## Development Setup

```bash
# 1. Fork & clone
git clone https://github.com/YOUR_USERNAME/gitbook-downloader.git
cd gitbook-downloader

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install in dev mode with all extras
pip install -e ".[all]"

# 4. Verify it works
gitbook-dl --version
```

---

## Project Structure

```
gitbook-downloader/
├── src/gitbook_downloader/
│   ├── __init__.py        # Package version + metadata
│   ├── __main__.py        # python -m entry point
│   ├── engine.py          # SmartEngine: discovery + download (core logic)
│   ├── splitter.py        # Markdown splitter (size + token-aware)
│   ├── cli.py             # CLI: argparse with download/split/gui subcommands
│   └── dashboard.py       # GUI: customtkinter dark-themed dashboard
├── pyproject.toml         # Package configuration
├── requirements.txt       # Plain pip dependencies
└── README.md
```

### Key modules

| Module | What it does | Dependencies |
|--------|--------------|--------------|
| `engine.py` | Two-phase download engine (discover → download) | requests, bs4, markdownify |
| `splitter.py` | Splits markdown by headers, size, or token count | tiktoken (optional) |
| `cli.py` | CLI entry point with subcommands | engine, splitter |
| `dashboard.py` | GUI with live stats and activity log | customtkinter, engine, splitter |

---

## Pull Request Process

1. **Create a branch** — `feature/your-feature` or `fix/your-bugfix`
2. **Keep changes focused** — one PR = one feature/fix
3. **Write clear commit messages** — explain *what* and *why*
4. **Test your changes** — run the CLI and GUI (if applicable)
5. **Update documentation** — if you add a feature, add it to the README
6. **Open the PR** — describe what you changed and why

### PR Title Convention

```
<type>: <short description>

Examples:
  feat: add PDF output option
  fix: handle 403 errors gracefully
  docs: add Docker usage guide
  refactor: extract URL normalizer
```

---

## Style Guide

- **Python**: Follow [PEP 8](https://peps.python.org/pep-0008/)
- **Docstrings**: Google-style (see existing code)
- **Imports**: Standard library → third-party → local (separated by blank lines)
- **Naming**: `snake_case` for variables/functions, `PascalCase` for classes
- **Line length**: 100 characters (not strict, but reasonable)
- **Type hints**: Use them for public functions (`def split_file(input_path: str, ...) -> list:`)

### Before committing

```bash
# Check for obvious issues
python -m py_compile src/gitbook_downloader/*.py

# Run the CLI to verify it loads
python -m gitbook_downloader --help
```

---

## Testing

Currently, testing is manual. Here's how to verify your changes:

### Engine tests

```bash
# Test with a small known site
gitbook-dl download https://docs.example.com/ -p 10 -w 2 -o test_output.md

# Check the output
head -100 test_output.md
```

### Splitter tests

```bash
# Create a test file
echo -e "# Header 1\n\nContent here\n\n## Subheader\n\nMore content" > test.md

# Test splitting
gitbook-dl split test.md -s 0.001
```

### GUI tests

```bash
gitbook-dl gui
# Verify: tabs switch, buttons work, log scrolls, stats update
```

---

## Feature Ideas

These are up for grabs — pick one and open a PR!

| Difficulty | Idea |
|------------|------|
| 🟢 Easy | Add `--dry-run` flag (discover only, no download) |
| 🟢 Easy | Add `--quiet` flag to suppress all output |
| 🟢 Easy | Support `GITBOOK_URL` environment variable |
| 🟡 Medium | Resume interrupted downloads (skip already-downloaded pages) |
| 🟡 Medium | Custom User-Agent or headers support |
| 🟡 Medium | Download images + embed as base64 |
| 🟡 Medium | JSON output format option |
| 🔴 Hard | Support for Docusaurus / ReadTheDocs / MkDocs |
| 🔴 Hard | Docker image with cron for scheduled downloads |
| 🔴 Hard | Web UI with Flask/FastAPI |

---

## Questions?

Open a [Discussion](https://github.com/RohannShetty/gitbook-downloader/discussions) or [Issue](https://github.com/RohannShetty/gitbook-downloader/issues).

Happy contributing! 🚀
