"""
CLI interface for GitBook Downloader.

Usage:
    gitbook-downloader download <url> [options]
    gitbook-downloader split <file> [options]
    gitbook-downloader gui
"""

import argparse
import os
import sys
import time
from datetime import timedelta

from .engine import SmartEngine
from .splitter import split_file


def cmd_download(args):
    """Download a GitBook documentation site."""
    print(f"\n{'═' * 60}")
    print(f"  GitBook Downloader  —  {args.url}")
    print(f"  Output: {args.output}")
    print(f"  Max pages: {args.max_pages}")
    print(f"  Workers: {args.workers}")
    print(f"{'═' * 60}\n")

    out = os.path.abspath(args.output)
    engine = SmartEngine(args.url, out, max_pages=args.max_pages)
    engine.CONCURRENCY = args.workers

    t0 = time.time()

    # Start engine in background thread
    import threading
    thread = threading.Thread(target=engine.run, daemon=True)
    thread.start()

    # Poll logs
    downloaded = 0
    failed = 0
    try:
        while not engine.done.is_set() or not engine.log.empty():
            try:
                entry = engine.log.get(timeout=0.1)
                level = entry["level"]
                msg = entry["msg"]
                if level == "highlight":
                    print(f"\n{msg}")
                elif level == "success":
                    print(f"  {msg}")
                elif level == "error":
                    print(f"  {msg}")
                elif level == "info":
                    print(f"  {msg}")

                # Update progress
                s = entry["stats"]
                downloaded = s.get("downloaded", 0)
                failed = s.get("failed", 0)
                discovered = s.get("discovered", 0)
                if s.get("phase") == "download" and discovered > 0:
                    pct = (downloaded + failed) / discovered * 100
                    print(f"\r  Progress: {downloaded}/{discovered} ({pct:.0f}%)  ", end="", flush=True)
            except Exception:
                pass

        engine.done.wait()
        elapsed = round(time.time() - t0, 1)

        print(f"\n\n{'═' * 60}")
        print(f"  DOWNLOAD COMPLETE")
        print(f"  ✓ Downloaded:  {downloaded} pages")
        print(f"  ✕ Failed:      {failed} pages")
        print(f"  ⏱  Time:        {timedelta(seconds=int(elapsed))}")
        print(f"  📄 Output:      {os.path.basename(out)}")
        print(f"{'═' * 60}\n")

    except KeyboardInterrupt:
        engine.stop()
        print("\n\n⏹  Stopped by user")
        sys.exit(0)


def cmd_split(args):
    """Split a markdown file into AI-friendly chunks."""
    try:
        split_file(
            input_path=args.file,
            output_dir=args.output_dir,
            max_mb=args.max_mb,
            max_tokens=args.max_tokens,
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
        print(f"GUI requires customtkinter: pip install customtkinter", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="gitbook-downloader",
        description="Download complete GitBook documentation sites and split into AI-friendly chunks.",
    )
    parser.add_argument("--version", action="version", version="gitbook-downloader 3.1.0")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # ── download ──
    dl = sub.add_parser("download", help="Download a GitBook documentation site")
    dl.add_argument("url", help="URL of the GitBook site (e.g., https://docs.example.com/)")
    dl.add_argument("-o", "--output", default="downloaded_docs.md", help="Output markdown file")
    dl.add_argument("-p", "--max-pages", type=int, default=5000, help="Maximum pages to download")
    dl.add_argument("-w", "--workers", type=int, default=5, help="Parallel download workers (1-10)")
    dl.set_defaults(func=cmd_download)

    # ── split ──
    sp = sub.add_parser("split", help="Split a markdown file into chunks")
    sp.add_argument("file", help="Path to the markdown file")
    sp.add_argument("-o", "--output-dir", help="Output directory for chunks")
    sp.add_argument("-s", "--max-mb", type=float, default=1.0, help="Max MB per chunk (default: 1.0)")
    sp.add_argument("-t", "--max-tokens", type=int, default=0,
                    help="Max tokens per chunk (overrides --max-mb, requires tiktoken)")
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
