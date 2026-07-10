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

Generated files:
    CLAUDE.md                           Claude Code (auto-read every session)
    .github/copilot-instructions.md     GitHub Copilot (workspace instructions)
    .cursor/rules                       Cursor (persistent AI rules)
    .agkit/agents.yaml                  Antigravity agkit (agent pipeline config)
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
    from tools.generate_claude_md import (
        _AGENT_ROLES,
        _PHASE_AGENTS,
        _PHASE_LABELS,
        _parse_phase,
        build_claude_md,
    )
except ImportError:
    from _core import atomic_write, load_yaml, py_invocation
    from generate_claude_md import (
        _AGENT_ROLES,
        _PHASE_AGENTS,
        _PHASE_LABELS,
        _parse_phase,
        build_claude_md,
    )

PLATFORMS = ["claude", "claude_agents", "copilot", "cursor", "antigravity"]

# ---------------------------------------------------------------------------
# Helpers shared across builders
# ---------------------------------------------------------------------------

def _active_agents(domain: str, phase: str) -> list[str]:
    phase_map = _PHASE_AGENTS.get(phase, {"_all": ["orchestrator"]})
    return phase_map.get(domain, phase_map["_all"])


def _agent_list_str(agents: list[str]) -> str:
    return ", ".join(f"{a} ({_AGENT_ROLES.get(a, 'specialist')})" for a in agents)


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
    phase_label = _PHASE_LABELS.get(phase, phase)
    agents = _active_agents(domain, phase)
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
        f"Active agents for this phase: {_agent_list_str(agents)}.\n"
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
    phase_label = _PHASE_LABELS.get(phase, phase)
    agents = _active_agents(domain, phase)
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
        f"Orchestrator is always active. Specialist agents for this phase: {_agent_list_str(agents)}.\n"
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
# Builder: Antigravity — .agkit/agents.yaml
# ---------------------------------------------------------------------------

_AGENT_DESCRIPTIONS: dict[str, str] = {
    "orchestrator":      "Phase driver — detects domain, routes tasks, drives 6-phase lifecycle",
    "architect_agent":   "System design, API contracts, solution architecture, research plans",
    "code_agent":        "Software + analytics implementation, refactoring, test generation",
    "execution_agent":   "Non-code output — docs, research, marketing copy, SOPs, runbooks",
    "ui_agent":          "Component hierarchy, layout, design tokens, accessibility",
    "ux_agent":          "Flow critique, onboarding sequences, funnel analysis, friction ID",
    "reviewer_agent":    "Severity-rated QA review for any domain (CRITICAL/HIGH/MEDIUM/LOW)",
    "compression_agent": "Token budget enforcement, context compression, cross-session resumption",
    "brain":             "Project brainstorming — 3+ approaches with trade-offs + a recommendation",
    "planpro":           "Implementation planning — short, specific, dependency-ordered plan file",
}

_AGENT_PHASES: dict[str, list[str]] = {
    "orchestrator":      ["task_framing", "requirements", "solution_design", "implementation", "review_refinement", "handoff"],
    "architect_agent":   ["requirements", "solution_design"],
    "code_agent":        ["implementation", "review_refinement"],
    "execution_agent":   ["implementation"],
    "ui_agent":          ["solution_design", "review_refinement"],
    "ux_agent":          ["solution_design", "review_refinement"],
    "reviewer_agent":    ["review_refinement"],
    "compression_agent": ["handoff"],
    "brain":             ["task_framing", "solution_design"],
    "planpro":           ["task_framing", "requirements", "solution_design"],
}

_AGENT_DOMAINS: dict[str, list[str]] = {
    "orchestrator":      ["software", "content", "research", "data_analytics", "product_design", "marketing", "ops_process", "general"],
    "architect_agent":   ["software", "content", "research", "data_analytics", "product_design", "marketing", "ops_process", "general"],
    "code_agent":        ["software", "data_analytics"],
    "execution_agent":   ["content", "research", "marketing", "ops_process", "product_design", "general"],
    "ui_agent":          ["product_design", "software"],
    "ux_agent":          ["product_design", "marketing"],
    "reviewer_agent":    ["software", "content", "research", "data_analytics", "product_design", "marketing", "ops_process", "general"],
    "compression_agent": ["software", "content", "research", "data_analytics", "product_design", "marketing", "ops_process", "general"],
    "brain":             ["software", "content", "research", "data_analytics", "product_design", "marketing", "ops_process", "general"],
    "planpro":           ["software", "content", "research", "data_analytics", "product_design", "marketing", "ops_process", "general"],
}

_AGENT_ORDER = [
    "orchestrator", "brain", "planpro", "architect_agent", "code_agent", "execution_agent",
    "ui_agent", "ux_agent", "reviewer_agent", "compression_agent",
]


def build_agkit_yaml(
    project_name: str,
    domain: str,
    stack: list[str],
    phase: str,
    kit_rel_path: str,
) -> str:
    regen_cmd = py_invocation(kit_rel_path, "generate_platform_configs.py")
    stack_list = stack if stack else ["unknown"]

    lines: list[str] = [
        "# agents-maker — Antigravity agkit config",
        f"# Auto-generated: {regen_cmd}",
        "# Regenerate after domain/phase changes.",
        f"# See {kit_rel_path}/platforms/antigravity.md for integration guide.",
        "",
        "kit_version: \"1.0\"",
        "",
        "project:",
        f"  name: {project_name}",
        f"  domain: {domain}",
        f"  stack: [{', '.join(stack_list)}]",
        f"  phase: {phase}",
        "",
        "agents:",
    ]

    for agent_id in _AGENT_ORDER:
        desc = _AGENT_DESCRIPTIONS.get(agent_id, agent_id)
        phases = _AGENT_PHASES.get(agent_id, [])
        domains = _AGENT_DOMAINS.get(agent_id, [])
        always = agent_id == "orchestrator"

        lines.append(f"  {agent_id}:")
        lines.append(f"    role: {_AGENT_ROLES.get(agent_id, 'specialist')}")
        lines.append(f"    description: \"{desc}\"")
        lines.append(f"    system_prompt_file: {_yaml_str(kit_rel_path + '/agents/' + agent_id + '.md')}")
        if always:
            lines.append("    always_active: true")
        else:
            lines.append(f"    active_phases: [{', '.join(phases)}]")
            lines.append(f"    active_domains: [{', '.join(domains)}]")
        lines.append("")

    lines += [
        "context:",
        "  inject_globally:",
        f"    - {_yaml_str(kit_rel_path + '/config/agents.yaml')}",
        f"    - {_yaml_str(kit_rel_path + '/config/domain_profiles.yaml')}",
        f"    - {_yaml_str(kit_rel_path + '/config/token_policies.yaml')}",
        "  inject_per_session:",
        f"    - {_yaml_str(kit_rel_path + '/project_state.md')}",
        "",
        "skills:",
    ]

    skills = [
        ("analyze_repo",      "Any session starting with a code repo"),
        ("design_api",        "API design, schema, contract decisions"),
        ("review_code",       "Code review, QA, security audit"),
        ("review_layout",     "UI/UX critique, layout and accessibility"),
        ("improve_copy",      "Writing quality, tone, clarity"),
        ("write_tests",       "Test generation, coverage, edge cases"),
        ("summarize_history", "Cross-session compression and handoff"),
        ("suggest_next",      "Auto-fires after every deliverable"),
        ("compare_approaches","Structured decision table for trade-offs"),
        ("animated_website",  "CSS/GSAP/Framer Motion animation code"),
        ("write_process_map", "SOP/runbook: steps + RACI + exceptions"),
        ("define_data_schema","ER sketch + metric definitions + data dictionary"),
    ]
    for key, trigger in skills:
        lines.append(f"  {key}:")
        lines.append(f"    skill_file: {_yaml_str(kit_rel_path + '/skills/' + key + '.md')}")
        lines.append(f"    trigger: \"{trigger}\"")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

_PLATFORM_PATHS: dict[str, str] = {
    "claude":      "CLAUDE.md",
    "copilot":     ".github/copilot-instructions.md",
    "cursor":      ".cursor/rules",
    "antigravity": ".agkit/agents.yaml",
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
        content = build_agkit_yaml(project_name, domain, stack, phase, kit_rel_path)
        builders["antigravity"] = (_PLATFORM_PATHS["antigravity"], content)

    # Claude Code subagents + slash commands (.claude/agents, .claude/commands).
    if "claude_agents" in platforms:
        try:
            from tools.generate_claude_agents import generate as _gen_claude
        except ImportError:
            from generate_claude_agents import generate as _gen_claude
        cw, cs = _gen_claude(project_root / ".claude", kit_dir, force=False, dry_run=dry_run)
        tag = "[dry-run] would write" if dry_run else "  [DONE]"
        print(f"{tag} {len(cw)} .claude/ file(s) — subagents + slash commands"
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
