# Scaling Workers Runbook

---

## When to Scale

Scale agent workers when you observe:

- Job queue depth consistently > 10 (reviews waiting > 5 minutes)
- Worker CPU > 80% sustained
- Review completion time increasing week-over-week

Check in Grafana: `worker-dashboard.json` → "Queue Depth" and "Job Duration" panels.

---

## How Workers Scale

Each worker process handles one job at a time. To handle more concurrent reviews:

1. Increase `WORKER_CONCURRENCY` (more threads per process — for I/O-bound work)
2. Increase the number of worker replicas (more processes — for compute-bound work)

ARCHON workers are primarily I/O-bound (waiting on Claude API, Tavily, Exa, GitHub) — so `WORKER_CONCURRENCY` is the first lever.

---

## Scaling via Environment Variable

```bash
# Railway CLI
railway variables set WORKER_CONCURRENCY=8 --service worker
railway redeploy --service worker
```

Recommended values:
| Reviews/hour | WORKER_CONCURRENCY | Replicas |
|---|---|---|
| < 10 | 4 (default) | 1 |
| 10–50 | 8 | 1 |
| 50–200 | 8 | 2–4 |
| 200+ | 8 | 4+ |

---

## Scaling via Replicas (Railway)

```bash
# Via Railway dashboard: Workers service → Settings → Replicas
# Or via CLI (if supported):
railway scale --service worker --replicas 4
```

Each replica runs independently and consumes from the same Redis queue. No coordination needed.

---

## Cost Awareness

Each additional worker replica increases:
- Railway compute cost (~$10–20/month per replica)
- Claude API costs (more parallel agent runs = more tokens/minute)
- Rate limit pressure on Anthropic, Tavily, and Exa APIs

Before scaling, check if the bottleneck is queue depth (need more workers) or API rate limits (need back-pressure instead).

---

## Rate Limit Handling

If scaling workers causes Claude API rate limit errors:

```bash
# Reduce requests per minute per worker
railway variables set ANTHROPIC_REQUESTS_PER_MINUTE=30 --service worker
```

And implement review queuing at the API level (max N reviews per user simultaneously).

---

## Monitoring After Scaling

After scaling, watch for 30 minutes:

```bash
# Queue should drain
rq info --url $REDIS_URL

# Error rate should not increase
# → Grafana: worker-dashboard.json → "Job Failure Rate"

# Review completion time should decrease
# → Grafana: worker-dashboard.json → "Job Duration p95"
```
