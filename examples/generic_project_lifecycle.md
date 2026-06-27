# Example Session: Generic Project Lifecycle

Two annotated mini-scenarios demonstrating the full 6-phase lifecycle:

1. **Software** — complaint-tracking microservice for a government portal.
2. **Research** — market research brief on algorithmic trading among Indian retail traders.

Each scenario shows example prompts, orchestrator responses at each phase, approval gates, and how `project_state` evolves.

---

## Scenario A — Software: Complaint-Tracking Microservice

**Opening message from user**:
> Build a microservice that tracks user complaints with SLAs for an Indian government portal. The portal is Python/FastAPI. We use Postgres and RabbitMQ already.

---

### Phase 0 — Task Framing

**Orchestrator detects**: keywords `microservice`, `FastAPI`, `Postgres` → domain: `software`. New service → `greenfield`.

**Orchestrator response** (style: `qa_brief`):

```
I've detected this is a greenfield software task. Before I frame it precisely:

1. What SLA tiers do you need? (e.g., P1 = resolve in 24h, P2 = 72h, P3 = 7 days)
2. Who raises complaints — citizens via a web portal, internal staff, or both?
3. Is there an existing auth system, or does this service handle auth itself?
4. Should escalation notifications go via email, SMS, RabbitMQ events, or all three?
5. Any compliance requirements? (e.g., data residency, RTI Act audit trail)
```

**User answers**: 3 tiers (P1/P2/P3), citizens via web portal, existing JWT auth, email + RabbitMQ event, RTI Act audit trail required.

**Orchestrator produces `task_profile`**:

```
## task_profile
- domain: software
- task_type: greenfield
- goal: Microservice to track citizen complaints with 3-tier SLAs, escalation, and RTI audit trail
- constraints: [Python 3.11, FastAPI, Postgres, RabbitMQ, existing JWT auth, RTI compliance]
- inputs_available: [existing auth service, RabbitMQ broker config]
- success_criteria: Complaints can be filed, tracked, escalated on SLA breach, and audited
- primary_agents: [architect_agent, code_agent, reviewer_agent]
- applicable_token_policy: generic_project_lifecycle.software
```

**Approval gate**:
```
Phase 0 complete. Artifact: task_profile

A) Approve — proceed to Phase 1 (Requirements)
B) Request changes
C) Change direction
```
*User: A*

---

### Phase 1 — Requirements

**Architect/Planner Agent produces `requirements_spec`** (style: `requirements_spec`):

```
## requirements_spec

### Goals
- Track complaints through lifecycle: Filed → Acknowledged → In Progress → Resolved → Closed
- Enforce SLA: P1=24h, P2=72h, P3=7 days; auto-escalate on breach
- Emit RabbitMQ event on status change and SLA breach
- RTI-compliant audit trail: every state change logged with actor + timestamp

### Non-Goals
- User authentication (existing JWT service handles this)
- Frontend UI (API only)
- Complaint categorisation / ML triage (future phase)

### Stakeholders
| Role | Need |
|---|---|
| Citizen | File and track complaint status |
| Portal Admin | View all complaints, override SLA tier |
| System (SLA job) | Escalate complaints that breach SLA |
| Compliance Officer | Audit trail export |

### Deliverables
| Deliverable | Acceptance criteria |
|---|---|
| REST API | All 7 endpoints functional, documented, auth-protected |
| SLA background job | Escalates within 5 min of breach; emits RabbitMQ event |
| Postgres schema | Complaint + audit_log tables with migration |
| Test suite | ≥80% line coverage; all SLA breach paths covered |

### Constraints
- [technical] Python 3.11, FastAPI, SQLAlchemy, Alembic, pytest
- [compliance] Every state change must be written to audit_log (RTI Act)
- [technical] No new infrastructure — use existing Postgres + RabbitMQ
- [time] MVP in 2 sprints

### Assumptions
- JWT tokens contain user_id and role claims
- RabbitMQ exchange `portal.events` already exists
- SLA clock starts at complaint creation time, not acknowledgment
```

**Approval gate**:
```
Phase 1 complete. Artifact: requirements_spec

A) Approve — proceed to Phase 2 (Solution Design)
B) Request changes — revise requirements_spec (specify what to change)
C) Change direction — restart Phase 1 with a different scope
D) Abort
```
User selects A.

---

### Phase 2 — Solution Design

**Architect/Planner Agent produces `solution_design`** (style: `solution_design`):

Key outputs (abbreviated):

**API Contract**:
| Method | Path | Description |
|---|---|---|
| POST | `/complaints` | File a new complaint |
| GET | `/complaints/{id}` | Get complaint detail + history |
| PATCH | `/complaints/{id}/status` | Update status (admin only) |
| POST | `/complaints/{id}/escalate` | Manual escalation |
| GET | `/complaints` | List with filters (status, tier, date range) |
| GET | `/complaints/{id}/audit` | RTI audit trail for a complaint |
| GET | `/health` | Liveness check |

**Data model**:
```sql
complaints (id, citizen_id, title, body, tier, status, created_at, resolved_at, escalated_at)
audit_log  (id, complaint_id, actor_id, action, from_status, to_status, timestamp, metadata)
```

**SLA job design**: APScheduler task runs every 5 minutes; queries complaints where `status NOT IN ('resolved','closed')` and `NOW() - created_at > sla_threshold(tier)`; updates status to `escalated`, writes audit_log row, publishes `complaint.sla_breached` to RabbitMQ.

**ADR**: Use APScheduler (in-process) over a separate Celery worker — simpler ops for MVP; revisit if job volume exceeds 1000 complaints/run.

**Approval gate**:
```
Phase 2 complete. Artifact: solution_design

A) Approve — proceed to Phase 3 (Implementation)
B) Request changes — revise solution_design (specify section to change)
C) Change direction — restart Phase 2 with a different approach
D) Abort
```
User selects A.

---

### Phase 3 — Implementation (abbreviated)

**Code Agent proposes build order**:
1. Postgres models + Alembic migration
2. Repository layer (ComplaintRepository, AuditRepository)
3. Service layer (ComplaintService, SLAService)
4. API routes + dependencies
5. SLA background job
6. Test suite

Each increment delivered in `implementation_slice` format. Example (Increment 1):

```
## Increment 1: Postgres models + migration

Increment Plan
- This slice: SQLAlchemy models for complaints + audit_log; Alembic migration
- Depends on: approved data model from solution_design
- Next slice: Repository layer

[diff showing models/complaint.py, models/audit_log.py, migrations/001_initial.py]

What changed and why
- audit_log.metadata stored as JSONB for flexibility; RTI audit needs actor context that varies by action type
- complaint.escalated_at nullable; only set on SLA breach

Caveats
- Migration assumes Postgres 14+; check target environment version

build_log entry: "Increment 1 — Postgres models: complaints + audit_log tables, Alembic migration 001"

---
Approve this increment / request changes / change direction?
```

**Example: user requests changes on Increment 1**

> **User:** Request changes — add a `CHECK` constraint so `status` only allows known values, and index `complaints(citizen_id, created_at)` for the list query.

> **Orchestrator → Code Agent (Increment 1 revised):**
> ```
> ## Increment 1 (revised): Postgres models + migration
>
> Increment Plan
> - This slice: same as before + CHECK constraint on status + composite index
> - Depends on: approved data model from solution_design
> - Next slice: Repository layer (unchanged)
>
> + ALTER TABLE complaints ADD CONSTRAINT chk_status
> +   CHECK (status IN ('open','in_review','escalated','resolved','closed'));
> + CREATE INDEX idx_complaints_citizen_created
> +   ON complaints(citizen_id, created_at DESC);
>
> What changed and why
> - CHECK constraint enforces the domain enum at the DB layer; cheaper than application-only validation
> - Composite index covers the GET /complaints list query filter used by citizen dashboards
>
> build_log entry: "Increment 1 (revised) — models + migration + status constraint + list index"
>
> ---
> Approve this increment / request changes / change direction?
> ```

User approves. Code Agent continues to Increment 2.

**project_state after Phase 3** (abbreviated):
```
current_phase: review_refinement
build_log:
  - Increment 1: Postgres models + migration
  - Increment 2: Repository layer (ComplaintRepository, AuditRepository)
  - Increment 3: Service layer with SLA logic
  - Increment 4: API routes + JWT dependency injection
  - Increment 5: APScheduler SLA job
  - Increment 6: pytest suite (87% line coverage)
key_decisions:
  - APScheduler over Celery (Turn 9, ADR approved)
  - SLA clock starts at created_at not acknowledged_at (Turn 4)
```

---

### Phase 4 — Review

**Reviewer Agent produces `refinement_report`** (abbreviated):

```
Verdict: minor_revisions_needed
Summary: 0 critical, 2 high, 3 medium, 1 low

| Severity | Area | Issue | Recommendation |
|---|---|---|---|
| high | security | PATCH /complaints/{id}/status has no ownership check — any admin can update any complaint | Add portal_id scoping to ComplaintRepository.get() |
| high | correctness | SLA job does not handle complaints created before service deployed (missing backfill guard) | Add WHERE created_at >= service_start_date config var |
| medium | test_coverage | No test for concurrent SLA escalation (race condition) | Add test using threading.Barrier |
| medium | correctness | audit_log.metadata not validated — None can be inserted | Add NOT NULL DEFAULT '{}' to migration |
| medium | compliance | audit_log has no index on complaint_id — RTI export query will be slow at scale | Add index idx_audit_log_complaint_id |
| low | readability | SLAService.check_and_escalate() is 60 lines — extract _compute_breach() helper | Refactor for testability |

Positive Findings
- Repository layer cleanly separates data access from business logic
- All 7 endpoints protected with JWT dependency; consistent error shape across routes
```

Code Agent applies fixes. Reviewer confirms: "All critical and high findings resolved. Ready for handoff."

---

### Phase 5 — Handoff

**`handoff_package`**:

```
## Summary
- Complaint-tracking microservice: 7 REST endpoints, 3-tier SLA enforcement, RTI audit trail
- Tech: FastAPI + SQLAlchemy + APScheduler + RabbitMQ publisher
- Test coverage: 91% line coverage after Phase 4 fixes

## How to Deploy
1. Set env vars: DATABASE_URL, RABBITMQ_URL, JWT_SECRET, SLA_SERVICE_START_DATE
2. Run: alembic upgrade head
3. Start: uvicorn app:app --host 0.0.0.0 --port 8000

## What's Done
- All 7 endpoints (see API contract in solution_design)
- SLA job (runs every 5 min; breach → escalated status + audit_log + RabbitMQ event)
- Full RTI audit trail with JSONB metadata

## What's Next
P1 (must do before production):
- Load test SLA job with 10K+ complaints to validate APScheduler at scale
- Add complaint_id to JWT scope validation (portal multi-tenancy)

P2 (strongly recommended):
- Add GET /complaints export endpoint for bulk RTI requests
- Add RabbitMQ consumer for complaint acknowledgment from field teams

P3 (future enhancement):
- ML complaint triage (auto-assign tier based on text)
- Citizen-facing status push notifications
```

**project_state evolution summary**:
| Turn | Milestone |
|---|---|
| 3 | task_profile confirmed |
| 6 | requirements_spec approved |
| 10 | solution_design approved (ADR for APScheduler) |
| 21 | All 6 implementation increments approved |
| 24 | refinement_report: 2 high fixed |
| 26 | handoff_package confirmed |

---

---

## Scenario B — Research: Algorithmic Trading Market Brief

**Opening message from user**:
> Write a 5-page market research brief on algorithmic trading adoption among Indian retail traders. Audience is fintech analysts. Public sources only.

---

### Phase 0 — Task Framing

**Orchestrator detects**: "market research brief", "adoption", "Indian retail traders" → domain: `research`, type: `greenfield`.

**Orchestrator response** (style: `qa_brief`):

```
1. 5 pages — roughly 2,500 words or formatted PDF pages?
2. Should this cover only retail adoption, or also compare with institutional algo trading?
3. Key timeframe: current state (2024–2025), or historical trend since SEBI first allowed algos?
4. Any specific angle you want emphasised — technology, regulation, platforms, or barriers?
5. Should I include a recommendations section, or findings + outlook only?
```

**User**: ~2,500 words, retail only, current state + near-term outlook, barriers + regulation most important, findings + outlook only (no recommendations).

**`task_profile`**:
```
## task_profile
- domain: research
- task_type: greenfield
- goal: 2,500-word brief on algo trading adoption among Indian retail traders (barriers + regulation focus)
- constraints: [public sources only, fintech analyst audience, professional tone, findings + outlook only]
- inputs_available: []
- success_criteria: Brief covers adoption rate, barriers, regulatory landscape, platform comparison, and near-term outlook with cited public sources
- primary_agents: [architect_agent, execution_agent, reviewer_agent]
```

---

### Phase 1 — Requirements

**`requirements_spec`** (abbreviated):

```
### Goals
- Quantify retail algo trading adoption where public data allows
- Identify primary barriers to wider adoption
- Summarise SEBI's regulatory framework and recent changes
- Compare 2–3 major platforms enabling retail algo trading
- Provide a near-term (12–18 month) outlook

### Non-Goals
- Institutional or HFT algo trading
- Recommendations for investors or platforms
- Primary research (surveys, interviews)

### Constraints
- [compliance] Public sources only; cite every factual claim
- [tone] Professional, data-driven; avoid advocacy language
- [length] 2,400–2,600 words across 7 sections
```

---

### Phase 2 — Solution Design

**Architect/Planner Agent produces `solution_design`** — document outline + research plan:

```
## solution_design

### Context
Indian retail participation in algorithmic trading has grown significantly post-SEBI's 2012 framework,
but penetration remains low relative to total retail investors. This brief maps the current landscape
for a fintech analyst audience.

### Approach
Desk research using SEBI circulars, NSE/BSE statistics, fintech industry reports (NASSCOM, BCG),
and major financial press (Economic Times, Mint). Analysis framework: PESTLE for barrier analysis.

### Structure (Document Outline)
1. Executive Summary (drafted last, ~200 words)
2. Market Size & Adoption Rate (~350 words) — quantitative data on retail algo trader count
3. Key Adoption Drivers (~350 words) — smartphone penetration, discount brokers, API availability
4. Barriers to Wider Adoption (~450 words) — PESTLE analysis: tech literacy, capital, regulation, trust
5. Regulatory Landscape (~400 words) — SEBI framework, algo approval process, 2022 circular
6. Platform Comparison (~350 words) — Zerodha Streak, Upstox Pro, Angel One SmartAPI
7. Near-Term Outlook (~400 words) — SEBI sandbox, institutional spillover, UPI/ONDC implications
8. Executive Summary (return to draft after sections 2–7 complete)

### Research Questions
- RQ1: How many Indian retail investors currently use algo trading? (Section 2)
- RQ2: What factors have driven adoption? (Section 3)
- RQ3: What prevents wider adoption? (Section 4, PESTLE)
- RQ4: What does SEBI's current framework permit and restrict? (Section 5)
- RQ5: How do the top 3 platforms compare on accessibility and feature depth? (Section 6)
- RQ6: What will shape adoption in the next 12–18 months? (Section 7)

### Risks & Open Questions
1. Public data on retail algo trader count is sparse — may need to use proxy metrics (API activations, platform disclosures)
2. Platform comparison data may be outdated if pricing changed post-research date
```

---

### Phase 3 — Drafting (abbreviated)

**Execution Agent proposes draft order**: Sections 2 → 3 → 4 → 5 → 6 → 7 → 1 (Executive Summary last).

**Increment 3 example** (Barriers section):

```
## Increment 3: Section 4 — Barriers to Wider Adoption

Increment Plan
- This slice: PESTLE analysis of adoption barriers (~450 words)
- Depends on: Approved Sections 2 and 3 (for context references)
- Next slice: Section 5 — Regulatory Landscape

---

## 4. Barriers to Wider Adoption

Despite favourable macro conditions, algo trading penetration among Indian retail investors
remains below 1% of active equity traders (Source: NSE, 2024). A PESTLE analysis reveals
barriers across six dimensions.

**Political / Regulatory**: SEBI's 2022 circular requires all third-party algo strategies to be
approved by exchanges before deployment. [DATA: Exact approval timeline from NSE not publicly
disclosed.] This has deterred smaller platforms from launching algo marketplaces...

[CONFLICT: BCG 2023 estimates 0.8% penetration; NASSCOM 2024 cites "less than 2%" — using
the more conservative BCG figure given it is methodology-documented.]

...

**build_log entry**: "Increment 3 — Section 4 (Barriers): PESTLE analysis, 447 words, 4 sources cited, 1 data gap flagged"

---
Approve this increment / request changes / change direction?
```

---

### Phase 4 — Review

**Reviewer Agent `refinement_report`** (abbreviated):

```
Verdict: minor_revisions_needed
Summary: 0 critical, 1 high, 2 medium, 1 low

| Severity | Area | Issue | Recommendation |
|---|---|---|---|
| high | research | Section 5 (Regulatory) describes the 2012 framework but does not mention SEBI's 2024 consultation paper on algo trading — significant omission for "current state" framing | Add paragraph on 2024 consultation paper and its implications |
| medium | content | Executive Summary written before Section 7 was finalised; Outlook summary does not match Section 7 content | Revise Executive Summary after Section 7 approval |
| medium | style | "Proliferation" used 4 times across sections 2 and 3 — noticeable repetition | Vary vocabulary |
| low | citations | Section 6 platform comparison cites "platform website, 2024" — should use specific page title | Improve citation specificity |

Positive Findings
- PESTLE framework in Section 4 is well-structured and consistently applied
- Data gap flags ([DATA:] and [CONFLICT:]) are used correctly — reviewer can identify unverified claims immediately
```

Execution Agent applies fixes. Reviewer confirms ready for handoff.

---

### Phase 5 — Handoff

```
## Summary
- 2,580-word market research brief on Indian retail algo trading
- Covers: market size, adoption drivers, barriers (PESTLE), SEBI regulation, platform comparison, 12-month outlook
- 18 public sources cited; 2 data gaps explicitly flagged for further verification

## What's Done
- All 7 sections drafted and reviewed
- 2024 SEBI consultation paper incorporated (Phase 4 fix)

## What's Next
P1 (before distribution):
- Verify the 2 [DATA:] placeholders with primary sources or remove them
- Legal review if distributing to regulated entities (investment advice boundary)

P2 (strongly recommended):
- Commission a 1-page visual summary (charts: adoption rate trend, PESTLE heatmap)
- Refresh platform comparison data quarterly

P3 (future research):
- Primary research: survey 200 retail traders on top 3 barriers to validate PESTLE findings
- Deep-dive on SEBI 2024 consultation paper outcomes once finalised
```

**project_state evolution summary**:
| Turn | Milestone |
|---|---|
| 3 | task_profile confirmed |
| 5 | requirements_spec approved |
| 7 | solution_design approved (7-section outline + PESTLE framework) |
| 16 | All 7 section drafts approved (Sections 2–7 + Executive Summary) |
| 19 | refinement_report: 1 high fixed (2024 SEBI paper added) |
| 21 | handoff_package confirmed |
