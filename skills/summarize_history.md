# Skill: summarize_history

## Description

Compress a multi-turn conversation history into a structured state block that preserves everything critical (requirements, decisions, constraints, open questions) while discarding redundant exchanges, repeated context, and resolved sub-questions. Used by the Compression Agent to reduce context size before sending to any specialist.

---

## When to invoke

- Conversation history exceeds `history_summarize_after_turns` from the active token policy.
- Total context token count exceeds `max_input_tokens` × 0.75.
- The user requests "summarize our session so far" or "reset context but keep decisions."

---

## Input expectations

| Input | Required | Description |
|---|---|---|
| `history` | Yes | Full conversation history (list of turns) |
| `active_query` | Yes | The user's current or next question — determines what is most relevant to keep |
| `never_drop` | No | Explicit list of items the user marked as critical |

**If required input is missing:**
- `history` — this skill cannot proceed without conversation history. If no history is available, return: "No history to compress — this appears to be a fresh session. Proceed with the active query directly." Do not fabricate history.
- `active_query` — infer from the most recent user message in the history; note the inference explicitly in the output.
- `never_drop` — proceed without; apply the standard "What must never be dropped" rules defined below.

---

## Output format

The skill produces a **Conversation State** block:

```
## Conversation State

**Session goal**: <one sentence: what the user is trying to accomplish overall>

**Completed subtasks**:
- <subtask> → <outcome>
- <subtask> → <outcome>

**Active constraints**:
- Language: <e.g., Python 3.11, no new dependencies>
- Must not change: <API surface, DB schema, etc.>
- Must reuse: <existing utilities, patterns>
- Other: <any hard constraint stated by the user>

**Key decisions made**:
- <decision> (turn N)
- <decision> (turn N)

**Open questions**:
- <question> — <who needs to answer: user | architect | code | unresolved>

**Last action**: <what was produced or agreed in the most recent turn>

**Next action**: <what the user or agent was about to do>
```

---

## What must never be dropped

Regardless of age or apparent redundancy:

- Any requirement prefixed with "must", "never", "always", "required", "constraint".
- Any confirmed architectural decision.
- Any security finding flagged `[SECURITY]`.
- Any item the user marked "remember this" or "keep this in mind."
- The user's most recent message (always retained verbatim in the context block).

---

## Token cost tier

**Low.** The skill itself is lightweight. Input (history) can be large; output (state block) is always compact: 150–350 tokens.

Compression hint: this skill is the primary mechanism for token reduction. Invoke it before other compression steps — it usually provides the largest reduction.

---

## Notes

- The state block is a **lossy** compression. Make the loss explicit: always include a "Not captured" line if anything material was omitted for brevity.
- Do not fabricate decisions. If a decision was discussed but not confirmed, list it under "Open questions" as "Under discussion: <topic>."
- Turn references (e.g., "turn N") help the user verify accuracy without replaying the full history. Include them for key decisions.
