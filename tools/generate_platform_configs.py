#!/usr/bin/env python3
"""
generate_platform_configs.py — Wire agents-maker into every AI platform you use.

Generates native config files for Claude Code, GitHub Copilot, Cursor, and Antigravity
from your project's domain/stack/phase. Commit the generated files — they are project
config, not private state.

Usage:
    python agents-maker/tools/generate_platform_configs.py
    python agents-maker/tools/generate_platform_configs.py --platforms claude copilot cursor
    python agents-maker/tools/generate_platform_configs.py --dry-run
    python agents-maker/tools/generate_platform_configs.py --path /your/project

Generated files (always-on "rules" layer):
    CLAUDE.md                           Claude Code (auto-read every session)
    .github/copilot-instructions.md     GitHub Copilot (workspace instructions)
    .cursor/rules                       Cursor (persistent AI rules)
    .agent/rules/agents-maker.md        Antigravity (native always-on rules)

Native slash-command /commands (the "agents" step) are written to each tool's
command folder by tools/generate_agents.py — see that file.
"""

from __future__ import annotations

__version__ = "1.0.0"

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent   # agents-maker/tools/
KIT_DIR = SCRIPT_DIR.parent                    # agents-maker/
sys.path.insert(0, str(KIT_DIR))

try:
    from tools._core import atomic_write, load_yaml, py_invocation
    from tools.generate_claude_md import _parse_phase, build_claude_md
    from tools.routing import PHASE_LABELS, agent_role_list, phase_agents
except ImportError:
    from _core import atomic_write, load_yaml, py_invocation
    from generate_claude_md import _parse_phase, build_claude_md
    from routing import PHASE_LABELS, agent_role_list, phase_agents

PLATFORMS = ["claude", "agents", "copilot", "cursor", "antigravity"]

# ---------------------------------------------------------------------------
# Helpers shared across builders
# ---------------------------------------------------------------------------

def _yaml_str(value: str) -> str:
    """Return a YAML-safe scalar: quoted if it contains spaces or YAML special characters."""
    if " " in value or any(c in value for c in ":{}[]#&*!|>'\"%@`"):
        return f'"{value}"'
    return value


# ---------------------------------------------------------------------------
# Builder: GitHub Copilot — .github/copilot-instructions.md
# ---------------------------------------------------------------------------

def build_copilot_md(
    project_name: str,
    domain: str,
    confidence: str,
    stack: list[str],
    phase: str,
    kit_rel_path: str,
) -> str:
    stack_str = ", ".join(stack) if stack else "unknown"
    phase_label = PHASE_LABELS.get(phase, phase)
    agents = phase_agents(phase, domain)
    regen_cmd = py_invocation(kit_rel_path, "generate_platform_configs.py")

    all_agents = [
        "orchestrator (routing — always active)",
        "architect_agent (system design, API contracts)",
        "code_agent (software + analytics implementation)",
        "execution_agent (docs, research, marketing, ops)",
        "ui_agent (layout, components, design tokens)",
        "ux_agent (flows, onboarding, funnel critique)",
        "reviewer_agent (QA, severity-rated review)",
        "compression_agent (context compression, resumption)",
    ]

    return (
        f"# agents-maker — GitHub Copilot Instructions\n"
        f"# Auto-generated: {regen_cmd}\n"
        f"# Regenerate after domain/phase changes.\n"
        f"\n"
        f"## Project Context\n"
        f"Project: {project_name} | Domain: {domain} (confidence: {confidence}) | Stack: {stack_str}\n"
        f"Current phase: {phase_label} (`{phase}`)\n"
        f"\n"
        f"## Agent Routing\n"
        f"This project uses the agents-maker multi-agent framework.\n"
        f"Active agents for this phase: {agent_role_list(agents)}.\n"
        f"\n"
        f"Full agent roster:\n"
        + "".join(f"- {a}\n" for a in all_agents)
        + f"\n"
        f"## Response Instructions\n"
        f"- Apply domain routing (`{domain}`) before every suggestion.\n"
        f"- Match output style to the current phase ({phase_label}):\n"
        f"  - implementation → working code with inline comments only\n"
        f"  - solution_design → structured tables and diagrams\n"
        f"  - review_refinement → severity-rated findings (CRITICAL / HIGH / MEDIUM / LOW)\n"
        f"- After every substantive response, suggest 3 ranked next steps.\n"
        f"- Prefer concise, structured output. Avoid explanatory prose when code or bullets suffice.\n"
        f"\n"
        f"## Kit Location\n"
        f"{kit_rel_path}/\n"
        f"Regenerate: `{regen_cmd}`\n"
    )


# ---------------------------------------------------------------------------
# Builder: Cursor — .cursor/rules
# ---------------------------------------------------------------------------

def build_cursor_rules(
    project_name: str,
    domain: str,
    confidence: str,
    stack: list[str],
    phase: str,
    kit_rel_path: str,
) -> str:
    stack_str = ", ".join(stack) if stack else "unknown"
    phase_label = PHASE_LABELS.get(phase, phase)
    agents = phase_agents(phase, domain)
    regen_cmd = py_invocation(kit_rel_path, "generate_platform_configs.py")

    return (
        f"# agents-maker — Cursor Rules\n"
        f"# Auto-generated: {regen_cmd}\n"
        f"# Regenerate after domain/phase changes.\n"
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
        f"All tasks in this project route through the agents-maker multi-agent framework.\n"
        f"Orchestrator is always active. Specialist agents for this phase: {agent_role_list(agents)}.\n"
        f"\n"
        f"## Instructions\n"
        f"- Apply domain routing and phase context from agents-maker before every task.\n"
        f"- Match output style to phase: implementation → code; design → tables; review → severity ratings.\n"
        f"- After every response: append a [Companion] block with 3 ranked next steps.\n"
        f"- Include a `Command:` line the user can copy to continue the workflow.\n"
        f"- Keep responses token-efficient. Prefer bullets over prose.\n"
        f"\n"
        f"## Kit Location\n"
        f"{kit_rel_path}/\n"
        f"Regenerate: `{regen_cmd}`\n"
    )


# ---------------------------------------------------------------------------
# Builder: Antigravity — native always-on rules at .agent/rules/agents-maker.md
# (Slash commands for Antigravity are emitted separately to .agent/workflows/ by
#  tools/generate_agents.py. The previous bespoke .agkit/agents.yaml was dropped —
#  Antigravity does not parse it.)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

_PLATFORM_PATHS: dict[str, str] = {
    "claude":      "CLAUDE.md",
    "copilot":     ".github/copilot-instructions.md",
    "cursor":      ".cursor/rules",
    "antigravity": ".agent/rules/agents-maker.md",
}


def generate_all(
    project_root: Path,
    kit_dir: Path,
    platforms: list[str],
    dry_run: bool,
) -> None:
    project_cfg = load_yaml(kit_dir / "config" / "project.yaml")
    if not project_cfg:
        print("[WARN] config/project.yaml not found — run init_project.py first.", file=sys.stderr)

    domain = project_cfg.get("primary_domain", "general")
    stack = project_cfg.get("stack", [])
    if isinstance(stack, str):
        stack = [s.strip() for s in stack.split(",") if s.strip()]
    project_name = project_cfg.get("project_name", project_root.name)
    confidence = "high" if project_cfg.get("primary_domain") else "low"

    state_path = kit_dir / "project_state.md"
    phase = _parse_phase(state_path.read_text(encoding="utf-8")) if state_path.exists() else "task_framing"

    try:
        kit_rel = kit_dir.relative_to(project_root)
        kit_rel_path = str(kit_rel).replace("\\", "/")
    except ValueError:
        kit_rel_path = "agents-maker"

    builders: dict[str, tuple[str, str]] = {}

    if "claude" in platforms:
        content = build_claude_md(project_name, domain, confidence, stack, phase, kit_rel_path)
        builders["claude"] = (_PLATFORM_PATHS["claude"], content)

    if "copilot" in platforms:
        content = build_copilot_md(project_name, domain, confidence, stack, phase, kit_rel_path)
        builders["copilot"] = (_PLATFORM_PATHS["copilot"], content)

    if "cursor" in platforms:
        content = build_cursor_rules(project_name, domain, confidence, stack, phase, kit_rel_path)
        builders["cursor"] = (_PLATFORM_PATHS["cursor"], content)

    if "antigravity" in platforms:
        # Antigravity reads always-on guidance from .agent/rules/*.md (native).
        content = build_claude_md(project_name, domain, confidence, stack, phase, kit_rel_path)
        builders["antigravity"] = (_PLATFORM_PATHS["antigravity"], content)

    # Native /command files for every tool: .claude/{agents,commands}, .agent/workflows,
    # .cursor/commands, .github/prompts.
    if "agents" in platforms:
        try:
            from tools.generate_agents import generate as _gen_agents
        except ImportError:
            from generate_agents import generate as _gen_agents
        cw, cs = _gen_agents(project_root, kit_dir, template=False, force=False, dry_run=dry_run)
        tag = "[dry-run] would write" if dry_run else "  [DONE]"
        print(f"{tag} {len(cw)} /command file(s) across tool folders"
              + (f"; kept {len(cs)} existing" if cs else ""))

    if dry_run:
        for platform, (rel_path, content) in builders.items():
            print(f"\n{'='*60}")
            print(f"  [{platform.upper()}] → {rel_path}")
            print(f"{'='*60}")
            print(content)
        return

    print()
    written: list[str] = []
    for platform, (rel_path, content) in builders.items():
        out_path = project_root / rel_path
        try:
            atomic_write(out_path, content)
            print(f"  [DONE] {rel_path}  ({platform})")
            written.append(rel_path)
        except OSError as e:
            print(f"  [FAIL] {rel_path}: {e}", file=sys.stderr)

    print()
    print(f"Domain: {domain}  (confidence: {confidence}) | Stack: {', '.join(stack) if stack else 'unknown'} | Phase: {phase}")
    print()
    if written:
        print("Commit these files — they are project config, not private state:")
        for f in written:
            print(f"  git add {f}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Generate platform config files for Claude Code, Copilot, Cursor, and Antigravity.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python agents-maker/tools/generate_platform_configs.py\n"
            "  python agents-maker/tools/generate_platform_configs.py --platforms claude copilot\n"
            "  python agents-maker/tools/generate_platform_configs.py --dry-run\n"
            "  python agents-maker/tools/generate_platform_configs.py --path /my/project\n"
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--platforms",
        nargs="+",
        choices=PLATFORMS,
        default=PLATFORMS,
        metavar="PLATFORM",
        help=f"Platforms to generate configs for (default: all). Choices: {', '.join(PLATFORMS)}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated configs to stdout without writing any files.",
    )
    parser.add_argument(
        "--path",
        help="Project root directory (default: parent of agents-maker/).",
    )
    args = parser.parse_args()

    if args.path:
        project_root = Path(args.path).resolve()
    else:
        project_root = KIT_DIR.parent

    if not project_root.exists() or not project_root.is_dir():
        print(f"[ERROR] Project root does not exist or is not a directory: {project_root}", file=sys.stderr)
        sys.exit(1)

    generate_all(project_root, KIT_DIR, args.platforms, args.dry_run)


if __name__ == "__main__":
    main()
