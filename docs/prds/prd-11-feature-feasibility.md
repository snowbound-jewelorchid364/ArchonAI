# PRD-11: Feature Feasibility

**Mode:** Feature Feasibility
**Phase:** Phase 3
**Status:** Draft
**Pricing:** Included in Pro and Team plans
**Last updated:** 2026-03-31

---

## 1. One-Line Summary

ARCHON Feature Feasibility answers the question "Can we build X?" — analysing a feature description against the current codebase to produce an effort estimate, risk assessment, architectural impact analysis, and recommended implementation approach with citations.

---

## 2. Problem Statement

**What problem does this solve?**
Engineering leaders and product managers frequently need to answer "can we build X?" under time pressure — before a sales call, a board meeting, or a product planning session. The answer requires understanding both the feature requirements and the current architectural constraints. Getting it wrong in either direction is costly: underestimating leads to blown commitments, overestimating means leaving deals on the table.

**Who experiences this problem?**
- CTOs and engineering leads fielding scoping questions from product, sales, or the board
- Technical founders who need to assess feasibility before committing to a customer or investor
- Engineering leads planning a quarterly roadmap and needing effort estimates for architectural changes

---

## 3. Goals

**30 days:** 10 completed feasibility assessments with at least 65% rated accurate or close to accurate by users
**60 days:** Feature Feasibility becomes the standard pre-planning artefact for Pro and Team plan users
**90 days:** At least 30% of users report the assessment was used in a real planning or sales context

---

## 4. Non-Goals

- **Not a project plan generator** — no Jira tickets, sprint plans, or story points
- **Not a code generator** — ARCHON assesses feasibility, not implementation
- **Not a product requirements tool** — user supplies the feature description; ARCHON does not scope it
- **Does not guarantee effort estimates** — estimates are architectural approximations, not commitments

---

## 5. User Stories

### Happy Path
**As a** CTO being asked "can we add SSO to our product in the next quarter?",
**I want to** run a feasibility assessment against our codebase,
**so that** I can give a grounded answer with supporting evidence rather than a gut estimate.

**Acceptance Criteria:**
```
Given a GitHub repo URL and a feature description (--feature "Add enterprise SSO via SAML 2.0")
When I run ARCHON in feature-feasibility mode
Then ARCHON analyses the codebase with software-architect and integration-architect as leads
And produces a feasibility report within 30 minutes
And the report includes: feasibility verdict (Straightforward / Moderate / Complex / Very Complex), effort estimate, architectural impact, risks, recommended approach, and citations
And the assessment is grounded in actual codebase patterns (auth system, user model, session management)
```

### Edge Case — Feature Conflicts with Existing Architecture
**As a** user assessing a feature that fundamentally conflicts with the current architecture,
**I want to** receive a clear assessment of the refactoring required,
**so that** I understand the true cost of the feature request.

**Acceptance Criteria:**
```
Given a feature that requires significant architectural changes (e.g., adding multi-tenancy to a single-tenant app)
When ARCHON completes the feasibility assessment
Then the report clearly states the architectural prerequisite changes required
And estimates combined effort for both the prerequisite changes and the feature itself
And flags the prerequisite changes as blocking dependencies
```

---

## 6. Functional Requirements

**Must:**
1. Accept `--mode feature-feasibility` with `--repo` and `--feature` (plain-English description) flags
2. Run software-architect and integration-architect as lead agents
3. Complete within 30 minutes
4. Produce a feasibility report with: verdict, effort estimate (days/weeks range), architectural impact summary, top 3 risks, recommended implementation approach, blocking dependencies, citations
5. Ground findings in actual codebase patterns (file references where relevant)
6. Cite every recommended implementation approach
7. Produce partial output if any agent fails

**Should:**
8. Identify quick-win implementation paths if available
9. Flag if the feature requires a dependency not currently in the codebase
10. Estimate the complexity of automated vs manual testing for the feature

**May:**
11. Generate a starter technical design doc outline for the feature
12. Compare 2–3 implementation approaches with trade-off notes

---

## 7. Non-Functional Requirements

- **Performance:** Report in under 30 minutes at p75
- **Reliability:** Partial report always delivered
- **Cost:** Average run cost under $8
- **Accuracy:** Effort estimate within 2x of actual for 70% of assessments (surveyed after implementation)

---

## 8. Success Metrics

**Primary:** At least 65% of users rate the feasibility verdict as accurate or close to accurate
**Secondary:** Completion rate > 90%; median delivery under 20 minutes; 30% of assessments used in real planning contexts

---

## 9. Open Questions

| Question | Owner | Due |
|---|---|---|
| Should effort be expressed as days (1–3d, 1–2w) or complexity tier (S/M/L/XL)? | Product | Phase 3 planning |
| Should Feature Feasibility run all 6 agents or just software + integration for speed? | Engineering | Phase 3 kickoff |
| Should the technical design doc outline be in scope for Phase 3 launch? | Product | Phase 3 planning |

---

## 10. Dependencies and Risks

**Dependencies:** Software-architect + integration-architect agents with feasibility framing; RAG pipeline; 30-minute timeout

**Risks:**

| Risk | Impact | Mitigation |
|---|---|---|
| Effort estimates are consistently off, reducing trust | High | Calibrate on known features; express as ranges not point estimates; survey users post-implementation |
| Feature description is too vague for meaningful analysis | Medium | Warn on short feature descriptions; list assumptions made |
| Blocking dependencies missed, leading to underestimated effort | Medium | Prompt agents to explicitly check for architectural prerequisites |

---

**Complexity:** S-M (similar to Review pipeline; scoped to a single feature)
**Suggested first sprint scope:** Phase 3 mode. Simplest new mode to build — reuse Review pipeline with feature-framing prompt and 30-minute timeout.
