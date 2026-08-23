"""gitbook-downloader v8 — Desktop GUI and CLI surface.

    gitbook-dl                        → Desktop GUI (or TUI fallback)
    gitbook-dl gui                    → Desktop GUI
    gitbook-dl capture <url> [--scope P]... [--exclude P]... [--max-pages N]
                  [--workers N] [--latest-only] [--versions v1,v2]
                  [--output both|library|local] [-o DIR] [--no-snapshot]
                  [--preset NAME]                                     (alias: dl)
    gitbook-dl <url>                  → sugar for capture
    gitbook-dl search QUERY [-d DOMAIN] [-l N]
    gitbook-dl ls                     → library domains (alias: list)
    gitbook-dl history DOMAIN · diff DOMAIN V1 V2
    gitbook-dl split FILE --max-mb X [-o DIR] [-q]
    gitbook-dl config [init|show|path] · mcp · tui

All captures go through the facade (:func:`gitbook_downloader.api.capture`)
— this module owns no download logic.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from . import __version__
except ImportError:  # pragma: no cover - direct-script fallback
    __version__ = "8.0.0"


# ── Helpers ─────────────────────────────────────────────────────────────


def _configure_console_streams() -> None:
    """Ensure standard output and error streams handle Unicode without charmap crashes."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _looks_like_url(text: str) -> bool:
    return text.startswith("http://") or text.startswith("https://")


def _import_tui_run():
    """Lazy-import seam for the TUI entrypoint (patchable in tests).

    Kept separate from :func:`_launch_tui` so tests can simulate a missing
    'textual' install without intercepting builtins.__import__ (unreliable
    for relative imports) or booting the real Textual app.
    """
    try:
        from .tui import run as tui_run
        return tui_run
    except ImportError:
        from .tui.app import run as tui_run  # type: ignore[no-redef]
        return tui_run


def _launch_tui() -> int:
    """Launch the Textual TUI lazily; print a friendly message if missing."""
    try:
        tui_run = _import_tui_run()
    except ImportError:
        print("The interactive TUI isn't available in this installation.",
              file=sys.stderr)
        print("It needs the 'textual' package "
              "(pip install \"gitbook-downloader[tui]\").", file=sys.stderr)
        print("You can still use the CLI:  gitbook-dl capture <url>",
              file=sys.stderr)
        return 1
    tui_run()
    return 0


def _launch_gui() -> int:
    """Launch the Desktop GUI; fall back to TUI if pywebview is unavailable."""
    try:
        from .gui import launch_gui
        launch_gui()
        return 0
    except ImportError:
        return _launch_tui()
    except Exception as exc:
        print(f"Note: Desktop GUI unavailable ({exc}). Starting TUI…", file=sys.stderr)
        return _launch_tui()



def _print_progress(event) -> None:
    """Render one facade ProgressEvent as a console line."""
    if event.kind == "discovered":
        print(f"  🔍 Discovered {event.count} pages...")
    elif event.kind == "downloaded":
        title = event.title or event.url or ""
        size = f" ({event.size_kb:.1f} KB)" if event.size_kb is not None else ""
        print(f"  ✅ {title}{size}")
    elif event.kind == "failed":
        print(f"  ❌ {event.url}: {event.message}", file=sys.stderr)
    # "written" is summarised by the result block below.


def _print_capture_result(result) -> None:
    width = 60
    print()
    print("─" * width)
    print(f"  Provider:      {result.provider}")
    print(f"  Pages:         {result.pages_captured}"
          f"   (skipped: {result.skipped})")
    if result.site_versions_found:
        print(f"  Site versions: {', '.join(result.site_versions_found)}")
    if result.version_id:
        print(f"  Snapshot of previous capture: {result.version_id}")
    if result.local_path:
        print(f"  Local output:  {result.local_path}")
    if result.library_path:
        print(f"  Library:       {result.library_path}")
    if result.book_file:
        print(f"  Book file:     {result.book_file}")
    if result.manifest_file:
        print(f"  Manifest:      {result.manifest_file}")
    for warning in result.warnings:
        print(f"  ⚠ {warning}", file=sys.stderr)
    print("─" * width)
    print()


# ── Commands ────────────────────────────────────────────────────────────


def cmd_capture(args) -> int:
    """Capture a documentation site via the facade."""
    from .api import LATEST_ONLY, CaptureError, capture
    from .utils.config import capture_options_from_config, load_full_config

    cfg = load_full_config()

    site_versions = None
    if getattr(args, "latest_only", False):
        site_versions = (LATEST_ONLY,)
    elif args.versions:
        site_versions = tuple(
            v.strip() for v in args.versions.split(",") if v.strip()
        )

    cli_overrides = {
        "workers": args.workers,
        "max_pages": args.max_pages,
        "path_scope": tuple(args.scope) if args.scope else None,
        "exclude_paths": tuple(args.exclude) if args.exclude else None,
        "site_versions": site_versions,
        "output_mode": args.output,
        "local_dir": str(args.output_dir) if args.output_dir else None,
        "snapshot": False if args.no_snapshot else None,
    }

    try:
        options = capture_options_from_config(
            cfg, preset=args.preset, cli_overrides=cli_overrides
        )
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.max_pages is not None and args.max_pages <= 0:
        print("Error: --max-pages must be a positive number "
              "(omit it for unlimited).", file=sys.stderr)
        return 2

    target = args.url
    if not target:
        preset_table = cfg.preset(args.preset or "")
        if not preset_table or not preset_table.get("url"):
            print("Error: a URL (or a --preset with a url) is required.",
                  file=sys.stderr)
            return 2
        target = str(preset_table["url"])

    print()
    print("=" * 50)
    print(f"  Capturing {target}")
    print(f"  Output mode: {options.output_mode}   Workers: {options.workers}")
    if options.max_pages:
        print(f"  Max pages:   {options.max_pages}")
    print("=" * 50)
    print()

    try:
        result = capture(target, options, progress=_print_progress)
    except CaptureError as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n  Cancelled.")
        return 130

    _print_capture_result(result)
    if result.pages_captured == 0:
        return 1
    return 0


def cmd_search(args) -> int:
    """Search downloaded documentation."""
    from .search import SearchIndex

    search = SearchIndex()
    results = search.search(args.query, domain=args.domain, limit=args.limit)

    if not results:
        print(f"No results found for '{args.query}'.")
        return 0

    print(f"\n{'─' * 60}")
    print(f"  Search results for: {args.query}")
    print(f"{'─' * 60}\n")

    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['title']}")
        print(f"     Domain: {r['domain']}")
        print(f"     URL:    {r['url']}")
        print(f"     Score:  {r.get('rank', 0):.2f}")
        print()

    print(f"{'─' * 60}")
    print(f"  {len(results)} result(s)")
    print(f"{'─' * 60}\n")
    return 0


def cmd_list(args) -> int:
    """List library domains."""
    from .storage import StorageManager

    storage = StorageManager()
    domains = storage.list_domains()

    if not domains:
        print("No domains captured yet. Try: gitbook-dl capture <url>")
        return 0

    print(f"\n{'─' * 60}")
    print(f"  Library Domains ({len(domains)} total)")
    print(f"{'─' * 60}\n")

    for meta in domains:
        print(f"  📚 {meta.get('domain', '?')}")
        print(f"     Pages: {meta.get('total_pages', '?')}  "
              f"Provider: {meta.get('provider') or '?'}")
        print(f"     Last updated: {meta.get('last_scraped', '?')}")
        print()
    return 0


def cmd_history(args) -> int:
    """Show snapshot history for one domain."""
    from .storage import StorageManager, VersionManager

    storage = StorageManager()
    versioning = VersionManager(storage)

    if not storage.domain_exists(args.domain):
        print(f"Domain '{args.domain}' not found in the library.", file=sys.stderr)
        return 1

    meta = storage.get_metadata(args.domain) or {}
    versions = versioning.get_versions(args.domain)

    print(f"\n{'─' * 60}")
    print(f"  History: {args.domain}")
    print(f"{'─' * 60}\n")
    print(f"  Provider: {meta.get('provider') or '?'}   "
          f"Pages: {meta.get('total_pages', '?')}")
    print(f"  Latest:   {meta.get('latest_version', '?')}\n")

    if not versions:
        print("  No snapshots recorded.")
    else:
        for v in versions:
            marker = " ← latest" if v.get("is_latest") else ""
            print(f"  🕑 {v.get('version')}  {v.get('timestamp', '')}"
                  f"  ({v.get('size_kb', 0)} KB){marker}")
    print()
    return 0


def cmd_diff(args) -> int:
    """Diff two snapshots of a domain."""
    from .storage import StorageManager, VersionManager, VersioningError

    storage = StorageManager()
    versioning = VersionManager(storage)

    if not storage.domain_exists(args.domain):
        print(f"Domain '{args.domain}' not found in storage.", file=sys.stderr)
        return 1

    try:
        diff_text = versioning.diff(args.domain, args.v1, args.v2)
    except VersioningError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not diff_text:
        print(f"No differences found between {args.v1} and {args.v2}.")
        return 0

    added = [l for l in diff_text.splitlines()
             if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in diff_text.splitlines()
               if l.startswith("-") and not l.startswith("---")]

    print(f"\n{'─' * 60}")
    print(f"  Diff: {args.domain}  {args.v1} vs {args.v2}")
    print(f"{'─' * 60}\n")
    print(f"  Lines added:   {len(added)}")
    print(f"  Lines removed: {len(removed)}\n")

    if args.verbose:
        for line in diff_text.splitlines()[:200]:
            print(f"  {line}")
        print()
    return 0


def cmd_split(args) -> int:
    """Split a markdown file into chunks."""
    from .splitter import split_file

    try:
        if args.output_dir:
            Path(args.output_dir).mkdir(parents=True, exist_ok=True)

        results = split_file(
            input_path=str(args.file),
            output_dir=args.output_dir,
            max_mb=args.max_mb,
            quiet=args.quiet,
        )
        print(f"\n  ✅ Split into {len(results)} chunk(s)")
        for filename, size in results:
            print(f"     {filename} ({size / 1024:.1f} KB)")
        print()
        return 0
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def cmd_config(args) -> int:
    """Config subcommands: init | show | path."""
    from .utils.config import (
        capture_options_from_config,
        config_search_paths,
        find_config_files,
        init_default_config,
        load_full_config,
    )

    action = args.config_command or "show"

    if action == "init":
        dest = "./gitbook-downloader.toml" if args.project else None
        written = init_default_config(dest)
        print(f"Config ready: {written}")
        if not args.project:
            print("(Project-level file: gitbook-dl config init --project)")
        return 0

    if action == "path":
        existing = dict(find_config_files())
        print("\nConfig search order (low → high precedence):")
        for label, path in config_search_paths():
            mark = "✓" if label in existing else "·"
            print(f"  [{mark}] {label:7} {path}")
        print()
        return 0

    # show (default)
    cfg = load_full_config()
    print(f"\n{'─' * 60}")
    print("  Configuration")
    if cfg.sources:
        print(f"  Sources: {', '.join(cfg.sources)}")
    else:
        print("  Sources: (none found — using built-in defaults)")
    print(f"{'─' * 60}\n")
    for key in sorted(cfg.values):
        print(f"  {key}: {cfg.values[key]}")
    if cfg.presets:
        print("\n  Presets:")
        for name, table in sorted(cfg.presets.items()):
            desc = table.get("url", "(no url)")
            print(f"    • {name}  →  {desc}")
    else:
        print("\n  Presets: (none defined)")
    print()

    # Sanity-check that the config still builds valid capture options.
    try:
        capture_options_from_config(cfg)
    except Exception as exc:  # noqa: BLE001
        print(f"  ⚠ Config does not produce valid capture options: {exc}",
              file=sys.stderr)
        return 1
    return 0


def cmd_mcp(args) -> int:
    """Start the MCP server for AI assistant integration."""
    try:
        from .mcp import main as mcp_main
    except ImportError:
        print("MCP functionality requires the 'mcp' package.", file=sys.stderr)
        print("Install it with: pip install gitbook-downloader[mcp]",
              file=sys.stderr)
        return 1
    mcp_main()
    return 0


def cmd_gui(args) -> int:
    """Launch the Desktop GUI."""
    return _launch_gui()


def cmd_tui(args) -> int:
    """Launch the interactive TUI."""
    return _launch_tui()


# ── Parser ──────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gitbook-dl",
        description=(
            "Capture documentation sites as Markdown — page tree, book file, "
            "and llms.txt manifest — into your project and a searchable library."
        ),
    )
    parser.add_argument(
        "--version", action="version",
        version=f"gitbook-downloader {__version__}",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # capture (alias: dl)
    cap = sub.add_parser(
        "capture", aliases=["dl"],
        help="Capture a documentation site (URL or --preset name)",
    )
    cap.add_argument("url", nargs="?", default=None,
                     help="URL of the documentation site (or omit with --preset)")
    cap.add_argument("--scope", action="append", metavar="P",
                     help="Only pages under this URL path prefix (repeatable)")
    cap.add_argument("--exclude", action="append", metavar="P",
                     help="Skip URLs matching this path pattern (repeatable)")
    cap.add_argument("--max-pages", type=int, default=None, metavar="N",
                     help="Stop after N pages (default: unlimited)")
    cap.add_argument("--workers", type=int, default=None, metavar="N",
                     help="Parallel fetches (default: 8)")
    cap.add_argument("--latest-only", action="store_true",
                     help="Capture only the newest detected site version")
    cap.add_argument("--versions", metavar="V1,V2",
                     help="Comma-separated site versions to capture (default: all)")
    cap.add_argument("--output", choices=["both", "library", "local"],
                     default=None,
                     help="Where to write output (default: both)")
    cap.add_argument("-o", "--output-dir", default=None, metavar="DIR",
                     help="Project-local output directory "
                          "(default: ./<domain>-docs/)")
    cap.add_argument("--no-snapshot", action="store_true",
                     help="Don't snapshot the previous capture before overwriting")
    cap.add_argument("--preset", default=None, metavar="NAME",
                     help="Use a named [presets.<name>] entry from config")
    cap.set_defaults(func=cmd_capture)

    # search
    srch = sub.add_parser("search", help="Search captured documentation")
    srch.add_argument("query", help="Search query (FTS5 syntax)")
    srch.add_argument("-d", "--domain", help="Restrict search to a domain")
    srch.add_argument("-l", "--limit", type=int, default=10,
                      help="Max results")
    srch.set_defaults(func=cmd_search)

    # ls (alias: list)
    lp = sub.add_parser("ls", aliases=["list"],
                        help="List library domains")
    lp.set_defaults(func=cmd_list)

    # history
    hp = sub.add_parser("history", help="Show snapshot history for a domain")
    hp.add_argument("domain", help="Domain name (e.g. docs.example.com)")
    hp.set_defaults(func=cmd_history)

    # diff
    dp = sub.add_parser("diff", help="Diff two snapshots of a domain")
    dp.add_argument("domain", help="Domain name")
    dp.add_argument("v1", help="First version identifier")
    dp.add_argument("v2", help="Second version identifier")
    dp.add_argument("-v", "--verbose", action="store_true",
                    help="Show the full diff")
    dp.set_defaults(func=cmd_diff)

    # split
    spl = sub.add_parser("split", help="Split a markdown file into chunks")
    spl.add_argument("file", help="Path to the markdown file")
    spl.add_argument("-o", "--output-dir", help="Output directory")
    spl.add_argument("--max-mb", "-s", type=float, default=1.0,
                     help="Max MB per chunk")
    spl.add_argument("-q", "--quiet", action="store_true",
                     help="Suppress progress output")
    spl.set_defaults(func=cmd_split)

    # config
    cp = sub.add_parser("config", help="Manage configuration")
    cp.add_argument("config_command", nargs="?", default=None,
                    choices=["init", "show", "path"])
    cp.add_argument("--project", action="store_true",
                     help="(with init) write ./gitbook-downloader.toml instead "
                          "of the global config")
    cp.set_defaults(func=cmd_config)

    # mcp
    mp = sub.add_parser("mcp", help="Start MCP server for AI assistants")
    mp.set_defaults(func=cmd_mcp)

    # gui
    gp = sub.add_parser("gui", help="Launch the Desktop GUI application")
    gp.set_defaults(func=cmd_gui)

    # tui
    tp = sub.add_parser("tui", help="Launch the interactive TUI")
    tp.set_defaults(func=cmd_tui)

    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_console_streams()
    argv = list(sys.argv[1:] if argv is None else argv)

    # Bare invocation → Desktop GUI (or TUI fallback)
    if not argv:
        return _launch_gui()

    # Bare-URL sugar: `gitbook-dl https://…` == `gitbook-dl capture https://…`
    if _looks_like_url(argv[0]):
        argv.insert(0, "capture")

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:  # pragma: no cover - argparse handles this
        parser.print_help()
        return 1

    return int(args.func(args) or 0)


if __name__ == "__main__":
    sys.exit(main())
