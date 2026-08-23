"""
Unit and integration tests for scripts/generate_release_notes.py.
Validates changelog parsing, categorization, SHA-256 checksum generation,
binary table rendering, commit fallbacks, and CLI behavior.
"""

import hashlib
import sys
from pathlib import Path
from unittest.mock import patch
import pytest

from scripts.generate_release_notes import (
    build_release_markdown,
    extract_changelog_section,
    generate_notes,
    get_previous_tag,
    main,
    parse_and_categorize_changelog,
    parse_commits_fallback,
    process_artifacts,
)


# ---------------------------------------------------------------------------
# 1. Changelog Section Extraction Tests
# ---------------------------------------------------------------------------


def test_extract_changelog_section_bracketed(tmp_path: Path):
    content = """# Changelog

## [9.0.1] - 2026-08-23

### Fixed
- Fixed critical domain lock race condition.

## [9.0.0] - 2026-08-20

### Added
- Initial release.
"""
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(content, encoding="utf-8")

    section = extract_changelog_section(changelog, "v9.0.1")
    assert section is not None
    assert "Fixed critical domain lock race condition." in section
    assert "Initial release." not in section


def test_extract_changelog_section_unbracketed(tmp_path: Path):
    content = """# Changelog

## 9.0.1 - 2026-08-23
Summary paragraph for 9.0.1.

- 🐛 Fix socket timeout.

## 8.0.0
Old version.
"""
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(content, encoding="utf-8")

    section = extract_changelog_section(changelog, "9.0.1")
    assert section is not None
    assert "Summary paragraph for 9.0.1." in section
    assert "Fix socket timeout." in section
    assert "Old version." not in section


def test_extract_changelog_section_with_v_prefix(tmp_path: Path):
    content = """# Changelog

## [v9.0.1] - 2026-08-23
- ✨ Feature A

## [v9.0.0]
- ✨ Feature B
"""
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(content, encoding="utf-8")

    section = extract_changelog_section(changelog, "v9.0.1")
    assert section is not None
    assert "Feature A" in section
    assert "Feature B" not in section


def test_extract_changelog_section_prerelease(tmp_path: Path):
    content = """# Changelog

## [9.0.0-beta.1] - 2026-08-23
- 🎨 Complete shadcn UI overhaul.

## [8.0.0] - 2026-08-20
- Legacy GUI.
"""
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(content, encoding="utf-8")

    section = extract_changelog_section(changelog, "v9.0.0-beta.1")
    assert section is not None
    assert "Complete shadcn UI overhaul." in section
    assert "Legacy GUI." not in section


def test_extract_changelog_section_not_found(tmp_path: Path):
    content = """# Changelog
## [1.0.0] - 2026-01-01
- First release.
"""
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(content, encoding="utf-8")

    assert extract_changelog_section(changelog, "v9.9.9") is None
    assert extract_changelog_section(tmp_path / "nonexistent.md", "v1.0.0") is None


# ---------------------------------------------------------------------------
# 2. Changelog Parsing & Categorization Tests
# ---------------------------------------------------------------------------


def test_parse_and_categorize_explicit_subheadings():
    raw_section = """Version overview summary paragraph.

### Added
- Native PDF export engine.
- Command palette navigation.

### Fixed
- Dead-process PID lock recovery.
- Memory leak on large sitemap crawl.

### Performance
- Zero-copy stream buffer.
- Async thread pool scaling.
"""
    categories = parse_and_categorize_changelog(raw_section)

    assert "Version overview summary paragraph." in categories["summary"]
    assert len(categories["features"]) == 2
    assert any("Native PDF export engine." in item for item in categories["features"])
    assert len(categories["fixes"]) == 2
    assert any("Dead-process PID lock recovery." in item for item in categories["fixes"])
    assert len(categories["performance"]) == 2
    assert any("Zero-copy stream buffer." in item for item in categories["performance"])


def test_parse_and_categorize_emoji_bullets():
    raw_section = """### 🚀 Release Overview Title

- 🔒 **Self-Recovering Domain Locks**: Reclaims dead locks.
- 🧭 **Intelligent Path-Scope**: Auto-bounds crawl for SPAs.
- ⚡ **Non-Blocking Cancellation**: Eliminates zombie threads.
- 🔌 **Socket Connection Timeouts**: Prevents hung handshakes.
- 🎨 **Premium Shadcn Desktop GUI**: Dark mode and motion.
"""
    categories = parse_and_categorize_changelog(raw_section)

    assert any("Release Overview Title" in s for s in categories["summary"])

    # 🔒 and 🔌 -> fixes
    assert len(categories["fixes"]) == 2
    assert any("Self-Recovering Domain Locks" in item for item in categories["fixes"])
    assert any("Socket Connection Timeouts" in item for item in categories["fixes"])

    # 🧭 and 🎨 -> features
    assert len(categories["features"]) == 2
    assert any("Intelligent Path-Scope" in item for item in categories["features"])
    assert any("Premium Shadcn Desktop GUI" in item for item in categories["features"])

    # ⚡ -> performance
    assert len(categories["performance"]) == 1
    assert any("Non-Blocking Cancellation" in item for item in categories["performance"])


def test_parse_and_categorize_multiline_and_indented_bullets():
    raw_section = """- 🔒 **Self-Recovering Domain Locks**:
  - Implemented cross-platform OS process validation.
  - Automatically reclaims abandoned lock files.
  - Added list_active_locks() and clear_all_locks().
- 🧭 **SPA Crawler**:
  - Emits live discovery telemetry.
"""
    categories = parse_and_categorize_changelog(raw_section)

    assert len(categories["fixes"]) == 1
    assert "Implemented cross-platform OS process validation." in categories["fixes"][0]
    assert "Added list_active_locks()" in categories["fixes"][0]

    assert len(categories["features"]) == 1
    assert "Emits live discovery telemetry." in categories["features"][0]


# ---------------------------------------------------------------------------
# 3. Fallback Git Commit Parsing Tests
# ---------------------------------------------------------------------------


def test_parse_commits_fallback():
    mock_commits = [
        "feat(core): add vector JSONL export (a1b2c3d)",
        "fix(lock): resolve domain lock contention (d4e5f6a)",
        "perf(engine): optimize AST markdown splitter (7b8c9d0)",
        "refactor(gui): modernize theme tokens (1122334)",
        "chore: update dependencies (5566778)",
    ]

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "\n".join(mock_commits)
        categories = parse_commits_fallback("v9.0.1", "v9.0.0")

        assert len(categories["features"]) >= 1
        assert any("add vector JSONL export" in c for c in categories["features"])

        assert len(categories["fixes"]) >= 1
        assert any("resolve domain lock contention" in c for c in categories["fixes"])

        assert len(categories["performance"]) >= 2
        assert any("optimize AST markdown splitter" in c for c in categories["performance"])
        assert any("modernize theme tokens" in c for c in categories["performance"])


# ---------------------------------------------------------------------------
# 4. Artifact Processing & SHA-256 Checksums Tests
# ---------------------------------------------------------------------------


def test_process_artifacts(tmp_path: Path):
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()

    win_exe = artifacts_dir / "gitbook-dl-windows-latest.exe"
    win_data = b"MOCK_WINDOWS_BINARY_CONTENT"
    win_exe.write_bytes(win_data)
    win_hash = hashlib.sha256(win_data).hexdigest()

    linux_bin = artifacts_dir / "gitbook-dl-ubuntu-latest"
    linux_data = b"MOCK_LINUX_BINARY_CONTENT"
    linux_bin.write_bytes(linux_data)
    linux_hash = hashlib.sha256(linux_data).hexdigest()

    mac_bin = artifacts_dir / "gitbook-dl-macos-latest"
    mac_data = b"MOCK_MACOS_BINARY_CONTENT"
    mac_bin.write_bytes(mac_data)
    mac_hash = hashlib.sha256(mac_data).hexdigest()

    manifest_content, table_rows = process_artifacts(artifacts_dir, write_manifest=True)

    # Verify SHA256SUMS.txt file was created
    manifest_file = artifacts_dir / "SHA256SUMS.txt"
    assert manifest_file.is_file()
    assert win_hash in manifest_file.read_text(encoding="utf-8")
    assert linux_hash in manifest_file.read_text(encoding="utf-8")
    assert mac_hash in manifest_file.read_text(encoding="utf-8")

    # Verify table rows
    assert len(table_rows) == 4  # 3 binaries + SHA256SUMS.txt row
    filenames = [r[0] for r in table_rows]
    assert "gitbook-dl-windows-latest.exe" in filenames
    assert "gitbook-dl-ubuntu-latest" in filenames
    assert "gitbook-dl-macos-latest" in filenames
    assert "SHA256SUMS.txt" in filenames

    # Verify platform classification
    row_dict = {r[0]: (r[1], r[3]) for r in table_rows}
    assert row_dict["gitbook-dl-windows-latest.exe"][0] == "Windows x64"
    assert row_dict["gitbook-dl-windows-latest.exe"][1] == win_hash
    assert row_dict["gitbook-dl-ubuntu-latest"][0] == "Linux x64"
    assert row_dict["gitbook-dl-ubuntu-latest"][1] == linux_hash
    assert row_dict["gitbook-dl-macos-latest"][0] == "macOS (Apple Silicon / Intel)"
    assert row_dict["gitbook-dl-macos-latest"][1] == mac_hash
    assert row_dict["SHA256SUMS.txt"][1] == "*(Verification Manifest)*"


def test_process_artifacts_none_or_empty():
    manifest, rows = process_artifacts(None)
    assert manifest == ""
    assert rows == []

    manifest, rows = process_artifacts(Path("/nonexistent/dir"))
    assert manifest == ""
    assert rows == []


# ---------------------------------------------------------------------------
# 5. Full Markdown Document Rendering Tests
# ---------------------------------------------------------------------------


def test_build_release_markdown_all_sections():
    categories = {
        "summary": ["Major release 9.0.1 with stability fixes."],
        "features": ["- ✨ Feature 1", "- 🎨 Feature 2"],
        "fixes": ["- 🔒 Fix 1", "- 🐛 Fix 2"],
        "performance": ["- ⚡ Perf 1"],
    }
    table_rows = [
        ("gitbook-dl-windows-latest.exe", "Windows x64", "24.5 MB", "a1b2c3d4"),
        ("SHA256SUMS.txt", "All Platforms", "< 1 KB", "*(Verification Manifest)*"),
    ]

    doc = build_release_markdown(
        tag="v9.0.1",
        categories=categories,
        table_rows=table_rows,
        prev_tag="v9.0.0",
        repo="RohannShetty/gitbook-downloader",
    )

    assert doc.startswith("# DocHarvest v9.0.1")
    assert "Major release 9.0.1 with stability fixes." in doc
    assert "### ✨ Features & Capabilities" in doc
    assert "### 🐛 Bug Fixes & Hardening" in doc
    assert "### ⚡ Performance & Architecture" in doc
    assert "### 📦 Downloadable Binaries & Verification Checksums" in doc
    assert "| `gitbook-dl-windows-latest.exe` | Windows x64 | 24.5 MB | `a1b2c3d4` |" in doc
    assert "| `SHA256SUMS.txt` | All Platforms | < 1 KB | *(Verification Manifest)* |" in doc
    assert "sha256sum -c SHA256SUMS.txt" in doc
    assert "Get-FileHash -Algorithm SHA256 gitbook-dl-windows-latest.exe" in doc
    assert "**Full Changelog**: https://github.com/RohannShetty/gitbook-downloader/compare/v9.0.0...v9.0.1" in doc


def test_build_release_markdown_single_compare_link():
    categories = {
        "summary": [],
        "features": ["- Feature"],
        "fixes": [],
        "performance": [],
    }
    doc = build_release_markdown(
        tag="v9.0.1",
        categories=categories,
        table_rows=[],
        prev_tag="v9.0.0",
        repo="RohannShetty/gitbook-downloader",
    )

    # Verify no duplicated Full Changelog links
    assert doc.count("Full Changelog") == 1
    assert "https://github.com/RohannShetty/gitbook-downloader/compare/v9.0.0...v9.0.1" in doc


# ---------------------------------------------------------------------------
# 6. End-to-End and CLI Tests
# ---------------------------------------------------------------------------


def test_generate_notes_end_to_end(tmp_path: Path):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("""# Changelog

## [9.0.1] - 2026-08-23

### 🛡️ Engine Hardening & UI Overhaul
Overview text.

- 🔒 **Self-Recovering Domain Locks**: Reclaims locks.
- 🧭 **Intelligent Path-Scope**: SPAs auto-bound.
- ⚡ **Cancellation**: Clean shutdown.
""", encoding="utf-8")

    artifacts_dir = tmp_path / "dist"
    artifacts_dir.mkdir()
    (artifacts_dir / "gitbook-dl-windows-latest.exe").write_bytes(b"DATA")

    notes = generate_notes(
        tag="v9.0.1",
        changelog_path=changelog,
        artifacts_dir=artifacts_dir,
        repo="RohannShetty/gitbook-downloader",
        write_checksums=True,
    )

    assert "# DocHarvest v9.0.1" in notes
    assert "### ✨ Features & Capabilities" in notes
    assert "### 🐛 Bug Fixes & Hardening" in notes
    assert "### ⚡ Performance & Architecture" in notes
    assert "### 📦 Downloadable Binaries & Verification Checksums" in notes


def test_cli_main_execution(tmp_path: Path):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("""## [1.0.0] - 2026-08-23
- ✨ First release
""", encoding="utf-8")

    out_file = tmp_path / "OUTPUT_NOTES.md"

    test_args = [
        "generate_release_notes.py",
        "--tag", "v1.0.0",
        "--changelog-path", str(changelog),
        "--output", str(out_file),
    ]

    with patch.object(sys, "argv", test_args):
        ret = main()
        assert ret == 0

    assert out_file.is_file()
    content = out_file.read_text(encoding="utf-8")
    assert "# DocHarvest v1.0.0" in content
    assert "First release" in content


def test_cli_main_missing_tag():
    test_args = ["generate_release_notes.py"]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit):
            main()
