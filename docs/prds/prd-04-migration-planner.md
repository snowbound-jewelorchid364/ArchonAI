# PRD-04: Migration Planner

**Mode:** Migration Planner
**Phase:** Phase 1
**Status:** Draft
**Pricing:** $499 per run
**Last updated:** 2026-03-31

---

## 1. One-Line Summary

ARCHON Migration Planner produces a cited, phased migration roadmap for teams modernising legacy systems — covering re-architecture strategy, data migration plan, integration re-wiring, cloud lift-and-shift or re-platforming, and risk-ordered execution phases.

---

## 2. Problem Statement

**What problem does this solve?**
Modernising a legacy system is one of the highest-risk engineering projects a startup or scale-up undertakes. Teams need to decide what to migrate, in what order, at what cost, with what risk — and they typically do this without a structured framework. Wrong sequencing causes production incidents. Underestimated data migration complexity causes delays measured in quarters, not weeks.

**Who experiences this problem?**
- Engineering leads at startups that have outgrown a monolith or first-generation architecture
- Teams migrating from one cloud provider to another
- Founders who inherited technical debt from a prior CTO and need a credible remediation plan
- Teams moving from self-managed infrastructure to managed cloud services

**How are they solving it today — and why is that insufficient?**
- Internal planning in spreadsheets — no systematic risk assessment, no citations, no cross-domain view
- Consulting engagements — expensive, slow, often produce a deck with no implementation detail
- Generic LLM advice — not grounded in the actual codebase, no citations, not phased or prioritised

**Cost of NOT solving this:**
Failed or stalled migrations are among the most expensive engineering failures. A poorly sequenced migration can mean months of re-work, data loss risk, production downtime, and team morale damage. The average cost of a failed modernisation project exceeds $500k for a Series A startup.

---

## 3. Goals

**30 days:** 5 completed migration plans with at least 60% rated 4/5 or higher
**60 days:** Establish Migration Planner as the go-to mode for teams at Series A preparing for scale
**90 days:** At least 3 case studies or testimonials demonstrating a migration plan used in production

---

## 4. Non-Goals

- **Not a project management tool** — ARCHON produces a plan, not Jira tickets or Gantt charts
- **Not a migration executor** — no automated migration scripts or data pipeline generation
- **Not a code rewriter** — ARCHON recommends patterns and phases, not refactored code
- **Does not cover database schema migrations in Phase 1** — Phase 1 adds data migration depth
- **Not a cloud cost calculator** — cost estimates are approximate; link to cloud pricing tools

---

## 5. User Stories

### Happy Path
**As an** engineering lead at a startup that has outgrown its monolith,
**I want to** receive a phased migration roadmap grounded in my actual codebase,
**so that** I can sequence the work by risk and value without starting from a blank whiteboard.

**Acceptance Criteria:**
```
Given a GitHub repo URL and optional migration context (target state, constraints, timeline)
When I run ARCHON in migration-planner mode
Then ARCHON analyses the codebase and runs integration + cloud agents as leads, with all 6 contributing
And produces a phased migration plan within 60 minutes
And each phase includes: scope, dependencies, risk rating, estimated effort, rollback strategy
And every major recommendation is cited
And the plan distinguishes between phases that can run in parallel vs must run sequentially
```

### Error Case
**As a** user whose migration plan run partially fails,
**I want to** receive whatever phases were completed,
**so that** I have a starting point for the domains that were analysed.

**Acceptance Criteria:**
```
Given a migration plan run where one or more agents fail
When the failure occurs after at least one agent has completed
Then ARCHON writes a partial migration plan
And clearly labels which domains are missing
And the partial plan is usable for completed domains
```

### Edge Case — Repo Has No Infrastructure Code
**As a** user whose repo contains only application code with no IaC or deployment config,
**I want to** receive a migration plan that acknowledges the infrastructure evidence gap,
**so that** the plan is accurate about what was and was not analysed.

**Acceptance Criteria:**
```
Given a repo with no IaC, Dockerfile, or deployment manifests
When ARCHON runs in migration-planner mode
Then the cloud-architect agent notes the infrastructure evidence gap explicitly
And produces cloud migration recommendations based on application code patterns
And the package includes an "Evidence Gaps" section listing missing artefacts
```

### Edge Case — Multi-Cloud or Hybrid
**As a** user running workloads across two cloud providers,
**I want to** receive a migration plan that addresses the multi-cloud complexity,
**so that** the plan accounts for data gravity, egress costs, and service parity gaps.

**Acceptance Criteria:**
```
Given a codebase with references to multiple cloud provider SDKs or config files
When ARCHON runs in migration-planner mode
Then the cloud-architect agent detects the multi-cloud pattern
And the plan includes a section on consolidation options, trade-offs, and sequencing
```

---

## 6. Functional Requirements

**Must:**
1. Must accept `--mode migration-planner` with `--repo` (GitHub URL) and optional `--target` (target state description) and `--timeline` flags
2. Must run all 6 agents with integration-architect and cloud-architect as lead agents
3. Must produce a phased migration plan with at minimum 2 and at most 5 phases
4. Each phase must include: name, scope, dependencies, risk rating (CRITICAL / HIGH / MEDIUM / LOW), estimated effort (S/M/L/XL), success criteria, rollback strategy
5. Must identify and flag circular dependencies between proposed phases
6. Must produce a risk register sorted by migration phase
7. Must cite every major pattern or technology recommendation
8. Must include a Mermaid diagram showing the proposed target architecture
9. Must include an Evidence Gaps section when key artefacts (IaC, Dockerfile, deployment config) are absent
10. Must produce partial output if any agent fails
11. Must note assumptions made when `--target` is not supplied

**Should:**
12. Should identify the top 3 migration anti-patterns present in the codebase (e.g., shared database, sync-only integrations, hardcoded config)
13. Should include a data migration strategy section covering schema changes, backfill patterns, and dual-write periods
14. Should provide a rough effort estimate for the overall migration (person-weeks)
15. Should flag compliance considerations if codebase handles regulated data types

**May:**
16. May generate a starter IaC skeleton for the target state
17. May produce a stakeholder summary slide deck outline for engineering leadership to present to board or investors

---

## 7. Non-Functional Requirements

- **Performance:** Full migration plan completes in under 60 minutes for repos up to 100k LOC at p75
- **Reliability:** Partial plan always delivered if at least one agent completes
- **Cost:** Average infrastructure and model cost per run stays under $15
- **Phase coherence:** Phases must not contradict each other — supervisor validates dependency ordering before output
- **Citation quality:** Every CRITICAL or HIGH risk migration finding has at least one citation
- **Security:** Repo contents processed in isolated temp storage; deleted after completion

---

## 8. Success Metrics

**Primary:** At least 60% of users rate the migration plan 4/5 or higher for usefulness as a real planning input

**Secondary:**
- Package completion rate greater than 85%
- Median time to package delivery under 50 minutes
- At least 50% of completed runs result in package download
- At least 3 users per month report the plan was used in a real migration decision within 90 days of launch

**Guard metrics:**
- Zero silent failures
- Zero plans with contradictory phase dependencies
- False positive rate on CRITICAL migration risks under 10%

---

## 9. Open Questions

| Question | Owner | Due |
|---|---|---|
| Should phase effort estimates use T-shirt sizes (S/M/L/XL) or person-weeks? | Product | Phase 1 planning |
| Is a 2-phase minimum realistic for trivially simple repos? Should we allow a 1-phase plan? | Product + Engineering | Phase 1 planning |
| Should the IaC skeleton for the target state be in scope for Phase 1 or deferred? | Engineering | Phase 1 kickoff |
| Should Migration Planner accept a `--from` and `--to` cloud provider flag for cloud-to-cloud migrations? | Product | Phase 1 planning |
| How do we handle monorepos with multiple services at different migration maturity stages? | Engineering | Phase 1 |

---

## 10. Dependencies and Risks

**Dependencies:**
- Integration-architect and cloud-architect agents as lead agents with migration-specific prompts
- Strands Agents SDK for parallel orchestration
- RAG pipeline for codebase analysis
- Tavily + Exa for migration pattern and anti-pattern citations
- Supervisor with phase dependency validation logic

**Risks:**

| Risk | Impact | Mitigation |
|---|---|---|
| Phases are sequenced incorrectly causing contradictions | High — plan is unusable | Supervisor validates phase DAG before output; flag cycles as CRITICAL findings |
| Effort estimates are too optimistic, leading to blown timelines | High — trust damage if followed | Label estimates as rough approximations; recommend validation with engineering team |
| Codebase lacks enough evidence to assess migration complexity | Medium — low-confidence plan | Add Evidence Gaps section; lower confidence scores where evidence is thin |
| Two lead agents (integration + cloud) produce conflicting migration strategies | Medium — incoherent plan | Supervisor cross-references domain recommendations and resolves conflicts explicitly |
| Data migration complexity is underestimated in Phase 1 scope | Medium — plan misses a major risk | Flag data migration as a dedicated section; add depth in Phase 1 with data-architect lead |

---

**Complexity:** M
**Suggested first sprint scope:** Not in Phase 1 — Phase 1 mode. When building: reuse Review pipeline with migration-framed prompts for integration + cloud agents. Validate phase DAG logic in supervisor before first release.
