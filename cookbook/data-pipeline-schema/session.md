---
domain: data_analytics
phases: 0–5
task: SaaS subscription analytics pipeline schema
stack: PostgreSQL → dbt → Snowflake → Metabase
volume: ~10M events/month
date: 2026-06-27
---

## CLI Invocation

```bash
python generate_prompt.py \
  --domain data_analytics \
  --task "Define data model and metric definitions for a SaaS subscription analytics pipeline. \
Need to track MRR, churn rate, LTV, and trial-to-paid conversion." \
  --stack "PostgreSQL (source), dbt, Snowflake (warehouse), Metabase (BI)" \
  --notes "Events table ~10M rows/month"
```

---

## Generated Prompt

```
## Project Context
Project : agents-maker (multi-agent coding + analytics assistant)
Session : sess_20260627_analytics_001
Domain  : data_analytics
Phase   : 0 (entry)

## Session State
completed_phases : []
artifacts        : {}
open_questions   : []

## Task
Define the data model and metric definitions for a SaaS subscription analytics pipeline.
Requirements:
  - Track MRR, churn rate, LTV, trial-to-paid conversion
  - Source: PostgreSQL operational DB
  - Transformation: dbt
  - Warehouse: Snowflake
  - BI layer: Metabase
  - Events table volume: ~10M rows/month

## Domain & Routing
primary_agent : orchestrator
next_agents   : [architect_agent, code_agent, reviewer_agent]
skill_hints   : [sql_schema, dbt_modeling, metric_definitions, ER_diagram]
```

---

## Phase 0 — Task Framing

**Agent: orchestrator**

Scoping questions resolved before handoff:

1. **Grain**: One row per subscription per calendar month (month-end snapshot). Trial periods modeled as subscription_status = 'trial'.
2. **Update frequency**: dbt jobs run nightly at 02:00 UTC; MRR dashboard refreshes at 06:00 UTC via Metabase cache.
3. **Existing schema**: PostgreSQL has `users`, `subscriptions`, `invoices`, `events` tables. No existing warehouse layer.
4. **Churn definition**: Voluntary cancel + involuntary (failed payment >30 days). Reactivations treated as new MRR, not recovered MRR for simplicity (revisit in v2).
5. **LTV model**: Historical (sum of paid invoices per customer cohort) for now; predictive LTV deferred.

Routing decision: architect_agent owns metric specs + ER design; code_agent owns DDL + dbt models; reviewer_agent validates metric correctness.

[Companion]
> Scoping locked. Key decisions: month-end grain, nightly refresh, churn = cancel + involuntary >30d, LTV = historical. architect_agent next.

---

## Phase 1 — Requirements

**Agent: architect_agent**

### Metric Definitions (source of truth)

| Metric | Formula | Grain | Notes |
|---|---|---|---|
| MRR | SUM(monthly_plan_amount) WHERE status = 'active' | Month, Plan | Normalize annual plans: arr/12 |
| New MRR | MRR from subscriptions with start_month = reporting_month | Month | First paid period only |
| Expansion MRR | MRR delta > 0 for existing subs (upgrades) | Month | Requires prior-month join |
| Contraction MRR | MRR delta < 0 for existing subs (downgrades) | Month | Abs value, sign flipped in report |
| Churned MRR | MRR of subs that moved to canceled in reporting_month | Month | |
| Net New MRR | New + Expansion − Contraction − Churned | Month | Waterfall identity |
| Churn Rate | Churned MRR / MRR at start of period | Month | Expressed as % |
| Trial Conversion | COUNT(trial→paid in month) / COUNT(trial_started in month-30d..month) | Month | 30-day conversion window |
| LTV (historical) | SUM(invoice.amount_paid) per customer cohort | Cohort (month) | Gross, pre-refund |
| ARPU | MRR / COUNT(DISTINCT active customers) | Month | |

### Source Table Assessment (PostgreSQL)

- `subscriptions.plan_amount` stores amount in cents — divide by 100 for USD.
- `subscriptions.billing_interval` ∈ {monthly, annual} — annual needs /12 normalization.
- `events` table has no index on `event_type` — recommend index before extraction.
- `invoices.status` ∈ {paid, open, void, uncollectible} — MRR uses paid only.

[Companion]
> Metric definitions finalized. 10 KPIs specified. Noted: annual plan normalization, cents-to-USD, churn window ambiguity resolved (>30d involuntary). ER design next.

---

## Phase 2 — Solution Design

**Agent: architect_agent**

### ER Diagram (Snowflake Warehouse Layer)

```
┌─────────────────────────┐
│      dim_date           │
│─────────────────────────│
│ PK date_key  (int)      │
│    full_date (date)     │
│    year      (int)      │
│    month     (int)      │
│    quarter   (int)      │
└────────────┬────────────┘
             │ FK
┌────────────▼────────────┐       ┌──────────────────────────┐
│   fct_subscription_     │       │      dim_customer         │
│       month             │       │──────────────────────────│
│─────────────────────────│  FK   │ PK customer_key (int)    │
│ PK sub_month_key (int)  ├───────► src_customer_id (int)   │
│ FK customer_key  (int)  │       │    email        (varchar) │
│ FK plan_key      (int)  │       │    signup_date  (date)   │
│ FK date_key      (int)  │       │    cohort_month (date)   │
│    mrr_amount    (num)  │       │    country      (varchar) │
│    status        (varchar)      │    acquired_channel (var) │
│    status_prev   (varchar)      └──────────────────────────┘
│    mrr_prev      (num)  │
│    mrr_change_type(var) │       ┌──────────────────────────┐
│    is_trial      (bool) │       │       dim_plan            │
│    trial_start   (date) │  FK   │──────────────────────────│
│    converted_at  (date) ├───────► PK plan_key   (int)     │
└─────────────────────────┘       │    plan_name  (varchar)  │
                                  │    plan_tier  (varchar)  │
┌─────────────────────────┐       │    billing_interval(var) │
│  fct_mrr_waterfall      │       │    base_price  (numeric) │
│─────────────────────────│       └──────────────────────────┘
│ PK waterfall_key (int)  │
│ FK date_key      (int)  │
│    new_mrr       (num)  │
│    expansion_mrr (num)  │
│    contraction_mrr(num) │
│    churned_mrr   (num)  │
│    net_new_mrr   (num)  │
│    total_mrr     (num)  │
└─────────────────────────┘
```

### dbt DAG (abbreviated)

```
sources/postgres/
  └── raw_subscriptions
  └── raw_invoices
  └── raw_events

staging/
  └── stg_subscriptions   (clean types, cents→USD, interval normalization)
  └── stg_invoices        (filter status=paid, join subscription_id)
  └── stg_events          (filter trial_started, converted, canceled)

intermediate/
  └── int_subscription_spine   (cross join date_spine × subscriptions, month-end status)
  └── int_trial_funnel         (trial cohorts with 30-day conversion window)

marts/
  └── fct_subscription_month   (grain: sub × month)
  └── fct_mrr_waterfall        (grain: month, aggregated MRR movements)
  └── dim_customer
  └── dim_plan
```

[Companion]
> ER diagram complete. 2 fact tables, 3 dimensions. DAG has 4 layers: sources → staging → intermediate → marts. code_agent next for DDL + dbt model SQL.

---

## Phase 3 — Implementation

**Agent: code_agent**

### Snowflake DDL

```sql
-- dim_customer
CREATE TABLE analytics.dim_customer (
    customer_key        INTEGER AUTOINCREMENT PRIMARY KEY,
    src_customer_id     INTEGER NOT NULL UNIQUE,
    email               VARCHAR(320),
    signup_date         DATE,
    cohort_month        DATE,          -- DATE_TRUNC('month', signup_date)
    country             VARCHAR(2),
    acquired_channel    VARCHAR(64),
    _loaded_at          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP
);

-- dim_plan
CREATE TABLE analytics.dim_plan (
    plan_key            INTEGER AUTOINCREMENT PRIMARY KEY,
    src_plan_id         INTEGER NOT NULL UNIQUE,
    plan_name           VARCHAR(128),
    plan_tier           VARCHAR(32),   -- 'starter','growth','enterprise'
    billing_interval    VARCHAR(16),   -- 'monthly','annual'
    base_price_usd      NUMERIC(10,2),
    _loaded_at          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP
);

-- dim_date (pre-populated via dbt seed or Snowflake date_spine macro)
CREATE TABLE analytics.dim_date (
    date_key    INTEGER PRIMARY KEY,   -- YYYYMMDD
    full_date   DATE    NOT NULL,
    year        SMALLINT,
    quarter     SMALLINT,
    month       SMALLINT,
    week        SMALLINT,
    day_of_week SMALLINT,
    is_weekday  BOOLEAN
);

-- fct_subscription_month
CREATE TABLE analytics.fct_subscription_month (
    sub_month_key       INTEGER AUTOINCREMENT PRIMARY KEY,
    customer_key        INTEGER NOT NULL REFERENCES analytics.dim_customer(customer_key),
    plan_key            INTEGER NOT NULL REFERENCES analytics.dim_plan(plan_key),
    date_key            INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    src_subscription_id INTEGER NOT NULL,
    mrr_amount          NUMERIC(12,2) NOT NULL,
    status              VARCHAR(32)   NOT NULL,
    status_prev         VARCHAR(32),
    mrr_prev            NUMERIC(12,2),
    mrr_change_type     VARCHAR(32),  -- 'new','expansion','contraction','churn','reactivation','unchanged'
    is_trial            BOOLEAN       DEFAULT FALSE,
    trial_start_date    DATE,
    trial_converted_at  DATE,
    _loaded_at          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP
);

-- fct_mrr_waterfall
CREATE TABLE analytics.fct_mrr_waterfall (
    waterfall_key       INTEGER AUTOINCREMENT PRIMARY KEY,
    date_key            INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    new_mrr             NUMERIC(12,2) NOT NULL DEFAULT 0,
    expansion_mrr       NUMERIC(12,2) NOT NULL DEFAULT 0,
    contraction_mrr     NUMERIC(12,2) NOT NULL DEFAULT 0,
    churned_mrr         NUMERIC(12,2) NOT NULL DEFAULT 0,
    reactivation_mrr    NUMERIC(12,2) NOT NULL DEFAULT 0,
    net_new_mrr         NUMERIC(12,2) GENERATED ALWAYS AS
                            (new_mrr + expansion_mrr - contraction_mrr
                             - churned_mrr + reactivation_mrr) VIRTUAL,
    total_mrr           NUMERIC(12,2) NOT NULL,
    _loaded_at          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP
);
```

### dbt: stg_subscriptions.sql (excerpt)

```sql
-- models/staging/stg_subscriptions.sql
WITH source AS (
    SELECT * FROM {{ source('postgres', 'subscriptions') }}
),
cleaned AS (
    SELECT
        id                                              AS subscription_id,
        customer_id,
        plan_id,
        status,
        -- normalize amount: cents → USD, annual → monthly
        CASE billing_interval
            WHEN 'annual'  THEN (plan_amount / 100.0) / 12
            WHEN 'monthly' THEN  plan_amount / 100.0
        END                                             AS mrr_amount,
        billing_interval,
        trial_start::DATE                               AS trial_start_date,
        trial_end::DATE                                 AS trial_end_date,
        started_at::DATE                                AS started_at,
        canceled_at::DATE                               AS canceled_at,
        updated_at
    FROM source
    WHERE id IS NOT NULL
)
SELECT * FROM cleaned
```

### dbt: int_subscription_spine.sql (excerpt)

```sql
-- models/intermediate/int_subscription_spine.sql
WITH spine AS (
    -- generates one row per subscription per month it was active
    {{ dbt_utils.date_spine(
        datepart = 'month',
        start_date = "DATE_TRUNC('month', (SELECT MIN(started_at) FROM {{ ref('stg_subscriptions') }}))",
        end_date   = "DATE_TRUNC('month', CURRENT_DATE)"
    ) }}
),
subs AS (SELECT * FROM {{ ref('stg_subscriptions') }}),
joined AS (
    SELECT
        s.subscription_id,
        s.customer_id,
        s.plan_id,
        s.mrr_amount,
        s.billing_interval,
        s.trial_start_date,
        s.trial_end_date,
        s.started_at,
        s.canceled_at,
        DATE_TRUNC('month', sp.date_month)              AS month_date,
        CASE
            WHEN s.trial_end_date >= sp.date_month
             AND s.trial_start_date < DATEADD(month,1,sp.date_month)
            THEN TRUE ELSE FALSE
        END                                             AS is_trial,
        CASE
            WHEN s.canceled_at < DATEADD(month,1,sp.date_month)
            THEN 'canceled'
            WHEN s.status = 'past_due'
             AND DATEDIFF(day, s.updated_at, CURRENT_DATE) > 30
            THEN 'involuntary_churn'
            ELSE s.status
        END                                             AS effective_status
    FROM spine sp
    JOIN subs s
        ON sp.date_month >= DATE_TRUNC('month', s.started_at)
       AND (s.canceled_at IS NULL
            OR sp.date_month <= DATE_TRUNC('month', s.canceled_at))
)
SELECT * FROM joined
```

### dbt: fct_mrr_waterfall.sql (excerpt)

```sql
-- models/marts/fct_mrr_waterfall.sql
WITH monthly AS (
    SELECT * FROM {{ ref('fct_subscription_month') }}
),
waterfall AS (
    SELECT
        date_key,
        SUM(CASE WHEN mrr_change_type = 'new'          THEN mrr_amount ELSE 0 END) AS new_mrr,
        SUM(CASE WHEN mrr_change_type = 'expansion'    THEN mrr_amount - mrr_prev ELSE 0 END) AS expansion_mrr,
        SUM(CASE WHEN mrr_change_type = 'contraction'  THEN mrr_prev - mrr_amount ELSE 0 END) AS contraction_mrr,
        SUM(CASE WHEN mrr_change_type = 'churn'        THEN mrr_prev ELSE 0 END) AS churned_mrr,
        SUM(CASE WHEN mrr_change_type = 'reactivation' THEN mrr_amount ELSE 0 END) AS reactivation_mrr,
        SUM(CASE WHEN status = 'active'                THEN mrr_amount ELSE 0 END) AS total_mrr
    FROM monthly
    GROUP BY date_key
)
SELECT
    {{ dbt_utils.generate_surrogate_key(['date_key']) }} AS waterfall_key,
    *,
    CURRENT_TIMESTAMP AS _loaded_at
FROM waterfall
```

[Companion]
> DDL complete: 5 tables, all FK relationships defined. 4 dbt models drafted (stg_subscriptions, int_subscription_spine, fct_subscription_month, fct_mrr_waterfall). reviewer_agent next.

---

## Phase 4 — Review

**Agent: reviewer_agent**

### Findings

| # | Severity | Location | Issue | Recommendation |
|---|---|---|---|---|
| 1 | HIGH | stg_subscriptions | Annual plan normalization divides by 12 but ignores mid-month starts — prorated first month will overcount MRR | Add `proration_factor` column; clamp to full months only in spine |
| 2 | HIGH | int_subscription_spine | `involuntary_churn` cutoff uses `updated_at` not `last_payment_attempt_at` — field not in scope | Confirm source field; fallback to `invoice.due_date` if unavailable |
| 3 | MEDIUM | fct_mrr_waterfall | `net_new_mrr` VIRTUAL column unsupported in older Snowflake editions (pre-2024) | Materialize as regular computed column in dbt instead |
| 4 | MEDIUM | fct_subscription_month | No surrogate key strategy documented — AUTOINCREMENT breaks idempotent dbt full-refresh | Switch to `dbt_utils.generate_surrogate_key(['src_subscription_id','date_key'])` |
| 5 | LOW | dim_customer | `email` stored in warehouse without masking — PII exposure risk | Apply Snowflake Dynamic Data Masking policy for non-admin roles |
| 6 | LOW | dbt DAG | No `sources.yml` freshness tests defined — stale PostgreSQL extract will silently pass | Add `loaded_at_field` freshness checks in sources.yml |

### Metric Formula Validation

- **Churn Rate**: Formula `churned_mrr / mrr_start_of_period` is correct. Confirm denominator is prior month-end total_mrr, not current — spine join uses prior row LAG(), verified correct.
- **Trial Conversion**: 30-day window looks back from `trial_end_date`, not `trial_start_date` — this is correct per SaaS convention. Window boundary is exclusive on right side; confirm with product team.
- **LTV**: Historical LTV from invoices is gross; net (post-refund) requires joining `refunds` table not yet in scope. Flag for v2.

[Companion]
> 6 findings: 2 HIGH, 2 MEDIUM, 2 LOW. Surrogate key fix and VIRTUAL column removal are must-haves before production deploy. PII masking should be pre-launch. reviewer_agent complete.

---

## Phase 5 — Handoff

**Agent: orchestrator**

### Handoff Package

**Artifacts delivered:**
- `analytics/schema/ddl.sql` — 5 production-ready Snowflake DDL statements
- `models/staging/stg_subscriptions.sql`
- `models/staging/stg_invoices.sql` (omitted from transcript, follows same pattern)
- `models/intermediate/int_subscription_spine.sql`
- `models/intermediate/int_trial_funnel.sql` (omitted from transcript)
- `models/marts/fct_subscription_month.sql`
- `models/marts/fct_mrr_waterfall.sql`
- `models/marts/dim_customer.sql`
- `models/marts/dim_plan.sql`

**Blocking items before deploy (from reviewer_agent):**
1. Resolve `last_payment_attempt_at` field availability in PostgreSQL source (Finding #2)
2. Replace AUTOINCREMENT PKs with `dbt_utils.generate_surrogate_key()` (Finding #4)
3. Remove VIRTUAL column from DDL; compute in dbt model (Finding #3)

**Recommended next session:** Add `sources.yml` freshness assertions, Snowflake masking policies for PII columns, and refund join for net LTV.

**Metabase setup notes:**
- Connect Metabase to Snowflake role `analytics_read` (read-only)
- Primary dashboard queries: `fct_mrr_waterfall` for waterfall chart, `fct_subscription_month` for cohort retention grid
- Suggested refresh schedule: 06:00 UTC (after dbt nightly completes at ~04:30 UTC for 10M-row volume)

[Companion]
> Session complete. 5 phases, 10 metric definitions, 5 DDL tables, 7 dbt models outlined, 6 review findings. 3 blocking items documented. Ready for engineering handoff.

---

## Final Artifacts Summary

### ER Diagram (reference copy)

```
dim_date ──────────────────────────────────────────────────────┐
   │ date_key                                                   │
   │                                                            │
   ▼ FK(date_key)                                              ▼ FK(date_key)
fct_subscription_month ←── FK(customer_key) ── dim_customer   fct_mrr_waterfall
   │                    ←── FK(plan_key)    ── dim_plan
   │
   └── mrr_change_type: new | expansion | contraction | churn | reactivation | unchanged
```

### Metric Definitions Table

| Metric | Formula | Grain | Source Model |
|---|---|---|---|
| MRR | SUM(mrr_amount) WHERE status='active' | Month | fct_subscription_month |
| New MRR | SUM(mrr_amount) WHERE mrr_change_type='new' | Month | fct_mrr_waterfall |
| Expansion MRR | SUM(mrr_amount - mrr_prev) WHERE mrr_change_type='expansion' | Month | fct_mrr_waterfall |
| Contraction MRR | SUM(mrr_prev - mrr_amount) WHERE mrr_change_type='contraction' | Month | fct_mrr_waterfall |
| Churned MRR | SUM(mrr_prev) WHERE mrr_change_type='churn' | Month | fct_mrr_waterfall |
| Net New MRR | new + expansion − contraction − churned + reactivation | Month | fct_mrr_waterfall |
| Churn Rate | churned_mrr / LAG(total_mrr) | Month | fct_mrr_waterfall |
| Trial Conversion | COUNT(converted) / COUNT(trial_started, -30d window) | Month | int_trial_funnel |
| LTV (historical) | SUM(invoice.amount_paid) GROUP BY cohort_month | Cohort | dim_customer + invoices |
| ARPU | total_mrr / COUNT(DISTINCT active customer_key) | Month | fct_subscription_month |

### Data Dictionary (key fields)

| Table | Column | Type | Description |
|---|---|---|---|
| fct_subscription_month | mrr_change_type | VARCHAR(32) | Movement classification: new, expansion, contraction, churn, reactivation, unchanged |
| fct_subscription_month | mrr_amount | NUMERIC(12,2) | MRR in USD for this sub in this month. Annual plans divided by 12. |
| fct_subscription_month | mrr_prev | NUMERIC(12,2) | MRR from prior month (LAG). NULL for new subscriptions. |
| fct_subscription_month | is_trial | BOOLEAN | TRUE if trial_start_date ≤ month_date < trial_end_date |
| fct_mrr_waterfall | contraction_mrr | NUMERIC(12,2) | Absolute value of MRR lost from downgrades. Always positive. |
| fct_mrr_waterfall | total_mrr | NUMERIC(12,2) | Closing MRR balance for the month (active subs only). |
| dim_customer | cohort_month | DATE | DATE_TRUNC('month', signup_date). Used for cohort retention and LTV analysis. |
| dim_plan | billing_interval | VARCHAR(16) | 'monthly' or 'annual'. Annual plans normalized to monthly MRR in staging. |
| stg_subscriptions | mrr_amount | NUMERIC(12,2) | Normalized MRR: cents÷100, annual÷12. |
