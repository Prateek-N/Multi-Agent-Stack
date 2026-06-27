# Domain Profiles

Domains are plug-in profiles that control how the Orchestrator routes agents, what artifact formats are expected, and which token policies apply during the `generic_project_lifecycle`. The full machine-readable registry lives in [`config/domain_profiles.yaml`](../config/domain_profiles.yaml).

**Adding a new domain requires only a YAML entry — no changes to any agent `.md` file.**

---

## Domain Profile Schema

Each entry in `config/domain_profiles.yaml` must include the following fields:

| Field | Required | Description | Example |
|---|---|---|---|
| `status` | required | `built_in` or `extension` | `extension` |
| `display_name` | required | Human-readable label | `"Legal & Compliance"` |
| `description` | required | One-sentence domain description | `"Contract reviews, policy docs, regulatory filings."` |
| `detection_signals.strong` | required | Keywords scoring 1.0 each toward this domain | `[contract, clause, regulation, filing]` |
| `detection_signals.weak` | required | Keywords scoring 0.4 each toward this domain | `[legal, policy, compliance]` |
| `primary_agents` | required | Phase → agent_id map for all 6 lifecycle phases | See below |
| `artifact_hints` | optional | Format hints injected into `solution_design` and `handoff_package` | See below |
| `token_policy_overrides` | optional | Phase-level overrides (empty `{}` = use global defaults) | See below |

### `primary_agents` map

Must cover all 6 lifecycle phases. The only field you typically vary is `implementation`:

```yaml
primary_agents:
  task_framing: orchestrator
  requirements: architect_agent
  solution_design: architect_agent
  implementation: execution_agent    # use code_agent when primary output is code
  review_refinement: reviewer_agent
  handoff: orchestrator
```

### `artifact_hints` (optional)

Injected by the Orchestrator into specialist agent context to populate domain-specific sections:

```yaml
artifact_hints:
  solution_design:
    structure_label: "What the Structure section should contain for this domain"
    structure_note: "Constraint or convention the agent should follow"
  handoff:
    deliverables_label: "What to list under What's Done in the handoff package"
```

### `token_policy_overrides` (optional)

Override any field from `config/token_policies.yaml` for specific phases:

```yaml
token_policy_overrides:
  implementation:
    max_input_files: 4
    max_input_tokens: 12000
```

Leave as `{}` to inherit global defaults.

---

## Built-in Domains

The kit ships with 7 built-in domains plus the `general` catch-all. Full signal lists, agent mappings, and artifact hints are in `config/domain_profiles.yaml`.

| Domain key | Typical deliverables | Implementation agent | Detection signals (sample) |
|---|---|---|---|
| `software` | APIs, services, code files, test suites, ADRs | Code Agent | code, api, deploy, refactor, bug |
| `content` | Reports, guides, documentation, articles | Execution Agent | write, article, report, document, draft |
| `research` | Research briefs, market analyses, literature reviews | Execution Agent | research, analysis, study, findings |
| `data_analytics` | Dashboards, pipelines, metric definitions, SQL | Code Agent | dashboard, pipeline, sql, dbt, kpi |
| `product_design` | PRDs, user stories, wireframe specs, service blueprints | Execution Agent | product, feature, prd, wireframe, persona |
| `marketing` | Campaign briefs, copy assets, content calendars | Execution Agent | campaign, messaging, funnel, cta, launch |
| `ops_process` | SOPs, runbooks, RACI matrices, process maps | Execution Agent | process, sop, raci, runbook, playbook |
| `general` | Any task — catch-all fallback | Execution Agent | (never auto-detected) |

For per-phase workflow details, see the phase walkthroughs in [`docs/workflows.md`](workflows.md).

---

## Adding a New Domain

**No core agent file needs to change.** Follow these steps:

### Step 1 — Add a profile entry to `config/domain_profiles.yaml`

Copy the template below and fill in every required field:

```yaml
  your_domain_key:            # lowercase_underscores, no spaces
    status: extension
    display_name: "Your Domain"
    description: "One sentence describing what this domain produces."
    detection_signals:
      strong: [keyword1, keyword2, keyword3]
      weak: [keyword4, keyword5]
    primary_agents:
      task_framing: orchestrator
      requirements: architect_agent
      solution_design: architect_agent
      implementation: execution_agent   # or code_agent for code-heavy work
      review_refinement: reviewer_agent
      handoff: orchestrator
    artifact_hints:
      solution_design:
        structure_label: "What the Structure section of solution_design should contain"
        structure_note: "One constraint or convention agents must follow for this domain"
      handoff:
        deliverables_label: "What to list in the handoff package under What's Done"
    token_policy_overrides: {}
```

### Step 2 — Optionally create a domain extension doc

For deep per-phase guidance, create `docs/domain_extensions/<your_domain_key>.md`. This is purely reference documentation — agents do not require it. Use the phase-notes table format:

```markdown
# <Domain Name> — Phase Notes

| Phase | Notes |
|---|---|
| Task Framing | What to detect and what questions to ask |
| Requirements | What domain-specific constraints to capture |
| Solution Design | What the Structure section must include |
| Implementation | Increment strategy and output format |
| Review | What the Reviewer Agent focuses on |
| Handoff | What the handoff package includes |
```

### Step 3 — Optionally add token policy overrides

If your domain needs tighter or looser token limits, add them to `token_policy_overrides` in your profile entry. No changes to `token_policies.yaml` are needed.

### Step 4 — Verify detection

Start a session using strong signal keywords from your new domain. The Orchestrator should detect it with `domain_confidence: high`. If detection is unreliable, add more specific strong signals to your profile.

---

## General Domain (Catch-All)

When no domain scores above the `confidence_threshold` (default: 0.40), the Orchestrator falls back to `general`:

1. Sets `domain = general`, `domain_confidence = low`.
2. Emits one clarifying question before producing the `task_profile`:
   > "I wasn't sure of the domain for this task. Is this closest to: software, content, research, data/analytics, product design, marketing, ops/process — or something else entirely?"
3. If the user names a domain from the list, re-runs detection with that domain and proceeds.
4. If the user says "something else" or names an unlisted domain, continues with `domain = general`.

The `general` domain uses permissive token policies, routes `implementation` to the Execution Agent, and produces artifacts conforming to the domain-neutral minimum schemas (see the Phase Interface Contracts in [`docs/workflows.md`](workflows.md)).
