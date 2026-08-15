# Contributing to agents-maker

Thank you for improving the kit. This guide covers the contribution workflow, standards, and the one required check before any PR.

---

## What to contribute

| Area | Examples |
|---|---|
| **New domain** | Add a YAML entry to `config/domain_profiles.yaml` |
| **New skill** | Add `skills/<name>.md` + register in `config/agents.yaml` |
| **New agent** | Add `agents/<name>.md` + register in `config/agents.yaml` |
| **Platform guide** | Add `platforms/<tool>.md` |
| **Bug fix** | Fix Python tools, agent logic, config errors |
| **Docs** | Improve examples, architecture docs, or platform guides |

---

## Before you start

- Check existing issues and PRs — your idea may already be in progress.
- For large changes (new agent, new domain, refactor), open an issue first to discuss approach.

---

## Contribution workflow

```bash
# 1. Fork and clone
git clone https://github.com/<your-username>/Multi-Agent-Stack
cd Multi-Agent-Stack

# 2. Create a branch
git checkout -b feat/my-new-skill

# 3. Make your changes

# 4. Run the integrity checker — must pass ALL 13 checks before opening a PR
python tools/validate_kit.py

# 5. Commit and push
git add .
git commit -m "feat: add <name> skill"
git push origin feat/my-new-skill

# 6. Open a pull request against main
```

---

## Required: validate_kit.py must pass

Every PR must pass all checks:

```
============================================================
  Result: ALL 13 checks PASSED
============================================================
```

If any check fails, fix it before opening the PR. The CI will also run this automatically.

---

## Standards by contribution type

### Adding a skill (`skills/<name>.md`)

A skill card must include:

- **Trigger condition** — when does this skill fire? (keyword or explicit `[skill: name]`)
- **Required inputs** — what fields must the agent provide?
- **If required input is missing** — explicit fallback for each field (ask user / infer / default / cannot proceed)
- **Output format** — exact structure of the skill's output (headers, tables, code blocks)
- **Token cost tier** — `low` / `medium` / `high`

Register in `config/agents.yaml`:
- Add to `skill_file_map`
- Add to `skills` list of each agent that can invoke it

### Adding a domain (`config/domain_profiles.yaml`)

A domain entry must include:

- `display_name`
- `detection_signals.strong` (≥3 signals)
- `detection_signals.weak` (≥2 signals)
- `primary_agents.implementation`
- `primary_agents.review_refinement`

Run `validate_kit.py` — Check 4 (domain coverage) will verify the new domain is registered everywhere it needs to be.

### Adding an agent (`agents/<name>.md`)

An agent spec must include:

- **Role** — one-line description
- **Activation** — when does the Orchestrator route here?
- **Input contract** — what context block fields does this agent consume?
- **Output contract** — what artifacts does this agent produce?
- **Skills invoked** — which skill cards does this agent use?

Register in `config/agents.yaml` with `agent_id`, `routing_tags`, `cost_tier`, and `skills` list.

---

## Commit message style

```
feat: add legal domain to domain_profiles.yaml
fix: handle empty project.yaml in generate_prompt.py
docs: add Bedrock integration example to platforms/
refactor: consolidate output style definitions
```

---

## Code style (Python tools)

- Python 3.9+ compatible (no walrus operator, no match/case)
- All file I/O wrapped in `try/except` with helpful error messages
- No external dependencies beyond `pyyaml` (listed in `requirements.txt`)
- Run `python tools/validate_kit.py` — it must pass

---

## Questions

Open a GitHub Discussion or file an issue with the `question` label.
