#!/usr/bin/env python3
"""
compare_prompts.py — Proof-of-value harness for agents-maker.

For a given task it builds TWO prompts and runs BOTH through the same model,
so you can see what the structuring actually changes:

  1. NAIVE      — the raw task, exactly as a user would type it into a chat box.
  2. STRUCTURED — the agents-maker prompt (system prompt + domain routing +
                  project context + Companion Mode), via generate_prompt.py --full.

Outputs (prompts + raw model responses) are written to examples/proof/<slug>/
so the comparison is reproducible and auditable — no cherry-picking.

Model runner
------------
By default it shells out to the Claude Code CLI in non-interactive mode
(`claude -p`), which reuses your existing auth (no API key needed). Override
with --runner to use any command that reads a prompt on stdin and prints the
completion on stdout, e.g.:

    python tools/compare_prompts.py "..." --runner "llm -m gpt-4o"

Usage
-----
    python tools/compare_prompts.py "add rate limiting to the auth service"
    python tools/compare_prompts.py "[domain: ops_process] write a Redis failover runbook"
    python tools/compare_prompts.py "write a launch tweet" --skip-run   # build prompts only
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
KIT_DIR = SCRIPT_DIR.parent
PROOF_DIR = KIT_DIR / "examples" / "proof"

_SEP = "=" * 60


def _slug(task: str) -> str:
    s = re.sub(r"\[domain:[^\]]*\]", "", task).strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s[:48] or "task").rstrip("-")


def build_structured_prompt(task: str, full: bool = True) -> str:
    """Run generate_prompt.py and extract the pasteable prompt body.

    full=True inlines the whole system prompt (single-message / free-tier paste).
    full=False returns only the context+task+routing block — use it as the `user`
    message when the system prompt is supplied separately in the `system` field.
    """
    cmd = [sys.executable, str(SCRIPT_DIR / "generate_prompt.py"), task]
    if full:
        cmd.append("--full")
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"generate_prompt.py failed: {proc.stderr[:300]}")
    # Output is: SEP / header / SEP / <body> / SEP / footer / SEP
    parts = proc.stdout.split(_SEP)
    if len(parts) < 4:
        raise RuntimeError("Unexpected generate_prompt.py output format.")
    return parts[2].strip()


def run_anthropic(system: str | None, user: str, model: str, max_tokens: int = 3000) -> str:
    """Call the Anthropic Messages API with proper role separation. Key from env."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set.")
    body: dict = {"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": user}]}
    if system:
        # Mark the (large, stable) system prompt as cacheable: the first call writes
        # the cache, later calls read it at ~0.1x input cost.
        body["system"] = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return f"[api error {e.code}] {e.read().decode('utf-8', 'replace')[:400]}"
    u = data.get("usage", {})
    print(
        f"       [usage] input={u.get('input_tokens',0)} "
        f"cache_write={u.get('cache_creation_input_tokens',0)} "
        f"cache_read={u.get('cache_read_input_tokens',0)} "
        f"output={u.get('output_tokens',0)}",
        file=sys.stderr,
    )
    return "".join(b.get("text", "") for b in data.get("content", [])).strip()


def run_model(prompt: str, runner: str, cwd: str) -> str:
    """Feed a prompt to the model runner (stdin) and return the completion text.

    Runs in an isolated empty `cwd` so an agent-style runner (e.g. claude -p)
    answers the prompt as text instead of inspecting the current repository —
    otherwise the comparison is confounded by whatever project it is run from.
    """
    cmd = runner.split() + ([] if runner.split()[0] != "claude" else ["-p"])
    proc = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True,
        encoding="utf-8", errors="replace", cwd=cwd,
    )
    if proc.returncode != 0:
        return f"[runner error rc={proc.returncode}]\n{proc.stderr[:500]}"
    return proc.stdout.strip()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Compare a naive vs agents-maker structured prompt on the same model.")
    ap.add_argument("task", help="The task to test (supports a leading [domain: X] prefix).")
    ap.add_argument("--runner", default="claude",
                    help='CLI mode: model command reading stdin, printing stdout (default: "claude" -> claude -p).')
    ap.add_argument("--api", action="store_true",
                    help="Use the Anthropic Messages API with proper system/user role separation (needs ANTHROPIC_API_KEY).")
    ap.add_argument("--model", default="claude-haiku-4-5-20251001", help="Model id for --api mode.")
    ap.add_argument("--skip-run", action="store_true", help="Only build the two prompts; do not call the model.")
    ap.add_argument("--out", default=None, help="Output directory (default: examples/proof/<slug>/).")
    args = ap.parse_args()

    out_dir = Path(args.out) if args.out else PROOF_DIR / _slug(args.task)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.api:
        # Role-separated: task-scoped system prompt in `system`, task+context as `user`.
        sp = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "generate_prompt.py"), args.task, "--system-only"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if sp.returncode != 0:
            raise RuntimeError(f"generate_prompt --system-only failed: {sp.stderr[:300]}")
        system_prompt = sp.stdout.strip()
        naive = args.task
        structured_user = build_structured_prompt(args.task, full=False)
        (out_dir / "naive_prompt.txt").write_text(naive + "\n", encoding="utf-8")
        (out_dir / "structured_user.txt").write_text(structured_user + "\n", encoding="utf-8")
        print(f"[built] {out_dir} (api mode, model={args.model})")
        print(f"        naive user: {len(naive)} chars | structured system: {len(system_prompt)} + user: {len(structured_user)} chars")
        if args.skip_run:
            print("[skip-run] prompts written; model not called.")
            return
        print("[run] naive (no system prompt)...")
        naive_out = run_anthropic(None, naive, args.model)
        (out_dir / "naive_output.md").write_text(naive_out + "\n", encoding="utf-8")
        print("[run] structured (system=system_prompt.md, user=task+context)...")
        structured_out = run_anthropic(system_prompt, structured_user, args.model)
        (out_dir / "structured_output.md").write_text(structured_out + "\n", encoding="utf-8")
        print(f"[done] outputs written to {out_dir}")
        print(f"       naive_output: {len(naive_out)} chars | structured_output: {len(structured_out)} chars")
        return

    naive = args.task
    structured = build_structured_prompt(args.task, full=True)

    (out_dir / "naive_prompt.txt").write_text(naive + "\n", encoding="utf-8")
    (out_dir / "structured_prompt.txt").write_text(structured + "\n", encoding="utf-8")
    print(f"[built] {out_dir}")
    print(f"        naive: {len(naive)} chars | structured: {len(structured)} chars")

    if args.skip_run:
        print("[skip-run] prompts written; model not called.")
        return

    sandbox = tempfile.mkdtemp(prefix="am-proof-")

    print(f"[run] naive via '{args.runner}' (isolated cwd)...")
    naive_out = run_model(naive, args.runner, sandbox)
    (out_dir / "naive_output.md").write_text(naive_out + "\n", encoding="utf-8")

    print(f"[run] structured via '{args.runner}' (isolated cwd)...")
    structured_out = run_model(structured, args.runner, sandbox)
    (out_dir / "structured_output.md").write_text(structured_out + "\n", encoding="utf-8")

    print(f"[done] outputs written to {out_dir}")
    print(f"       naive_output: {len(naive_out)} chars | structured_output: {len(structured_out)} chars")


if __name__ == "__main__":
    main()
