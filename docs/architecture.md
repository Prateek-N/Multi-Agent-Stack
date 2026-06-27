# Architecture

## Overview

This kit uses a **supervisor/specialist** multi-agent pattern. The Orchestrator is the single entry point for user requests. It maintains task state, detects the domain, drives a 6-phase lifecycle, and routes to specialist agents phase by phase. Specialists are stateless: they receive a structured context block and return a structured result.

```
User Request
     │
     ▼
┌─────────────────────────────────────────────────────┐
│                    Orchestrator                     │
│  - detect domain (scoring against domain_profiles)  │
│  - drive 6-phase lifecycle with approval gates      │
│  - route each phase to the right specialist         │
│  - maintain project_state across turns              │
│  - emit project_state.md snapshot after each phase  │
└────────┬────────────────────────────────────────────┘
         │ routes to:
    ┌────┴──────────────────────────────────────────┐
    ▼           ▼            ▼          ▼           ▼
Architect    Code         Execution  Reviewer   Compression
 Agent       Agent         Agent      Agent       Agent
(Ph 1+2)  (Ph 3:         (Ph 3:     (Ph 4:     (cross-cutting)
          software/      other      all
          analytics)     domains)   domains)
    ▲           ▲            ▲
    └──── Supporting specialists ────┘
         UI Agent · UX Agent
         (invoked during Ph 2–3 as needed)
```

---

## Agent Responsibilities

| Agent | File | Phases | Primary inputs | Primary outputs |
|---|---|---|---|---|
| Orchestrator | `orchestrator.md` | 0, 5, all gates | User message, domain_profiles.yaml | `task_profile`, `handoff_package`, routing decisions |
| Architect Agent | `architect_agent.md` | 1 (Requirements), 2 (Solution Design) | Requirements context, domain | `requirements_spec`, `solution_design` |
| Code Agent | `code_agent.md` | 3 (Implementation) | File snippets, solution_design | Code diffs, `work_product`, `build_log` |
| Execution Agent | `execution_agent.md` | 3 (Implementation) | Outline, prior sections, solution_design | Drafted sections, `work_product`, `build_log` |
| UI Agent | `ui_agent.md` | Supporting (Ph 2–3) | Component tree, design tokens | Layout recommendations, component hierarchy |
| UX Agent | `ux_agent.md` | Supporting (Ph 2–3) | Flow description, user persona | Friction points, improvement suggestions |
| Reviewer Agent | `reviewer_agent.md` | 4 (Review) | `work_product`, `build_log` | Severity-rated `refinement_report` |
| Compression Agent | `compression_agent.md` | Cross-cutting | Full context block, token policy | Compressed context, `project_state.md` snapshots |

**Phase 3 routing rule:** Code Agent handles `software` and `data_analytics` domains; Execution Agent handles `content`, `research`, `marketing`, `ops_process`, and `product_design`.

---

## Domain Plug-In System

Domain detection and phase routing are driven entirely by `config/domain_profiles.yaml`. No agent `.md` file encodes domain logic — the Orchestrator reads the registry at session start.

### Detection algorithm

```
score(d) = (strong_signal_matches × 1.0 + weak_signal_matches × 0.4) / 3

If max_score < confidence_threshold (0.40):
    domain = general  →  Orchestrator asks one clarifying question
Elif top-2 scores within ambiguity_threshold (0.10):
    domain_confidence = medium  →  Orchestrator surfaces both candidates
Else:
    domain_confidence = high  →  proceed directly to task_profile
```

A `[domain: <key>]` prefix in the user message bypasses scoring entirely.

### Built-in domains

| Domain key | Typical task types | Phase 3 agent |
|---|---|---|
| `software` | APIs, microservices, scripts, refactors | Code Agent |
| `data_analytics` | Dashboards, pipelines, SQL, metrics | Code Agent |
| `content` | Articles, docs, white papers, guides | Execution Agent |
| `research` | Literature reviews, market studies | Execution Agent |
| `product_design` | PRDs, user stories, wireframes | Execution Agent |
| `marketing` | Campaigns, messaging, launch briefs | Execution Agent |
| `ops_process` | SOPs, runbooks, process maps | Execution Agent |
| `general` | Catch-all when no domain is detected | Execution Agent |

### Adding a new domain

Add one YAML entry to `config/domain_profiles.yaml`. No agent `.md` file changes required:

```yaml
domains:
  legal:
    status: extension
    display_name: "Legal & Compliance"
    description: "Contract reviews, policy documents, regulatory filings."
    detection_signals:
      strong: [contract, clause, regulation, filing, legal]
      weak: [policy, compliance, terms]
    primary_agents:
      task_framing: orchestrator
      requirements: architect_agent
      solution_design: architect_agent
      implementation: execution_agent
      review_refinement: reviewer_agent
      handoff: orchestrator
    artifact_hints:
      solution_design:
        structure_label: "Clause map, jurisdiction scope, document structure"
    token_policy_overrides: {}
```

See `docs/domains.md` for the full schema and step-by-step guide.

---

## Generic Project Lifecycle

Every task — regardless of domain — follows the same 6-phase lifecycle:

| Phase | Output artifact | Primary agent | Approval gate |
|---|---|---|---|
| 0 — Task Framing | `task_profile` | Orchestrator | A/B/C/D: Approve / Revise / Change direction / Abort |
| 1 — Requirements | `requirements_spec` | Architect Agent | A/B/C/D |
| 2 — Solution Design | `solution_design` | Architect Agent (+ UI/UX) | A/B/C/D |
| 3 — Implementation | `work_product` + `build_log` | Code Agent or Execution Agent | Per increment: Approve / Request changes / Change direction |
| 4 — Review | `refinement_report` | Reviewer Agent | Apply all / Apply selected / Discuss |
| 5 — Handoff | `handoff_package` | Orchestrator | Done |

After each approved phase, the Compression Agent emits a `project_state.md` snapshot. Paste it at the start of any future session to resume without replaying history.

Token policies for each phase are defined in `config/token_policies.yaml` under `workflows.generic_project_lifecycle.phases`. See `docs/workflows.md` for phase walkthroughs and interface contracts.

---

## Context Flow

Every agent invocation receives a **context block** with three sections:

```
## Project State
<compact summary produced by context_loaders/project_summary.py>

## Relevant Files
<filtered file list with relevance scores, produced by relevance_filter>

## Conversation State
<semantic summary of prior turns, produced by semantic_summarizer>
```

The Orchestrator assembles this block before routing to a specialist. The Compression Agent can be invoked first to reduce the block if it exceeds the token budget.

---

## Token Optimization Layer

```
Orchestrator
     │
     ├─► Relevance Filter  ── scores files → selects top N
     │         │
     ├─► Semantic Summarizer ── compresses history → state block
     │         │
     └─► Compressor.py  ── applies token_policies.yaml preset
               │
               ▼
         [LLM API call]
```

### Input compression strategies

| Strategy | When applied | What it does |
|---|---|---|
| History summarization | Every N turns (configurable per workflow/phase) or context > 75% | Replaces raw turns with a structured state block |
| Relevance filtering | Every call | Scores files by query relevance; keeps top K above threshold |
| Project summary | Session start | Replaces full repo with a compact summary |
| Snippet truncation | When file > 200 lines | Keeps first 40 + last 40 lines + a gap marker |

### Output compression strategies

| Strategy | Applied via | What it does |
|---|---|---|
| Output style preset | `token_policies.yaml` per workflow + phase | Controls verbosity, format, max response tokens |
| Concise mode instruction | Agent system prompt | Directs agent to use bullet lists, short prose |
| Response length cap | Platform-level setting | Hard token limit on completion |

---

## Routing Logic

The Orchestrator maps each lifecycle phase to the correct agent using `primary_agents` from `config/domain_profiles.yaml`, not hardcoded routing tags. The `config/agents.yaml` `routing_tags` are used for within-phase intent routing (e.g., deciding which skill to invoke).

| Agent | routing_tags (for skill dispatch) | Phase(s) |
|---|---|---|
| Orchestrator | `orchestrate`, `route`, `lifecycle`, `domain` | 0, 5, gates |
| Architect Agent | `architecture`, `requirements`, `design`, `api`, `adr` | 1, 2 |
| Code Agent | `code`, `implement`, `refactor`, `test`, `migrate`, `bug` | 3 (software/analytics) |
| Execution Agent | `write`, `draft`, `document`, `sop`, `research`, `copy` | 3 (other domains) |
| UI Agent | `component`, `layout`, `css`, `design tokens`, `html` | Supporting |
| UX Agent | `flow`, `friction`, `onboarding`, `form`, `user journey` | Supporting |
| Reviewer Agent | `review`, `qa`, `critique`, `audit`, `severity` | 4 |
| Compression Agent | `compress`, `summarize`, `token`, `context`, `resume` | Cross-cutting |

---

## Config Files

### `config/agents.yaml`

Machine-readable agent registry. Fields per agent:

- `name` — identifier used in routing.
- `description` — one-line summary for the Orchestrator's routing prompt.
- `skills` — list of skill identifiers from `skills/`.
- `routing_tags` — keywords that trigger skill dispatch within a phase.
- `domains` — list of domain keys this agent serves as primary.
- `cost_tier` — `low` | `medium` | `high` (approximate relative token cost).
- `default_output_style` — default verbosity preset from `token_policies.yaml`.

### `config/domain_profiles.yaml`

Domain plug-in registry. Fields per domain:

- `detection_signals.strong` / `weak` — keywords scored against user message.
- `primary_agents` — maps each phase name to an agent_id.
- `artifact_hints` — per-phase format hints injected into the solution_design and handoff artifacts.
- `token_policy_overrides` — phase-level token policy adjustments for this domain.

### `config/token_policies.yaml`

Per-workflow and per-phase token policies. Key sections:

- `workflows.<name>` — standalone workflow presets (code_review, feature_implementation, etc.).
- `workflows.generic_project_lifecycle.phases` — per-phase token limits for the 6-phase lifecycle.
- `workflows.generic_project_lifecycle.domains` — domain-specific overrides layered on top of phase defaults.
- `output_styles` — named verbosity presets referenced by workflow policies.

---

## Skill Invocation

Skills are defined in `skills/*.md`. They are structured prompts that an agent includes inline when it needs that capability. Skills are stateless and reusable across agents.

| Skill | Primary agents | When invoked |
|---|---|---|
| `analyze_repo` | Orchestrator, Architect | Session start, no project summary provided |
| `design_api` | Architect Agent | Phase 2, API design task |
| `review_code` | Reviewer Agent, Code Agent | Phase 4 (software domain) |
| `review_layout` | UI Agent, Reviewer Agent | Phase 4 (product_design domain) |
| `improve_copy` | Execution Agent, UX Agent | Phase 3–4 (content/marketing) |
| `write_tests` | Code Agent | Phase 3 (software domain) |
| `summarize_history` | Compression Agent | Turn threshold hit or explicit request |
| `suggest_next` | Orchestrator, Code Agent, Execution Agent, Reviewer Agent | Auto-fires after every approved deliverable — surfaces 3 ranked next moves |
| `compare_approaches` | Orchestrator, Architect Agent | On-demand when user says "compare", "trade-off", or "which approach"; any Phase 2 design branch |
| `animated_website` | UI Agent, Code Agent | Any animation, motion design, or interactive effect request |

---

## Companion Mode

Companion Mode activates when the user's message contains a `## Project Context` block (injected by `generate_prompt.py`) or when `project.yaml` is present in the session context.

In Companion Mode, the Orchestrator appends a structured block at the end of **every** response:

```
---
[Companion] Phase: <current_phase> | Domain: <domain> | Est. token budget used: ~N%

What to do next (pick one):
[Recommended] A: <action>   — Command: python agents-maker/tools/generate_prompt.py "..."
B: <action>
C: <action>
---
```

This block is generated by invoking the `suggest_next` skill. The `compare_approaches` skill fires additionally when the response involves a design decision with ≥ 2 valid paths.

---

## Tooling Layer

Three Python tools implement the Companion Mode workflow:

| Tool | Run | What it does |
|---|---|---|
| `tools/init_project.py` | Once per project | Scans project, detects domain + stack, writes `config/project.yaml`, assembles `system_prompt.md` from all agents + skills, creates `project_state.md` template |
| `tools/generate_prompt.py` | Before every session | Detects domain from problem statement, infers lifecycle phase from `project_state.md`, selects agents and skills, outputs a structured prompt block to paste into any AI tool |
| `tools/validate_kit.py` | After any edit | Runs 8 integrity checks: YAML parse, agent files, skill files, domain coverage, agent references, output styles, domain scoring, file inventory |

**Flow:**
```
init_project.py          → system_prompt.md (paste once into AI tool system prompt)
generate_prompt.py "task" → structured user message (paste before every session)
AI response              → includes [Companion] block with next-step options
Save project_state.md    → generate_prompt.py reads it next session (resumption)
```

---

## LLM Provider Abstraction

Agent specs and skill cards are provider-neutral. Provider-specific surface areas:

1. How system prompts are delivered (see `platforms/`).
2. How tool/function calls are registered (only needed for agentic tool-call loops).
3. The `compressor.py` adapter layer, which has one subclass per provider.

To add a new provider: implement a `ProviderAdapter` subclass in `token_optimization/compressor.py` and add `platforms/<provider>.md`.

---

## Extending the Kit

| Goal | Action |
|---|---|
| Add a new domain | Add entry to `config/domain_profiles.yaml` — no agent `.md` changes required |
| Add a new specialist agent | Create `agents/<name>.md`, register in `agents.yaml` with skills and routing tags |
| Add a new skill | Create `skills/<name>.md`, add skill key to relevant agents in `agents.yaml` |
| Add a new workflow preset | Add entry to `config/token_policies.yaml` `workflows:`, document in `docs/workflows.md` |
| Add a new provider | Subclass `ProviderAdapter` in `compressor.py`, add `platforms/<name>.md` |
| Verify kit integrity | Run `python tools/validate_kit.py` |
