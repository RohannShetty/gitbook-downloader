"""GitBook Downloader v5.0 — .md-aware streaming download, llms.txt discovery, improved content extraction."""

__version__ = "5.0.0"


def _fix_pyinstaller_imports():
    """Fix module imports when running as a PyInstaller --onefile executable.

    In --onefile mode, the script runs standalone (not as a package),
    so relative imports (from .engine) fail. This adds the internal
    package directory to sys.path so absolute imports (from engine) work.
    """
    import sys as _sys
    import os as _os

    if getattr(_sys, 'frozen', False) and hasattr(_sys, '_MEIPASS'):
        pkg_dir = _os.path.join(_sys._MEIPASS, 'gitbook_downloader')
        if _os.path.isdir(pkg_dir) and pkg_dir not in _sys.path:
            _sys.path.insert(0, pkg_dir)
        # Also add the MEIPASS root for ctk_fonts etc.
        if _sys._MEIPASS not in _sys.path:
            _sys.path.insert(0, _sys._MEIPASS)
