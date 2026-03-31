# PRD-13: Onboarding Accelerator

**Mode:** Onboarding Accelerator
**Phase:** Phase 3
**Status:** Draft
**Pricing:** Included in Team plan
**Last updated:** 2026-03-31

---

## 1. One-Line Summary

ARCHON Onboarding Accelerator generates a comprehensive architecture orientation package for a new CTO, VP of Engineering, or senior hire — explaining the existing system, its key decisions, its strengths and risks, and a suggested 30/60/90-day architectural agenda.

---

## 2. Problem Statement

**What problem does this solve?**
When a new technical leader joins a startup, they spend their first 4–8 weeks trying to understand the existing architecture. This is expensive: the new hire's time is spent on discovery instead of leadership, and the existing team spends hours giving context that is never written down. A new CTO who misreads the codebase makes poor early decisions that compound.

**Who experiences this problem?**
- Incoming CTOs and VPs of Engineering joining startups
- Founding teams onboarding their first senior technical hire
- Lead engineers joining a new team and needing to get up to speed fast

---

## 3. Goals

**30 days:** 5 completed onboarding packages with at least 70% rated as accelerating architectural understanding
**60 days:** Onboarding Accelerator becomes part of the standard hiring process for Team plan customers
**90 days:** Average time to architectural competence reduced by at least 2 weeks for users who received an ARCHON onboarding package

---

## 4. Non-Goals

- **Not an HR onboarding tool** — covers technical architecture only, not company culture, org structure, or processes
- **Not a code walkthrough** — produces an architectural narrative, not a line-by-line tour
- **Not a team assessment** — does not evaluate the engineering team, only the codebase and architecture
- **Does not replace human onboarding** — accelerates but does not replace 1:1 context transfer

---

## 5. User Stories

### Happy Path
**As a** new CTO joining a 20-person startup,
**I want to** receive a comprehensive architecture orientation package based on the actual codebase,
**so that** I can understand the current system, its key decisions, and its risks in my first week rather than my first month.

**Acceptance Criteria:**
```
Given a GitHub repo URL and optional context (--role "New CTO" --context "Joining a Series A B2B SaaS company")
When I run ARCHON in onboarding-accelerator mode
Then ARCHON analyses the codebase with all 6 specialist agents in explanatory mode
And produces an onboarding package within 60 minutes
And the package includes: architecture narrative, key technology decisions and their rationale, system strengths, current risks and debt, domain-by-domain overview, and a suggested 30/60/90-day architectural agenda
And the narrative is written for a senior technical leader, not an IC engineer
And every major claim is grounded in the codebase with file references
```

### Edge Case — Minimal Documentation in Repo
**As a** user running Onboarding Accelerator on a repo with no ADRs, READMEs, or inline comments,
**I want to** receive an architecture narrative inferred from the code itself,
**so that** the package is useful even when documentation is absent.

**Acceptance Criteria:**
```
Given a repo with minimal documentation
When ARCHON runs in onboarding-accelerator mode
Then ARCHON infers architectural decisions from code patterns and structure
And notes: "Documentation is limited — architecture narrative inferred from codebase analysis"
And clearly distinguishes inferred decisions from documented ones
```

---

## 6. Functional Requirements

**Must:**
1. Accept `--mode onboarding-accelerator` with `--repo` and optional `--role` and `--context` flags
2. Run all 6 agents in explanatory (not diagnostic) mode — focus on understanding, not gap-finding
3. Produce an onboarding package with: architecture narrative, key decision log (inferred ADRs), system map, strengths, risks and debt, domain overviews, suggested 30/60/90-day agenda
4. Write for a senior technical audience (CTO/VP Eng level), not IC engineers
5. Ground the narrative in codebase patterns and file structure
6. Complete within 60 minutes
7. Produce partial output if any agent fails

**Should:**
8. Generate a visual system map (Mermaid diagram) showing key service and data boundaries
9. Produce an inferred ADR log for the top 5–7 architectural decisions visible in the code
10. Highlight the 3 highest-priority risks to address in the first 90 days

**May:**
11. Produce a "questions to ask the team" section — gaps in understanding that require human context
12. Support a `--compare` flag to compare two repos (e.g., before/after a migration)

---

## 7. Non-Functional Requirements

- **Performance:** Full package in under 60 minutes at p75
- **Tone:** Narrative must be readable by a senior non-IC technical leader (no excessive implementation detail)
- **Accuracy:** Inferred decisions must be clearly labelled as inferred; never presented as confirmed
- **Cost:** Average run cost under $15

---

## 8. Success Metrics

**Primary:** At least 70% of users rate the package as accelerating architectural understanding by at least 1 week
**Secondary:** Completion rate > 90%; package download rate > 80%; 30% reduction in onboarding ramp time reported by users at 90-day survey

---

## 9. Open Questions

| Question | Owner | Due |
|---|---|---|
| Should the 30/60/90-day agenda be generic or inferred from the specific risks found? | Product | Phase 3 planning |
| Should "questions to ask the team" section be in scope for Phase 3 launch? | Product | Phase 3 planning |
| Should Onboarding Accelerator write more positively than Review mode (less gap-focused, more narrative)? | Product | Phase 3 kickoff |

---

## 10. Dependencies and Risks

**Dependencies:** All 6 agents with explanatory-mode prompts; supervisor with narrative synthesis capability; Mermaid diagram generator

**Risks:**

| Risk | Impact | Mitigation |
|---|---|---|
| Narrative is too technical for a non-IC CTO | High | Tune prompts for senior leadership audience; test with non-engineer readers |
| Inferred ADRs are wrong, misleading new hire | High | Label all inferred decisions clearly; recommend validation with founding team |
| Package is too long to be useful in first week | Medium | Enforce executive summary first; paginate by domain; suggest 30-min sections |

---

**Complexity:** M
**Suggested first sprint scope:** Phase 3 mode. Reuse Review pipeline with explanatory framing. Add narrative synthesis layer in supervisor — distinct from diagnostic merge used in Review mode.
