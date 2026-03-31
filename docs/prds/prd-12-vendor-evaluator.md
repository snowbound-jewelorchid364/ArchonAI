# PRD-12: Vendor Evaluator

**Mode:** Vendor Evaluator
**Phase:** Phase 3
**Status:** Draft
**Pricing:** Included in Pro and Team plans
**Last updated:** 2026-03-31

---

## 1. One-Line Summary

ARCHON Vendor Evaluator analyses a technology or vendor choice decision — database, message broker, cloud provider, API gateway, observability platform — against the current codebase and produces a cited, structured evaluation with a recommendation.

---

## 2. Problem Statement

**What problem does this solve?**
Every startup faces recurring technology selection decisions: which database for a new service, which message broker for an event-driven migration, which observability platform to standardise on. These decisions are high-stakes, time-consuming to research properly, and often made based on familiarity or marketing rather than fit with the actual architecture. A wrong vendor choice costs months of migration work.

**Who experiences this problem?**
- Engineering leads evaluating a new database or infrastructure component for a specific workload
- CTOs standardising their technology stack at Series A
- Founders making first-time technology choices for a new product

---

## 3. Goals

**30 days:** 10 completed vendor evaluations with at least 60% rated as useful input to a real technology decision
**60 days:** Vendor Evaluator becomes the standard pre-decision artefact for Pro and Team plan users
**90 days:** At least 3 user testimonials about a technology decision informed by ARCHON Vendor Evaluator

---

## 4. Non-Goals

- **Not a procurement tool** — no pricing negotiation, contract review, or vendor contact
- **Not a benchmark runner** — does not run performance benchmarks against candidates
- **Not a final decision maker** — produces a structured recommendation, not a mandate
- **Does not evaluate every possible vendor** — focuses on the candidates the user specifies

---

## 5. User Stories

### Happy Path
**As an** engineering lead evaluating PostgreSQL vs MongoDB for a new document-heavy service,
**I want to** receive a structured evaluation grounded in my codebase and current architecture,
**so that** I can make a defensible technology decision without spending a week on research.

**Acceptance Criteria:**
```
Given a GitHub repo URL and vendor evaluation context (--evaluate "PostgreSQL vs MongoDB for document storage service")
When I run ARCHON in vendor-evaluator mode
Then ARCHON analyses the codebase and runs relevant specialist agents
And produces an evaluation report within 30 minutes
And the report includes: evaluation criteria, per-candidate assessment, recommendation with rationale, migration effort if switching from current stack, citations
And every major claim about a candidate is cited from a credible source
And the recommendation accounts for both the feature and the existing codebase context
```

---

## 6. Functional Requirements

**Must:**
1. Accept `--mode vendor-evaluator` with `--repo` and `--evaluate` (description of decision) flags
2. Accept optional `--candidates` flag to specify the options being compared
3. Run the most relevant specialist agents based on the evaluation category (data-architect for databases, cloud-architect for infra, integration-architect for messaging, etc.)
4. Complete within 30 minutes
5. Produce an evaluation report with: criteria matrix, per-candidate scoring, recommendation, rationale, migration considerations, citations
6. Cite every major claim about each candidate
7. Ground the recommendation in the current codebase architecture

**Should:**
8. Identify evaluation criteria automatically from the technology category if not supplied
9. Include a migration effort estimate if the recommendation differs from the current stack
10. Flag lock-in risks for the recommended option

**May:**
11. Generate a decision record (ADR) template pre-filled with the evaluation findings
12. Support evaluating more than 2 candidates

---

## 7. Non-Functional Requirements

- **Performance:** Report in under 30 minutes at p75
- **Cost:** Average run cost under $8
- **Citation quality:** Every claim about a candidate has at least one credible citation
- **Neutrality:** Evaluation criteria applied consistently across all candidates

---

## 8. Success Metrics

**Primary:** At least 60% of users rate the recommendation as a useful input to their actual decision
**Secondary:** Completion > 90%; 30% of evaluations result in the recommended option being adopted

---

## 9. Open Questions

| Question | Owner | Due |
|---|---|---|
| Should ARCHON infer candidates from the evaluation description, or require explicit --candidates? | Product | Phase 3 planning |
| Should ADR generation be in scope for Phase 3 launch? | Product | Phase 3 planning |
| How do we handle proprietary vendors with limited public technical documentation? | Engineering | Phase 3 kickoff |

---

## 10. Dependencies and Risks

**Dependencies:** Relevant specialist agents with evaluation framing; Tavily + Exa for vendor documentation and comparison sources; RAG pipeline

**Risks:**

| Risk | Impact | Mitigation |
|---|---|---|
| Evaluation is biased toward well-documented open-source options over proprietary ones | Medium | Explicit criteria consistency check in supervisor; note documentation gaps |
| Recommendation conflicts with existing vendor relationships | Low | Note existing stack context; frame as technical recommendation, not procurement mandate |
| Vendor landscape changes after evaluation | Low-Medium | All recommendations cite sources with dates; advise re-running for time-sensitive decisions |

---

**Complexity:** S-M
**Suggested first sprint scope:** Phase 3 mode. Start with database evaluations only, validate criteria matrix quality before expanding to all technology categories.
