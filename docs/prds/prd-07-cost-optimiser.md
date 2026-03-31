# PRD-07: Cost Optimiser

**Mode:** Cost Optimiser
**Phase:** Phase 2
**Status:** Draft
**Pricing:** Included in Pro and Team plans; $199 one-off for Starter
**Last updated:** 2026-03-31

---

## 1. One-Line Summary

ARCHON Cost Optimiser analyses a codebase and cloud architecture to identify specific, quantified cost reduction opportunities — covering cloud resource rightsizing, inefficient data access patterns, over-provisioned services, and architectural changes that reduce monthly spend.

---

## 2. Problem Statement

**What problem does this solve?**
Startup cloud bills grow faster than engineering teams notice. By the time the bill spike triggers action, teams are already spending $5–20k/month more than they should. Most cost reviews are reactive, shallow, and not grounded in actual code patterns — they miss the architectural root causes of cost waste.

**Who experiences this problem?**
- CTOs and engineering leads at startups where the AWS/GCP/Azure bill has become a line item on the board deck
- Founders approaching Series A who need to demonstrate cost efficiency to investors
- Engineering teams who have completed a fast-growth phase and now need to optimise for profitability

**How are they solving it today — and why is that insufficient?**
- AWS Cost Explorer / cloud billing dashboards — show what you spent, not why or how to fix it
- Manual architecture reviews — time-consuming, incomplete, miss code-level patterns
- FinOps consultants — expensive, not grounded in codebase
- Generic LLM advice — not grounded in actual infrastructure code or usage patterns

**Cost of NOT solving this:**
At $10k/month cloud spend, a 30% reduction saves $36k/year. At $50k/month, the same reduction saves $180k/year. For a pre-profitability startup, this can be the difference between 18 and 24 months of runway.

---

## 3. Goals

**30 days:** 5 completed cost optimisation reports with at least one quantified saving identified per run
**60 days:** Average identified saving per run exceeds $500/month
**90 days:** At least 3 users report implementing a cost saving from ARCHON findings within 30 days

---

## 4. Non-Goals

- **Not a billing tool** — ARCHON does not connect to cloud billing APIs
- **Not a reserved instance recommender** — RI/savings plan recommendations require billing history ARCHON does not have
- **Not a live monitoring tool** — ARCHON analyses infra-as-code and application code, not live telemetry
- **Not a cloud cost calculator** — savings estimates are approximate; link to cloud pricing calculators
- **Does not cover SaaS tool costs** — focus is cloud infrastructure and application architectural patterns

---

## 5. User Stories

### Happy Path
**As a** CTO whose AWS bill has grown to $15k/month,
**I want to** receive a prioritised list of architectural cost reduction opportunities grounded in my codebase,
**so that** I can tell my board what we are doing to optimise spend without spending a week on an internal review.

**Acceptance Criteria:**
```
Given a GitHub repo URL and optional --monthly-spend flag
When I run ARCHON in cost-optimiser mode
Then ARCHON analyses the codebase with cloud-architect as lead agent and data-architect contributing
And produces a cost optimisation report within 60 minutes
And every finding includes: description, estimated monthly saving, implementation effort (S/M/L/XL), priority (Quick Win / High Impact / Long Term)
And every finding is grounded in actual codebase patterns (IaC files, application code, or detected anti-patterns)
And every HIGH or CRITICAL finding is cited with a source
```

### Error Case
**As a** user whose cost optimisation run partially fails,
**I want to** receive findings for the domains that completed,
**so that** I still have actionable savings opportunities even with a partial run.

**Acceptance Criteria:**
```
Given a cost optimiser run where one or more agents fail
When the failure occurs after at least one agent has completed
Then ARCHON writes a partial cost report with completed domain findings
And labels the report as partial with indication of missing domains
```

### Edge Case — No IaC in Repo
**As a** user whose repo has no Terraform, CloudFormation, or CDK code,
**I want to** receive cost findings based on application code patterns,
**so that** the run is still useful even without infrastructure-as-code present.

**Acceptance Criteria:**
```
Given a repo with no IaC files detected
When ARCHON runs in cost-optimiser mode
Then ARCHON analyses application code for cost-relevant patterns (N+1 queries, large data transfers, polling vs events, etc.)
And notes: "No IaC detected — cost findings are based on application code patterns only"
And produces application-layer cost findings rather than infrastructure findings
```

### Edge Case — No --monthly-spend Provided
**As a** user who does not supply current spend,
**I want to** receive relative savings estimates (percentage or effort tier) rather than dollar amounts,
**so that** the findings are still useful without precise billing context.

**Acceptance Criteria:**
```
Given a cost optimiser run with no --monthly-spend flag
When ARCHON produces savings estimates
Then estimates use relative tiers (High / Medium / Low saving potential) rather than dollar amounts
And the report notes: "Provide --monthly-spend for dollar-value estimates"
```

---

## 6. Functional Requirements

**Must:**
1. Must accept `--mode cost-optimiser` with `--repo` and optional `--monthly-spend` and `--cloud` (aws/gcp/azure) flags
2. Must run cloud-architect as lead agent with data-architect, integration-architect, and software-architect contributing cost-relevant findings
3. Must produce a cost optimisation report with:
   - Executive summary (total estimated saving range)
   - Quick wins (implementable in < 1 week)
   - High impact changes (implementable in 1–4 weeks)
   - Long-term architectural changes (1–3 months)
   - Per-finding detail: description, root cause, codebase evidence, estimated saving, effort, priority
   - Risk register for cost-related architectural changes
   - Citations for recommended patterns
4. Must categorise findings by type: over-provisioning, inefficient data access, unnecessary data transfer, idle resources, architectural inefficiency
5. Must provide dollar estimates if `--monthly-spend` is supplied, relative tiers otherwise
6. Must ground every finding in codebase evidence (IaC files, application code patterns, or detected anti-patterns)
7. Must cite every HIGH or critical saving opportunity
8. Must produce partial output if any agent fails
9. Must note if no IaC is present and adjust scope to application-layer findings

**Should:**
10. Should identify the top 3 "quick win" savings (implementable in under 1 week)
11. Should estimate payback period for architectural changes (effort cost vs monthly saving)
12. Should flag findings that require architectural changes vs configuration changes only
13. Should produce a prioritised action list suitable for sharing with engineering team

**May:**
14. May generate a FinOps summary slide outline for board or investor presentations
15. May compare estimated spend at current architecture vs recommended architecture at 3 scales

---

## 7. Non-Functional Requirements

- **Performance:** Full report completes in under 60 minutes at p75
- **Reliability:** Partial report always delivered
- **Cost:** Average run cost under $12
- **Evidence grounding:** At least 80% of findings reference specific codebase patterns or files
- **Savings accuracy:** Savings estimates clearly labelled as approximate; not presented as guaranteed
- **Security:** No credentials, API keys, or billing data from user codebase included in output

---

## 8. Success Metrics

**Primary:** Average identified saving per completed run exceeds $500/month (or equivalent relative tier)

**Secondary:**
- Package completion rate greater than 90%
- Median time to report delivery under 45 minutes
- At least 50% of completed runs result in at least one quick win actioned within 30 days
- At least 3 users report implementing a cost saving from ARCHON findings within 90 days

**Guard metrics:**
- Zero savings estimates presented as guaranteed
- Zero findings without codebase evidence
- Zero credentials or billing data in output

---

## 9. Open Questions

| Question | Owner | Due |
|---|---|---|
| Should `--monthly-spend` accept a total bill or a per-service breakdown? | Product | Phase 2 planning |
| Should Cost Optimiser run cloud-architect only for speed, or all 6 agents for completeness? | Engineering | Phase 2 kickoff |
| How do we handle repos that use cloud SDKs without IaC (common in early startups)? | Engineering | Phase 2 kickoff |
| Should savings estimates use a fixed compute cost model or cloud provider pricing API? | Engineering | Phase 2 planning |
| Is a FinOps summary for investors in scope for Phase 2, or Phase 3? | Product | Phase 2 planning |

---

## 10. Dependencies and Risks

**Dependencies:**
- Cloud-architect agent with cost-optimisation framing and cloud provider pricing knowledge in prompts
- Data-architect agent contributing data access pattern cost findings
- Tavily + Exa for FinOps best practice citations
- RAG pipeline for IaC and application code analysis
- Output formatter with quick win / high impact / long term categorisation

**Risks:**

| Risk | Impact | Mitigation |
|---|---|---|
| Savings estimates are too high and create unrealistic expectations | High — trust damage | Label all estimates as approximate; use conservative ranges; link to pricing calculators |
| No IaC in repo leads to low-value findings | Medium — poor ROI for user | Detect IaC absence early; set expectations; still produce application-layer findings |
| Cost findings require architectural changes that are too disruptive for a startup | Medium — findings are dismissed | Prioritise quick wins prominently; distinguish config changes from architectural changes |
| Cloud pricing changes invalidate savings estimates | Low-Medium — stale estimates | Use relative tiers as default; dollar estimates only with user-supplied spend context |

---

**Complexity:** M
**Suggested first sprint scope:** Not in Phase 1 or Phase 1 — Phase 2 mode. When building: start with cloud-architect only, validate savings estimate accuracy on 3 repos with known cloud spend before adding multi-agent depth.
