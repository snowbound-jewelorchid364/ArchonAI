# Incident Response Runbook

---

## Severity Levels

| Level | Description | Response Time | Examples |
|---|---|---|---|
| SEV-1 | Complete service outage | < 15 min | API down, DB unreachable, all reviews failing |
| SEV-2 | Major feature broken | < 1 hour | Reviews not completing, checkpoints not firing |
| SEV-3 | Degraded performance | < 4 hours | Slow reviews, PDF export failing, SSE dropping |
| SEV-4 | Minor issue | Next business day | Edge case failures, UI glitches |

---

## Incident Response Steps

### Step 1 — Detect

Monitoring alerts via:
- Sentry: error rate spike or new exception type
- Prometheus/Grafana: API error rate > 5%, worker job failure rate > 10%
- Railway: service crash or OOM restart
- User report

### Step 2 — Triage

```bash
# Check all service health
curl https://api.archon.ai/health/ready

# Check Railway service status (Railway CLI)
railway status

# Check recent errors
# → Sentry dashboard: app.sentry.io/archon

# Check job queue
rq info --url $REDIS_URL
# Look for: queue depth, failed jobs, worker count
```

### Step 3 — Isolate

**API issues:**
```bash
# Check API logs (Railway)
railway logs --service api --tail 100

# Check DB connectivity
railway run --service api -- python -c "
from archon.db.session import engine
import asyncio
asyncio.run(engine.connect())
print('DB OK')
"
```

**Worker issues:**
```bash
# Check worker logs
railway logs --service worker --tail 100

# Check failed jobs
rq failed --url $REDIS_URL

# Inspect a failed job
rq job show <job-id> --url $REDIS_URL
```

**Agent run failures:**
```sql
-- Find recently failed analyses
SELECT id, status, error_message, created_at
FROM analyses
WHERE status = 'failed'
  AND created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;

-- Check which agents failed
SELECT agent_type, error_message, completed_at
FROM agent_runs
WHERE analysis_id = '<analysis-id>';
```

### Step 4 — Mitigate

**Option A: Restart service (Railway)**
```bash
railway redeploy --service api
railway redeploy --service worker
```

**Option B: Scale workers**
```bash
# Increase worker replicas in Railway dashboard
# Or via CLI:
railway scale --service worker --replicas 4
```

**Option C: Clear stuck jobs**
```bash
# Move failed jobs back to queue for retry
rq requeue --all --url $REDIS_URL

# Or discard failed jobs if they're poisoned
rq empty failed --url $REDIS_URL
```

**Option D: Database connection pool exhaustion**
```bash
# Check active connections
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# Kill idle connections
psql $DATABASE_URL -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND query_start < NOW() - INTERVAL '5 minutes';
"
```

### Step 5 — Communicate

For SEV-1 or SEV-2 affecting users:
- Update status page (status.archon.ai)
- Email affected users if reviews are lost/delayed
- Post in #incidents Slack channel

### Step 6 — Resolve and Document

After incident is resolved:
1. Confirm all services healthy (`/health/ready` returning 200)
2. Confirm job queue draining normally
3. Write postmortem within 48 hours (use [postmortem template](#postmortem-template))

---

## Common Incidents

### All reviews stuck in "running" status

**Cause:** Worker process died mid-job; jobs are orphaned in DB but not in queue.

**Fix:**
```sql
-- Reset stuck analyses
UPDATE analyses
SET status = 'failed', error_message = 'Worker process died — please retry'
WHERE status = 'running'
  AND updated_at < NOW() - INTERVAL '2 hours';
```

Notify affected users to retry.

---

### Claude API rate limit errors

**Cause:** 6 parallel agents × multiple reviews = hitting Anthropic rate limits.

**Fix:**
```bash
# Reduce worker concurrency temporarily
# In Railway: set WORKER_CONCURRENCY=2 env var and redeploy
```

Long-term: request rate limit increase from Anthropic or implement exponential backoff.

---

### pgvector HNSW index corruption

**Cause:** Rare — usually due to OOM during index build.

**Fix:**
```sql
REINDEX INDEX idx_code_chunks_embedding;
```

---

## Postmortem Template

```markdown
# Incident Postmortem — [Date] — [Title]

## Summary
One paragraph describing what happened, impact, and resolution.

## Timeline
- HH:MM — Alert fired / incident detected
- HH:MM — On-call engineer engaged
- HH:MM — Root cause identified
- HH:MM — Mitigation applied
- HH:MM — Incident resolved

## Root Cause
Technical description of what caused the incident.

## Impact
- Users affected: N
- Reviews affected: N
- Duration: X hours Y minutes

## What Went Well
- ...

## What Went Poorly
- ...

## Action Items
| Action | Owner | Due |
|---|---|---|
| | | |
```
