# ARCHON — Pending Tasks

**Last validated:** 2026-04-01
**Overall readiness:** 97-98%
**Tests:** 477 tests, ~70 files, 89% coverage
**New features tracked in:** NEWFEATURES.md

---

## ✅ Phase 6: Complete

All Phase 6 deliverables shipped: Output Formats + Chat Foundation + Input Parsers.

### Phase 6A — Architecture Chat ✅ COMPLETE

- [x] `src/archon/chat/__init__.py`
- [x] `src/archon/chat/engine.py` — streaming chat engine (SSE), saves history
- [x] `src/archon/chat/history.py` — ChatMessage Pydantic model + DB persistence
- [x] `src/archon/chat/context_builder.py` — system prompt with embedded review findings
- [x] `src/api/routes/chat.py` — POST + GET `/reviews/{id}/chat`, SSE StreamingResponse
- [x] Registered in `src/api/main.py`
- [x] `src/db/models.py` — ChatMessageRow added
- [x] `web/src/components/chat/ChatWindow.tsx` — SSE-streaming chat UI, loads history on mount
- [x] `web/src/app/(dashboard)/reviews/[id]/chat/page.tsx`
- [x] `src/tests/test_chat_engine.py` — 10 tests, all passing
- [ ] Alembic migration for `chat_messages` — run on deploy: `alembic revision --autogenerate -m "add chat_messages table"`

---

### Phase 6B — Input Format Parsers ✅ COMPLETE

- [x] `src/archon/input/__init__.py`
- [x] `src/archon/input/base.py` — ParsedInput model + InputParser ABC
- [x] `src/archon/input/pdf_parser.py` — pymupdf
- [x] `src/archon/input/image_parser.py` — Claude Vision API
- [x] `src/archon/input/website_parser.py` — httpx + BeautifulSoup4
- [x] `src/archon/input/iac_parser.py` — python-hcl2 (Terraform) + yaml (CloudFormation)
- [x] `src/archon/input/sql_parser.py` — sqlparse
- [x] `src/archon/input/openapi_parser.py` — pyyaml/json
- [x] `src/archon/input/zip_parser.py` — stdlib zipfile, delegates to other parsers
- [x] `src/archon/input/combiner.py` — merges ParsedInputs into unified context
- [x] `src/api/routes/inputs.py` — POST `/reviews/{id}/inputs` (multipart upload)
- [x] Registered in `src/api/main.py`
- [x] Tests: 17 tests across 6 files, all passing

**Copilot prompt:**
```
@workspace Build input format parsers for ARCHON — Phase 6B.

Read:
- src/archon/rag/chunker.py — understand how text content is processed
- src/archon/core/models/ — understand domain model patterns
- src/api/routes/reviews.py — follow same route pattern

Build src/archon/input/ module:

1. base.py
   - ParsedInput Pydantic model: source_type, title, content (str), metadata (dict), images (list[bytes])
   - InputParser ABC with: async parse(source: str | bytes) -> ParsedInput

2. pdf_parser.py (uv add pymupdf)
   - PdfParser(InputParser): accepts file bytes
   - Extract text per page, extract images
   - Return ParsedInput(source_type="pdf", content=full_text, metadata={pages, title})

3. image_parser.py
   - ImageParser(InputParser): accepts file bytes or URL
   - Call Claude claude-opus-4-6 vision: "Describe the architecture shown. List all components, connections, and technology choices visible."
   - Return ParsedInput(source_type="image", content=description)

4. website_parser.py (uv add httpx beautifulsoup4)
   - WebsiteParser(InputParser): accepts URL string
   - httpx GET, BeautifulSoup extract main content (remove nav/footer/ads)
   - Return ParsedInput(source_type="website", content=cleaned_text, metadata={url, title})

5. iac_parser.py (uv add python-hcl2)
   - IaCParser(InputParser): accepts .tf file content or .yaml CloudFormation
   - Extract resources, providers, variables, outputs
   - Return ParsedInput(source_type="iac", content=structured_summary, metadata={resource_types})

6. sql_parser.py (uv add sqlparse)
   - SqlParser(InputParser): accepts SQL dump string
   - Extract CREATE TABLE statements, column names + types, FK relationships
   - Return ParsedInput(source_type="sql", content=schema_summary, metadata={tables, relationships})

7. openapi_parser.py
   - OpenApiParser(InputParser): accepts YAML or JSON string
   - Extract endpoints (path + method + description), schemas, security schemes
   - Return ParsedInput(source_type="openapi", content=api_summary, metadata={endpoint_count, auth_type})

8. zip_parser.py
   - ZipParser(InputParser): accepts zip bytes
   - Extract, scan for .tf/.yaml/.sql/.pdf files, delegate to appropriate parser
   - Return ParsedInput(source_type="zip", content=combined_content)

9. combiner.py
   - merge_inputs(inputs: list[ParsedInput]) -> str
   - Produce structured context string with section headers per input type

10. src/api/routes/inputs.py
    - POST /reviews/{review_id}/inputs (multipart, field: file UploadFile, type: str)
    - Auth required
    - Parse based on type, store ParsedInput in Redis keyed by review_id
    - Return { source_type, title, content_preview (first 500 chars), metadata }

11. Register: api_v1.include_router(inputs.router, prefix="/reviews")

12. Tests: src/tests/test_input_pdf.py, test_input_image.py, test_input_website.py, test_input_iac.py, test_input_sql.py, test_input_openapi.py
    - Use fixture files in fixtures/input_samples/
    - Mock Claude API calls in image parser tests
    - Mock httpx in website parser tests

Run: pytest src/tests/test_input_*.py -v
```

---

## ✅ Phase 7: Complete — Idea Mode (Mode 15) + Multi-option Design

- [x] `src/archon/engine/modes/configs.py` — IDEA_MODE added (Mode 15)
- [x] `src/archon/engine/intake.py` — ProductBrief + 6 plain-English intake questions
- [x] `src/archon/engine/requirements_translator.py` — TechnicalConstraints translator
- [x] `src/archon/engine/multi_option_designer.py` — 3 options: Lean / Scalable / Enterprise
- [x] `src/archon/output/formatter.py` — product_summary, architecture_options, recommended_option, what_to_build_first, plain_english_glossary sections
- [x] `src/api/routes/intake.py` — POST /intake/start (SSE questions) + POST /intake/submit
- [x] Registered in `src/api/main.py`
- [x] `main.py` — `--idea` CLI flag added
- [x] `web/src/components/idea/IntakeWizard.tsx` — 4-step wizard UI
- [x] `web/src/app/(dashboard)/idea/page.tsx`
- [x] Tests: `test_intake.py`, `test_requirements_translator.py`, `test_multi_option_designer.py` — 9 new tests
- [x] **428 tests total, all passing**

---

## ✅ Phase 8: Complete — Architecture Memory + Health Score

### Phase 8A — Architecture Memory ✅ COMPLETE

- [x] `src/db/models.py` — `ArchitectureSnapshotRow`, `DecisionHistoryRow` DB tables added
- [x] `src/archon/memory/snapshot.py` — `save_snapshot()`, `get_snapshots()`, `build_memory_context()`
- [x] `src/archon/memory/decisions.py` — `save_decisions()` (ADR-only), `get_decisions()`, `_extract_section()`
- [x] `src/api/routes/memory.py` — `GET /memory/snapshots`, `/decisions`, `/timeline`
- [x] `src/archon/engine/supervisor.py` — `run()` accepts `memory_context: str = ""` injected by jobs worker
- [x] `src/api/services/review_service.py` — `update_review_status()` calls `save_snapshot + save_decisions` on COMPLETED
- [x] `src/tests/test_memory_snapshot.py` — 5 tests
- [x] `src/tests/test_memory_decisions.py` — 4 tests

### Phase 8B — Architecture Health Score ✅ COMPLETE

- [x] `src/db/models.py` — `HealthScoreRow` DB table added
- [x] `src/archon/health/scorer.py` — `compute_health_score()` (0–100, severity penalties, security+cloud 1.5x weighted), `save_health_score()`, `get_score_history()`, `get_latest_score()`
- [x] `src/api/routes/health_score.py` — `GET /health-score/{repo_url:path}/latest` and `/history`
- [x] `src/api/services/review_service.py` — calls `save_health_score()` on COMPLETED
- [x] `web/src/components/health/HealthScoreRing.tsx` — SVG ring (green ≥80 / amber 60-79 / red <60) + domain bars
- [x] `web/src/components/health/ScoreTrendChart.tsx` — pure SVG line chart
- [x] `web/src/app/(dashboard)/health/page.tsx` — health dashboard
- [x] `src/tests/test_health_scorer.py` — 6 tests
- [x] **~443 tests total (~15 new from Phase 8)**

---

## ✅ Phase 9: Complete — MCP Connectors

### Phase 9A — ARCHON as MCP Server ✅ COMPLETE

- [x] `src/archon/mcp/__init__.py`
- [x] `src/archon/mcp/server.py` — 5 MCP tools: `review_repo`, `get_findings`, `ask_architecture`, `get_health_score`, `get_adrs`
- [x] `src/archon/mcp/config.py` — `MCPSettings` (ARCHON_API_URL, ARCHON_API_KEY)
- [x] `mcp_server.py` — entry point (`python mcp_server.py`)
- [x] `mcp_config.json` — Claude Desktop / Cursor config example

### Phase 9B — Inbound MCP Connectors ✅ COMPLETE

- [x] `src/archon/mcp/connectors/__init__.py`
- [x] `src/archon/mcp/connectors/base.py` — `ConnectorContext` model + `MCPConnector` ABC
- [x] `src/archon/mcp/connectors/github_connector.py` — PRs, commit frequency, contributors, tech-debt issues
- [x] `src/archon/mcp/connectors/aws_connector.py` — CloudFormation, Cost Explorer, CloudWatch alarms, Security Hub
- [x] `src/archon/mcp/connectors/slack_connector.py` — HITL Block Kit checkpoints + health digests
- [x] `src/archon/mcp/connector_registry.py` — `fetch_connector_context()` with Redis TTL (1hr)
- [x] `src/api/routes/connectors.py` — GET /connectors, POST /connectors/{name}/fetch, GET /connectors/{name}/context/{repo}
- [x] Registered in `src/api/main.py`

### Phase 9C — Wired into Agent Context ✅ COMPLETE

- [x] `src/api/workers/review_worker.py` — fetches GitHub + AWS connector context before supervisor.run()
- [x] `src/archon/engine/supervisor.py` — accepts `connector_context: str = ""`

### Tests ✅

- [x] `src/tests/test_mcp_server.py` — 6 tests
- [x] `src/tests/test_connectors.py` — 8 tests
- [x] **477 tests total, 89% coverage, 0 warnings**

---

## ✅ Priority 1 — Tests (65% → 80%+) — COMPLETE

**Result: 477 tests, 89% coverage, 0 warnings.**

- [x] `test_supervisor_e2e.py` — full pipeline: 6 agents in → merged ReviewPackage out. Assert ≥ 1 finding per domain, deduplication fires, executive summary generated
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
