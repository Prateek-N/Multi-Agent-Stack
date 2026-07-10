---
description: Experience / Flow Agent. Critiques and improves any multi-step journey: user flows (software), reader journeys (content), process flows (ops), conversion funnels (marketing), onboarding sequences.
---
# /ux

$ARGUMENTS

## Task
Use the `ux` subagent (agents-maker) to handle the request above.

CONTEXT:
- Project config, if present: `agents-maker/config/project.yaml` — read it for domain, stack, and constraints before acting.
- User request: $ARGUMENTS

Follow the `ux` agent's output contract. If the request is a self-contained task, deliver the finished artifact directly (Direct Task Mode) — do not ask for project context you can infer. End with the [Companion] next-steps block.
