#!/usr/bin/env python3
"""
demo/app.py — agents-maker live demo for HuggingFace Spaces.

Shows domain detection scoring, agent routing, and a full structured
prompt block — all in the browser, no setup required.
"""

import sys
from pathlib import Path

DEMO_DIR = Path(__file__).parent
KIT_DIR  = DEMO_DIR.parent
if str(KIT_DIR) not in sys.path:
    sys.path.insert(0, str(KIT_DIR))

try:
    import gradio as gr
except ImportError:
    print("[ERROR] gradio not installed. Run: pip install gradio", file=sys.stderr)
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("[ERROR] pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Domain config — loaded from kit if available, otherwise inline fallback
# ---------------------------------------------------------------------------

_INLINE_DOMAINS: dict[str, dict] = {
    "software":      {"strong": ["api", "code", "function", "class", "refactor", "test", "database", "endpoint", "deploy", "bug", "service", "backend", "repository", "migration"], "weak": ["system", "performance", "cache", "scale", "module"]},
    "content":       {"strong": ["blog", "article", "write", "draft", "copy", "post", "newsletter", "content", "editorial"], "weak": ["audience", "tone", "voice", "publish", "seo"]},
    "research":      {"strong": ["research", "literature review", "survey", "study", "paper", "academic", "hypothesis", "citation", "methodology"], "weak": ["data", "findings", "evidence", "analysis"]},
    "data_analytics":{"strong": ["dashboard", "metrics", "analytics", "pipeline", "sql", "dataset", "visualization", "funnel", "kpi", "report"], "weak": ["trend", "chart", "bi", "etl"]},
    "product_design":{"strong": ["product", "feature", "user story", "wireframe", "persona", "onboarding", "prd", "roadmap"], "weak": ["ux", "ui", "flow", "prototype", "design"]},
    "marketing":     {"strong": ["campaign", "marketing", "launch", "gtm", "go-to-market", "brand", "conversion", "ad", "creative"], "weak": ["growth", "funnel", "lead", "channel", "audience"]},
    "ops_process":   {"strong": ["runbook", "sop", "process", "workflow", "incident", "on-call", "raci", "procedure", "escalation", "failover"], "weak": ["checklist", "team", "handoff", "operations"]},
    "general":       {"strong": [], "weak": []},
}

_DOMAIN_AGENTS: dict[str, list[str]] = {
    "software":       ["orchestrator", "architect_agent", "code_agent", "reviewer_agent"],
    "content":        ["orchestrator", "architect_agent", "execution_agent", "reviewer_agent"],
    "research":       ["orchestrator", "architect_agent", "execution_agent", "reviewer_agent"],
    "data_analytics": ["orchestrator", "architect_agent", "code_agent", "reviewer_agent"],
    "product_design": ["orchestrator", "architect_agent", "ui_agent", "ux_agent", "reviewer_agent"],
    "marketing":      ["orchestrator", "architect_agent", "execution_agent", "ux_agent", "reviewer_agent"],
    "ops_process":    ["orchestrator", "architect_agent", "execution_agent", "reviewer_agent"],
    "general":        ["orchestrator"],
}

_DOMAIN_SKILLS: dict[str, list[str]] = {
    "software":       ["analyze_repo", "review_code", "write_tests", "suggest_next"],
    "content":        ["improve_copy", "summarize_history", "suggest_next"],
    "research":       ["analyze_repo", "compare_approaches", "summarize_history"],
    "data_analytics": ["define_data_schema", "analyze_repo", "suggest_next"],
    "product_design": ["review_layout", "improve_copy", "compare_approaches"],
    "marketing":      ["improve_copy", "compare_approaches", "suggest_next"],
    "ops_process":    ["write_process_map", "summarize_history", "suggest_next"],
    "general":        ["suggest_next", "compare_approaches"],
}


def _load_domain_config() -> tuple[dict, dict]:
    """Load domain signals and settings from kit config if available."""
    cfg_path = KIT_DIR / "config" / "domain_profiles.yaml"
    try:
        with open(cfg_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        return raw.get("domains", {}), raw.get("detection_settings", {})
    except Exception:
        return {}, {}


_DOMAINS_CFG, _SETTINGS = _load_domain_config()
_CONF_THRESHOLD = _SETTINGS.get("confidence_threshold", 0.40)
_AMB_THRESHOLD  = _SETTINGS.get("ambiguity_threshold", 0.10)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _score_all(task: str) -> dict[str, float]:
    msg = task.lower()
    scores: dict[str, float] = {}
    for domain, fallback in _INLINE_DOMAINS.items():
        if domain == "general":
            scores["general"] = 0.0
            continue
        if domain in _DOMAINS_CFG:
            sigs  = _DOMAINS_CFG[domain].get("detection_signals", {})
            strong = sigs.get("strong", [])
            weak   = sigs.get("weak", [])
        else:
            strong = fallback["strong"]
            weak   = fallback["weak"]
        s = sum(1.0 for sig in strong if sig in msg)
        w = sum(0.4 for sig in weak   if sig in msg)
        scores[domain] = round((s + w) / 3, 3)
    return scores


def _top_domain(scores: dict[str, float]) -> tuple[str, str, float]:
    ranked = sorted(
        [(d, s) for d, s in scores.items() if d != "general"],
        key=lambda x: -x[1],
    )
    top_d, top_s = ranked[0]
    _, sec_s = ranked[1] if len(ranked) > 1 else ("", 0.0)
    if top_s < _CONF_THRESHOLD:
        return "general", "low", top_s
    conf = "medium" if (top_s - sec_s) < _AMB_THRESHOLD else "high"
    return top_d, conf, top_s


# ---------------------------------------------------------------------------
# Demo logic
# ---------------------------------------------------------------------------

def run_demo(task: str) -> tuple[str, str, str]:
    task = task.strip()
    if not task:
        empty = "*Enter a task to see results.*"
        return empty, empty, ""

    scores = _score_all(task)
    top_d, conf, top_s = _top_domain(scores)
    agents = _DOMAIN_AGENTS.get(top_d, ["orchestrator"])
    skills = _DOMAIN_SKILLS.get(top_d, ["suggest_next"])

    # Domain scores table
    all_sorted = sorted(scores.items(), key=lambda x: -x[1])
    rows = []
    for d, s in all_sorted:
        filled = int(s * 10)
        bar    = "█" * filled + "░" * max(0, 10 - filled)
        marker = "  ← **detected**" if d == top_d else ""
        rows.append(f"| `{d}` | {s:.2f} | `{bar}`{marker} |")
    scores_md = (
        f"| Domain | Score | Signal strength |\n"
        f"|---|---|---|\n"
        + "\n".join(rows)
    )

    # Routing panel
    routing_md = (
        f"**Detected domain**: `{top_d}`  (confidence: **{conf}**)\n\n"
        f"**Active agents** ({len(agents)}):\n"
        + "".join(f"- `{a}`\n" for a in agents)
        + f"\n**Active skills** ({len(skills)}):\n"
        + "".join(f"- `{s}`\n" for s in skills)
        + "\n\n*Domain and agents are auto-detected — you never need to specify them.*"
    )

    # Generated prompt block
    task_display = task if len(task) <= 80 else task[:77] + "..."
    prompt_block = (
        f"{'='*60}\n"
        f"  PASTE THIS AS YOUR NEXT MESSAGE\n"
        f"  Domain: {top_d} ({conf}) | Phase: task_framing\n"
        f"  Active agents: {', '.join(agents[:3])}\n"
        f"{'='*60}\n\n"
        f"## Project Context\n"
        f"Name: my-project | Stack: (your stack here) | Domain: {top_d}\n\n"
        f"## Session State\n"
        f"Session 1 — starting fresh\n\n"
        f"## Task\n"
        f"{task}\n\n"
        f"## Domain & Routing\n"
        f"Domain: {top_d} (confidence: {conf}, score: {top_s:.2f})\n"
        f"Suggested phase: task_framing\n"
        f"Active agents: {', '.join(agents)}\n"
        f"Active skills: {', '.join(skills)}\n"
        f"{'='*60}\n\n"
        f"# To generate this for your own project:\n"
        f"# git clone https://github.com/Prateek-N/Multi-Agent-Stack.git agents-maker\n"
        f'# python agents-maker/tools/generate_prompt.py "{task_display}"\n'
    )

    return scores_md, routing_md, prompt_block


# ---------------------------------------------------------------------------
# Gradio interface
# ---------------------------------------------------------------------------

EXAMPLES = [
    ["Add Redis sliding-window rate limiting to a FastAPI auth service"],
    ["Write a go-to-market brief for a developer tool launching on Product Hunt"],
    ["Design an on-call runbook for PostgreSQL primary failover with Patroni"],
    ["Build a SaaS subscription analytics dashboard with MRR and churn metrics"],
    ["Audit the settings page UX of a B2B SaaS app for a high Billing bounce rate"],
    ["Write a literature review on transformer efficiency improvements since 2017"],
]

with gr.Blocks(title="agents-maker — Live Demo", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        "# 🤖 agents-maker\n"
        "### Multi-LLM · Multi-Agent · Any Project · Any AI Tool\n\n"
        "Type any task. See **domain detection scoring**, **agent routing**, "
        "and the **full structured prompt block** — instantly. No setup, no account.\n\n"
        "> Clone it: `git clone https://github.com/Prateek-N/Multi-Agent-Stack.git agents-maker`"
    )

    with gr.Row():
        task_box = gr.Textbox(
            label="Describe your task",
            placeholder=(
                "e.g. 'Add Redis rate limiting to FastAPI auth service' "
                "or 'Write a GTM brief for Product Hunt launch'"
            ),
            lines=2,
            scale=5,
        )
        go_btn = gr.Button("Detect →", variant="primary", scale=1, min_width=100)

    gr.Examples(examples=EXAMPLES, inputs=task_box, label="Try an example")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Domain Detection")
            scores_out = gr.Markdown(value="*Enter a task above.*")
        with gr.Column(scale=1):
            gr.Markdown("## Agent Routing")
            routing_out = gr.Markdown(value="*Enter a task above.*")

    gr.Markdown("## Generated Prompt Block")
    gr.Markdown(
        "*Copy this and paste it as your first message to Claude, ChatGPT, or any LLM. "
        "The AI will route to the right specialist agent automatically.*"
    )
    prompt_out = gr.Textbox(
        label="",
        lines=16,
        show_copy_button=True,
        interactive=False,
        placeholder="Your generated prompt will appear here.",
    )

    gr.Markdown(
        "---\n"
        "**Get the full kit:**\n"
        "```bash\n"
        "git clone https://github.com/Prateek-N/Multi-Agent-Stack.git agents-maker\n"
        "python agents-maker/tools/init_project.py          # one-time setup\n"
        "python agents-maker/tools/generate_prompt.py \"your task\"  # before every session\n"
        "```\n\n"
        "[📖 Cookbook](https://github.com/Prateek-N/Multi-Agent-Stack/tree/main/cookbook)  ·  "
        "[🔁 GitHub Action](https://github.com/Prateek-N/Multi-Agent-Stack/tree/main/actions/review-pr)  ·  "
        "[📄 README](https://github.com/Prateek-N/Multi-Agent-Stack#readme)  ·  "
        "[MIT License](https://github.com/Prateek-N/Multi-Agent-Stack/blob/main/LICENSE)"
    )

    go_btn.click(fn=run_demo, inputs=task_box, outputs=[scores_out, routing_out, prompt_out])
    task_box.submit(fn=run_demo, inputs=task_box, outputs=[scores_out, routing_out, prompt_out])

if __name__ == "__main__":
    demo.launch()
