---
description: Manages context and output compression. Runs after each lifecycle phase to update project_state, and on token-budget triggers during long sessions.
---
# /compress

$ARGUMENTS

## Task
Use the `compress` subagent (agents-maker) to handle the request above.

CONTEXT:
- Project config, if present: `agents-maker/config/project.yaml` — read it for domain, stack, and constraints before acting.
- User request: $ARGUMENTS

Follow the `compress` agent's output contract. If the request is a self-contained task, deliver the finished artifact directly (Direct Task Mode) — do not ask for project context you can infer. End with the [Companion] next-steps block.
