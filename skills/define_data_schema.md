# Skill: define_data_schema

## Description

Produce a data schema artifact: entity-relationship sketch (ASCII), metric definition table, and data dictionary. Used by the Code Agent and Architect Agent in `data_analytics` tasks (Phases 2–3) and by any domain when a solution design requires specifying data structures.

---

## When to invoke

- User requests a data model, schema, data dictionary, or metric definitions.
- Architect Agent needs to specify data structures as part of a solution design.
- Code Agent needs a schema contract before writing queries or pipeline code.
- Review phase identifies metrics that lack formula or grain definitions.

---

## Input expectations

| Input | Required | Description |
|---|---|---|
| `entities` | Yes | List of data entities (tables, streams, or collections). Each: `{name, description, key_fields[]}` |
| `metrics` | Yes | List of metrics to define. Each: `{name, description}` |
| `grain` | Yes | The atomic unit each metric row represents (e.g., "one row per user per day") |
| `filters` | No | Standard filters applied to the data (e.g., `is_active=true`, `event_type='purchase'`) |
| `existing_tools` | No | Data stack in use (e.g., "BigQuery + dbt", "Postgres + SQLAlchemy", "Spark") |
| `relationships` | No | Foreign-key or join relationships between entities |

**If required input is missing:**
- `entities` — ask: "What data entities are involved? (e.g., users, orders, events — with their primary key fields)"
- `metrics` — ask: "Which metrics need to be defined? List each by name and what it measures."
- `grain` — ask: "What does one row in the output represent? (e.g., one user, one transaction, one day)"
- `filters` — default to "none" and note: "Add standard filters if some records should always be excluded."
- `existing_tools` — default to "unspecified"; omit tool-specific syntax notes from output.

---

## Output format

### 1. Entity-Relationship Sketch (ASCII)

```
## Entity-Relationship Sketch

<EntityA> (PK: <key>)
  ├── <field>: <type>
  └── <field>: <type>
        |
        | 1:N
        ↓
<EntityB> (PK: <key>, FK: <EntityA.key>)
  ├── <field>: <type>
  └── <field>: <type>
```

Use `|` for 1:1, `1:N` for one-to-many, `M:N` for many-to-many. If relationships were not provided, output a flat list of entities and note: "Relationships not specified — add FK links after confirming cardinality."

### 2. Metric Definition Table

```markdown
## Metric Definitions

| Metric | Formula | Grain | Standard Filters | NULL behavior | Owner |
|---|---|---|---|---|---|
| <metric_name> | <formula or description> | <grain> | <filter or "none"> | <what NULL means / how handled> | <team or role> |
```

**Required fields per metric row:**
- **Formula** — either a precise SQL-style expression or a plain-language definition if formula is not yet specified (flag with `[draft]`)
- **Grain** — must match the stated `grain` input or note the exception
- **NULL behavior** — explicitly state what a NULL value means for this metric (e.g., "NULL = user has no purchases", "NULL = sensor offline")

### 3. Data Dictionary

```markdown
## Data Dictionary

### <EntityName>
| Field | Type | Description | Nullable | Example |
|---|---|---|---|---|
| <field> | <type> | <description> | Yes / No | <example value> |
```

Generate one section per entity listed in `entities`.

---

## Token cost tier

**Medium.** Requires translating business descriptions into precise technical definitions. Output grows with number of entities and metrics. Typical output: 400–900 tokens.

---

## Notes

- If a metric formula is ambiguous, output it as `[draft: <best interpretation>]` and add a clarifying question below the table.
- Flag any metric that cannot be computed from the provided entities: `[BLOCKED: requires <missing entity or field>]`.
- If `existing_tools` is specified, add a "Tool notes" row below each metric noting any platform-specific behavior (e.g., BigQuery's handling of DIV0, dbt metric layer syntax).
- The ER sketch uses ASCII art only — no Mermaid or PlantUML unless the user explicitly requests a diagram format.
