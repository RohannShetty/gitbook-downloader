"""
Markdown Splitter — Split large markdown files into AI-friendly chunks.

Splits on header boundaries (#) so chunks never break mid-section.
Supports token-aware splitting via tiktoken (optional).
"""

import os
import re

# Try to import tiktoken for token-aware splitting
try:
    import tiktoken

    _TIKTOKEN_AVAILABLE = True
    _enc = tiktoken.get_encoding("cl100k_base")  # GPT-4 / Claude encoding
except ImportError:
    _TIKTOKEN_AVAILABLE = False
    _enc = None


def count_tokens(text: str) -> int:
    """Count tokens in text. Falls back to character estimate if tiktoken unavailable."""
    if _TIKTOKEN_AVAILABLE and _enc is not None:
        return len(_enc.encode(text))
    # Rough estimate: ~4 chars per token for English text
    return len(text) // 4


def split_markdown(
    input_path: str,
    output_dir: str,
    max_mb: float = 1.0,
    max_tokens: int = 0,
    chunk_prefix: str = "doc_part",
):
    """
    Split a markdown file into chunks.

    Args:
        input_path: Path to the markdown file
        output_dir: Directory to write chunks to
        max_mb: Maximum chunk size in megabytes (default 1.0)
        max_tokens: Maximum tokens per chunk (0 = use max_mb instead)
        chunk_prefix: Prefix for chunk filenames

    Returns:
        List of (filename, byte_size) tuples
    """
    os.makedirs(output_dir, exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    if max_tokens > 0 and _TIKTOKEN_AVAILABLE:
        # Token-aware splitting
        return _split_by_tokens(content, output_dir, max_tokens, chunk_prefix)
    else:
        # Byte-size splitting (header-boundary aware)
        return _split_by_size(content, output_dir, max_mb, chunk_prefix)


def _split_by_size(content: str, output_dir: str, max_mb: float, prefix: str):
    """Split by byte size on header boundaries."""
    sections = content.split("\n#")
    chunks = []
    current = ""
    limit = int(max_mb * 1024 * 1024)

    for i, sec in enumerate(sections):
        if i > 0:
            sec = "#" + sec
        if len((current + sec).encode("utf-8")) > limit and current.strip():
            chunks.append(current)
            current = sec
        else:
            current += sec
    if current.strip():
        chunks.append(current)

    results = []
    for i, chunk in enumerate(chunks, 1):
        fname = os.path.join(output_dir, f"{prefix}_{i:03d}.md")
        with open(fname, "w", encoding="utf-8") as f:
            f.write(chunk)
        results.append((fname, len(chunk)))
    return results


def _split_by_tokens(content: str, output_dir: str, max_tokens: int, prefix: str):
    """Split by token count on header boundaries."""
    sections = content.split("\n#")
    chunks = []
    current = ""

    for i, sec in enumerate(sections):
        if i > 0:
            sec = "#" + sec
        combined = current + sec
        if count_tokens(combined) > max_tokens and current.strip():
            chunks.append(current)
            current = sec
        else:
            current = combined
    if current.strip():
        chunks.append(current)

    results = []
    for i, chunk in enumerate(chunks, 1):
        fname = os.path.join(output_dir, f"{prefix}_{i:03d}.md")
        with open(fname, "w", encoding="utf-8") as f:
            f.write(chunk)
        token_count = count_tokens(chunk)
        results.append((fname, len(chunk), token_count))
    return results


def split_file(
    input_path: str,
    output_dir: str | None = None,
    max_mb: float = 1.0,
    max_tokens: int = 0,
    quiet: bool = False,
):
    """
    Convenience function for splitting with progress output.

    Args:
        input_path: Path to the markdown file
        output_dir: Output directory (defaults to <input>_chunks/)
        max_mb: Max megabytes per chunk
        max_tokens: Max tokens per chunk (0 = use max_mb)
        quiet: Suppress output
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    if output_dir is None:
        base = os.path.splitext(input_path)[0]
        output_dir = f"{base}_chunks"

    if not quiet:
        print(f"📄 Input:  {input_path}")
        print(f"📁 Output: {output_dir}")
        if max_tokens > 0:
            print(f"🎯 Max:    {max_tokens:,} tokens per chunk")
        else:
            print(f"📏 Max:    {max_mb} MB per chunk")
        print()

    chunks = split_markdown(input_path, output_dir, max_mb, max_tokens)

    if not quiet:
        total_bytes = 0
        for item in chunks:
            if len(item) == 3:
                fn, sz, tk = item
                total_bytes += sz
                kb = sz / 1024
                s = f"{kb / 1024:.1f} MB" if kb >= 1024 else f"{kb:.0f} KB"
                print(f"  ✓ {os.path.basename(fn):32s} {s:>10s}  ({tk:,} tokens)")
            else:
                fn, sz = item
                total_bytes += sz
                kb = sz / 1024
                s = f"{kb / 1024:.1f} MB" if kb >= 1024 else f"{kb:.0f} KB"
                print(f"  ✓ {os.path.basename(fn):32s} {s:>10s}")
        print(f"\n━━━ {len(chunks)} chunks ({total_bytes / 1024:.0f} KB total) ━━━")

    return chunks
