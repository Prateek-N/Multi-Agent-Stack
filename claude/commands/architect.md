---
description: Architect / Planner. Turns requirements into domain-appropriate solution designs: system architecture (software), document outline (content), research plan (research), campaign strategy (marketing), process map (ops_process).
---
# /architect

$ARGUMENTS

## Task
Use the `architect` subagent (agents-maker) to handle the request above.

CONTEXT:
- Project config, if present: `agents-maker/config/project.yaml` — read it for domain, stack, and constraints before acting.
- User request: $ARGUMENTS

Follow the `architect` agent's output contract. If the request is a self-contained task, deliver the finished artifact directly (Direct Task Mode) — do not ask for project context you can infer. End with the [Companion] next-steps block.
