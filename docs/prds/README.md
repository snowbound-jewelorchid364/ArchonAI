# ARCHON — PRD Index

**Product:** ARCHON — "Your Frontier AI Architect. From idea to infrastructure."
**Last updated:** 2026-03-31

One PRD per mode. Write PRDs in phase order — only what you're about to build.

---

## PRD Status

| # | Mode | File | Phase | Status | Priority |
|---|---|---|---|---|---|
| 01 | Review | [prd-01-review.md](./prd-01-review.md) | Phase 1 | Draft | P0 |
| 02 | Design | [prd-02-design.md](./prd-02-design.md) | Phase 1 | Draft | P0 |
| 03 | Migration Planner | [prd-03-migration-planner.md](./prd-03-migration-planner.md) | Phase 1 | Not started | P1 |
| 04 | Compliance Auditor | [prd-04-compliance-auditor.md](./prd-04-compliance-auditor.md) | Phase 1 | Not started | P1 |
| 05 | Due Diligence Responder | [prd-05-due-diligence.md](./prd-05-due-diligence.md) | Phase 1 | Not started | P1 |
| 06 | Incident Responder | [prd-06-incident-responder.md](./prd-06-incident-responder.md) | Phase 1 | Not started | P1 |
| 07 | Cost Optimiser | [prd-07-cost-optimiser.md](./prd-07-cost-optimiser.md) | Phase 2 | Not started | P2 |
| 08 | PR Reviewer | [prd-08-pr-reviewer.md](./prd-08-pr-reviewer.md) | Phase 2 | Not started | P2 |
| 09 | Scaling Advisor | [prd-09-scaling-advisor.md](./prd-09-scaling-advisor.md) | Phase 2 | Not started | P2 |
| 10 | Drift Monitor | [prd-10-drift-monitor.md](./prd-10-drift-monitor.md) | Phase 2 | Not started | P2 |
| 11 | Feature Feasibility | [prd-11-feature-feasibility.md](./prd-11-feature-feasibility.md) | Phase 3 | Not started | P3 |
| 12 | Vendor Evaluator | [prd-12-vendor-evaluator.md](./prd-12-vendor-evaluator.md) | Phase 3 | Not started | P3 |
| 13 | Onboarding Accelerator | [prd-13-onboarding-accelerator.md](./prd-13-onboarding-accelerator.md) | Phase 3 | Not started | P3 |
| 14 | Sunset Planner | [prd-14-sunset-planner.md](./prd-14-sunset-planner.md) | Phase 3 | Not started | P3 |

---

## Pricing Reference

| Tier | Modes | Price |
|---|---|---|
| Event-based | Due Diligence, Compliance, Migration, Incident | $299–$999/run |
| On-demand | Review, Design, Cost Optimiser, Scaling, Feasibility, Vendor, Onboarding, Sunset | Included in plan |
| Subscription gate | PR Reviewer (Pro+), Drift Monitor (Team+) | $199–$499/month |

## Agent Reference

| Agent | System Prompt | Finding Prefix |
|---|---|---|
| software-architect | `prompts/software_architect.md` | F-SW |
| cloud-architect | `prompts/cloud_architect.md` | F-CL |
| security-architect | `prompts/security_architect.md` | F-SC |
| data-architect | `prompts/data_architect.md` | F-DA |
| integration-architect | `prompts/integration_architect.md` | F-IN |
| ai-architect | `prompts/ai_architect.md` | F-AI |
| supervisor | `prompts/supervisor.md` | — |

---

## Writing PRDs with GitHub Copilot

Open Copilot Chat (`Ctrl+Alt+I`) and use `@workspace`. Run exploration prompt first:

```
@workspace Read PRODUCT_PLAN.md, CLAUDE.md, and docs/prds/README.md.
Summarise the 14 ARCHON modes, the 6 agents, and the 3 pricing tiers.
Do not write anything yet — just confirm you understand the product.
```

Then use the per-mode prompt from `docs/prds/README.md` to fill each stub.
