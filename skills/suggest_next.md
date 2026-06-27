# Skill: Suggest Next Steps

## Purpose

After completing any deliverable — an approved artifact, an approved increment, or any answer to a
user question — surface three concrete, prioritized next moves so the user always knows what to do
without having to think about it.

This skill fires **automatically** at the end of every response when Companion Mode is active.
It may also be invoked on demand: "what should I do next?" / "what's next?" / "options?"

---

## Trigger Conditions

- After every approved phase artifact (`task_profile`, `requirements_spec`, `solution_design`,
  `work_product`, `refinement_report`, `handoff_package`)
- After every approved implementation increment in the `build_log`
- When the user explicitly asks about next steps
- When the user selects option A/B/C at an approval gate and you need to confirm what follows

---

## Input Expectations

This skill fires automatically — it does not require explicit user input. It reads from the active session context:

| Input | Source | Description |
|---|---|---|
| `current_phase` | `project_state.md` or context | Lifecycle phase just completed or currently active |
| `current_domain` | Detected or stated in session | Domain key (software, content, research, etc.) |
| `last_artifact` | Just produced in this response | The deliverable, approved increment, or answered question |
| `open_decisions` | `project_state.md` | Any unresolved questions or deferred choices |
| `project_constraints` | `project.yaml` or stated constraints | Hard limits that options must not violate |

**If context is missing:**
- `current_phase` — if unclear (e.g., session just started), surface 3 clarifying questions instead of next-step options.
- `last_artifact` — if no artifact was just produced, use the most recent approved item from the conversation.
- `open_decisions` — if none recorded, infer likely next steps from the current phase alone.
- `project_constraints` — if none known, options may be generic; note this and suggest running `init_project.py` to load project context.

---

## Output Format

Append this block at the end of the response, after the main artifact or answer:

```
---
**What to do next** (pick one):

**[Recommended] A: <specific, action-verb name>**
Why: <one sentence — must connect to the project's current state, known constraint, or open risk>
Effort: <~N mins | ~N hours | ~1 session | ~N sessions>
Token cost: <low | medium | high>
Command: `python agents-maker/tools/generate_prompt.py "<A description verbatim>"`

**B: <specific, action-verb name>**
Why: <one sentence>
Effort: <estimate> | Token cost: <low | medium | high>

**C: <specific, action-verb name>**
Why: <one sentence>
Effort: <estimate> | Token cost: <low | medium | high>

_Not what you need? Describe your actual next step and the Orchestrator will re-plan._
---
```

---

## Token Cost Key

| Level | Meaning |
|---|---|
| low | Conversation only — no files needed; very short context |
| medium | 3–5 source files needed; normal session size |
| high | Full repo scan or large diff needed; use `project_summary.py` first |

---

## Ranking Rules

**Option A — Recommended** must be:
- The highest-impact move given the current phase and project state
- The lowest-risk choice (reversible, testable, doesn't lock future decisions)
- Directly executable in the next session

**Option B** — A valid alternative with a different priority axis (e.g., speed vs. quality,
breadth vs. depth, technical vs. documentation).

**Option C** — A "don't ignore this later" option: something with lower immediate urgency but
higher future cost if deferred (e.g., a growing tech debt item, an untested path, a doc gap).

---

## Rules

- Never suggest an option that contradicts an already-approved artifact or ADR.
- Options must be specific to this project — not generic advice.
- If the current phase is unclear (e.g., session just started), surface 3 clarifying questions
  instead of next-step options.
- The `Command:` field on Option A always uses the exact phrasing a user can copy-paste.
- If the project has `key_constraints` in `project.yaml`, check each option against them.
- Never repeat an option that was just completed in this session.
