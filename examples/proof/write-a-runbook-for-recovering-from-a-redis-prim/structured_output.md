# Redis Primary Failover Recovery Runbook

## Overview
**Process name**: Redis Primary Failover Recovery  
**Trigger**: Automated failover detected (replica promoted) OR manual failover initiated  
**Goal**: Restore Redis cluster to stable, redundant state with minimal data loss and downtime  
**SLA**: Acknowledge within 5 min | Failover completion within 15 min | Full recovery within 1 hour  
**Actors**: On-call DBA, Platform Engineer, Application Owner, Incident Commander

---

## Process Steps

| # | Step | Actor | Tool / System | Output |
|---|---|---|---|---|
| 1 | Receive failover alert (automated or manual trigger) | Monitoring system | PagerDuty, CloudWatch, Redis Sentinel | Alert ticket created; on-call DBA paged |
| 2 | Acknowledge alert and open war room | On-call DBA | Slack, war room link | Incident declared; team assembled in 2 min |
| 3 | Verify failover has occurred | On-call DBA | `redis-cli -h <new-primary> info replication` | Confirm new primary, check replica list, note primary ID and epoch |
| 4 | Check replica connectivity and lag | Platform Engineer | `redis-cli -h <replica-ip> info replication \| grep offset` | Document replica offsets; identify any lagging replicas |
| 5 | If old primary is still responsive: Issue SHUTDOWN on old primary | On-call DBA | SSH to old primary node; `redis-cli SHUTDOWN NOSAVE` | Old primary halts; prevents split-brain |
| 6 | Inspect new primary for correctness | Application Owner | `redis-cli -h <new-primary> DBSIZE`, `KEYS *` (sample) | Verify no unexpected data loss; check key count against baseline |
| 7 | Re-enable application traffic to new primary | Platform Engineer | Update app config / DNS / load balancer; deploy | Apps reconnect to new primary; monitor error rate |
| 8 | Restart old primary node | Platform Engineer | SSH to old primary; `sudo systemctl start redis` | Old primary boots; automatically joins as replica (Sentinel manages) |
| 9 | Confirm old primary joined as replica | On-call DBA | `redis-cli -h <old-primary-ip> info replication` | Old primary shows as replica; syncing or synced |
| 10 | Monitor replication lag and error rates for 5 min | Platform Engineer | CloudWatch, application logs | Lag <100ms; error rate <0.1% (baseline) |
| 11 | Document incident and root cause | Incident Commander | Runbook, incident ticket | Incident closed; post-mortem scheduled if needed |

---

## RACI Matrix

| Step | On-call DBA | Platform Engineer | Application Owner | Incident Commander |
|---|---|---|---|---|
| 1 — Receive alert | I | I | I | A |
| 2 — Acknowledge and assemble | R | C | C | A |
| 3 — Verify failover | **R** | — | — | I |
| 4 — Check replica lag | **R** | C | — | — |
| 5 — Shutdown old primary | **R** | C | — | — |
| 6 — Inspect new primary | C | — | **R** | I |
| 7 — Re-enable traffic | C | **R** | C | — |
| 8 — Restart old primary | C | **R** | — | — |
| 9 — Confirm replica join | **R** | C | — | I |
| 10 — Monitor recovery | C | **R** | C | — |
| 11 — Document incident | C | C | C | **A** |

Legend: **R** = Responsible | **A** = Accountable | **C** = Consulted | **I** = Informed | — = Not involved

---

## Exception Paths

| Condition | Detected at step | Recovery action | Owner |
|---|---|---|---|
| Old primary unresponsive / already halted | 5 | Skip step 5; proceed to step 6. Document in incident ticket that manual intervention prevented split-brain. | On-call DBA |
| New primary shows unexpected data loss (DBSIZE << baseline) | 6 | **STOP.** Do not re-enable traffic. Escalate to Database Team lead. Investigate: check replica offsets from step 4; determine if loss occurred pre-failover or during. May require restore from backup. | Application Owner + DBA |
| Replica reports very high lag (>1000ms) | 4 or 10 | Check network: `ping <replica-ip>`, verify no packet loss. If network OK: replica may be CPU-bound. Increase `slowlog get` output; identify expensive commands. If lag persists >5 min, reduce traffic to primary until lag clears (degrade gracefully). | Platform Engineer |
| Old primary fails to rejoin as replica after restart (step 8–9) | 9 | SSH to old primary; check Redis logs: `tail -f /var/log/redis/redis-server.log`. If Sentinel config is stale, manually configure replication: `redis-cli SLAVEOF <new-primary-ip> 6379`. Notify Sentinel that it should manage this; do not leave manual replication in place. | On-call DBA |
| Application receives connection errors after traffic re-enable | 7 | Verify app is using correct primary endpoint / DNS name. Check Redis `CLIENT LIST` on new primary to confirm connections arriving. If connections not arriving: rolling restart of app replicas. | Platform Engineer |
| Split-brain detected (two primaries with conflicting writes) | Any | **CRITICAL.** Kill one primary immediately (the one **not** owned by Sentinel). **Do not attempt reconciliation.** Notify Database Architect. Restore from backup if needed. | On-call DBA + Architect |

---

## Pre-Incident Checklist (Preparation)

Before any failover, ensure:
- [ ] Sentinel is running on ≥3 nodes and has quorum
- [ ] Replica is synced (replication offset matches primary)
- [ ] Network between primary and replica is stable (<1ms latency, <0.1% loss)
- [ ] Backup of Redis data is recent (< 1 hour old) and verified
- [ ] Application is configured to reconnect on primary failover
- [ ] On-call DBA and Platform Engineer have been trained on this runbook
- [ ] War room link and Slack channel are established and tested

---

## Success Criteria

Failover recovery is **complete** when:
- [ ] New primary is stable and accepting writes
- [ ] Old primary is running as a replica and fully synced (lag ≈ 0)
- [ ] All application instances reconnected to new primary
- [ ] Error rate returned to baseline (<0.1%)
- [ ] No split-brain condition present
- [ ] Incident is documented with timeline and root cause

---

## Key Commands Reference

```bash
# Check replication status
redis-cli -h <host> INFO REPLICATION

# View current primary and replicas
redis-cli -h <host> ROLE

# Force shutdown of old primary (blocks split-brain)
redis-cli -h <old-primary> SHUTDOWN NOSAVE

# Manually demote primary and trigger new election (Sentinel-managed)
redis-cli -h <sentinel-host> -p 26379 SENTINEL FAILOVER <master-name>

# Monitor real-time replication offset
redis-cli -h <host> INFO REPLICATION | grep offset

# Check Sentinel quorum and master discovery
redis-cli -h <sentinel-host> -p 26379 SENTINEL MASTERS

# Restart Redis service (after node recovery)
sudo systemctl restart redis-server
# Verify it came up as replica (should auto-rejoin if Sentinel is running)
redis-cli INFO REPLICATION
```

---

## Post-Incident Actions

1. **Within 1 hour**: Document what triggered the failover (network partition, primary node crash, manual failover test). Update runbook with any new findings.
2. **Within 1 day**: Schedule post-mortem if failover was unplanned. Review: Did Sentinel behave as expected? Any network issues? Application reconnection latency acceptable?
3. **Within 1 week**: Run a failover test in staging to verify this runbook is current and team is trained.

---

## Notes & Guardrails

- **Never manually intervene** in Sentinel-managed failover unless explicitly instructed. Sentinel
