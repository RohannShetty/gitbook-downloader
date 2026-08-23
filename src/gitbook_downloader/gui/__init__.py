"""Desktop GUI module for gitbook-downloader."""

from __future__ import annotations

from .app import launch_gui
from .bridge import ApiBridge

__all__ = ["launch_gui", "ApiBridge"]
