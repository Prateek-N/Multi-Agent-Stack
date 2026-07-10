#!/usr/bin/env python3
"""
generate_claude_agents.py — Emit Claude Code subagents + slash commands.

Turns the agents-maker roster into native Claude Code files so a user can clone
the kit into their project and immediately invoke named agents:

    /brain      brainstorm the whole project (options + trade-offs + recommendation)
    /planpro    produce the best-possible implementation plan
    /architect /code /execute /ui /ux /review /orchestrate /compress

For each agent it writes:
  <dest>/.claude/agents/<name>.md    — subagent (frontmatter + the agent spec body)
  <dest>/.claude/commands/<name>.md  — slash command that invokes the subagent

Non-destructive by default: existing same-named files are skipped (never clobber
a user's own agents/commands). Use --force to overwrite.

Usage:
    python agents-maker/tools/generate_claude_agents.py                 # -> <project>/.claude
    python agents-maker/tools/generate_claude_agents.py --project /path # -> /path/.claude
    python agents-maker/tools/generate_claude_agents.py --template      # -> agents-maker/claude (shipped copy)
    python agents-maker/tools/generate_claude_agents.py --dry-run
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
    from tools._core import atomic_write, load_yaml
except ImportError:
    from _core import atomic_write, load_yaml

# Full autonomy: agents may read, edit, write, and run commands.
AGENT_TOOLS = "Read, Grep, Glob, Edit, Write, Bash"

# command name -> agent id (filename stem in agents/). The command/subagent use
# the short, clean name; the body comes from the (possibly _agent-suffixed) spec.
COMMANDS: dict[str, str] = {
    "brain":       "brain",
    "planpro":     "planpro",
    "orchestrate": "orchestrator",
    "architect":   "architect_agent",
    "code":        "code_agent",
    "execute":     "execution_agent",
    "ui":          "ui_agent",
    "ux":          "ux_agent",
    "review":      "reviewer_agent",
    "compress":    "compression_agent",
}


def _flatten(text: str, limit: int = 300) -> str:
    """Collapse whitespace to a single line (YAML-frontmatter-safe) and cap length."""
    one = " ".join(text.split())
    return one[: limit - 1] + "…" if len(one) > limit else one


def _description(agent_id: str, agents_cfg: dict) -> str:
    desc = _flatten(str(agents_cfg.get(agent_id, {}).get("description", "")))
    return desc or f"agents-maker {agent_id} agent"


def build_subagent(cmd: str, agent_id: str, agents_cfg: dict, kit_dir: Path) -> str:
    body = (kit_dir / "agents" / f"{agent_id}.md").read_text(encoding="utf-8").strip()
    return (
        "---\n"
        f"name: {cmd}\n"
        f"description: {_description(agent_id, agents_cfg)}\n"
        f"tools: {AGENT_TOOLS}\n"
        "model: inherit\n"
        "---\n\n"
        f"{body}\n"
    )


def build_command(cmd: str, agent_id: str, agents_cfg: dict) -> str:
    return (
        "---\n"
        f"description: {_description(agent_id, agents_cfg)}\n"
        "---\n"
        f"# /{cmd}\n\n"
        "$ARGUMENTS\n\n"
        "## Task\n"
        f"Use the `{cmd}` subagent (agents-maker) to handle the request above.\n\n"
        "CONTEXT:\n"
        "- Project config, if present: `agents-maker/config/project.yaml` — read it for "
        "domain, stack, and constraints before acting.\n"
        "- User request: $ARGUMENTS\n\n"
        f"Follow the `{cmd}` agent's output contract. If the request is a self-contained "
        "task, deliver the finished artifact directly (Direct Task Mode) — do not ask for "
        "project context you can infer. End with the [Companion] next-steps block.\n"
    )


def generate(dest_claude: Path, kit_dir: Path, *, force: bool = False, dry_run: bool = False) -> tuple[list[str], list[str]]:
    """Write subagents + commands under dest_claude. Returns (written, skipped) rel paths."""
    agents_cfg = load_yaml(kit_dir / "config" / "agents.yaml").get("agents", {})
    written: list[str] = []
    skipped: list[str] = []

    for cmd, agent_id in COMMANDS.items():
        targets = [
            (dest_claude / "agents" / f"{cmd}.md", build_subagent(cmd, agent_id, agents_cfg, kit_dir)),
            (dest_claude / "commands" / f"{cmd}.md", build_command(cmd, agent_id, agents_cfg)),
        ]
        for path, content in targets:
            rel = f"{path.parent.name}/{path.name}"
            if path.exists() and not force:
                skipped.append(rel)
                continue
            if dry_run:
                written.append(rel)
                continue
            atomic_write(path, content)
            written.append(rel)

    return written, skipped


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Generate Claude Code subagents + slash commands from the agents-maker roster.")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    ap.add_argument("--project", help="Project root; writes <root>/.claude/ (default: parent of agents-maker/).")
    ap.add_argument("--template", action="store_true", help="Write the shipped template copy to agents-maker/claude/ instead of a project's .claude/.")
    ap.add_argument("--force", action="store_true", help="Overwrite existing files (default: skip existing).")
    ap.add_argument("--dry-run", action="store_true", help="List what would be written without writing.")
    args = ap.parse_args()

    if args.template:
        dest = KIT_DIR / "claude"
    else:
        root = Path(args.project).resolve() if args.project else KIT_DIR.parent
        dest = root / ".claude"

    written, skipped = generate(dest, KIT_DIR, force=args.force, dry_run=args.dry_run)

    tag = "[dry-run] would write" if args.dry_run else "wrote"
    print(f"{tag} {len(written)} file(s) under {dest}")
    for r in written:
        print(f"  + {r}")
    if skipped:
        print(f"skipped {len(skipped)} existing file(s) (use --force to overwrite):")
        for r in skipped:
            print(f"  = {r}")
    if not args.dry_run and not args.template:
        cmds = ", ".join(f"/{c}" for c in COMMANDS)
        print(f"\nCommands available in this project: {cmds}")


if __name__ == "__main__":
    main()
