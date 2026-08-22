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
# a real script file, so we generate a two-line runner that imports cli:main.
RUNNER = """\
from gitbook_downloader.cli import main

if __name__ == "__main__":
    main()
"""

# Hidden imports: packages imported dynamically (Textual loads widgets lazily;
# markdownify/bs4 are plugin-style). Stdlib modules need no entries.
HIDDEN_IMPORTS = [
    "textual",
    "textual.widgets",
    "rich",
    "markdownify",
    "bs4",
    "lxml",
    "requests",
    "urllib3",
]


def build() -> int:
    with tempfile.TemporaryDirectory(prefix="gbd-build-") as tmp:
        runner = os.path.join(tmp, "gitbook_dl_entry.py")
        with open(runner, "w", encoding="utf-8") as fh:
            fh.write(RUNNER)

        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            "--console",  # TUI world: console app, no windowed GUI
            "--name",
            "gitbook-dl",
            "--collect-all",
            "gitbook_downloader",  # submodules + package data (TUI assets)
        ]
        for mod in HIDDEN_IMPORTS:
            cmd += ["--hidden-import", mod]
        cmd += ["--clean", "--noconfirm", runner]

        print("Building gitbook-dl (console onefile) ...")
        print(f"Command: {' '.join(cmd)}")
        print()

        result = subprocess.run(cmd, cwd=ROOT)

    out = os.path.join(ROOT, "dist")
    if result.returncode == 0 and os.path.isdir(out):
        for name in sorted(os.listdir(out)):
            path = os.path.join(out, name)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"Built: {path} ({size_mb:.1f} MB)")
    return result.returncode


if __name__ == "__main__":
    sys.exit(build())
