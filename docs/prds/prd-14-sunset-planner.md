# PRD-14: Sunset Planner

**Mode:** Sunset Planner
**Phase:** Phase 3
**Status:** Draft
**Pricing:** Included in Pro and Team plans
**Last updated:** 2026-03-31

---

## 1. One-Line Summary

ARCHON Sunset Planner produces a safe, sequenced decommission plan for a legacy service, feature, or integration — mapping dependencies, data migration requirements, consumer impact, and a zero-downtime retirement sequence.

---

## 2. Problem Statement

**What problem does this solve?**
Decommissioning a legacy service is as hard as building a new one, and teams consistently underestimate it. The failure mode is predictable: a service that "should be simple to remove" turns out to have 12 undocumented consumers, 3 years of production data with no migration path, and a hard dependency from a critical payment flow. The result is either a stalled decommission or a production incident.

**Who experiences this problem?**
- Engineering leads removing a legacy monolith service by service as part of a modernisation
- Founders decommissioning a first-generation feature that has been replaced by a newer implementation
- Teams retiring a third-party integration that is being replaced by a different vendor

---

## 3. Goals

**30 days:** 5 completed sunset plans with at least 60% rated as useful in a real decommission project
**60 days:** Sunset Planner becomes the standard first step before any decommission project
**90 days:** At least 2 users report a zero-incident decommission using an ARCHON sunset plan

---

## 4. Non-Goals

- **Not a code deletion tool** — ARCHON produces a plan, not automated removal scripts
- **Not a data migration executor** — identifies data migration requirements, does not run migrations
- **Does not guarantee completeness** — dependency maps are based on static analysis; runtime dependencies may be missed
- **Not a project plan** — no Jira tickets or sprint assignments

---

## 5. User Stories

### Happy Path
**As an** engineering lead planning to decommission a legacy notification service,
**I want to** receive a comprehensive dependency map and sequenced sunset plan,
**so that** I can retire the service safely without causing a production incident.

**Acceptance Criteria:**
```
Given a GitHub repo URL and sunset target (--sunset "legacy-notification-service")
When I run ARCHON in sunset-planner mode
Then ARCHON analyses the codebase with integration-architect and data-architect as leads
And produces a sunset plan within 60 minutes
And the plan includes: dependency map, consumer inventory, data migration requirements, zero-downtime retirement sequence, rollback triggers, and risk register
And every dependency is grounded in actual codebase evidence
And every HIGH or CRITICAL risk is cited
```

### Edge Case — Target Service Has No Clear Boundaries
**As a** user trying to sunset a feature embedded in a monolith (not a discrete service),
**I want to** receive a plan that accounts for the embedded nature of the target,
**so that** the plan is realistic about the surgical extraction required.

**Acceptance Criteria:**
```
Given a sunset target that is not a discrete service but an embedded feature
When ARCHON analyses the codebase
Then ARCHON identifies the code paths, data models, and consumers associated with the target feature
And the plan includes an extraction phase before decommission
And clearly notes: "Target is embedded in monolith — extraction required before decommission"
```

### Edge Case — Production Data Has No Clear Retention Path
**As a** user sunsetting a service with 3 years of production data and no clear retention requirement,
**I want to** receive guidance on data disposition options,
**so that** I do not accidentally delete data that is needed for compliance or audit purposes.

**Acceptance Criteria:**
```
Given a sunset target whose database or data store has no clear retention or migration path
When ARCHON produces the sunset plan
Then the data section includes: data inventory, retention options (archive / migrate / delete), compliance considerations, and a recommended disposition
And flags any data types that may have regulatory retention requirements
```

---

## 6. Functional Requirements

**Must:**
1. Accept `--mode sunset-planner` with `--repo` and `--sunset` (target service, feature, or integration name) flags
2. Run integration-architect and data-architect as lead agents
3. Produce a sunset plan with: dependency map, consumer inventory, data migration requirements, retirement sequence (phased), rollback triggers per phase, risk register, citations
4. Ground all dependency findings in codebase evidence
5. Flag runtime dependencies that cannot be detected via static analysis
6. Complete within 60 minutes
7. Produce partial output if any agent fails
8. Include compliance considerations for data with regulatory retention requirements

**Should:**
9. Identify a safe "dark launch" strategy — disabling the service without removing it first
10. Estimate effort for each sunset phase (S/M/L/XL)
11. Identify quick validation steps to confirm the service is safe to remove
12. Flag any consumers that are external (third-party APIs, partners) vs internal

**May:**
13. Generate a communication template for notifying internal consumers of the sunset timeline
14. Produce a post-sunset verification checklist

---

## 7. Non-Functional Requirements

- **Performance:** Full plan in under 60 minutes at p75
- **Reliability:** Partial plan always delivered
- **Cost:** Average run cost under $12
- **Dependency completeness:** Clearly distinguish statically-detected from potentially-missed runtime dependencies

---

## 8. Success Metrics

**Primary:** At least 60% of users rate the sunset plan as useful in a real decommission project
**Secondary:** Completion rate > 90%; at least 2 zero-incident decommissions reported within 90 days; 30% of plans result in a discovered dependency not previously known to the team

---

## 9. Open Questions

| Question | Owner | Due |
|---|---|---|
| Should --sunset accept a file path as well as a service/feature name? | Engineering | Phase 3 kickoff |
| How do we handle runtime dependency detection gaps — warning only, or suggest dynamic tracing tools? | Product | Phase 3 planning |
| Should the communication template for consumer notification be in scope for Phase 3? | Product | Phase 3 planning |

---

## 10. Dependencies and Risks

**Dependencies:** Integration-architect + data-architect agents with decommission-framing prompts; RAG pipeline for dependency graph analysis; Tavily + Exa for decommission pattern citations

**Risks:**

| Risk | Impact | Mitigation |
|---|---|---|
| Static analysis misses runtime dependencies, causing production incident | Critical | Clearly warn about static analysis limits; recommend dynamic tracing validation before execution |
| Data disposition recommendation leads to accidental deletion of regulated data | Critical | Always flag potential regulatory retention requirements; recommend legal/compliance review for data decisions |
| Sunset plan is too conservative, leaving dead code in production indefinitely | Low | Balance safety with decisiveness; provide "confidence level" per dependency finding |
| Target is too broadly defined (e.g., "sunset authentication") to produce a useful plan | Medium | Validate target specificity; warn if target is ambiguous; ask for scoping in Phase 1 HITL |

---

**Complexity:** M-L (dependency graph analysis is the hardest part)
**Suggested first sprint scope:** Phase 3 mode. Start with discrete service targets only (not embedded features). Validate dependency map accuracy on 3 known-decommissioned services before general release.
