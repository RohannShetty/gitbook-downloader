"""
Launcher for PyInstaller-packaged executable.
Run this directly or use as PyInstaller entry point.
"""

import sys
import os

# Ensure we can import from the bundled package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gitbook_downloader.dashboard import ModernDashboard


def main():
    ModernDashboard().mainloop()


if __name__ == "__main__":
    main()
