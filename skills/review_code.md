# Skill: review_code

## Description

Perform a structured code review of one or more file snippets. Return a severity-rated issue table covering correctness, security, performance, readability, and test coverage. Each finding includes file:line, issue description, and a concrete recommendation.

---

## When to invoke

- The Code Agent is asked to review or critique existing code.
- The Orchestrator routes a "review this PR" or "audit this file" request.
- A refactoring task requires a baseline assessment before changes.

---

## Input expectations

| Input | Required | Description |
|---|---|---|
| `files` | Yes | One or more file snippets with paths |
| `review_focus` | No | One or more of: `security`, `performance`, `correctness`, `readability`, `test_coverage`, `all` (default: `all`) |
| `language` | No | Programming language (inferred from file extension if omitted) |
| `context` | No | Brief description of what the code does, to avoid false positives |

**If required input is missing:**
- `files` — ask: "Please paste the code files or snippets you want reviewed." Do not produce a review without actual code.
- `review_focus` — default to `all`; note this in the output summary line.
- `language` — infer from file extension or code syntax; if indeterminate, note "Language inferred as [X] — correct if wrong."
- `context` — proceed without it; note any assumptions made about the code's purpose in the Positive Findings section.

---

## Output format

```
## Code Review: <file(s) reviewed>

**Summary**: N critical, N high, N medium, N low, N info

| Severity | File:Line | Category | Issue | Recommendation |
|---|---|---|---|---|
| critical | auth.py:47 | security | SQL query built via string concat | Use parameterized queries |
| high | user_service.py:112 | correctness | `get_user()` returns None without handling | Add None check or raise a typed exception |
| medium | utils.py:23 | performance | List comprehension inside tight loop | Pre-compute outside the loop |
| low | models.py:8 | readability | Variable name `d` is ambiguous | Rename to `user_data` |
| info | api.py:55 | test_coverage | No test covers the 404 path | Add a test case for missing resource |

## Positive Findings
- <bullet: what is done well — not just issues>

## Out of scope
- <bullet: anything noticed but not within the requested review_focus>
```

---

## Severity definitions

| Severity | Meaning |
|---|---|
| `critical` | Bug, security vulnerability, or data corruption risk in production |
| `high` | Likely to cause incorrect behavior under normal conditions |
| `medium` | Degraded performance, poor error handling, or maintainability risk |
| `low` | Style, naming, or minor readability issue |
| `info` | Observation or suggestion; no action required |

---

## Token cost tier

**Medium.** Scales with number of files. Typical output per 100-line file: 200–400 tokens.

Compression hint: for large codebases, filter to `review_focus: security` or `review_focus: correctness` to reduce output. Ask the requester which categories matter most.

---

## Notes

- Always include at least one "Positive Findings" item. Reviews with no positive findings tend to be ignored.
- `[SECURITY]` findings must be present in the table even if `review_focus` does not include security — security is never optional.
- Do not flag style issues as `high` or `critical`. Enforce severity discipline.
- If a file has no issues, return: "No findings for `<file>` at the requested severity level."
