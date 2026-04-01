# ARCHON — Pending Tasks

**Last validated:** 2026-04-01
**Overall readiness:** 82-85%
**Tests:** 308 tests, 40 files, ~50% coverage
**New features tracked in:** NEWFEATURES.md

---

## ⭐ Priority 0 — Phase 6: Output Formats (build next)

All formats are free / open source. See NEWFEATURES.md Section 1 for full spec.

- [ ] `src/archon/output/html_exporter.py` — self-contained HTML, Mermaid CDN, filterable findings
- [ ] `src/archon/output/pdf_exporter.py` — WeasyPrint (`uv add weasyprint`), executive summary + full findings
- [ ] `src/archon/output/svg_renderer.py` — shell to mermaid-cli, fallback to raw .mmd
- [ ] `src/archon/output/github_issues.py` — push HIGH+ findings as GitHub Issues (free API)
- [ ] `src/archon/output/github_adr.py` — commit ADRs to /docs/adr/ in user's repo
- [ ] `src/archon/output/slack_notifier.py` — Block Kit webhook, health score + top findings
- [ ] `src/archon/output/yaml_exporter.py` — pyyaml serialization (`uv add pyyaml`)
- [ ] Update `src/archon/output/package_assembler.py` — add `format` param
- [ ] Update `main.py` — add `--format`, `--github-issues`, `--github-adrs`, `--slack-webhook` flags
- [ ] `web/app/share/[token]/page.tsx` — public shareable review page (no login)
- [ ] Tests for all 7 exporters in `src/tests/`

**Copilot prompt:** See NEWFEATURES.md bottom section "Copilot Prompt — Phase 6"

---

## 🔴 Priority 1 — Tests (50% → 80%+)

Coverage is stuck at ~50%. Need more integration-level tests.

- [ ] `test_supervisor_e2e.py` — full pipeline: 6 agents in → merged ReviewPackage out. Assert ≥ 1 finding per domain, deduplication fires, executive summary generated
- [ ] `test_hitl_full_flow.py` — Supervised mode: all 4 checkpoints fire in order, approve() continues, veto() returns partial output
- [ ] `test_runner.py` — job status transitions: RUNNING → COMPLETED, RUNNING → PARTIAL (on timeout), RUNNING → FAILED (on error)
- [ ] `test_rag_indexer.py` — index python_fastapi fixture repo, assert chunks stored, retriever returns relevant results
- [ ] `test_chunker_ast.py` — AST chunking for Python/JS/TS: functions and classes are chunk boundaries (not line-based splits)
- [ ] `test_formatter_all_modes.py` — run formatter for all 14 modes, assert mode-specific sections present in output
- [ ] `test_e2e_review.py` — full pipeline on fixtures/sample_repos/python_fastapi/: clone → index → agents → merge → ZIP. Assert package structure matches spec
- [ ] `test_e2e_design.py` — full design pipeline on a brief string, assert output has stack recommendation + ≥ 3 ADRs + ER diagram
- [ ] `test_partial_output.py` — kill 1 agent mid-run, verify other 5 agents' findings still delivered
- [ ] `test_large_repo_rejection.py` — repo > 500k LOC rejected with clear ArchonError

**Target:** `pytest --cov=src --cov-report=term-missing` shows ≥ 80%

**Copilot prompt:**
```
@workspace Expand test coverage from ~50% to 80%+.

Create these test files in src/tests/:
1. test_supervisor_e2e.py — full pipeline with mocked agents, assert merged ReviewPackage
2. test_hitl_full_flow.py — Supervised mode all 4 checkpoints, approve + veto paths
3. test_runner.py — job status transitions (RUNNING/COMPLETED/PARTIAL/FAILED)
4. test_rag_indexer.py — index fixtures/sample_repos/python_fastapi/, assert retrieval works
5. test_chunker_ast.py — AST chunking for Python/JS, functions = chunk boundaries
6. test_formatter_all_modes.py — formatter for all 14 modes, assert mode-specific sections
7. test_e2e_review.py — full pipeline on python_fastapi fixture, assert ZIP package structure
8. test_e2e_design.py — design mode on brief string, assert ADRs + stack recommendation
9. test_partial_output.py — 1 agent fails, other 5 still deliver output
10. test_large_repo_rejection.py — >500k LOC raises ArchonError

Read source files before writing each test.
After every 3 files: pytest src/tests/ -v --tb=short
Final: pytest --cov=src --cov-report=term-missing
```

---

## 🔴 Priority 2 — Real-Repo Validation (B4)

All modes are wired but have never run against a real codebase. Finding quality is unknown.

- [ ] `python main.py --repo https://github.com/tiangolo/fastapi --mode review`
  - Every CRITICAL finding has file + line number
  - Every HIGH+ finding has ≥ 1 citation with valid URL (HTTP 200)
  - Runtime < 60 min, cost < $15
- [ ] `python main.py --repo https://github.com/tiangolo/full-stack-fastapi-template --mode review`
  - Same checks + output delivered in < 60 minutes
- [ ] `python main.py --brief "B2B SaaS, multi-tenant, REST API, PostgreSQL, 10k users, $1k/month cloud" --mode design`
  - Stack recommendation, ER diagram, IaC skeleton, ≥ 3 ADRs, all citation URLs valid
- [ ] Tune prompts if quality is low (too generic / missing evidence / hallucinated URLs)
- [ ] Save output to output/validation/

**Copilot prompt:**
```
@workspace Run ARCHON against 3 real targets and validate output quality.

1. python main.py --repo https://github.com/tiangolo/fastapi --mode review
2. python main.py --repo https://github.com/tiangolo/full-stack-fastapi-template --mode review
3. python main.py --brief "B2B SaaS, multi-tenant, REST API, PostgreSQL, 10k users, $1k/month cloud" --mode design

For each run check:
- Every CRITICAL finding has a real file path + line number
- Every HIGH+ finding has ≥ 1 citation URL that returns HTTP 200
- No hallucinated URLs
- Runtime < 60 min, cost < $15 (log token counts)

If quality is low, read prompts/*.md and improve specificity.
Save outputs to output/validation/.
```

---

## 🟡 Priority 3 — Modes 7-14 Specialized Logic

Configs + routing done. No mode-specific agent logic or real-world tests.

- [ ] **Cost Optimiser (7)** — agent routing: cloud (lead) + data. Input: cost CSV + IaC. Output: ranked savings, effort vs savings matrix, IaC quick wins
- [ ] **PR Reviewer (8)** — input: PR diff only (not full codebase). Complete in < 2 min. Output: structured PR comment with blocker/warning/suggestion labels. Wire into github-app/src/app.py
- [ ] **Scaling Advisor (9)** — agent routing: data (lead) + cloud + integration. Input: APM data + target scale. Output: bottleneck ranking, scaling strategy, auto-scaling IaC, cost model at scale
- [ ] **Drift Monitor (10)** — input: previous snapshot + live IaC + recent PRs. Output: drift report. Complete drift_worker.py. Wire weekly cron trigger
- [ ] **Feature Feasibility (11)** — input: feature brief + current architecture. Output: build/buy/defer verdict, complexity (S/M/L/XL), prerequisites, risk register
- [ ] **Vendor Evaluator (12)** — input: shortlisted vendors + evaluation criteria. Output: comparison matrix, TCO over 3 years, lock-in risk, recommended vendor
- [ ] **Onboarding Accelerator (13)** — input: codebase + optional focus areas. Output: annotated system map, first-week/first-month learning path, known landmines
- [ ] **Sunset Planner (14)** — input: service to sunset + codebase. Output: full dependency map, ordered shutdown sequence, data disposition plan, GDPR deletion checklist

**Copilot prompt:**
```
@workspace Implement specialized logic for Modes 7-14.

Read docs/prds/prd-07 through prd-14 for full requirements.
Read src/archon/engine/modes/configs.py to understand current configs.
Read src/archon/agents/base.py to understand the agent pattern.

For each mode:
1. Add mode-specific agent prompt variant (mode_focus field passed to agents)
2. Add mode-specific input parsing (cost CSV, PR diff, APM data, etc.)
3. Add mode-specific output sections in formatter.py
4. Write 3-5 tests per mode

Modes in priority order: PR Reviewer (8), Cost Optimiser (7), Feature Feasibility (11), Vendor Evaluator (12), Scaling Advisor (9), Drift Monitor (10), Onboarding Accelerator (13), Sunset Planner (14).
```

---

## 🟡 Priority 4 — Distribution Channels

All 3 channels have real HTTP clients. Missing: commands, UI, error handling, publish.

### VS Code Extension
- [ ] Implement `archon.reviewWorkspace` command — trigger review on open workspace
- [ ] Implement `archon.designMode` command — input panel for brief
- [ ] Implement findings sidebar TreeView — grouped by severity
- [ ] Implement inline decorations — highlight files with CRITICAL findings
- [ ] Implement progress webview — SSE streaming agent status
- [ ] Implement `archon.configure` command — store API key in SecretStorage
- [ ] Write extension command tests
- [ ] Publish to VS Code Marketplace

### GitHub App
- [ ] Add error handling for Anthropic API failures (return partial comment, not silence)
- [ ] Add retry logic — 3 retries with exponential backoff on comment post failure
- [ ] Add per-repo config — which branches trigger review, which file patterns to ignore
- [ ] Implement `callback.py` — currently empty
- [ ] Add rate limiting — max 1 review per PR per 5 minutes
- [ ] Publish to GitHub Marketplace

### CLI Package
- [ ] Implement `archon login` command — POST /auth/token, store in config
- [ ] Add Rich live display for SSE streaming (agent progress in terminal)
- [ ] Add connection error handling (no internet, expired token, wrong API URL)
- [ ] Write tests for all 6 CLI commands with mocked API
- [ ] Publish to PyPI as `archon-cli`

---

## 🟡 Priority 5 — Launch Infrastructure

- [ ] **Railway deployment** — deploy API + worker + frontend. Health checks passing. Env vars set.
- [ ] **Stripe go-live** — activate Starter ($49) / Pro ($199) / Team ($499) products. Test checkout flow end-to-end.
- [ ] **Search adapter fallback** — if Tavily fails, use Exa only (and vice versa). Currently no fallback logic.
- [ ] **pgvector integration test** — run with real PostgreSQL + pgvector extension (testcontainers). Test concurrent writes from multiple agents.
- [ ] **Rate limiting load test** — verify 100 req/min sliding window holds under concurrent load.

---

## Definition of Done

ARCHON ships when ALL of these pass:

- [ ] `pytest --cov=src` ≥ 80%
- [ ] 3 real-repo runs pass (< 60 min, < $15, finding quality ≥ 4/5)
- [ ] Railway deployment live + health checks green
- [ ] Stripe checkout working (Starter plan end-to-end)
- [ ] `pip install archon-cli` + `archon review` works
- [ ] GitHub App posts PR comment within 2 min of PR open
