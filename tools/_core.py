"""
tools/_core.py

Shared low-level primitives for the agents-maker tools: YAML loading,
crash-safe atomic writes, source-hash computation, and shell-invocation
formatting. Centralizing these removes the copy-pasted helpers that were
previously duplicated across init_project.py, generate_prompt.py,
generate_claude_md.py, generate_platform_configs.py, and validate_kit.py.

Behavior is intentionally identical to the helpers it replaces.
"""

from __future__ import annotations

__version__ = "1.0.0"

import hashlib
import os
import sys
import tempfile
from pathlib import Path

# agents-maker/ (parent of tools/)
KIT_DIR = Path(__file__).resolve().parent.parent

try:
    import yaml
except ImportError:  # pragma: no cover - environment guard
    print("[ERROR] pyyaml is required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> dict:
    """Load a YAML file, returning {} on missing file and logging parse/permission errors."""
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}
    except yaml.YAMLError as e:
        print(f"[ERROR] YAML parse error in {path}: {e}", file=sys.stderr)
        return {}
    except PermissionError:
        print(f"[ERROR] Permission denied reading {path}", file=sys.stderr)
        return {}


# ---------------------------------------------------------------------------
# Atomic writes (write to temp then os.replace — crash-safe)
# ---------------------------------------------------------------------------

def atomic_write(path: Path, content: str) -> None:
    """Atomically write text to path (temp file + os.replace)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", dir=path.parent, delete=False, suffix=".tmp", encoding="utf-8"
    ) as f:
        f.write(content)
        tmp = f.name
    os.replace(tmp, path)


def atomic_write_yaml(path: Path, data: dict) -> None:
    """Atomically dump a dict to a YAML file (temp file + os.replace)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", dir=path.parent, delete=False, suffix=".tmp", encoding="utf-8"
    ) as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        tmp = f.name
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Source hash — lets validate_kit.py detect a stale system_prompt.md
# ---------------------------------------------------------------------------

def source_hash(kit_dir: Path = KIT_DIR) -> str:
    """SHA-256 (first 16 hex chars) over all agent + skill markdown, line-ending normalized."""
    h = hashlib.sha256()
    agent_files = sorted((kit_dir / "agents").glob("*.md")) if (kit_dir / "agents").is_dir() else []
    skill_files = sorted((kit_dir / "skills").glob("*.md")) if (kit_dir / "skills").is_dir() else []
    for path in agent_files + skill_files:
        try:
            h.update(path.read_bytes().replace(b"\r\n", b"\n"))
        except (OSError, PermissionError):
            pass
    return h.hexdigest()[:16]


# ---------------------------------------------------------------------------
# Shell-invocation formatting
# ---------------------------------------------------------------------------

def py_invocation(kit_rel: str, tool: str) -> str:
    """Return a shell-safe 'python ...' invocation, quoting the path when it contains spaces."""
    path = f"{kit_rel}/tools/{tool}"
    return f'python "{path}"' if " " in path else f"python {path}"
