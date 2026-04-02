# ARCHON — Pending Tasks

**Last validated:** 2026-04-01
**Overall readiness:** 99% code-complete
**Tests:** 531 passing, 89% coverage, 0 warnings
**Repo:** https://github.com/VenkataAnilKumar/ArchonAI (public)

---

## ✅ Completed

| Phase | Description | Tests |
|---|---|---|
| Phase 1 | Agent engine CLI — 6 agents + RAG + web search | ✅ |
| Phase 2 | Full agent engine — HITL, 15 modes, session persistence | ✅ |
| Phase 3 | SaaS shell — FastAPI + Next.js + Clerk + Stripe | ✅ |
| Phase 4 | Research quality — citations UI, confidence scores, diagrams | ✅ |
| Phase 5 | Distribution — VS Code, GitHub App, CLI (fully hardened) | ✅ |
| Phase 6 | Input formats + Output formats + Architecture Chat (SSE) | ✅ |
| Phase 7 | Idea Mode (Mode 15) + intake wizard + multi-option design | ✅ |
| Phase 8 | Architecture Memory + Health Score (0–100, SVG dashboard) | ✅ |
| Phase 9 | MCP Server (5 tools) + GitHub/AWS/Slack connectors | ✅ |
| Modes 7-14 | Specialized logic — cost, PR, scaling, drift, feasibility, vendor, onboarding, sunset | ✅ |
| CLI Auth | login/logout/status + connection/auth/API error handling | ✅ |
| GitHub App | Retry logic, partial-failure comment, per-repo config, callback.py, rate limiting | ✅ |
| VS Code | SecretStorage for API key, archon.configure command | ✅ |
| CLI SSE | Rich live display, --no-stream flag, offline/expired-token tests | ✅ |
| Tests | 531 tests, 89% coverage, 0 warnings | ✅ |
| Cleanup | Scratch files removed, .gitignore updated, repo public | ✅ |

---

## 🔴 Priority 1 — Real-Repo Validation

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

## 🟡 Priority 3 — Publish Distribution Channels

Code-complete. Needs accounts + publishing steps only.

### VS Code Extension
- [ ] Publish to VS Code Marketplace (needs publisher account + `vsce publish`)

### GitHub App
- [ ] Register on GitHub Marketplace (needs GitHub App registration + listing)

### CLI Package
- [ ] Publish to PyPI as `archon-cli` (needs PyPI account + `twine upload`)

---

## Definition of Done

ARCHON ships when ALL of these pass:

- [x] `pytest --cov=src` ≥ 80% — **89% ✅**
- [x] All 15 modes implemented with specialized logic — **✅**
- [x] Distribution channels code-complete — **✅**
- [ ] 3 real-repo runs pass (< 60 min, < $15, finding quality ≥ 4/5)
- [ ] Railway deployment live + health checks green
- [ ] Stripe checkout working (Starter plan end-to-end)
- [ ] `pip install archon-cli` + `archon review` works
- [ ] GitHub App posts PR comment within 2 min of PR open
