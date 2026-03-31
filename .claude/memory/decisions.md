---
name: ARCHON Decisions
description: Architectural and product decisions log for ARCHON — ADR-style
type: project
---

# ARCHON — Decisions Log

All significant decisions recorded here. Format: decision, context, rationale, alternatives considered.

---

## D001 — Product Name: ARCHON
**Date:** 2026-03-31
**Decision:** Name the product ARCHON
**Rationale:** Greek ἄρχων — ruler, chief magistrate, commander. Implies authority, leadership, decision-making. Short, memorable, fits the architecture domain.
**Tagline:** "Your Frontier AI Architect. From idea to infrastructure."

---

## D002 — Agent Runtime: Strands Agents SDK
**Date:** 2026-03-31
**Decision:** Use Strands Agents SDK (Python, open source by AWS) as the agent runtime
**Rationale:** Same technology stack AWS uses for Frontier Agents. MCP-native. Works with Claude API directly (no Bedrock required). Built-in tools: tavily_search, exa_search, file_read, python_repl, diagram, think, memory, mcp_client.
**Alternatives considered:**
- LangChain/LangGraph — more complex, higher abstraction overhead
- CrewAI — good for prototyping but limited enterprise features
- AutoGen — conversational focus, not task-execution focus
- Custom — too much work for MVP

---

## D003 — LLM: Claude claude-opus-4-6
**Date:** 2026-03-31
**Decision:** Use claude-opus-4-6 for all 6 architect agents
**Rationale:** Best reasoning capability for architecture domain. Cost is justified by output quality ($5–15/review estimated). Architecture decisions require deep reasoning, not speed.
**Risk:** High cost at scale — monitor per-review COGS, switch agents to claude-sonnet-4-6 for research phases if needed.

---

## D004 — Vector Store: pgvector over Qdrant
**Date:** 2026-03-31
**Decision:** Use pgvector extension on PostgreSQL for RAG
**Rationale:** Simpler ops — already in Postgres, no additional service to manage. Sufficient ANN performance for MVP (repos up to 500k LOC). Hybrid search (semantic + keyword) supported via pg_trgm.
**Alternatives considered:**
- Qdrant — better ANN performance at scale, but extra service to deploy
- Pinecone — managed, but cloud dependency and cost
- Chroma — good for dev, not production-grade

---

## D005 — Web Research: Tavily + Exa (both)
**Date:** 2026-03-31
**Decision:** Use both Tavily and Exa search APIs per agent
**Rationale:** Tavily optimised for recency and factual retrieval (good for CVEs, pricing, recent docs). Exa optimised for semantic/neural search (good for architecture patterns, blog posts, papers). Combined = better coverage.
**Alternative:** Tavily only — simpler, cheaper. Revisit at Phase 3.

---

## D006 — Build Order: CLI-first (Phase 1)
**Date:** 2026-03-31
**Decision:** Phase 1 is a CLI script only — no UI, no billing, no HITL
**Rationale:** Proves the core hypothesis (agents produce useful findings) before investing in SaaS infrastructure. Fastest path to validation. If agents produce poor output, nothing else matters.

---

## D007 — Intelligence Stack: 3-Layer Architecture
**Date:** 2026-03-31
**Decision:** Combine Frontier Agent + Perplexity Research + RAG in 3 distinct layers
**Rationale:**
- Frontier Agent layer = autonomy + tool use + session persistence
- Research layer = live web knowledge, no cutoff, citations
- RAG layer = private codebase knowledge, team conventions, past decisions
Each layer compensates for the weaknesses of the others.

---

## D008 — HITL: 4 Checkpoints, 3 Modes
**Date:** 2026-03-31
**Decision:** 4 fixed checkpoints (scope, findings, decisions, final) with 3 modes (Autopilot/Balanced/Supervised)
**Rationale:** Enterprise buyers need control. 4 checkpoints cover all critical decision junctures without being annoying. 3 modes let users choose their comfort level with autonomy.
