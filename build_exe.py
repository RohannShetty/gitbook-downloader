"""
Build Script — Creates standalone console binaries for GitBook Downloader.

This is the SINGLE SOURCE OF TRUTH for PyInstaller settings.
CI (.github/workflows/build-release.yml) and local builds both run this
script; there is deliberately no second copy of the spec.

Run:  python build_exe.py

Output: dist/gitbook-dl(.exe)  — console onefile, TUI entry point
        (`gitbook_downloader.cli:main`; bare invocation launches the Textual TUI).
"""

import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))

# Entry point: the console script target from pyproject.toml. PyInstaller needs
# a real script file, so we generate a runner that imports cli:main.
#
# Two non-obvious requirements:
# 1. `gitbook_downloader.tui` is imported LAZILY by cli.py, so PyInstaller's
#    static analysis never sees it — we must import it here explicitly or the
#    frozen exe reports "TUI isn't available" (v7.0.0 release bug).
# 2. Double-clicking an exe gives you a console that closes the instant the
#    process exits. An unexpected crash must pause so the user can read it.
RUNNER = """\
import sys

# Ensure UTF-8 output on Windows consoles so Unicode box chars and emojis never crash cp1252/cp437
if sys.platform == "win32":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

import gitbook_downloader.tui.app  # noqa: F401  (force-bundle the lazy TUI)
import gitbook_downloader.gui.app  # noqa: F401  (force-bundle the Desktop GUI)
from gitbook_downloader.cli import main

if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException:
        import traceback

        traceback.print_exc()
        if getattr(sys, "frozen", False):
            try:
                input("\\nAn unexpected error occurred. Press Enter to close...")
            except EOFError:
                pass
        raise
"""

# Hidden imports: packages imported dynamically (Textual loads widgets lazily;
# markdownify/bs4 are plugin-style; webview loads edgechromium/pythonnet dynamically).
HIDDEN_IMPORTS = [
    "textual",
    "textual.widgets",
    "rich",
    "markdownify",
    "bs4",
    "lxml",
    "requests",
    "urllib3",
    "pyperclip",
    "webview",
    "clr_loader",
    "pythonnet",
    "bottle",
]

# Whole-package collects: modules whose submodules/data files are loaded
# dynamically and would otherwise be missed by static analysis.
COLLECT_ALL = [
    "gitbook_downloader",  # submodules + package data (TUI + GUI assets)
    "textual",             # .tcss stylesheets, drivers, widget data
    "webview",             # pywebview drivers and JS bridges
]


def build() -> int:
    frontend_dir = os.path.join(ROOT, "frontend")
    if os.path.isdir(frontend_dir) and os.path.isfile(os.path.join(frontend_dir, "package.json")):
        print("Compiling frontend React/shadcn assets with Vite...")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        npm_res = subprocess.run([npm_cmd, "run", "build"], cwd=frontend_dir)
        if npm_res.returncode != 0:
            print("Frontend compilation failed!")
            return npm_res.returncode

    with tempfile.TemporaryDirectory(prefix="gbd-build-") as tmp:
        runner = os.path.join(tmp, "gitbook_dl_entry.py")
        with open(runner, "w", encoding="utf-8") as fh:
            fh.write(RUNNER)

        web_src = os.path.join(ROOT, "src", "gitbook_downloader", "gui", "web")
        data_sep = ";" if sys.platform == "win32" else ":"
        add_data = f"{web_src}{data_sep}gitbook_downloader/gui/web"

        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            "--console",  # Console bootloader that launches Desktop GUI or CLI
            "--name",
            "gitbook-dl",
            "--add-data",
            add_data,
        ]
        for mod in COLLECT_ALL:
            cmd += ["--collect-all", mod]
        for mod in HIDDEN_IMPORTS:
            cmd += ["--hidden-import", mod]
        cmd += ["--clean", "--noconfirm", runner]

        print("Building gitbook-dl (console onefile) ...")
        print(f"Command: {' '.join(cmd)}")
        print()

        result = subprocess.run(cmd, cwd=ROOT)

    out = os.path.join(ROOT, "dist")
    if result.returncode == 0 and os.path.isdir(out):
        # Remove stale artifacts from earlier builds/eras so dist/ only ever
        # contains what this script just produced.
        produced = {"gitbook-dl.exe" if sys.platform == "win32" else "gitbook-dl"}
        for name in sorted(os.listdir(out)):
            path = os.path.join(out, name)
            if name not in produced:
                import shutil

                shutil.rmtree(path, ignore_errors=True) if os.path.isdir(path) else os.remove(path)
                print(f"Removed stale artifact: {path}")
            else:
                size_mb = os.path.getsize(path) / (1024 * 1024)
                print(f"Built: {path} ({size_mb:.1f} MB)")
    return result.returncode


if __name__ == "__main__":
    sys.exit(build())
