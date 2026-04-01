# ARCHON — Product Plan

**"Your Frontier AI Architect. From idea to infrastructure."**

---

## What Is ARCHON?

ARCHON is an autonomous SaaS co-pilot that runs 6 specialist AI architect agents in parallel — researching your codebase and the live web — to deliver a complete, cited Architecture Review Package in under an hour, with human checkpoints at every critical decision.

**Anyone with a product idea — engineer or not — can get a complete architecture.** Submit a voice note, a sketch, a Figma file, a PDF, or just describe your idea in plain English. ARCHON asks the right questions and produces a full architecture design.

**Name origin:** Greek ἄρχων — ruler, chief magistrate, commander.

---

## The Problem

Architecture reviews are expensive, slow, and inconsistent.

- Hiring a principal architect costs $200–350k/year
- External consultants charge $5–15k per engagement, take 2–4 weeks
- DIY reviews miss security, cost, and compliance angles
- Asking Claude/GPT directly gives generic, ungrounded, outdated answers
- Most startups skip reviews entirely and pay for it later (costly rewrites, outages, compliance failures)
- Non-engineers (founders, PMs) have no way to validate their product architecture before hiring engineers

**Average architectural mistake costs $50–500k to fix post-production.**

---

## Product Vision

ARCHON = AWS Frontier Agent Autonomy + Perplexity Research Intelligence + Human-in-the-Loop Control

```
AWS Frontier Agents    →  Autonomous execution, specialist agents, long-running tasks
Perplexity             →  Real-time web research, RAG synthesis, cited answers
Human-in-the-Loop      →  Checkpoints, redirect, approve, veto — human stays in control
```

---

## Intelligence Stack (4 Layers)

### Layer 1 — Frontier Agent Layer (AWS Pattern)
- Autonomous execution — runs for hours without intervention
- Supervisor + specialist agent pattern
- Session persistence — survives restarts
- Full tool access: file, shell, code, MCP, HTTP
- Governance + guardrails

### Layer 2 — Research Layer (Perplexity Pattern)
- Parallel web search per agent (Tavily + Exa)
- Deep content extraction from top sources
- Re-ranking by relevance + recency
- Citation tracking end-to-end
- Always up-to-date — no knowledge cutoff

### Layer 3 — RAG Layer (Private Knowledge)
- Codebase indexed per project (pgvector)
- Past ADRs + decisions searchable
- Internal docs + runbooks
- Hybrid search: semantic + keyword
- Re-indexed on every new review

### Layer 4 — Multimodal Input Layer (New)
- Voice → OpenAI Whisper transcription
- Images → Claude Vision API (sketches, whiteboards, AWS Console, diagrams)
- PDFs → pymupdf (business plans, PRDs, compliance reports, data rooms)
- Figma URLs → Figma REST API (screens + user flows)
- Website URLs → scraper ("build something like X")
- IaC files → python-hcl2 (Terraform, CloudFormation)
- Database schemas → sqlparse (SQL dumps, ERDs)
- OpenAPI specs → pyyaml
- All inputs normalised to unified context before agents run

---

## The 6 Specialist Architect Agents

| Agent | Domain |
|---|---|
| `software-architect` | App patterns (hexagonal/clean/DDD), NFRs, ADRs, tech debt |
| `cloud-architect` | AWS/GCP/Azure, IaC, FinOps, networking, DR |
| `security-architect` | Zero-trust, IAM, compliance (SOC2/HIPAA/GDPR) |
| `data-architect` | Data strategy, governance, data mesh, MDM |
| `integration-architect` | EDA, microservices, API gateway, service mesh |
| `ai-architect` | ML/AI systems, RAG pipelines, agentic architectures |
| `team-architecture` | **Supervisor** — orchestrates all 6, merges outputs |

---

## The 14 ARCHON Modes

ARCHON is not a single-purpose tool — it covers every stage of the product architecture lifecycle.

### Lifecycle Modes
| Mode | Trigger | Lead Agent |
|---|---|---|
| **Design** | Starting a new product from scratch | All 6 (prescriptive) |
| **Review** | Audit an existing codebase | All 6 (diagnostic) |
| **Migration Planner** | Monolith → services, on-prem → cloud | integration + cloud |
| **Scaling Advisor** | Traffic growing, bottlenecks detected | data + cloud |
| **Sunset Planner** | Decommissioning a service or feature | integration + data |

### Event-Triggered Modes (High Urgency)
| Mode | Trigger | Lead Agent |
|---|---|---|
| **Incident Responder** | P0/P1 outage in progress or post-mortem | software + cloud |
| **Compliance Auditor** | SOC2 / HIPAA / GDPR audit deadline | security |
| **Due Diligence Responder** | Fundraise / M&A / investor TDD | All 6 (external audience) |
| **Cost Optimiser** | Cloud bill spike / CFO pressure | cloud + data |

### Continuous / Embedded Modes
| Mode | Trigger | Frequency |
|---|---|---|
| **PR Reviewer** | Pull request opened | Per-PR (< 2 min) |
| **Drift Monitor** | Architecture diverging from design | Weekly scheduled |

### Decision Support Modes
| Mode | Trigger | Lead Agent |
|---|---|---|
| **Feature Feasibility** | PM asks "can we build X?" | software + data |
| **Vendor Evaluator** | Choosing between databases, cloud providers, SaaS tools | cloud + integration |
| **Onboarding Accelerator** | New CTO / senior engineer joins | All 6 (explanatory) |

---

## How a Review Works (Review Mode)

```
User submits goal / connects repo
        ↓
CHECKPOINT 1 — Scope Confirmation        ← Human approves
        ↓
AUTONOMOUS PHASE 1 — Research
  6 agents in parallel:
  • RAG over codebase
  • Web search (Tavily + Exa)
  • Deep content extraction
  (15–30 min)
        ↓
CHECKPOINT 2 — Findings Review           ← Human reviews / redirects
        ↓
AUTONOMOUS PHASE 2 — Deep Analysis
  • Multi-step reasoning (think tool)
  • Generate alternatives + trade-offs
  • Produce domain artifacts
  (20–45 min)
        ↓
CHECKPOINT 3 — Architecture Decisions    ← Human chooses direction
        ↓
AUTONOMOUS PHASE 3 — Artifact Production
  • ADRs, IaC, diagrams, risk register
        ↓
CHECKPOINT 4 — Final Review              ← Human approves
        ↓
Architecture Review Package Delivered
```

---

## HITL Modes

| Mode | Checkpoints | Best For |
|---|---|---|
| **Autopilot** | 1 + 4 only | Trusted workflows, repeat reviews |
| **Balanced** | All 4 (default) | Standard use |
| **Supervised** | Agent-level approvals | High-stakes, regulated industries |

---

## Output Package Per Review

```
Architecture Review Package
├── Executive Summary (1 page)
├── Per-Domain Reports (6 agents, cited findings)
│   ├── software-architect.md
│   ├── cloud-architect.md
│   ├── security-architect.md
│   ├── data-architect.md
│   ├── integration-architect.md
│   └── ai-architect.md
├── ADRs/                    ← one per key decision
├── terraform/               ← IaC skeleton
├── diagrams/                ← Mermaid C4 + AWS diagrams
├── risk-register.md         ← prioritised by severity
└── citations.md             ← all web sources used
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent runtime | Strands Agents SDK (Python, open source) |
| LLM | Claude API (claude-opus-4-6, medium thinking budget) |
| LLM (fast) | Claude API (claude-haiku-4-5-20251001, summaries/metadata) |
| Thinking budgets | Medium (default), High (due diligence/compliance), Low (drift monitor) |
| Web research | Tavily Search API + Exa Search API (both, with retry) |
| RAG / vector store | pgvector (prod) + InMemoryStore (dev) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Backend | FastAPI + Redis + SQLAlchemy 2 async |
| Frontend | Next.js 15 + Tailwind CSS + shadcn/ui |
| Auth | Clerk (JWT/JWKS) |
| Database | PostgreSQL + Alembic migrations |
| Billing | Stripe |
| Diagrams | Mermaid C4 diagrams |
| Deploy | Docker + Railway |

---

## Pricing

Three tiers matching the three monetisation signals:

### Event-Based (High Urgency, One-Shot)
| Mode | Price | Target |
|---|---|---|
| Due Diligence Responder | $999/run | Pre-fundraise, M&A |
| Compliance Auditor | $499/run | SOC2/HIPAA prep |
| Incident Responder | $299/run | Post-mortem RCA |
| Migration Planner | $499/run | Modernisation projects |

### Subscription (Recurring)
| Plan | Price | Includes | Target |
|---|---|---|---|
| **Starter** | $49/month | 3 on-demand runs/month | Solo founders |
| **Pro** | $199/month | Unlimited runs + PR Reviewer | Growing teams |
| **Team** | $499/month | All modes + Drift Monitor + 5 seats | Scale-ups |

### Enterprise
Custom pricing — unlimited seats, SSO, private deployment, SLA, compliance packages.

---

## Build Phases

### Phase 1 — Agent Engine CLI ✅ COMPLETE
6 agents + RAG + web search producing architecture findings via CLI.

Modes: **Review** + **Design**. CLI only, no UI.

### Phase 2 — Full Agent Engine + High-Urgency Modes ✅ COMPLETE
- HITL checkpoints (4 checkpoints, 3 modes: Autopilot/Balanced/Supervised)
- Session persistence (Redis)
- Modes: **Migration Planner**, **Compliance Auditor**, **Due Diligence Responder**, **Incident Responder**
- Hard timeout + partial output fallback
- Full output package generation (Markdown + ZIP)

### Phase 3 — SaaS Shell + Continuous Modes ✅ COMPLETE
- FastAPI backend (Redis job queue, SSE streaming, SQLAlchemy 2 async)
- Next.js 15 frontend (dashboard, review progress, results viewer)
- Clerk JWT auth + Stripe billing + 3-tier pricing
- GitHub repo connector
- Modes: **Cost Optimiser**, **PR Reviewer** (webhook), **Scaling Advisor**, **Drift Monitor** (scheduled)

### Phase 4 — Research Quality + Decision Support Modes ✅ COMPLETE
- Citations consolidation + deduplication
- Confidence scoring system
- Mermaid diagram generator (C4 + flowchart)
- Shareable review links (public share tokens)
- ZIP package builder
- Modes: **Feature Feasibility**, **Vendor Evaluator**, **Onboarding Accelerator**, **Sunset Planner**

### Phase 5 — Distribution 🟡 IN PROGRESS
- VS Code extension + GitHub Marketplace (PR Reviewer)
- CLI distribution (pip install archon-cli)
- Team collaboration + multi-seat

### Phase 6 — Input Formats + Output Formats + Chat (Planned)
**Input formats — any format a founder or engineer naturally has:**
- Voice → OpenAI Whisper transcription
- Images → Claude Vision API (sketches, whiteboards, AWS Console, diagrams)
- PDF → pymupdf (business plans, PRDs, compliance reports, data rooms)
- Figma URL → Figma REST API (screens + user flows as context)
- Website URL → scraper ("build something like X")
- Terraform / IaC → python-hcl2 parser
- Database schema → sqlparse (SQL dumps)
- OpenAPI / Swagger → pyyaml parser
- ZIP / folder upload → stdlib zipfile
- Multimodal combiner → merge all inputs to unified context

**Output formats — all free / open source:**
- Shareable web link — `/share/{token}`, no login required
- Self-contained HTML — Mermaid CDN, filterable findings
- PDF export — WeasyPrint (open source)
- GitHub Issues — HIGH+ findings as tickets (free API)
- GitHub ADR commit — ADRs to `/docs/adr/` in user's repo
- Slack webhook digest — health score + findings (free)
- JSON / YAML export — pyyaml

**Chat foundation (required for all phases after this):**
- Architecture Chat — conversational Q&A grounded in findings + RAG + web search
- `/api/reviews/{id}/chat` endpoint
- Chat grounded in any input format provided

### Phase 7 — Idea Mode + Design (Planned)
Non-engineers can go from napkin idea to full architecture via conversation.
- **Idea Mode (Mode 15)** — natural language idea → architecture, no repo, no brief, no jargon
- **Conversational intake** — 5-6 plain product questions (users, features, budget, timeline, compliance)
- **Requirements translator** — maps product answers to technical constraints silently
- **Multi-option design** — 3 options: Lean / Scalable / Enterprise with cost, timeline, trade-offs, IaC
- **Plain English output** — findings rendered without jargon, every decision explained simply
- **Visual architecture map** — interactive color-coded SVG, click component → see findings
- **"What to build first" plan** — week-by-week prioritised build sequence

### Phase 8 — Intelligence (Planned)
- **Architecture Memory** — persistent knowledge graph per org, remembers all reviews + decisions
- **Architecture Health Score** — continuous 0–100 score across 6 domains, weekly digest, alert rules

### Phase 9 — MCP Connectors (Planned)
Strands SDK is MCP-native — connectors add live operational data to agent context.
- **ARCHON as MCP Server** — expose review, findings, chat, health score to Cursor / Claude Desktop
- **GitHub MCP** — PR history, commit patterns, code ownership
- **AWS MCP** — live CloudFormation, Cost Explorer, CloudWatch, Security Hub
- **Slack MCP** — HITL approvals direct in Slack
- **Datadog MCP** — APM traces, error rates, latency
- **Snyk MCP** — live CVEs in dependencies
- **Linear / Jira MCP** — findings → tickets workflow
- **Terraform Cloud MCP** — live IaC state, drift detection

---

## Success Metrics

**Primary:** Review completion rate > 75% within 30 days of launch

**Secondary:**
- Time to Checkpoint 1: < 10 minutes median
- Post-review rating: > 60% rated ≥ 4/5
- 30-day retention: > 35% run a second review

**North Star:** $10k MRR at 90 days

---

## Key Risks

| Risk | Mitigation |
|---|---|
| Strands SDK breaking changes | Pin version; abstract behind our own runner interface |
| Claude Opus cost $5–15/review | Cost model before launch; price reviews to cover COGS |
| Agent runs > 2 hours | Hard 2hr timeout; partial output always delivered |
| RAG quality on large repos | Test on 5 real repos; add 500k LOC limit |
| GitHub enterprise OAuth rejection | Support zip upload fallback |

---

## Competitive Positioning

| | AWS Frontier Agents | Perplexity | GitHub Copilot | ARCHON |
|---|---|---|---|---|
| Autonomous long-running | ✅ | ❌ | ❌ | ✅ |
| Real-time web research | ❌ | ✅ | ❌ | ✅ |
| RAG over private codebase | ✅ | ❌ | ✅ | ✅ |
| 6 specialist architects | ❌ (3) | ❌ | ❌ | ✅ |
| Cited recommendations | ❌ | ✅ | ❌ | ✅ |
| IaC + ADRs produced | ✅ | ❌ | ❌ | ✅ |
| Human-in-the-loop control | Limited | ❌ | ❌ | ✅ |
| AWS-independent | ❌ | ✅ | ✅ | ✅ |
| Architecture-specialised | Partial | ❌ | ❌ | ✅ |
| 14 specialised modes | ❌ | ❌ | ❌ | ✅ |
| PR-level architecture review | ❌ | ❌ | Partial | ✅ |
| Compliance audit packages | ❌ | ❌ | ❌ | ✅ |
| M&A / TDD package | ❌ | ❌ | ❌ | ✅ |
| Greenfield design mode | ❌ | ❌ | ❌ | ✅ |
| Multi-option architecture design | ❌ | ❌ | ❌ | ✅ |
| Shareable review link | ❌ | ✅ | ❌ | ✅ |
| Architecture Chat (RAG-grounded) | ❌ | Partial | ❌ | ✅ |
| Architecture Memory + History | ❌ | ❌ | ❌ | ✅ |
| MCP connector ecosystem | ❌ | ❌ | ❌ | ✅ |
| GitHub Issues / ADR commit | ❌ | ❌ | Partial | ✅ |
| Architecture Health Score | ❌ | ❌ | ❌ | ✅ |
