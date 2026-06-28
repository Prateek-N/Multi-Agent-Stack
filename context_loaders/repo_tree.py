"""
context_loaders/repo_tree.py

Walk a repository and emit a filtered, indented file tree with one-line
descriptions for key files. Output is designed to be pasted directly into
an agent session as the "Relevant Files" section of the context block.

Usage:
    python context_loaders/repo_tree.py --path /your/repo
    python context_loaders/repo_tree.py --path /your/repo --filter src/ app/ components/
    python context_loaders/repo_tree.py --path /your/repo --max-depth 3 --output tree.txt

Output format:
    src/
      services/
        user_service.py          # UserService: CRUD + auth helpers
        order_service.py         # OrderService: order lifecycle management
      models/
        user.py                  # User ORM model
    tests/
      test_user_service.py       # Unit tests for UserService
"""

from __future__ import annotations

__version__ = "1.0.0"

import argparse
import sys
from pathlib import Path

# Files to always exclude from the tree
DEFAULT_EXCLUDES = frozenset({
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build",
    ".next", ".nuxt", "coverage", ".coverage", "*.pyc", "*.pyo",
    "*.egg-info", ".DS_Store", "Thumbs.db",
})

# Extensions considered "key" files worth showing even in dense trees
KEY_EXTENSIONS = frozenset({
    ".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".rb", ".rs",
    ".yaml", ".yml", ".toml", ".json", ".env.example", ".md",
    ".sql", ".proto", ".graphql", ".gql",
})

# File-level description heuristics: (pattern, description)
DESCRIPTION_HINTS: list[tuple[str, str]] = [
    ("test_", "unit/integration tests"),
    ("_test.", "unit/integration tests"),
    (".test.", "unit/integration tests"),
    ("spec.", "unit/integration tests"),
    ("router", "route definitions"),
    ("routes", "route definitions"),
    ("controller", "request handler"),
    ("handler", "request handler"),
    ("service", "business logic"),
    ("repository", "data access layer"),
    ("repo.", "data access layer"),
    ("model", "data model / ORM"),
    ("schema", "schema definition"),
    ("migration", "database migration"),
    ("config", "configuration"),
    ("settings", "configuration"),
    ("middleware", "middleware"),
    ("utils", "utility helpers"),
    ("helpers", "utility helpers"),
    ("constants", "constants / enums"),
    ("types", "type definitions"),
    ("index.", "module entrypoint"),
    ("main.", "application entrypoint"),
    ("app.", "application entrypoint"),
    ("__init__", "package init"),
    ("Dockerfile", "container build definition"),
    ("docker-compose", "multi-service container config"),
    ("Makefile", "build/task runner"),
    ("pyproject.toml", "Python project config"),
    ("package.json", "Node.js project config"),
    ("requirements", "Python dependencies"),
]


def _should_exclude(name: str) -> bool:
    name_lower = name.lower()
    for excl in DEFAULT_EXCLUDES:
        if excl.startswith("*"):
            if name_lower.endswith(excl[1:]):
                return True
        elif name_lower == excl.lower():
            return True
    return False


def _describe_file(filename: str) -> str:
    lower = filename.lower()
    for pattern, description in DESCRIPTION_HINTS:
        if pattern.lower() in lower:
            return description
    return ""


def _is_key_file(path: Path) -> bool:
    return path.suffix in KEY_EXTENSIONS


def walk_tree(
    root: Path,
    filter_paths: list[str] | None = None,
    max_depth: int = 5,
    show_all: bool = False,
) -> list[tuple[int, Path, bool]]:
    """
    Walk the directory tree and return (depth, path, is_dir) tuples.
    filter_paths: if set, only include subtrees whose prefix matches one of these strings.
    """
    results: list[tuple[int, Path, bool]] = []

    def _walk(directory: Path, depth: int) -> None:
        if depth > max_depth:
            return
        try:
            entries = sorted(
                (p for p in directory.iterdir() if not p.is_symlink()),
                key=lambda p: (p.is_file(), p.name.lower()),
            )
        except PermissionError:
            return

        for entry in entries:
            if _should_exclude(entry.name):
                continue
            rel = entry.relative_to(root)

            if filter_paths:
                rel_str = str(rel).replace("\\", "/")
                if entry.is_dir():
                    if not any(
                        rel_str.startswith(fp.rstrip("/")) or fp.rstrip("/").startswith(rel_str)
                        for fp in filter_paths
                    ):
                        continue
                else:
                    if not any(rel_str.startswith(fp.rstrip("/")) for fp in filter_paths):
                        continue

            if entry.is_dir():
                results.append((depth, entry, True))
                _walk(entry, depth + 1)
            elif entry.is_file():
                if show_all or _is_key_file(entry):
                    results.append((depth, entry, False))

    _walk(root, 0)
    return results


def format_tree(entries: list[tuple[int, Path, bool]], root: Path | None = None) -> str:
    lines: list[str] = []
    for depth, path, is_dir in entries:
        indent = "  " * depth
        name = path.name + ("/" if is_dir else "")
        if not is_dir:
            desc = _describe_file(path.name)
            comment = f"  # {desc}" if desc else ""
            lines.append(f"{indent}{name}{comment}")
        else:
            lines.append(f"{indent}{name}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Emit a filtered, annotated file tree for agent context."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--path", required=True, help="Root directory of the repository.")
    parser.add_argument(
        "--filter", nargs="*", metavar="PREFIX",
        help="Only include subtrees matching these path prefixes (e.g., src/ app/)."
    )
    parser.add_argument("--max-depth", type=int, default=5, help="Maximum directory depth (default: 5).")
    parser.add_argument("--all", action="store_true", help="Include all files, not just key extensions.")
    parser.add_argument("--output", help="Write output to this file instead of stdout.")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory.", file=sys.stderr)
        sys.exit(1)

    entries = walk_tree(root, filter_paths=args.filter, max_depth=args.max_depth, show_all=args.all)
    output = f"## Repository Tree: {root.name}/\n\n```\n{format_tree(entries, root)}\n```\n"
    output += f"\n({len([e for e in entries if not e[2]])} files shown)\n"

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        sys.stdout.buffer.write(output.encode("utf-8"))


if __name__ == "__main__":
    main()
