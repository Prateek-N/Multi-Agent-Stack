<div align="center">

# 🤖 agents-maker

### Multi-LLM · Multi-Agent · Any Project · Any AI Tool

> **One command. Any project. Any AI tool.**
> Every AI session becomes structured, token-efficient, and decision-aware.

[![npm](https://img.shields.io/npm/v/@prateek_ai/agents-maker?color=cb3837&logo=npm)](https://www.npmjs.com/package/@prateek_ai/agents-maker)
[![Kit Integrity](https://github.com/Prateek-N/Multi-Agent-Stack/actions/workflows/validate.yml/badge.svg)](https://github.com/Prateek-N/Multi-Agent-Stack/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Agents](https://img.shields.io/badge/Agents-10-purple)
![Skills](https://img.shields.io/badge/Skills-12-green)
![Domains](https://img.shields.io/badge/Domains-8-orange)
![Tests](https://img.shields.io/badge/Tests-60%2F60-brightgreen)

</div>

---

**agents-maker** is a structured prompting kit — provider-neutral Markdown + YAML you drop into any project. It's not an agent runtime: nothing executes on its own. Instead it acts as intelligent middleware between your problem statement and any AI tool — Claude, ChatGPT, Codex, or anything else — turning a task into a structured, domain-routed, token-budgeted prompt (with specialist "agent" personas and a resumable session state) that you paste into the LLM. Instead of dumping raw context into a chat window, you give it your stack, constraints, and task — and it routes to the right specialists, enforces a token budget, and always tells you what to do next.

> 💡 **The key insight**: AI quality is bounded by context quality. agents-maker teaches you exactly what context to give, structures it automatically, and makes every session resume-able without replaying history.

---

## ✨ What It Does

| 😤 Without agents-maker | 🚀 With agents-maker |
|---|---|
| Re-explain the project every session | `project_state.md` resumes automatically |
| AI gives generic boilerplate patterns | Specialist agent uses your actual stack |
| Wrong domain, wrong agent, wrong output | Domain auto-detected from task description |
| Bloated context, slow token-heavy responses | Token budget enforced per phase and domain |
| "What do I do next?" after every response | 3 ranked next steps surfaced automatically |
| One-size-fits-all output style | 11 output styles matched to phase and task |

- 🎯 **Domain is auto-detected** from your task — software, content, research, marketing, analytics, product design, ops
- 🧠 **10 named agents** — invoke any by name (`/brain`, `/planpro`, `/code`, …), or let the Orchestrator route automatically
- 💰 **Token budget is enforced** — context is compressed to fit the right window per phase
- 🗺️ **Next steps always surfaced** — 3 ranked options after every response
- 🔄 **State persists across sessions** — resume long projects without replaying history
- 🔌 **Works with any LLM** — pure Markdown + YAML, no provider lock-in, no API keys

---

## ⚡ Quickstart

Run this from your project root — no git clone, no repo URL to remember:

```bash
npx @prateek_ai/agents-maker init
```

Then run the setup script (handles Python deps, validation, and generates `system_prompt.md`):

### 🍎 macOS / Linux / WSL

```bash
bash agents-maker/quickstart.sh
```

### 🪟 Windows

```powershell
.\agents-maker\quickstart.ps1
```

### 🌍 Global install — use across all your projects

```bash
npm install -g @prateek_ai/agents-maker
agents-maker init
```

The quickstart script handles everything:
1. ✅ Checks Python 3.9+
2. 📦 Installs `pyyaml` (the only dependency)
3. 🔍 Validates all 12 kit integrity checks
4. 🚀 Runs `init_project.py` to scan your project and generate `system_prompt.md`
5. 📋 Prints all commands you need, ready to copy-paste

> **Prefer git?** `git clone https://github.com/Prateek-N/Multi-Agent-Stack.git agents-maker` works too.

---

## 🧠 Clone & Invoke — named agents in your project

`npx @prateek_ai/agents-maker init` also installs **Claude Code subagents + slash commands**
into your project's `.claude/` (non-destructively — it never overwrites your own files). Open
the project in Claude Code and invoke any agent by name:

```
/brain      Brainstorm the whole project — 3+ approaches, trade-offs, one recommendation
/planpro    Turn a goal into the best-possible plan (short, specific, dependency-ordered)
/architect  System design, API contracts, data models, ADRs
/code       Implement, refactor, and test (software + analytics)
/execute    Non-code drafting — docs, research, marketing copy, SOPs
/ui         Component hierarchy, layout, design tokens, accessibility
/ux         Flow critique, onboarding, funnel/friction analysis
/review     Severity-rated QA review (CRITICAL / HIGH / MEDIUM / LOW)
/orchestrate  Route a complex task across specialists (6-phase lifecycle)
/compress   Compress context / summarize session state
```

Typical flow: **`/brain`** to explore options → **`/planpro`** to lock a plan → **`/code`** to
build → **`/review`** to check it. The main agent can also delegate to these as subagents.

> Regenerate the `.claude/` files any time (e.g. after adding agents):
> `python agents-maker/tools/generate_claude_agents.py`

---

## 🚦 Two Ways to Use It

### 🅰️ Zero-Python Workflow (no installation needed)

1. Paste `system_prompt.md` into your AI tool as the **system prompt** or Project Knowledge — do this **once**
2. Open `PROMPT_TEMPLATE.md`, fill in your context and task, paste it as your message:

```
## Project Context
Name: my-app | Stack: Python, FastAPI | Domain: software

## Session State
Session 1 — starting fresh

## Task
Add rate limiting to the auth service
```

### 🅱️ Companion Mode CLI (Python — automated)

```bash
# One-time bootstrap — scans your project, generates system_prompt.md
python agents-maker/tools/init_project.py

# Before every session — generates a structured, domain-routed message
python agents-maker/tools/generate_prompt.py "add rate limiting to the auth service"
```

Output:
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

## 🌐 Platform Integration

One command wires agents-maker into every AI platform you use. Run it once after init:

```bash
python agents-maker/tools/generate_platform_configs.py
```

This writes a native config file for each platform — committed to git, auto-loaded on every session, no copy-paste required:

| Platform | Config file written | What it does |
|---|---|---|
| 🟣 **Claude Code** | `CLAUDE.md` | Auto-read every session — domain, stack, phase, agent routing loaded silently |
| 🟢 **GitHub Copilot** | `.github/copilot-instructions.md` | Workspace-level instructions — Copilot applies agent routing on every suggestion |
| 🔵 **Cursor** | `.cursor/rules` | Persistent AI rules — Cursor applies domain context across all tabs |
| ⚡ **Antigravity** | `.agkit/agents.yaml` | Full agent pipeline config — all 10 agents + 12 skills registered with phase/domain wiring |

**Commit all generated files** — they are project config, not private state. Every developer who clones the repo gets the full multi-agent setup automatically.

```bash
# Generate for all platforms (default)
python agents-maker/tools/generate_platform_configs.py

# Generate for specific platforms only
python agents-maker/tools/generate_platform_configs.py --platforms claude copilot

# Preview without writing
python agents-maker/tools/generate_platform_configs.py --dry-run

# Or generate during init
python agents-maker/tools/init_project.py --platforms
```

Regenerate whenever your domain, stack, or phase changes.

```markdown
# agents-maker — Project AI Config

## Active Domain
software  (confidence: high)

## Stack
Python, FastAPI, PostgreSQL

## Current Phase
Implementation (`implementation`)

## Agent Routing
Orchestrator is always active. Specialist agents: code_agent (implementation), reviewer_agent (QA).

## Session Instructions
- Apply domain routing and phase context from agents-maker before every task.
- After every response: append a [Companion] block with 3 ranked next steps.
```

---

## 📚 Context Guide — What to Give the AI

> The quality of every AI response is bounded by the context you provide.

### 🧱 The 5 Context Layers

| Layer | Field | Impact if missing |
|---|---|---|
| 🏷️ **Project identity** | Name, Stack | AI uses generic patterns instead of your actual technology |
| 🎯 **Domain** | Domain key | AI may mis-route (software task treated as content) |
| 🚧 **Constraints** | Key constraints | AI proposes solutions you can't use |
| 📍 **Session state** | Phase + approved artifacts | AI restarts from scratch instead of continuing |
| 🎯 **Task specificity** | Concrete, scoped description | AI asks 5 clarifying questions before doing anything |

---

### 🔍 Project Context — What Each Field Unlocks

```
## Project Context
Name: auth-service
Stack: Python 3.11, FastAPI, PostgreSQL 15, Redis 7, Docker
Domain: software
Key constraints: no breaking changes to /login, Redis already in use, must support 10k req/min
```

**`Stack`** — the Code Agent uses this to pick the right patterns, libraries, and idioms. Be specific:

| Weak | Strong |
|---|---|
| `"Python"` | `"Python 3.11, FastAPI, PostgreSQL 15"` |
| `"JavaScript"` | `"Next.js 14, TypeScript, Tailwind, Prisma"` |

**`Key constraints`** — the highest-ROI field. Constraints eliminate entire classes of wrong answers before the AI starts:

| 🚫 Without constraints | ✅ With constraints |
|---|---|
| AI suggests a new caching library | AI uses your existing Redis setup |
| AI proposes a breaking API change | AI works around the existing `/login` contract |
| AI writes a 4,000-word document | AI writes within your 800-word limit |

**`Domain`** — controls which specialist agents activate. Force it with `[domain: X]` in your task — all 8 domains are supported:
```
## Task
[domain: ops_process] Write a runbook for Redis failover.
[domain: marketing]   Write a go-to-market brief for our SaaS launch.
[domain: software]    Refactor the auth service — add sliding-window rate limiting.
```
The header shows `(forced)` as the confidence when a prefix is used, so you always know routing was explicit.

---

### ✍️ Task Specificity — Good vs Weak

The pattern: **Deliverable + Scope + Success criteria.** Three sentences max.

| 😩 Weak | 💪 Strong |
|---|---|
| `fix the bug` | `Fix 500 on POST /auth/refresh when Redis key has expired — stack trace in issue #47` |
| `improve the UI` | `Redesign signup form: reduce fields from 9 to 5, inline validation, mobile-first` |
| `write blog post` | `1,200-word technical post for senior engineers on REST→GraphQL: what broke, 3 takeaways` |
| `add tests` | `pytest for RedisRateLimiter: happy path, limit exceeded, bypass for 10.x.x.x, Redis failure` |
| `review the code` | `Security review of auth middleware — focus on token validation, rate limit bypass vectors` |

---

### 🗂️ Code Context — How to Attach Your Repo

```bash
# Annotated repo tree → paste into session message
python agents-maker/context_loaders/repo_tree.py --path .

# Stack + structure summary
python agents-maker/context_loaders/project_summary.py --path .

# Split a large file into token-safe chunks
python agents-maker/context_loaders/file_chunker.py --path . --files src/auth/middleware.py
```

Or paste manually after your `## Task` block:

```
## Repo Context
src/
├── auth/
│   ├── middleware.py     ← rate limiting goes here
│   └── routes.py
└── core/
    └── redis.py          ← existing Redis client

Key file — src/core/redis.py:
[paste relevant excerpt]
```

---

### 🔁 Session State — Resume Without Replay

After each approved phase, ask the AI:
```
Produce an updated project_state.md for this session.
```

Paste the result into your next session's `## Session State` block. The Compression Agent reads it and jumps directly to the current phase — no re-explaining, no token waste.

```yaml
# project_state.md
## Current Phase
implementation

## Approved Artifacts
- task_profile: add sliding-window rate limiter to auth service
- requirements_spec: 100 req/min per IP, Redis-backed, bypass for 10.x.x.x
- solution_design: FastAPI middleware, sliding window, Redis ZSET, X-RateLimit-* headers

## Build Log
- Increment 1: RedisRateLimiter class + ZSET logic ✓
- Increment 2: FastAPI middleware integration ✓

## Open Decisions
- Should /health bypass be configurable or hard-coded?
```

---

### 🗺️ Domain-Specific Context Tips

| Domain | 📋 Most important context to include |
|---|---|
| `💻 software` | Stack versions, existing patterns, file paths, code excerpts |
| `✍️ content` | Target audience, tone, word count, format, examples you like |
| `🔬 research` | Question to answer, scope limits, citation style, sources to exclude |
| `📊 data_analytics` | Data schema or sample rows, metrics that matter, existing tools |
| `🎨 product_design` | User persona, current flow (numbered steps), pain point, platform |
| `📣 marketing` | ICP, channel, brand voice, competitor positioning |
| `⚙️ ops_process` | Team size, existing tools, compliance requirements, who runs it |

---

### 🎯 Phase-Based Context — What to Include Per Phase

| Phase (`--phase` key) | 📎 Add this to your session message |
|---|---|
| **Task Framing** (`task_framing`) | Full project context + constraint list. Let the AI ask clarifying questions. |
| **Requirements** (`requirements`) | Non-negotiables, stakeholder constraints, timeline. |
| **Solution Design** (`solution_design`) | Existing system diagrams or structure; previous ADRs. |
| **Implementation** (`implementation`) | Relevant code excerpts, file paths, test patterns already in use. |
| **Review** (`review_refinement`) | What success looks like, known edge cases, compliance checklist. |
| **Handoff** (`handoff`) | Deployment target, who receives the handoff, format preferences. |

---

### 🔧 Forcing a Skill

Skills fire automatically, but you can invoke any explicitly:

```
[skill: compare_approaches] Compare Redis sliding window vs token bucket for our rate limiter.
[skill: animated_website] Build a scroll-driven hero entrance animation using GSAP.
[skill: review_code] Security review of src/auth/middleware.py — focus on token validation.
```

---

## 🛠️ Command Reference

```bash
# 📦 Install into your project
npx @prateek_ai/agents-maker init                        # on-demand (no install needed)
npm install -g @prateek_ai/agents-maker && agents-maker init  # global install

# 🚀 One-command setup (after init)
bash agents-maker/quickstart.sh                          # macOS / Linux / WSL
.\agents-maker\quickstart.ps1                            # Windows PowerShell

# 🔧 Bootstrap a new project (run once)
python agents-maker/tools/init_project.py
python agents-maker/tools/init_project.py --path /your/project
python agents-maker/tools/init_project.py --update       # regenerate system_prompt.md
python agents-maker/tools/init_project.py --claude-md    # also write CLAUDE.md (Claude Code)

# 💬 Generate a prompt before any AI session
python agents-maker/tools/generate_prompt.py "describe your task"
python agents-maker/tools/generate_prompt.py "[domain: software] your task"  # force domain
python agents-maker/tools/generate_prompt.py "your task" --phase implementation
python agents-maker/tools/generate_prompt.py "your task" --compress   # add token policy block
python agents-maker/tools/generate_prompt.py "your task" --full       # embed full system prompt

# 🌐 Wire into all AI platforms (Claude Code, Copilot, Cursor, Antigravity)
python agents-maker/tools/generate_platform_configs.py
python agents-maker/tools/generate_platform_configs.py --platforms claude copilot
python agents-maker/tools/generate_platform_configs.py --dry-run  # preview without writing
python agents-maker/tools/init_project.py --platforms              # generate during init

# 📊 Context loaders (paste output alongside your task)
python agents-maker/context_loaders/project_summary.py --path .
python agents-maker/context_loaders/repo_tree.py --path .
python agents-maker/context_loaders/file_chunker.py --path . --files src/main.py

# ✅ Validate kit integrity (run after any edits)
python agents-maker/tools/validate_kit.py

# 🧪 Run the full test suite
python agents-maker/tools/test_kit.py
```

**Valid phases:** `task_framing` · `requirements` · `solution_design` · `implementation` · `review_refinement` · `handoff`

**Valid domains for `[domain: X]`:** `software` · `content` · `research` · `data_analytics` · `product_design` · `marketing` · `ops_process` · `general`

---

## 🧠 The 10 Agents

> Invoke any by name (`/brain`, `/planpro`, `/code`, …) — or let the Orchestrator route automatically.

| Agent | Command | 🎯 What it handles |
|---|---|---|
| 🧠 **Brain** | `/brain` | Brainstorm the whole project — 3+ approaches, trade-offs, one recommendation |
| 🗺️ **PlanPro** | `/planpro` | Best-possible plan — short, specific, dependency-ordered, verifiable |
| 🎛️ **Orchestrator** | `/orchestrate` | Entry point — detects domain, drives 6-phase lifecycle, aggregates output |
| 🏗️ **Architect / Planner** | `/architect` | System design, API contracts, research plans, campaign strategy, process maps |
| 💻 **Code Agent** | `/code` | Software implementation, refactoring, test generation (software + analytics) |
| ✍️ **Execution Agent** | `/execute` | Non-code work — documents, research sections, marketing copy, SOPs, runbooks |
| 🖥️ **UI Agent** | `/ui` | Component hierarchy, layout, design tokens, accessibility, landing pages |
| 🧭 **UX Agent** | `/ux` | Flow critique, onboarding sequences, funnel analysis, friction identification |
| 🔍 **Reviewer Agent** | `/review` | QA for any domain — severity-rated reviews, edge cases, brand alignment |
| 🗜️ **Compression Agent** | `/compress` | Token budget enforcement, context compression, cross-session resumption |

---

## 🔄 The 6-Phase Lifecycle

> Every task — code, content, research, marketing, ops — runs through the same structure.

| Phase | 🔄 What happens | 📄 Output artifact |
|---|---|---|
| **0 — Task Framing** | Orchestrator interprets intent, detects domain, sets constraints | `task_profile` |
| **1 — Requirements** | Architect clarifies scope, surfaces ambiguities | `requirements_spec` |
| **2 — Solution Design** | Architect proposes approach; UI/UX agents join for design tasks | `solution_design` |
| **3 — Implementation** | Code Agent (software) or Execution Agent (everything else) builds | `work_product` |
| **4 — Review** | Reviewer Agent critiques, flags issues, suggests fixes | `refinement_report` |
| **5 — Handoff** | Orchestrator packages deliverables, surfaces next-project options | `handoff_package` |

Each phase ends with an **approval gate** (A/B/C options). The AI never proceeds without your sign-off. Small tasks can merge phases — the Orchestrator proposes this automatically.

---

## 🃏 The 12 Skill Cards

> Skills are reusable capability definitions. They define exact output formats so responses are always structured.

| Skill | ⚡ Triggered by |
|---|---|
| `🔎 analyze_repo` | Any session starting with a code repo |
| `📐 design_api` | API design, schema, contract decisions |
| `🔬 review_code` | Code review, QA, security audit requests |
| `🖼️ review_layout` | UI/UX critique, layout and accessibility review |
| `✨ improve_copy` | Writing quality, tone, and clarity improvement |
| `🧪 write_tests` | Test generation, coverage, and edge-case requests |
| `📦 summarize_history` | Cross-session compression and context handoff |
| `🗺️ suggest_next` | **Auto-fires** after every deliverable — 3 ranked next moves |
| `⚖️ compare_approaches` | "compare", "trade-off", "which approach" — structured decision table |
| `🎬 animated_website` | CSS / GSAP / Framer Motion animation plans and production-ready code |
| `🗂️ write_process_map` | SOP, runbook, or workflow doc — numbered steps + RACI + exceptions |
| `🗃️ define_data_schema` | Data model, metric definitions, or data dictionary requests |

---

## 🌐 8 Built-In Domains

> Domain detection is automatic. Use `[domain: X]` to force it.

| Domain | 💡 Example tasks | 🤖 Implementation agent |
|---|---|---|
| `💻 software` | build API, fix bug, refactor service | Code Agent |
| `✍️ content` | write blog post, draft newsletter, edit article | Execution Agent |
| `🔬 research` | literature review, competitive analysis, synthesis | Execution Agent |
| `📊 data_analytics` | build dashboard, analyze funnel, clean dataset | Code Agent |
| `🎨 product_design` | design onboarding flow, map user journey | Execution Agent + UI/UX |
| `📣 marketing` | go-to-market strategy, campaign copy, brand guide | Execution Agent + UX |
| `⚙️ ops_process` | write SOP, design runbook, document process | Execution Agent |
| `❓ general` | fallback — Orchestrator asks clarifying questions | — |

> Add a new domain with a single YAML block in `config/domain_profiles.yaml` — no agent files change.

---

## 🤝 Companion Mode: What the AI Returns

When `system_prompt.md` is loaded, every AI response automatically ends with a `[Companion]` block:

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

## 🔋 Token Optimization

The kit enforces a token budget per phase and domain, defined in `config/token_policies.yaml`:

- 📏 **Per-phase limits** — implementation phases get more tokens than framing phases
- 🎯 **Per-domain overrides** — product_design gets UI/UX context; software gets code context
- 🔢 **Relevance filtering** — files are scored and ranked; only the most relevant are included
- 🗜️ **History compression** — raw discussion turns dropped after each phase; only approved artifacts kept

Use `--compress` to attach the active token policy to any generated prompt. Use `--full` only on platforms without persistent system prompts.

---

## 🖥️ Works With Any AI Tool

| Platform | 🔗 How to use |
|---|---|
| 🟣 **Claude (Projects)** | Paste `system_prompt.md` into Project Instructions — one-time setup. See [`platforms/claude.md`](platforms/claude.md) Option A. |
| 🟣 **Claude (free tier)** | Paste `system_prompt.md` as your first message each session. See [`platforms/claude.md`](platforms/claude.md) Option C. |
| 🟢 **OpenAI / ChatGPT** | Pass `system_prompt.md` as the `system` role — Companion Mode works identically. See [`platforms/openai.md`](platforms/openai.md). |
| 🔵 **Antigravity** | Map phases to pipeline stages. See [`platforms/antigravity.md`](platforms/antigravity.md). |
| ⚪ **Any other tool** | Use `--full` flag — one self-contained paste includes everything. |

---

## ✅ Validate the Kit

After any edits, run the integrity checker:

```bash
python agents-maker/tools/validate_kit.py
```

Runs **12 checks**: YAML parse · agent files + structure · skill files + structure · domain coverage · agent references · output styles · domain scoring · file inventory · compressor dry-run · system_prompt.md freshness.

```
============================================================
  Result: ALL 12 checks PASSED
============================================================
```

---

## 📁 Repository Map

```
agents-maker/
├── 📄 README.md
├── 📋 CHANGELOG.md                  ← version history
├── 🤝 CONTRIBUTING.md               ← contribution guide + standards
├── 📜 LICENSE                       ← MIT
├── 📦 package.json                  ← npm package (@prateek_ai/agents-maker)
├── 🖥️  bin/
│   └── cli.js                       ← npx entry point (agents-maker init)
├── 🚀 quickstart.sh                 ← setup script (macOS / Linux / WSL)
├── 🚀 quickstart.ps1                ← setup script (Windows PowerShell)
├── 🧠 system_prompt.md              ← paste into your AI tool once (all agents + skills)
├── 📝 PROMPT_TEMPLATE.md            ← fill in before every session (no Python needed)
├── ⚙️  .github/
│   └── workflows/
│       ├── validate.yml             ← CI: runs validate_kit.py on every push/PR
│       └── release.yml              ← tag-triggered GitHub Release publisher
├── 📚 docs/
│   ├── architecture.md              ← agent graph, context flow, design decisions
│   ├── workflows.md                 ← lifecycle phases, interface contracts
│   └── domains.md                   ← domain plug-in schema + built-in domain cards
├── 🤖 agents/
│   ├── orchestrator.md              ← phase driver, domain detection, Companion Mode
│   ├── architect_agent.md           ← requirements + solution design (all domains)
│   ├── code_agent.md                ← software/data implementation
│   ├── execution_agent.md           ← non-code drafting (content, research, marketing, ops)
│   ├── ui_agent.md                  ← presentation / interface layer
│   ├── ux_agent.md                  ← experience / flow critique
│   ├── reviewer_agent.md            ← QA, severity-rated review (Phase 4)
│   └── compression_agent.md         ← context compression + cross-session resumption
├── 🃏 skills/
│   ├── analyze_repo.md
│   ├── design_api.md
│   ├── review_code.md
│   ├── review_layout.md
│   ├── improve_copy.md
│   ├── write_tests.md
│   ├── summarize_history.md
│   ├── suggest_next.md              ← auto-fires after every deliverable
│   ├── compare_approaches.md        ← on-demand decision support
│   ├── animated_website.md          ← CSS/GSAP/Framer Motion animation code
│   ├── write_process_map.md         ← SOP/runbook: steps + RACI + exceptions
│   └── define_data_schema.md        ← ER sketch + metric definitions + data dictionary
├── ⚙️  config/
│   ├── agents.yaml                  ← agent registry: skills, routing tags, cost tier
│   ├── token_policies.yaml          ← compression + verbosity presets per phase + domain
│   └── domain_profiles.yaml         ← domain detection signals, agent mappings
├── 🖥️  platforms/
│   ├── claude.md
│   ├── openai.md
│   └── antigravity.md
├── 🔧 tools/
│   ├── init_project.py              ← one-time bootstrap (run once per project)
│   ├── generate_prompt.py           ← daily driver (run before every session)
│   ├── generate_platform_configs.py ← wire into Claude Code, Copilot, Cursor, Antigravity
│   ├── generate_claude_md.py        ← writes CLAUDE.md for Claude Code integration
│   ├── validate_kit.py              ← 12-check integrity validator
│   ├── test_kit.py                  ← 60-test edge-case suite (CI + local)
│   └── domain_utils.py              ← shared domain scoring (used by all 3 tools)
├── 🔌 context_loaders/
│   ├── project_summary.py           ← stack + structure detection
│   ├── repo_tree.py                 ← annotated directory tree
│   └── file_chunker.py              ← large-file token splitter
├── 💰 token_optimization/
│   ├── output_styles.md             ← style usage guide (definitions in token_policies.yaml)
│   └── compressor.py                ← compression pipeline (reference impl; provider adapters are stubs)
└── 📖 examples/
    └── generic_project_lifecycle.md  ← two full annotated lifecycle walkthroughs
```

---

## 🧩 Extend It

**➕ Add a domain** — YAML only, no agent files change:
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

**➕ Add an agent** — create `agents/<name>.md`, register in `config/agents.yaml`

**➕ Add a skill** — create `skills/<name>.md`, add key to relevant agents in `config/agents.yaml`

After any addition, run `python agents-maker/tools/validate_kit.py` to confirm integrity.

---

## 🤔 How It Compares

agents-maker is a **structured prompting layer**, not an agent runtime. It's complementary to — not a replacement for — the tools you already use.

| | agents-maker | Cursor `.cursorrules` / Claude Projects | LangGraph / CrewAI / Agents SDK |
|---|---|---|---|
| **What it is** | Portable Markdown+YAML that structures your *prompt* | Per-tool persistent instructions | Code frameworks that *execute* agents |
| **Runs code / calls the LLM?** | No — you paste into any tool | No | Yes |
| **Provider lock-in** | None (works with all) | Tied to that one tool | You wire the provider |
| **Best at** | Repeatable, domain-routed, resumable *context* across any tool | Deep integration in one editor | Autonomous multi-step execution |

**Use agents-maker when** you jump between AI tools and want one consistent, token-budgeted, resumable way to frame work — without building your own scaffolding or locking into a single vendor. **Reach for a real agent framework** when you need autonomous execution, tool-calling loops, or a running service.

---

## 🏛️ Design Principles

| Principle | What it means |
|---|---|
| 🔌 **LLM-agnostic** | No provider hard-wired anywhere — agent specs are plain Markdown |
| 📝 **Markdown-first** | Paste any agent file directly into any platform as a system prompt |
| 🚫 **Zero infrastructure** | No server, no background process, no API keys required |
| 🧩 **Plug-in domains** | Add a domain in YAML; the rest of the kit adapts automatically |
| 💰 **Token-aware by default** | Every agent references token policies; context never bloats silently |
| 🔄 **Cross-session by design** | `project_state.md` makes long projects resumable without history replay |

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for standards on adding skills, agents, and domains.

Run `python agents-maker/tools/validate_kit.py` before every PR — CI enforces this automatically.

---

<div align="center">

Made with 🧠 by [Prateek Narvariya](https://github.com/Prateek-N) · MIT License · [Changelog](CHANGELOG.md) · [Docs](docs/)

</div>
