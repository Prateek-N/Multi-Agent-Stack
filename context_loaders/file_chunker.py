"""
context_loaders/file_chunker.py

Extract, read, and optionally truncate specific files for inclusion in an
agent context block. Designed to be used after repo_tree.py identifies
the relevant files.

Usage:
    # Read specific files
    python context_loaders/file_chunker.py \\
        --path /your/repo \\
        --files services/user_service.py models/user.py tests/test_user_service.py

    # Read all files under a directory, truncated
    python context_loaders/file_chunker.py \\
        --path /your/repo \\
        --dirs services/ models/ \\
        --max-lines 200

    # Output to a file
    python context_loaders/file_chunker.py \\
        --path /your/repo \\
        --files services/user_service.py \\
        --output chunks.txt

Output format (paste directly into agent context):
    ### services/user_service.py
    ```python
    <file content or truncated snippet>
    ```
"""

from __future__ import annotations

__version__ = "1.0.0"

import argparse
import sys
from pathlib import Path

# Default truncation settings (matches token_optimization defaults)
DEFAULT_MAX_LINES = 200
DEFAULT_HEAD_LINES = 40
DEFAULT_TAIL_LINES = 40

# Extensions that have a known language tag for fenced code blocks
LANG_MAP: dict[str, str] = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".js": "javascript",
    ".jsx": "jsx",
    ".go": "go",
    ".java": "java",
    ".rb": "ruby",
    ".rs": "rust",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".c": "c",
    ".sql": "sql",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".json": "json",
    ".md": "markdown",
    ".sh": "bash",
    ".bash": "bash",
    ".graphql": "graphql",
    ".gql": "graphql",
    ".proto": "protobuf",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
}


def _lang_tag(path: Path) -> str:
    return LANG_MAP.get(path.suffix.lower(), "text")


def truncate_content(content: str, max_lines: int, head_lines: int, tail_lines: int) -> tuple[str, int]:
    """
    Truncate content to head + tail with a gap marker.
    Returns (truncated_content, lines_omitted).
    """
    lines = content.splitlines()
    if len(lines) <= max_lines:
        return content, 0

    head = lines[:head_lines]
    tail = lines[-tail_lines:]
    omitted = len(lines) - head_lines - tail_lines
    gap = f"# ... [{omitted} lines omitted — request full file if needed] ..."
    return "\n".join(head + [gap] + tail), omitted


def read_file(
    file_path: Path,
    max_lines: int = DEFAULT_MAX_LINES,
    head_lines: int = DEFAULT_HEAD_LINES,
    tail_lines: int = DEFAULT_TAIL_LINES,
    no_truncate: bool = False,
) -> dict:
    """
    Read a single file and return a dict with path, content, lang, and truncation info.
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError) as e:
        return {
            "path": str(file_path),
            "content": f"# Error reading file: {e}",
            "lang": "text",
            "truncated": False,
            "lines_omitted": 0,
            "total_lines": 0,
        }

    total_lines = content.count("\n") + 1

    if no_truncate:
        truncated_content, omitted = content, 0
    else:
        truncated_content, omitted = truncate_content(content, max_lines, head_lines, tail_lines)

    return {
        "path": str(file_path),
        "content": truncated_content,
        "lang": _lang_tag(file_path),
        "truncated": omitted > 0,
        "lines_omitted": omitted,
        "total_lines": total_lines,
    }


def format_chunk(chunk: dict, root: Path | None = None) -> str:
    """Format a single file chunk as a fenced code block for agent context."""
    display_path = chunk["path"]
    if root:
        try:
            display_path = str(Path(chunk["path"]).relative_to(root))
        except ValueError:
            pass

    header = f"### {display_path}"
    if chunk["truncated"]:
        header += f"  _(truncated: {chunk['lines_omitted']} lines omitted of {chunk['total_lines']} total)_"

    return f"{header}\n```{chunk['lang']}\n{chunk['content']}\n```"


def collect_from_dirs(
    root: Path,
    dirs: list[str],
    extensions: set[str] | None = None,
    max_files: int = 20,
) -> list[Path]:
    """Collect file paths from specified subdirectories."""
    if extensions is None:
        extensions = set(LANG_MAP.keys())

    paths: list[Path] = []
    for d in dirs:
        target = root / d.lstrip("/")
        if not target.is_dir():
            print(f"Warning: {target} is not a directory — skipping.", file=sys.stderr)
            continue
        for p in sorted(target.rglob("*")):
            if p.is_file() and p.suffix in extensions:
                paths.append(p)
            if len(paths) >= max_files:
                break
    return paths[:max_files]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract and format file chunks for agent context."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--path", required=True, help="Repository root directory.")
    parser.add_argument(
        "--files", nargs="*", metavar="FILE",
        help="Relative paths to specific files (from --path root)."
    )
    parser.add_argument(
        "--dirs", nargs="*", metavar="DIR",
        help="Subdirectories to collect all key files from."
    )
    parser.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES,
                        help=f"Max lines before truncation (default: {DEFAULT_MAX_LINES}).")
    parser.add_argument("--head-lines", type=int, default=DEFAULT_HEAD_LINES,
                        help=f"Lines kept from start on truncation (default: {DEFAULT_HEAD_LINES}).")
    parser.add_argument("--tail-lines", type=int, default=DEFAULT_TAIL_LINES,
                        help=f"Lines kept from end on truncation (default: {DEFAULT_TAIL_LINES}).")
    parser.add_argument("--no-truncate", action="store_true",
                        help="Disable truncation (caution: may produce very large output).")
    parser.add_argument("--max-files", type=int, default=20,
                        help="Max files when using --dirs (default: 20).")
    parser.add_argument("--output", help="Write output to this file instead of stdout.")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory.", file=sys.stderr)
        sys.exit(1)

    file_paths: list[Path] = []

    if args.files:
        root_resolved = root.resolve()
        for f in args.files:
            p = (root / f).resolve()
            if not str(p).startswith(str(root_resolved)):
                print(f"[WARN] Skipping {f} — path escapes project root.", file=sys.stderr)
                continue
            if p.is_file():
                file_paths.append(p)
            else:
                print(f"[WARN] {p} not found — skipping.", file=sys.stderr)

    if args.dirs:
        file_paths.extend(collect_from_dirs(root, args.dirs, max_files=args.max_files))

    if not file_paths:
        print("No files found. Provide --files or --dirs.", file=sys.stderr)
        sys.exit(1)

    chunks = [
        read_file(
            p,
            max_lines=args.max_lines,
            head_lines=args.head_lines,
            tail_lines=args.tail_lines,
            no_truncate=args.no_truncate,
        )
        for p in file_paths
    ]

    header = f"## Relevant Files ({len(chunks)} files)\n"
    body = "\n\n".join(format_chunk(c, root=root) for c in chunks)
    output = header + "\n" + body + "\n"

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        sys.stdout.buffer.write(output.encode("utf-8"))


if __name__ == "__main__":
    main()
