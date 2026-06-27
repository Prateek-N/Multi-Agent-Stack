# 📖 agents-maker Cookbook

Complete end-to-end session transcripts — real prompts, real AI responses, real output artifacts.
Each entry covers all 6 lifecycle phases (Task Framing → Handoff) for one domain.

Browse by what you're building:

---

## Sessions

| Domain | Task | File |
|---|---|---|
| `software` | Add Redis sliding-window rate limiting to a FastAPI auth service | [fastapi-rate-limiter/session.md](fastapi-rate-limiter/session.md) |
| `product_design` | UI/UX audit of a B2B SaaS settings page with severity-rated findings | [react-component-audit/session.md](react-component-audit/session.md) |
| `marketing` | GTM strategy brief for a developer tool launching on Product Hunt | [go-to-market-brief/session.md](go-to-market-brief/session.md) |
| `data_analytics` | ER schema + metric definitions for a SaaS subscription analytics pipeline | [data-pipeline-schema/session.md](data-pipeline-schema/session.md) |
| `ops_process` | On-call runbook (steps + RACI + exceptions) for a PostgreSQL failover | [sre-runbook/session.md](sre-runbook/session.md) |
| `research` | Literature review plan + annotated bibliography for a transformer survey | [research-lit-review/session.md](research-lit-review/session.md) |

---

## What each entry shows

Every session transcript includes:

1. **The CLI command** — the exact `generate_prompt.py` call the user ran
2. **The generated prompt block** — what gets pasted into the AI tool
3. **AI responses per phase** — real excerpts with agent names and [Companion] blocks
4. **Final output artifact** — the actual deliverable (code, brief, runbook, schema, etc.)

---

## How to run any of these yourself

```bash
# Replace with the task from any session above
python agents-maker/tools/generate_prompt.py "add Redis rate limiting to FastAPI auth service"
# Copy the printed block → paste as your message to Claude or any LLM
```

The domain is auto-detected. No configuration needed.

---

## Adding a new entry

1. Run `generate_prompt.py` with your real task
2. Work through all 6 phases with your AI tool
3. Save the transcript to `cookbook/<slug>/session.md`
4. Add a row to this README table

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full contribution guide.
