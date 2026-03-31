# ADR-004: rq Over Celery for Job Queue

**Status:** Accepted
**Date:** 2026-03-31
**Deciders:** ARCHON founding team

---

## Context

ARCHON requires a durable job queue for agent analysis runs. The two main Python job queue options are Celery (the industry standard) and rq (Redis Queue — simpler, Redis-native).

---

## Decision

Use **rq** (Redis Queue) for MVP.

---

## Rationale

**Simplicity.** rq has a significantly smaller surface area than Celery. No broker configuration, no task serialisation config, no result backend setup. A working rq worker is 10 lines of Python. A working Celery setup is a configuration file, a separate result backend, and documentation for the broker URL format.

**Redis is already required.** ARCHON uses Redis for rate limiting and SSE fan-out. rq runs on the same Redis instance — no additional infrastructure.

**Sufficient for MVP scale.** rq handles thousands of jobs per second on a single Redis node. ARCHON's MVP target is 50 concurrent reviews. rq is not the bottleneck.

**Debugging is straightforward.** `rq info` and the rq dashboard show queue depth, job status, and worker count. Debugging a failed Celery task in production is significantly harder.

---

## Consequences

- Worker processes started with: `rq worker archon:analysis archon:ingest`
- Job timeout set to 900 seconds (15 minutes) — matches agent run hard limit
- Failed jobs retained for 7 days for debugging
- rq dashboard deployed as a separate lightweight service in production
- Job result TTL: 24 hours (results written to DB, not relied upon from Redis)

---

## Migration Seam

The job dispatch interface in `analysis_service.py` is abstracted behind `enqueue_analysis(analysis_id: UUID)`. Migrating to Celery or a cloud job queue (AWS SQS + Lambda) requires changes in one file.

---

## Alternatives Rejected

**Celery:** More powerful (periodic tasks, canvas workflows, chord/chain primitives). Rejected for MVP — the configuration overhead and debugging complexity are not justified by ARCHON's simple job structure (one job type, linear execution).

**AWS SQS + Lambda:** Eliminates worker management. Rejected: Lambda's 15-minute timeout is marginal for 60-minute agent runs. Revisit if moving to serverless architecture.

**BullMQ (Node.js):** Would require a Node.js worker process. ARCHON's agent code is Python — cross-language workers add unnecessary complexity.
