# ARCHON — Architecture Overview

This document is the entry point for understanding ARCHON's technical architecture. For production detail, see [ARCHITECTURE.md](../../ARCHITECTURE.md).

---

## System Summary

ARCHON is a four-process SaaS product built around a job queue architecture:

```
Browser → API (FastAPI) → Redis Queue → Agent Worker (Strands + Claude)
                                              ↓
                                        PostgreSQL + pgvector
                                              ↓
                                        PDF Exporter (Puppeteer)
```

---

## Process Responsibilities

| Process | Tech | Owns |
|---|---|---|
| `apps/web` | Next.js 15 | UI, routing, SSE polling, checkpoint interaction |
| `apps/api` | FastAPI | Auth, project/analysis CRUD, job dispatch, SSE fan-out |
| `workers/agent` | Python + Strands | Agent execution, RAG, web research, output generation |
| `services/pdf-exporter` | Node.js + Puppeteer | HTML → PDF rendering |

**Critical boundary:** The API never executes agent code. The worker never serves HTTP. All inter-process communication goes through PostgreSQL (state) and Redis (job queue).

---

## Architecture Decision Records

| ADR | Decision |
|---|---|
| [ADR-001](./adr-001-monorepo.md) | Monorepo with independent service boundaries |
| [ADR-002](./adr-002-worker-separation.md) | Separate agent worker process via job queue |
| [ADR-003](./adr-003-pgvector.md) | pgvector over dedicated vector database |
| [ADR-004](./adr-004-rq-queue.md) | rq over Celery for job queue |
| [ADR-005](./adr-005-sse.md) | Server-Sent Events over WebSocket for progress streaming |

---

## Data Flow: Full Analysis Run

```
1. User clicks "Run Review"
   → POST /api/v1/projects/:id/analyses
   → API creates analysis row (status=queued)
   → API enqueues rq job (analysis_id)
   → API returns 202 Accepted

2. Browser opens SSE stream
   → GET /api/v1/analyses/:id/events
   → Polls DB for agent_run updates
   → Streams AgentProgressEvent to browser

3. Worker picks up job
   → Reads analysis row from DB
   → Clones + indexes repo → pgvector (ingest phase)
   → Fans out 6 agents via asyncio.gather()

4. Each agent (in parallel):
   → Hybrid search over code_chunks (RAG)
   → Web search via Tavily + Exa
   → Runs Strands agent loop (think → search → reason → produce)
   → Writes findings to agent_runs row
   → Inserts citations into citations table

5. At checkpoint (if Balanced/Supervised mode):
   → Worker inserts checkpoint row (status=pending)
   → Worker updates analysis status=awaiting_checkpoint
   → SSE event fires: checkpoint_ready
   → Browser shows checkpoint modal
   → User approves/edits/rejects
   → PATCH /checkpoints/:id/approve
   → Worker resumes

6. Supervisor merges all 6 outputs
   → Deduplicates findings
   → Builds ADRs, Terraform, diagrams, risk register
   → Inserts into outputs table
   → Updates analysis status=completed

7. SSE fires: analysis_complete
   → Browser shows results view
   → User exports PDF
```

---

## Key Technology Choices

- **Strands Agents SDK** — AWS open-source agent framework, same stack as AWS Frontier Agents. MCP-native, built-in tools (tavily_search, exa_search, file_read, think, diagram).
- **claude-opus-4-6** — Best reasoning quality for architecture domain. Cost offset by output depth.
- **pgvector** — Keeps all state in one system. HNSW index + BM25 hybrid search sufficient at MVP scale.
- **rq** — Simpler than Celery, Redis-native, sufficient for initial scale target (50 concurrent reviews).
- **SSE** — Unidirectional progress streaming. No WebSocket complexity required.

---

## Non-Functional Requirements

| NFR | Target |
|---|---|
| Review start time | < 30s from trigger to first agent executing |
| Checkpoint notification | < 60s from agent pause to user notification |
| Dashboard page load | < 1.5s at p95 |
| Review runtime | < 60 min median |
| API uptime | 99.5% |
| Concurrent reviews | 50 (MVP) |
| Max repo size | 500k LOC |
| Tenant isolation | Complete — no cross-tenant RAG possible |
