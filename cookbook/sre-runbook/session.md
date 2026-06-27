<!--
domain: ops_process
phase_range: 0–5
task: SRE on-call runbook — PostgreSQL primary→replica failover (Patroni/HAProxy/PgBouncer/K8s)
-->

---
domain: ops_process
phase_range: "0–5"
task: PostgreSQL 15 primary-to-replica failover runbook (Patroni, HAProxy, PgBouncer, Kubernetes)
rto: "< 5 minutes"
team: 3 SREs, 2 on-call engineers
---

## CLI Invocation

```bash
python generate_prompt.py \
  --domain ops_process \
  --task "Write an on-call runbook SOP for PostgreSQL primary→replica failover using Patroni." \
  --stack "PostgreSQL 15, Patroni, HAProxy, PgBouncer, Kubernetes" \
  --team "3 SREs, 2 on-call engineers" \
  --rto "< 5 minutes" \
  --scenarios "primary_crash,network_partition,planned_maintenance" \
  --output-format runbook
```

---

## Generated Prompt

```
## Project Context
Domain      : ops_process
Stack       : PostgreSQL 15 · Patroni (etcd backend) · HAProxy · PgBouncer · Kubernetes 1.29
Team        : 3 SREs (Alice, Bob, Carol), 2 on-call engineers (Dave, Eve)
RTO target  : < 5 minutes (primary crash), < 10 minutes (network partition)
Artifact    : Numbered SOP runbook + RACI matrix + exception table

## Session State
phase       : 0 (Task Framing — no prior context)
prior_work  : none
open_issues : none

## Task
Produce a production-grade on-call runbook covering three failover scenarios:
  1. Unplanned primary crash (hardware / OOM / kernel panic)
  2. Network partition (primary isolated; replica still reachable by clients)
  3. Planned maintenance failover (rolling upgrade, node drain)

Each scenario must include:
  - Pre-conditions / detection signals
  - Step-by-step remediation (real CLI commands, not pseudocode)
  - Rollback / undo path
  - Definition of Done

Also produce:
  - RACI matrix mapping each step to Alice/Bob/Carol/Dave/Eve
  - Exception table (scenario × failure mode × mitigation)

## Domain & Routing
domain         : ops_process
primary_agent  : architect_agent   (phases 1–2: process map, RACI skeleton)
secondary_agent: execution_agent   (phase 3: full runbook draft)
review_agent   : reviewer_agent    (phase 4: edge-case audit)
orchestrator   : handles phase 0 scoping and phase 5 handoff
constraints    :
  - All kubectl commands must target namespace "postgres" unless noted
  - Patroni REST API base: http://patroni-svc:8008
  - HAProxy stats socket: /var/run/haproxy/admin.sock
  - PgBouncer admin DB: psql -p 6432 -U pgbouncer pgbouncer
  - etcd cluster: etcd-0.etcd-headless:2379 (3-node)
```

---

## Phase 0 — Task Framing

**Agent:** orchestrator

Scoping complete. Confirmed parameters:

- **RTO < 5 min** applies to scenario 1 (primary crash). Scenario 2 (network partition) gets a
  relaxed 10-minute budget because split-brain resolution requires human confirmation before
  Patroni's DCS lock expires (default `ttl: 30s`, `loop_wait: 10s`, `retry_timeout: 10s`).
- **Team mapping:** Alice and Bob are primary on-call SREs (pager rotation). Carol is senior SRE
  (escalation). Dave and Eve are on-call engineers (secondary responders, runbook executors).
- **Patroni DCS:** etcd 3-node cluster. Quorum requires 2/3 nodes. Loss of etcd quorum blocks
  automatic leader election — this becomes a manual procedure (captured in exception table).
- **HAProxy:** Two backends defined — `pg_primary` (read-write, port 5432) and `pg_replica`
  (read-only, port 5433). HAProxy health-checks Patroni `/primary` and `/replica` endpoints
  every 2 seconds.
- **PgBouncer:** Running in transaction-pooling mode. During failover, in-flight transactions
  will be terminated; PgBouncer reconnects automatically once HAProxy re-routes.

Routing: architect_agent → phases 1 and 2. Execution_agent → phase 3. Reviewer_agent → phase 4.

> **[Companion]** Phase 0 locked. Architect agent will now produce the process map skeleton and
> RACI structure. No commands to run yet — this phase is scoping only.

---

## Phase 1 — Requirements (Process Map Skeleton)

**Agent:** architect_agent

### Failover Process Map

```
DETECT → TRIAGE → ISOLATE → PROMOTE → REPOINT → VALIDATE → CLOSE
```

| Stage    | Owner         | Tooling                          | Exit Criterion                          |
|----------|---------------|----------------------------------|-----------------------------------------|
| DETECT   | Dave/Eve      | PagerDuty alert, Patroni metrics | Alert fired; primary unreachable >30 s  |
| TRIAGE   | Alice/Bob     | `patronictl list`, kubectl logs  | Scenario identified (crash/partition/planned) |
| ISOLATE  | Alice/Bob     | `patronictl pause`, kubectl cordon | Writes blocked or primary fenced      |
| PROMOTE  | Patroni auto / Alice | `patronictl failover`       | New primary confirmed in DCS            |
| REPOINT  | Alice/Bob     | HAProxy reload, PgBouncer reload | Traffic flowing to new primary          |
| VALIDATE | Dave/Eve      | `psql` smoke test, replication lag | Lag < 10 MB; app health checks green  |
| CLOSE    | Carol         | PagerDuty resolve, postmortem ticket | Incident closed; old primary demoted  |

### Inputs Required from execution_agent
1. Exact `patronictl` and `kubectl` command sequences per scenario.
2. HAProxy socket commands for backend weight manipulation.
3. PgBouncer `PAUSE` / `RESUME` sequence with timeout.
4. etcd manual leader-wipe procedure (exception path).

> **[Companion]** Process map locked. Seven stages, five roles. Architect will now design the
> RACI matrix and exception table structure before execution_agent drafts the full runbook.

---

## Phase 2 — Solution Design (RACI + Exception Table Structure)

**Agent:** architect_agent

### RACI Matrix (skeleton — execution_agent will fill command detail)

| Step                              | Alice | Bob  | Carol | Dave | Eve  |
|-----------------------------------|-------|------|-------|------|------|
| Acknowledge PagerDuty alert       | I     | I    | I     | R    | A    |
| Confirm primary unreachable       | A     | R    | I     | C    | C    |
| Identify scenario type            | R     | C    | I     | C    | C    |
| Pause Patroni cluster (if needed) | R     | A    | I     | —    | —    |
| Execute `patronictl failover`     | R     | A    | C     | —    | —    |
| Reload HAProxy                    | A     | R    | —     | C    | —    |
| Pause / Resume PgBouncer          | A     | R    | —     | —    | C    |
| Run smoke-test queries            | C     | —    | —     | R    | A    |
| Confirm replication re-established| R     | C    | —     | A    | —    |
| Resolve PagerDuty + open postmortem | I   | I    | R     | A    | C    |
| Demote / rebuild old primary      | R     | C    | A     | —    | —    |

### Exception Table Structure

| Scenario         | Failure Mode                     | Detection Signal              | Mitigation                         |
|------------------|----------------------------------|-------------------------------|-------------------------------------|
| Primary crash    | etcd quorum lost                 | Patroni logs: "no DCS quorum" | Manual promotion (see §EX-1)        |
| Primary crash    | Replica has replication lag >1GB | `patronictl list` lag column  | Choose lag-leader; accept data loss window |
| Network partition| Split-brain — both nodes primary | Two `/primary` endpoints respond | Fence old primary via `kubectl delete pod` |
| Network partition| HAProxy still routing to old primary | HAProxy stats show old backend UP | Force backend down via socket cmd |
| Planned failover | PgBouncer holds open transactions | `SHOW POOLS` — cl_active > 0 | Wait for drain or force disconnect  |
| Planned failover | Patroni switchover times out     | `patronictl switchover` exits non-zero | Retry with `--force`; escalate to Carol |

> **[Companion]** RACI and exception table skeleton complete. Execution agent will now draft the
> full numbered runbook with real commands, filling in every cell.

---

## Phase 3 — Implementation (Full Runbook Draft)

**Agent:** execution_agent

---

# PostgreSQL Failover Runbook v1.0
**Effective:** 2026-06-27 | **RTO:** <5 min (crash), <10 min (partition) | **Owner:** Carol (SRE Lead)

---

## Scenario A — Unplanned Primary Crash

**Trigger:** PagerDuty alert `postgres-primary-down`; Patroni `/primary` returns 503 >30 s.

### Pre-conditions
- etcd cluster has quorum (≥ 2/3 nodes healthy).
- At least one replica is running with lag < 100 MB.

### Steps

**A1. Acknowledge and assess (Dave/Eve — target: 60 s)**
```bash
# Confirm primary is down
patronictl -c /etc/patroni/patroni.yml list

# Expected: primary row shows "stopped" or absent
# Check etcd health
etcdctl --endpoints=http://etcd-0.etcd-headless:2379 endpoint health
```

**A2. Confirm no etcd quorum issue (Alice/Bob — target: 30 s)**
```bash
etcdctl --endpoints=\
  http://etcd-0.etcd-headless:2379,\
  http://etcd-1.etcd-headless:2379,\
  http://etcd-2.etcd-headless:2379 \
  endpoint status --write-out=table
# Proceed only if ≥ 2 rows show "isLeader=true/false" without error.
# If quorum lost → jump to Exception EX-1.
```

**A3. Pause PgBouncer to prevent dirty writes during promotion (Bob — target: 30 s)**
```bash
psql -h pgbouncer-svc -p 6432 -U pgbouncer pgbouncer \
  -c "PAUSE 5000;"
# 5000 ms timeout — in-flight txns complete or are killed.
```

**A4. Trigger Patroni automatic failover confirmation (Alice — target: 60 s)**
```bash
# Patroni should have already elected a new leader.
# If not, force it:
patronictl -c /etc/patroni/patroni.yml failover pg-cluster \
  --master <old-primary-pod> \
  --candidate <replica-pod-with-lowest-lag> \
  --force
# Confirm new primary:
patronictl -c /etc/patroni/patroni.yml list
```

**A5. Reload HAProxy to pick up new primary (Bob — target: 30 s)**
```bash
# HAProxy health-checks /primary endpoint — reload triggers re-evaluation.
kubectl rollout restart deployment/haproxy -n postgres
# Or if HAProxy is outside K8s:
echo "reload" | socat stdio /var/run/haproxy/admin.sock
```

**A6. Resume PgBouncer (Bob — target: 15 s)**
```bash
psql -h pgbouncer-svc -p 6432 -U pgbouncer pgbouncer \
  -c "RESUME;"
```

**A7. Smoke test (Dave/Eve — target: 60 s)**
```bash
psql -h haproxy-svc -p 5432 -U app appdb \
  -c "SELECT now(), pg_is_in_recovery();"
# Expected: pg_is_in_recovery = false (i.e., this is the new primary)

psql -h haproxy-svc -p 5433 -U app appdb \
  -c "SELECT now(), pg_is_in_recovery();"
# Expected: pg_is_in_recovery = true (replica still serving reads)
```

**A8. Verify replication re-established (Alice — target: 90 s)**
```bash
patronictl -c /etc/patroni/patroni.yml list
# lag column for replica must show < 10MB within 90 s.
```

**A9. Rebuild old primary as replica (Alice — target: post-RTO)**
```bash
# After RTO window closes — old pod restarts and Patroni runs pg_rewind automatically.
kubectl delete pod <old-primary-pod> -n postgres
# Patroni init container will run: pg_rewind --target-pgdata=/data --source-server="..."
# Confirm in logs:
kubectl logs <old-primary-pod> -n postgres | grep "pg_rewind"
```

**A10. Close incident (Carol)**
```bash
# Resolve PagerDuty alert via API or UI.
# Open postmortem in Jira: project=SRE, type=Postmortem, link incident ID.
```

**Definition of Done:** New primary serving writes. Replica lag < 10 MB. App health checks green.
PagerDuty resolved. Postmortem ticket open.

**Rollback:** Not applicable for unplanned crash. If promotion caused data divergence, pg_rewind
the new primary back to the last common WAL position (requires Carol approval).

---

## Scenario B — Network Partition

**Trigger:** Primary pod is alive but unreachable by clients; replica visible. Patroni DCS lock
may still be held by old primary if partition is inside the cluster network.

**Additional risk:** Split-brain (two nodes both believe they are primary).

### Steps

**B1. Detect split-brain (Dave/Eve — target: 60 s)**
```bash
# Query Patroni REST API on each pod directly:
for pod in $(kubectl get pods -n postgres -l app=patroni -o name); do
  echo "=== $pod ===" 
  kubectl exec $pod -n postgres -- \
    curl -s http://localhost:8008/patroni | python3 -m json.tool | grep '"role"'
done
# If two pods return "role": "master" → split-brain. Proceed to B2-fence.
# If one master, one replica → no split-brain; skip to B4.
```

**B2. Fence old/isolated primary (Alice — CONFIRM BEFORE RUNNING)**
```bash
# Delete the pod that clients CANNOT reach (confirm pod name from B1 output).
kubectl delete pod <isolated-primary-pod> -n postgres --grace-period=0 --force
# This terminates postgres, releasing the DCS lock within ttl window (30 s).
```

**B3. Wait for Patroni to elect new leader (Alice — target: 45 s)**
```bash
watch -n 2 'patronictl -c /etc/patroni/patroni.yml list'
# Wait until one node shows "Leader" role without asterisk conflict.
```

**B4–B8.** Execute steps A3 through A8 (PgBouncer pause → HAProxy reload →
PgBouncer resume → smoke test → replication check).

**Definition of Done:** Single primary confirmed in `patronictl list`. No dual-master state.

---

## Scenario C — Planned Maintenance Failover

**Trigger:** Scheduled — node drain, rolling upgrade, or kernel patch.

### Steps

**C1. Pre-announce (Carol — 30 min before)**
```bash
# Post to #incidents Slack: "Planned failover 14:00 UTC. Expected disruption < 60 s."
```

**C2. Drain application connections (Bob — target: 5 min before)**
```bash
psql -h pgbouncer-svc -p 6432 -U pgbouncer pgbouncer \
  -c "SHOW POOLS;"
# Wait until cl_active drops to 0, or set max_client_conn=0 to block new connections.
```

**C3. Initiate Patroni switchover (Alice — target: T+0)**
```bash
patronictl -c /etc/patroni/patroni.yml switchover pg-cluster \
  --master <current-primary-pod> \
  --candidate <target-replica-pod> \
  --scheduled now
# Patroni will: checkpoint → promote replica → demote primary.
# Observe output for "switched over" confirmation.
```

**C4. Confirm switchover (Dave/Eve — target: T+60 s)**
```bash
patronictl -c /etc/patroni/patroni.yml list
# New leader confirmed.
psql -h haproxy-svc -p 5432 -U app appdb -c "SELECT pg_is_in_recovery();"
```

**C5. Drain and patch old primary node (Bob)**
```bash
kubectl cordon <old-primary-node>
kubectl drain <old-primary-node> --ignore-daemonsets --delete-emptydir-data
# Apply patch, reboot, uncordon.
kubectl uncordon <old-primary-node>
```

**C6. Rejoin old primary as replica** — Patroni handles automatically on pod restart.

**C7. Resume PgBouncer and validate** — steps A6–A8.

**Definition of Done:** Switchover complete. Old node patched and rejoined as replica.
No unplanned disruption. Lag < 10 MB.

---

## Exception Procedures

### EX-1: etcd Quorum Lost
```bash
# DO NOT run patronictl failover — DCS is unavailable.
# 1. Restore etcd quorum first:
etcdctl --endpoints=http://etcd-0.etcd-headless:2379 member list
# Identify failed member. Remove and re-add:
etcdctl member remove <member-id>
etcdctl member add etcd-2 --peer-urls=http://etcd-2.etcd-headless:2380
# 2. Once quorum restored, Patroni auto-resumes within loop_wait (10 s).
# 3. If primary is still down, proceed with Scenario A from step A4.
```

### EX-2: pg_rewind Fails on Old Primary Rejoining
```bash
# Check Patroni init logs:
kubectl logs <old-primary-pod> -n postgres -c patroni-init
# If timeline divergence > wal_keep_size:
patronictl -c /etc/patroni/patroni.yml reinit pg-cluster <old-primary-pod> --force
# This triggers a full base backup from new primary — takes longer but is safe.
```

---

## RACI Matrix (Final)

| Step                                   | Alice | Bob   | Carol | Dave  | Eve   |
|----------------------------------------|-------|-------|-------|-------|-------|
| Acknowledge PagerDuty                  | I     | I     | I     | **R** | **A** |
| Confirm primary unreachable + etcd OK  | **A** | **R** | I     | C     | C     |
| Identify scenario (A/B/C)              | **R** | C     | I     | C     | C     |
| Pause PgBouncer                        | **A** | **R** | —     | —     | C     |
| Fence isolated primary (B2, if needed) | **R** | **A** | C     | —     | —     |
| Execute patronictl failover/switchover | **R** | **A** | C     | —     | —     |
| Reload HAProxy                         | **A** | **R** | —     | C     | —     |
| Resume PgBouncer                       | **A** | **R** | —     | —     | C     |
| Smoke-test queries                     | C     | —     | —     | **R** | **A** |
| Verify replication re-established      | **R** | C     | —     | **A** | —     |
| Resolve PagerDuty + open postmortem    | I     | I     | **R** | **A** | C     |
| Rebuild old primary as replica         | **R** | C     | **A** | —     | —     |
| Patch and uncordon node (planned)      | C     | **R** | **A** | —     | —     |

R = Responsible · A = Accountable · C = Consulted · I = Informed · — = Not involved

---

## Exception Table (Final)

| Scenario  | Failure Mode                        | Detection Signal                              | Mitigation                                        | Owner  |
|-----------|-------------------------------------|-----------------------------------------------|---------------------------------------------------|--------|
| Crash     | etcd quorum lost                    | `etcdctl endpoint health` shows ≥2 unhealthy  | Restore etcd quorum first (EX-1), then failover   | Alice  |
| Crash     | Replica lag > 1 GB at failover      | `patronictl list` lag column                  | Accept data loss; choose lag-leader; notify Carol | Alice  |
| Crash     | pg_rewind fails on rejoin           | Patroni init container exits non-zero         | `patronictl reinit --force` (EX-2)                | Alice  |
| Partition | Split-brain detected                | Two pods return `"role":"master"`             | Force-delete isolated pod (B2); confirm manually  | Alice  |
| Partition | HAProxy still routing to old primary| HAProxy stats: old backend weight > 0         | `set weight pg_primary/<old-server> 0` via socket | Bob    |
| Partition | DCS lock held by partitioned node   | Patroni loop_wait passes; no new leader       | Wait for ttl=30 s expiry, then re-check           | Alice  |
| Planned   | PgBouncer cl_active > 0 at switchover | `SHOW POOLS` output                         | Extend drain window; set `max_client_conn=0`      | Bob    |
| Planned   | `patronictl switchover` exits non-zero | Command output / exit code                  | Retry with `--force`; escalate to Carol if fails  | Alice  |
| Any       | HAProxy health-check misconfigured  | Both backends DOWN in stats                   | Manually set backend weights; page Carol          | Bob    |
| Any       | PgBouncer stuck in PAUSE            | `SHOW POOLS` cl_waiting keeps climbing        | `KILL <pool>` then `RESUME`                       | Bob    |

---

> **[Companion]** Full runbook drafted. Three scenarios (A/B/C), two exception procedures
> (EX-1, EX-2), completed RACI, completed exception table. Sending to reviewer_agent.

---

## Phase 4 — Review

**Agent:** reviewer_agent

Reviewed runbook v1.0. Findings:

**FINDING-1 (HIGH): Missing — PgBouncer reconnect delay after RESUME**
Step A6 resumes PgBouncer but does not verify that the new backend is accepting connections.
PgBouncer may silently queue connections if HAProxy hasn't finished reloading.
**Recommendation:** Add a `SHOW POOLS` check after RESUME confirming `cl_waiting = 0` within 10 s.

**FINDING-2 (MEDIUM): Ambiguous ownership — Step A9 (rebuild old primary)**
RACI shows Alice as R. But if Alice is still monitoring the new primary's lag (A8), a concurrent
rebuild may distract her. Consider assigning A9 to Bob with Alice as Accountable.

**FINDING-3 (MEDIUM): Missing — WAL archiving status check before Scenario B fence**
If `archive_mode = on`, fencing the isolated primary mid-WAL-archive can leave gaps.
**Recommendation:** Before B2, run:
```bash
kubectl exec <isolated-primary-pod> -n postgres -- \
  psql -U postgres -c "SELECT last_archived_wal, last_failed_wal FROM pg_stat_archiver;"
```
Confirm `last_failed_wal` is NULL before proceeding.

**FINDING-4 (LOW): Scenario C missing pre-switchover checkpoint**
`patronictl switchover` issues a CHECKPOINT, but a manual pre-checkpoint reduces switchover
duration. Add before C3:
```bash
kubectl exec <current-primary-pod> -n postgres -- \
  psql -U postgres -c "CHECKPOINT;"
```

**FINDING-5 (LOW): Exception table missing — PgBouncer auth_file stale after failover**
If the new primary has a different `pg_hba.conf` or password rotation occurred, PgBouncer
may fail to authenticate. Add row to exception table: detection = PgBouncer logs
`ERROR: Auth failed`, mitigation = reload PgBouncer config + re-test.

> **[Companion]** Five findings: 1 HIGH, 2 MEDIUM, 2 LOW. execution_agent should patch A6,
> add WAL archive check before B2, add pre-checkpoint to C3, and add exception row for
> PgBouncer auth. RACI amendment (FINDING-2) is Carol's decision.

---

## Phase 5 — Handoff

**Agent:** orchestrator

Runbook v1.0 is complete pending reviewer patches. Summary for handoff:

**Deliverables produced:**
- Runbook SOP: 3 scenarios (A: crash, B: partition, C: planned), numbered steps with exact CLI commands
- RACI matrix: 13 steps × 5 roles, fully populated
- Exception table: 10 rows covering etcd loss, split-brain, pg_rewind failure, PgBouncer stall, HAProxy misconfiguration

**Open actions before v1.1 publish:**

| ID          | Action                                             | Owner | Due        |
|-------------|----------------------------------------------------|-------|------------|
| ACT-1       | Add `SHOW POOLS` post-RESUME check (FINDING-1)     | Bob   | 2026-06-28 |
| ACT-2       | Add WAL archive status check before B2 (FINDING-3) | Alice | 2026-06-28 |
| ACT-3       | Add pre-CHECKPOINT to C3 (FINDING-4)               | Alice | 2026-06-28 |
| ACT-4       | Add PgBouncer auth exception row (FINDING-5)       | Bob   | 2026-06-28 |
| ACT-5       | Decide A9 RACI amendment (FINDING-2)               | Carol | 2026-06-30 |

**Links:**
- Patroni docs: https://patroni.readthedocs.io/en/latest/patronictl.html
- PgBouncer admin: https://www.pgbouncer.org/usage.html#admin-console
- HAProxy runtime API: https://www.haproxy.com/documentation/haproxy-runtime-api/
- etcd disaster recovery: https://etcd.io/docs/v3.5/op-guide/recovery/

**Next steps:**
1. Apply ACT-1 through ACT-4 patches → publish as runbook v1.1.
2. Schedule a tabletop drill with Dave and Eve against Scenario A in staging.
3. Wire PagerDuty runbook link to `postgres-primary-down` alert rule.
4. Set a 90-day review reminder — re-validate commands against next Patroni minor version.

> **[Companion]** Handoff complete. All phases closed. File this session under
> `cookbook/sre-runbook/session.md`. Tag: `ops_process`, `patroni`, `postgresql`, `runbook`.
