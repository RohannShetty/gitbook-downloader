"""GitBook Downloader v6.0 — CLI interface with subcommands for download, search, list, diff, split, config, mcp, and GUI."""

import argparse
import os
import sys
import time
from pathlib import Path

try:
    from .engine import stream_download
    from .splitter import split_file
    from .utils import load_config, DEFAULTS
except ImportError:
    from engine import stream_download
    from splitter import split_file
    from utils import load_config, DEFAULTS


def cmd_download(args):
    """Download a documentation site."""
    print()
    print("=" * 50)
    print("  GitBook Downloader v6.0")
    print(f"  URL:     {args.url}")
    print(f"  Workers: {args.workers}")
    if args.max_pages:
        print(f"  Max:     {args.max_pages} pages")
    print("=" * 50)
    print()

    t0 = time.time()
    pages = 0
    errors = 0

    def progress(data):
        nonlocal pages, errors
        if data["phase"] == "discovery":
            discovered = data.get("discovered", 0)
            print(f"  🔍 Discovered {discovered} pages...")
        elif data["phase"] == "downloaded":
            pages += 1
            title = data.get("title", data["url"])
            print(f"  ✅ {title} ({data['size_kb']:.1f} KB)")
        elif data["phase"] == "error":
            errors += 1
            print(f"  ❌ {data['url']}: {data['error']}")
        elif data["phase"] == "done":
            elapsed = round(time.time() - t0, 1)
            print()
            print("=" * 50)
            print(f"  Pages: {data['pages']}  Errors: {data['errors']}  Time: {elapsed}s")
            print(f"  Size:  {data['total_size_kb']:.1f} KB")
            print(f"  Provider: {data['provider']}")
            print("=" * 50)
            print()

    try:
        content = stream_download(
            args.url,
            max_pages=args.max_pages,
            workers=args.workers,
            progress_callback=progress,
        )
        if not content:
            print("  No content was downloaded.")
    except KeyboardInterrupt:
        print("\n  Cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n  Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_search(args):
    """Search downloaded documentation."""
    from .search import SearchIndex

    search = SearchIndex()
    results = search.search(args.query, domain=args.domain, limit=args.limit)

    if not results:
        print(f"No results found for '{args.query}'.")
        return

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


def cmd_list(args):
    """List downloaded domains."""
    from .storage import StorageManager

    storage = StorageManager()
    domains = storage.list_domains()

    if not domains:
        print("No domains downloaded yet.")
        return

    print(f"\n{'─' * 60}")
    print(f"  Downloaded Domains ({len(domains)} total)")
    print(f"{'─' * 60}\n")

    for d in domains:
        meta = d  # list_domains already returns metadata dicts
        domain_name = meta.get("domain", "?")
        print(f"  📚 {domain_name}")
        print(f"     Pages: {meta.get('total_pages', '?')}  Provider: {meta.get('provider', '?')}")
        print(f"     Last updated: {meta.get('last_scraped', '?')}")
        print()


def cmd_history(args):
    """Show download history."""
    from .storage import StorageManager, VersionManager

    storage = StorageManager()
    versioning = VersionManager(storage)
    domains_meta = storage.list_domains()

    if not domains_meta:
        print("No download history available.")
        return

    print(f"\n{'─' * 60}")
    print(f"  Download History")
    print(f"{'─' * 60}\n")

    for meta in domains_meta:
        domain_name = meta.get("domain", "?")
        versions = versioning.get_versions(domain_name)
        versions_count = len(versions)
        print(f"  📚 {domain_name} ({versions_count} snapshot(s))")
        print(f"     Provider: {meta.get('provider', '?')}")
        print(f"     Pages: {meta.get('total_pages', '?')}")
        print()

    print(f"{'─' * 60}\n")


def cmd_diff(args):
    """Diff two versions of a domain."""
    from .storage import StorageManager, VersionManager

    storage = StorageManager()
    versioning = VersionManager(storage)

    if not storage.domain_exists(args.domain):
        print(f"Domain '{args.domain}' not found in storage.")
        sys.exit(1)

    diff_text = versioning.diff(args.domain, args.v1, args.v2)
    if not diff_text:
        print(f"No differences found between {args.v1} and {args.v2}.")
        return

    added = [l for l in diff_text.splitlines() if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in diff_text.splitlines() if l.startswith("-") and not l.startswith("---")]

    print(f"\n{'─' * 60}")
    print(f"  Diff: {args.domain}")
    print(f"  {args.v1} vs {args.v2}")
    print(f"{'─' * 60}\n")

    print(f"  Lines added:   {len(added)}")
    print(f"  Lines removed: {len(removed)}")

    if args.verbose:
        print()
        for line in diff_text.splitlines()[:200]:
            print(f"  {line}")

    print()


def cmd_split(args):
    """Split a markdown file into chunks."""
    try:
        input_path = args.file
        if args.output_dir:
            path = Path(args.output_dir)
            path.mkdir(parents=True, exist_ok=True)

        results = split_file(
            input_path=str(input_path),
            output_dir=args.output_dir,
            max_mb=args.max_mb,
            quiet=args.quiet,
        )
        print(f"\n  ✅ Split into {len(results)} chunk(s)")
        for filename, size in results:
            print(f"     {filename} ({size / 1024:.1f} KB)")
        print()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_config(args):
    """Show current configuration."""
    config = load_config()
    print(f"\n{'─' * 60}")
    print(f"  Configuration")
    print(f"{'─' * 60}\n")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()


def cmd_mcp(args):
    """Start the MCP server for AI assistant integration."""
    try:
        from .mcp import main as mcp_main
        mcp_main()
    except ImportError as e:
        print("MCP functionality requires the 'mcp' package.", file=sys.stderr)
        print("Install it with: pip install gitbook-downloader[mcp]", file=sys.stderr)
        sys.exit(1)


def cmd_gui(args):
    """Launch the modern GUI."""
    try:
        from .dashboard import ModernDashboard
        ModernDashboard().mainloop()
    except ImportError as e:
        print("GUI requires customtkinter: pip install customtkinter", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="gitbook-downloader",
        description="Download documentation sites and split into AI-friendly chunks.",
    )
    parser.add_argument("--version", action="version", version="gitbook-downloader 6.0.0")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # download
    dl = sub.add_parser("download", aliases=["dl"], help="Download a documentation site")
    dl.add_argument("url", help="URL of the documentation site")
    dl.add_argument("-w", "--workers", type=int, default=5, help="Parallel workers (1-10)")
    dl.add_argument("-p", "--max-pages", type=int, default=0, help="Max pages (0=unlimited)")
    dl.set_defaults(func=cmd_download)

    # search
    srch = sub.add_parser("search", help="Search downloaded documentation")
    srch.add_argument("query", help="Search query (FTS5 syntax)")
    srch.add_argument("-d", "--domain", help="Restrict search to a domain")
    srch.add_argument("-l", "--limit", type=int, default=10, help="Max results")
    srch.set_defaults(func=cmd_search)

    # list
    lp = sub.add_parser("list", aliases=["ls"], help="List downloaded domains")
    lp.set_defaults(func=cmd_list)

    # history
    hp = sub.add_parser("history", aliases=["hist"], help="Show download history")
    hp.set_defaults(func=cmd_history)

    # diff
    dp = sub.add_parser("diff", help="Diff two versions of a domain")
    dp.add_argument("domain", help="Domain name")
    dp.add_argument("v1", help="First version identifier")
    dp.add_argument("v2", help="Second version identifier")
    dp.add_argument("-v", "--verbose", action="store_true", help="Show full diff")
    dp.set_defaults(func=cmd_diff)

    # split
    spl = sub.add_parser("split", help="Split a markdown file into chunks")
    spl.add_argument("file", help="Path to the markdown file")
    spl.add_argument("-o", "--output-dir", help="Output directory")
    spl.add_argument("-s", "--max-mb", type=float, default=1.0, help="Max MB per chunk")
    spl.add_argument("-q", "--quiet", action="store_true", help="Suppress progress output")
    spl.set_defaults(func=cmd_split)

    # config
    cp = sub.add_parser("config", help="Show configuration")
    cp.set_defaults(func=cmd_config)

    # mcp
    mp = sub.add_parser("mcp", help="Start MCP server for AI assistants")
    mp.set_defaults(func=cmd_mcp)

    # gui
    gp = sub.add_parser("gui", help="Launch the modern GUI")
    gp.set_defaults(func=cmd_gui)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
