# ARCHON — Claude Project Context

**"Your Frontier AI Architect. From idea to infrastructure."**

This file is auto-loaded by Claude Code in every session inside this project.
Always read this first. For detailed memory, see `.claude/memory/MEMORY.md`.

---

## What Is ARCHON?

ARCHON is a Frontier AI Architect SaaS that combines:
- **AWS Frontier Agent autonomy** — 6 specialist architects run in parallel for hours
- **Perplexity-style research** — live web search (Tavily + Exa) + RAG over codebase
- **Human-in-the-Loop** — 4 checkpoints, 3 modes (Autopilot / Balanced / Supervised)

Output: Complete Architecture Review Package (ADRs + IaC + Diagrams + Risk Register + Citations)

---

## Project Structure

```
Archon/
├── CLAUDE.md                  ← You are here
├── PRODUCT_PLAN.md            ← Full product plan + PRD
├── .claude/
│   └── memory/
│       ├── MEMORY.md          ← Memory index
│       ├── decisions.md       ← All architectural decisions (ADRs)
│       ├── build_phases.md    ← Phase tracking
│       ├── tech_stack.md      ← Tech choices + rationale
│       └── conventions.md     ← Coding conventions + standards
├── agents/                    ← 6 specialist architect agent definitions
├── engine/                    ← Strands runner + orchestrator
├── rag/                       ← Codebase indexer + retriever (pgvector)
├── research/                  ← Tavily + Exa web search pipeline
├── tools/                     ← Shared agent tools
├── output/                    ← Findings formatter + package builder
├── api/                       ← FastAPI backend
├── web/                       ← Next.js 15 frontend
└── main.py                    ← CLI entry point (Phase 1)
```

---

## The 6 Agents

| Agent | File | Domain |
|---|---|---|
| `software-architect` | `agents/software_architect.py` | Patterns, NFRs, ADRs, tech debt |
| `cloud-architect` | `agents/cloud_architect.py` | AWS/GCP/Azure, IaC, FinOps |
| `security-architect` | `agents/security_architect.py` | Zero-trust, IAM, compliance |
| `data-architect` | `agents/data_architect.py` | Data strategy, governance, mesh |
| `integration-architect` | `agents/integration_architect.py` | EDA, microservices, API gateway |
| `ai-architect` | `agents/ai_architect.py` | ML/AI systems, RAG, agentic |
| `team-architecture` | `engine/supervisor.py` | Orchestrates all 6, merges output |

---

## Tech Stack (Quick Reference)

| Layer | Technology |
|---|---|
| Agent runtime | Strands Agents SDK (Python) |
| LLM | Claude API — `claude-opus-4-5` |
| Web research | Tavily API + Exa API |
| RAG / vector | pgvector (PostgreSQL) |
| Backend | FastAPI + Redis + BullMQ |
| Frontend | Next.js 15 + Tailwind + shadcn/ui |
| Auth | Clerk |
| Database | PostgreSQL + SQLAlchemy 2 async |
| Billing | Stripe |
| Deploy | Docker + Railway |

---

## Build Phase Status

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Agent engine CLI — 6 agents + RAG + web search → markdown | Not started |
| Phase 1 | Full agent engine — HITL, checkpoints, session persistence | Pending |
| Phase 2 | SaaS shell — FastAPI + Next.js + Clerk + Stripe | Pending |
| Phase 3 | Research quality — citations UI, confidence scores, diagrams | Pending |
| Phase 4 | VS Code extension + CLI distribution | Future |

**Current:** Phase 1

---

## Phase 1 Goal

Prove core hypothesis: 6 agents + RAG + web research → useful architecture findings.

```bash
python main.py --repo https://github.com/user/repo --mode review
python main.py --brief "SaaS video platform, 10k users, $2k/month budget" --mode design
# Runs all 6 agents autonomously
# Outputs: archon-review.md
```

No UI. No billing. No HITL. Agent engine only. Modes: review + design.

## The 14 ARCHON Modes

| # | Mode | Phase | Trigger |
|---|---|---|---|
| 1 | Review | Phase 1 | Audit existing codebase |
| 2 | Design | Phase 1 | New product from scratch |
| 3 | Migration Planner | Phase 2 | Modernisation project |
| 4 | Compliance Auditor | Phase 2 | SOC2/HIPAA/GDPR audit |
| 5 | Due Diligence Responder | Phase 2 | Fundraise / M&A |
| 6 | Incident Responder | Phase 2 | P0/P1 outage |
| 7 | Cost Optimiser | Phase 3 | Cloud bill spike |
| 8 | PR Reviewer | Phase 3 | Pull request opened |
| 9 | Scaling Advisor | Phase 3 | Traffic growing |
| 10 | Drift Monitor | Phase 3 | Weekly architecture check |
| 11 | Feature Feasibility | Phase 4 | "Can we build X?" |
| 12 | Vendor Evaluator | Phase 4 | Database / cloud choice |
| 13 | Onboarding Accelerator | Phase 4 | New CTO / senior hire |
| 14 | Sunset Planner | Phase 4 | Decommission a service |

---

## Key Conventions

- **Language:** Python 3.11+ for all agent/backend code
- **Agent definitions:** Each agent is a Python class wrapping a Strands Agent with domain-specific system prompt + tools
- **Tool naming:** snake_case everywhere
- **Output format:** All agent outputs are structured Pydantic models before being rendered to markdown
- **Citations:** Every web-sourced finding MUST include source URL + title + excerpt
- **Secrets:** Never hardcode API keys — always use `.env` + `python-dotenv`
- **Tests:** pytest — unit tests for tools, integration tests for agents (use small test repos)

---

## Environment Variables Required

```
ANTHROPIC_API_KEY=
TAVILY_API_KEY=
EXA_API_KEY=
GITHUB_TOKEN=
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
CLERK_SECRET_KEY=
STRIPE_SECRET_KEY=
```

---

## Important Decisions (see .claude/memory/decisions.md for full log)

1. **Strands Agents SDK** over LangChain/CrewAI — same tech AWS uses, MCP-native, Bedrock-optional
2. **pgvector** over Qdrant — simpler ops, already in Postgres, sufficient for MVP
3. **Tavily + Exa both** — Tavily for recency, Exa for semantic depth
4. **claude-opus-4-5** — best reasoning for architecture domain, cost justified by output quality
5. **CLI-first Phase 1** — proves agent engine before investing in UI
