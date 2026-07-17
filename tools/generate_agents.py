#!/usr/bin/env python3
"""
generate_agents.py — Emit native /command files for every supported AI tool.

Turns the agents-maker roster into the slash-command / workflow / prompt format
each tool actually reads, so after install a user can type `/brain`, `/planpro`,
`/code`, … in the chat box of whichever tool they use:

    Antigravity (IDE)  ->  .agent/workflows/<name>.md      (description: frontmatter)
    Claude Code        ->  .claude/commands/<name>.md      (+ .claude/agents/<name>.md)
    Cursor (1.6+)      ->  .cursor/commands/<name>.md       (plain markdown)
    Copilot (VS Code)  ->  .github/prompts/<name>.prompt.md (${input:task})

Every file is SELF-CONTAINED — it embeds the full agent spec — so commands keep
working even when the bulky `agents-maker/` folder is gitignored or removed.

Non-destructive by default: existing same-named files are skipped. Use --force.

Usage:
    python agents-maker/tools/generate_agents.py                 # -> <project> tool dirs
    python agents-maker/tools/generate_agents.py --project /path # -> /path tool dirs
    python agents-maker/tools/generate_agents.py --template      # -> agents-maker/dist/ (shipped copy)
    python agents-maker/tools/generate_agents.py --dry-run
"""

from __future__ import annotations

__version__ = "2.0.0"

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

# Full autonomy: agents may read, edit, write, and run commands (see README safety note).
AGENT_TOOLS = "Read, Grep, Glob, Edit, Write, Bash"

# command name -> agent id (filename stem in agents/).
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
    one = " ".join(text.split())
    return one[: limit - 1] + "…" if len(one) > limit else one


def _description(agent_id: str, cfg: dict) -> str:
    return _flatten(str(cfg.get(agent_id, {}).get("description", ""))) or f"agents-maker {agent_id} agent"


def _body(agent_id: str, kit_dir: Path) -> str:
    """The full agent spec — embedded so the command works without the kit folder."""
    return (kit_dir / "agents" / f"{agent_id}.md").read_text(encoding="utf-8").strip()


# --- per-tool builders -----------------------------------------------------

def build_claude_subagent(cmd: str, agent_id: str, cfg: dict, kit_dir: Path) -> str:
    return (
        "---\n"
        f"name: {cmd}\n"
        f"description: {_description(agent_id, cfg)}\n"
        f"tools: {AGENT_TOOLS}\n"
        "model: inherit\n"
        "---\n\n"
        f"{_body(agent_id, kit_dir)}\n"
    )


def build_claude_command(cmd: str, agent_id: str, cfg: dict, kit_dir: Path) -> str:
    return (
        "---\n"
        f"description: {_description(agent_id, cfg)}\n"
        "---\n"
        f"# /{cmd}\n\n"
        "$ARGUMENTS\n\n"
        f"Use the `{cmd}` subagent (agents-maker) to handle the request above. If it is a "
        "self-contained task, deliver the finished artifact directly (Direct Task Mode); otherwise "
        "ask one clarifying question first. End with the [Companion] next-steps block.\n"
    )


def build_antigravity(cmd: str, agent_id: str, cfg: dict, kit_dir: Path) -> str:
    return (
        "---\n"
        f"description: {_description(agent_id, cfg)}\n"
        "---\n"
        f"# /{cmd}\n\n"
        f"Act as the **{cmd}** agent specified below. The user's request follows this command in the "
        "chat — if no request was given, ask for one. Deliver exactly per the agent's Output Contract, "
        "then end with the [Companion] next-steps block.\n\n"
        "---\n\n"
        f"{_body(agent_id, kit_dir)}\n"
    )


def build_cursor(cmd: str, agent_id: str, cfg: dict, kit_dir: Path) -> str:
    return (
        f"# /{cmd} — {_description(agent_id, cfg)}\n\n"
        f"Act as the **{cmd}** agent specified below. Treat any text after the command as the task; "
        "if none, ask for one. Follow the agent's Output Contract and end with the [Companion] "
        "next-steps block.\n\n"
        "---\n\n"
        f"{_body(agent_id, kit_dir)}\n"
    )


def build_copilot(cmd: str, agent_id: str, cfg: dict, kit_dir: Path) -> str:
    return (
        "---\n"
        f"description: {_description(agent_id, cfg)}\n"
        "---\n"
        f"Act as the **{cmd}** agent specified below. Task: ${{input:task}}\n"
        "If no task is given, ask for one. Follow the agent's Output Contract and end with the "
        "[Companion] next-steps block.\n\n"
        "---\n\n"
        f"{_body(agent_id, kit_dir)}\n"
    )


# (template subdir under dist/, project subdir under root, filename pattern, builder)
OUTPUTS = [
    ("claude/agents",         ".claude/agents",   "{cmd}.md",        build_claude_subagent),
    ("claude/commands",       ".claude/commands", "{cmd}.md",        build_claude_command),
    ("antigravity/workflows", ".agent/workflows", "{cmd}.md",        build_antigravity),
    ("cursor/commands",       ".cursor/commands", "{cmd}.md",        build_cursor),
    ("copilot/prompts",       ".github/prompts",  "{cmd}.prompt.md", build_copilot),
]


def generate(dest_root: Path, kit_dir: Path, *, template: bool = False,
             force: bool = False, dry_run: bool = False) -> tuple[list[str], list[str]]:
    """Write command files for all tools under dest_root. Returns (written, skipped) rel paths."""
    cfg = load_yaml(kit_dir / "config" / "agents.yaml").get("agents", {})
    written: list[str] = []
    skipped: list[str] = []
    for tmpl_sub, proj_sub, fname, builder in OUTPUTS:
        subdir = tmpl_sub if template else proj_sub
        for cmd, agent_id in COMMANDS.items():
            path = dest_root / subdir / fname.format(cmd=cmd)
            rel = f"{subdir}/{fname.format(cmd=cmd)}"
            if path.exists() and not force:
                skipped.append(rel)
                continue
            if not dry_run:
                atomic_write(path, builder(cmd, agent_id, cfg, kit_dir))
            written.append(rel)
    return written, skipped


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Generate native /command files for Antigravity, Claude Code, Cursor, and Copilot.")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    ap.add_argument("--project", help="Project root; writes tool dirs there (default: parent of agents-maker/).")
    ap.add_argument("--template", action="store_true", help="Write the shipped template copy to agents-maker/dist/ instead of a project.")
    ap.add_argument("--force", action="store_true", help="Overwrite existing files (default: skip existing).")
    ap.add_argument("--dry-run", action="store_true", help="List what would be written without writing.")
    args = ap.parse_args()

    if args.template:
        dest = KIT_DIR / "dist"
    else:
        dest = Path(args.project).resolve() if args.project else KIT_DIR.parent

    written, skipped = generate(dest, KIT_DIR, template=args.template, force=args.force, dry_run=args.dry_run)

    tag = "[dry-run] would write" if args.dry_run else "wrote"
    print(f"{tag} {len(written)} file(s) under {dest}")
    for r in written:
        print(f"  + {r}")
    if skipped:
        print(f"skipped {len(skipped)} existing file(s) (use --force to overwrite)")
    if not args.template:
        cmds = ", ".join(f"/{c}" for c in COMMANDS)
        print(f"\nCommands available in this project: {cmds}")


if __name__ == "__main__":
    main()
