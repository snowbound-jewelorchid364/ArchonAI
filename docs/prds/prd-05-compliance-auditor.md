# PRD-05: Compliance Auditor

**Mode:** Compliance Auditor
**Phase:** Phase 1
**Status:** Draft
**Pricing:** $499 per run
**Last updated:** 2026-03-31

---

## 1. One-Line Summary

ARCHON Compliance Auditor analyses a codebase against a selected compliance framework — SOC 2, HIPAA, GDPR, or PCI-DSS — and produces a gap analysis, remediation roadmap, and evidence-ready findings report grounded in actual code and cited regulatory sources.

---

## 2. Problem Statement

**What problem does this solve?**
Startups pursuing SOC 2 Type II, HIPAA compliance, GDPR readiness, or PCI-DSS certification face a multi-month, expensive process. Most engage a consulting firm or auditor for $20–50k and spend months collecting evidence. The majority of the work is reactive — finding gaps during the audit rather than proactively identifying and closing them before the auditor arrives. ARCHON Compliance Auditor shifts this left: identify gaps against the codebase before the auditor does.

**Who experiences this problem?**
- Founders at B2B SaaS companies pursuing SOC 2 to close enterprise deals
- CTOs at healthtech startups approaching HIPAA compliance for the first time
- Engineering leads at fintech companies preparing for PCI-DSS
- European or global startups handling personal data under GDPR obligations

**How are they solving it today — and why is that insufficient?**
- Manual internal review against a checklist — incomplete, not grounded in code, misses implementation gaps
- Compliance automation tools (Vanta, Drata) — policy-layer only, do not audit the codebase
- External auditors — expensive, slow, find gaps after months of prep
- Generic LLMs — produce policy text but cannot assess actual implementation against requirements

**Cost of NOT solving this:**
Failed audits delay enterprise deals by 3–6 months. Non-compliance findings during due diligence can kill funding rounds. GDPR fines can reach 4% of global annual turnover. HIPAA penalties range from $100 to $50,000 per violation.

---

## 3. Goals

**30 days:** 5 completed compliance audits across at least 2 frameworks with at least 65% rated 4/5 or higher
**60 days:** Compliance Auditor becomes the recommended first step before engaging a formal auditor
**90 days:** At least 2 users report the audit findings helped them pass a formal compliance review faster

---

## 4. Non-Goals

- **Not a formal compliance certification** — ARCHON produces a gap analysis, not a certification or audit report accepted by regulators
- **Not a policy generator** — ARCHON does not write privacy policies or terms of service
- **Not a penetration test** — security findings are based on code analysis and best practices, not active exploitation
- **Not a substitute for a qualified auditor** — ARCHON is a preparation tool, not a replacement for formal audit
- **Does not cover all compliance frameworks at launch** — SOC 2, HIPAA, GDPR, PCI-DSS only in Phase 1

---

## 5. User Stories

### Happy Path
**As a** founder pursuing SOC 2 Type II certification,
**I want to** receive a gap analysis grounded in my actual codebase,
**so that** I can close gaps before my auditor arrives and reduce the time and cost of the formal audit.

**Acceptance Criteria:**
```
Given a GitHub repo URL and a selected compliance framework (SOC 2 / HIPAA / GDPR / PCI-DSS)
When I run ARCHON in compliance-auditor mode
Then ARCHON analyses the codebase with security-architect as lead agent and all 6 contributing
And produces a compliance gap analysis within 60 minutes
And every gap finding is mapped to a specific control or requirement from the selected framework
And each gap includes: control reference, finding description, evidence from codebase, remediation recommendation, effort estimate
And every HIGH or CRITICAL gap has at least one citation from regulatory or authoritative source
```

### Error Case
**As a** user whose compliance audit partially fails,
**I want to** receive findings for the domains that completed,
**so that** I still have actionable gaps to close even with a partial run.

**Acceptance Criteria:**
```
Given a compliance audit run where one or more agents fail
When the failure occurs after at least one agent has completed
Then ARCHON writes a partial compliance report
And clearly labels which control domains are incomplete
And the partial report is actionable for completed domains
```

### Edge Case — Framework Not Explicitly Specified
**As a** user who does not specify a compliance framework,
**I want to** receive a best-effort compliance assessment based on detected data types and patterns,
**so that** ARCHON infers the most relevant framework from the codebase.

**Acceptance Criteria:**
```
Given a repo with no --framework flag supplied
When ARCHON detects patterns suggesting regulated data (PHI, PII, payment card data)
Then ARCHON infers the most likely applicable framework(s) and proceeds
And notes the inferred framework prominently: "Detected: PII handling patterns — assessing against GDPR and SOC 2"
And the user can override the inference in Phase 1 HITL mode
```

### Edge Case — No Regulated Data Detected
**As a** user running compliance audit on a repo with no regulated data patterns,
**I want to** receive a clear assessment that the framework requirements may not apply,
**so that** I do not invest in compliance overhead that is not warranted.

**Acceptance Criteria:**
```
Given a repo with no detectable PII, PHI, or payment data patterns
When ARCHON runs in compliance-auditor mode with HIPAA or PCI-DSS selected
Then ARCHON notes: "No PHI/payment patterns detected — compliance requirement may not apply to this codebase"
And produces a general security posture assessment instead
```

---

## 6. Functional Requirements

**Must:**
1. Must accept `--mode compliance-auditor` with `--repo` and `--framework` (SOC2 / HIPAA / GDPR / PCI-DSS) flags
2. Must infer framework from codebase patterns if `--framework` is not supplied
3. Must run security-architect as lead agent with all 6 agents contributing relevant findings
4. Must map every finding to a specific control reference from the selected framework
5. Must produce a gap analysis report with the following sections:
   - Executive summary (compliance posture rating: Ready / Partially Ready / Not Ready)
   - Control-by-control gap table (control ID, status, finding, evidence, remediation, effort)
   - Critical gaps requiring immediate remediation
   - Remediation roadmap with phased priority ordering
   - Evidence inventory (what exists vs what is missing)
   - Risk register ordered by compliance risk
   - Citations to regulatory and authoritative sources
6. Must require at least one citation per HIGH or CRITICAL gap finding
7. Must include an Evidence Inventory section listing artefacts present vs absent (encryption config, access logs, audit trails, data retention config)
8. Must produce partial output if any agent fails
9. Must never log or quote raw PII, credentials, or sensitive literals from the codebase

**Should:**
10. Should produce a remediation roadmap with phases ordered by audit priority (what auditors check first)
11. Should estimate effort (S/M/L/XL) per gap remediation
12. Should flag quick wins — gaps that can be closed in under 1 week
13. Should note which gaps are likely to be policy-layer vs implementation-layer (differentiating Vanta/Drata scope from ARCHON scope)

**May:**
14. May support multiple frameworks in a single run (e.g., SOC 2 + GDPR overlap analysis)
15. May generate a compliance readiness score as a percentage of controls passing

---

## 7. Non-Functional Requirements

- **Performance:** Full compliance audit completes in under 60 minutes for repos up to 100k LOC at p75
- **Reliability:** Partial report always delivered if at least one agent completes
- **Cost:** Average cost per run stays under $15
- **Control mapping accuracy:** Every finding mapped to a specific, verifiable control reference — no vague mappings
- **Citation quality:** Every CRITICAL gap cites the specific regulatory article, section, or control
- **Security:** Secrets, PII, and PHI detected in codebase are never quoted or logged in output

---

## 8. Success Metrics

**Primary:** At least 65% of users rate the compliance gap analysis 4/5 or higher for usefulness in real compliance prep

**Secondary:**
- Package completion rate greater than 85%
- Median time to package delivery under 50 minutes
- At least 50% of completed runs result in download
- At least 30% of users report closing at least one gap identified by ARCHON within 30 days

**Guard metrics:**
- Zero silent failures
- Zero findings mapped to vague or non-existent control references
- Secrets or PII never appear in generated output

---

## 9. Open Questions

| Question | Owner | Due |
|---|---|---|
| Should compliance posture be rated as a score (0–100) or a categorical rating (Ready / Partially Ready / Not Ready)? | Product | Phase 1 planning |
| Should multi-framework runs (SOC 2 + GDPR) be priced as one run or two? | Product | Phase 1 planning |
| How do we handle framework version differences (e.g., SOC 2 2017 vs current Trust Services Criteria)? | Engineering | Phase 1 kickoff |
| Should ARCHON produce a formatted evidence package for auditors, or just the gap analysis for internal use? | Product | Phase 1 planning |
| What is the boundary between ARCHON's codebase-layer findings and Vanta/Drata policy-layer findings? | Product | Before launch |

---

## 10. Dependencies and Risks

**Dependencies:**
- Security-architect agent with compliance-specific prompts per framework
- Control reference database for SOC 2, HIPAA, GDPR, and PCI-DSS (embedded in prompts or retrieval)
- Tavily + Exa for regulatory source citations
- RAG pipeline for codebase analysis
- Output formatter capable of producing control-mapped gap tables

**Risks:**

| Risk | Impact | Mitigation |
|---|---|---|
| Control mappings are inaccurate or vague, reducing credibility with auditors | Critical — trust damage if used in real audit prep | Ground all control mappings in specific, verifiable framework references; include in prompt |
| Framework inference is wrong, leading to irrelevant gap analysis | High — wasted run | Require explicit confirmation when inferring; warn clearly; allow override |
| Codebase lacks evidence for many controls, producing a mostly-gap report | Medium — low utility if gaps are all assumption-based | Distinguish confirmed gaps from evidence-gap findings; calibrate confidence accordingly |
| Secrets or PII detected in codebase are inadvertently included in output | Critical — security and legal violation | Scrub output; never quote raw sensitive values; test with seeded credentials |
| Compliance frameworks evolve and prompt references go stale | Medium — findings become inaccurate | Pin framework version in prompts; track framework update schedule |

---

**Complexity:** M-L (control mapping logic adds complexity over base Review pipeline)
**Suggested first sprint scope:** Not in Phase 1 — Phase 1 mode. When building: start with SOC 2 only, validate control mapping accuracy against known SOC 2 Trust Services Criteria before adding additional frameworks.
