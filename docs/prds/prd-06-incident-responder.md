# PRD-06: Incident Responder

**Mode:** Incident Responder
**Phase:** Phase 1
**Status:** Draft
**Pricing:** $299 per run
**Last updated:** 2026-03-31

---

## 1. One-Line Summary

ARCHON Incident Responder gives engineering teams a fast, structured architectural triage report during or immediately after a P0/P1 production incident — identifying likely root cause categories, blast radius, immediate mitigations, and post-incident architectural fixes grounded in the codebase.

---

## 2. Problem Statement

**What problem does this solve?**
During a production incident, engineering teams are under extreme time pressure. They need to quickly answer three questions: what broke, why it broke, and how to stop it happening again. Most teams have excellent runbooks for known failure modes but struggle with novel incidents where the failure crosses multiple system boundaries. The architectural root cause is often only identified weeks later during a postmortem.

**Who experiences this problem?**
- On-call engineers and engineering leads at startups with limited senior architectural coverage
- CTOs who need to quickly communicate blast radius and mitigation to stakeholders during an incident
- Founding teams without a dedicated SRE function who are handling their first major production incident

**How are they solving it today — and why is that insufficient?**
- Scrolling through logs and dashboards in parallel — siloed, slow, misses cross-system patterns
- Calling in senior engineers or architects — not always available at 3am, expensive on-call burn
- Post-incident only analysis — useful but arrives too late to minimize MTTR
- Generic LLMs during incidents — not grounded in the actual codebase, no architectural context

**Cost of NOT solving this:**
Extended MTTR directly translates to revenue loss, customer churn, and SLA breach penalties. For a SaaS with $1M ARR, every hour of downtime typically costs $1,100–$2,700 in direct revenue impact. Architectural blind spots during incidents also increase the risk of data loss.

---

## 3. Goals

**30 days:** 5 completed incident triage reports with at least 60% rated useful during or after an actual incident
**60 days:** Incident Responder becomes a standard tool in on-call runbooks for at least 3 ARCHON customers
**90 days:** Measurable MTTR reduction reported by at least 2 users who ran Incident Responder during a live incident

---

## 4. Non-Goals

- **Not a log analysis tool** — ARCHON does not ingest live logs, metrics, or traces
- **Not an alerting or monitoring system** — ARCHON does not replace Datadog, PagerDuty, or Grafana
- **Not a real-time system** — ARCHON analyses the codebase at rest, not live system state
- **Not an automated remediation tool** — ARCHON recommends actions, it does not execute them
- **Not a root cause determination tool** — ARCHON identifies likely architectural root cause categories, not definitive RCA
- **Not a postmortem writer** — postmortem document generation is out of scope for Phase 1

---

## 5. User Stories

### Happy Path
**As an** on-call engineering lead during a P1 database connectivity incident,
**I want to** run ARCHON against my repo with incident context and receive architectural triage guidance,
**so that** I can quickly identify likely root cause categories and stop the bleeding faster.

**Acceptance Criteria:**
```
Given a GitHub repo URL and incident context (--incident "database connections exhausted, auth service degraded")
When I run ARCHON in incident-responder mode
Then ARCHON analyses the codebase with software-architect and cloud-architect as lead agents
And produces an incident triage report within 30 minutes
And the report includes: likely root cause categories, blast radius assessment, immediate mitigations, architectural fixes
And every mitigation recommendation is grounded in the actual codebase (referencing real files and patterns)
And every architectural fix recommendation is cited
```

### Error Case
**As a** user running Incident Responder while other systems are under load,
**I want to** receive a partial triage report if some agents fail,
**so that** I still have actionable guidance even with a degraded run.

**Acceptance Criteria:**
```
Given an incident responder run where one or more agents fail
When the failure occurs after at least one agent has completed
Then ARCHON writes a partial triage report
And labels it as partial with clear indication of which domains are missing
And the partial report is immediately actionable for completed domains
```

### Edge Case — Vague Incident Description
**As a** user who can only provide a brief incident description (e.g., "site is down"),
**I want to** receive a broad architectural risk triage rather than a targeted analysis,
**so that** ARCHON is still useful when I do not have time to characterise the incident fully.

**Acceptance Criteria:**
```
Given a very short or vague --incident description (under 20 words)
When ARCHON runs in incident-responder mode
Then ARCHON produces a broad-coverage triage covering the top 5 highest-risk architectural patterns in the codebase
And notes: "Incident context is limited — producing broad architectural risk triage"
And avoids confidently attributing root cause without sufficient context
```

### Edge Case — No Recent Code Changes
**As a** user investigating an incident on a codebase with no recent commits,
**I want to** receive architectural analysis focused on known risk patterns rather than recent change impact,
**so that** the analysis is still relevant even when the incident is not change-induced.

**Acceptance Criteria:**
```
Given a codebase with no commits in the past 30 days
When ARCHON runs in incident-responder mode
Then ARCHON does not produce findings anchored to "recent changes"
And focuses on persistent architectural risk patterns (connection pooling, retry logic, circuit breakers, etc.)
```

---

## 6. Functional Requirements

**Must:**
1. Must accept `--mode incident-responder` with `--repo` and `--incident` (plain-English description) flags
2. Must accept optional `--severity` flag (P0 / P1 / P2) to calibrate analysis depth and urgency framing
3. Must run software-architect and cloud-architect as lead agents, all 6 contributing
4. Must complete within 30 minutes (stricter than standard 60-minute limit — incidents are time-sensitive)
5. Must produce a triage report with the following sections:
   - Incident summary (restated)
   - Likely root cause categories (top 3, ranked by probability)
   - Blast radius assessment (which systems are likely affected and why)
   - Immediate mitigations (actions takeable in the next 30 minutes)
   - Architectural fixes (changes to prevent recurrence, phased by urgency)
   - Risk register for the incident context
   - Citations for recommended patterns and fixes
6. Must ground all findings in actual codebase patterns (file references where possible)
7. Must require citations for every architectural fix recommendation
8. Must produce partial output if any agent fails — incidents cannot wait for retries
9. Must not produce false-confidence definitive RCA — findings are candidate causes, not confirmed causes
10. Must never log or expose secrets, credentials, or sensitive config from the codebase

**Should:**
11. Should identify the specific code patterns most likely contributing to the described incident (e.g., missing connection pool limits, no circuit breaker, synchronous external calls in hot path)
12. Should estimate recovery time for each recommended immediate mitigation (e.g., "config change — 5 minutes", "deploy fix — 20 minutes")
13. Should flag if the incident pattern suggests a data loss risk requiring immediate action
14. Should identify if the incident is likely infrastructure-layer vs application-layer vs integration-layer

**May:**
15. May generate a draft postmortem skeleton in Phase 2
16. May integrate with incident management tools (PagerDuty, OpsGenie) in Phase 3

---

## 7. Non-Functional Requirements

- **Performance:** Triage report completes in under 30 minutes — hard limit for incident use case
- **Reliability:** Partial report always delivered; never block on a single agent failure
- **Cost:** Average cost per run stays under $10 (faster run = lower cost)
- **Grounding quality:** At least 80% of immediate mitigations reference specific codebase patterns or files
- **Confidence calibration:** Root cause findings must be expressed as candidate causes, not definitive RCA
- **Security:** Never log, quote, or expose secrets, tokens, or credentials found in codebase

---

## 8. Success Metrics

**Primary:** At least 60% of users rate the triage report as useful during or immediately after an actual incident

**Secondary:**
- Report completion rate (within 30-minute limit) greater than 90%
- Median time to report delivery under 20 minutes
- At least 50% of completed runs result in at least one immediate mitigation actioned
- At least 2 documented cases of measurable MTTR reduction within 90 days of launch

**Guard metrics:**
- Zero reports delivered after 30 minutes without warning
- Zero cases of false-confidence definitive RCA
- Zero secrets or credentials in generated output

---

## 9. Open Questions

| Question | Owner | Due |
|---|---|---|
| Should Incident Responder have a hard 30-minute timeout that terminates agents, or a soft warning at 20 minutes? | Engineering | Phase 1 kickoff |
| Should the triage report be optimised for on-call engineer (technical depth) or CTO/stakeholder (executive summary)? Or both? | Product | Phase 1 planning |
| Should we allow `--incident` to accept a URL to a PagerDuty or Opsgenie alert? | Product | Phase 2 planning |
| Should Incident Responder run fewer agents (software + cloud only) for speed, or all 6 in parallel? | Engineering | Phase 1 kickoff |
| How do we handle repos where the relevant service is a subdirectory of a monorepo? | Engineering | Phase 1 |

---

## 10. Dependencies and Risks

**Dependencies:**
- Software-architect and cloud-architect agents with incident-triage framing prompts
- Strands Agents SDK with 30-minute hard timeout per agent
- RAG pipeline for fast codebase retrieval
- Tavily + Exa for mitigation and fix citations
- Supervisor with incident-context injection

**Risks:**

| Risk | Impact | Mitigation |
|---|---|---|
| Report takes longer than 30 minutes during an active incident | Critical — unusable during the incident it is designed for | Hard 20-minute timeout per agent; partial output always delivered; supervisor completes with available findings |
| Overconfident RCA leads team down wrong diagnostic path | High — extends MTTR | Frame all findings as candidate causes; require confidence score per finding; prohibit definitive RCA language in prompts |
| Codebase is outdated vs production (stale default branch) | Medium — analysis misses recent changes | Warn if last commit > 30 days; recommend using latest branch |
| Team under incident stress mis-interprets findings | Medium — wrong action taken | Write immediate mitigations in imperative, unambiguous language; include effort estimates |
| Incident Responder run itself consumes engineering attention needed for the incident | Low-Medium — distraction risk | Optimize for fast time-to-first-finding; allow background run while team investigates live |

---

**Complexity:** M (speed constraint is the key differentiator from Review mode)
**Suggested first sprint scope:** Not in Phase 1 — Phase 1 mode. When building: start with software-architect + cloud-architect only (faster), validate 30-minute completion on 5 test repos before adding all 6 agents.
