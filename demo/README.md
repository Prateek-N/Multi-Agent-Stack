---
title: agents-maker Live Demo
emoji: 🤖
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: demo/app.py
pinned: false
license: mit
short_description: Multi-agent prompt engineering — live domain detection + routing
---

# agents-maker — Live Demo

Type any task. See **domain detection scoring** across all 8 domains, **agent routing** for the detected domain, and the **full structured prompt block** ready to paste into Claude, ChatGPT, or any LLM.

No setup. No API keys. No account. Pure local computation.

## What it shows

1. **Domain detection scores** — bar chart of signal strength across all 8 domains (software, content, research, data_analytics, product_design, marketing, ops_process, general)
2. **Agent routing** — which of the 8 specialist agents activate for your task and domain
3. **Generated prompt block** — the exact structured message you'd paste into your AI tool

## Try these examples

- `Add Redis sliding-window rate limiting to a FastAPI auth service` → software
- `Write a GTM brief for a developer tool launching on Product Hunt` → marketing
- `Design a PostgreSQL failover runbook with RACI and exception table` → ops_process
- `Build a SaaS subscription analytics dashboard with MRR and churn` → data_analytics
- `Audit the UX of a B2B settings page with a high Billing bounce rate` → product_design
- `Plan a literature review on transformer efficiency improvements since 2017` → research

## Get the full kit

```bash
git clone https://github.com/Prateek-N/Multi-Agent-Stack.git agents-maker
python agents-maker/tools/init_project.py          # one-time setup
python agents-maker/tools/generate_prompt.py "your task here"
```

The CLI generates the same structured prompt block you see in this demo, but personalized to your actual project stack, phase, and state.

## Links

- [GitHub repo](https://github.com/Prateek-N/Multi-Agent-Stack)
- [Cookbook — 6 real session transcripts](https://github.com/Prateek-N/Multi-Agent-Stack/tree/main/cookbook)
- [GitHub Action for PR reviews](https://github.com/Prateek-N/Multi-Agent-Stack/tree/main/actions/review-pr)
- [Claude Code integration](https://github.com/Prateek-N/Multi-Agent-Stack#-claude-code-integration)
