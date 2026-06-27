# Workflows

Step-by-step guides for the three primary use cases. Each workflow describes what context to collect, how the Orchestrator routes the request, and which token optimization steps apply.

---

## Workflow 1: Code Assistance

**Use for**: implementing a new feature, refactoring existing code, writing tests, fixing a bug, migrating to a new library.

### Steps

**1. Collect context**

```bash
python context_loaders/project_summary.py --path /your/repo
python context_loaders/repo_tree.py --path /your/repo --filter src/ app/ services/
```

Paste both outputs as the opening message in your session.

**2. State your task**

Be specific. Include:
- What you want (feature, refactor, test, fix).
- Which files or modules are involved (if known).
- Any constraints (language version, framework, must not change API surface).

Example:
> Add a `POST /users/{id}/deactivate` endpoint to `services/user_service.py`. It should soft-delete by setting `is_active=False`. Reuse the existing `UserRepository.update()` method. Add unit tests using the project's existing pytest fixtures.

**3. Orchestrator routing**

The Orchestrator detects routing tags: `code`, possibly `architecture` if a new data model is involved.

- If scope is clear → routes directly to **Code Agent**.
- If a new service or schema is needed → routes to **Architect Agent** first, then **Code Agent**.

**4. Token optimization applied**

| Step | Policy |
|---|---|
| Relevance filter | Selects `user_service.py`, `user_repository.py`, test fixtures, schema files |
| History summarization | Applied if session > 6 turns |
| Output style | `detailed_with_code` (patches + explanation) |

**5. Review output**

The Code Agent returns patch-style diffs or full file replacements. Review for:
- Correctness against stated constraints.
- No invented APIs or methods.
- Tests follow existing fixture patterns.

---

## Workflow 2: Feature Design

**Use for**: designing a new API endpoint, planning a new microservice, creating a data model, writing an ADR.

### Steps

**1. Collect context**

```bash
python context_loaders/project_summary.py --path /your/repo
```

Also collect any relevant existing API specs (e.g., OpenAPI YAML, proto files) and paste as snippets.

**2. State your goal**

Include:
- What the feature does and for whom.
- Integration points with existing services.
- Any non-functional requirements (latency, consistency, auth).

Example:
> Design a notification service that sends transactional emails and in-app notifications. It should be called by the Order Service and User Service. Events should be queued (we use RabbitMQ). Max latency for email delivery: 30s. No new databases — reuse Postgres.

**3. Orchestrator routing**

Detects tag: `architecture`. Routes to **Architect Agent**.

If the output feeds immediately into implementation, Orchestrator sequences **Architect Agent → Code Agent**.

**4. Token optimization applied**

| Step | Policy |
|---|---|
| Relevance filter | Selects existing service entrypoints, queue config, shared schema files |
| Output style | `design_brief` (tables, bullet lists, no inline code unless requested) |

**5. Review output**

The Architect Agent returns:
- Service responsibility summary.
- API contract (endpoint list or interface definition).
- Data flow diagram (text-based).
- Open questions that need answers before implementation.

---

## Workflow 3: UI/UX Improvement

**Use for**: improving a dashboard layout, simplifying an onboarding flow, critiquing a form, improving microcopy.

### Steps

**1. Collect context**

Paste relevant component files and/or describe the UI in plain text. Include:
- Component tree or screen list.
- User persona or primary use case.
- Any specific pain points you are aware of.

```bash
python context_loaders/file_chunker.py --path /your/repo --files components/Dashboard.tsx components/Onboarding/
```

**2. State your goal**

Be specific about whether you want:
- Layout recommendations (→ **UI Agent**).
- Flow critique / friction removal (→ **UX Agent**).
- Both (→ Orchestrator sequences **UX Agent → UI Agent**).

Example:
> Our onboarding has 6 steps. Users drop off at step 3 (company info). The persona is a solo developer signing up for a dev tool. Suggest how to reduce steps and improve the copy on the company info screen.

**3. Orchestrator routing**

- `ux` tag → **UX Agent** for flow critique.
- `ui` tag → **UI Agent** for component/layout recommendations.
- Both tags → **UX Agent** first (restructure flow), then **UI Agent** (implement the restructured flow as components).

**4. Token optimization applied**

| Step | Policy |
|---|---|
| Relevance filter | Selects only the specific screen components, not unrelated components |
| Output style | `concise_bullets` for UX critique; `design_brief` for UI recommendations |
| Snippet truncation | Component files > 200 lines are truncated to props + render section |

**5. Review output**

- UX Agent: numbered list of friction points with severity + suggested fix.
- UI Agent: component hierarchy changes, design token suggestions, layout adjustments.

---

## Workflow 4: Code Review

**Use for**: reviewing a PR, auditing a file for quality/security, checking test coverage.

### Steps

**1. Collect context**

Paste the diff or specific files. For large PRs, use `file_chunker.py` to extract changed files.

**2. State scope**

Specify what to focus on: security, performance, readability, test coverage, API design, etc.

**3. Orchestrator routing**

Routes to **Code Agent** with skill `review_code` invoked.

**4. Token optimization applied**

| Step | Policy |
|---|---|
| Output style | `review_checklist` (severity-rated issues in a table) |
| Max input files | 10 (if PR is larger, filter to highest-risk files first) |

---

## Combining Workflows

Workflows can be chained. The Orchestrator handles sequencing automatically based on routing tag priority:

```
architecture → code → review_code
ux → ui → review_layout → improve_copy
```

For a full feature build (design → implement → test → review), simply state the full goal and let the Orchestrator sequence the specialists. Use the `detailed_with_code` output style for these longer sessions.

---

## Universal Generic Project Lifecycle

A domain-agnostic workflow that applies to any complex task: software, content, research, analytics, product design, marketing, and operational processes. The same six-phase structure is used for all domains; only the agents selected and output formats vary.

For domain-specific details, see [`docs/domains.md`](docs/domains.md).
For token policies per phase, see [`config/token_policies.yaml`](config/token_policies.yaml) under `workflows.generic_project_lifecycle`.

---

### Phase Overview

| # | Phase | Key output artifact | Primary agent(s) |
|---|---|---|---|
| 0 | Task Framing & Domain Detection | `task_profile` | Orchestrator |
| 1 | Requirements & Problem Understanding | `requirements_spec` | Architect/Planner, Orchestrator |
| 2 | Solution Design | `solution_design` | Architect/Planner, UI/UX agents |
| 3 | Implementation / Drafting | `work_product` + `build_log` | Execution Agent, Code Agent (software) |
| 4 | Review, Testing & Refinement | `refinement_report` | Reviewer Agent |
| 5 | Packaging, Handoff & Next Steps | `handoff_package` | Orchestrator, Execution Agent |

Every phase ends with an explicit **approval gate**: the Orchestrator presents a phase summary and asks "Approve / request changes / change direction?" before advancing.

---

### Generic Phase Interface Contracts

Each phase has a domain-neutral interface contract: the minimum inputs it requires, the artifact it must produce, and the validation the Orchestrator runs before accepting it. Domain-specific extensions are additive — they never replace these minimums.

---

**Phase 0 — Task Framing**

| | |
|---|---|
| **Preconditions** | Session start; user's opening message available |
| **Inputs consumed** | User message |
| **Output produced** | `task_profile` |
| **Required fields** | `domain`, `domain_confidence`, `task_type`, `goal`, `constraints[]`, `success_criteria`, `primary_agents[]` |
| **Domain extension fields** | Any domain-specific clarifications captured during framing (e.g., `stack`, `word_count_target`) |
| **Validation before advance** | All required fields non-empty; `domain_confidence` is `high` or `medium`; user has explicitly approved |

---

**Phase 1 — Requirements**

| | |
|---|---|
| **Preconditions** | Approved `task_profile` |
| **Inputs consumed** | `task_profile`, any existing docs/specs/code provided by user |
| **Output produced** | `requirements_spec` |
| **Required fields** | `goals[]`, `non_goals[]`, `deliverables[]` (each with acceptance criteria), `constraints[]` (each tagged by type), `assumptions[]` |
| **Domain extension fields** | Domain-specific constraint types (e.g., `[compliance]` for software/ops, `[tone]` for content/marketing) |
| **Validation before advance** | At least one item in `goals`, `non_goals`, and `deliverables`; all `constraints` have a type tag; user approved |

---

**Phase 2 — Solution Design**

| | |
|---|---|
| **Preconditions** | Approved `requirements_spec` |
| **Inputs consumed** | `requirements_spec`, existing project context |
| **Output produced** | `solution_design` |
| **Required fields** | `context` (problem restatement), `approach` (chosen strategy + rationale), `structure` (domain-specific breakdown), `risks[]` (each with mitigation or open question) |
| **Domain extension fields** | `structure` content varies by domain (see `artifact_hints.solution_design.structure_label` in `domain_profiles.yaml`) |
| **Validation before advance** | `structure` covers all `deliverables` from `requirements_spec`; at least one risk listed; user approved |

---

**Phase 3 — Implementation**

| | |
|---|---|
| **Preconditions** | Approved `solution_design` |
| **Inputs consumed** | `solution_design`, project state, prior approved increments |
| **Output produced** | Growing `work_product` + `build_log` entries |
| **Required fields per increment** | `increment_n`, `description`, `status: approved`, work content (code diff / document section / copy asset) |
| **Domain extension fields** | Increment format varies: diff for software, section heading + body for content, copy asset for marketing |
| **Validation before advance to Phase 4** | All planned increments in `solution_design.structure` are present in `build_log` as `approved`; user signals implementation complete |

---

**Phase 4 — Review**

| | |
|---|---|
| **Preconditions** | Substantially complete `work_product`; approved `requirements_spec` and `solution_design` for comparison |
| **Inputs consumed** | `work_product`, `requirements_spec`, `solution_design` |
| **Output produced** | `refinement_report` |
| **Required fields** | `verdict` (ready_to_ship / minor_revisions / significant_revisions), `findings[]` (each: severity, area, issue, recommendation), `positive_findings[]` (minimum 2 items) |
| **Domain extension fields** | Domain-specific review lens (see `reviewer_agent.md` → Review Lens by Domain) |
| **Validation before advance** | All `critical` and `high` findings resolved; Reviewer Agent emits explicit "ready for handoff" confirmation; user approved |

---

**Phase 5 — Handoff**

| | |
|---|---|
| **Preconditions** | Reviewer Agent confirmation from Phase 4 |
| **Inputs consumed** | `work_product`, all prior artifacts |
| **Output produced** | `handoff_package` |
| **Required fields** | `summary[]` (3-5 bullets), `whats_done[]`, `whats_next.p1[]` (must do), `whats_next.p2[]` (recommended), `whats_next.p3[]` (future) |
| **Domain extension fields** | Domain-specific delivery instructions (env vars for software, key findings table for research, channel calendar for marketing) — see `artifact_hints.handoff.deliverables_label` in `domain_profiles.yaml` |
| **Validation before advance** | `whats_done` matches all `build_log` entries; `whats_next.p1` is non-empty; user confirmed |

---

### Phase 0 — Task Framing & Domain Detection

**Inputs**: User's opening message (any format — goal, problem statement, rough idea).

**Output artifact**: `task_profile`

```
task_profile:
  domain: <software | content | research | data_analytics | product_design | marketing | ops_process>
  task_type: <greenfield | extension | investigation>
  goal: <one sentence>
  constraints: [list]
  inputs_available: [list of what the user already has]
  success_criteria: <how done looks>
  primary_agents: [list selected for this domain]
```

**Primary agent**: Orchestrator
**Supporting agents**: None (Orchestrator works directly with the user here)

**Questions the Orchestrator asks** (output style: `qa_brief`):
1. What is the primary deliverable?
2. Is this greenfield, an extension, or an investigation?
3. Who is the end user or reader?
4. What hard constraints apply (deadline, stack, length, compliance)?
5. What does success look like?

**Token optimization**:
- No file context needed yet.
- History summarization not triggered (typically 1–3 turns).
- After `task_profile` is confirmed, Compression Agent emits a session-start state block.

**Approval gate**: Orchestrator presents the `task_profile` and asks the user to confirm or correct it before proceeding.

---

### Phase 1 — Requirements & Problem Understanding

**Inputs**: Confirmed `task_profile`, any existing documents/specs/code the user provides.

**Output artifact**: `requirements_spec`

```
requirements_spec:
  goals: [list]
  non_goals: [list]
  stakeholders: [list with roles]
  deliverables: [list with acceptance criteria]
  constraints: [{type, description}]
  assumptions: [list of inferred items]
```

**Primary agent**: Architect/Planner
**Supporting agents**: Orchestrator (drives clarification loop)

**Questions asked** (output style: `requirements_spec`):
- What must the solution do vs. what is explicitly out of scope?
- Who are the stakeholders and what does each need?
- What quality/compliance/style constraints apply?
- What existing assets, systems, or knowledge can be reused?

**Token optimization**:
- Relevant files filtered in (e.g., existing spec, codebase summary, prior research).
- `max_input_files: 5`, `max_input_tokens: 14000`.
- Output style: `requirements_spec`.

**Approval gate**: Orchestrator presents the `requirements_spec` in full and asks for approval before solution design begins.

---

### Phase 2 — Solution Design

**Inputs**: Approved `requirements_spec`, existing project context.

**Output artifact**: `solution_design`

Structure (consistent skeleton across all domains):
- **Context** — problem restated in one paragraph.
- **Approach** — chosen strategy and rationale.
- **Structure** — domain-specific breakdown (architecture / outline / methodology / campaign stages).
- **Risks & Open Questions** — blockers and decisions needed before implementation.

**Primary agent**: Architect/Planner
**Supporting agents**: UI Agent (presentation/interface layer), UX Agent (experience/flow layer)

**Domain-specific structure output**:
| Domain | "Structure" section contains |
|---|---|
| `software` | Service map, API contract, data model, ADR |
| `content` | Document outline (H-tree), style guide, argument map |
| `research` | Research question hierarchy, methodology, source list, analysis framework |
| `data_analytics` | Data model, metric definitions, pipeline DAG |
| `product_design` | Feature brief, user journey, screen flow, component hierarchy |
| `marketing` | Campaign stages, messaging framework, channel plan |
| `ops_process` | Process map, RACI matrix, exception-handling table |

**Token optimization**:
- `max_input_files: 5`, `max_input_tokens: 12000`.
- Output style: `solution_design`.
- Compression Agent compresses requirements discussion into `requirements_spec` before this phase.

**Approval gate**: Full `solution_design` artifact presented. Explicit approval before any implementation begins.

---

### Phase 3 — Implementation / Drafting

**Inputs**: Approved `solution_design`, project state.

**Output artifact**: `work_product` (growing) + `build_log`

Each increment follows this structure (output style: `implementation_slice`):
```
Increment Plan:
- This slice: <what is being produced now>
- Depends on: <prior approved increment or design decision>
- Next slice: <what comes after>

[work product content — code diff, document section, research note, copy asset]

Approve this increment / request changes / change direction?
```

**Primary agent**: Code Agent (software), Execution Agent (all other domains)
**Supporting agents**: UI Agent, UX Agent (for design-heavy domains)

**Token optimization**:
- `max_input_files: 6`, `max_input_tokens: 18000`.
- History summarized after 5 turns (long phase).
- Output style: `implementation_slice`.
- `build_log` appended to project state after each approved increment.

**Approval gate**: After each increment. User may approve, request changes, or redirect to a different part of the solution.

---

### Phase 4 — Review, Testing & Refinement

**Inputs**: Completed (or near-complete) `work_product`, `requirements_spec`, `solution_design`.

**Output artifact**: `refinement_report`

```
refinement_report:
  verdict: <ready_to_ship | minor_revisions | significant_revisions>
  findings: [{severity, area, issue, recommendation}]
  positive_findings: [list]
  applied_changes: [list after iteration]
```

**Primary agent**: Reviewer Agent
**Supporting agents**: Code Agent (for software fixes), Execution Agent (for content/copy fixes)

**Review lens by domain**:
| Domain | What is reviewed |
|---|---|
| `software` | Correctness, edge cases, security, test coverage, performance |
| `content` | Logical flow, claims vs. evidence, style consistency, reading level |
| `research` | Rigor, coverage gaps, bias, source credibility |
| `data_analytics` | Metric correctness, NULL handling, grain consistency |
| `marketing` | Brand alignment, CTA clarity, funnel coherence |
| `ops_process` | Edge case coverage, ownership clarity, compliance |

**Token optimization**:
- `max_input_files: 8`, `max_input_tokens: 20000`.
- Output style: `critique_summary`.
- Compression Agent summarizes prior implementation turns before this phase runs.

**Approval gate**: After review findings are presented and changes applied, Reviewer Agent confirms: "All critical/high items resolved — ready to proceed to handoff?" User approves.

---

### Phase 5 — Packaging, Handoff & Next Steps

**Inputs**: Approved `work_product`, all prior artifacts.

**Output artifact**: `handoff_package`

```
handoff_package:
  summary: [3–5 bullets]
  how_to_use: [numbered steps]
  whats_done: [list]
  whats_next:
    p1_must_do: [list]
    p2_recommended: [list]
    p3_future: [list]
```

**Primary agent**: Orchestrator
**Supporting agents**: Execution Agent (drafts domain-specific instructions)

**Token optimization**:
- `max_input_tokens: 8000` (context is now the final artifact + project state, not raw files).
- Output style: `handoff_package`.
- After handoff is confirmed, Compression Agent archives the full `project_state.md` snapshot for future sessions.

**Approval gate**: Final — user confirms the handoff package is complete.

---

### Domain Examples

#### Example A — Software: Complaint-Tracking Microservice

**User**: "Build a microservice that tracks user complaints with SLAs for an Indian government portal."

| Phase | What happens |
|---|---|
| 0 — Task Framing | Orchestrator detects domain: `software`, type: `greenfield`. Asks: stack? team? SLA values? existing auth? Produces `task_profile`. |
| 1 — Requirements | Architect/Planner elicits: complaint lifecycle states, SLA thresholds, notification triggers, audit requirements. Produces `requirements_spec` with compliance constraint `[compliance: RTI Act]`. |
| 2 — Solution Design | Architect/Planner produces: REST API contract (POST /complaints, GET /complaints/{id}, PATCH /complaints/{id}/escalate), Postgres data model, SLA-check background job design, ADR for queue choice. |
| 3 — Implementation | Code Agent delivers: data models → repository layer → service layer → API routes → SLA job → tests. One component per increment. |
| 4 — Review | Reviewer Agent: flags missing index on `complaints.status`, missing auth on escalation endpoint, no test for SLA breach notification. Code Agent applies fixes. |
| 5 — Handoff | Docker setup instructions, migration command, env var list, recommended Phase 2 features (dashboard, bulk export). |

**Project state evolution (abbreviated)**:
```
Turn 2:  task_profile confirmed (domain: software, greenfield)
Turn 5:  requirements_spec approved (7 endpoints, 3 SLA tiers)
Turn 8:  solution_design approved (ADR: RabbitMQ for SLA notifications)
Turn 18: work_product complete (8 increments, 12 files)
Turn 21: refinement_report: 2 critical fixed, 3 medium fixed
Turn 23: handoff_package confirmed
```

---

#### Example B — Research: Market Research Brief

**User**: "Write a 5-page market research brief on algorithmic trading adoption among Indian retail traders."

| Phase | What happens |
|---|---|
| 0 — Task Framing | Orchestrator detects domain: `research`, type: `greenfield`. Asks: audience (technical or executive?), sources (public data only?), 5-page = ~2500 words?, deadline. Produces `task_profile`. |
| 1 — Requirements | Architect/Planner elicits: key research questions (adoption rate, barriers, regulatory context, platform comparison), audience (fintech analyst, not academic), tone (professional, data-driven). |
| 2 — Solution Design | Architect/Planner produces: research question tree (3 primary + 8 sub-questions), document outline (Executive Summary, Market Size, Adoption Drivers, Barriers, Regulatory Landscape, Platform Comparison, Outlook), seed source list, analysis framework (PESTLE for barriers). |
| 3 — Drafting | Execution Agent drafts section by section: Executive Summary → Market Size → Adoption Drivers → Barriers → Regulatory → Platform Comparison → Outlook. Each section ~350–400 words. |
| 4 — Review | Reviewer Agent checks: unsupported claims (3 flagged), missing SEBI regulatory context (high severity), inconsistent use of "algo trading" vs. "algorithmic trading". All fixed. |
| 5 — Handoff | Final 2,650-word document, key findings table (5 rows), limitations section, 3 recommended follow-up research questions. |

**Project state evolution (abbreviated)**:
```
Turn 2:  task_profile confirmed (domain: research, 2500 words, fintech analyst audience)
Turn 4:  requirements_spec approved (3 research questions, PESTLE framework)
Turn 6:  solution_design approved (7-section outline, seed sources)
Turn 16: work_product complete (7 section drafts)
Turn 19: refinement_report: 1 high fixed, 2 medium fixed
Turn 21: handoff_package confirmed
```
