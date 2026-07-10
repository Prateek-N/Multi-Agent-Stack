---
description: Generic Execution Agent for non-software domains. Drafts content, research notes, campaign copy, SOP sections, and any other non-code work product in small, reviewable increments. In the generic_project_lifecycle, handles Phase 3 for content, research, marketing, ops_process, and product_design tas…
---
# /execute

$ARGUMENTS

## Task
Use the `execute` subagent (agents-maker) to handle the request above.

CONTEXT:
- Project config, if present: `agents-maker/config/project.yaml` — read it for domain, stack, and constraints before acting.
- User request: $ARGUMENTS

Follow the `execute` agent's output contract. If the request is a self-contained task, deliver the finished artifact directly (Direct Task Mode) — do not ask for project context you can infer. End with the [Companion] next-steps block.
