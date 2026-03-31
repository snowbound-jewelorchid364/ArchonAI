# ARCHON Phase 1 — Architecture

**Goal:** Prove the core hypothesis — 6 agents + RAG + web research → useful architecture findings.

This document describes Phase 1 only. The full SaaS architecture is in [ARCHITECTURE.md](../../ARCHITECTURE.md).

---

## Phase 1 Scope

Phase 1 is a **CLI script** that produces a flat markdown review file. No web app, no API server, no auth, no billing, no Docker, no PostgreSQL, no Redis.

```bash
python main.py --repo https://github.com/user/repo --output archon-review.md
# or
python main.py --describe "FastAPI monolith, 3 services, deployed on AWS ECS" --output archon-review.md
```

---

## Phase 1 Directory Structure

```
archon/
├── main.py                          ← CLI entry point
├── pyproject.toml                   ← uv project: all deps
├── .env.example                     ← Required API keys
├── .env                             ← Local secrets (gitignored)
│
├── agents/
│   ├── __init__.py
│   ├── base.py                      ← BaseArchitectAgent (shared Strands setup)
│   ├── software_architect.py        ← App patterns, NFRs, ADRs
│   ├── cloud_architect.py           ← AWS/GCP/Azure, IaC, FinOps
│   ├── security_architect.py        ← Zero-trust, IAM, compliance
│   ├── data_architect.py            ← Data strategy, governance
│   ├── integration_architect.py     ← EDA, microservices, APIs
│   └── ai_architect.py              ← ML/AI, RAG, agentic
│
├── prompts/
│   ├── software_architect.md        ← System prompt for software-architect
│   ├── cloud_architect.md           ← System prompt for cloud-architect
│   ├── security_architect.md        ← System prompt for security-architect
│   ├── data_architect.md            ← System prompt for data-architect
│   ├── integration_architect.md     ← System prompt for integration-architect
│   ├── ai_architect.md              ← System prompt for ai-architect
│   └── supervisor.md                ← System prompt for team-architecture
│
├── supervisor/
│   ├── __init__.py
│   ├── orchestrator.py              ← Fan-out 6 agents, collect results
│   └── merger.py                    ← Deduplicate + merge findings
│
├── rag/
│   ├── __init__.py
│   ├── fetcher.py                   ← Clone/read GitHub repo files
│   ├── chunker.py                   ← Split files into chunks
│   └── store.py                     ← In-memory vector store (Phase 1)
│
├── research/
│   ├── __init__.py
│   ├── tavily.py                    ← Tavily search wrapper
│   ├── exa.py                       ← Exa search wrapper
│   └── pipeline.py                  ← Combined research pipeline
│
├── output/
│   ├── __init__.py
│   ├── models.py                    ← Pydantic: Finding, Citation, Artifact
│   └── formatter.py                 ← Findings → markdown report
│
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── test_chunker.py
    │   ├── test_merger.py
    │   ├── test_formatter.py
    │   └── test_research_pipeline.py
    └── integration/
        └── test_full_review.py      ← End-to-end with mock APIs
```

---

## Phase 1 RAG Strategy

**Decision:** In-memory vector store using `sentence-transformers` (no database required).

```
GitHub Repo URL
      ↓
rag/fetcher.py        ← Clone repo (or use GitHub API for small repos)
      ↓
rag/chunker.py        ← Split files into 512-token chunks
                         Language-aware splitting (tree-sitter for Python/JS/Go)
                         Fallback: line-based splitting for other languages
      ↓
rag/store.py          ← Generate embeddings (sentence-transformers/all-MiniLM-L6-v2)
                         Store in numpy array (in-memory, no DB)
                         Cosine similarity search at query time
      ↓
Agent context         ← Top-10 chunks injected per agent query
```

**Why no pgvector in Phase 1:**
- pgvector requires PostgreSQL — adds infrastructure dependency before validating agents
- In-memory store is sufficient for a single CLI run (repo not persisted between runs)
- Phase 1 goal is to validate agent quality, not production RAG performance

**Upgrade path:** Replace `rag/store.py` with pgvector in Phase 1 — the `search()` interface stays the same.

---

## Phase 1 Output Format

Phase 1 produces a **single flat markdown file** (`archon-review.md`):

```markdown
# ARCHON Architecture Review
**Repository:** https://github.com/user/repo
**Date:** 2026-03-31
**Agents:** software-architect, cloud-architect, security-architect, data-architect, integration-architect, ai-architect

---

## Executive Summary
[2-3 paragraph summary from supervisor]

---

## Critical Findings (CRITICAL + HIGH)
[Consolidated list across all agents]

---

## Software Architecture
[software-architect findings]

## Cloud Architecture
[cloud-architect findings]

## Security Architecture
[security-architect findings]

## Data Architecture
[data-architect findings]

## Integration Architecture
[integration-architect findings]

## AI Architecture
[ai-architect findings — omitted if no AI/ML in codebase]

---

## Architecture Decision Records
[All ADRs in sequence]

---

## Terraform Skeleton
[IaC skeleton if cloud resources identified]

---

## Risk Register
| ID | Domain | Severity | Title | Recommendation |
|---|---|---|---|---|

---

## Citations
[All web sources used]
```

**Phase 2 upgrade:** Explode the flat file into nested package directories (`adrs/`, `terraform/`, `diagrams/`).

---

## Phase 1 Execution Flow

```python
# main.py pseudocode

async def main(repo_url: str, output_path: str):
    # 1. Ingest
    files = await fetch_repo(repo_url)
    chunks = chunk_files(files)
    store = build_vector_store(chunks)

    # 2. Build context
    context = ReviewContext(
        repo_url=repo_url,
        store=store,
        file_tree=extract_file_tree(files),
        tech_signals=detect_technologies(files)
    )

    # 3. Run 6 agents in parallel
    results = await asyncio.gather(
        SoftwareArchitectAgent().review(context),
        CloudArchitectAgent().review(context),
        SecurityArchitectAgent().review(context),
        DataArchitectAgent().review(context),
        IntegrationArchitectAgent().review(context),
        AIArchitectAgent().review(context),
        return_exceptions=True
    )

    # 4. Handle failures
    findings = [r for r in results if isinstance(r, AgentFindings)]
    errors = [r for r in results if isinstance(r, Exception)]
    log_errors(errors)

    # 5. Merge + format
    merged = merge_findings(findings)
    report = format_markdown(merged)

    # 6. Write output
    Path(output_path).write_text(report)
    print(f"Review complete: {output_path}")
    print(f"Findings: {len(merged.findings)} | Citations: {len(merged.citations)}")
```

---

## Phase 1 Dependencies

```toml
# pyproject.toml
[project]
name = "archon"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "strands-agents>=0.1.0",
    "strands-agents-tools>=0.1.0",
    "anthropic>=0.40.0",
    "sentence-transformers>=3.0.0",
    "numpy>=1.26.0",
    "pydantic>=2.6.0",
    "python-dotenv>=1.0.0",
    "gitpython>=3.1.40",
    "tree-sitter>=0.23.0",
    "tree-sitter-python>=0.23.0",
    "tree-sitter-javascript>=0.23.0",
    "click>=8.1.7",
    "rich>=13.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-mock>=3.12.0",
    "ruff>=0.3.0",
]
```

---

## Phase 1 Environment Variables

Minimum required to run:

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
EXA_API_KEY=...
GITHUB_TOKEN=ghp_...          # For private repos (optional for public)
```

No database, no Redis, no Clerk, no Stripe needed.

---

## Phase 1 Success Criteria

The phase is complete when:

1. `python main.py --repo https://github.com/strands-agents/sdk` produces `archon-review.md`
2. The review contains ≥ 4 agent reports (all 6 attempted, ≥ 4 complete)
3. At least 1 finding per agent, with ≥ 1 citation per finding
4. At least 1 ADR generated
5. Runtime < 20 minutes
6. Total Claude API cost < $5 per run
