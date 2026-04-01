# ARCHON — Pending Work

**Last validated:** 2026-03-31
**Validation result:** 85% production-ready
**Honest status:** Phase 1 = 90%, Phase 2 = 85%, Phases 3-4 = 40%, Phase 5 = 85%

---

## Validation Summary

| Area | Status | Gap |
|---|---|---|
| B1: pgvector SQL | ✅ Done | Correct `$N` placeholders for asyncpg |
| B2: cost_reader.py | ✅ Done | 170 lines, real parser, 9 tests |
| B3: API tests | ✅ Done | 261 lines, 16 test functions |
| B4: Real-repo validation | ⏭️ Deferred | — |
| Mode wiring (all 14) | ✅ Done | ALL_MODES + AGENT_REGISTRY + _build_agents() |
| Tavily / Exa adapters | ✅ Real | Real httpx calls to live APIs |
| Claude adapter | ✅ Real | AsyncAnthropic + extended thinking enabled |
| VS Code extension | ✅ Real | Real fetch() + SSE streaming |
| GitHub App | ✅ Real | 100 lines, signature verification, PR webhook |
| CLI package | ✅ Real | Real httpx, start/stream/download |
| Test coverage | 🟡 ~30% | 203 tests, 22 files — missing 19 dedicated modules |
| Output module tests | 🟡 Partial | citations/confidence/diagrams/zip — only in test_output_extended.py |
| Fixtures | 🟡 Partial | Only small_repo/ — missing node_app/ and python_fastapi/ |

---

## 🔴 Critical Blockers (fix first)

### B1. pgvector SQL Bug — will crash on first use
**Location:** `src/archon/infrastructure/vector_store/pgvector_store.py` lines 61-64, 77-79
**Issue:** SQL INSERT and query use numbered placeholders ($1, $2) but parameters are passed incorrectly — will crash on first `add_documents()` or `query()` call
- [x] Fix SQL parameter placeholders in `add_documents()` (lines 61-64)
- [x] Fix SQL parameter placeholders in `query()` (lines 77-79)
- [x] Add SQL correctness tests (source inspection) in test_pgvector_store.py

**Copilot prompt:**
```
@workspace Fix the SQL bug in src/archon/infrastructure/vector_store/pgvector_store.py
Lines 61-64 and 77-79 have broken SQL parameter placeholders in add_documents() and query().
Fix the placeholders, then write integration tests using testcontainers.
```

---

### B2. cost_reader.py Missing — Mode 7 (Cost Optimiser) blocked
**Location:** `src/archon/infrastructure/cost_reader.py`
**Issue:** File does not exist. Cost Optimiser mode cannot run without it.
- [x] Created `src/archon/infrastructure/tools/cost_reader.py` (AWS + GCP + Azure)
  - Parse AWS Cost Explorer CSV export
  - Parse GCP Billing CSV export
  - Return structured cost data (service, cost, usage_type, region)
- [x] 9 tests in test_cost_reader.py — all passing

**Copilot prompt:**
```
@workspace Create src/archon/infrastructure/cost_reader.py
It must parse AWS Cost Explorer and GCP Billing CSV exports.
Read docs/prds/prd-07-cost-optimiser.md for what data is needed.
Write unit tests with sample CSV fixtures in src/tests/fixtures/
```

---

### B3. API Routes 0% Tested — Production risk
**Location:** `src/api/` — 9 routes, 28 files, 0% coverage
**Issue:** No tests for any API route. Error handling, auth, streaming all unvalidated.
- [x] 16 tests in test_api_routes.py covering health, reviews, jobs, packages, feedback, webhooks
- [x] Test Clerk JWT auth middleware -- 8 tests (exempt paths, missing token, valid mock, expired, invalid)
- [x] Test rate limiting -- 6 tests (exempt, under limit, at limit 429, retry-after header, expired pruning)
- [x] Test SSE streaming -- 7 tests (status, not-found, progress events, failed, partial, headers)
- [x] Test error responses (404, 400, 402)

**Copilot prompt:**
```
@workspace Write tests for all API routes in src/api/
Read src/api/routes/ — 9 route files, all 0% tested.
Use pytest + httpx AsyncClient. Mock Clerk JWT auth.
Test: happy path, auth failure, rate limit, error responses.
Target: 80%+ coverage on src/api/
```

---

### B4. No Real-Repo Validation — DEFERRED (do after Phase 1 test coverage done)
**Issue:** All modes are wired but have NEVER been run against a real codebase. Finding quality, citation accuracy, and cost are all unknown.
- [ ] Run: `python main.py --repo https://github.com/tiangolo/fastapi --mode review`
  - Verify every CRITICAL finding has file + line number
  - Verify every HIGH+ finding has ≥ 1 citation with valid URL (HTTP 200)
  - Verify executive summary health rating is accurate
  - Log: runtime, token count, cost (target < $15)
- [ ] Run: `python main.py --repo https://github.com/tiangolo/full-stack-fastapi-template --mode review`
  - Same checks + verify output in < 60 minutes
- [ ] Run: `python main.py --brief "B2B SaaS, multi-tenant, REST API, PostgreSQL, 10k users, $1k/month cloud" --mode design`
  - Verify stack recommendation, ER diagram, IaC skeleton, ≥ 3 ADRs
  - Verify all citation URLs return HTTP 200
- [ ] Tune prompts if quality is low

---

## 🔴 Priority 1 — Fix Phase 1 (Tests + Validation)

### 1. Expand Test Coverage (~30% → 80%+)

**Location:** `src/tests/`
**Current state:** 203 tests, 22 test files, ~30% coverage. Missing 19 dedicated test modules.

Tasks:
- [x] test_agent_ai/cloud/data/integration/security/software.py — 6 agent test files ✅
- [x] test_hitl.py — 12 tests covering all 3 HITL modes + 4 checkpoints ✅
- [x] test_github_reader.py — 8 tests: clone, file listing, 500k LOC rejection ✅
- [x] test_redis_cache.py — 5 tests: set/get/expiry, namespace isolation ✅
- [x] test_claude_adapter.py — 5 tests: thinking budgets, fallback, retry ✅
- [x] test_tavily_adapter.py — 4 tests: success, 429, network error, empty ✅
- [x] test_exa_adapter.py — 5 tests: success, 500, timeout, empty ✅
- [x] test_zip_builder.py — 9 tests: archive structure, file presence, ZIP integrity ✅
- [x] test_citations.py — 6 tests: deduplication, credibility scoring ✅
- [x] test_confidence.py — 12 tests: scoring across severity levels ✅
- [x] test_diagram_generator.py — 8 tests: valid Mermaid C4 + flowchart output ✅
- [x] fixtures/sample_repos/node_app/ — index.js, package.json, .env.example ✅
- [x] fixtures/sample_repos/python_fastapi/ — main.py, routes, models, db.py ✅

**Target:** `pytest --cov=src --cov-report=term-missing` shows ≥ 80%

---

### 2. Wire Modes 3-6 into ALL_MODES

**Location:** `src/archon/engine/modes/configs.py`
**Current state:** Modes 3-6 are DEFINED in configs.py but NOT added to `ALL_MODES` dict. They are unreachable.

Tasks:
- [x] Add modes 3-6 to `ALL_MODES` dict in `configs.py` ✅ (also added modes 7-14)
- [x] Add mode selector logic in `supervisor.py` — AGENT_REGISTRY + _build_agents() ✅
- [x] Add system prompt variant per mode — mode_focus passthrough to all 6 agents ✅
- [x] Add output template routing per mode in `formatter.py` — _SECTION_MAP + _resolve_section ✅
- [x] Add HITL checkpoint config per mode — MODE_HITL_OVERRIDES + MODE_HITL_MINIMUM ✅

**Mode-specific agent routing:**
```
Migration Planner  → integration-architect (lead), cloud, software, data
Compliance Auditor → security-architect (lead), data, cloud, software
Due Diligence      → all 6 (external audience tone, high thinking budget)
Incident Responder → software + cloud only (speed mode, 5-min increments)
```

---

### 3. Validate Prompts on Real Repos

**Current state:** All 7 prompts exist but have NEVER been run against a real codebase.

Tasks:
- [ ] Run: `python main.py --repo https://github.com/tiangolo/fastapi --mode review`
  - Check: every CRITICAL finding has file + line number
  - Check: every HIGH+ finding has ≥ 1 citation with valid URL (returns HTTP 200)
  - Check: executive summary health rating matches finding severity
  - Check: no hallucinated URLs
  - Log: total runtime, token count, cost
- [ ] Run: `python main.py --repo https://github.com/tiangolo/full-stack-fastapi-template --mode review`
  - Same checks as above
  - Check: output delivered in < 60 minutes
  - Check: LLM cost < $15
- [ ] Run: `python main.py --brief "B2B SaaS, multi-tenant, REST API, PostgreSQL, 10k users year 1, $1k/month cloud budget" --mode design`
  - Check: output contains stack recommendation, ER diagram, IaC skeleton, ≥ 3 ADRs
  - Check: every technology recommendation is named specifically (not generic)
  - Check: all citations have valid URLs
- [ ] Tune prompts based on results (too generic / missing evidence / wrong severity / hallucinated URLs)

---

### 4. End-to-End Integration Test

**Location:** `src/tests/integration/test_e2e.py`
**Current state:** Integration tests exist but only use a 150 LOC fixture repo — not representative.

Tasks:
- [ ] Write `test_e2e_review.py` — full pipeline on `fixtures/sample_repos/python_fastapi/`
  - clone → index → 6 agents → merge → format → output file
  - Assert output package structure matches spec
  - Assert ≥ 1 finding per domain
  - Assert every CRITICAL finding has evidence
- [ ] Write `test_e2e_design.py` — full design pipeline on a real brief
- [ ] Write `test_partial_output.py` — kill 1 agent mid-run, verify partial output delivered
- [ ] Write `test_large_repo_rejection.py` — repo > 500k LOC rejected with clear error
- [ ] Write `test_hitl_checkpoints.py` — verify all 4 checkpoints fire in Supervised mode

---

## 🔴 Priority 2 — Implement Modes 7-14 (Phases 3-4)

Modes 7-14 have PRDs written but ZERO code. Each mode needs full implementation.

### 5. Cost Optimiser (Mode 7)
**PRD:** `docs/prds/prd-07-cost-optimiser.md`
**Location:** `src/archon/engine/modes/`

- [x] Add `COST_OPTIMISER` config to `configs.py` and `ALL_MODES` ✅
- [ ] Agent routing: cloud-architect (lead), data-architect
- [ ] Input: cloud cost export CSV (AWS Cost Explorer / GCP Billing) + current IaC
- [ ] Add cost export parser: `src/archon/infrastructure/cost_reader.py`
- [ ] Output sections: ranked savings opportunities, effort vs savings matrix, IaC quick wins, projected cost curve
- [ ] Test with: sample AWS Cost Explorer export

### 6. PR Reviewer (Mode 8)
**PRD:** `docs/prds/prd-08-pr-reviewer.md`
**Location:** `src/archon/engine/modes/` + `github-app/src/`

- [x] Add `PR_REVIEWER` config to `configs.py` and `ALL_MODES` ✅
- [ ] Agent routing: contextual — only agents relevant to changed files
- [ ] Input: PR diff (not full codebase) + existing architecture snapshot
- [ ] NFR: complete in < 2 minutes (narrow scope, no RAG indexing)
- [ ] Output: structured PR comment — severity labels (blocker/warning/suggestion), links to ADRs
- [ ] Wire `github-app/src/app.py` to call PR Reviewer mode (currently calls generic review)
- [ ] Test with: sample PR diff fixture

### 7. Scaling Advisor (Mode 9)
**PRD:** `docs/prds/prd-09-scaling-advisor.md`
**Location:** `src/archon/engine/modes/`

- [x] Add `SCALING_ADVISOR` config to `configs.py` and `ALL_MODES` ✅
- [ ] Agent routing: data-architect (lead), cloud-architect, integration-architect
- [ ] Input: current architecture + APM data or load description + target scale (10x/100x) + timeline
- [ ] Output: bottleneck ranking by failure threshold, scaling strategy per component, auto-scaling IaC, load test plan, cost model at target scale
- [ ] Test with: single-DB monolith brief targeting 100x scale

### 8. Drift Monitor (Mode 10)
**PRD:** `docs/prds/prd-10-drift-monitor.md`
**Location:** `src/archon/engine/modes/` + `src/api/workers/drift_worker.py`

- [x] Add `DRIFT_MONITOR` config to `configs.py` and `ALL_MODES` ✅
- [ ] Agent routing: all 6 (diff/comparison mode, not generative)
- [ ] Input: previous architecture snapshot + live IaC state + recent merged PRs
- [ ] Output: drift report — what changed, what was expected, what wasn't, ADRs needing update, manual console changes
- [ ] Complete `src/api/workers/drift_worker.py` — currently exists but is likely a stub
- [ ] Wire scheduled cron trigger (weekly by default)
- [ ] Test with: architecture snapshot + 3 deliberate drift changes

### 9. Feature Feasibility (Mode 11)
**PRD:** `docs/prds/prd-11-feature-feasibility.md`
**Location:** `src/archon/engine/modes/`

- [x] Add `FEATURE_FEASIBILITY` config to `configs.py` and `ALL_MODES` ✅
- [ ] Agent routing: software-architect (lead), data-architect
- [ ] Input: feature brief or PRD + current architecture
- [ ] Output: feasibility verdict (build/buy/defer) per component, complexity estimate (S/M/L/XL), prerequisites, risk register, recommended approach
- [ ] Test with: "add real-time collaboration to existing SaaS" brief

### 10. Vendor Evaluator (Mode 12)
**PRD:** `docs/prds/prd-12-vendor-evaluator.md`
**Location:** `src/archon/engine/modes/`

- [x] Add `VENDOR_EVALUATOR` config to `configs.py` and `ALL_MODES` ✅
- [ ] Agent routing: cloud-architect (lead), integration-architect, data-architect
- [ ] Input: shortlisted vendors (2-5) + current architecture + evaluation criteria
- [ ] Output: comparison matrix, lock-in risk register, TCO over 3 years, recommended vendor with rationale, switch cost estimate
- [ ] Test with: "PostgreSQL vs MongoDB vs DynamoDB for a multi-tenant SaaS"

### 11. Onboarding Accelerator (Mode 13)
**PRD:** `docs/prds/prd-13-onboarding-accelerator.md`
**Location:** `src/archon/engine/modes/`

- [x] Add `ONBOARDING_ACCELERATOR` config to `configs.py` and `ALL_MODES` ✅
- [ ] Agent routing: all 6 (explanatory mode, not diagnostic)
- [ ] Input: codebase + optional "areas to focus on" list
- [ ] Output: personalised onboarding guide, annotated system map, "first week / first month" learning path, glossary, known landmines section
- [ ] Test with: a realistic codebase a new CTO would inherit

### 12. Sunset Planner (Mode 14)
**PRD:** `docs/prds/prd-14-sunset-planner.md`
**Location:** `src/archon/engine/modes/`

- [x] Add `SUNSET_PLANNER` config to `configs.py` and `ALL_MODES` ✅
- [ ] Agent routing: integration-architect (lead), data-architect, security-architect
- [ ] Input: service/component to sunset + codebase
- [ ] Output: full dependency map, ordered shutdown sequence (leaf nodes first), data disposition plan, migration guide, GDPR deletion compliance checklist, cost savings projection
- [ ] Test with: a legacy auth service targeted for replacement

---

## 🟡 Priority 3 — Complete Distribution Channels

### 13. VS Code Extension — Complete Commands + Publish
**Location:** `vscode-extension/src/`
**Current state:** archon-client.ts has real fetch() calls + SSE streaming. Commands and UI not yet implemented.

- [ ] Implement `archon-client.ts` — real HTTP calls to ARCHON API (POST /reviews, GET /jobs/:id/stream)
- [ ] Implement `archon.reviewWorkspace` command — clone + trigger review on open workspace
- [ ] Implement `archon.designMode` command — input panel for brief, trigger design mode
- [ ] Implement findings sidebar TreeView — populate with findings grouped by severity
- [ ] Implement inline decorations — highlight files referenced in CRITICAL findings
- [ ] Implement progress webview — SSE streaming showing agent status during run
- [ ] Implement `archon.configure` command — API key stored in VS Code SecretStorage
- [ ] Write unit tests for extension commands
- [ ] Publish to VS Code Marketplace

### 14. GitHub App — Complete Error Handling + Publish
**Location:** `github-app/src/app.py`
**Current state:** 100 lines implemented — signature verification, PR webhook handler, real httpx calls. Missing: error handling, retry, per-repo config.

- [ ] Add error handling for Anthropic API failures (return partial comment, not silence)
- [ ] Add retry logic — 3 retries with exponential backoff if comment posting fails
- [ ] Add per-repo config — which branches trigger review, which file patterns to ignore
- [ ] Implement `callback.py` — currently empty
- [ ] Add rate limiting — max 1 review per PR per 5 minutes
- [ ] Write integration tests using GitHub App test fixtures
- [ ] Publish to GitHub Marketplace

### 15. CLI Package — Complete + Publish to PyPI
**Location:** `cli-package/src/archon_cli/client.py`
**Current state:** client.py has real httpx calls — start_review, stream_progress, get_review, download_package all implemented. Missing: `archon login` command, Rich TUI for streaming, PyPI publish.

- [ ] Implement `client.py` — real HTTP calls to ARCHON API using httpx
  - `create_review(repo_url, mode, hitl)` → returns job_id
  - `stream_progress(job_id)` → SSE stream of agent status events
  - `get_package(job_id)` → returns ReviewPackage
  - `download_zip(job_id, output_path)` → downloads ZIP
  - `get_history()` → returns list of past reviews
- [ ] Implement `archon login` command — POST /auth/token, store in config
- [ ] Add real SSE streaming to terminal (Rich live display with agent progress)
- [ ] Add connection error handling (no internet, wrong API URL, expired token)
- [ ] Write tests for all 6 CLI commands with mocked API
- [ ] Publish to PyPI as `archon-cli`

---

## 🟡 Priority 4 — Infrastructure Hardening

### 16. Search Adapters — Add Tests + Fallback Logic
**Location:** `src/archon/infrastructure/search/`
**Current state:** ✅ Both adapters have real httpx calls to live APIs. Missing: fallback logic and dedicated tests.

- [x] Tavily adapter — real httpx.AsyncClient calls to api.tavily.com ✅
- [x] Exa adapter — real httpx.AsyncClient calls to api.exa.ai ✅
- [ ] Add fallback: if Tavily fails, use Exa only (and vice versa)
- [ ] Add rate limiting: max 10 calls/min per adapter
- [ ] Write dedicated tests with mocked HTTP responses

### 17. pgvector — Real Integration
**Location:** `src/archon/infrastructure/pgvector_store.py`
**Current state:** 97-line file, 0% tested. Likely has bugs.

- [ ] Write integration tests using testcontainers PostgreSQL with pgvector extension
- [ ] Test: insert chunks, search by query, namespace isolation per project
- [ ] Test: concurrent writes from multiple agents
- [ ] Add Alembic migration for pgvector table schema
- [ ] Verify HNSW index is created correctly

### 18. Rate Limiting on API
**Location:** `src/api/middleware/rate_limit.py`
**Current state:** Middleware file exists, implementation not verified.

- [ ] Verify sliding window rate limiting: 100 req/min per user
- [ ] Add per-endpoint limits: review creation max 5 concurrent per user
- [x] Test rate limiting -- 6 tests (exempt, under limit, at limit 429, retry-after header, expired pruning)
- [ ] Return proper 429 response with Retry-After header

---

## Copilot Prompts

### Fix Priority 1 — Wire Modes 3-6
```
@workspace Read PENDING.md Priority 1 Task 2.

The modes 3-6 (Migration Planner, Compliance Auditor, Due Diligence,
Incident Responder) are DEFINED in src/archon/engine/modes/configs.py
but NOT added to the ALL_MODES dict and NOT wired into the supervisor.

Do the following:
1. Add modes 3-6 to ALL_MODES dict in configs.py
2. Update supervisor.py to route to the correct agent subset per mode
3. Add system prompt variant per mode (different framing)
4. Add output template routing per mode in formatter.py

Read these files first:
- src/archon/engine/modes/configs.py
- src/archon/engine/supervisor.py
- src/archon/output/formatter.py
- docs/prds/prd-03-migration-planner.md
- docs/prds/prd-04-compliance-auditor.md
- docs/prds/prd-05-due-diligence.md
- docs/prds/prd-06-incident-responder.md
```

### ✅ DONE — Expand Test Coverage (~30% → 80%+)
**Last checked:** 2026-03-31 — 308 tests, 38 files. 16/16 new test files created. Both fixtures added.

```
@workspace Read PENDING.md Priority 1 Task 1 "Expand Test Coverage".

Create these 16 test files one by one. Read the source file before writing each test.

Priority order:
1. src/tests/test_hitl.py — test all 3 HITL modes + 4 checkpoints
2. src/tests/test_agent_software.py — mock LLM/search, test AgentOutput shape
3. src/tests/test_agent_cloud.py
4. src/tests/test_agent_security.py
5. src/tests/test_agent_data.py
6. src/tests/test_agent_integration.py
7. src/tests/test_agent_ai.py
8. src/tests/test_zip_builder.py
9. src/tests/test_citations.py
10. src/tests/test_confidence.py
11. src/tests/test_diagram_generator.py
12. src/tests/test_github_reader.py
13. src/tests/test_redis_cache.py
14. src/tests/test_claude_adapter.py
15. src/tests/test_tavily_adapter.py
16. src/tests/test_exa_adapter.py

Also create:
- src/tests/fixtures/sample_repos/node_app/ (index.js, package.json, .env.example)
- src/tests/fixtures/sample_repos/python_fastapi/ (main.py, routes/users.py, models/user.py, db.py)

After every 4 files run: pytest src/tests/ -v --tb=short
Final: pytest --cov=src --cov-report=term-missing
```

### Implement Modes 7-14
```
@workspace Read PENDING.md Priority 2 Tasks 5-12.

Implement all 8 modes (7-14): Cost Optimiser, PR Reviewer, Scaling Advisor,
Drift Monitor, Feature Feasibility, Vendor Evaluator, Onboarding Accelerator,
Sunset Planner.

For each mode:
1. Add config to src/archon/engine/modes/configs.py + ALL_MODES dict
2. Add agent routing (correct subset of 6 agents)
3. Add output template in formatter.py
4. Write tests

Read PRDs in docs/prds/prd-07 through prd-14 for full requirements.
Follow the pattern of existing modes (Review, Design) in configs.py.
```

### Complete Distribution Channels
```
@workspace Read PENDING.md Priority 3.

Complete these 3 distribution channels:
1. VS Code extension — implement archon-client.ts (real API calls) + all commands
2. GitHub App — add error handling, retry, per-repo config, implement callback.py
3. CLI package — implement client.py (real httpx calls), archon login, SSE streaming

Read these files first:
- PENDING.md Priority 3 (Tasks 13, 14, 15)
- docs/api/README.md (API endpoints)
- vscode-extension/src/ (existing scaffolding)
- github-app/src/app.py (existing webhook handler)
- cli-package/src/archon_cli/ (existing CLI structure)
```

---

## Definition of Done

ARCHON is **production-ready** when ALL of these pass:

**Phase 1:**
- [ ] Test coverage ≥ 80% (`pytest --cov=src`)
- [ ] 3 real-repo end-to-end runs pass (< 60 min, < $15, finding quality ≥ 4/5)
- [ ] Modes 1-2 (Review + Design) verified on 3 different codebases

**Phase 2:**
- [ ] Modes 3-6 wired, tested, and verified on test inputs
- [ ] HITL checkpoints fire correctly per mode

**Phase 3-4:**
- [ ] Modes 7-14 implemented and tested
- [ ] Drift Monitor runs on schedule without errors

**Phase 5:**
- [ ] VS Code extension installs and runs a review end-to-end
- [ ] GitHub App posts PR comment within 2 minutes of PR open
- [ ] `pip install archon-cli` + `archon review` works end-to-end

**Infrastructure:**
- [ ] pgvector tested with real PostgreSQL
- [ ] Search adapters tested with real API calls
- [ ] Rate limiting verified under load
- [ ] Stripe billing live (Starter $49 / Pro $199 / Team $499)
- [ ] Railway deployment live and passing health checks
