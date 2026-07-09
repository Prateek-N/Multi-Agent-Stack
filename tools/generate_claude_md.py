#!/usr/bin/env python3
"""
generate_claude_md.py — Writes CLAUDE.md to your project root for Claude Code integration.

Claude Code auto-reads CLAUDE.md every session, so agents-maker domain/phase/stack
context loads automatically — no copy-paste, no CLI step before every message.

Usage:
    python agents-maker/tools/generate_claude_md.py
    python agents-maker/tools/generate_claude_md.py --path /your/project
    python agents-maker/tools/generate_claude_md.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

__version__ = "1.0.0"

SCRIPT_DIR = Path(__file__).resolve().parent   # agents-maker/tools/
KIT_DIR = SCRIPT_DIR.parent                     # agents-maker/
sys.path.insert(0, str(KIT_DIR))

try:
    from tools._core import atomic_write, load_yaml, py_invocation
    from tools.routing import AGENT_ROLES, PHASE_AGENTS, PHASE_LABELS, phase_agents
except ImportError:
    from _core import atomic_write, load_yaml, py_invocation
    from routing import AGENT_ROLES, PHASE_AGENTS, PHASE_LABELS, phase_agents

# Backward-compatible aliases (generate_platform_configs imports these names).
_PHASE_AGENTS = PHASE_AGENTS
_PHASE_LABELS = PHASE_LABELS
_AGENT_ROLES = AGENT_ROLES

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_phase(state_text: str) -> str:
    m = re.search(r"##\s+Current Phase\s*\n+(\S+)", state_text)
    if m:
        return m.group(1).strip()
    return "task_framing"


def _active_agents(domain: str, phase: str) -> list[str]:
    return phase_agents(phase, domain)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

def build_claude_md(
    project_name: str,
    domain: str,
    confidence: str,
    stack: list[str],
    phase: str,
    kit_rel_path: str,
) -> str:
    stack_str = ", ".join(stack) if stack else "unknown"
    phase_label = _PHASE_LABELS.get(phase, phase)
    agents = _active_agents(domain, phase)
    agent_list = ", ".join(
        f"{a} ({_AGENT_ROLES.get(a, 'specialist')})" for a in agents
    )
    regen_cmd = py_invocation(kit_rel_path, "generate_claude_md.py")
    prompt_cmd = py_invocation(kit_rel_path, "generate_prompt.py")

    return (
        f"# agents-maker — Project AI Config\n"
        f"# Auto-generated: {regen_cmd}\n"
        f"# Regenerate after domain/phase changes: {regen_cmd}\n"
        f"\n"
        f"## Active Domain\n"
        f"{domain}  (confidence: {confidence})\n"
        f"\n"
        f"## Stack\n"
        f"{stack_str}\n"
        f"\n"
        f"## Current Phase\n"
        f"{phase_label} (`{phase}`)\n"
        f"\n"
        f"## Agent Routing\n"
        f"All tasks in this project route through the agents-maker multi-agent kit.\n"
        f"Orchestrator is always active. Specialist agents for this phase: {agent_list}.\n"
        f"\n"
        f"## Session Instructions\n"
        f"- Apply domain routing and phase context from agents-maker before every task.\n"
        f"- After every response: append a [Companion] block with 3 ranked next steps.\n"
        f"- Include a `Command:` line the user can copy to continue the workflow.\n"
        f"\n"
        f"## Kit Location\n"
        f"{kit_rel_path}/ (relative to project root)\n"
        f'Generate a fresh prompt: `{prompt_cmd} "your task"`\n'
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Write CLAUDE.md to your project root for Claude Code integration.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python agents-maker/tools/generate_claude_md.py\n"
            "  python agents-maker/tools/generate_claude_md.py --path /my/project\n"
            "  python agents-maker/tools/generate_claude_md.py --dry-run\n"
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--path",
        help="Project root directory (default: parent of agents-maker/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated CLAUDE.md to stdout without writing the file.",
    )
    args = parser.parse_args()

    # Resolve project root
    if args.path:
        project_root = Path(args.path).resolve()
    else:
        project_root = KIT_DIR.parent

    if not project_root.exists() or not project_root.is_dir():
        print(
            f"[ERROR] Project root does not exist or is not a directory: {project_root}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load project config
    project_cfg = load_yaml(KIT_DIR / "config" / "project.yaml")
    if not project_cfg:
        print(
            "[WARN] config/project.yaml not found — run init_project.py first.",
            file=sys.stderr,
        )

    domain = project_cfg.get("primary_domain", "general")
    stack = project_cfg.get("stack", [])
    if isinstance(stack, str):
        stack = [s.strip() for s in stack.split(",") if s.strip()]

    # domain_confidence is not stored in project.yaml yet; infer from presence of the key
    confidence = "high" if project_cfg.get("primary_domain") else "low"

    # Read current phase from project_state.md
    state_path = KIT_DIR / "project_state.md"
    if state_path.exists():
        phase = _parse_phase(state_path.read_text(encoding="utf-8"))
    else:
        phase = "task_framing"

    # Compute kit path relative to project root (for portability)
    try:
        kit_rel = KIT_DIR.relative_to(project_root)
        kit_rel_path = str(kit_rel).replace("\\", "/")
    except ValueError:
        kit_rel_path = "agents-maker"

    content = build_claude_md(
        project_name=project_root.name,
        domain=domain,
        confidence=confidence,
        stack=stack,
        phase=phase,
        kit_rel_path=kit_rel_path,
    )

    if args.dry_run:
        print(content)
        return

    out_path = project_root / "CLAUDE.md"
    atomic_write(out_path, content)

    print(f"\nWritten: {out_path}")
    print(f"  Domain : {domain}  (confidence: {confidence})")
    print(f"  Stack  : {', '.join(stack) if stack else 'unknown'}")
    print(f"  Phase  : {phase}")
    print()
    print("Claude Code will auto-load this context on every session.")
    print("Commit CLAUDE.md to git — it is project config, not private state.")
    print()


if __name__ == "__main__":
    main()
