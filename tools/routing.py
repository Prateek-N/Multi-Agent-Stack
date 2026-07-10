"""
tools/routing.py

Single source of truth for lifecycle routing metadata: which specialist
agents are active for a given (phase, domain), plus phase labels and agent
role labels used across the generators.

Previously this mapping was hardcoded independently in three places
(generate_prompt.py, generate_claude_md.py, generate_platform_configs.py),
and the three copies had drifted apart. Centralizing them here makes the
routing consistent across every generated artifact (the pasted prompt,
CLAUDE.md, Copilot/Cursor rules, and the agkit config).

Two views are exposed because the tools present routing differently:
  * phase_agents(phase, domain)  -> the phase's agent list as declared in the
    table (used where the orchestrator is mentioned separately, e.g. CLAUDE.md).
  * active_agents(phase, domain) -> orchestrator-first, deduplicated (used for
    the "Active agents" line of a generated prompt).
"""

from __future__ import annotations

# Phase -> domain -> agents. "_all" is the default for domains without an override.
PHASE_AGENTS: dict[str, dict[str, list[str]]] = {
    "task_framing":     {"_all": ["orchestrator"]},
    "requirements":     {"_all": ["orchestrator", "architect_agent"]},
    "solution_design":  {
        "_all":          ["architect_agent"],
        "software":      ["architect_agent", "ui_agent"],
        "product_design": ["architect_agent", "ui_agent", "ux_agent"],
        "marketing":     ["architect_agent", "ux_agent"],
    },
    "implementation":   {
        "_all":          ["execution_agent"],
        "software":      ["code_agent"],
        "data_analytics": ["code_agent"],
    },
    "review_refinement": {
        "_all":          ["reviewer_agent"],
        "software":      ["reviewer_agent", "code_agent"],
        "product_design": ["reviewer_agent", "ui_agent", "ux_agent"],
        "marketing":     ["reviewer_agent", "ux_agent"],
    },
    "handoff":          {"_all": ["orchestrator", "execution_agent"]},
}

PHASE_LABELS: dict[str, str] = {
    "task_framing":     "Task Framing",
    "requirements":     "Requirements",
    "solution_design":  "Solution Design",
    "implementation":   "Implementation",
    "review_refinement": "Review & Refinement",
    "handoff":          "Handoff",
    # aliases accepted by generate_prompt.py
    "framing":          "Task Framing",
    "design":           "Solution Design",
    "implement":        "Implementation",
    "review":           "Review & Refinement",
}

AGENT_ROLES: dict[str, str] = {
    "orchestrator":      "routing",
    "architect_agent":   "design",
    "code_agent":        "implementation",
    "execution_agent":   "execution",
    "ui_agent":          "UI",
    "ux_agent":          "UX",
    "reviewer_agent":    "QA",
    "compression_agent": "compression",
    "brain":             "brainstorm",
    "planpro":           "planning",
}


def phase_agents(phase: str, domain: str) -> list[str]:
    """Agents declared for (phase, domain), falling back to the phase's `_all` list."""
    phase_map = PHASE_AGENTS.get(phase, {"_all": ["orchestrator"]})
    return list(phase_map.get(domain, phase_map["_all"]))


def active_agents(phase: str, domain: str) -> list[str]:
    """Orchestrator-first, de-duplicated agent list for a generated prompt."""
    agents = ["orchestrator"]
    for a in phase_agents(phase, domain):
        if a not in agents:
            agents.append(a)
    return agents


def domain_agents(domain: str) -> list[str]:
    """Every agent this domain uses across all phases (union), orchestrator first.

    Used to scope a self-contained/Direct-Task-Mode system prompt: it must carry
    the domain's implementation + review specialists (and their skills), not just
    the phase-0 orchestrator — otherwise the skills that add value get dropped.
    Still excludes agents from other domains, so it stays smaller than the full kit.
    """
    seen: list[str] = ["orchestrator"]
    for phase in PHASE_AGENTS:
        for a in active_agents(phase, domain):
            if a not in seen:
                seen.append(a)
    return seen
