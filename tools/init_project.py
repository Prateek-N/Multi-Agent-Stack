#!/usr/bin/env python3
"""
init_project.py — One-time project bootstrap for agents-maker Companion Mode.

Usage:
    python agents-maker/tools/init_project.py
    python agents-maker/tools/init_project.py --path /your/project
    python agents-maker/tools/init_project.py --update   # regenerate system_prompt.md
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — allow imports from context_loaders and config
# ---------------------------------------------------------------------------

__version__ = "1.0.0"

SCRIPT_DIR = Path(__file__).resolve().parent       # agents-maker/tools/
KIT_DIR = SCRIPT_DIR.parent                        # agents-maker/
sys.path.insert(0, str(KIT_DIR))

try:
    from context_loaders.project_summary import build_summary
    from context_loaders.repo_tree import walk_tree
except ImportError as e:
    print(f"[ERROR] Could not import context_loaders: {e}", file=sys.stderr)
    print("[ERROR] Make sure you're running from the project root and agents-maker/ is present.", file=sys.stderr)
    sys.exit(1)

try:
    from tools._core import atomic_write, atomic_write_yaml, load_yaml, source_hash
    from tools.domain_utils import detect_domain as _detect_domain
except ImportError:
    from _core import atomic_write, atomic_write_yaml, load_yaml, source_hash
    from domain_utils import detect_domain as _detect_domain


def detect_domain(summary_text: str) -> tuple[str, str]:
    return _detect_domain(summary_text, kit_dir=KIT_DIR)  # type: ignore[return-value]


def detect_stack_from_summary(summary_text: str) -> list[str]:
    for line in summary_text.splitlines():
        if line.startswith("**Stack**:"):
            parts = line.split(":", 1)[1].strip()
            if parts and parts != "Unknown":
                return [p.strip() for p in parts.split(",") if p.strip()]
    return []


# ---------------------------------------------------------------------------
# YAML injection guard — reject strings with characters that break yaml.dump
# ---------------------------------------------------------------------------

_YAML_UNSAFE = frozenset({'"', "'", ':', '!', '{', '}', '[', ']', '\\', '\n', '\r'})


def _sanitize_yaml_str(value: str, field: str) -> str:
    bad = [c for c in value if c in _YAML_UNSAFE]
    if bad:
        safe = "".join(c for c in value if c not in _YAML_UNSAFE)
        print(
            f"[WARN] {field!r} contained unsafe YAML characters {sorted(set(bad))} — stripped.",
            file=sys.stderr,
        )
        return safe
    return value


# ---------------------------------------------------------------------------
# system_prompt.md builder
# ---------------------------------------------------------------------------

def build_system_prompt(project_name: str, domain: str, stack: list[str]) -> str:
    agents_dir = KIT_DIR / "agents"
    agent_order = [
        "orchestrator.md",
        "brain.md",
        "planpro.md",
        "architect_agent.md",
        "code_agent.md",
        "execution_agent.md",
        "ui_agent.md",
        "ux_agent.md",
        "reviewer_agent.md",
        "compression_agent.md",
    ]
    skill_count = len(list((KIT_DIR / "skills").glob("*.md"))) if (KIT_DIR / "skills").exists() else 0
    src_hash = source_hash(KIT_DIR)
    version_header = (
        f"# agents-maker system_prompt.md\n"
        f"# Version: 1.0 | Generated: {date.today().isoformat()} | Source hash: {src_hash}\n"
        f"# Regenerate: python agents-maker/tools/init_project.py --update\n"
        f"# Contains: {len(agent_order)} agents + {skill_count} skills\n"
        f"#\n"
        f"# [Companion] INSTRUCTION (always active):\n"
        f"# After every response append a [Companion] block:\n"
        f"#   ---\n"
        f"#   [Companion] Phase: <phase> | Domain: <domain> | Est. token budget used: ~N%\n"
        f"#   What to do next (pick one):\n"
        f"#   [Recommended] A: <action>  Command: python agents-maker/tools/generate_prompt.py \"...\"\n"
        f"#   B: <action>\n"
        f"#   C: <action>\n"
        f"#   ---\n"
    )
    sections: list[str] = [version_header]

    for fname in agent_order:
        fpath = agents_dir / fname
        if fpath.exists():
            try:
                content = fpath.read_text(encoding="utf-8").strip()
                sections.append(content)
                sections.append("---")
            except (PermissionError, OSError) as e:
                print(f"[WARN] Could not read {fpath}: {e}", file=sys.stderr)

    skills_dir = KIT_DIR / "skills"
    if skills_dir.exists():
        for skill_file in sorted(skills_dir.glob("*.md")):
            try:
                content = skill_file.read_text(encoding="utf-8").strip()
                sections.append(content)
                sections.append("---")
            except (PermissionError, OSError) as e:
                print(f"[WARN] Could not read {skill_file}: {e}", file=sys.stderr)

    stack_str = ", ".join(stack) if stack else "unknown"
    context_block = (
        f"## Project Context\n\n"
        f"Project name: {project_name}  \n"
        f"Primary domain: {domain}  \n"
        f"Stack: {stack_str}  \n"
        f"Initialized: {date.today().isoformat()}  \n"
    )
    sections.append(context_block)

    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# project_state.md template
# ---------------------------------------------------------------------------

STATE_TEMPLATE = """\
# Project State
schema_version: "1.0"

## Current Phase
task_framing

## Domain
(detected at init — override here if needed)

## Approved Artifacts
(none yet)

## Open Decisions
(none yet)

## Build Log
(empty)

## Session Notes
(add notes after each session)
"""

VALID_DOMAINS = [
    "software", "content", "research", "data_analytics",
    "product_design", "marketing", "ops_process", "general",
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Bootstrap agents-maker Companion Mode for a project.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python agents-maker/tools/init_project.py\n"
            "  python agents-maker/tools/init_project.py --path /my/project\n"
            "  python agents-maker/tools/init_project.py --update  # regenerate system_prompt.md\n"
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--path",
        help="Project root directory (default: parent of agents-maker/)",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Regenerate system_prompt.md even if it already exists.",
    )
    parser.add_argument(
        "--claude-md",
        action="store_true",
        help="Also generate CLAUDE.md in the project root (Claude Code integration).",
    )
    parser.add_argument(
        "--platforms",
        action="store_true",
        help=(
            "Generate config files for ALL supported platforms: "
            "Claude Code (CLAUDE.md), GitHub Copilot (.github/copilot-instructions.md), "
            "Cursor (.cursor/rules), Antigravity (.agkit/agents.yaml). "
            "Supersedes --claude-md."
        ),
    )
    args = parser.parse_args()

    # Resolve project root
    if args.path:
        project_root = Path(args.path).resolve()
    else:
        project_root = KIT_DIR.parent

    if not project_root.exists():
        print(f"[ERROR] Project root does not exist: {project_root}", file=sys.stderr)
        sys.exit(1)
    if not project_root.is_dir():
        print(f"[ERROR] Path is not a directory: {project_root}", file=sys.stderr)
        sys.exit(1)

    project_name = project_root.name
    print(f"\nInitializing agents-maker for: {project_root}")
    print("-" * 60)

    # Step 1 — Scan project
    print("Scanning project...")
    try:
        summary_text = build_summary(project_root)
        walk_tree(project_root, max_depth=3, show_all=False)
    except Exception as e:
        print(f"[WARN] Project scan encountered an error: {e}", file=sys.stderr)
        summary_text = ""

    # Step 2 — Detect domain
    detected_domain, confidence = detect_domain(summary_text)
    stack = detect_stack_from_summary(summary_text)

    print(f"Detected domain : {detected_domain} (confidence: {confidence})")
    print(f"Detected stack  : {', '.join(stack) if stack else 'unknown'}")

    # Step 3 — Confirm or override domain
    print(f"\nValid domains: {', '.join(VALID_DOMAINS)}")
    try:
        user_input = input(
            f"Press Enter to accept '{detected_domain}', or type a domain to override: "
        ).strip().lower()
    except (EOFError, KeyboardInterrupt):
        user_input = ""

    # Validate user input strictly
    if not user_input:
        final_domain = detected_domain
    elif len(user_input) > 50:
        print(f"[WARN] Input too long — keeping '{detected_domain}'", file=sys.stderr)
        final_domain = detected_domain
    elif not user_input.replace("_", "").isalpha():
        print(f"[WARN] Invalid domain name (letters and underscores only) — keeping '{detected_domain}'", file=sys.stderr)
        final_domain = detected_domain
    elif user_input in VALID_DOMAINS:
        final_domain = user_input
        print(f"Using domain: {final_domain}")
    else:
        print(f"[WARN] '{user_input}' is not a recognized domain — keeping '{detected_domain}'", file=sys.stderr)
        final_domain = detected_domain

    # Step 4 — Write config/project.yaml
    config_dir = KIT_DIR / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    project_yaml_path = config_dir / "project.yaml"

    # Preserve session_count if updating
    existing_cfg = load_yaml(project_yaml_path)
    session_count = existing_cfg.get("session_count", 0) if args.update else 0
    created_at = existing_cfg.get("created_at", date.today().isoformat()) if args.update else date.today().isoformat()

    safe_name = _sanitize_yaml_str(project_name, "project_name")
    safe_stack = [_sanitize_yaml_str(s, f"stack[{i}]") for i, s in enumerate(stack)]

    project_cfg = {
        "project_name": safe_name,
        "created_at": created_at,
        "primary_domain": final_domain,
        "stack": safe_stack,
        "key_constraints": existing_cfg.get("key_constraints", []) if args.update else [],
        "session_count": session_count,
        "last_session": existing_cfg.get("last_session") if args.update else None,
    }
    try:
        atomic_write_yaml(project_yaml_path, project_cfg)
    except OSError as e:
        print(f"[ERROR] Could not write project.yaml: {e}", file=sys.stderr)
        sys.exit(1)

    # Step 5 — Generate system_prompt.md
    system_prompt_path = KIT_DIR / "system_prompt.md"
    if not system_prompt_path.exists() or args.update:
        system_prompt_text = build_system_prompt(project_name, final_domain, stack)
        try:
            atomic_write(system_prompt_path, system_prompt_text)
        except OSError as e:
            print(f"[ERROR] Could not write system_prompt.md: {e}", file=sys.stderr)
            sys.exit(1)
        char_count = len(system_prompt_text)
        token_estimate = char_count // 4
        system_prompt_status = f"(~{char_count:,} chars, ~{token_estimate:,} tokens)"
        system_prompt_done = True
    else:
        system_prompt_status = "(already exists — use --update to regenerate)"
        system_prompt_done = False

    # Step 6 — Create project_state.md if absent
    state_path = KIT_DIR / "project_state.md"
    if not state_path.exists():
        try:
            atomic_write(state_path, STATE_TEMPLATE)
            state_created = True
        except OSError as e:
            print(f"[ERROR] Could not write project_state.md: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        state_created = False

    # Step 7 — Print summary
    print()
    print("=" * 60)
    try:
        print(f"  [DONE] {project_yaml_path.relative_to(KIT_DIR.parent)}")
        tag = "[DONE]" if system_prompt_done else "[SKIP]"
        print(f"  {tag} {system_prompt_path.relative_to(KIT_DIR.parent)}  {system_prompt_status}")
        if state_created:
            print(f"  [DONE] {state_path.relative_to(KIT_DIR.parent)}  (template created)")
        else:
            print("  [SKIP] project_state.md  (already exists — not overwritten)")
    except ValueError:
        print(f"  [DONE] {project_yaml_path}")
        print(f"  [DONE] {system_prompt_path}")
    print("=" * 60)
    print()
    print("Next: Paste system_prompt.md into your AI tool as the system prompt (do this once).")
    print('Then: python agents-maker/tools/generate_prompt.py "your first task"')
    print()

    # --platforms: generate configs for all supported AI platforms
    if args.platforms:
        try:
            from tools.generate_platform_configs import PLATFORMS, generate_all
        except ImportError:
            from generate_platform_configs import PLATFORMS, generate_all
        print("Generating platform configs (Claude Code, Copilot, Cursor, Antigravity)...")
        generate_all(project_root, KIT_DIR, PLATFORMS, dry_run=False)

    # --claude-md: generate CLAUDE.md only (kept for backward compatibility)
    elif args.claude_md:
        try:
            from tools.generate_claude_md import _parse_phase, build_claude_md
        except ImportError:
            from generate_claude_md import _parse_phase, build_claude_md

        state_path = KIT_DIR / "project_state.md"
        phase = _parse_phase(state_path.read_text(encoding="utf-8")) if state_path.exists() else "task_framing"
        try:
            kit_rel = KIT_DIR.relative_to(project_root)
            kit_rel_path = str(kit_rel).replace("\\", "/")
        except ValueError:
            kit_rel_path = "agents-maker"

        claude_md_content = build_claude_md(
            project_name=project_name,
            domain=final_domain,
            confidence="high",
            stack=stack,
            phase=phase,
            kit_rel_path=kit_rel_path,
        )
        claude_md_path = project_root / "CLAUDE.md"
        try:
            atomic_write(claude_md_path, claude_md_content)
            print(f"  [DONE] CLAUDE.md written to {claude_md_path}")
            print("         Claude Code will auto-load domain/phase/stack on every session.")
            print("         Commit CLAUDE.md to git — it is project config, not private state.")
        except OSError as e:
            print(f"  [WARN] Could not write CLAUDE.md: {e}", file=sys.stderr)
        print()
    else:
        print("Tip: Wire agents-maker into Claude Code, Copilot, Cursor, and Antigravity:")
        print("     python agents-maker/tools/generate_platform_configs.py")
        print()


if __name__ == "__main__":
    main()
