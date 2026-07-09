#!/usr/bin/env python3
"""
validate_kit.py — Multi-Agent Assistant Kit integrity checker.

Run after any change to config files, agents, skills, or domains:
    python tools/validate_kit.py

Runs 12 checks:
  1.    YAML parse — all 3 config files
  2.    Agent .md files exist and have content
  3.    Skill .md files exist and have content
  4.    Domain coverage in token_policies.yaml
  5.    Domain primary_agents reference valid agent_ids
  6.    Output style references are defined
  7.    Domain detection scoring (8 test messages)
  8.    File inventory matches README repository map
  9.    Compressor dry-run (PolicyLoader loads 3 workflows)
  10.   Skill markdown structure (input, output, token cost sections)
  11.   Agent markdown structure (role, goals, context sections)
  12.   system_prompt.md freshness (source hash matches current agents + skills)

Exit code 0 = all checks pass. Exit code 1 = one or more failures.
Requires pyyaml (pip install pyyaml).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

__version__ = "1.0.0"

ROOT = Path(__file__).parent.parent

# Allow sibling imports (domain_utils, _core) whether run as a script or module.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from tools._core import source_hash
    from tools.domain_utils import score_domain
except ImportError:
    from _core import source_hash
    from domain_utils import score_domain


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_yaml(path: str) -> dict:
    import yaml
    full_path = ROOT / path
    try:
        with full_path.open(encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        fail(f"YAML parse error in {path}: {e}")
        return {}
    except FileNotFoundError:
        fail(f"File not found: {path}")
        return {}


def ok(msg: str) -> None:
    print(f"  [PASS] {msg}")


def fail(msg: str) -> None:
    print(f"  [FAIL] {msg}")
    FAILURES.append(msg)


FAILURES: list[str] = []


# ---------------------------------------------------------------------------
# Check 1 — YAML parses
# ---------------------------------------------------------------------------

def check_yaml_parse() -> tuple[dict, dict, dict]:
    print("\n--- YAML Parse ---")
    agents_cfg = domain_cfg = policy_cfg = {}
    for path in ["config/agents.yaml", "config/domain_profiles.yaml", "config/token_policies.yaml"]:
        try:
            data = load_yaml(path)
            ok(f"YAML: {path}")
            if "agents" in path:
                agents_cfg = data
            elif "domain" in path:
                domain_cfg = data
            else:
                policy_cfg = data
        except Exception as e:
            fail(f"YAML: {path} — {e}")
    return agents_cfg, domain_cfg, policy_cfg


# ---------------------------------------------------------------------------
# Check 2 — Agent .md files exist
# ---------------------------------------------------------------------------

def check_agent_files(agents_cfg: dict) -> None:
    print("\n--- Agent Files ---")
    registered = list((agents_cfg.get("agents") or {}).keys())
    if not registered:
        fail("agents.yaml has no agents registered")
        return
    missing = []
    empty = []
    for agent_id in registered:
        md = ROOT / "agents" / f"{agent_id}.md"
        if not md.exists():
            missing.append(agent_id)
        else:
            content = md.read_text(encoding="utf-8").strip()
            if len(content) < 100:
                empty.append(f"{agent_id}.md ({len(content)} chars)")
    if missing:
        fail(f"Agent files missing for: {missing}")
    elif empty:
        fail(f"Agent files suspiciously short (< 100 chars): {empty}")
    else:
        ok(f"Agent files: {len(registered)}/{len(registered)} present ({', '.join(registered)})")


# ---------------------------------------------------------------------------
# Check 3 — Skill .md files exist
# ---------------------------------------------------------------------------

def check_skill_files(agents_cfg: dict) -> None:
    print("\n--- Skill Files ---")
    agents = agents_cfg.get("agents") or {}
    all_skills: set[str] = set()
    for cfg in agents.values():
        for s in (cfg.get("skills") or []):
            all_skills.add(s)
    if not all_skills:
        ok("No skills referenced in agents.yaml (skip)")
        return
    missing = []
    empty = []
    for s in sorted(all_skills):
        skill_path = ROOT / "skills" / f"{s}.md"
        if not skill_path.exists():
            missing.append(s)
        else:
            content = skill_path.read_text(encoding="utf-8").strip()
            if len(content) < 50:
                empty.append(f"{s}.md ({len(content)} chars)")
    if missing:
        fail(f"Skill files missing: {missing}")
    elif empty:
        fail(f"Skill files suspiciously short (< 50 chars): {empty}")
    else:
        ok(f"Skill files: {len(all_skills)}/{len(all_skills)} present")


# ---------------------------------------------------------------------------
# Check 4 — Domain coverage in token_policies.yaml
# ---------------------------------------------------------------------------

def check_domain_coverage(domain_cfg: dict, policy_cfg: dict) -> None:
    print("\n--- Domain Coverage in token_policies.yaml ---")
    domains = list((domain_cfg.get("domains") or {}).keys())
    if not domains:
        fail("domain_profiles.yaml has no domains")
        return
    # generic_project_lifecycle is nested under workflows:
    lifecycle = (policy_cfg.get("workflows") or {}).get("generic_project_lifecycle") or {}
    covered = set((lifecycle.get("domains") or {}).keys())
    missing = [d for d in domains if d not in covered]
    if missing:
        fail(f"Domains missing from token_policies generic_project_lifecycle.domains: {missing}")
    else:
        ok(f"Domain coverage: all {len(domains)} domains have overrides ({', '.join(domains)})")


# ---------------------------------------------------------------------------
# Check 5 — domain primary_agents reference valid agent_ids
# ---------------------------------------------------------------------------

def check_primary_agents(domain_cfg: dict, agents_cfg: dict) -> None:
    print("\n--- Domain primary_agents Validity ---")
    valid_ids = set((agents_cfg.get("agents") or {}).keys())
    domains = domain_cfg.get("domains") or {}
    errors = []
    for d, cfg in domains.items():
        for phase, agent_id in (cfg.get("primary_agents") or {}).items():
            if agent_id not in valid_ids:
                errors.append(f"domain={d} phase={phase}: unknown agent '{agent_id}'")
    if errors:
        for e in errors:
            fail(e)
    else:
        ok("All domain primary_agents reference valid agent_ids")


# ---------------------------------------------------------------------------
# Check 6 — output_style references exist in output_styles block
# ---------------------------------------------------------------------------

def check_output_styles(policy_cfg: dict) -> None:
    print("\n--- Output Style References ---")
    defined_styles = set((policy_cfg.get("output_styles") or {}).keys())
    if not defined_styles:
        fail("No output_styles defined in token_policies.yaml")
        return

    refs: set[str] = set()
    # Scan workflows and phases for output_style keys
    for key, val in (policy_cfg.get("workflows") or {}).items():
        if isinstance(val, dict) and "output_style" in val:
            refs.add(val["output_style"])

    # generic_project_lifecycle is nested under workflows: in token_policies.yaml.
    lifecycle = (policy_cfg.get("workflows") or {}).get("generic_project_lifecycle") or {}
    for phase_key, phase_val in (lifecycle.get("phases") or {}).items():
        if isinstance(phase_val, dict) and "output_style" in phase_val:
            refs.add(phase_val["output_style"])
    for d_key, d_val in (lifecycle.get("domains") or {}).items():
        for phase_key, phase_val in (d_val or {}).items():
            if isinstance(phase_val, dict) and "output_style" in phase_val:
                refs.add(phase_val["output_style"])

    missing_styles = refs - defined_styles
    if missing_styles:
        fail(f"output_style values referenced but not defined: {sorted(missing_styles)}")
    else:
        ok(f"Output styles: all {len(refs)} referenced styles are defined")


# ---------------------------------------------------------------------------
# Check 7 — Domain detection scoring smoke test
# ---------------------------------------------------------------------------

SCORING_TESTS = [
    ("software",       "high",   "Help me refactor the UserService and add unit tests for the API endpoints."),
    ("content",        "high",   "Write a blog post about AI trends for our marketing newsletter."),
    ("data_analytics", "high",   "Analyze our sales funnel conversion data and build a dashboard."),
    ("general",        "low",    "Help me document the onboarding process for new engineers."),
    ("product_design", "high",   "Design a mobile checkout flow for our e-commerce app."),
    ("research",       "high",   "Write a literature review on transformer architectures."),
    ("marketing",      "high",   "Create a go-to-market strategy for our new SaaS product."),
    ("general",        "low",    "I need help with something."),
]


def check_domain_scoring(domain_cfg: dict) -> None:
    # Uses the shared scorer (domain_utils.score_domain) — the same code the
    # runtime tools use — so this check can never validate a stale copy.
    print("\n--- Domain Detection Scoring ---")
    domains = domain_cfg.get("domains") or {}
    settings = domain_cfg.get("settings") or {}
    passed = 0
    for exp_domain, exp_conf, msg in SCORING_TESTS:
        got_domain, got_conf = score_domain(msg, domains, settings)
        if got_domain == exp_domain and got_conf == exp_conf:
            passed += 1
        else:
            fail(
                f"Scoring mismatch: expected ({exp_domain}, {exp_conf}), "
                f"got ({got_domain}, {got_conf}) for: \"{msg[:55]}...\""
            )
    if passed == len(SCORING_TESTS):
        ok(f"Domain scoring: {passed}/{len(SCORING_TESTS)} test messages routed correctly")


# ---------------------------------------------------------------------------
# Check 8 — File inventory from README.md repository map
# ---------------------------------------------------------------------------

# (defined below — keep check order consistent with main())

# ---------------------------------------------------------------------------
# Check 9 — Compressor dry-run
# ---------------------------------------------------------------------------

def check_compressor() -> None:
    print("\n--- Compressor Dry-Run ---")
    try:
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from token_optimization.compressor import PolicyLoader
        loader = PolicyLoader(ROOT / "config" / "token_policies.yaml")
        loader.load()
        for workflow in ["feature_implementation", "code_review", "feature_design"]:
            policy = loader.get_workflow_policy(workflow)
            if not policy.output_style:
                fail(f"PolicyLoader.get_workflow_policy('{workflow}') returned empty output_style")
                return
            if policy.max_input_tokens <= 0:
                fail(f"Policy '{workflow}' has invalid max_input_tokens: {policy.max_input_tokens}")
                return
        ok("Compressor: PolicyLoader loads and returns valid policies for 3 workflows")
    except ImportError as e:
        fail(f"Compressor import failed: {e}")
    except Exception as e:
        fail(f"Compressor dry-run failed: {e}")


# ---------------------------------------------------------------------------
# Check 10 — Skill markdown structure
# ---------------------------------------------------------------------------

_REQUIRED_SKILL_SECTIONS = ["input", "output", "token cost"]


def check_skill_structure(agents_cfg: dict) -> None:
    print("\n--- Skill Markdown Structure ---")
    agents = agents_cfg.get("agents") or {}
    all_skills: set[str] = set()
    for cfg in agents.values():
        for s in (cfg.get("skills") or []):
            all_skills.add(s)

    if not all_skills:
        ok("No skills to check (skip)")
        return

    issues: list[str] = []
    for skill_key in sorted(all_skills):
        path = ROOT / "skills" / f"{skill_key}.md"
        if not path.exists():
            continue  # already caught by Check 3
        content = path.read_text(encoding="utf-8").lower()
        missing = [s for s in _REQUIRED_SKILL_SECTIONS if s not in content]
        if missing:
            issues.append(f"{skill_key}.md missing sections: {missing}")

    if issues:
        for issue in issues:
            fail(f"Skill structure: {issue}")
    else:
        ok(f"Skill structure: all {len(all_skills)} skill cards have required sections (input, output, token cost)")


# ---------------------------------------------------------------------------
# Check 11 — Agent markdown structure
# ---------------------------------------------------------------------------

_REQUIRED_AGENT_SECTIONS = ["## role", "## goals", "context"]


def check_agent_structure(agents_cfg: dict) -> None:
    print("\n--- Agent Markdown Structure ---")
    registered = list((agents_cfg.get("agents") or {}).keys())

    if not registered:
        ok("No agents to check (skip)")
        return

    issues: list[str] = []
    for agent_id in registered:
        path = ROOT / "agents" / f"{agent_id}.md"
        if not path.exists():
            continue  # already caught by Check 2
        content = path.read_text(encoding="utf-8").lower()
        missing = [s for s in _REQUIRED_AGENT_SECTIONS if s not in content]
        if missing:
            issues.append(f"{agent_id}.md missing sections: {missing}")

    if issues:
        for issue in issues:
            fail(f"Agent structure: {issue}")
    else:
        ok(f"Agent structure: all {len(registered)} agent specs have required sections (role, goals, context)")


# ---------------------------------------------------------------------------
# Check 8 — File inventory from README.md repository map (continued below)
# ---------------------------------------------------------------------------

def check_file_inventory() -> None:
    print("\n--- File Inventory (README.md repository map) ---")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    # Find the repository map code block and extract file names
    block = re.search(r"Repository Map.*?```(.*?)```", readme, re.DOTALL)
    if not block:
        ok("No repository map block found in README.md (skip)")
        return

    files_in_readme: list[str] = []
    for line in block.group(1).splitlines():
        # Allow optional emoji/unicode between tree indicator and filename
        m = re.search(r"(?:├──|└──)\s*[^\w\s./\\-]*\s*([\w][\w.\-]*\.\w+)", line)
        if m:
            files_in_readme.append(m.group(1))

    if not files_in_readme:
        ok("Repository map found but no file entries extracted (skip)")
        return

    missing = [f for f in files_in_readme if not list(ROOT.rglob(f))]
    if missing:
        fail(f"Files in README map not found on disk: {missing}")
    else:
        ok(f"File inventory: all {len(files_in_readme)} files from README map exist on disk")


# ---------------------------------------------------------------------------
# Check 12 — system_prompt.md freshness
# ---------------------------------------------------------------------------

def check_system_prompt_freshness() -> None:
    print("\n--- system_prompt.md Freshness ---")
    sp_path = ROOT / "system_prompt.md"
    if not sp_path.exists():
        ok("system_prompt.md not present — skipping freshness check (run init_project.py to generate)")
        return

    try:
        content = sp_path.read_text(encoding="utf-8")
    except (OSError, PermissionError) as e:
        fail(f"Could not read system_prompt.md: {e}")
        return

    m = re.search(r"Source hash:\s*([a-f0-9]{16})", content)
    if not m:
        fail("system_prompt.md has no source hash — regenerate with: python tools/init_project.py --update")
        return

    stored = m.group(1)
    current = source_hash(ROOT)
    if stored != current:
        fail(
            f"system_prompt.md is stale (stored hash {stored} != current {current}). "
            "Regenerate: python tools/init_project.py --update"
        )
    else:
        ok(f"system_prompt.md is current (source hash: {current})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    if "--version" in sys.argv or "-V" in sys.argv:
        print(f"validate_kit.py {__version__}")
        return 0
    FAILURES.clear()
    print("=" * 60)
    print("  Multi-Agent Assistant Kit — Integrity Checker")
    print(f"  Root: {ROOT}")
    print("=" * 60)

    agents_cfg, domain_cfg, policy_cfg = check_yaml_parse()
    check_agent_files(agents_cfg)
    check_skill_files(agents_cfg)
    check_domain_coverage(domain_cfg, policy_cfg)
    check_primary_agents(domain_cfg, agents_cfg)
    check_output_styles(policy_cfg)
    check_domain_scoring(domain_cfg)
    check_file_inventory()
    check_compressor()
    check_skill_structure(agents_cfg)
    check_agent_structure(agents_cfg)
    check_system_prompt_freshness()

    total_checks = 12
    failed = len(FAILURES)
    passed = total_checks - failed

    print("\n" + "=" * 60)
    if failed == 0:
        print(f"  Result: ALL {total_checks} checks PASSED")
    else:
        print(f"  Result: {passed}/{total_checks} checks passed. {failed} FAILURE(s):")
        for f in FAILURES:
            print(f"    - {f}")
    print("=" * 60)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
