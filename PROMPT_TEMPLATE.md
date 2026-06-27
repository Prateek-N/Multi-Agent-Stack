# agents-maker Prompt Template

Use this template as your message to the AI every session.
No Python required — just fill in the blanks and paste.

---

## How to use

1. Load `system_prompt.md` as your system prompt (once, stays loaded in Claude Projects / Assistants)
2. Fill in this template before each session
3. Paste it as your user message

---

## Session Message Template

```
## Project Context
Name: <your project name>
Stack: <languages and frameworks, e.g. "Python, FastAPI, PostgreSQL">
Domain: <software | content | research | data_analytics | product_design | marketing | ops_process>
Key constraints: <optional — e.g. "no external API calls", "mobile-first", "< 2s response time">

## Session State
<paste your project_state.md here to resume — or write "Session 1 — starting fresh">

## Task
<describe what you want to work on this session>
```

---

## Filled example — software project, resuming

```
## Project Context
Name: auth-service
Stack: Python, FastAPI, PostgreSQL, Redis
Domain: software
Key constraints: no breaking changes to existing /login endpoint

## Session State
# Project State
schema_version: "1.0"

## Current Phase
implementation

## Approved Artifacts
- task_profile: add rate limiting to auth service
- requirements_spec: max 100 req/min per IP, Redis-backed, bypass for internal IPs
- solution_design: sliding window counter in Redis, FastAPI middleware

## Build Log
- Increment 1: RedisRateLimiter class with sliding window ✓

## Open Decisions
- Should rate limit apply to /health endpoint?

## Session Notes
Session 3 — middleware partially implemented, tests pending

## Task
Write pytest tests for RedisRateLimiter covering: happy path, limit exceeded, bypass for internal IPs, Redis connection failure.
```

---

## Filled example — content project, fresh start

```
## Project Context
Name: company-blog
Stack: Markdown, Ghost CMS
Domain: content
Key constraints: 800-1200 words per post, technical audience, no promotional tone

## Session State
Session 1 — starting fresh

## Task
Write a technical blog post about how we migrated from REST to GraphQL and what we learned.
```

---

## Domain quick-pick

| Your project | Use this domain |
|---|---|
| App, API, backend, frontend, scripts | `software` |
| Blog, docs, newsletter, articles | `content` |
| Literature review, analysis, synthesis | `research` |
| Dashboards, data pipelines, analytics | `data_analytics` |
| Product flows, UX, mobile apps | `product_design` |
| Campaigns, copy, GTM strategy | `marketing` |
| SOPs, runbooks, process docs | `ops_process` |
| Not sure | omit it — AI will auto-detect |

---

## Force domain routing (optional)

Prefix your Task line to override auto-detection:

```
## Task
[domain: ops_process] Write an onboarding SOP for new engineers joining the platform team.
```

---

## After the AI responds

The AI will end its response with a `[Companion]` block:

```
---
[Companion] Phase: implementation | Domain: software | Est. token budget: ~38%

What to do next (pick one):
[Recommended] A: Write unit tests for RedisRateLimiter
B: Implement the /health endpoint bypass
C: Add rate limit headers to API response

To continue: copy the next task and fill it into ## Task above
---
```

Pick an option, update `## Session State` with the current phase and approved artifacts, and paste the template again.

---

## Saving session state

After each session, ask the AI:

```
Produce an updated project_state.md for this session.
```

Save what it gives you as `agents-maker/project_state.md` and paste it in the next session's `## Session State` block.
