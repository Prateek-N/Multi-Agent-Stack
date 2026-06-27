# Skill: improve_copy

## Description

Review and rewrite microcopy: button labels, placeholder text, error messages, empty states, tooltips, section headings, and instructional text. Output is a before/after table with a brief rationale for each change.

---

## When to invoke

- The UX Agent identifies copy as a friction source.
- The UI Agent needs updated labels to go with a layout change.
- A standalone request targets onboarding copy, error messages, or empty states.

---

## Input expectations

| Input | Required | Description |
|---|---|---|
| `copy_items` | Yes | List of current strings with their UI context |
| `persona` | Yes | Who is reading this copy and what they are trying to do |
| `tone` | No | `professional` \| `friendly` \| `technical` \| `minimal` (default: `professional`) |
| `constraints` | No | Character limits, must-include terms, brand voice rules |

**If required input is missing:**
- `copy_items` absent → ask: "Please share the copy strings you want improved (paste them with their UI location, e.g. 'Submit button label: Submit Form')."
- `persona` absent → infer from project domain (e.g., software → "developer using this tool") and state the assumption explicitly in the output header. Do not block on this.

---

## Output format

```
## Copy Improvements: <screen/feature name>

**Tone**: <detected or specified>
**Persona**: <one-line summary>

| Context | Current copy | Issue | Improved copy | Rationale |
|---|---|---|---|---|
| Submit button | "Submit" | Generic; doesn't describe outcome | "Save changes" | Action-oriented; tells user what happens |
| Error: required field | "Field is required" | Negative framing; no guidance | "Enter your email address" | Tells user exactly what to do |
| Empty state | "No data" | Unexplained; leaves user stuck | "No reports yet. Create your first report →" | Explains state + shows next action |
| Placeholder | "Enter name..." | Redundant with label | "" (remove) | Labels already describe the field |
| Tooltip | "Click to expand" | States the obvious | Remove tooltip entirely | The chevron icon is self-explanatory |

## Unchanged Items
| Item | Reason kept |
|---|---|
| "Cancel" button | Standard affordance; no improvement needed |
```

---

## Token cost tier

**Low.** Typically 150–300 tokens regardless of number of copy items.

Compression hint: this skill is already token-light. No compression needed.

---

## Notes

- **Tone consistency**: all suggestions in a single invocation must match the specified tone. Do not mix friendly and technical voice.
- **Character limits**: if a constraint specifies a character limit (e.g., mobile button label ≤ 20 chars), flag any suggestion that exceeds it.
- **Do not over-improve**: if the current copy is acceptable, mark it in "Unchanged Items". Unnecessary rewrites create churn.
- **Placeholder text**: the default recommendation is to remove placeholders when a label exists. Only suggest placeholder text if the field format is non-obvious (e.g., date format).
