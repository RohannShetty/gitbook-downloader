"""Design tokens — single source of truth for the TUI look.

Binding tokens (plan §6):

======================  ==========  ==========================================
token                   value       role
======================  ==========  ==========================================
canvas (dark)           #09090b     app background, dark theme (default)
canvas (light)          #fafafa     app background, light theme
surface                 #18181b     cards / tables / raised panels (dark)
hairline                #27272a     1px borders everywhere (dark)
hairline (light)        #e4e4e7     1px borders (light)
accent                  #f59e0b     THE one accent: primary action, active
                                    tab marker, focus ring, progress fill,
                                    snippet highlights, detected-provider chip
accent-strong           #d97706     same hue, AA-safe on light canvas
prose ink               #e4e4e7     body text (dark) / #18181b (light)
muted ink               #a1a1aa     secondary labels (dark) / #52525b (light)
faint ink               #71717a     hints, timestamps
danger (semantic only)  #f85149     errors, destructive confirm (dark)
success (semantic only) #3fb950     diff "added" (dark)
mono font               JetBrains Mono, Cascadia Mono, Consolas…
prose font              Inter, Segoe UI Variable, system-ui…
======================  ==========  ==========================================

Discipline rules enforced here:

* Amber appears ONLY where this module puts it — never as body text,
  never as decoration. Green/red appear ONLY as diff/error semantics.
* Numerals, paths, URLs, table data, keycaps: mono stack (``.mono``).
  Labels, descriptions, buttons: prose stack (the root default).
* Flat surfaces + hairlines only. No gradients, no glow, no emoji icons.
"""

from __future__ import annotations

from textual.theme import Theme

# ── Raw palette (zinc scale + one amber) ─────────────────────────────────

CANVAS_DARK = "#09090b"      # zinc-950
CANVAS_LIGHT = "#fafafa"     # zinc-50
SURFACE_DARK = "#18181b"     # zinc-900
SURFACE_LIGHT = "#ffffff"
PANEL_DARK = "#111113"       # between canvas and surface
PANEL_LIGHT = "#f4f4f5"      # zinc-100
HAIRLINE_DARK = "#27272a"    # zinc-800
HAIRLINE_LIGHT = "#e4e4e7"   # zinc-200
HAIRLINE_STRONG_DARK = "#3f3f46"  # zinc-700
HAIRLINE_STRONG_LIGHT = "#d4d4d8" # zinc-300

INK_HI_DARK = "#e4e4e7"      # zinc-200
INK_HI_LIGHT = "#18181b"     # zinc-900
INK_MUTED_DARK = "#a1a1aa"   # zinc-400
INK_MUTED_LIGHT = "#52525b"  # zinc-600
INK_FAINT_DARK = "#71717a"   # zinc-500
INK_FAINT_LIGHT = "#71717a"

ACCENT = "#f59e0b"           # amber-500 — the ONE accent
ACCENT_STRONG = "#d97706"    # amber-600 — light-theme shade of the same hue
ON_ACCENT = "#09090b"        # text sitting on amber fills

DANGER_DARK = "#f85149"
DANGER_LIGHT = "#cf222e"
SUCCESS_DARK = "#3fb950"
SUCCESS_LIGHT = "#1a7f37"

MONO_STACK = '"JetBrains Mono", "Cascadia Mono", "SF Mono", Consolas, monospace'
PROSE_STACK = '"Inter", "Segoe UI Variable Text", "Segoe UI", system-ui, sans-serif'

# ── Textual themes ───────────────────────────────────────────────────────

GB_DARK = Theme(
    name="gb-dark",
    dark=True,
    primary=ACCENT,
    secondary=INK_MUTED_DARK,
    accent=ACCENT,
    foreground=INK_HI_DARK,
    background=CANVAS_DARK,
    surface=SURFACE_DARK,
    panel=PANEL_DARK,
    boost=HAIRLINE_DARK,
    success=SUCCESS_DARK,
    warning=ACCENT,
    error=DANGER_DARK,
    variables={
        "hairline": HAIRLINE_DARK,
        "hairline-strong": HAIRLINE_STRONG_DARK,
        "ink-muted": INK_MUTED_DARK,
        "ink-faint": INK_FAINT_DARK,
        "raised": SURFACE_DARK,
        "on-accent": ON_ACCENT,
        "mono-font": MONO_STACK,
        "prose-font": PROSE_STACK,
    },
)

GB_LIGHT = Theme(
    name="gb-light",
    dark=False,
    primary=ACCENT_STRONG,
    secondary=INK_MUTED_LIGHT,
    accent=ACCENT_STRONG,
    foreground=INK_HI_LIGHT,
    background=CANVAS_LIGHT,
    surface=SURFACE_LIGHT,
    panel=PANEL_LIGHT,
    boost=HAIRLINE_LIGHT,
    success=SUCCESS_LIGHT,
    warning=ACCENT_STRONG,
    error=DANGER_LIGHT,
    variables={
        "hairline": HAIRLINE_LIGHT,
        "hairline-strong": HAIRLINE_STRONG_LIGHT,
        "ink-muted": INK_MUTED_LIGHT,
        "ink-faint": INK_FAINT_LIGHT,
        "raised": SURFACE_LIGHT,
        "on-accent": CANVAS_LIGHT,
        "mono-font": MONO_STACK,
        "prose-font": PROSE_STACK,
    },
)

THEMES = (GB_DARK, GB_LIGHT)
DEFAULT_THEME = "gb-dark"

#: Parse-time fallbacks. App stylesheets are parsed BEFORE any theme is
#: applied, so every custom variable referenced in styles.tcss must exist
#: even under the stock textual theme. Values here mirror GB_DARK; an
#: active gb-dark/gb-light theme overrides them per theme.
BASE_TOKENS = {
    "hairline": HAIRLINE_DARK,
    "hairline-strong": HAIRLINE_STRONG_DARK,
    "ink-muted": INK_MUTED_DARK,
    "ink-faint": INK_FAINT_DARK,
    "raised": SURFACE_DARK,
    "on-accent": ON_ACCENT,
    "mono-font": MONO_STACK,
    "prose-font": PROSE_STACK,
}


def register_and_apply(app) -> None:
    """Register both themes on *app* and apply the default (dark first)."""
    for theme in THEMES:
        app.register_theme(theme)
    if app.theme not in {t.name for t in THEMES}:
        app.theme = DEFAULT_THEME


# ── Formatting helpers shared by screens (mono/tabular discipline) ───────


def format_size(size_bytes: int) -> str:
    """Human size, stable column width: ``812 B`` / ``1.2 MB``."""
    value = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            if unit == "B":
                return f"{int(value)} B"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} GB"


def format_count(n: int) -> str:
    """Right-alignable numeral grouping: ``12,406``."""
    return f"{n:,}"
