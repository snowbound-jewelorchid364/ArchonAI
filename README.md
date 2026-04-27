<div align="center">

# ARCHON

### Your Frontier AI Architect. From idea to infrastructure.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Claude Opus 4](https://img.shields.io/badge/Claude-Opus_4-CC785C?style=for-the-badge&logo=anthropic&logoColor=white)](https://anthropic.com)
[![Tests](https://img.shields.io/badge/Tests-531_passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](src/tests/)
[![Coverage](https://img.shields.io/badge/Coverage-89%25-brightgreen?style=for-the-badge)](src/tests/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**6 specialist AI architects. 15 modes. Parallel execution. Cited findings. One package.**

[Getting Started](#-getting-started) · [Features](#-features) · [Modes](#-the-15-modes) · [Architecture](#-architecture) · [Distribution](#-distribution) · [Pricing](#-pricing)

</div>

---

![ARCHON Demo](./assets/demo.svg)

---

## The Problem

Hiring a principal architect costs **$200–350k/year**. External consultants charge **$5–15k/engagement** and take weeks. Most startups skip architecture reviews entirely — and the average architectural mistake costs **$50–500k to fix** post-production.

## The Solution

ARCHON is an **autonomous AI architecture co-pilot** that delivers a complete, cited Architecture Review Package in under 60 minutes.

- **Frontier Agent Autonomy** — 6 specialist architects run in parallel for up to 60 minutes
- **Perplexity-Style Research** — live web search (Tavily + Exa) with every finding cited and scored
- **Codebase Intelligence** — RAG over your actual code, not generic advice
- **Human-in-the-Loop** — 4 checkpoints, 3 control modes (Autopilot / Balanced / Supervised)
- **15 Modes** — from architecture review to PR gating, cost optimisation, and incident response
- **MCP Server** — expose ARCHON as an MCP tool for Claude Desktop, VS Code, and custom agents

---

## Features

| Feature | Description |
|---|---|
| **6 Specialist Agents** | Software, Cloud, Security, Data, Integration, and AI architects |
| **Parallel Execution** | All 6 agents run simultaneously via `asyncio.gather()` |
| **15 Modes** | Review, Design, Migration, Compliance, PR Reviewer, Cost Optimiser, and 9 more |
| **Full Citations** | Every finding backed by code evidence or a live web source URL |
| **Confidence Scoring** | Per-finding and per-section confidence with methodology breakdown |
| **Mermaid Diagrams** | Auto-generated C4, data flow, integration, and deployment diagrams |
| **Architecture Memory** | Persistent decision history and architecture snapshot diffing |
| **Health Score** | 0–100 architecture health score with SVG dashboard |
| **MCP Server** | 5 MCP tools: review, findings, ask, health score, ADRs |
| **HITL Checkpoints** | Pause, review, and redirect agents at 4 decision points |
| **Export Formats** | Markdown, ZIP package, HTML, PDF, GitHub comment, Slack message |
| **Multi-Input** | GitHub URL, ZIP, PDF, Figma, website, IaC, OpenAPI spec, voice, image |
| **VS Code Extension** | Run reviews and browse findings directly from your editor |
| **GitHub App** | Auto-review PRs on open/sync — posts structured comment within 2 min |
| **CLI Package** | `pip install archon-cli` — login, review, stream, export |
| **Zero-Trust Security** | Clerk JWT auth, per-tenant isolation, secrets never logged |
| **Stripe Billing** | 3 subscription tiers + event-based pricing |

---

## The 6 Agents

```
+-------------------------------------------------------------+
|                       SUPERVISOR                             |
|              Fan-out → Deduplicate → Merge                   |
+----------+----------+----------+----------+----------+------+
| Software | Cloud    | Security | Data     | Integr.  | AI   |
| Architect| Architect| Architect| Architect| Architect| Arch |
|          |          |          |          |          |      |
| Patterns | AWS/GCP  | Zero     | Schema   | EDA      | RAG  |
| NFRs     | Azure    | Trust    | Govern.  | APIs     | ML   |
| Tech Debt| IaC      | IAM      | Pipelines| Service  | Agent|
| ADRs     | FinOps   | Comply   | PII      | Mesh     | Ops  |
+----------+----------+----------+----------+----------+------+
```

---

## The 15 Modes

<details>
<summary><strong>Click to expand all modes</strong></summary>

| # | Mode | Category | Description |
|---|---|---|---|
| 1 | **Review** | Lifecycle | Audit existing codebase — the core mode |
| 2 | **Design** | Lifecycle | New product architecture from a brief |
| 3 | **Migration Planner** | Lifecycle | Modernisation and platform migration |
| 4 | **Compliance Auditor** | High Urgency | SOC2 / HIPAA / GDPR / PCI-DSS audit |
| 5 | **Due Diligence** | High Urgency | Investor / M&A technical package |
| 6 | **Incident Responder** | High Urgency | P0/P1 outage architecture triage |
| 7 | **Cost Optimiser** | Continuous | Cloud spend reduction with savings matrix |
| 8 | **PR Reviewer** | Continuous | Architecture review on pull requests |
| 9 | **Scaling Advisor** | Continuous | Capacity and growth planning from APM data |
| 10 | **Drift Monitor** | Continuous | Weekly architecture health check |
| 11 | **Feature Feasibility** | Decision Support | Build / buy / defer verdict for a feature brief |
| 12 | **Vendor Evaluator** | Decision Support | Database / cloud / tool TCO + lock-in matrix |
| 13 | **Onboarding Accelerator** | Decision Support | Annotated system map + learning path for new hires |
| 14 | **Sunset Planner** | Decision Support | Service shutdown sequence + GDPR checklist |
| 15 | **Idea Mode** | Design | Natural language → complete architecture in minutes |

</details>

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Node.js 18+ (for frontend)
- API keys: Anthropic, Tavily, Exa

### 1. Clone and Install

```bash
git clone https://github.com/VenkataAnilKumar/ArchonAI.git
cd ArchonAI

# Install Python dependencies
pip install uv
uv pip install -e ".[dev]"

# Install frontend dependencies
cd web && npm install && cd ..
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys:
#   ANTHROPIC_API_KEY=sk-ant-...
#   TAVILY_API_KEY=tvly-...
#   EXA_API_KEY=exa-...
#   DATABASE_URL=postgresql://...
#   REDIS_URL=redis://...
```

### 3. Start Infrastructure

```bash
docker compose up -d   # PostgreSQL (pgvector) + Redis
```

### 4. Run Database Migrations

```bash
cd src/db && alembic upgrade head && cd ../..
```

### 5. Run

**CLI (quickest)**

```bash
# Review an existing codebase
python main.py --repo https://github.com/user/repo --mode review

# Design from a brief
python main.py --brief "SaaS video platform, 10k users, $2k/month budget" --mode design

# Check feature feasibility
python main.py --brief "Add multi-region failover in 6 weeks" --mode feature_feasibility

# With Human-in-the-Loop
python main.py --repo https://github.com/user/repo --mode review --hitl balanced

# See all 15 modes
python main.py --help
```

**Web App**

```bash
# Terminal 1: API
uvicorn src.api.main:app --reload --port 8000

# Terminal 2: Frontend
cd web && npm run dev

# Open http://localhost:3000
```

**CLI Package**

```bash
pip install archon-cli

archon login           # authenticate with your ARCHON account
archon review --repo https://github.com/user/repo
archon status          # check account + active reviews
```

---

## Distribution

ARCHON ships across four surfaces — all code-complete:

### VS Code Extension
Install from VS Code Marketplace (coming soon) or build locally:
```bash
cd vscode-extension && npm install && npm run compile
```
- `ARCHON: Configure API Key` — stores key in VS Code SecretStorage
- `ARCHON: Review Workspace` — trigger review on open project
- Findings sidebar, inline decorations, live SSE progress panel

### GitHub App
Install from GitHub Marketplace (coming soon). Once installed:
- Opens a PR → ARCHON posts a structured architecture review comment within 2 min
- Per-repo config via `.archon.yml` (branches, ignore patterns, file cap)
- Retry logic, partial-failure comments, rate limiting built in

### CLI Package (`archon-cli`)
```bash
pip install archon-cli    # coming soon on PyPI
```
Full command set: `login`, `logout`, `status`, `review`, `design`, `export`
Rich live SSE display — watch all 6 agents run in real time in your terminal.

### MCP Server
Expose ARCHON as an MCP server for Claude Desktop or any MCP-compatible client:
```json
{
  "mcpServers": {
    "archon": {
      "command": "python",
      "args": ["-m", "archon.mcp.server"],
      "env": { "ARCHON_API_KEY": "your-key" }
    }
  }
}
```
Available tools: `review_repo`, `get_findings`, `ask_architecture`, `get_health_score`, `get_adrs`

---

## Architecture

```
Archon/
├── main.py                     # CLI entry point (15 modes)
├── src/
│   ├── archon/                 # Core domain (hexagonal architecture)
│   │   ├── core/
│   │   │   ├── models/         # Pydantic domain models
│   │   │   └── ports/          # Abstract interfaces (ports)
│   │   ├── agents/             # 6 specialist agents + base class
│   │   ├── engine/             # Supervisor, Runner, HITL, 15 mode configs
│   │   ├── engine/modes/       # Per-mode focus, inputs, output sections
│   │   ├── rag/                # Chunker, Indexer, Retriever
│   │   ├── input/              # Multi-format parsers (PDF, APM, cost CSV, IaC)
│   │   ├── output/             # Formatters, ZIP builder, diagrams, share
│   │   ├── mcp/                # MCP server (5 tools)
│   │   ├── workers/            # Drift worker (cron-triggered)
│   │   └── infrastructure/     # Claude, Tavily, Exa, pgvector, GitHub, Redis
│   ├── api/                    # FastAPI (9 route groups, SSE streaming)
│   ├── db/                     # SQLAlchemy models + Alembic migrations
│   └── tests/                  # 513 pytest tests, 89% coverage
├── web/                        # Next.js 15 + Clerk + Stripe + shadcn/ui
├── vscode-extension/           # VS Code extension (TypeScript)
├── cli-package/                # archon-cli PyPI package
├── github-app/                 # GitHub App for PR auto-review
└── docs/                       # PRDs, ADRs, architecture, runbooks
```

### Clean Architecture (Hexagonal)

```
+--------------------------------------------------+
|  Delivery Layer                                  |
|  CLI · FastAPI · Next.js · VS Code · GitHub App  |
+--------------------------------------------------+
|  Application Layer                               |
|  Supervisor · Runner · HITL · RAG · Output       |
+--------------------------------------------------+
|  Domain Layer  (zero external dependencies)      |
|  core/models (Pydantic) · core/ports (ABCs)      |
+--------------------------------------------------+
|  Infrastructure Layer                            |
|  Claude · Tavily · Exa · pgvector · GitHub       |
+--------------------------------------------------+
         Dependency direction: inward only
```

---

## Output Package

Every ARCHON review produces a complete, downloadable package:

```
archon-review-myrepo-20260401/
├── README.md                # Executive summary + navigation guide
├── findings/                # One .md per agent domain (6 files)
├── adrs/                    # Architecture Decision Records
├── terraform/               # IaC skeletons with comments
├── diagrams/                # Mermaid .mmd files (C4, data flow, deployment)
├── risk-register.md         # All findings sorted by severity + confidence
└── citations.md             # All sources consolidated and deduplicated
```

---

## Testing

```bash
# Full suite
pytest src/tests/ cli-package/tests/ github-app/tests/ -q

# With coverage
pytest src/tests/ --cov=src --cov-report=term-missing

# Single suite
pytest src/tests/ -v --tb=short
```

**531 tests · 89% coverage · 0 warnings**

---

## Pricing

| Plan | Price | Reviews | Modes |
|---|---|---|---|
| **Starter** | $49/month | 3 on-demand | Core 6 modes |
| **Pro** | $199/month | Unlimited | All 15 modes + PR Reviewer |
| **Team** | $499/month | Unlimited | All modes + Drift Monitor + 5 seats |

**Event-based (one-shot):**

| Mode | Price |
|---|---|
| Due Diligence Responder | $999/run |
| Compliance Auditor | $499/run |
| Migration Planner | $499/run |
| Incident Responder | $299/run |

---

## Documentation

| Document | Description |
|---|---|
| [Product Plan](docs/PRODUCT_PLAN.md) | Full product vision, pricing, GTM |
| [Architecture](docs/ARCHITECTURE.md) | System design + hexagonal architecture |
| [PRDs](docs/prds/) | 15 mode PRDs with user stories + NFRs |
| [ADRs](docs/architecture/) | Architecture Decision Records |
| [Getting Started](docs/development/getting-started.md) | Developer setup guide |
| [Security Model](docs/security/security-model.md) | Data handling + tenant isolation |
| [Runbooks](docs/runbooks/) | DB migrations, incidents, scaling |

---

## Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Follow** the coding conventions in [`.claude/rules/python.md`](.claude/rules/python.md)
4. **Write tests** — maintain ≥ 89% coverage
5. **Run** `ruff check .` and `pytest` before committing
6. **Submit** a pull request

### Code Standards

- Python 3.11+ with type hints on all public functions
- `ruff` for linting and formatting
- Pydantic v2 models for all data contracts
- Async I/O everywhere (`httpx`, not `requests`)
- Google-style docstrings on public APIs
- `MagicMock()` for containers, `AsyncMock()` for async methods in tests

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Contact

- **Author:** Venkata Anil Kumar
- **GitHub:** [@VenkataAnilKumar](https://github.com/VenkataAnilKumar)
- **Project:** [github.com/VenkataAnilKumar/ArchonAI](https://github.com/VenkataAnilKumar/ArchonAI)

---

<div align="center">

**Built by architects, for architects.**

*ARCHON — because every startup deserves a principal architect.*

</div>
