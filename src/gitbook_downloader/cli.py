"""
CLI interface for GitBook Downloader.

Usage:
    gitbook-dl download <url> [options]
    gitbook-dl split <file> [options]
    gitbook-dl gui
"""

import argparse
import os
import sys
import time
from datetime import timedelta

from .engine import download_docs
from .splitter import split_file


def cmd_download(args):
    """Download a GitBook documentation site."""
    print(f"\n{'═' * 50}")
    print(f"  GitBook Downloader")
    print(f"  URL:    {args.url}")
    print(f"  Output: {args.output}")
    print(f"  Max:    {args.max_pages} pages")
    print(f"{'═' * 50}\n")

    t0 = time.time()
    out = os.path.abspath(args.output)

    try:
        pages, errors = download_docs(args.url, out, max_pages=args.max_pages)
        elapsed = round(time.time() - t0, 1)

        print(f"\n{'═' * 50}")
        print(f"  DOWNLOAD COMPLETE")
        print(f"  ✓ Pages:    {pages}")
        print(f"  ✕ Errors:   {len(errors)}")
        print(f"  ⏱  Time:     {timedelta(seconds=int(elapsed))}")
        print(f"  📄 Output:   {os.path.basename(out)}")
        print(f"{'═' * 50}\n")
    except KeyboardInterrupt:
        print("\n\n⏹  Stopped by user")
        sys.exit(0)


def cmd_split(args):
    """Split a markdown file into AI-friendly chunks."""
    try:
        split_file(
            input_path=args.file,
            output_dir=args.output_dir,
            max_mb=args.max_mb,
            quiet=False,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_gui(args):
    """Launch the graphical interface."""
    try:
        from .dashboard import Dashboard
        Dashboard().mainloop()
    except ImportError as e:
        print("GUI requires customtkinter: pip install customtkinter", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="gitbook-downloader",
        description="Download complete GitBook documentation sites and split into AI-friendly chunks.",
    )
    parser.add_argument("--version", action="version", version="gitbook-downloader 3.1.1")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # ── download ──
    dl = sub.add_parser("download", help="Download a GitBook documentation site")
    dl.add_argument("url", help="URL of the GitBook site (e.g., https://docs.example.com/)")
    dl.add_argument("-o", "--output", default="downloaded_docs.md", help="Output markdown file")
    dl.add_argument("-p", "--max-pages", type=int, default=500, help="Maximum pages to download")
    dl.set_defaults(func=cmd_download)

    # ── split ──
    sp = sub.add_parser("split", help="Split a markdown file into chunks")
    sp.add_argument("file", help="Path to the markdown file")
    sp.add_argument("-o", "--output-dir", help="Output directory for chunks")
    sp.add_argument("-s", "--max-mb", type=float, default=1.0, help="Max MB per chunk (default: 1.0)")
    sp.set_defaults(func=cmd_split)

    # ── gui ──
    gui = sub.add_parser("gui", help="Launch the graphical dashboard")
    gui.set_defaults(func=cmd_gui)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
