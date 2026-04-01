# ARCHON — Pending Tasks

**Last validated:** 2026-04-01
**Overall readiness:** 97-98%
**Tests:** 477 passing, 89% coverage, 0 warnings
**Repo:** https://github.com/VenkataAnilKumar/ArchonAI (public)

---

## ✅ Completed

| Phase | Description | Tests |
|---|---|---|
| Phase 1 | Agent engine CLI — 6 agents + RAG + web search | ✅ |
| Phase 2 | Full agent engine — HITL, 14 modes, session persistence | ✅ |
| Phase 3 | SaaS shell — FastAPI + Next.js + Clerk + Stripe | ✅ |
| Phase 4 | Research quality — citations UI, confidence scores, diagrams | ✅ |
| Phase 5 | Distribution — VS Code, GitHub App, CLI (HTTP clients) | ✅ |
| Phase 6 | Input formats + Output formats + Architecture Chat (SSE) | ✅ |
| Phase 7 | Idea Mode (Mode 15) + intake wizard + multi-option design | ✅ |
| Phase 8 | Architecture Memory + Health Score (0–100, SVG dashboard) | ✅ |
| Phase 9 | MCP Server (5 tools) + GitHub/AWS/Slack connectors | ✅ |
| Tests | 477 tests, 89% coverage, 0 warnings | ✅ |
| Cleanup | Scratch files removed, .gitignore updated, repo public | ✅ |

---

## 🔴 Priority 1 — Real-Repo Validation (B4)

All 15 modes are wired but have never run against a real codebase. Finding quality is unknown.

- [ ] `python main.py --repo https://github.com/tiangolo/fastapi --mode review`
  - Every CRITICAL finding has file + line number
  - Every HIGH+ finding has ≥ 1 citation URL returning HTTP 200
  - Runtime < 60 min, cost < $15
- [ ] `python main.py --repo https://github.com/tiangolo/full-stack-fastapi-template --mode review`
  - Same quality checks
- [ ] `python main.py --brief "B2B SaaS, multi-tenant, REST API, PostgreSQL, 10k users, $1k/month cloud" --mode design`
  - Stack recommendation, ER diagram, IaC skeleton, ≥ 3 ADRs, all citation URLs valid
- [ ] Tune prompts if quality is low — read `prompts/*.md`, improve specificity
- [ ] Save output to `output/validation/`

---

## 🔴 Priority 2 — Launch Infrastructure

- [ ] **Railway deployment** — deploy API + worker + frontend. Health checks passing. Env vars set.
- [ ] **Alembic migrations** — run on deploy:
  ```
  alembic revision --autogenerate -m "add chat_messages table"
  alembic revision --autogenerate -m "add memory and health_score tables"
  alembic upgrade head
  ```
- [ ] **Stripe go-live** — activate Starter ($49) / Pro ($199) / Team ($499). Test checkout end-to-end.
- [ ] **Search adapter fallback** — if Tavily fails, fall back to Exa only (and vice versa).
- [ ] **pgvector integration test** — run with real PostgreSQL + pgvector (testcontainers). Test concurrent agent writes.
- [ ] **Rate limiting load test** — verify 100 req/min sliding window under concurrent load.

---

## 🟡 Priority 3 — Distribution Channels (Phase 5 completion)

### VS Code Extension
- [ ] `archon.reviewWorkspace` — trigger review on open workspace
- [ ] `archon.designMode` — input panel for brief
- [ ] Findings sidebar TreeView — grouped by severity
- [ ] Inline decorations — highlight files with CRITICAL findings
- [ ] Progress webview — SSE streaming agent status
- [ ] `archon.configure` — store API key in SecretStorage
- [ ] Publish to VS Code Marketplace

### GitHub App
- [ ] Error handling for Anthropic API failures (partial comment, not silence)
- [ ] Retry logic — 3 retries with exponential backoff on comment post failure
- [ ] Per-repo config — which branches trigger review, which file patterns to ignore
- [ ] Implement `callback.py` — currently empty
- [ ] Rate limiting — max 1 review per PR per 5 minutes
- [ ] Publish to GitHub Marketplace

### CLI Package
- [ ] `archon login` command — POST /auth/token, store in config
- [ ] Rich live display for SSE streaming (agent progress in terminal)
- [ ] Connection error handling (no internet, expired token, wrong API URL)
- [ ] Tests for all 6 CLI commands with mocked API
- [ ] Publish to PyPI as `archon-cli`

---

## 🟡 Priority 4 — Modes 7-14 Specialized Logic

Configs + routing done. Mode-specific agent focus, inputs, and output sections pending.

| Mode | Lead Agent | Pending |
|---|---|---|
| 7 — Cost Optimiser | Cloud | cost CSV + IaC input, savings matrix output |
| 8 — PR Reviewer | Software | PR diff only input, < 2 min, structured comment output |
| 9 — Scaling Advisor | Data | APM data input, bottleneck ranking + auto-scaling IaC |
| 10 — Drift Monitor | Cloud | snapshot diff input, weekly cron trigger |
| 11 — Feature Feasibility | Software | feature brief input, build/buy/defer verdict |
| 12 — Vendor Evaluator | All | vendor list input, TCO + lock-in matrix |
| 13 — Onboarding Accelerator | Software | codebase input, annotated system map + learning path |
| 14 — Sunset Planner | Integration | service input, shutdown sequence + GDPR checklist |

---

## Definition of Done

ARCHON ships when ALL of these pass:

- [x] `pytest --cov=src` ≥ 80% — **89% ✅**
- [ ] 3 real-repo runs pass (< 60 min, < $15, finding quality ≥ 4/5)
- [ ] Railway deployment live + health checks green
- [ ] Stripe checkout working (Starter plan end-to-end)
- [ ] `pip install archon-cli` + `archon review` works
- [ ] GitHub App posts PR comment within 2 min of PR open
