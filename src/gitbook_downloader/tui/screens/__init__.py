"""TUI surfaces package."""

from .diagnostics import DiagnosticsSurface
from .diff import DiffSurface
from .library import LibrarySurface
from .search import SearchSurface
from .wizard import WizardSurface

__all__ = [
    "DiagnosticsSurface",
    "DiffSurface",
    "LibrarySurface",
    "SearchSurface",
    "WizardSurface",
]
