# ARCHON — New Features Roadmap

**Created:** 2026-04-01
**Updated:** 2026-04-01
**Status:** Planned — not yet built
**Vision:** Anyone with a product idea — engineer or not — can get a complete architecture.

---

## 0. Input Formats + Multimodal

ARCHON accepts any form of input a founder or engineer naturally has. No technical preparation required.

### 0.1 Input Format Table

| # | Input Format | Who Uses It | How ARCHON Uses It | Library / API |
|---|---|---|---|---|
| 1 | **Natural language text** | Everyone | Idea Mode intake, conversational design | Existing |
| 2 | **Voice / speech** | Non-engineers, founders | Speak your product idea → transcribed → Idea Mode | OpenAI Whisper (free, open source) |
| 3 | **Image — sketch / wireframe** | Designers, founders | Extracts UI flows, features, component structure | Claude Vision API |
| 4 | **Image — whiteboard photo** | Engineering teams | Reads architecture diagram, converts to C4 | Claude Vision API |
| 5 | **Image — AWS Console screenshot** | Engineers, DevOps | Security architect reads live infra config visually | Claude Vision API |
| 6 | **Image — existing diagram (PNG/SVG)** | CTOs, architects | Ingests draw.io / Miro / Lucidchart exports as context | Claude Vision API |
| 7 | **PDF — business plan / PRD** | Founders, PMs | Extracts product requirements, features, constraints | pymupdf (open source) |
| 8 | **PDF — compliance report** | CTOs, compliance | Feeds Compliance Auditor + Security Architect agents | pymupdf (open source) |
| 9 | **PDF — vendor / tech evaluation** | Engineering leads | Feeds Vendor Evaluator mode | pymupdf (open source) |
| 10 | **Figma URL** | Designers, founders | Extracts screens, components, user flows as product context | Figma REST API (free) |
| 11 | **Website URL** | Non-engineers | Scrapes product to understand features — "build something like X" | httpx + BeautifulSoup (free) |
| 12 | **GitHub repo URL** | Engineers | Full codebase RAG — existing flow | Existing |
| 13 | **OpenAPI / Swagger file** | Backend engineers | Integration Architect reads API contracts | pyyaml / json (free) |
| 14 | **Terraform / IaC file** | DevOps, cloud engineers | Cloud Architect reads live infra definition | HCL parser (open source) |
| 15 | **Database schema (SQL dump)** | Backend engineers | Data Architect reads schema, finds N+1s, missing indexes | sqlparse (open source) |
| 16 | **Video — Loom / screen recording** | Engineering leads | Extracts architecture walkthrough knowledge | OpenAI Whisper (audio) + Claude Vision (frames) |
| 17 | **ZIP / folder upload** | Everyone | Direct file upload instead of GitHub URL | zipfile (stdlib) |

---

### 0.2 Multimodal Combinations

Users can combine multiple inputs in one session. ARCHON merges all context before running agents.

| Combination | Use Case |
|---|---|
| Voice + Figma URL | Non-engineer describes idea while sharing design |
| PDF (PRD) + GitHub repo | PM's requirements + engineer's codebase reviewed together |
| Whiteboard photo + website URL | Early-stage founder: sketch + competitor reference |
| AWS Console screenshot + Terraform file | Cloud audit with both visual and code evidence |
| OpenAPI spec + database schema | Integration + data architecture review without full codebase |
| Voice + sketch image | Earliest possible stage — idea on napkin |

---

### 0.3 Input Processing Pipeline

```
Any Input Format
      │
      ▼
┌─────────────────────────────────────┐
│  Input Normaliser                   │
│                                     │
│  Voice    → Whisper → text          │
│  Image    → Claude Vision → text    │
│  PDF      → pymupdf → text          │
│  Figma    → Figma API → text        │
│  Website  → scraper → text          │
│  Code     → RAG chunker → vectors   │
│  IaC/SQL  → parser → structured     │
└─────────────────────────────────────┘
      │
      ▼
Unified context object → all 6 agents
```

All inputs normalise to a unified context. Agents don't need to know the source format.

---

### 0.4 Libraries (All Free / Open Source)

| Library | Purpose | Install |
|---|---|---|
| OpenAI Whisper | Voice → text transcription | `uv add openai-whisper` |
| Claude Vision API | Image understanding | Existing Anthropic SDK |
| pymupdf | PDF → text + images | `uv add pymupdf` |
| BeautifulSoup4 | Website scraping | `uv add beautifulsoup4` |
| httpx | HTTP requests for scraping | Existing |
| sqlparse | SQL schema parsing | `uv add sqlparse` |
| python-hcl2 | Terraform HCL parsing | `uv add python-hcl2` |
| pyyaml | OpenAPI / YAML parsing | `uv add pyyaml` |

---

## 1. Output Formats (Free / Open Source Only)

All formats are zero-cost. Build in priority order.

| # | Format | Library | Effort | Impact |
|---|---|---|---|---|
| 1 | Shareable web link | Existing DB + Next.js | S | ⭐⭐⭐⭐⭐ |
| 2 | Self-contained HTML | Mermaid.js CDN (free) | S | ⭐⭐⭐⭐⭐ |
| 3 | GitHub Issues | GitHub API (free) | S | ⭐⭐⭐⭐ |
| 4 | PDF export | WeasyPrint (open source) | S | ⭐⭐⭐⭐ |
| 5 | GitHub ADR commit | GitHub API (free) | S | ⭐⭐⭐⭐ |
| 6 | SVG diagrams | mermaid-cli (open source) | S | ⭐⭐⭐ |
| 7 | Slack webhook digest | Slack incoming webhooks (free) | S | ⭐⭐⭐ |
| 8 | JSON / YAML export | pyyaml (open source) | XS | ⭐⭐⭐ |

### 1.1 Shareable Web Link
- Public URL: `archon.ai/share/{token}`
- No login required to view
- Full interactive report with filterable findings
- `share_token` already in DB schema — just needs Next.js page `/share/[token]`
- "Run your own review" CTA at bottom → acquisition channel

### 1.2 Self-Contained HTML Export
- Single `.html` file — open in any browser, no server needed
- Embedded CSS + JS + findings + diagrams
- Mermaid.js loaded from CDN for diagram rendering
- Filterable findings by severity and domain
- Dark/light mode, print-ready CSS
- **File:** `src/archon/output/html_exporter.py`

### 1.3 PDF Export (WeasyPrint)
- Executive summary page: health score, top 3 risks, cost impact, dollar figures
- Full findings with file + line references
- ADRs and citations included
- `uv add weasyprint` — no cloud service needed
- **File:** `src/archon/output/pdf_exporter.py`

### 1.4 SVG Diagrams
- Render Mermaid `.mmd` files to proper `.svg` using `mermaid-cli`
- `npm install -g @mermaid-js/mermaid-cli` (free)
- Fall back to raw `.mmd` if CLI not installed
- Embeddable in HTML, PDF, Confluence, Notion, email
- **File:** `src/archon/output/svg_renderer.py`

### 1.5 GitHub Issues Integration
- Push every HIGH+ finding as a GitHub Issue
- Labels: severity + domain (e.g. `critical`, `security`)
- Body includes: file, line, recommendation, citations, link back to review
- Uses existing `GITHUB_TOKEN` from `.env`
- GitHub API free tier: 5,000 req/hour
- **File:** `src/archon/output/github_issues.py`

### 1.6 GitHub ADR Commit
- Commit all ADRs to `/docs/adr/` in the user's repo
- Commit message: `docs: add ADRs from ARCHON review {date}`
- ADRs become permanent part of codebase history
- Uses existing `GITHUB_TOKEN` from `.env`
- **File:** `src/archon/output/github_adr.py`

### 1.7 Slack Webhook Digest
- User pastes Slack incoming webhook URL in settings
- Triggered after every review + optionally on weekly schedule
- Block Kit format: health score, critical count, top finding, link to full report
- Free on all Slack plans
- **File:** `src/archon/output/slack_notifier.py`

### 1.8 JSON / YAML Export
- Serialize `ReviewPackage` Pydantic model to JSON (already works via `model_dump_json`)
- Add YAML via `pyyaml` (`uv add pyyaml`)
- Machine-readable — developers can process findings programmatically
- **File:** `src/archon/output/yaml_exporter.py`

### 1.9 CLI Flags (wire all formats into main.py)
```bash
python main.py --repo URL --mode review --format html
python main.py --repo URL --mode review --format pdf
python main.py --repo URL --mode review --format json
python main.py --repo URL --mode review --github-issues
python main.py --repo URL --mode review --github-adrs
python main.py --repo URL --mode review --slack-webhook https://hooks.slack.com/...
```

---

## 2. Architecture Design Improvements

Expand Design Mode (Mode 2) from a one-shot document generator into a real design tool.

### 2.1 Multi-Option Design
- Generate 3 architecture options per design run: Lean / Scalable / Enterprise-ready
- Each option has: cost estimate, team size, timeline, trade-offs, ADRs, IaC, risk register
- User picks the option that fits their constraints
- New output section: `options-comparison.md` — side-by-side matrix

### 2.2 Constraint Solver
- Intake form before design starts (CLI flags or API fields):
  ```
  --budget 1500           # monthly cloud budget in USD
  --team-size 3           # number of engineers
  --compliance hipaa      # compliance requirements
  --timeline 8            # weeks to MVP
  --scale-y1 5000         # users year 1
  --scale-y2 50000        # users year 2
  ```
- All 6 agents receive constraints and design within them
- Cloud architect won't recommend Kubernetes on a $1,500/month budget
- Output includes: constraint validation (can this actually be built with these constraints?)

### 2.3 Progressive C4 Design (Checkpoint-Driven)
- Design top-down through 4 C4 levels, one checkpoint per level
- Level 1 — System Context: who uses it, what it connects to
- Level 2 — Container View: services, databases, APIs → user approves
- Level 3 — Component View: internal structure of each container → user approves
- Level 4 — Code/Schema: data models, API contracts, IaC → user approves
- User can stop at any level

### 2.4 Architecture Spec Format (archon-spec.yaml)
- Structured, versioned, machine-readable canonical output
- All other formats (HTML, PDF, diagrams) rendered from this spec
- Versionable in git, diffable, queryable by Architecture Chat
- Schema:
  ```yaml
  version: "1.0"
  mode: design
  constraints: { budget_monthly, team_size, compliance, timeline_weeks }
  architecture:
    options: [ { id, name, cost_monthly, services, adrs, risks } ]
  findings: [ { id, severity, domain, title, file, line, recommendation, citations } ]
  adrs: [ { id, title, status, decision, rationale, citations } ]
  ```

---

## 3. Core Product Expansions

### 3.1 Architecture Chat
- Conversational interface grounded in review findings + codebase RAG + web search
- Available after any review — ask anything about the architecture
- Examples:
  - *"How would adding real-time features affect our DB setup?"*
  - *"What's the blast radius if the auth service goes down?"*
  - *"Should we use Kafka or SQS for this use case?"*
- Every answer cites sources
- Reuses existing RAG + Claude adapter infrastructure
- **New:** `src/archon/engine/chat.py` — chat session manager
- **New:** `/api/reviews/{id}/chat` — POST endpoint

### 3.2 Architecture Memory
- Persistent knowledge graph per org — ARCHON remembers every review and decision
- Re-reviews reference history: *"In March 2025 you chose PostgreSQL — that decision is now creating a bottleneck"*
- Architecture timeline: visual history of how the system evolved
- Decision memory: why you chose X over Y, 18 months ago
- Regression detection: *"this ADR was violated in last week's PRs"*
- **New DB tables:** `architecture_snapshots`, `decision_history`

### 3.3 Architecture Health Score
- Continuous 0–100 score broken down across 6 domains
- Computed after every review, stored as a time series
- Weekly trend charts on the dashboard
- Alert rules: *"notify me if security score drops below 70"*
- Weekly Slack/email digest: score + what changed + what improved
- **New:** `src/archon/engine/health_scorer.py`
- **New:** `/api/reviews/{id}/health` endpoint

### 3.4 Team Collaboration
- Assign findings to engineers (with Slack/email notification)
- Comment threads on individual findings
- Finding status: Open → In Progress → Resolved
- One-click export to GitHub Issues, Linear, Jira
- Team activity feed on dashboard
- Unlocks Team ($499/month) and Enterprise tiers
- **New DB tables:** `finding_assignments`, `finding_comments`, `finding_status`

---

## 4. MCP Connectors

Strands Agents SDK is already MCP-native. Connectors add live data to agent context.

### 4.1 ARCHON as MCP Server
Expose ARCHON capabilities as MCP tools — callable from Cursor, Claude Desktop, any MCP client.

```python
archon.review_repo(url, mode)     # trigger a review
archon.get_findings(severity)     # query findings
archon.ask_architecture(question) # architecture chat
archon.get_health_score()         # current health score
archon.get_adrs()                 # list all ADRs
```

**File:** `src/archon/mcp/server.py`

### 4.2 Inbound MCP Connectors (agents pull live data)

| Connector | Free Tier | Data for Agents |
|---|---|---|
| **GitHub MCP** | ✅ Free | PR history, commit patterns, code ownership |
| **AWS MCP** | ✅ Free | CloudFormation, Cost Explorer, CloudWatch, Security Hub |
| **Slack MCP** | ✅ Free | HITL approvals direct in Slack |
| **Terraform Cloud MCP** | ✅ Free tier | Live IaC state, drift detection |
| **Datadog MCP** | Free tier | APM traces, error rates, p99 latency |
| **PagerDuty MCP** | Free tier | Incident history, MTTR, recurring failures |
| **Snyk MCP** | ✅ Free tier | Live CVEs in dependencies |
| **Linear MCP** | ✅ Free tier | Tech debt tickets, open bugs |

### 4.3 Build Order
1. ARCHON as MCP Server (highest reach, reuses existing infrastructure)
2. GitHub MCP connector (extends existing GitHub reader)
3. AWS MCP connector (most impactful for finding quality)
4. Slack MCP connector (HITL approvals in Slack)

---

## 5. Required Features — Master List

Based on the "Idea to Architecture" vision: anyone with a product idea, engineer or not, gets a complete architecture.

### Input Formats (Phase 6)
- [ ] Voice input — OpenAI Whisper → text transcription
- [ ] Image input — Claude Vision API (sketches, whiteboards, AWS Console, diagrams)
- [ ] PDF ingestion — pymupdf (business plans, PRDs, compliance reports)
- [ ] Figma URL — Figma REST API (screens + user flows as context)
- [ ] Website URL — httpx + BeautifulSoup scraper ("build something like X")
- [ ] OpenAPI / Swagger file — pyyaml parser
- [ ] Terraform / IaC file — python-hcl2 parser
- [ ] Database schema (SQL dump) — sqlparse
- [ ] ZIP / folder upload — zipfile stdlib
- [ ] Multimodal combiner — merge all input types into unified context object
- [ ] `src/archon/input/` — new module: normaliser + parsers per format

### Output Formats (Phase 6)
- [ ] Shareable web link — `/share/{token}` Next.js page
- [ ] Self-contained HTML export — Mermaid CDN, filterable findings
- [ ] PDF export — WeasyPrint
- [ ] GitHub Issues — HIGH+ findings as tickets
- [ ] GitHub ADR commit — ADRs to `/docs/adr/`
- [ ] Slack webhook digest — Block Kit health score + findings
- [ ] JSON / YAML export — pyyaml

### Idea Mode + Design (Phase 7)
- [ ] Idea Mode (Mode 15) — natural language idea → architecture, no repo needed
- [ ] Conversational intake — 5-6 plain product questions (no jargon)
- [ ] Requirements translator — product answers → technical constraints (silent)
- [ ] Multi-option design — 3 options: Lean / Scalable / Enterprise with constraints
- [ ] Plain English output renderer — findings without jargon, decisions explained simply
- [ ] Visual architecture map — interactive color-coded SVG, click → findings
- [ ] "What to build first" plan — week-by-week prioritised build sequence

### Intelligence (Phase 8)
- [ ] Architecture Chat — conversational Q&A grounded in findings + RAG + web search
- [ ] Architecture Memory — persistent knowledge graph per org, remembers all decisions
- [ ] Architecture Health Score — 0–100 across 6 domains, weekly digest, alert rules

---

## 6. Implementation Plan

### Phase 6 — Input + Output Formats
- [ ] `src/archon/input/` — new module
  - [ ] `voice_transcriber.py` — Whisper
  - [ ] `image_analyser.py` — Claude Vision
  - [ ] `pdf_reader.py` — pymupdf
  - [ ] `figma_reader.py` — Figma API
  - [ ] `website_scraper.py` — httpx + BeautifulSoup
  - [ ] `iac_parser.py` — python-hcl2
  - [ ] `schema_parser.py` — sqlparse
  - [ ] `api_spec_parser.py` — pyyaml
  - [ ] `input_normaliser.py` — merges all inputs to unified context
- [ ] `src/archon/output/html_exporter.py`
- [ ] `src/archon/output/pdf_exporter.py`
- [ ] `src/archon/output/github_issues.py`
- [ ] `src/archon/output/slack_notifier.py`
- [ ] `src/archon/output/yaml_exporter.py`
- [ ] Wire into `package_assembler.py` + `main.py`
- [ ] `web/app/share/[token]/page.tsx`

### Phase 7 — Idea Mode + Design
- [ ] `src/archon/engine/modes/idea_mode.py` — Mode 15
- [ ] `src/archon/engine/intake.py` — conversational question engine
- [ ] `src/archon/engine/requirements_translator.py` — product → technical
- [ ] Multi-option design (3 options with constraints)
- [ ] Plain English renderer in `formatter.py`
- [ ] Interactive visual map (D3.js or Cytoscape.js — free)
- [ ] "What to build first" section in output

### Phase 8 — Intelligence
- [ ] `src/archon/engine/chat.py` — chat session manager
- [ ] `/api/reviews/{id}/chat` — POST endpoint
- [ ] `src/archon/memory/` — knowledge graph per org
- [ ] `src/archon/engine/health_scorer.py` — 0-100 score
- [ ] Dashboard: health score trend charts

### Phase 9 — MCP
- [ ] ARCHON as MCP Server
- [ ] GitHub MCP connector
- [ ] AWS MCP connector
- [ ] Slack MCP connector

---

## Copilot Prompt — Phase 6 (Output Formats)

```
@workspace Read NEWFEATURES.md Section 1 "Output Formats".

Implement all 8 output formats. Read src/archon/output/ first to understand
the existing output pipeline and src/archon/core/models/review_package.py
for the data model.

Build in this order:
1. src/archon/output/html_exporter.py — self-contained HTML with Mermaid CDN
2. src/archon/output/pdf_exporter.py — WeasyPrint (uv add weasyprint)
3. src/archon/output/svg_renderer.py — shell to mmdc, fall back to .mmd
4. src/archon/output/github_issues.py — GitHub API, HIGH+ findings as issues
5. src/archon/output/github_adr.py — commit ADRs to /docs/adr/
6. src/archon/output/slack_notifier.py — Block Kit webhook message
7. src/archon/output/yaml_exporter.py — pyyaml serialization

Then:
8. Update src/archon/output/package_assembler.py — add format param
9. Update main.py — add --format, --github-issues, --github-adrs, --slack-webhook flags
10. Add /share/[token] page in web/app/share/[token]/page.tsx

Write tests for each exporter. Run pytest after each file.
```
