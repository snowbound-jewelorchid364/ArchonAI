# PRD-02: Design Mode

**Mode:** Design
**Phase:** Phase 1
**Status:** Draft
**Pricing:** Included in all plans (Starter: 3 runs/month, Pro: unlimited, Team: unlimited)
**Last updated:** 2026-03-31

---

## 1. One-Line Summary

ARCHON Design Mode takes a plain-English product brief and produces a complete, cited, production-ready architecture blueprint — covering software patterns, cloud infrastructure, security posture, data strategy, integration design, and AI/ML systems — in under an hour.

---

## 2. Problem Statement

**What problem does this solve?**
Solo founders and early engineering leads starting a new product face a blank-slate architecture problem. They know what they want to build but not how to build it well at scale. A wrong early decision — wrong database, wrong service boundary, wrong auth strategy — compounds into months of rework. Getting it right from the start requires breadth that no single engineer has.

**Who experiences this problem?**
- Solo founders starting a new SaaS, API product, or platform
- Small engineering teams (1–5 engineers) about to begin a greenfield build
- Engineering leads designing a new service or product line within an existing company

**How are they solving it today — and why is that insufficient?**
- Asking generic LLMs (ChatGPT, Claude) — output is plausible but not cited, not grounded in a real brief, and not validated against production patterns
- Copying architecture from blog posts — often dated, not tailored to their constraints
- Hiring a consultant — too slow and expensive for a pre-seed or seed-stage decision
- Skipping it entirely — the most common outcome; debt begins on day 1

**Cost of NOT solving this:**
Architectural mistakes made at greenfield stage are the most expensive to fix. A wrong database choice, a monolith that should have been modular, or an auth system that cannot support enterprise SSO typically costs 3–6 months of re-platforming at Series A.

---

## 3. Goals

**30 days:** 10 completed design packages with at least 65% rated 4/5 or higher for usefulness
**60 days:** Design Mode becomes the #1 mode by run volume (most users start with a new idea)
**90 days:** At least 30% of Design Mode users return within 30 days to run a Review on their implementation

---

## 4. Non-Goals

- **Not a code generator** — ARCHON produces architecture blueprints, not working code
- **Not a project manager** — no sprint plans, no task breakdown, no story points
- **Not a requirements elicitor** — user must supply a brief; ARCHON does not interview the user interactively in Phase 1
- **Not a tech stack picker for trivial apps** — Design Mode is calibrated for production systems, not todo-list tutorials
- **Phase 1 HITL checkpoints are out of scope for Phase 1** — full checkpoint workflow ships in Phase 1

---

## 5. User Stories

### Happy Path
**As a** solo founder starting a new SaaS product,
**I want to** provide a plain-English brief and receive a complete architecture blueprint,
**so that** I can start building with confidence and avoid costly early mistakes.

**Acceptance Criteria:**
```
Given a plain-English product brief (50–500 words) describing the product, scale, and constraints
When I run ARCHON in design mode
Then ARCHON runs all 6 specialist agents in parallel with prescriptive framing
And produces a complete architecture package within 60 minutes
And every major technology recommendation is cited with a source
And the package covers software patterns, cloud infra, security, data, integration, and AI/ML
And recommendations distinguish between "required for launch" and "recommended for scale"
```

### Error Case
**As a** user whose design run partially fails,
**I want to** receive a partial blueprint rather than nothing,
**so that** I still have a starting point even when one domain is incomplete.

**Acceptance Criteria:**
```
Given a design run where one or more agents fail
When the failure occurs after at least one agent has completed
Then ARCHON writes a partial design package
And clearly labels incomplete domains with agent failure status
And the partial package is still usable for the completed domains
And the CLI exits with a non-zero status code indicating partial completion
```

### Edge Case — Vague Brief
**As a** user who provides a very short or vague brief (under 30 words),
**I want to** receive a warning and still get a best-effort design,
**so that** I understand the output quality is limited by brief quality.

**Acceptance Criteria:**
```
Given a brief under 30 words or containing no technology or scale constraints
When ARCHON runs in design mode
Then ARCHON emits a warning: "Brief is short — design quality improves with more context"
And proceeds with best-effort assumptions
And notes assumptions explicitly in the package (e.g., "Assumed: SaaS web app, < 10k users at launch")
```

### Edge Case — AI/ML-Heavy Brief
**As a** founder building an AI-first product,
**I want to** receive specific AI/ML architecture recommendations,
**so that** I don't default to naive patterns that won't scale.

**Acceptance Criteria:**
```
Given a brief that mentions AI, ML, LLM, RAG, embeddings, or model serving
When ARCHON runs in design mode
Then the ai-architect agent produces findings specific to the AI/ML components described
And recommends model serving strategy, RAG pipeline design, or training infrastructure as appropriate
And cites current best-practice sources for the recommended patterns
```

---

## 6. Functional Requirements

**Must:**
1. Must accept a plain-English product brief via `--brief "..."` flag (CLI) or text input (web UI)
2. Must accept optional constraint flags: `--budget`, `--scale`, `--cloud`, `--compliance`
3. Must run all 6 specialist agents in parallel with prescriptive / greenfield framing (distinct from Review mode diagnostic framing)
4. Must generate a complete architecture package with the following sections:
   - Executive summary
   - Recommended architecture overview
   - Software architecture (patterns, module structure, NFRs)
   - Cloud architecture (IaC skeleton, compute, networking, cost model at 3 scales)
   - Security architecture (zero-trust design, IAM, encryption, compliance readiness)
   - Data architecture (schema design, storage strategy, governance)
   - Integration architecture (API design, event patterns, third-party integrations)
   - AI/ML architecture (if relevant to brief)
   - Risk register
   - Citations
5. Must distinguish between launch requirements and scale recommendations in every domain section
6. Must cite every major technology recommendation with at least one source
7. Must include a Terraform skeleton covering core infrastructure resources
8. Must include at least one Mermaid diagram (system context or container view) in the package
9. Must produce partial output if any agent fails
10. Must note explicit assumptions made when brief is vague or incomplete

**Should:**
11. Should generate a cost estimate at three scales: launch, 10k users, 100k users
12. Should include alternative technology options with trade-off notes for major decisions
13. Should flag compliance considerations if the brief mentions regulated industries or data types
14. Should allow rerunning only failed agents to complete a partial package

**May:**
15. May support interactive brief refinement in Phase 1 HITL mode
16. May generate a starter ADR set covering the top 3–5 architectural decisions

---

## 7. Non-Functional Requirements

- **Performance:** Full design package completes in under 60 minutes for any valid brief at p75
- **Reliability:** Partial package always delivered if at least one agent completes
- **Cost:** Average infrastructure and model cost per run stays under $15
- **Citation quality:** Every major technology recommendation includes at least one citation from a credible source
- **Assumption transparency:** All assumptions made due to brief vagueness are stated explicitly
- **Security:** No user brief content is logged beyond metadata; briefs are not used for model training

---

## 8. Success Metrics

**Primary:** At least 65% of users rate the design package 4/5 or higher for usefulness as a starting architecture

**Secondary:**
- Package completion rate greater than 90%
- Median time to package delivery under 45 minutes
- At least 60% of completed runs include a downloaded or exported package
- At least 30% of Design Mode users run Review Mode on their implementation within 30 days

**Guard metrics (must not degrade):**
- Zero silent failures — partial package always produced
- False positive rate on CRITICAL findings under 10%
- Assumption rate (assumptions made due to vague briefs) under 20% of findings

---

## 9. Open Questions

| Question | Owner | Due |
|---|---|---|
| Should `--brief` accept a file path (e.g., `--brief brief.txt`) in addition to inline text? | Engineering | Phase 1 kickoff |
| What is the minimum viable brief length before ARCHON warns vs refuses? | Product | Phase 1 kickoff |
| Should Design Mode produce a starter ADR set in Phase 1 or defer to Phase 1? | Product | Phase 1 planning |
| Does the Terraform skeleton ship in Phase 1 or is it deferred to Phase 1? | Engineering | Phase 1 kickoff |
| Should cost estimates at 3 scales be static (based on known pricing) or live (via cloud pricing APIs)? | Engineering | Phase 2 planning |

---

## 10. Dependencies and Risks

**Dependencies:**
- Strands Agents SDK for agent orchestration
- Anthropic API for Claude claude-opus-4-6 with prescriptive design prompts
- Tavily and Exa for technology recommendation citations
- Package formatter with Mermaid diagram generation support
- Terraform skeleton generator (cloud-architect agent output)

**Risks:**

| Risk | Impact | Mitigation |
|---|---|---|
| Vague briefs produce generic, low-value output | High — core value proposition fails | Add assumption logging and brief quality warning; tune prompts with vague brief test cases |
| Agents produce conflicting recommendations across domains | High — incoherent package | Supervisor cross-references domain outputs and flags contradictions before merge |
| Technology recommendations become stale as ecosystem evolves | Medium — cited sources go out of date | Always use live Tavily + Exa search per run; never rely on training data alone for version recommendations |
| IaC skeleton is too skeleton — not useful as a starting point | Medium — low perceived value | Define minimum skeleton fidelity standard: at least VPC, compute, database, and IAM resources per run |
| Cost estimates are inaccurate enough to mislead budget planning | Medium — trust damage | Label estimates clearly as approximate; link to cloud pricing calculators for validation |

---

**Complexity:** M
**Suggested first sprint scope:** Brief ingestion + all 6 agents with prescriptive framing + package formatter. Reuse Review pipeline with a different supervisor prompt. Validate with 3 test briefs (simple SaaS API, AI-first product, regulated fintech vertical).
