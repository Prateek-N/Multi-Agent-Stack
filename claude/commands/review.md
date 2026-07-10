---
description: QA / Review Agent. Performs critical review of any work product: code tests and edge cases (software), clarity and rigor (content/research), data correctness (analytics), brand alignment (marketing), edge case coverage (ops). Owns Phase 4 across all domains.
---
# /review

$ARGUMENTS

## Task
Use the `review` subagent (agents-maker) to handle the request above.

CONTEXT:
- Project config, if present: `agents-maker/config/project.yaml` — read it for domain, stack, and constraints before acting.
- User request: $ARGUMENTS

Follow the `review` agent's output contract. If the request is a self-contained task, deliver the finished artifact directly (Direct Task Mode) — do not ask for project context you can infer. End with the [Companion] next-steps block.
