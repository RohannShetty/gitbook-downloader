"""
CLI for GitBook Downloader v3.2.

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
    print(f"  GitBook Downloader v3.2")
    print(f"  URL:     {args.url}")
    print(f"  Output:  {args.output}")
    print(f"  Max:     {args.max_pages} pages")
    print(f"  Workers: {args.workers}")
    print(f"{'═' * 50}\n")

    t0 = time.time()
    out = os.path.abspath(args.output)

    try:
        pages, errors = download_docs(
            args.url, out,
            max_pages=args.max_pages,
            workers=args.workers,
        )
        elapsed = round(time.time() - t0, 1)
        print(f"\n{'═' * 50}")
        print(f"  ✅ {pages} pages | {len(errors)} errors | {timedelta(seconds=int(elapsed))}")
        print(f"  📄 {os.path.basename(out)}")
        print(f"{'═' * 50}\n")
    except KeyboardInterrupt:
        print("\n⏹ Cancelled")
        sys.exit(0)


def cmd_split(args):
    """Split a markdown file into chunks."""
    try:
        split_file(input_path=args.file, output_dir=args.output_dir,
                   max_mb=args.max_mb, quiet=False)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_gui(args):
    """Launch the modern GUI."""
    try:
        from .dashboard import ModernDashboard
        ModernDashboard().mainloop()
    except ImportError as e:
        print("GUI requires customtkinter: pip install customtkinter", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="gitbook-downloader",
        description="Download complete GitBook documentation sites and split into AI-friendly chunks.",
    )
    parser.add_argument("--version", action="version", version="gitbook-downloader 3.2.0")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    dl = sub.add_parser("download", help="Download a GitBook documentation site")
    dl.add_argument("url", help="URL of the GitBook site")
    dl.add_argument("-o", "--output", default="downloaded_docs.md", help="Output file")
    dl.add_argument("-p", "--max-pages", type=int, default=500, help="Max pages")
    dl.add_argument("-w", "--workers", type=int, default=5, help="Parallel workers (1-10)")
    dl.set_defaults(func=cmd_download)

    sp = sub.add_parser("split", help="Split a markdown file into chunks")
    sp.add_argument("file", help="Path to the markdown file")
    sp.add_argument("-o", "--output-dir", help="Output directory")
    sp.add_argument("-s", "--max-mb", type=float, default=1.0, help="Max MB per chunk")
    sp.set_defaults(func=cmd_split)

    gui = sub.add_parser("gui", help="Launch the modern GUI")
    gui.set_defaults(func=cmd_gui)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
