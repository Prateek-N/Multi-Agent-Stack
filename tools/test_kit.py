#!/usr/bin/env python3
"""
test_kit.py — Comprehensive edge-case test suite for agents-maker.

Run from the repo root:
    python tools/test_kit.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

PASS_COUNT = 0
FAIL_COUNT = 0
RESULTS = []


def run(cmd: list[str], cwd: Path = ROOT, input_text: str | None = None) -> tuple[int, str, str]:
    result = subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True,
        input=input_text, encoding="utf-8", errors="replace"
    )
    return result.returncode, result.stdout, result.stderr


def check(n: int, desc: str, passed: bool, reason: str = "") -> None:
    global PASS_COUNT, FAIL_COUNT
    if passed:
        PASS_COUNT += 1
        tag = f"PASS [{n:02d}]"
    else:
        FAIL_COUNT += 1
        tag = f"FAIL [{n:02d}]"
    msg = f"{tag} {desc}"
    if not passed and reason:
        msg += f"\n         Reason: {reason}"
    print(msg)
    RESULTS.append((n, passed, desc, reason))


def section(title: str) -> None:
    print(f"\n{'-' * 60}")
    print(f"  {title}")
    print('-' * 60)


# -------------------------------------------------------------
# A. generate_prompt.py — normal cases
# -------------------------------------------------------------
section("A. generate_prompt.py — normal cases")

rc, out, err = run([PY, "tools/generate_prompt.py", "add rate limiting to the auth service"])
check(1, "Basic run exits 0", rc == 0, err[:200] if rc != 0 else "")
check(2, "Output contains ## Project Context", "## Project Context" in out, "")
check(3, "Software domain auto-detected", "software" in out.lower(), out[:300])

rc, out, err = run([PY, "tools/generate_prompt.py", "add rate limiting", "--phase", "implementation"])
check(4, "--phase implementation -> output contains 'implementation'", "implementation" in out, "")

rc, out, err = run([PY, "tools/generate_prompt.py", "add rate limiting", "--phase", "review"])
check(5, "--phase review -> output contains 'review'", "review" in out, "")

rc, out, err = run([PY, "tools/generate_prompt.py", "add rate limiting", "--full"])
check(6, "--full flag -> output contains orchestrator content", "Orchestrator" in out or "orchestrator" in out, "")

rc, out, err = run([PY, "tools/generate_prompt.py", "add rate limiting", "--compress"])
check(7, "--compress flag -> output contains ## Output Policy", "## Output Policy" in out, out[-300:])

rc, out, err = run([PY, "tools/generate_prompt.py", "[domain: content] write a blog post about GraphQL"])
check(8, "[domain: content] prefix -> domain is content", "content" in out.lower(), "")

rc, out, err = run([PY, "tools/generate_prompt.py", "[domain: ops_process] write a runbook for failover"])
check(9, "[domain: ops_process] prefix -> execution_agent or ops_process in output", "ops_process" in out.lower() or "execution_agent" in out.lower(), out[:300])

# -------------------------------------------------------------
# B. generate_prompt.py — edge cases / error handling
# -------------------------------------------------------------
section("B. generate_prompt.py — edge cases / error handling")

rc, out, err = run([PY, "tools/generate_prompt.py", ""])
check(10, "Empty problem -> non-zero exit", rc != 0, f"exit={rc}")
check(11, "Empty problem -> stderr contains 'empty'", "empty" in err.lower(), err[:200])

long_input = "x" * 5001
rc, out, err = run([PY, "tools/generate_prompt.py", long_input])
check(12, "Problem > 5000 chars -> non-zero exit", rc != 0, f"exit={rc}")
check(13, "Problem > 5000 chars -> stderr contains 'too long'", "too long" in err.lower(), err[:200])

rc, out, err = run([PY, "tools/generate_prompt.py", "task", "--phase", "invalid_phase"])
check(14, "Invalid --phase value -> non-zero exit", rc != 0, f"exit={rc}")

valid_phases = ["task_framing", "requirements", "design", "solution_design",
                "implementation", "implement", "review", "review_refinement", "handoff", "framing"]
all_phases_ok = True
failed_phase = ""
for ph in valid_phases:
    rc2, _, err2 = run([PY, "tools/generate_prompt.py", "some task", "--phase", ph])
    if rc2 != 0:
        all_phases_ok = False
        failed_phase = f"phase={ph} exit={rc2} err={err2[:100]}"
        break
check(15, "All valid --phase values exit 0", all_phases_ok, failed_phase)

# -------------------------------------------------------------
# C. Domain detection — all 8 domains
# -------------------------------------------------------------
section("C. Domain detection — all 8 domains")

domain_tests = [
    (16, "software",       "Refactor the UserRepository class and add unit tests for the API endpoints"),
    (17, "content",        "Write a technical blog post about our REST to GraphQL migration for developers"),
    (18, "research",       "Write a literature review on transformer model architectures for NLP"),
    (19, "data_analytics", "Build a sales funnel dashboard with conversion metrics and pipeline analytics"),
    (20, "product_design", "Design a mobile onboarding flow for our e-commerce app with persona mapping"),
    (21, "marketing",      "Create a go-to-market strategy and campaign brief for our SaaS product launch"),
    (22, "ops_process",    "Write a runbook SOP for our database failover and disaster recovery procedure"),
    (23, "general",        "I need help with something"),
]

for n, expected_domain, task in domain_tests:
    rc, out, err = run([PY, "tools/generate_prompt.py", task])
    combined = out.lower() + err.lower()
    if expected_domain == "general":
        # Low-confidence tasks fall back to project domain when project.yaml has primary_domain set.
        # Accept either "general" OR "from-project" (scoring fell below threshold, used project default).
        found = "general" in combined or "from-project" in combined
    else:
        found = expected_domain in combined
    check(n, f"Domain detection -> {expected_domain}", found, f"task='{task[:50]}...' output snippet: {out[:200]}")

# -------------------------------------------------------------
# D. validate_kit.py — all 12 checks pass
# -------------------------------------------------------------
section("D. validate_kit.py — all 12 checks pass normally")

rc, out, err = run([PY, "tools/validate_kit.py"])
check(24, "validate_kit.py exits 0", rc == 0, err[:200])
check(25, "ALL 12 checks PASSED in output", "ALL 12 checks PASSED" in out, out[-300:])

# -------------------------------------------------------------
# E. validate_kit.py — failure detection (temporarily corrupt files)
# -------------------------------------------------------------
section("E. validate_kit.py — failure detection")

orch_path = ROOT / "agents" / "orchestrator.md"
orch_backup = orch_path.read_text(encoding="utf-8")

try:
    orch_path.rename(ROOT / "agents" / "orchestrator.md.bak")
    rc, out, err = run([PY, "tools/validate_kit.py"])
    check(26, "Missing agent file -> FAIL in output", "FAIL" in out, out[-300:])
finally:
    bak = ROOT / "agents" / "orchestrator.md.bak"
    if bak.exists():
        bak.rename(orch_path)

skill_path = ROOT / "skills" / "analyze_repo.md"
skill_backup = skill_path.read_text(encoding="utf-8")
try:
    skill_path.write_text("short", encoding="utf-8")
    rc, out, err = run([PY, "tools/validate_kit.py"])
    check(27, "Stub skill file (< 50 chars) -> FAIL in output", "FAIL" in out, out[-300:])
finally:
    skill_path.write_text(skill_backup, encoding="utf-8")

try:
    skill_path.write_text("# Skill: test\n\nNo input or output section here.\n\nToken budget: low\n", encoding="utf-8")
    rc, out, err = run([PY, "tools/validate_kit.py"])
    check(28, "Skill missing input/output headings -> FAIL in output", "FAIL" in out, out[-300:])
finally:
    skill_path.write_text(skill_backup, encoding="utf-8")

agent_path = ROOT / "agents" / "orchestrator.md"
agent_backup = agent_path.read_text(encoding="utf-8")
try:
    agent_path.write_text("# Orchestrator\n\nSome content without required sections.\n" * 5, encoding="utf-8")
    rc, out, err = run([PY, "tools/validate_kit.py"])
    check(29, "Agent missing ## Role/Goals/Context -> FAIL in output", "FAIL" in out, out[-300:])
finally:
    agent_path.write_text(agent_backup, encoding="utf-8")

# Confirm restore worked
rc, out, err = run([PY, "tools/validate_kit.py"])
check(30, "All files restored -> validator passes again", "ALL 12 checks PASSED" in out, out[-200:])

# -------------------------------------------------------------
# F. Compressor / PolicyLoader — direct import tests
# -------------------------------------------------------------
section("F. Compressor / PolicyLoader — direct import tests")

sys.path.insert(0, str(ROOT))

try:
    from token_optimization.compressor import (
        CompressionReport,
        Compressor,
        ContextBlock,
        PolicyLoader,
    )

    loader = PolicyLoader(ROOT / "config" / "token_policies.yaml")
    loader.load()
    check(31, "PolicyLoader imports and loads without error", True, "")

    for wf in ["feature_implementation", "code_review", "feature_design"]:
        policy = loader.get_workflow_policy(wf)
        ok_wf = policy.max_input_tokens > 0 and bool(policy.output_style)
        check({"feature_implementation": 32, "code_review": 33, "feature_design": 34}[wf],
              f"get_workflow_policy('{wf}') returns valid policy",
              ok_wf, f"max_input_tokens={policy.max_input_tokens} output_style={policy.output_style}")

    unknown_policy = loader.get_workflow_policy("completely_unknown_workflow_xyz")
    check(35, "Unknown workflow -> fallback policy, no crash",
          unknown_policy is not None and unknown_policy.max_input_tokens >= 0, "")

    policy = loader.get_workflow_policy("feature_implementation")
    compressor = Compressor(policy)
    empty_block = ContextBlock()
    compressed, report = compressor.compress(empty_block)
    check(36, "compress(empty ContextBlock) returns without crash",
          isinstance(compressed, str) and isinstance(report, CompressionReport), "")

    block_with_state = ContextBlock(
        project_state="Name: test-project\nStack: Python, FastAPI\nDomain: software",
        active_query="add rate limiting to the auth service",
        conversation_state="User asked about rate limiting. We discussed Redis sliding window.",
    )
    compressed2, report2 = compressor.compress(block_with_state)
    check(37, "compress(ContextBlock with content) returns non-empty string",
          isinstance(compressed2, str) and len(compressed2) > 0, f"len={len(compressed2)}")

    loader_bad = PolicyLoader("/nonexistent/path/token_policies.yaml")
    try:
        loader_bad.load()
        check(38, "PolicyLoader with bad path -> graceful fallback, no exception", True, "")
    except Exception as e:
        check(38, "PolicyLoader with bad path -> graceful fallback, no exception", False, str(e))

except ImportError as e:
    for n in range(31, 39):
        check(n, "Compressor import test", False, str(e))

# -------------------------------------------------------------
# G. Context loaders — smoke tests
# -------------------------------------------------------------
section("G. Context loaders — smoke tests")

rc, out, err = run([PY, "context_loaders/project_summary.py", "--path", str(ROOT)])
check(39, "project_summary.py exits 0", rc == 0, err[:200])
check(40, "project_summary.py output contains 'Stack' or 'Language'",
      "stack" in out.lower() or "language" in out.lower(), out[:300])

rc, out, err = run([PY, "context_loaders/repo_tree.py", "--path", str(ROOT)])
check(41, "repo_tree.py exits 0", rc == 0, err[:200])
check(42, "repo_tree.py output contains directory structure",
      "agents" in out.lower() or "skills" in out.lower(), out[:300])

rc, out, err = run([PY, "context_loaders/file_chunker.py", "--path", str(ROOT), "--files", "README.md"])
check(43, "file_chunker.py exits 0", rc == 0, err[:200])
check(44, "file_chunker.py output contains README content",
      "agents-maker" in out.lower() or "readme" in out.lower(), out[:300])

# -------------------------------------------------------------
# H. init_project.py — smoke tests
# -------------------------------------------------------------
section("H. init_project.py — smoke tests")

rc, out, err = run([PY, "tools/init_project.py", "--path", str(ROOT), "--update"])
check(45, "init_project.py --update exits 0", rc == 0, err[:300])
check(46, "system_prompt.md still exists after --update", (ROOT / "system_prompt.md").exists(), "")

# -------------------------------------------------------------
# I. generate_prompt.py — missing project.yaml
# -------------------------------------------------------------
section("I. generate_prompt.py — missing project.yaml")

proj_yaml = ROOT / "config" / "project.yaml"
proj_backup = None
renamed = False

if proj_yaml.exists():
    proj_backup = proj_yaml.read_text(encoding="utf-8")
    proj_yaml.rename(ROOT / "config" / "project.yaml.bak")
    renamed = True

try:
    rc, out, err = run([PY, "tools/generate_prompt.py", "add rate limiting"])
    check(47, "Missing project.yaml -> tool still exits 0", rc == 0, err[:200])
    check(48, "Missing project.yaml -> [WARN] printed to stderr", "[WARN]" in err, err[:200])
finally:
    bak = ROOT / "config" / "project.yaml.bak"
    if bak.exists():
        bak.rename(proj_yaml)
    elif proj_backup and not proj_yaml.exists():
        proj_yaml.write_text(proj_backup, encoding="utf-8")

# -------------------------------------------------------------
# J. system_prompt.md integrity
# -------------------------------------------------------------
section("J. system_prompt.md integrity")

sp = ROOT / "system_prompt.md"
check(49, "system_prompt.md exists", sp.exists(), "")
if sp.exists():
    sp_text = sp.read_text(encoding="utf-8")
    check(50, "system_prompt.md > 10,000 chars", len(sp_text) > 10000, f"actual: {len(sp_text)}")
    check(51, "system_prompt.md contains orchestrator content (## Role or ## Goals)",
          "## role" in sp_text.lower() or "## goals" in sp_text.lower(), "")
    check(52, "system_prompt.md contains version header",
          "agents-maker system_prompt.md" in sp_text, sp_text[:200])
    check(53, "system_prompt.md contains [Companion] instruction",
          "[Companion]" in sp_text, sp_text[:500])
else:
    for n in range(50, 54):
        check(n, "system_prompt.md content check", False, "file missing")

# -------------------------------------------------------------
# K. generate_prompt.py — --compress with all phases
# -------------------------------------------------------------
section("K. --compress with all phases")

compress_phases = ["task_framing", "implementation", "review_refinement", "handoff", "solution_design"]
for i, ph in enumerate(compress_phases):
    rc, out, err = run([PY, "tools/generate_prompt.py", "some task", "--phase", ph, "--compress"])
    n = 54 + i
    check(n, f"--compress --phase {ph} -> exits 0 + Output Policy in output",
          rc == 0 and "## Output Policy" in out,
          f"exit={rc} stderr={err[:100]}")

# -------------------------------------------------------------
# L. --full + --compress combined
# -------------------------------------------------------------
section("L. --full + --compress combined")

rc, out, err = run([PY, "tools/generate_prompt.py", "add feature", "--full", "--compress"])
check(59, "--full --compress combined -> exits 0", rc == 0, err[:200])
check(60, "--full --compress -> contains both system prompt and Output Policy",
      ("Orchestrator" in out or "orchestrator" in out) and "## Output Policy" in out, "")

# -------------------------------------------------------------
# M. generate_claude_agents.py — subagents + slash commands
# -------------------------------------------------------------
section("M. generate_claude_agents.py — .claude/ subagents + commands")

rc, out, err = run([PY, "tools/generate_claude_agents.py", "--template", "--dry-run"])
check(61, "generate_claude_agents --dry-run exits 0", rc == 0, err[:200])
check(62, "dry-run reports 20 files (10 agents + 10 commands)",
      out.count("agents/") >= 10 and out.count("commands/") >= 10, out[:300])

claude_agents_dir = ROOT / "claude" / "agents"
claude_cmds_dir = ROOT / "claude" / "commands"
agent_files = sorted(claude_agents_dir.glob("*.md")) if claude_agents_dir.is_dir() else []
cmd_files = sorted(claude_cmds_dir.glob("*.md")) if claude_cmds_dir.is_dir() else []
check(63, "committed claude/ templates: 10 agents + 10 commands",
      len(agent_files) == 10 and len(cmd_files) == 10,
      f"agents={len(agent_files)} commands={len(cmd_files)}")

pp = claude_agents_dir / "planpro.md"
pp_text = pp.read_text(encoding="utf-8") if pp.exists() else ""
check(64, "subagent planpro.md has valid frontmatter (name/tools/model)",
      "name: planpro" in pp_text and "tools:" in pp_text and "model: inherit" in pp_text,
      pp_text[:200])

brain_cmd = claude_cmds_dir / "brain.md"
bc_text = brain_cmd.read_text(encoding="utf-8") if brain_cmd.exists() else ""
check(65, "command brain.md has description + $ARGUMENTS",
      "description:" in bc_text and "$ARGUMENTS" in bc_text, bc_text[:200])

# -------------------------------------------------------------
# Summary
# -------------------------------------------------------------
total = PASS_COUNT + FAIL_COUNT
print(f"\n{'=' * 60}")
print(f"  RESULTS: {PASS_COUNT}/{total} tests passed | {FAIL_COUNT} failed")
print('=' * 60)

if FAIL_COUNT > 0:
    print("\nFailed tests:")
    for n, passed, desc, reason in RESULTS:
        if not passed:
            print(f"  [{n:02d}] {desc}")
            if reason:
                print(f"       {reason[:300]}")

sys.exit(0 if FAIL_COUNT == 0 else 1)
