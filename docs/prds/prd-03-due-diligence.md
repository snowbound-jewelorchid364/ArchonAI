# PRD-03: Due Diligence Responder

**Mode:** Due Diligence Responder
**Phase:** Phase 1
**Status:** Draft
**Pricing:** $999 per run
**Last updated:** 2026-03-31

---

## 1. One-Line Summary

ARCHON Due Diligence Responder gives founders and engineering leaders a fast, evidence-backed technical diligence package they can use with investors, acquirers, enterprise buyers, or internal stakeholders without spinning up a week-long consulting project.

---

## 2. Problem Statement

**What problem does this solve?**
Startups routinely face technical diligence requests during fundraising, M&A, enterprise procurement, and board review. They need to explain architecture quality, security posture, scalability risk, cloud maturity, and AI/data readiness quickly and credibly. Most teams do not have a principal architect or staff engineer available to prepare a defensible response package on short notice.

**Who experiences this problem?**
- Founders preparing for investor or acquirer diligence
- CTOs and engineering leads answering enterprise customer security and architecture reviews
- Startup teams needing a structured technical narrative for external audiences

**How are they solving it today — and why is that insufficient?**
- Pulling together ad hoc docs, dashboards, and diagrams manually — slow, inconsistent, incomplete
- Hiring consultants — expensive and too slow for time-sensitive diligence cycles
- Asking generic LLMs — lacks repo grounding, citations, and audience-specific structure
- Reusing outdated internal docs — often stale and disconnected from the current codebase

**Cost of NOT solving this:**
Weak diligence responses delay deals, reduce trust, create avoidable follow-up questions, and can materially impact fundraising outcomes, customer procurement, or acquisition valuation. The cost is not just engineering time; it is deal risk.

---

## 3. Goals

**30 days:** 5 completed due diligence packages with at least 60% rated 4/5 or higher for usefulness
**60 days:** 50% of users who run Due Diligence Responder report using the output in a real external diligence process
**90 days:** Due Diligence Responder becomes the highest-value paid one-off mode with at least $3k in mode-specific revenue

---

## 4. Non-Goals

- **Not legal advice** — ARCHON supports technical diligence, not legal diligence
- **Not a formal security certification** — it informs diligence responses but does not replace SOC 2, ISO 27001, or a third-party audit
- **Not a sales collateral generator** — output is evidence-driven, not marketing copy
- **Not a substitute for human review** — founders and engineering leaders still own the final narrative
- **Phase 1 has no polished web workflow** — this mode is engine-first before full SaaS UI maturity in Phase 2

---

## 5. User Stories

### Happy Path
**As a** founder preparing for investor diligence,
**I want to** submit my GitHub repo and receive a structured technical diligence package,
**so that** I can answer architecture, security, and scalability questions with credible evidence instead of scrambling across docs and Slack threads.

**Acceptance Criteria:**
```
Given a valid GitHub repo URL and optional diligence context
When I run ARCHON in due-diligence mode
Then ARCHON analyzes the codebase with all 6 specialist agents in parallel
And produces a single diligence package within 60 minutes
And the package includes strengths, material risks, evidence gaps, and remediation priorities
And every HIGH or CRITICAL finding includes a citation
And the executive summary is readable by a non-IC stakeholder such as an investor, buyer, or enterprise evaluator
```

### Error Case
**As a** user whose diligence run partially fails,
**I want to** receive a partial but clearly labeled package,
**so that** I still have usable material for time-sensitive external conversations.

**Acceptance Criteria:**
```
Given a due diligence run where one or more agents fail
When the failure occurs after at least one agent has completed
Then ARCHON writes a partial diligence package
And clearly labels the output as partial with agent completion status
And identifies which evidence areas are incomplete
And exits with a non-zero status code
And does not discard completed findings
```

### Edge Case
**As a** user whose repo lacks infrastructure code, documentation, or deployment config,
**I want to** receive a diligence package that distinguishes confirmed evidence from missing evidence,
**so that** the output remains credible and does not overstate confidence.

**Acceptance Criteria:**
```
Given a repo with limited operational or infrastructure evidence
When ARCHON completes the diligence run
Then the package includes an explicit "Evidence Gaps" section
And findings that rely on incomplete evidence are marked with lower confidence
And ARCHON does not infer production practices without support from code or cited sources
```

---

## 6. Functional Requirements

**Must:**
1. Must accept a GitHub repo URL or local repo path as input
2. Must accept optional diligence context including company stage, deployment scale, buyer/investor context, and any custom diligence questions
3. Must run all 6 specialist agents in parallel with due-diligence framing
4. Must ground findings in the codebase via RAG and supplement with Tavily + Exa research where relevant
5. Must produce a single diligence package with these core sections:
   - Executive summary
   - Strengths
   - Material risks
   - Evidence gaps
   - Remediation priorities
   - Domain sections for software, cloud, security, data, integration, and AI
6. Must distinguish between "confirmed in codebase" and "recommended based on best practice"
7. Must require citations for every HIGH or CRITICAL finding
8. Must include confidence scoring per finding or per section
9. Must deliver partial output if any agent fails
10. Must reject repos exceeding 500k LOC with a clear error message and guidance to scope the run
11. Must avoid exposing secrets, tokens, or raw sensitive literals in the output package
12. Must preserve an audit trail of model version, prompt version, and run timestamp in package metadata

**Should:**
13. Should allow users to provide a custom diligence question set as input
14. Should generate a stakeholder-friendly executive summary that avoids unnecessary implementation detail
15. Should allow rerunning only failed agents to complete a partial package
16. Should support exporting both markdown and package ZIP artifacts

**May:**
17. May support audience-specific output variants such as investor-facing, acquirer-facing, or enterprise customer-facing
18. May support branded exports for enterprise and advisor workflows

---

## 7. Non-Functional Requirements

- **Performance:** Full diligence package completes in under 60 minutes for repos up to 100k LOC at p75
- **Reliability:** Partial package is always delivered if at least one agent completes
- **Cost:** Average infrastructure and model cost per run stays under $20
- **Evidence quality:** Every CRITICAL finding includes code evidence or a high-quality citation; every HIGH finding includes at least one citation
- **Clarity:** Executive summary must be understandable by non-engineering stakeholders within 5 minutes of reading
- **Security:** Repo contents are processed in isolated temp storage and deleted after completion; secrets are never logged or quoted verbatim in output

---

## 8. Success Metrics

**Primary:** At least 60% of users rate the diligence package 4/5 or higher for usefulness in an external diligence process

**Secondary:**
- Package completion rate greater than 85%
- Median time to package delivery under 45 minutes
- At least 70% of completed runs result in package download or export
- At least 50% of users report the package reduced diligence prep time by 50% or more

**Guard metrics (must not degrade):**
- Zero silent failures
- False positive rate on CRITICAL findings under 10%
- No leakage of secrets or raw credentials in generated output

---

## 9. Open Questions

| Question | Owner | Due |
|---|---|---|
| Should Due Diligence Responder require a user-supplied audience type, or default to a generic diligence package? | Product | Before Phase 1 build |
| What is the right confidence rubric for evidence gaps vs confirmed risks? | Product + Engineering | Before Phase 1 build |
| Should custom diligence questionnaires be free-form text, markdown, or a structured template? | Product | Phase 1 |
| What output format is required first for paid usage: markdown only, or markdown plus PDF/ZIP? | Product | Before launch |
| Should this mode reuse Review findings internally and reformat them, or run a distinct prompt chain optimized for external stakeholders? | Engineering | Before implementation |

---

## 10. Dependencies and Risks

**Dependencies:**
- Strands Agents SDK for agent orchestration
- Anthropic API access for the chosen frontier model
- Tavily and Exa API keys for web research
- RAG indexing pipeline with repo chunking and retrieval
- Package formatter capable of producing stakeholder-readable output

**Risks:**

| Risk | Impact | Mitigation |
|---|---|---|
| Output sounds too technical for investors or procurement stakeholders | High — package is less usable in real diligence | Add audience-aware executive summary and plain-language synthesis in supervisor |
| Repo lacks enough operational evidence to support claims | High — low confidence or misleading output | Add explicit Evidence Gaps section and lower confidence scoring |
| Hallucinated or weakly supported strengths make the package less credible | High — trust damage in external diligence | Require evidence tags and citations for all material claims |
| Model and search API cost exceed assumptions | Medium — margins degrade on one-off pricing | Benchmark on 3 representative repos and cap research depth by mode |
| Agent failure during high-stakes runs creates incomplete packages | Medium — poor experience under time pressure | Persist partial outputs, retry failed agents, clearly label incompleteness |

---

**Complexity:** M
**Suggested first sprint scope:** Reuse Review pipeline with a distinct supervisor prompt and external-audience package formatter. Start with software, security, and cloud agents end-to-end, then expand to all 6 once package structure is validated.
