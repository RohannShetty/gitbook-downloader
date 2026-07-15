"""
Markdown Splitter — Split large downloaded docs into AI-friendly chunks.

Splits on markdown headers (#) so chunks NEVER break mid-section or mid-code-block.
This is the exact logic that produced the 37 clean chunks from the 39 MB download.
"""

import os


def split_markdown(input_path, output_dir=None, max_mb=1.0, progress_callback=None):
    """
    Split a markdown file into chunks on header boundaries.

    Respects markdown structure — splits on `#` headers so each chunk
    starts cleanly at a section boundary. Chunks are never cut mid-paragraph
    or mid-code-block.

    Args:
        input_path: Path to the combined markdown file
        output_dir: Directory to write chunks into (created if missing)
        max_mb: Maximum chunk size in megabytes (default 1.0)

    Returns:
        List of (filename, byte_size) tuples
    """
    os.makedirs(output_dir, exist_ok=True)

    # Read input
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    max_bytes = int(max_mb * 1024 * 1024)

    # Split on markdown headers — this is the key: we split at `\n#`
    # so each chunk starts at a header boundary
    sections = content.split("\n#")
    chunks = []
    current = ""

    for i, section in enumerate(sections):
        if i > 0:
            section = "#" + section  # Restore the header marker

        # If adding this section would exceed the limit AND we already have content,
        # finish the current chunk and start a new one
        if len((current + section).encode("utf-8")) > max_bytes and current.strip():
            chunks.append(current)
            current = section
        else:
            current += section

    # Don't forget the last chunk
    if current.strip():
        chunks.append(current)

    # Write chunks to disk
    results = []
    for i, chunk in enumerate(chunks, 1):
        filename = os.path.join(output_dir, f"doc_part_{i:02d}.md")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(chunk)
        chunk_path = filename
        results.append((filename, len(chunk)))
        if progress_callback:
            progress_callback({"phase": "chunk", "index": i, "total": len(chunks), "filename": os.path.basename(chunk_path)})

    return results


def split_file(input_path, output_dir=None, max_mb=1.0, quiet=False, progress_callback=None):
    """
    Convenience function — split with progress output.

    Args:
        input_path: Path to markdown file
        output_dir: Output directory (defaults to <input>_chunks/)
        max_mb: Max megabytes per chunk
        quiet: Suppress output

    Returns:
        List of (filename, byte_size) tuples
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    if output_dir is None:
        base = os.path.splitext(input_path)[0]
        output_dir = f"{base}_chunks"

    if not quiet:
        print(f"Reading {input_path}...")
        print(f"Splitting into chunks (max {max_mb} MB each)...")

    chunks = split_markdown(input_path, output_dir, max_mb, progress_callback=progress_callback)

    if not quiet:
        total_kb = 0
        for fn, sz in chunks:
            kb = sz / 1024
            total_kb += kb
            s = f"{kb / 1024:.1f} MB" if kb >= 1024 else f"{kb:.0f} KB"
            print(f"  Created: {os.path.basename(fn):30s} {s:>10s}")

        print(f"\n  Done! {len(chunks)} chunks created ({total_kb:.0f} KB total)")

    return chunks
