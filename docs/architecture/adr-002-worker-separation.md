# ADR-002: Separate Agent Worker Process via Job Queue

**Status:** Accepted
**Date:** 2026-03-31
**Deciders:** ARCHON founding team

---

## Context

ARCHON's core operation — running 6 AI architect agents in parallel — takes 3–60 minutes and consumes significant CPU and memory. We need to decide how this work is executed in relation to the HTTP API.

Options considered:
1. **In-process async** — API handles agent execution in async background tasks
2. **Separate worker process via job queue** — API enqueues jobs; dedicated worker process consumes and executes
3. **Serverless functions** — Each agent run as a cloud function

---

## Decision

**Separate worker process** consuming jobs from a Redis queue (rq). The API never imports or executes agent code.

---

## Rationale

**Agent runs are long and resource-intensive.** Running 6 Claude Opus agents in parallel for up to 60 minutes inside an HTTP server process will exhaust the API's thread pool, inflate memory, and cause timeouts on unrelated requests. HTTP servers are designed for short-lived request/response cycles.

**Independent scaling.** Agent work scales with the number of reviews queued, not with HTTP traffic. Workers can be scaled horizontally without touching the API tier.

**Fault isolation.** A crashed worker does not take down the API. A crashed API does not orphan in-flight agent runs. The job queue provides durable state — jobs survive process restarts.

**Restart safety.** During deployments, the API restarts in seconds. Workers drain gracefully — they finish their current job before stopping. Zero in-flight reviews are lost.

**Ownership boundary.** The worker owns writes to `agent_runs`, `checkpoints`, `outputs`, and `citations`. The API owns reads and the analysis lifecycle. This boundary prevents concurrent write conflicts and makes each process's responsibility clear.

---

## Consequences

- API and worker are separate Python packages with separate `pyproject.toml` files
- All inter-process communication goes through PostgreSQL (state) and Redis (jobs)
- The API cannot call agent code directly — ever
- Real-time progress uses SSE polling the database, not shared memory or message passing
- Worker metrics exposed on port 9000 for Prometheus scraping

---

## Alternatives Rejected

**In-process async (FastAPI BackgroundTasks):** Rejected. Background tasks in FastAPI share the process memory and are killed on API restart. Not suitable for 60-minute agent runs.

**Serverless functions:** Rejected for MVP. Serverless cold starts add latency, 15-minute Lambda limits are insufficient for long reviews, and debugging distributed agent runs across cloud functions is significantly harder. Revisit at scale.
