# Claude Integration Guide

How to use this kit with Anthropic Claude: Projects, Claude.ai, and the Anthropic API.

---

## Companion Mode (Recommended)

The fastest way to use this kit with Claude. Run two commands once, then one command before every session.

### One-time setup (per project)

```bash
# 1. Bootstrap the project
python agents-maker/tools/init_project.py

# 2. Paste system_prompt.md into Claude as the system prompt or Project Instructions
#    (do this once — it contains all agents + skills pre-assembled)
```

### Before every session

```bash
python agents-maker/tools/generate_prompt.py "what you want to work on"
```

Copy the printed block and paste it as your next message to Claude. That's it.

**What you get back from Claude in Companion Mode:**

Every response ends with a structured block:
```
---
[Companion] Phase: implementation | Domain: software | Est. token budget: ~42%

What to do next (pick one):
[Recommended] A: Write unit tests for the new middleware
Command: python agents-maker/tools/generate_prompt.py "write tests for rate-limiting middleware"

B: Open Phase 4 review on the full auth service
C: Document rate-limit config in the runbook
---
```

You always know what to do next. Paste the `Command:` from option A to continue.

---

## Option A — Claude Projects (claude.ai)

Claude Projects lets you set a persistent system prompt. This is the recommended zero-code integration — one paste, no file uploads needed.

### Setup steps

**1. Create a project**

In Claude.ai, create a new Project. Name it something like "Dev Assistant" or after your project.

**2. Set the Project Instructions**

Open Project Settings → Instructions. Paste the entire contents of `system_prompt.md` as the Project Instructions.

That's it — `system_prompt.md` contains all 8 agents and 12 skills pre-assembled (~28K tokens). No individual file uploads needed.

```
# Copy the full contents of system_prompt.md and paste here:
cat agents-maker/system_prompt.md | pbcopy   # macOS
type agents-maker\system_prompt.md | clip     # Windows
```

**3. Start a session**

Fill in `PROMPT_TEMPLATE.md` and paste it as your first message. Or use the CLI:

```bash
python agents-maker/tools/generate_prompt.py "your task here"
# Copy the printed block → paste as your message
```

---

### Keeping your system prompt current

When you add new agents or skills to the kit, regenerate `system_prompt.md` and repaste it into Project Instructions:

```bash
python agents-maker/tools/init_project.py --update
# Then copy the updated system_prompt.md into Project Instructions
```

Run `python tools/validate_kit.py` first to confirm all 8 integrity checks pass before regenerating.

---

## Option B — Claude API (programmatic)

### Minimal example

```python
import anthropic
from pathlib import Path

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

def load_agent_kit() -> str:
    """Load orchestrator + all agent specs + skills as system context."""
    parts = []
    for path in [
        "agents/orchestrator.md",
        "agents/code_agent.md",
        "agents/ui_agent.md",
        "agents/ux_agent.md",
        "agents/architect_agent.md",
        "agents/compression_agent.md",
    ]:
        parts.append(f"# {path}\n\n{Path(path).read_text()}")
    for skill_file in Path("skills").glob("*.md"):
        parts.append(f"# {skill_file}\n\n{skill_file.read_text()}")
    return "\n\n---\n\n".join(parts)

system_prompt = load_agent_kit()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    system=system_prompt,
    messages=[
        {
            "role": "user",
            "content": (
                "## Project State\n<paste project_summary.py output here>\n\n"
                "Task: Add soft-delete to UserService."
            ),
        }
    ],
)
print(response.content[0].text)
```

### With token optimization (using compressor.py)

```python
from token_optimization.compressor import Compressor, ContextBlock, FileEntry, PolicyLoader
from context_loaders.repo_tree import list_files
from context_loaders.file_chunker import chunk_files

# Load policy
loader = PolicyLoader()
loader.load()
policy = loader.get_workflow_policy("feature_implementation")

# Build context block
files = chunk_files(list_files("/your/repo", filter_paths=["src/"]))
block = ContextBlock(
    project_state=project_summary,
    files=[FileEntry(path=f["path"], content=f["content"]) for f in files],
    conversation_state=conversation_state,
    active_query="Add soft-delete to UserService",
)

compressor = Compressor(policy)
compressed_context, report = compressor.compress(block)

# Send to Claude
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    system=system_prompt,
    messages=[{"role": "user", "content": compressed_context}],
)
```

---

## Token-optimized defaults for Claude

### Concise mode system prompt suffix

Append to the orchestrator system prompt to enable concise mode by default:

```
Output style: concise_bullets
Max response length: 600 tokens
Omit introductory sentences. Start all responses with the first finding or action.
```

### Context window guidance

| Claude model | Max input tokens | Recommended max_input_tokens policy |
|---|---|---|
| claude-haiku-4-5 | 200K | 60,000 |
| claude-sonnet-4-6 | 200K | 100,000 |
| claude-opus-4-7 | 200K | 150,000 |

Set `max_input_tokens` in `token_policies.yaml` well below the model limit to leave room for the system prompt and output.

---

## Using extended thinking (Claude Sonnet / Opus)

For complex architecture tasks, enable extended thinking:

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    system=system_prompt,
    messages=[...],
)
```

Route only to `architect_agent` when thinking is enabled — it is expensive and most specialist tasks do not benefit.

---

## Option C — Claude.ai Free Tier (no Projects access)

If you are on the Claude.ai free plan and do not have access to Projects, use this approach each session:

**1. Open a new Claude.ai conversation.**

**2. Paste `system_prompt.md` as your very first message** (before describing your task):

```
# Paste the full contents of agents-maker/system_prompt.md here as your first message.
# On macOS:
cat agents-maker/system_prompt.md | pbcopy

# On Windows:
type agents-maker\system_prompt.md | clip
```

Send this message first. Claude will acknowledge the agent kit and wait for your task.

**3. Send your task using `PROMPT_TEMPLATE.md`:**

Open `PROMPT_TEMPLATE.md`, fill in the blanks, and send it as your second message. Or use the CLI:

```bash
python agents-maker/tools/generate_prompt.py "your task here"
# Copy the printed block → paste as your second message
```

**Limitations vs. Option A (Projects):** The system prompt uses ~6K–24K tokens of your context window each session. On free-tier models, this leaves less room for file content and conversation history. Use `context_loaders/file_chunker.py` with `--max-lines 100` to keep file snippets small.

**Tip:** Save a `project_state.md` at the end of each session by copying the Orchestrator's final state block. Paste it at the start of the next session (after `system_prompt.md`) to resume without replaying history.

---

## Routing without a project (API-only)

If you cannot use Projects, prepend the relevant agent spec inline:

```python
specialist_prompt = Path("agents/code_agent.md").read_text()
user_message = f"{specialist_prompt}\n\n---\n\n{context}\n\n{user_query}"
```

This is less elegant but fully functional.

---

## Minimal Lifecycle Invocation

You do not need to specify a domain or configure anything beyond a task description. The Orchestrator detects the domain automatically from your message.

### Example — auto-detected domain

```
User: "Help me write a product requirements document for a mobile checkout flow."

Orchestrator behavior:
1. Scores signals: "product" (strong), "requirements" (strong), "mobile" (weak) → domain = product_design, confidence = high
2. Produces task_profile and asks 3–5 scoping questions (Phase 0, qa_brief style)
3. Awaits user approval before advancing to Phase 1
```

No domain hint required. Just describe the task.

### Example — domain hint prefix

If auto-detection might be ambiguous, prefix your message with `[domain: <key>]`:

```
[domain: ops_process] Write an SOP for our employee offboarding process.
```

Valid domain keys: `software`, `content`, `research`, `data_analytics`, `product_design`, `marketing`, `ops_process`. To add a custom domain, see [`docs/domains.md`](../docs/domains.md).

### Example — resuming a prior session

Paste the contents of a saved `project_state.md` file as your opening message:

```
[Paste contents of project_state.md here]

Continue from where we left off.
```

The Orchestrator detects the `project_state.md` format, loads the state, and resumes at the recorded `current_phase` without replaying history.

### Adding `domain_profiles.yaml` to project knowledge (Claude Projects)

For the Orchestrator to load domain profiles at runtime, add `config/domain_profiles.yaml` to your Project knowledge documents alongside the other config files. Without it, the Orchestrator falls back to its built-in inline defaults (same 7 domains, same confidence thresholds).
