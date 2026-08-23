#!/usr/bin/env python3
"""
Automated Release Notes & Cryptographic Checksum Generator for DocHarvest / GitBook Downloader.

Features:
1. Parses `CHANGELOG.md` for target release tag and extracts overview + categorized changes.
2. Falls back to conventional git commits if tag is not yet in `CHANGELOG.md`.
3. Partitions updates into 4 canonical sections:
   - ✨ Features & Capabilities
   - 🐛 Bug Fixes & Hardening
   - ⚡ Performance & Architecture
   - 📦 Downloadable Binaries & Verification Checksums
4. Computes SHA-256 hashes for all staged release binaries and writes SHA256SUMS.txt.
5. Generates markdown verification table with file sizes and OS platforms.
6. Emits a clean, non-duplicated comparison link footer.
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def get_previous_tag(current_tag: str) -> Optional[str]:
    """Find the tag immediately preceding current_tag in git history."""
    try:
        cmd = ["git", "describe", "--tags", "--abbrev=0", f"{current_tag}^"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        tag = res.stdout.strip()
        if tag:
            return tag
    except Exception:
        pass

    try:
        cmd = ["git", "tag", "--sort=-creatordate"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        tags = [t.strip() for t in res.stdout.strip().splitlines() if t.strip()]
        if current_tag in tags:
            idx = tags.index(current_tag)
            if idx + 1 < len(tags):
                return tags[idx + 1]
        elif tags:
            for t in tags:
                if t != current_tag:
                    return t
    except Exception:
        pass

    return None


def extract_changelog_section(changelog_path: Path, tag: str) -> Optional[str]:
    """
    Extract the raw section for the given version tag from CHANGELOG.md.
    Supports formats:
      - ## [9.0.1] - 2026-08-23
      - ## 9.0.1
      - ## [v9.0.1] - 2026-08-23
      - ## v9.0.1
      - ## [9.0.0-beta.1] - 2026-08-23
    Returns raw section text (excluding the ## version line), or None if tag not found.
    """
    if not changelog_path.is_file():
        return None

    content = changelog_path.read_text(encoding="utf-8")
    clean_ver = tag.lstrip("v")

    lines = content.splitlines()
    in_section = False
    section_lines: List[str] = []

    tag_pattern = re.compile(
        rf"^##\s+\[?v?{re.escape(clean_ver)}\]?(?:\s+-\s+|\s+|$|\b)",
        re.IGNORECASE,
    )
    next_header_pattern = re.compile(r"^##\s+(?!#)")

    for line in lines:
        if not in_section:
            if tag_pattern.match(line.strip()):
                in_section = True
            continue
        else:
            if next_header_pattern.match(line.strip()):
                break
            section_lines.append(line)

    if not in_section:
        return None

    return "\n".join(section_lines).strip()


def parse_and_categorize_changelog(raw_section: str) -> Dict[str, List[str]]:
    """
    Categorizes raw changelog content into:
    - summary: list of summary lines/paragraphs
    - features: ✨ Features & Capabilities
    - fixes: 🐛 Bug Fixes & Hardening
    - performance: ⚡ Performance & Architecture
    """
    categories: Dict[str, List[str]] = {
        "summary": [],
        "features": [],
        "fixes": [],
        "performance": [],
    }

    lines = raw_section.splitlines()
    current_cat: Optional[str] = None
    current_bullet_lines: List[str] = []

    def classify_by_keywords(text: str) -> Optional[str]:
        # Check first line (title/header line of bullet) first
        text_lines = text.strip().splitlines()
        first_line = text_lines[0].lower() if text_lines else ""

        # High-confidence emoji / prefix check on first line
        if any(k in first_line for k in ["🔒", "🛡️", "🐛", "🔌", "⚠️", "🚨", "fix:", "fix(", "bug:", "[fix]"]):
            return "fixes"
        if any(k in first_line for k in ["⚡", "🚀", "⚙️", "🏗️", "perf:", "perf(", "refactor:", "refactor(", "[perf]"]):
            return "performance"
        if any(k in first_line for k in ["🎨", "✨", "🧭", "📦", "📁", "🔍", "💎", "feat:", "feat(", "add:", "[feat]"]):
            return "features"

        # Keyword check on first line
        if any(k in first_line for k in ["fix", "bug", "harden", "security", "dead-process", "crash", "timeout", "lock"]):
            return "fixes"
        if any(k in first_line for k in ["perf", "speed", "concurr", "thread", "zombie", "async", "latency", "scale", "optim", "refactor"]):
            return "performance"
        if any(k in first_line for k in ["feat", "add", "new", "improv", "ui", "view", "palette", "export", "reader", "rag", "pdf", "studio", "support"]):
            return "features"

        # Whole-text fallback
        text_lower = text.lower()
        if any(k in text_lower for k in ["🔒", "🛡️", "🐛", "🔌", "fix:", "bug:", "dead-process", "crash"]):
            return "fixes"
        if any(k in text_lower for k in ["⚡", "🚀", "perf:", "thread", "zombie", "latency"]):
            return "performance"
        if any(k in text_lower for k in ["🎨", "✨", "🧭", "📦", "📁", "🔍", "feat:", "reader", "rag", "pdf"]):
            return "features"

        return None

    def flush_bullet(header_cat: Optional[str], bullet_lines: List[str]):
        if not bullet_lines:
            return
        entry = "\n".join(bullet_lines).rstrip()
        bullet_cat = classify_by_keywords(entry)
        target_cat = bullet_cat or header_cat or "features"
        categories[target_cat].append(entry)

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("---") or stripped.startswith("***"):
            continue

        # Subheading match: ### Added, ### Fixed, ### Changed, etc.
        if stripped.startswith("###"):
            flush_bullet(current_cat, current_bullet_lines)
            current_bullet_lines = []
            header_lower = stripped.lower()

            if any(k in header_lower for k in ["fix", "bug", "harden", "security", "lock", "safety"]):
                current_cat = "fixes"
            elif any(k in header_lower for k in ["perf", "speed", "architect", "change", "refactor", "engine", "scale"]):
                current_cat = "performance"
            elif any(k in header_lower for k in ["add", "feat", "improv", "ui", "rag", "pdf", "export", "studio", "new"]):
                current_cat = "features"
            else:
                clean_header = stripped.lstrip("#").strip()
                categories["summary"].append(f"**{clean_header}**")
                current_cat = None
            continue

        # Check if line is a top-level bullet (starts with `- ` or `* `, not indented)
        is_top_level_bullet = (
            (line.startswith(("- ", "* "))) or
            (not line.startswith(("  ", "\t")) and stripped.startswith(("- ", "* ")))
        )

        if is_top_level_bullet:
            flush_bullet(current_cat, current_bullet_lines)
            current_bullet_lines = [stripped]
        elif current_bullet_lines:
            current_bullet_lines.append(line)
        else:
            categories["summary"].append(stripped)

    flush_bullet(current_cat, current_bullet_lines)
    return categories


def parse_commits_fallback(current_tag: str, prev_tag: Optional[str]) -> Dict[str, List[str]]:
    """Parse git commits between prev_tag and current_tag when changelog entry is missing."""
    categories: Dict[str, List[str]] = {
        "summary": [f"Release updates and binary builds for {current_tag}."],
        "features": [],
        "fixes": [],
        "performance": [],
    }

    rev_range = f"{prev_tag}..{current_tag}" if prev_tag else current_tag
    try:
        cmd = ["git", "log", rev_range, "--pretty=format:%s (%h)"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        commits = [c.strip() for c in res.stdout.strip().splitlines() if c.strip()]
    except Exception:
        commits = []

    for c in commits:
        c_lower = c.lower()
        if c_lower.startswith(("feat", "feat:", "feat(")):
            categories["features"].append(f"- {c}")
        elif c_lower.startswith(("fix", "fix:", "fix(", "security", "harden")):
            categories["fixes"].append(f"- {c}")
        elif c_lower.startswith(("perf", "perf:", "perf(", "refactor", "refactor:", "refactor(", "build", "ci")):
            categories["performance"].append(f"- {c}")
        else:
            if any(k in c_lower for k in ["fix", "bug", "harden", "lock", "crash"]):
                categories["fixes"].append(f"- {c}")
            elif any(k in c_lower for k in ["perf", "speed", "async", "optim", "refactor"]):
                categories["performance"].append(f"- {c}")
            elif any(k in c_lower for k in ["feat", "add", "ui", "rag", "pdf", "export"]):
                categories["features"].append(f"- {c}")
            else:
                categories["performance"].append(f"- {c}")

    return categories


def process_artifacts(
    artifacts_dir: Optional[Path],
    write_manifest: bool = True
) -> Tuple[str, List[Tuple[str, str, str, str]]]:
    """
    Computes SHA-256 for all artifacts in artifacts_dir.
    Returns (sha256sums_manifest_content, list_of_table_rows)
    Row: (filename, platform, size_str, sha256_hash)
    """
    if not artifacts_dir or not artifacts_dir.is_dir():
        return "", []

    entries = sorted(artifacts_dir.iterdir(), key=lambda p: p.name)
    table_rows: List[Tuple[str, str, str, str]] = []
    manifest_lines: List[str] = []

    for p in entries:
        if not p.is_file() or p.name == "SHA256SUMS.txt":
            continue

        data = p.read_bytes()
        sha256 = hashlib.sha256(data).hexdigest()
        size_bytes = len(data)
        if size_bytes >= 1024 * 1024:
            size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{max(size_bytes / 1024, 0.1):.1f} KB"

        # Detect platform
        name = p.name.lower()
        if "windows" in name or name.endswith(".exe"):
            platform = "Windows x64"
        elif "ubuntu" in name or "linux" in name:
            platform = "Linux x64"
        elif "macos" in name or "darwin" in name:
            platform = "macOS (Apple Silicon / Intel)"
        else:
            platform = "Universal / Cross-Platform"

        table_rows.append((p.name, platform, size_str, sha256))
        manifest_lines.append(f"{sha256}  {p.name}")

    manifest_content = "\n".join(manifest_lines) + "\n" if manifest_lines else ""
    if write_manifest and manifest_content:
        manifest_file = artifacts_dir / "SHA256SUMS.txt"
        manifest_file.write_text(manifest_content, encoding="utf-8")
        table_rows.append(("SHA256SUMS.txt", "All Platforms", "< 1 KB", "*(Verification Manifest)*"))

    return manifest_content, table_rows


def build_release_markdown(
    tag: str,
    categories: Dict[str, List[str]],
    table_rows: List[Tuple[str, str, str, str]],
    prev_tag: Optional[str],
    repo: str,
) -> str:
    """Renders the final Release Notes Markdown document."""
    out: List[str] = []
    clean_ver = tag.lstrip("v")
    out.append(f"# DocHarvest v{clean_ver}\n")

    if categories.get("summary"):
        summary_text = "\n\n".join(categories["summary"]).strip()
        if summary_text:
            out.append(f"{summary_text}\n")

    # 1. ✨ Features & Capabilities
    if categories.get("features"):
        out.append("### ✨ Features & Capabilities\n")
        for item in categories["features"]:
            out.append(f"{item}\n")
        out.append("")

    # 2. 🐛 Bug Fixes & Hardening
    if categories.get("fixes"):
        out.append("### 🐛 Bug Fixes & Hardening\n")
        for item in categories["fixes"]:
            out.append(f"{item}\n")
        out.append("")

    # 3. ⚡ Performance & Architecture
    if categories.get("performance"):
        out.append("### ⚡ Performance & Architecture\n")
        for item in categories["performance"]:
            out.append(f"{item}\n")
        out.append("")

    # 4. 📦 Downloadable Binaries & Verification Checksums
    if table_rows:
        out.append("### 📦 Downloadable Binaries & Verification Checksums\n")
        out.append("| Asset / Executable | Target Platform | File Size | SHA-256 Checksum |")
        out.append("| :--- | :--- | :--- | :--- |")
        for fname, plat, size, sha in table_rows:
            if sha.startswith("*"):
                out.append(f"| `{fname}` | {plat} | {size} | {sha} |")
            else:
                out.append(f"| `{fname}` | {plat} | {size} | `{sha}` |")
        out.append("")
        out.append("#### Verification Instructions")
        out.append("```bash")
        out.append("# Linux / macOS integrity verification:")
        out.append("sha256sum -c SHA256SUMS.txt\n")
        out.append("# Windows PowerShell integrity verification:")
        out.append("Get-FileHash -Algorithm SHA256 gitbook-dl-windows-latest.exe")
        out.append("```\n")

    # Comparison Footer
    out.append("---")
    if prev_tag:
        out.append(f"**Full Changelog**: https://github.com/{repo}/compare/{prev_tag}...{tag}")
    else:
        out.append(f"**Release Commits**: https://github.com/{repo}/commits/{tag}")

    return "\n".join(out).strip() + "\n"


def generate_notes(
    tag: str,
    changelog_path: Optional[Path] = None,
    artifacts_dir: Optional[Path] = None,
    repo: str = "RohannShetty/gitbook-downloader",
    write_checksums: bool = True,
) -> str:
    """Core functional entry point to generate release notes string."""
    raw_section = None
    if changelog_path and changelog_path.is_file():
        raw_section = extract_changelog_section(changelog_path, tag)

    prev_tag = get_previous_tag(tag)

    if raw_section:
        categories = parse_and_categorize_changelog(raw_section)
    else:
        categories = parse_commits_fallback(tag, prev_tag)

    _, table_rows = process_artifacts(artifacts_dir, write_manifest=write_checksums)

    return build_release_markdown(
        tag=tag,
        categories=categories,
        table_rows=table_rows,
        prev_tag=prev_tag,
        repo=repo,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate rich categorized release notes for DocHarvest.")
    parser.add_argument("--tag", required=True, help="Release tag (e.g. v9.0.1)")
    parser.add_argument(
        "--changelog", "--changelog-path",
        dest="changelog",
        default="CHANGELOG.md",
        help="Path to CHANGELOG.md",
    )
    parser.add_argument("--artifacts-dir", default=None, help="Directory with staged release binaries")
    parser.add_argument("--repo", default="RohannShetty/gitbook-downloader", help="GitHub repository (owner/name)")
    parser.add_argument("--output", default="RELEASE_NOTES.md", help="Output file path")
    parser.add_argument("--write-checksums", action="store_true", default=True, help="Generate SHA256SUMS.txt in artifacts dir")
    args = parser.parse_args()

    changelog_path = Path(args.changelog) if args.changelog else Path("CHANGELOG.md")
    artifacts_dir = Path(args.artifacts_dir) if args.artifacts_dir else None

    notes = generate_notes(
        tag=args.tag,
        changelog_path=changelog_path,
        artifacts_dir=artifacts_dir,
        repo=args.repo,
        write_checksums=args.write_checksums,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(notes, encoding="utf-8")
    print(f"Successfully generated release notes at: {out_path.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
