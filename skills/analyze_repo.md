# Skill: analyze_repo

## Description

Walk a repository's file tree and produce a compact, structured summary of the project: detected stack, primary services or modules, main entrypoints, test structure, and key configuration files. Used by the Orchestrator and Architect Agent to build the Project State block at the start of a session.

---

## When to invoke

- Session start, when no project summary is available.
- When routing a task that requires understanding the broader project structure beyond the provided snippets.
- When the Architect Agent needs a service map before designing a new component.

---

## Input expectations

| Input | Required | Description |
|---|---|---|
| `repo_path` | Yes | Root path of the repository |
| `filter_paths` | No | List of subdirectory prefixes to include (e.g., `src/`, `app/`, `services/`) |
| `exclude_patterns` | No | Patterns to exclude (e.g., `node_modules/`, `__pycache__/`, `.git/`) |
| `max_depth` | No | Maximum directory depth to traverse (default: 4) |

In a conversational context, the user provides these via the `context_loaders/repo_tree.py` and `context_loaders/project_summary.py` scripts, and pastes the output.

**If required input is missing:**
- `repo_path` — if no path is provided and no repo context has been pasted, ask: "Please paste the output of `python agents-maker/context_loaders/repo_tree.py` or describe your project's directory structure." Do not produce a summary from nothing.
- `filter_paths` — default to scanning the entire repo up to `max_depth`.
- `exclude_patterns` — default to excluding `node_modules/`, `__pycache__/`, `.git/`, `dist/`, `build/`.
- `max_depth` — default to 4.

---

## Output format

The skill produces a structured text block:

```
## Project Summary

**Stack**: <language(s), runtime version(s), primary framework(s)>
**Build tool**: <e.g., pip + setuptools, npm + webpack, gradle>
**Test framework**: <e.g., pytest, jest, JUnit>
**Containerization**: <Docker | none | Kubernetes manifests present>

## Services / Modules

| Name | Path | Responsibility |
|---|---|---|
| <name> | <path> | <one-line description> |

## Main Entrypoints

| File | Purpose |
|---|---|
| <path> | <what it starts or exports> |

## Key Config Files

| File | Purpose |
|---|---|
| <path> | <what it configures> |

## Test Structure

| Path | Type | Coverage scope |
|---|---|---|
| <path> | unit | integration | e2e | <scope> |
```

---

## Token cost tier

**Medium.** Involves reading file tree and inspecting key files. Output is typically 300–600 tokens.

Compression hint: the output is already compact. Do not summarize it further — it is the basis for all other context in the session.

---

## Notes

- This skill is implemented as `context_loaders/project_summary.py`. In agent sessions without tool access, the user runs it locally and pastes the output.
- If the repo has no recognizable structure, return the raw tree truncated at `max_depth` and note: "Could not detect stack — please specify language and framework manually."
