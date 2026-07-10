---
description: Supervisor agent. Detects domain and task type, drives phase sequence, applies token policies, and aggregates specialist outputs.
---
# /orchestrate

$ARGUMENTS

## Task
Use the `orchestrate` subagent (agents-maker) to handle the request above.

CONTEXT:
- Project config, if present: `agents-maker/config/project.yaml` — read it for domain, stack, and constraints before acting.
- User request: $ARGUMENTS

Follow the `orchestrate` agent's output contract. If the request is a self-contained task, deliver the finished artifact directly (Direct Task Mode) — do not ask for project context you can infer. End with the [Companion] next-steps block.
