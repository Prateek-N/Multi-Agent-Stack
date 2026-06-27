# Skill: write_process_map

## Description

Document a business or operational process as a structured, executable artifact: numbered step table, RACI matrix, and exception-handling table. Used by the Execution Agent in `ops_process` tasks (Phase 3) and the Architect Agent when designing workflows for any domain.

---

## When to invoke

- User requests an SOP, runbook, procedure, workflow, or process documentation.
- Architect Agent needs to specify an operational process as part of a solution design.
- Review phase identifies a process that lacks owner assignments or exception paths.

---

## Input expectations

| Input | Required | Description |
|---|---|---|
| `process_name` | Yes | Name of the process (e.g., "Incident Response", "Customer Onboarding") |
| `actors` | Yes | List of roles involved (e.g., `["On-call Engineer", "Team Lead", "Customer"]`) |
| `trigger` | Yes | What initiates this process (e.g., alert fired, form submitted, scheduled) |
| `steps` | Yes | Ordered list of steps. Each step: `{action, actor, tool_or_system, output}` |
| `exception_paths` | No | List of known failure conditions and their recovery steps |
| `goal` | No | One-sentence description of the successful outcome |
| `sla` | No | Time constraints (e.g., "acknowledge within 15 min, resolve within 4h") |

**If required input is missing:**
- `process_name` — ask: "What is this process called? (e.g., 'Weekly Deploy', 'Customer Escalation')"
- `actors` — ask: "Who are the roles involved? List each as a job title or system name."
- `trigger` — ask: "What starts this process? (e.g., an alert, a request, a scheduled event)"
- `steps` — ask: "Walk me through the steps. For each, tell me: who does what, using which tool, and what is the output?"
- `exception_paths` — default to "None documented" and note the gap in the output.

---

## Output format

### 1. Process Overview

```
## Process: <process_name>
**Trigger**: <trigger>
**Goal**: <goal or "not specified">
**SLA**: <sla or "not specified">
**Actors**: <comma-separated list>
```

### 2. Step Table

```markdown
## Process Steps

| # | Step | Actor | Tool / System | Output |
|---|---|---|---|---|
| 1 | <action> | <actor> | <tool> | <output> |
| 2 | ... | ... | ... | ... |
```

### 3. RACI Matrix

```markdown
## RACI Matrix

| Step | <Actor 1> | <Actor 2> | <Actor N> |
|---|---|---|---|
| 1 — <step name> | R | A | I |
| 2 — <step name> | C | R | — |

Legend: R = Responsible, A = Accountable, C = Consulted, I = Informed, — = Not involved
```

Each step must have exactly one **A** (Accountable). If no accountable role is clear, flag it: `[A: unassigned — confirm ownership]`.

### 4. Exception-Handling Table

```markdown
## Exception Paths

| Condition | Detected at step | Recovery action | Owner |
|---|---|---|---|
| <failure condition> | <step #> | <what to do> | <role> |
```

If no exception paths were provided, output:
```
## Exception Paths
No exception paths documented. Recommended: add paths for the 2–3 most likely failure conditions.
```

---

## Token cost tier

**Low.** Pure document generation from structured inputs. Typical output: 200–500 tokens.

---

## Notes

- Validate that every step has an actor. If a step has no actor, flag it: `[Actor: unassigned]`.
- RACI matrix rows correspond 1:1 to the steps in the step table.
- If `actors` contains systems (not people), assign them R only, never A.
- For processes with more than 20 steps, suggest splitting into sub-processes at natural phase boundaries.
