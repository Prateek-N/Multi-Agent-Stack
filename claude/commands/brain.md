---
description: Project brainstorming and decision support. Explores the problem space, generates 3+ genuinely different approaches with trade-offs, and recommends one. Invoked directly (/brain); pairs with planpro. Reads the repo to ground ideas.
---
# /brain

$ARGUMENTS

## Task
Use the `brain` subagent (agents-maker) to handle the request above.

CONTEXT:
- Project config, if present: `agents-maker/config/project.yaml` — read it for domain, stack, and constraints before acting.
- User request: $ARGUMENTS

Follow the `brain` agent's output contract. If the request is a self-contained task, deliver the finished artifact directly (Direct Task Mode) — do not ask for project context you can infer. End with the [Companion] next-steps block.
