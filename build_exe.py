"""
Build Script — Creates a standalone .exe for GitBook Downloader.

Run:  python build_exe.py

Output: dist/GitBook-Downloader.exe
"""

import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

# PyInstaller command
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--windowed",          # No console window for GUI
    "--name", "GitBook-Downloader",
    "--add-data", f"src{os.sep}gitbook_downloader{os.pathsep}gitbook_downloader",
    "--hidden-import", "customtkinter",
    "--hidden-import", "tkinter",
    "--hidden-import", "markdownify",
    "--hidden-import", "bs4",
    "--hidden-import", "lxml",
    "--hidden-import", "requests",
    "--hidden-import", "urllib3",
    "--clean",
    "--noconfirm",
    os.path.join(ROOT, "src", "gitbook_downloader", "dashboard.py"),
]

print("Building GitBook Downloader.exe ...")
print(f"Command: {' '.join(cmd)}")
print()

result = subprocess.run(cmd, cwd=ROOT)
sys.exit(result.returncode)
