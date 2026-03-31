# PRD-09: Scaling Advisor

**Mode:** Scaling Advisor
**Phase:** Phase 2
**Status:** Draft
**Pricing:** Included in Pro and Team plans
**Last updated:** 2026-03-31

---

## 1. One-Line Summary

ARCHON Scaling Advisor analyses a codebase for architectural bottlenecks and produces a prioritised scaling roadmap — identifying the specific patterns, services, and data models that will break first as traffic grows, with concrete recommendations and effort estimates.

---

## 2. Problem Statement

**What problem does this solve?**
Startups hit scaling walls at predictable growth inflection points — 10k users, 100k users, 1M events/day. The patterns that cause failures are well-known (synchronous chains, unindexed queries, single-writer databases, stateful services) but teams only discover them under load. Post-incident scaling fixes are expensive — they require architectural changes under production pressure.

**Who experiences this problem?**
- Engineering leads whose product is growing faster than their architecture was designed for
- CTOs preparing for a marketing campaign, product launch, or seasonal traffic spike
- Founders post-Series A who need to scale from 1k to 100k users without a re-platform

**How are they solving it today — and why is that insufficient?**
- Load testing — finds symptoms but not root causes
- Manual architecture reviews before a launch — incomplete, time-consuming, miss cross-cutting patterns
- Generic LLM advice — not grounded in actual codebase, not prioritised by impact

---

## 3. Goals

**30 days:** 5 completed scaling reports with at least one actionable bottleneck identified per run
**60 days:** Scaling Advisor becomes the pre-launch standard for Pro and Team plan users
**90 days:** At least 3 users report a prevented scaling incident attributable to ARCHON findings

---

## 4. Non-Goals

- **Not a load testing tool** — ARCHON does not generate or run load tests
- **Not a capacity planner** — does not produce infrastructure capacity numbers without IaC context
- **Does not predict exact failure thresholds** — provides risk-ranked bottleneck analysis, not precise failure points
- **Not a performance profiler** — ARCHON analyses architectural patterns, not runtime performance data

---

## 5. User Stories

### Happy Path
**As an** engineering lead preparing for a product launch expected to 10x current traffic,
**I want to** receive a prioritised list of architectural bottlenecks and scaling risks,
**so that** I can fix the most critical issues before the launch rather than during it.

**Acceptance Criteria:**
```
Given a GitHub repo URL and optional --scale (e.g., "10x traffic in 30 days") context
When I run ARCHON in scaling-advisor mode
Then ARCHON analyses the codebase with data-architect and cloud-architect as lead agents
And produces a scaling report within 60 minutes
And the report ranks bottlenecks by: failure severity at target scale, implementation effort, and time to fix
And every bottleneck is grounded in a specific codebase pattern with file references where possible
And every HIGH or CRITICAL bottleneck is cited with a source
```

### Edge Case — No Scale Target Provided
**As a** user who does not know their expected scale,
**I want to** receive a general architectural scaling risk assessment,
**so that** I understand my highest-risk patterns regardless of a specific traffic target.

**Acceptance Criteria:**
```
Given a scaling-advisor run with no --scale flag
When ARCHON produces the report
Then ARCHON assesses general scaling risk for the top 5 most common failure patterns
And notes: "No scale target provided — assessing against common scaling inflection points (10x, 100x)"
```

---

## 6. Functional Requirements

**Must:**
1. Accept `--mode scaling-advisor` with `--repo` and optional `--scale` and `--current-load` flags
2. Run data-architect and cloud-architect as lead agents, all 6 contributing
3. Produce a scaling report with: bottleneck inventory, risk ranking, recommended fixes per bottleneck, effort estimates, and a phased scaling roadmap
4. Ground every bottleneck finding in a codebase pattern or file reference
5. Cite every HIGH/CRITICAL bottleneck finding
6. Produce partial output if any agent fails
7. Distinguish between immediate fixes (pre-launch) and longer-term architectural improvements

**Should:**
8. Identify the single highest-risk bottleneck per domain (the "most likely first failure")
9. Estimate the traffic level at which each bottleneck is likely to become critical (if --current-load provided)
10. Produce a pre-launch checklist of quick wins

**May:**
11. Generate a load test plan outline targeting the identified bottlenecks
12. Produce an infrastructure scaling estimate (compute, database, cache tier sizing) if IaC is present

---

## 7. Non-Functional Requirements

- **Performance:** Full report in under 60 minutes at p75
- **Reliability:** Partial report always delivered
- **Cost:** Average run cost under $12
- **Evidence grounding:** At least 80% of bottleneck findings reference specific codebase patterns
- **Prioritisation:** Bottlenecks sorted by impact-at-scale, not just severity

---

## 8. Success Metrics

**Primary:** At least 65% of users rate the scaling report as useful in pre-launch or scaling planning
**Secondary:** Completion rate > 90%; at least one quick win actioned per run; 3 prevented incidents reported within 90 days

---

## 9. Open Questions

| Question | Owner | Due |
|---|---|---|
| Should --scale accept multipliers (10x) or absolute numbers (100k users/day)? | Product | Phase 2 planning |
| Should Scaling Advisor reuse the last Review RAG index or re-index? | Engineering | Phase 2 kickoff |
| Is a load test plan outline in scope for Phase 2 or Phase 3? | Product | Phase 2 planning |

---

## 10. Dependencies and Risks

**Dependencies:** Data-architect + cloud-architect agents with scaling-framing prompts; RAG pipeline; Tavily + Exa

**Risks:**

| Risk | Impact | Mitigation |
|---|---|---|
| Bottleneck predictions are wrong and team fixes non-issues | Medium | Ground findings in codebase evidence; express as risk probability not certainty |
| No IaC limits cloud scaling recommendations | Medium | Detect IaC absence; focus on application-layer bottlenecks |
| Scale target is unrealistic, producing irrelevant recommendations | Low | Cap analysis at 1000x; note if target seems unrealistic |

---

**Complexity:** M
**Suggested first sprint scope:** Phase 2 mode. Reuse Review pipeline with scaling-framing prompts and data + cloud as lead agents.
