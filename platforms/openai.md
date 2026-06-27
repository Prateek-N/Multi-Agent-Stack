# OpenAI Integration Guide

How to use this kit with OpenAI: Chat Completions API, Assistants API, and Responses API (Agents SDK).

---

## Using Companion Mode on OpenAI

Companion Mode works the same on OpenAI as on any other platform. Every response ends with a structured `[Companion]` block offering three ranked next steps. Here is the minimal setup using the Chat Completions API:

### One-time setup

```bash
python agents-maker/tools/init_project.py
# Generates system_prompt.md — load this as the system role every session
```

### Before every session

```bash
python agents-maker/tools/generate_prompt.py "your task here"
# Copy the printed block → send as the user message
```

### Minimal Chat Completions example

```python
from openai import OpenAI
from pathlib import Path

client = OpenAI()  # reads OPENAI_API_KEY from env

system_prompt = Path("agents-maker/system_prompt.md").read_text(encoding="utf-8")

# Generate a routed prompt with the CLI, then send it:
user_message = Path("my_prompt.txt").read_text(encoding="utf-8")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_message},
    ],
    max_tokens=4096,
)
print(response.choices[0].message.content)
# → Response ends with [Companion] block: three ranked next steps
```

The `system_prompt.md` contains all 8 agents + 12 skills pre-assembled. Pass it once as the `system` role. Use `generate_prompt.py` output as the `user` role each turn. For multi-turn sessions, append prior `assistant` + `user` messages to the `messages` list normally.

See [platforms/claude.md](claude.md) for the full Companion Mode walkthrough and lifecycle example.

---

## Option A — Chat Completions API (simplest)

No assistant setup required. Load agent specs as the system message.

```python
from openai import OpenAI
from pathlib import Path

client = OpenAI()  # reads OPENAI_API_KEY from env

def load_orchestrator_system() -> str:
    parts = [Path("agents/orchestrator.md").read_text()]
    for path in Path("agents").glob("*.md"):
        if path.name != "orchestrator.md":
            parts.append(f"# {path.name}\n\n{path.read_text()}")
    for path in Path("skills").glob("*.md"):
        parts.append(f"# {path.name}\n\n{path.read_text()}")
    return "\n\n---\n\n".join(parts)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": load_orchestrator_system()},
        {"role": "user", "content": f"{project_summary}\n\nTask: {user_task}"},
    ],
    max_tokens=4096,
)
print(response.choices[0].message.content)
```

---

## Option B — Assistants API

Create one Assistant per agent. The Orchestrator assistant calls specialist assistants via tool calls or by spawning threads.

### Step 1 — Create assistants

```python
from openai import OpenAI
from pathlib import Path

client = OpenAI()

AGENT_FILES = {
    "orchestrator": "agents/orchestrator.md",
    "code_agent": "agents/code_agent.md",
    "ui_agent": "agents/ui_agent.md",
    "ux_agent": "agents/ux_agent.md",
    "architect_agent": "agents/architect_agent.md",
    "compression_agent": "agents/compression_agent.md",
}

assistants = {}
for name, path in AGENT_FILES.items():
    instructions = Path(path).read_text()
    # Append skill cards to each agent's instructions
    # (Only skills listed in config/agents.yaml for that agent)
    asst = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        model="gpt-4o",
        tools=[],  # add file_search or code_interpreter if needed
    )
    assistants[name] = asst.id
    print(f"Created {name}: {asst.id}")
```

Save the returned IDs to a local file (e.g., `.assistant_ids.json`) for reuse.

### Step 2 — Run a thread

```python
import json, time

ids = json.loads(Path(".assistant_ids.json").read_text())

thread = client.beta.threads.create()
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=f"{project_summary}\n\nTask: {user_task}",
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=ids["orchestrator"],
)

# Poll for completion
while run.status in ("queued", "in_progress"):
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

messages = client.beta.threads.messages.list(thread_id=thread.id)
print(messages.data[0].content[0].text.value)
```

### Step 3 — Register routing as a tool (optional)

To enable the Orchestrator to explicitly call specialists, define a tool:

```python
route_tool = {
    "type": "function",
    "function": {
        "name": "route_to_specialist",
        "description": "Invoke a specialist agent with a structured context block.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent": {
                    "type": "string",
                    "enum": ["code_agent", "ui_agent", "ux_agent", "architect_agent", "compression_agent"],
                    "description": "Which specialist to invoke."
                },
                "context_block": {
                    "type": "string",
                    "description": "Full context block to send to the specialist."
                },
            },
            "required": ["agent", "context_block"],
        },
    },
}

# Add to orchestrator assistant:
client.beta.assistants.update(
    assistant_id=ids["orchestrator"],
    tools=[route_tool],
)
```

Handle the tool call in your run loop and spawn a new thread to the appropriate specialist assistant.

---

## Option C — Responses API / Agents SDK

The OpenAI Agents SDK (beta) supports multi-agent handoffs natively.

```python
from agents import Agent, Runner

orchestrator = Agent(
    name="Orchestrator",
    instructions=Path("agents/orchestrator.md").read_text(),
    model="gpt-4o",
)

code_agent = Agent(
    name="CodeAgent",
    instructions=Path("agents/code_agent.md").read_text(),
    model="gpt-4o",
)

# Register specialists as handoff targets
orchestrator.handoffs = [code_agent]

result = Runner.run_sync(orchestrator, f"{project_summary}\n\nTask: {user_task}")
print(result.final_output)
```

---

## Token policy integration

Apply `token_policies.yaml` via `compressor.py` before constructing messages:

```python
from token_optimization.compressor import Compressor, ContextBlock, PolicyLoader

loader = PolicyLoader()
loader.load()
policy = loader.get_workflow_policy("feature_implementation")
compressor = Compressor(policy)
compressed, report = compressor.compress(context_block)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": compressed},
]
```

---

## Token and cost guidance

| Model | Context window | Recommended max_input_tokens |
|---|---|---|
| gpt-4o | 128K | 50,000 |
| gpt-4o-mini | 128K | 60,000 |
| o3 / o4-mini | 200K | 100,000 |

Set `max_input_tokens` in `token_policies.yaml` to leave at least 4K tokens for the output.

---

## Mapping agents.yaml to OpenAI primitives

| `agents.yaml` field | OpenAI equivalent |
|---|---|
| `name` | `Assistant.name` |
| `description` | `Assistant.description` |
| `skills` | Included inline in `Assistant.instructions` |
| `routing_tags` | Used in Orchestrator's `route_to_specialist` tool logic |
| `cost_tier: high` | Consider `o3` or `gpt-4o`; `cost_tier: low` → `gpt-4o-mini` |
| `default_output_style` | Append style instructions to `Assistant.instructions` |

---

## Minimal Lifecycle Invocation

You do not need to specify a domain. The Orchestrator scores the user's message against `config/domain_profiles.yaml` automatically.

### Example — auto-detected domain

```python
# No domain configuration needed — just describe the task
user_task = "Write a go-to-market strategy brief for our new developer tool."

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": load_orchestrator_system()},
        {"role": "user", "content": user_task},
    ],
)
# Orchestrator detects domain = marketing (signals: "strategy", "brief" → medium confidence)
# then asks 3–5 scoping questions before producing task_profile
```

### Example — domain hint prefix

For unambiguous routing, prefix the user message:

```python
user_task = "[domain: ops_process] Write a runbook for our database failover procedure."
# Orchestrator skips scoring, uses ops_process directly with domain_confidence = high
```

### Storing project_state across threads (Assistants API)

The Orchestrator emits a `project_state.md` snapshot after each approved phase. To persist it across Assistants API sessions, attach it as a file on the thread:

```python
# Save project_state.md emitted by the Orchestrator
project_state_content = extract_project_state_from_response(last_response)
Path("project_state.md").write_text(project_state_content)

# Resume in a new thread by attaching it
new_thread = client.beta.threads.create()
with open("project_state.md", "rb") as f:
    file = client.files.create(file=f, purpose="assistants")

client.beta.threads.messages.create(
    thread_id=new_thread.id,
    role="user",
    content="Continue from where we left off.",
    attachments=[{"file_id": file.id, "tools": [{"type": "file_search"}]}],
)
```

### domain_profiles.yaml via file_search

To give the Orchestrator access to domain profiles at runtime, upload `config/domain_profiles.yaml` as a vector store file and enable `file_search` on the orchestrator assistant. The Orchestrator will retrieve it when scoring domain signals.

```python
vector_store = client.beta.vector_stores.create(name="agent-kit-config")
client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id,
    files=[open("config/domain_profiles.yaml", "rb"),
           open("config/token_policies.yaml", "rb")],
)
client.beta.assistants.update(
    assistant_id=ids["orchestrator"],
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)
