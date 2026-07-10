---
description: Execution Agent for the software domain. Implements, refactors, and tests code. In the generic_project_lifecycle, handles Phase 3 (implementation) and Phase 4 fix-application for software tasks.
---
# /code

$ARGUMENTS

## Task
Use the `code` subagent (agents-maker) to handle the request above.

CONTEXT:
- Project config, if present: `agents-maker/config/project.yaml` — read it for domain, stack, and constraints before acting.
- User request: $ARGUMENTS

Follow the `code` agent's output contract. If the request is a self-contained task, deliver the finished artifact directly (Direct Task Mode) — do not ask for project context you can infer. End with the [Companion] next-steps block.
