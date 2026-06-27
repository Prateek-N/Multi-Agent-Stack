# Antigravity Integration Guide

Conceptual mapping of this kit to Antigravity's agent primitives. Because Antigravity's API surface evolves, this guide focuses on conceptual equivalences rather than exact API calls.

---

> Companion Mode works the same across all platforms. See [platforms/claude.md](claude.md) for the full Companion Mode walkthrough, then follow the platform-specific steps below.

---

## Core Primitive Mapping

| This kit | Antigravity equivalent | Notes |
|---|---|---|
| Agent spec (`.md` system prompt) | Agent definition / instruction set | Paste the Markdown as the agent's system instructions |
| `config/agents.yaml` | Agent registry / manifest | Import as agent metadata; use routing_tags for intent routing |
| `config/token_policies.yaml` | Context policy / pipeline config | Map to context window management settings |
| `config/domain_profiles.yaml` | Domain/intent classifier config | Load as global knowledge for the Orchestrator agent |
| Skill card (`.md`) | Tool definition / capability card | Register each skill as a tool or callable capability |
| Orchestrator | Supervisor / planner agent | Entry point — drives the 6-phase lifecycle and delegates to specialists |
| Specialist agents | Worker agents / sub-agents | Register with the Orchestrator as callable workers |
| `context_loaders/*.py` | Context ingestion pipeline | Run locally; paste output as session-opening message |
| `token_optimization/compressor.py` | Context compression middleware | Integrate as a preprocessing step before context reaches the agent pipeline |

---

## Agent Graph Setup

In Antigravity, define the agent graph with the Orchestrator at the root:

```
Orchestrator (root / lifecycle driver)
├── ArchitectAgent     ← Phase 1 (Requirements) + Phase 2 (Solution Design)
├── CodeAgent          ← Phase 3 Implementation for software + data_analytics
├── ExecutionAgent     ← Phase 3 Implementation for content, research, marketing, ops_process
├── UIAgent            ← Supporting: presentation/interface layer
├── UXAgent            ← Supporting: experience/flow critique
├── ReviewerAgent      ← Phase 4 (Review & Refinement)
└── CompressionAgent   ← Cross-cutting: token management + cross-session resumption
```

For each node:
1. Create an agent with the corresponding `.md` file content as its system prompt.
2. Attach its skill cards from `skills/` (listed in `config/agents.yaml` under each agent).
3. Set routing tags from `config/agents.yaml` as intent triggers or classifier labels.

---

## Minimal Lifecycle Invocation

No domain configuration is needed. The Orchestrator detects the domain from the user's first message using `config/domain_profiles.yaml`.

**Example invocation**:
```
User: "Help me document the onboarding process for new engineers."

Orchestrator behavior:
1. Scores message: "document" (content/weak), "process" (ops_process/strong), "onboarding" (product_design/weak)
2. ops_process scores highest → domain = ops_process, confidence = high
3. Produces task_profile, asks 3–5 scoping questions
4. Drives user through 6 phases with explicit approval gates
```

**Domain hint override**: prefix the message with `[domain: <key>]` to bypass scoring:
```
[domain: content] Write a technical white paper on distributed tracing.
```

---

## Context Injection

Inject these documents into Antigravity's global knowledge or session context:

| Document | Where to inject | Required |
|---|---|---|
| `config/agents.yaml` | Global knowledge / agent metadata | Yes |
| `config/token_policies.yaml` | Pipeline config / session settings | Yes |
| `config/domain_profiles.yaml` | Orchestrator's knowledge (domain detection) | Yes |
| Output of `project_summary.py` | Session-level context at conversation start | For code tasks only |
| Output of `repo_tree.py` | Session-level context; update when files change | For code tasks only |
| `project_state.md` (if resuming) | Opening message or session context | For session resumption |

---

## Token Policy Mapping

Map `token_policies.yaml` fields to Antigravity's context management settings:

| `token_policies.yaml` field | Antigravity setting (approximate) |
|---|---|
| `max_input_tokens` | Context window limit / max context size |
| `max_input_files` | Max attached documents per turn |
| `history_summarize_after_turns` | Auto-summarization turn threshold |
| `force_state_block_after_turns: 20` | Hard summarization trigger after 20 turns |
| `output_style` | Response format preset / verbosity setting |
| `relevance_drop_threshold` | Relevance threshold for document retrieval |
| `project_state_snapshot_after_phase` | Emit `project_state.md` after each approved phase |

If Antigravity does not expose these settings directly, apply them via `compressor.py` as a local preprocessing step.

---

## Skill Cards as Tools

Register each skill card as an Antigravity tool:

| Skill file | Tool name | Trigger condition |
|---|---|---|
| `skills/analyze_repo.md` | `analyze_repo` | Session start; no project summary provided |
| `skills/design_api.md` | `design_api` | Architect Agent: API design task |
| `skills/review_code.md` | `review_code` | Reviewer Agent: software domain review |
| `skills/review_layout.md` | `review_layout` | UI/UX Agent: layout critique |
| `skills/improve_copy.md` | `improve_copy` | UX Agent or Execution Agent: microcopy |
| `skills/write_tests.md` | `write_tests` | Code Agent: test generation |
| `skills/summarize_history.md` | `summarize_history` | Compression Agent: turn/token threshold hit |

Each tool's description should be the first paragraph of the corresponding skill card.

---

## Lifecycle Phase Wiring

The Orchestrator drives 6 phases sequentially. In Antigravity, model this as a stateful pipeline:

| Phase | Primary agent to call | Output artifact |
|---|---|---|
| 0 — Task Framing | Orchestrator (direct) | `task_profile` |
| 1 — Requirements | ArchitectAgent | `requirements_spec` |
| 2 — Solution Design | ArchitectAgent (+ UIAgent/UXAgent as needed) | `solution_design` |
| 3 — Implementation | CodeAgent (software/data) or ExecutionAgent (other) | `work_product` + `build_log` |
| 4 — Review | ReviewerAgent | `refinement_report` |
| 5 — Handoff | Orchestrator (direct) | `handoff_package` |

The Orchestrator reads the active domain from `config/domain_profiles.yaml` to determine which agent handles Phase 3 (the only phase where the agent varies by domain).

---

## Cross-Session Resumption

After each approved phase the Orchestrator emits a `project_state.md` snapshot. To resume a prior session:

1. Inject `project_state.md` into the session context (file attachment or opening message).
2. The Orchestrator (via `compression_agent.md` Cross-Session Resumption protocol) loads it, emits a status line, and continues from `current_phase`.
3. Phases already in `phase_history` are skipped — only the current and remaining phases run.

---

## Limitations and Workarounds

| Limitation | Workaround |
|---|---|
| No persistent state across sessions | Emit `project_state.md` at each phase; inject at session start to resume |
| No file ingestion | Run `context_loaders/*.py` locally and paste output as the opening message |
| No custom token policy settings | Apply `compressor.py` as a local preprocessing step |
| No multi-agent routing | Use the single-agent fallback below |

### Single-agent fallback

If Antigravity does not support multi-agent routing, run the entire kit as one agent by concatenating all specs in this order:

```
# Orchestrator
<orchestrator.md content>

---
# Architect / Planner Agent
<architect_agent.md content>

---
# Code Agent
<code_agent.md content>

---
# Execution Agent
<execution_agent.md content>

---
# Reviewer Agent
<reviewer_agent.md content>

---
# UI Agent
<ui_agent.md content>

---
# UX Agent
<ux_agent.md content>

---
# Compression Agent
<compression_agent.md content>
```

The Orchestrator simulates routing by switching roles within a single context window. The 6-phase lifecycle still works — the agent simply fulfills each specialist role in turn.
