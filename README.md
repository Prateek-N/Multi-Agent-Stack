# agents-maker

> Clone once. Use forever. Every AI session becomes structured, token-efficient, and decision-aware.

**agents-maker** is a multi-agent assistant kit you drop into any project. It acts as intelligent middleware between your problem statement and any AI tool — Claude, Codex, Antigravity, or anything else. Instead of dumping raw context into a chat window, you give it your stack, constraints, and task — and it routes to the right specialists, enforces a token budget, and always tells you what to do next.

**The key insight**: AI quality is bounded by context quality. agents-maker teaches you exactly what context to give, structures it automatically, and makes every session resume-able without replaying history.

---

## What It Does

**Without agents-maker** — every AI session starts from scratch. You re-explain the project, the AI gives generic output, you spend tokens rediscovering context, and at the end you wonder what to do next.

**With agents-maker:**

| Without | With |
|---|---|
| Re-explain project every session | `project_state.md` resumes automatically |
| AI gives generic patterns | Specialist agent uses your actual stack |
| Wrong domain, wrong agent | Domain auto-detected from task description |
| Bloated context, slow responses | Token budget enforced per phase and domain |
| "What do I do next?" | 3 ranked next steps after every response |
| One-size-fits-all output | 11 output styles matched to phase and task |

- **Domain is auto-detected** from your task description (software, content, research, marketing, analytics, product design, ops)
- **8 specialist agents** activate only when relevant — Orchestrator routes, you never name an agent
- **Token budget is enforced** — context is compressed to fit the right window per phase
- **Next steps are always surfaced** — after every response, 3 ranked options appear
- **State persists across sessions** — `project_state.md` resumes long projects without replaying history
- **Works with any LLM** — pure Markdown + YAML, no provider lock-in, no API keys required

---

## Quickstart

### Step 1 — Clone into your project

```bash
git clone https://github.com/<your-username>/agents-maker
```

### Step 2 — Load the system prompt (once)

Paste `system_prompt.md` into your AI tool as the **system prompt** or Project Knowledge. It contains all 8 agents and 10 skills pre-assembled (~24K tokens). Do this once per project — it stays loaded.

### Step 3 — Fill the message template before every session

Open `PROMPT_TEMPLATE.md`, fill in your project context and task, and paste it as your next message:

```
## Project Context
Name: my-app | Stack: Python, FastAPI | Domain: software

## Session State
Session 1 — starting fresh

## Task
Add rate limiting to the auth service
```

That's the zero-Python workflow. No installation required.

---

## Optional: Companion Mode CLI (Python)

If you have Python and want automation — auto domain detection, phase inference, session state tracking:

```bash
# One-time bootstrap
python agents-maker/tools/init_project.py

# Before every session (generates the message template automatically)
python agents-maker/tools/generate_prompt.py "your task here"
```

```
============================================================
  PASTE THIS AS YOUR NEXT MESSAGE
  Project: my-app | Domain: software (high) | Phase: implementation
  Est. tokens: ~3,800 | Agents: orchestrator, code_agent
============================================================

## Project Context
Name: my-app | Stack: python, fastapi, postgres | Domain: software

## Session State
Phase: implementation | Approved: requirements_spec, solution_design

## Task
add rate limiting to the auth service

## Domain & Routing
Domain: software (confidence: high, score: 1.33)
Suggested phase: implementation
Active agents: orchestrator, code_agent
Active skills: review_code, write_tests, suggest_next
============================================================
```

---

## Context Guide — What to Give the AI

The quality of every AI response is bounded by the context you provide. This section shows exactly what fields matter, why, and what good vs weak input looks like.

### The 5 Context Layers

Every session message has five layers. The more you fill in, the sharper the output:

| Layer | Field | Impact if missing |
|---|---|---|
| **Project identity** | Name, Stack | AI uses generic patterns instead of your actual technology |
| **Domain** | Domain key | AI may mis-route (software task treated as content) |
| **Constraints** | Key constraints | AI proposes solutions you can't use |
| **Session state** | Phase + approved artifacts | AI restarts from scratch instead of continuing |
| **Task specificity** | Concrete, scoped description | AI asks 5 clarifying questions before doing anything |

---

### Project Context — What Each Field Unlocks

```
## Project Context
Name: auth-service
Stack: Python 3.11, FastAPI, PostgreSQL 15, Redis 7, Docker
Domain: software
Key constraints: no breaking changes to /login, Redis already in use, must support 10k req/min
```

**Name** — used in all artifact headers and `project_state.md`. Keep it short, no spaces.

**Stack** — the Code Agent and Architect Agent use this to pick the right patterns, libraries, and idioms. Be specific: `"Python"` is weak; `"Python 3.11, FastAPI, PostgreSQL 15"` is strong. Include version numbers if they matter.

**Domain** — controls which specialist agents activate. If you skip it, the Orchestrator scores your task description automatically. Force it with `[domain: X]` in the Task line when you know it:
```
## Task
[domain: ops_process] Write a runbook for Redis failover.
```

**Key constraints** — the single highest-ROI field. Constraints eliminate entire classes of wrong answers before the AI starts:

| Weak (no constraints) | Strong (constraints given) |
|---|---|
| AI suggests a new caching library | AI uses your existing Redis setup |
| AI proposes a breaking API change | AI works around the existing /login contract |
| AI writes a 4,000-word document | AI writes within your 800-word limit |

---

### Task Specificity — Good vs Weak

The task description is where most context is lost. Be concrete about the deliverable, not the problem.

| Weak task | Strong task |
|---|---|
| `fix the bug` | `Fix the 500 error on POST /auth/refresh when the Redis key has expired — stack trace in issue #47` |
| `improve the UI` | `Redesign the signup form: reduce fields from 9 to 5, add inline validation, mobile-first` |
| `write blog post` | `Write a 1,200-word technical post for senior engineers on our REST→GraphQL migration: what broke, what we learned, 3 concrete takeaways` |
| `add tests` | `Write pytest tests for RedisRateLimiter: happy path, limit exceeded, bypass for internal IPs (10.x.x.x), Redis connection failure` |
| `review the code` | `Review the new auth middleware for security issues — focus on token validation, rate limit bypass vectors, and session fixation` |

**The pattern**: Deliverable + Scope + Success criteria. Three sentences max.

---

### Code Context — How to Attach Your Repo

For software and data tasks, paste the repo tree and key file excerpts into your session message. The context loaders generate these automatically:

```bash
# Generate repo tree (paste into session message)
python agents-maker/context_loaders/repo_tree.py

# Generate project summary (stack, structure, entry points)
python agents-maker/context_loaders/project_summary.py

# Split a large file into token-safe chunks
python agents-maker/context_loaders/file_chunker.py src/auth/middleware.py
```

Or attach them manually — paste the output directly after your `## Task` block:

```
## Task
Add rate limiting to the FastAPI auth service.

## Repo Context
src/
├── auth/
│   ├── middleware.py     ← rate limiting goes here
│   ├── models.py
│   └── routes.py
├── core/
│   └── redis.py          ← existing Redis client
config/
└── settings.py           ← RATE_LIMIT_* env vars defined here

Key file — src/core/redis.py:
[paste relevant excerpt]
```

The more targeted the file excerpt, the less the AI has to guess about your existing patterns.

---

### Session State — How to Resume Without Replay

After each phase is approved, ask the AI:
```
Produce an updated project_state.md for this session.
```

Paste what it returns into your next session's `## Session State` block. The Compression Agent reads it and jumps directly to the current phase — no re-explaining, no token waste.

A complete session state looks like this:

```yaml
# project_state.md
schema_version: "1.0"

## Current Phase
implementation

## Approved Artifacts
- task_profile: add sliding-window rate limiter to auth service
- requirements_spec: 100 req/min per IP, Redis-backed, bypass for 10.x.x.x, no /health limit
- solution_design: FastAPI middleware, sliding window counter, Redis ZSET, X-RateLimit-* headers

## Build Log
- Increment 1: RedisRateLimiter class + ZSET logic ✓
- Increment 2: FastAPI middleware integration ✓

## Open Decisions
- Should /health bypass be configurable or hard-coded?

## Session Notes
Session 4 — tests pending, /health decision pending
```

---

### Domain-Specific Context Tips

| Domain | Most important context to include |
|---|---|
| `software` | Stack versions, existing patterns, file paths, relevant code excerpts |
| `content` | Target audience, tone, word count, format (blog/newsletter/doc), examples you like |
| `research` | Question to answer, scope limits, preferred citation style, sources to exclude |
| `data_analytics` | Data schema or sample rows, metrics that matter, existing tools (dbt/Looker/etc.) |
| `product_design` | User persona, current flow (numbered steps), pain point, platform (web/iOS/Android) |
| `marketing` | ICP (ideal customer profile), channel, brand voice, competitor positioning |
| `ops_process` | Team size, existing tools, compliance requirements, who runs the runbook |

---

### Phase-Based Context — What to Include Per Phase

The Orchestrator drives 6 phases. Different context matters at each:

| Phase | Add this to your session message |
|---|---|
| **0 — Framing** | Full project context + constraint list. Let the AI ask clarifying questions. |
| **1 — Requirements** | Any non-negotiables, stakeholder constraints, timeline. |
| **2 — Design** | Existing system diagrams or structure if relevant; previous ADRs. |
| **3 — Implementation** | Relevant code excerpts, file paths, test patterns already in use. |
| **4 — Review** | What success looks like, known edge cases, compliance checklist if any. |
| **5 — Handoff** | Deployment target, who receives the handoff, format preferences. |

---

### Forcing a Skill

Skills fire automatically, but you can invoke any skill explicitly by naming it in your task:

```
## Task
[skill: compare_approaches] Compare Redis sliding window vs token bucket for our rate limiter.

## Task
[skill: animated_website] Build a scroll-driven entrance animation for the hero section using GSAP.

## Task
[skill: review_code] Security review of src/auth/middleware.py — focus on token validation.
```

---

## Command Reference

```bash
# Bootstrap a new project (run once)
python agents-maker/tools/init_project.py
python agents-maker/tools/init_project.py --path /your/project

# Generate a prompt before any AI session
python agents-maker/tools/generate_prompt.py "describe your task"

# Force a specific lifecycle phase
python agents-maker/tools/generate_prompt.py "write integration tests" --phase implementation

# Full mode: prepend the entire system prompt (for platforms without persistent system prompts)
python agents-maker/tools/generate_prompt.py "your task" --full

# Run after any edits to verify kit integrity
python agents-maker/tools/validate_kit.py
```

---

## The 8 Specialist Agents

The Orchestrator routes your task to the right specialists automatically. You never call them by name.

| Agent | What it handles |
|---|---|
| **Orchestrator** | Entry point — detects domain, drives 6-phase lifecycle, aggregates output |
| **Architect / Planner** | System design, API contracts, research plans, campaign strategy, process maps |
| **Code Agent** | Software implementation, refactoring, test generation (software + analytics) |
| **Execution Agent** | Non-code work — documents, research sections, marketing copy, SOPs, runbooks |
| **UI Agent** | Component hierarchy, layout, design tokens, accessibility, landing pages |
| **UX Agent** | Flow critique, onboarding sequences, funnel analysis, friction identification |
| **Reviewer Agent** | QA for any domain — severity-rated reviews, edge cases, brand alignment |
| **Compression Agent** | Token budget enforcement, context compression, cross-session resumption |

---

## The 6-Phase Lifecycle

Every task — code, content, research, marketing, ops — runs through the same structure:

| Phase | What happens | Output |
|---|---|---|
| 0 — Task Framing | Orchestrator interprets intent, detects domain, sets constraints | `task_profile` |
| 1 — Requirements | Architect clarifies scope, surfaces ambiguities | `requirements_spec` |
| 2 — Solution Design | Architect proposes approach; UI/UX agents join for design tasks | `solution_design` |
| 3 — Implementation | Code Agent (software) or Execution Agent (everything else) builds | `work_product` |
| 4 — Review | Reviewer Agent critiques, flags issues, suggests fixes | `refinement_report` |
| 5 — Handoff | Orchestrator packages deliverables and surfaces next-project options | `handoff_package` |

Each phase ends with an **approval gate** (A/B/C options). The AI never proceeds to the next phase without your sign-off. Small tasks can merge phases — the Orchestrator proposes this automatically.

---

## The 10 Skill Cards

Skills are reusable capability definitions that agents invoke. They define exact output formats so responses are always structured.

| Skill | Triggered by |
|---|---|
| `analyze_repo` | Any session that starts with a code repo |
| `design_api` | API design, schema, contract decisions |
| `review_code` | Code review, QA, audit requests |
| `review_layout` | UI/UX critique, layout review |
| `improve_copy` | Writing quality, tone, clarity improvement |
| `write_tests` | Test generation, coverage requests |
| `summarize_history` | Cross-session compression, context handoff |
| `suggest_next` | Auto-fires after every deliverable — 3 ranked next moves |
| `compare_approaches` | "compare", "trade-off", "which approach" — structured decision table |
| `animated_website` | CSS/GSAP/Framer Motion animation plans and production-ready code |

---

## 8 Built-In Domains

Domain detection is automatic. Prefix with `[domain: X]` to force it.

| Domain | Example tasks | Implementation agent |
|---|---|---|
| `software` | build API, fix bug, refactor service | Code Agent |
| `content` | write blog post, draft newsletter, edit article | Execution Agent |
| `research` | literature review, competitive analysis, synthesis | Execution Agent |
| `data_analytics` | build dashboard, analyze funnel, clean dataset | Code Agent |
| `product_design` | design onboarding flow, map user journey | Execution Agent + UI/UX |
| `marketing` | go-to-market strategy, campaign copy, brand guide | Execution Agent + UX |
| `ops_process` | write SOP, design runbook, document process | Execution Agent |
| `general` | fallback — Orchestrator asks clarifying questions |  |

Add a new domain with a YAML entry in `config/domain_profiles.yaml` — no agent files change.

---

## Companion Mode: What the AI Returns

When `system_prompt.md` is loaded, every AI response automatically ends with:

```
---
[Companion] Phase: implementation | Domain: software | Est. token budget used: ~42%

What to do next (pick one):

[Recommended] A: Write unit tests for the rate-limiting middleware
Why: Coverage is the only open item before this increment is reviewable.
Effort: ~30 mins | Token cost: low
Command: `python agents-maker/tools/generate_prompt.py "write unit tests for rate-limiting middleware"`

B: Open Phase 4 review on the full auth service
Why: The reviewer agent can flag edge cases before the feature ships.
Effort: ~1 session | Token cost: medium

C: Document the rate-limiting config in the runbook
Why: Ops teams will need this when rate limits need tuning in production.
Effort: ~20 mins | Token cost: low
---
```

You always know what to do next. No planning overhead between sessions.

---

## Cross-Session Resumption

After each approved phase, the Compression Agent emits a `project_state.md`. Save it:

```bash
# Paste what the AI gives you into:
agents-maker/project_state.md
```

Next session, `generate_prompt.py` reads it automatically and resumes from where you left off — no need to re-explain anything.

---

## Token Optimization

The kit enforces a token budget per phase and domain, defined in `config/token_policies.yaml`:

- **Per-phase limits**: implementation phases get more tokens than framing phases
- **Per-domain overrides**: product_design gets UI/UX context; software gets code context
- **Relevance filtering**: files are scored and ranked — only the most relevant are included
- **History compression**: raw discussion turns are dropped after each phase; only approved artifacts are kept

Run `--full` mode only on platforms without persistent system prompts. Otherwise, keep `system_prompt.md` in the system slot and run standard `generate_prompt.py` before each session.

---

## Works With Any AI Tool

| Platform | How to use |
|---|---|
| **Claude** | Paste `system_prompt.md` into Project Knowledge or the system prompt field. See [`platforms/claude.md`](platforms/claude.md). |
| **OpenAI / Codex** | Upload to Assistants via file_search or paste as system message. See [`platforms/openai.md`](platforms/openai.md). |
| **Antigravity** | Map phases to pipeline stages. See [`platforms/antigravity.md`](platforms/antigravity.md). |
| **Any other tool** | Use `--full` flag — one self-contained paste includes everything. |

---

## Validate the Kit

After any edits, run the integrity checker:

```bash
python agents-maker/tools/validate_kit.py
```

Runs 11 checks: YAML parse, agent files + structure, skill files + structure, domain coverage, agent references, output styles, domain scoring, file inventory, compressor dry-run.

---

## Repository Map

```
agents-maker/
├── README.md
├── CHANGELOG.md                     ← version history
├── CONTRIBUTING.md                  ← contribution guide + standards
├── LICENSE                          ← MIT
├── quickstart.sh                    ← one-command setup (macOS / Linux / WSL)
├── quickstart.ps1                   ← one-command setup (Windows PowerShell)
├── system_prompt.md                 ← paste this into your AI tool once (all agents + skills)
├── PROMPT_TEMPLATE.md               ← fill this in before every session (no Python needed)
├── .github/
│   └── workflows/
│       └── validate.yml             ← CI: runs validate_kit.py on every push/PR
├── docs/
│   ├── architecture.md              ← agent graph, context flow, design decisions
│   ├── workflows.md                 ← lifecycle phases, interface contracts
│   └── domains.md                   ← domain plug-in schema + built-in domain cards
├── agents/
│   ├── orchestrator.md              ← phase driver, domain detection, Companion Mode
│   ├── architect_agent.md           ← requirements + solution design (all domains)
│   ├── code_agent.md                ← software/data implementation
│   ├── execution_agent.md           ← non-code drafting (content, research, marketing, ops)
│   ├── ui_agent.md                  ← presentation / interface layer
│   ├── ux_agent.md                  ← experience / flow critique
│   ├── reviewer_agent.md            ← QA, severity-rated review (Phase 4)
│   └── compression_agent.md         ← context compression + cross-session resumption
├── skills/
│   ├── analyze_repo.md
│   ├── design_api.md
│   ├── review_code.md
│   ├── review_layout.md
│   ├── improve_copy.md
│   ├── write_tests.md
│   ├── summarize_history.md
│   ├── suggest_next.md              ← auto-fires after every deliverable
│   ├── compare_approaches.md        ← on-demand decision support
│   └── animated_website.md          ← CSS/GSAP/Framer Motion animation plans + code
├── config/
│   ├── agents.yaml                  ← agent registry: skills, routing tags, cost tier
│   ├── token_policies.yaml          ← compression + verbosity presets per phase + domain
│   └── domain_profiles.yaml         ← domain detection signals, agent mappings
├── platforms/
│   ├── claude.md
│   ├── openai.md
│   └── antigravity.md
├── tools/
│   ├── init_project.py              ← one-time bootstrap (run once per project)
│   ├── generate_prompt.py           ← daily driver (run before every session)
│   ├── validate_kit.py              ← 11-check integrity validator
│   └── test_kit.py                  ← 60-test edge-case suite (CI + local)
├── context_loaders/
│   ├── project_summary.py           ← stack + structure detection
│   ├── repo_tree.py                 ← annotated directory tree
│   └── file_chunker.py              ← large-file token splitter
├── token_optimization/
│   ├── output_styles.md             ← style usage guide (definitions in token_policies.yaml)
│   └── compressor.py                ← token budget enforcement engine
└── examples/
    └── generic_project_lifecycle.md  ← two full annotated lifecycle walkthroughs
```

---

## Extend It

**Add a domain** — YAML only, no agent files change:
```yaml
# config/domain_profiles.yaml
domains:
  legal:
    display_name: "Legal & Compliance"
    detection_signals:
      strong: [contract, clause, regulation, filing]
      weak: [policy, compliance, terms]
    primary_agents:
      implementation: execution_agent
      review_refinement: reviewer_agent
```

**Add an agent** — create `agents/<name>.md`, register in `config/agents.yaml`.

**Add a skill** — create `skills/<name>.md`, add key to relevant agents in `config/agents.yaml`.

---

## Design Principles

- **LLM-agnostic** — no provider hard-wired anywhere; agent specs are plain Markdown
- **Markdown-first** — paste any agent file directly into any platform as a system prompt
- **Zero infrastructure** — no server, no background process, no API keys required
- **Plug-in domains** — add a domain in YAML; the rest of the kit adapts automatically
- **Token-aware by default** — every agent references token policies; context never bloats silently
- **Cross-session by design** — `project_state.md` makes long projects resumable without history replay
