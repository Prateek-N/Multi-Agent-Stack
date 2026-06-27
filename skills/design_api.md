# Skill: design_api

## Description

Draft a complete, unambiguous API contract for a set of related endpoints or an interface definition. Output is a structured contract that a developer can implement against without requiring further clarification. Covers REST, GraphQL (query/mutation list), and RPC-style interfaces.

---

## When to invoke

- The Architect Agent needs to define the public surface of a new service.
- A feature requires new endpoints and the contract must be agreed before implementation begins.
- An existing API is being versioned or extended and the delta must be documented.

---

## Input expectations

| Input | Required | Description |
|---|---|---|
| `feature_description` | Yes | What the API enables the client to do |
| `api_style` | Yes | `REST` \| `GraphQL` \| `RPC` \| `event` |
| `existing_contracts` | No | Snippets of existing API contracts to ensure consistency |
| `auth_model` | No | `none` \| `bearer_token` \| `api_key` \| `oauth2` \| `session` |
| `versioning_strategy` | No | `url_prefix` \| `header` \| `none` |
| `non_functional` | No | Latency target, rate limits, pagination requirements |

**If required input is missing:**
- `feature_description` absent → ask: "What should this API allow a client to do? (one sentence is enough to start.)"
- `api_style` absent → infer from project stack (`project.yaml`): Python/FastAPI → REST, GraphQL server present → GraphQL, event-driven stack → event. State the assumption; user may override inline.
- `auth_model` absent → default to `bearer_token` for external APIs, `none` for internal. State assumption in the contract header.

---

## Output format

### REST

```
## API Contract: <feature name>

**Base path**: `/api/v<N>/<resource>`
**Auth**: <auth_model>

| Method | Path | Description | Request body | Response | Error codes |
|---|---|---|---|---|---|
| POST | `/resource` | <desc> | `{field: type}` | `201 {id, ...}` | 400, 409 |
| GET | `/resource/{id}` | <desc> | — | `200 {id, ...}` | 404 |
| PATCH | `/resource/{id}` | <desc> | `{field?: type}` | `200 {id, ...}` | 400, 404 |
| DELETE | `/resource/{id}` | <desc> | — | `204` | 404 |

### Request / Response Schemas

**POST /resource — Request**
\`\`\`json
{
  "field": "string",   // required; max 255 chars
  "other": "integer"   // optional; default: 0
}
\`\`\`

**POST /resource — Response (201)**
\`\`\`json
{
  "id": "uuid",
  "field": "string",
  "created_at": "ISO8601"
}
\`\`\`

### Error Response Shape
\`\`\`json
{
  "error": "string",       // machine-readable code
  "message": "string",     // human-readable
  "details": {}            // optional; field-level validation errors
}
\`\`\`
```

### GraphQL

```
## GraphQL Contract: <feature name>

**Queries**
| Name | Arguments | Returns | Description |
|---|---|---|---|

**Mutations**
| Name | Input type | Returns | Description |
|---|---|---|---|

**Types**
\`\`\`graphql
type Resource {
  id: ID!
  field: String!
}
\`\`\`
```

### Event / async

```
## Event Contract: <feature name>

| Event name | Producer | Consumers | Payload schema | Ordering guarantee |
|---|---|---|---|---|
```

---

## Token cost tier

**Medium.** Schema detail depends on endpoint count. Typical output: 400–800 tokens.

Compression hint: if the contract is long, the caller may request "schema stubs only" — field names and types without descriptions or examples.

---

## Notes

- Always include at least one error code per endpoint. "200 only" contracts are incomplete.
- Use consistent field naming: match the existing project convention (snake_case vs camelCase) visible in `existing_contracts`.
- Do not prescribe implementation details (ORM, DB table name, handler class). The contract is interface-only.
