# Redis Primary Failover Recovery Runbook

**Domain:** ops_process  
**Severity:** High  
**Last Updated:** [DATE]  
**Owned By:** Platform/Database Team

---

## Table of Contents
1. [Overview](#overview)
2. [Detection & Alerting](#detection--alerting)
3. [Initial Assessment](#initial-assessment)
4. [Recovery Procedures](#recovery-procedures)
5. [Validation](#validation)
6. [Post-Incident](#post-incident)

---

## Overview

### What is a Primary Failover?

A Redis primary failover occurs when the primary (master) node becomes unavailable and a replica is automatically promoted to primary, or when a manual failover is triggered. This runbook covers recovery procedures for both scenarios.

### Key Objectives
- Restore cluster to healthy state with single primary
- Minimize data loss and service degradation
- Document root cause for post-incident analysis
- Restore replication topology

### Expected Impact
- **Availability:** Brief interruption (seconds to minutes)
- **Data Loss:** Potentially 0-N seconds of in-flight writes
- **Read/Write Performance:** Possible elevation during recovery

---

## Detection & Alerting

### Alert Indicators

| Signal | Threshold | Severity |
|--------|-----------|----------|
| Primary node down | Immediate | Critical |
| Replication lag | >5 seconds | High |
| Replica promotion event | Immediate | High |
| Failed sentinel quorum | >1 sentinel down | Medium |
| Memory exhaustion | >95% | High |

### Detection Methods

```bash
# Check primary status
redis-cli -h <primary-host> -p 6379 info replication

# Monitor sentinel
redis-cli -h <sentinel-host> -p 26379 sentinel masters

# Check cluster role
redis-cli -h <redis-host> -p 6379 role
```

### Alerting Verification
- [ ] Check PagerDuty/OpsGenie alert details
- [ ] Correlate with log aggregation (ELK/Splunk/DataDog)
- [ ] Verify alert timestamp matches incident occurrence

---

## Initial Assessment

### Step 1: Gather Situational Awareness (5 min)

**Action Items:**

```bash
# 1. Connect to Redis environment
export REDIS_PRIMARY=<primary-host>
export REDIS_SENTINEL=<sentinel-host>
export REDIS_PORT=6379
export SENTINEL_PORT=26379

# 2. Check current topology
redis-cli -h $REDIS_PRIMARY -p $REDIS_PORT INFO replication

# Output should show:
# role:master or role:slave

# 3. List all nodes
redis-cli -h $REDIS_SENTINEL -p $SENTINEL_PORT sentinel masters

# 4. Check sentinel state
redis-cli -h $REDIS_SENTINEL -p $SENTINEL_PORT sentinel slaves <master-name>

# 5. Review recent logs
tail -100 /var/log/redis/redis-server.log
tail -100 /var/log/redis/sentinel.log

# 6. Check connectivity to all nodes
for node in <node1> <node2> <node3>; do
  echo "Testing $node:"
  redis-cli -h $node -p $REDIS_PORT ping
done
```

**Document Findings:**
- [ ] Current primary node
- [ ] Current replica nodes (if any)
- [ ] Sentinel quorum status
- [ ] Network connectivity status
- [ ] Recent error messages

### Step 2: Identify Failover Trigger

Ask: **Why did failover occur?**

```bash
# Check for OOM (Out of Memory)
redis-cli -h $REDIS_PRIMARY -p $REDIS_PORT info memory | grep used_memory

# Check for hung process
ps aux | grep redis-server

# Check system resources
top -bn1 | head -20

# Check network issues
mtr -r -c 100 <primary-ip>

# Check log for crash
journalctl -u redis-server -n 50 --no-pager
```

**Possible Root Causes:**
- [ ] Hardware failure (CPU/disk/network)
- [ ] Out of memory condition
- [ ] Software crash (segfault, assertion)
- [ ] Network partition
- [ ] Manual intervention
- [ ] Sentinel misconfiguration

---

## Recovery Procedures

### Scenario A: Automatic Failover (Recommended Path)

**Conditions:** Replica was automatically promoted by Sentinel

#### Step 1: Verify New Primary

```bash
# Identify new primary
NEW_PRIMARY=$(redis-cli -h $REDIS_SENTINEL -p $SENTINEL_PORT \
  sentinel get-master-addr-by-name <master-name> | head -1)

echo "New primary is: $NEW_PRIMARY"

# Verify it's accepting writes
redis-cli -h $NEW_PRIMARY -p $REDIS_PORT ping
redis-cli -h $NEW_PRIMARY -p $REDIS_PORT info replication
```

**Expected Output:**
```
role:master
connected_slaves:N
```

#### Step 2: Investigate Former Primary

```bash
# For each affected host:
PRIMARY_HOST="<former-primary-ip>"

# Check if process is running
ssh $PRIMARY_HOST "systemctl status redis-server"

# Check logs for crash reasons
ssh $PRIMARY_HOST "journalctl -u redis-server -n 100 --no-pager"

# Check system health
ssh $PRIMARY_HOST "free -h && df -h / && top -bn1 | head -15"

# Verify disk space
ssh $PRIMARY_HOST "du -sh /var/lib/redis/*"
```

#### Step 3: Restart Former Primary as Replica

```bash
PRIMARY_HOST="<former-primary-ip>"
NEW_PRIMARY="<new-primary-host>"
REDIS_PORT=6379

# 1. SSH to former primary
ssh $PRIMARY_HOST

# 2. Stop Redis gracefully
sudo systemctl stop redis-server

# 3. Optionally backup current data (if investigating)
# sudo cp -r /var/lib/redis /var/lib/redis.backup.$(date +%s)

# 4. Clear old AOF if corrupted (DANGEROUS - only if instructed)
# sudo rm /var/lib/redis/appendonly.aof

# 5. Start Redis
sudo systemctl start redis-server

# 6. Wait for startup
sleep 5

# 7. Configure as replica
redis-cli -p $REDIS_PORT REPLICAOF $NEW_PRIMARY $REDIS_PORT

# 8. Verify
redis-cli -p $REDIS_PORT info replication
```

#### Step 4: Monitor Resynchronization

```bash
# Watch replication lag decrease
watch -n 2 "redis-cli -h $NEW_PRIMARY -p $REDIS_PORT info replication | \
  grep -E 'connected_slaves|slave.*offset|master_repl_offset'"

# Expected behavior:
# - slave_repl_offset gradually increases
# - Eventually matches master's master_repl_offset
# - slave_state changes to "online"

# For large datasets, this may take 5-30+ minutes
# Do NOT interrupt this process
```

**Success Criteria:**
```
connected_slaves:1
slave0:ip=<ip>,port=6379,state=online,offset=<offset>,lag=0
```

### Scenario B: Manual Failover Required

**Conditions:** Automatic failover failed or primary cannot be recovered

#### Step 1: Force Failover via Sentinel

```bash
# WARNING: Only if automatic failover failed to promote a replica

MASTER_NAME="<redis-master-name>"  # e.g., "mymaster"

# Get current master
redis-cli -h $REDIS_SENTINEL -p $SENTINEL_PORT \
  sentinel get-master-addr-by-name $MASTER_NAME

# Execute manual failover (controlled)
redis-cli -h $REDIS_SENTINEL -p $SENTINEL_PORT \
  sentinel failover $MASTER_NAME

# Monitor progress
watch -n 1 "redis-cli -h $REDIS_SENTINEL -p $SENTINEL_PORT \
  sentinel get-master-addr-by-name $MASTER_NAME"

# Wait for new master to be elected (typically 30 seconds)
```

#### Step 2: Update Application Configuration

```bash
# If using Sentinel-aware clients:
# - Most clients auto-discover new primary through Sentinel
