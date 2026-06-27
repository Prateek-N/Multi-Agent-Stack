"""
context_loaders

Utilities for generating compact project context for agent sessions.

Scripts:
    repo_tree.py       - Walk repo and emit a filtered file tree with descriptions.
    file_chunker.py    - Extract and truncate key files for agent context.
    project_summary.py - Produce a compact stack/services/entrypoints summary.

Typical session setup:
    python context_loaders/project_summary.py --path /your/repo
    python context_loaders/repo_tree.py --path /your/repo --filter src/ app/
    (paste both outputs as the opening message in your agent session)
"""
