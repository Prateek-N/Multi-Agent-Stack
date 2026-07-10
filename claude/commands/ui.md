---
description: Presentation / Interface Agent. Component hierarchy, layout, design tokens, and accessibility for any visual medium: UI, document layout, slide/deck structure, information hierarchy, landing pages.
---
# /ui

$ARGUMENTS

## Task
Use the `ui` subagent (agents-maker) to handle the request above.

CONTEXT:
- Project config, if present: `agents-maker/config/project.yaml` — read it for domain, stack, and constraints before acting.
- User request: $ARGUMENTS

Follow the `ui` agent's output contract. If the request is a self-contained task, deliver the finished artifact directly (Direct Task Mode) — do not ask for project context you can infer. End with the [Companion] next-steps block.
