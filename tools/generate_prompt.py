#!/usr/bin/env python3
"""
generate_prompt.py — Daily-use tool for agents-maker Companion Mode.

Assembles a domain-routed, phase-aware prompt block to paste into any AI tool
(Claude, Codex, Antigravity). Selects the right agents and skills for the
current lifecycle phase, inlines project context and session state, and
prints the result to stdout.

Note: This tool does not run the token compression pipeline from compressor.py.
Use the --full flag to include the full system prompt; otherwise the system
prompt should be loaded separately as a persistent system instruction.

Usage:
    python agents-maker/tools/generate_prompt.py "add rate limiting to the auth service"
    python agents-maker/tools/generate_prompt.py "compare JWT vs Redis sessions"
    python agents-maker/tools/generate_prompt.py "add tests" --phase implementation
    python agents-maker/tools/generate_prompt.py "add tests" --full
"""

import argparse
import sys
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent   # agents-maker/tools/
KIT_DIR = SCRIPT_DIR.parent                    # agents-maker/
sys.path.insert(0, str(KIT_DIR))

try:
    import yaml
except ImportError:
    print("[ERROR] pyyaml is required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

__version__ = "1.0.0"

MAX_PROBLEM_LENGTH = 5000

# ---------------------------------------------------------------------------
# Domain scoring — delegated to shared domain_utils module
# ---------------------------------------------------------------------------

try:
    from tools.domain_utils import detect_domain as _du_detect, _load_yaml
except ImportError:
    from domain_utils import detect_domain as _du_detect, _load_yaml


def detect_domain(problem: str) -> tuple[str, str, float]:
    return _du_detect(problem, kit_dir=KIT_DIR, include_score=True)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Phase inference
# ---------------------------------------------------------------------------

PHASES = [
    "task_framing",
    "requirements",
    "solution_design",
    "implementation",
    "review_refinement",
    "handoff",
]

PHASE_ALIASES = {
    "framing": "task_framing",
    "task_framing": "task_framing",
    "requirements": "requirements",
    "design": "solution_design",
    "solution_design": "solution_design",
    "implementation": "implementation",
    "implement": "implementation",
    "review": "review_refinement",
    "review_refinement": "review_refinement",
    "handoff": "handoff",
}


def infer_phase(state_path: Path) -> str:
    if not state_path.exists():
        return "task_framing"
    try:
        text = state_path.read_text(encoding="utf-8")
    except (OSError, PermissionError):
        return "task_framing"

    # Look for "## Current Phase" section and read the next non-empty line
    in_phase_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "## Current Phase":
            in_phase_section = True
            continue
        if in_phase_section:
            if stripped and not stripped.startswith("#"):
                for phase in PHASES:
                    if phase in stripped.lower():
                        return phase
                # Line found but didn't match — stop looking
                break
    return "task_framing"


# ---------------------------------------------------------------------------
# Agent selection per phase × domain
# ---------------------------------------------------------------------------

PHASE_AGENTS: dict[str, list[str]] = {
    "task_framing":      ["orchestrator"],
    "requirements":      ["orchestrator", "architect_agent"],
    "solution_design":   ["orchestrator", "architect_agent"],
    "implementation":    ["orchestrator"],
    "review_refinement": ["orchestrator", "reviewer_agent"],
    "handoff":           ["orchestrator"],
}

IMPLEMENTATION_AGENT: dict[str, str] = {
    "software":       "code_agent",
    "data_analytics": "code_agent",
    "content":        "execution_agent",
    "research":       "execution_agent",
    "product_design": "execution_agent",
    "marketing":      "execution_agent",
    "ops_process":    "execution_agent",
    "general":        "execution_agent",
}

DESIGN_AGENTS: dict[str, list[str]] = {
    "product_design": ["ui_agent", "ux_agent"],
    "marketing":      ["ux_agent"],
}


def select_agents(phase: str, domain: str) -> list[str]:
    agents = list(PHASE_AGENTS.get(phase, ["orchestrator"]))

    if phase == "implementation":
        impl_agent = IMPLEMENTATION_AGENT.get(domain, "execution_agent")
        if impl_agent not in agents:
            agents.append(impl_agent)
        for extra in DESIGN_AGENTS.get(domain, []):
            if extra not in agents:
                agents.append(extra)

    if phase == "solution_design":
        for extra in DESIGN_AGENTS.get(domain, []):
            if extra not in agents:
                agents.append(extra)

    return agents


def select_skills(agents: list[str]) -> list[str]:
    agents_cfg = _load_yaml(KIT_DIR / "config" / "agents.yaml").get("agents", {})
    seen: set[str] = set()
    skills: list[str] = []
    for agent in agents:
        for skill in agents_cfg.get(agent, {}).get("skills", []):
            if skill not in seen:
                seen.add(skill)
                skills.append(skill)
    return skills


# ---------------------------------------------------------------------------
# Load agent + skill markdown content
# ---------------------------------------------------------------------------

def load_agent_md(agent_name: str) -> str:
    path = KIT_DIR / "agents" / f"{agent_name}.md"
    if path.exists():
        try:
            return path.read_text(encoding="utf-8").strip()
        except (OSError, PermissionError):
            pass
    return f"# {agent_name}\n(agent file not found)"


def load_skill_md(skill_key: str) -> str:
    path = KIT_DIR / "skills" / f"{skill_key}.md"
    if path.exists():
        try:
            return path.read_text(encoding="utf-8").strip()
        except (OSError, PermissionError):
            pass
    return ""


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------

def _token_est(text: str) -> int:
    """Rough estimate: 1 token ≈ 4 chars. For accuracy use anthropic SDK count_tokens."""
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Core prompt builder
# ---------------------------------------------------------------------------

def build_prompt(
    problem: str,
    domain: str,
    confidence: str,
    score: float,
    phase: str,
    agents: list[str],
    skills: list[str],
    project_cfg: dict,
    state_text: str,
    include_system: bool = False,
) -> str:
    parts: list[str] = []

    if include_system:
        sys_path = KIT_DIR / "system_prompt.md"
        if sys_path.exists():
            try:
                parts.append(sys_path.read_text(encoding="utf-8").strip())
                parts.append("\n" + "=" * 60 + "\n")
            except (OSError, PermissionError):
                print("[WARN] Could not read system_prompt.md — inlining agents instead.", file=sys.stderr)
                include_system = False

        if not sys_path.exists() or not include_system:
            for agent in agents:
                parts.append(load_agent_md(agent))
                parts.append("---")
            for skill in skills:
                content = load_skill_md(skill)
                if content:
                    parts.append(content)
                    parts.append("---")

    project_name = project_cfg.get("project_name", "unknown")
    proj_domain = project_cfg.get("primary_domain", domain)
    stack = project_cfg.get("stack", [])
    stack_str = ", ".join(stack) if stack else "unknown"
    key_constraints = project_cfg.get("key_constraints", [])

    context_lines = [
        "## Project Context",
        f"Name: {project_name} | Stack: {stack_str} | Domain: {proj_domain}",
    ]
    if key_constraints:
        context_lines.append(f"Constraints: {'; '.join(str(c) for c in key_constraints)}")
    parts.append("\n".join(context_lines))

    if state_text.strip():
        parts.append(f"## Session State\n{state_text.strip()}")
    else:
        session_num = project_cfg.get("session_count", 0) + 1
        parts.append(f"## Session State\nSession {session_num} — starting fresh")

    parts.append(f"## Task\n{problem}")

    routing_lines = [
        "## Domain & Routing",
        f"Domain: {domain} (confidence: {confidence}, score: {score:.2f})",
        f"Suggested phase: {phase}",
        f"Active agents: {', '.join(agents)}",
        f"Active skills: {', '.join(skills)}",
    ]
    if domain == "general":
        routing_lines.append(
            "\nNote: Domain confidence is low. Consider prefixing your task with "
            "`[domain: software]` (or another domain) to force routing."
        )
    parts.append("\n".join(routing_lines))

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Generate a domain-routed prompt for your next AI session.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python agents-maker/tools/generate_prompt.py "add rate limiting"\n'
            '  python agents-maker/tools/generate_prompt.py "add tests" --phase implementation\n'
            '  python agents-maker/tools/generate_prompt.py "add tests" --full\n'
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("problem", help="What you want to work on this session.")
    parser.add_argument(
        "--phase",
        choices=list(PHASE_ALIASES.keys()),
        default=None,
        help="Force a specific lifecycle phase (default: inferred from project_state.md).",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Prepend full system prompt content (for platforms without persistent system prompts).",
    )
    parser.add_argument(
        "--compress",
        action="store_true",
        help="Apply token policy for the detected phase/domain: appends output style instruction and reports token budget.",
    )
    args = parser.parse_args()

    # Validate problem statement
    if not args.problem.strip():
        print("[ERROR] Problem statement cannot be empty.", file=sys.stderr)
        sys.exit(1)
    if len(args.problem) > MAX_PROBLEM_LENGTH:
        print(f"[ERROR] Problem statement too long ({len(args.problem)} chars, max {MAX_PROBLEM_LENGTH}).", file=sys.stderr)
        sys.exit(1)

    # Load project config
    project_yaml_path = KIT_DIR / "config" / "project.yaml"
    project_cfg = _load_yaml(project_yaml_path)
    if not project_cfg:
        print(
            "[WARN] project.yaml not found or empty. Run init_project.py first for best results.",
            file=sys.stderr,
        )

    # Load session state
    state_path = KIT_DIR / "project_state.md"
    try:
        state_text = state_path.read_text(encoding="utf-8") if state_path.exists() else ""
    except (OSError, PermissionError):
        state_text = ""

    # Detect domain; fall back to project domain if confidence is low
    domain, confidence, score = detect_domain(args.problem)
    if confidence == "low" and project_cfg.get("primary_domain"):
        domain = project_cfg["primary_domain"]
        confidence = "from-project"
        score = 0.0

    # Determine phase
    if args.phase:
        phase = PHASE_ALIASES.get(args.phase, args.phase)
    else:
        phase = infer_phase(state_path)

    agents = select_agents(phase, domain)
    skills = select_skills(agents)

    prompt_text = build_prompt(
        problem=args.problem,
        domain=domain,
        confidence=confidence,
        score=score,
        phase=phase,
        agents=agents,
        skills=skills,
        project_cfg=project_cfg,
        state_text=state_text,
        include_system=args.full,
    )

    # Apply token policy when --compress is requested
    if args.compress:
        _phase_to_workflow = {
            "task_framing":      "generic_project_lifecycle",
            "requirements":      "generic_project_lifecycle",
            "solution_design":   "feature_design",
            "implementation":    "feature_implementation",
            "review_refinement": "code_review",
            "handoff":           "generic_project_lifecycle",
        }
        try:
            from token_optimization.compressor import PolicyLoader
            _loader = PolicyLoader(KIT_DIR / "config" / "token_policies.yaml")
            _loader.load()
            _workflow = _phase_to_workflow.get(phase, "feature_implementation")
            _policy = _loader.get_workflow_policy(_workflow)
            prompt_text += (
                f"\n\n## Output Policy\n"
                f"Workflow: {_workflow}\n"
                f"Output style: {_policy.output_style}\n"
                f"Max input tokens: {_policy.max_input_tokens:,}\n"
                f"Max files in context: {_policy.max_input_files}\n"
                f"History compress after: {_policy.history_summarize_after_turns} turns"
            )
            print(
                f"  [Compress] Workflow: {_workflow} | Style: {_policy.output_style} "
                f"| Budget: {_policy.max_input_tokens:,} tokens",
                file=sys.stderr,
            )
        except ImportError as e:
            print(f"[WARN] --compress skipped (import error): {e}", file=sys.stderr)
        except Exception as e:
            print(f"[WARN] --compress skipped: {e}", file=sys.stderr)

    token_est = _token_est(prompt_text)
    project_name = project_cfg.get("project_name", "unknown")

    print("=" * 60)
    print("  PASTE THIS AS YOUR NEXT MESSAGE")
    print(f"  Project: {project_name} | Domain: {domain} ({confidence}) | Phase: {phase}")
    print(f"  Est. tokens: ~{token_est:,} | Agents: {', '.join(agents)}")
    print("=" * 60)
    print()
    print(prompt_text)
    print()
    print("=" * 60)
    print("  After the AI responds:")
    print("  -> Save any project_state.md the AI produces to agents-maker/project_state.md")
    print('  -> python agents-maker/tools/generate_prompt.py "your next task"')
    print("=" * 60)

    # Silently update session_count + last_session
    if project_yaml_path.exists():
        project_cfg["session_count"] = project_cfg.get("session_count", 0) + 1
        project_cfg["last_session"] = date.today().isoformat()
        try:
            with open(project_yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(project_cfg, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        except (OSError, PermissionError) as e:
            print(f"[WARN] Could not update session_count in project.yaml: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
