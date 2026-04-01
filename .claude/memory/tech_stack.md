---
name: ARCHON Tech Stack
description: Technology choices with rationale for ARCHON
type: project
---

# ARCHON - Tech Stack

## Core

| Layer | Technology | Version | Why |
|---|---|---|---|
| Agent runtime | Strands Agents SDK | latest (pin on use) | AWS open source, MCP-native, same stack as Frontier Agents |
| LLM | Claude API | claude-opus-4-6 | Best reasoning for architecture domain, thinking budgets |
| LLM (fast) | Claude API | claude-haiku-4-5-20251001 | Summaries, metadata, titles |
| Thinking budgets | Medium/High/Low | per-mode | Medium default, High for due diligence/compliance, Low for drift |
| Web research | Tavily API | latest | Recency-optimised, great for CVEs + docs |
| Web research | Exa API | latest | Semantic/neural search for patterns + papers |
| RAG / vector | pgvector | 0.7+ | In Postgres, no extra service, hybrid search |
| RAG / dev | InMemoryStore | built-in | No external deps for local dev |
| Embeddings | sentence-transformers | all-MiniLM-L6-v2 | Local, no API cost, lazy-loaded |

## Backend

| Layer | Technology | Why |
|---|---|---|
| API framework | FastAPI | Async, Python-native (matches agent stack), automatic OpenAPI |
| Job queue | Redis | Async agent runs, rate limiting, caching |
| Database | PostgreSQL 16 | pgvector support, reliable |
| ORM | SQLAlchemy 2.0 (async) | Pythonic, async-first |
| Migrations | Alembic | Schema versioning |
| Validation | Pydantic v2 | All agent outputs are Pydantic models |
| Auth SDK | Clerk (JWT/JWKS) | JWT verification for FastAPI middleware |
| Billing SDK | Stripe Python SDK | Subscriptions + webhooks |

## Frontend

| Layer | Technology | Why |
|---|---|---|
| Framework | Next.js 15 (App Router) | RSC, streaming, best DX |
| Styling | Tailwind CSS v4 | Utility-first, consistent |
| Components | shadcn/ui | Accessible, customisable, Radix-based |
| Data fetching | SSE (useSSE hook) | Real-time review progress streaming |
| Diagrams | Mermaid.js | Render agent-produced diagrams client-side |
| Auth | Clerk React SDK | Drop-in auth UI |

## Infrastructure

| Layer | Technology | Why |
|---|---|---|
| Containerisation | Docker + Docker Compose | Local dev parity with production |
| Hosting | Railway | Simple, git-push deploy, Postgres + Redis included |
| Secrets | .env + Railway env vars | Never in code |
| CI/CD | GitHub Actions | Automated testing + linting |

## Development

| Tool | Purpose |
|---|---|
| uv | Python package manager (fast) |
| pytest | Testing (pytest-asyncio for async) |
| ruff | Linting and formatting |
