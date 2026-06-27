# Skill: Compare Approaches

## Purpose

When a decision has multiple valid implementation paths, produce a structured trade-off comparison
and recommend one approach based on the current project's constraints, stack, and goals.

This skill is how the kit provides **decision support** — not just executing a chosen path, but
helping the user pick the right one before committing.

---

## Trigger Conditions

Invoke this skill when the user's message contains:
- "compare", "trade-off", "trade off", "pros and cons"
- "which approach", "which is better", "should I use X or Y"
- "what are my options for…", "how should I implement…"
- Any design choice point during Phase 2 (Solution Design) where ≥2 valid paths exist
- When the Reviewer Agent (Phase 4) flags a design decision as revisable

---

## Input Expectations

| Input | Required | Description |
|---|---|---|
| `decision_question` | Yes | The specific choice being evaluated — e.g., "Redis vs. in-memory cache for rate limiting" |
| `candidate_approaches` | Yes | 2–4 named options to compare (from user message or inferred from design context) |
| `project_constraints` | No | Stack, team size, timeline, must-not constraints from `task_profile`, `requirements_spec`, or `project.yaml` |
| `approved_adrs` | No | Any architecture decisions already confirmed — recommendations must not contradict them |

**If required input is missing:**
- `decision_question` — infer from the user's message; if still ambiguous, ask: "What specifically are you deciding between?" before producing the table.
- `candidate_approaches` — if only one approach is named, actively surface a second (hybrid, deferral, or "don't solve this yet") so the comparison has ≥2 options.
- `project_constraints` — proceed without; note that the recommendation is based on general trade-offs only, not project-specific context.
- `approved_adrs` — proceed without; add a caveat: "Check existing ADRs before committing to this recommendation."

---

## Output Format

```
**Decision: <the specific question being decided — one clear sentence>**

| Approach | Pros | Cons | Complexity | Token cost to implement |
|---|---|---|---|---|
| A: <name> | <2–3 specific pros> | <2–3 specific cons> | low / med / high | low / med / high |
| B: <name> | <2–3 specific pros> | <2–3 specific cons> | low / med / high | low / med / high |
| C: <name> | <2–3 specific pros> | <2–3 specific cons> | low / med / high | low / med / high |

**Recommendation for this project: Approach <X>**
Reasoning: <2–3 sentences that reference specific project constraints, stack details, or known
goals from the task_profile or requirements_spec — not generic advice>

Confidence: <high | medium | low>
Reversibility: <easy to change later | hard to change later | irreversible — flag with WARNING>

Next step: `python agents-maker/tools/generate_prompt.py "implement <chosen approach name> for <decision context>"`
```

---

## Column Definitions

| Column | What to write |
|---|---|
| Pros | Specific advantages for THIS project — reference stack, team size, timeline if known |
| Cons | Specific drawbacks — what breaks, what becomes harder |
| Complexity | Effort to implement: low = <1 session, med = 1–3 sessions, high = 3+ sessions |
| Token cost | Context needed by AI to implement: low = conversation, med = 3–5 files, high = full repo |

---

## Rules

- Always provide **2–4 options**. Never output a comparison with just one option.
- Pros and cons must be specific to the project — not copy-pasted generic trade-offs.
- The **Recommendation** must cite at least one known constraint from `project.yaml`,
  `requirements_spec`, or the current conversation.
- If `Reversibility` is **irreversible**, prepend: `⚠ WARNING: This decision is difficult to undo.`
- If `Confidence` is **low**, explain what additional information would raise it.
- Never recommend an approach that conflicts with an already-approved ADR or `requirements_spec` constraint.
- If the user only asks about two options, still consider whether a third option exists (hybrid,
  defer, or "don't solve this yet").
- After the table, offer: "Want me to expand on any approach? Say 'expand on approach X.'"
