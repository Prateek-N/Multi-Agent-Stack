#!/usr/bin/env python3
"""
grade_proof.py — Blind adversarial grading for compare_prompts.py output.

Takes a proof folder (naive_prompt.txt + naive_output.md + structured_output.md),
anonymizes the two responses as A/B (order decided by a stable per-folder seed,
so it is blind but reproducible), and asks an impartial judge model to score both
on completeness / correctness / actionability / structure and pick a winner.

The judge is a DIFFERENT model from the one that produced the outputs, to reduce
self-preference bias. Judge input excludes the system prompt, so it stays well
under tight input-token rate limits.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python tools/grade_proof.py examples/proof/<folder>
    python tools/grade_proof.py examples/proof/<folder> --judge claude-sonnet-5
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

CRITERIA = ["completeness", "correctness", "actionability", "structure"]


def call_judge(prompt: str, model: str, max_tokens: int = 1200) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set.")
    body = {"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"judge api error {e.code}: {e.read().decode('utf-8','replace')[:300]}") from None
    return "".join(b.get("text", "") for b in data.get("content", [])).strip()


def build_prompt(task: str, resp_a: str, resp_b: str) -> str:
    return (
        "You are a strict, impartial evaluator. A user made this request:\n\n"
        f"<request>\n{task}\n</request>\n\n"
        "Two assistants answered. Judge only how well each fulfills the request "
        "(ignore length; longer is not better).\n\n"
        f"### Response A\n{resp_a}\n\n### Response B\n{resp_b}\n\n"
        "Score each response 1-5 on completeness, correctness, actionability, structure. "
        "Then pick the overall winner. Respond with ONLY JSON, no prose:\n"
        '{"A":{"completeness":0,"correctness":0,"actionability":0,"structure":0},'
        '"B":{"completeness":0,"correctness":0,"actionability":0,"structure":0},'
        '"winner":"A|B|tie","reason":"one sentence"}'
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Blind-grade a compare_prompts.py proof folder.")
    ap.add_argument("folder", help="Proof folder containing naive_/structured_ files.")
    ap.add_argument("--judge", default="claude-sonnet-5", help="Judge model id (default: claude-sonnet-5).")
    args = ap.parse_args()

    d = Path(args.folder)
    task = (d / "naive_prompt.txt").read_text(encoding="utf-8").strip()
    naive = (d / "naive_output.md").read_text(encoding="utf-8").strip()
    structured = (d / "structured_output.md").read_text(encoding="utf-8").strip()

    # Stable, reproducible blind assignment: structured is A iff folder-hash is even.
    seed = int(hashlib.sha256(d.name.encode()).hexdigest(), 16)
    structured_is_a = (seed % 2 == 0)
    resp_a, resp_b = (structured, naive) if structured_is_a else (naive, structured)

    raw = call_judge(build_prompt(task, resp_a, resp_b), args.judge)
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        raise RuntimeError(f"Judge did not return JSON:\n{raw[:300]}")
    verdict = json.loads(m.group(0))

    label = {"A": "structured" if structured_is_a else "naive",
             "B": "naive" if structured_is_a else "structured"}
    winner = label.get(verdict.get("winner", ""), verdict.get("winner", "tie"))
    scores = {label[k]: verdict[k] for k in ("A", "B")}

    lines = [
        f"# Blind grade — {d.name}",
        "",
        f"- **Judge:** `{args.judge}` (different model than the one that produced the outputs)",
        f"- **Blind mapping:** structured = Response {'A' if structured_is_a else 'B'}",
        f"- **Winner:** **{winner}**",
        f"- **Reason:** {verdict.get('reason','')}",
        "",
        "| Criterion | naive | structured |",
        "|---|---|---|",
    ]
    for c in CRITERIA:
        lines.append(f"| {c} | {scores['naive'].get(c,'?')} | {scores['structured'].get(c,'?')} |")
    n_tot = sum(scores["naive"].get(c, 0) for c in CRITERIA)
    s_tot = sum(scores["structured"].get(c, 0) for c in CRITERIA)
    lines.append(f"| **total** | **{n_tot}** | **{s_tot}** |")
    (d / "grade.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[graded] {d.name}: winner={winner} | naive={n_tot} structured={s_tot} (judge={args.judge})")


if __name__ == "__main__":
    main()
