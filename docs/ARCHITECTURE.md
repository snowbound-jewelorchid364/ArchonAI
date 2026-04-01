# ARCHON - Production Architecture

**Hexagonal / Ports and Adapters Architecture**

---

## System Overview

ARCHON is a three-process SaaS product:

| Process | Tech | Role |
|---|---|---|
| CLI | Python (main.py) | Local review runs, all 14 modes |
| API | FastAPI | REST API, auth, billing, job dispatch, SSE |
| Worker | Python + Redis | Background review execution |

All processes share one PostgreSQL (pgvector) and one Redis instance.

---

## Architecture Layers

Dependency rule: layers only depend inward. Domain has zero external deps.

| Layer | Location | Responsibility |
|---|---|---|
| Delivery | main.py, src/api/, web/ | CLI, REST API, Next.js frontend |
| Application | src/archon/engine/, rag/, output/ | Supervisor, Runner, HITL, RAG, Output |
| Domain | src/archon/core/models/, core/ports/ | Pydantic models + abstract interfaces |
| Infrastructure | src/archon/infrastructure/ | Claude, Tavily, Exa, pgvector, GitHub, Redis |

---

## Data Flow: Review Mode

1. User submits repo URL (CLI or API)
2. GitHubReader clones repo to /tmp/archon-<job-id>/
3. Chunker splits files, Embedder creates vectors, stored in VectorStore
4. Supervisor fans out 6 agents via asyncio.gather()
5. Each agent: query RAG, search web (Tavily+Exa), Claude (thinking), parse JSON, return AgentOutput
6. Supervisor: collect, deduplicate, cross-reference, executive summary
7. HITL checkpoints (if Balanced/Supervised mode)
8. PackageAssembler produces Markdown + ZIP
9. CLI writes to ./output/ | API stores in DB

---

## Agent Architecture

Each specialist agent extends BaseArchitectAgent with:
- domain (e.g. software, cloud, security)
- prompt_file (prompts/<agent>.md)
- search_queries (mode-specific web search queries)
- finding_prefix (e.g. SA- for software architect)

Run loop: RAG query > web search > build prompt > Claude call > parse JSON > AgentOutput

---

## Core Domain Models

| Model | File | Purpose |
|---|---|---|
| Finding | core/models/finding.py | Actionable finding with severity, citations, confidence |
| Artifact | core/models/artifact.py | ADR, IaC skeleton, or Mermaid diagram |
| AgentOutput | core/models/agent_output.py | Complete output from one agent |
| ReviewPackage | core/models/review_package.py | Merged output from all 6 agents |
| Job | core/models/job.py | Job state tracking |

---

## Port Interfaces

| Port | Implementations |
|---|---|
| LLMPort | ClaudeAdapter (claude-opus-4-6 with thinking budgets) |
| SearchPort | TavilyAdapter, ExaAdapter (both with retry + backoff) |
| VectorStorePort | InMemoryStore (dev), PgVectorStore (production) |
| RepoPort | GitHubReader (clone + validate + cleanup) |

---

## HITL (Human-in-the-Loop)

| Mode | Checkpoints Active | Use Case |
|---|---|---|
| Autopilot | 1 (scope) + 4 (final) | Trusted, repeat reviews |
| Balanced | All 4 (default) | Standard use |
| Supervised | All 4 + per-agent approval | High-stakes, regulated |

4 checkpoints: Scope Confirmation > Findings Review > Architecture Decisions > Final Review

---

## API Endpoints

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| /health | GET | None | Health check |
| /api/reviews | POST | Clerk JWT | Start a review |
| /api/reviews | GET | Clerk JWT | List user reviews |
| /api/reviews/{id} | GET | Clerk JWT | Get review details |
| /api/jobs/{id}/stream | GET | Clerk JWT | SSE agent progress |
| /api/packages/{id}/download | GET | Clerk JWT | Download ZIP |
| /api/billing/portal | POST | Clerk JWT | Stripe portal redirect |
| /api/billing/webhook | POST | Stripe sig | Payment events |
| /api/webhooks/github | POST | GitHub sig | PR review trigger |
| /api/share/{token} | GET | None | Public shared review |

---

## Database Schema

| Table | Key Columns |
|---|---|
| users | id, clerk_id, email, plan, stripe_customer_id |
| reviews | id, user_id, repo_url, mode, status, findings_json, package_path |
| packages | id, review_id, format, storage_path, share_token |

ORM: SQLAlchemy 2 async. Migrations: Alembic.

---

## Infrastructure

| Service | Local (docker-compose) | Production (Railway) |
|---|---|---|
| PostgreSQL + pgvector | localhost:5432 | Railway Postgres |
| Redis | localhost:6379 | Railway Redis |
| API | uvicorn :8000 | Railway service |
| Frontend | next dev :3000 | Railway static |
| Worker | python worker | Railway worker |

---

## Security

- All API routes require Clerk JWT except /health and /api/share/{token}
- Rate limiting: 100 req/min per user (Redis sliding window)
- Repo content never logged, only metadata
- Secrets via .env + pydantic-settings, never in code
- Temp dirs cleaned after every run
- CORS: allow-list frontend domain only