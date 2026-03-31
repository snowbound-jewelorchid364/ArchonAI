# PRD-10: Drift Monitor

**Mode:** Drift Monitor
**Phase:** Phase 2
**Status:** Draft
**Pricing:** Included in Team plan only
**Last updated:** 2026-03-31

---

## 1. One-Line Summary

ARCHON Drift Monitor runs a weekly automated architecture check against a connected repo and emails a diff report showing what has changed architecturally since the last review — flagging new risks, regressions, and improvements.

---

## 2. Problem Statement

**What problem does this solve?**
Architecture reviews are point-in-time snapshots. A codebase that was well-architected in January can accumulate significant drift by March. Teams that complete a full ARCHON Review have no automated way to track whether the recommendations were implemented, whether new debt has appeared, or whether the architectural posture has improved or degraded week-over-week.

**Who experiences this problem?**
- CTOs and engineering leads who completed an ARCHON Review and want to track progress
- Team plan customers whose engineering team is shipping 5–20 PRs per week
- Engineering leads who need to demonstrate architectural health progress to a board or investor

**How are they solving it today — and why is that insufficient?**
- Monthly architecture reviews — too infrequent; drift accumulates between reviews
- PR Reviewer — catches individual PRs but does not provide a weekly aggregate view
- Manual tracking — no systematic way to compare architectural state week-over-week

---

## 3. Goals

**30 days:** Drift Monitor running on at least 3 Team plan repos with weekly reports delivered
**60 days:** At least 50% of Drift Monitor users report the weekly summary is part of their engineering routine
**90 days:** Average architectural health score improves measurably over 8 weeks for teams using Drift Monitor

---

## 4. Non-Goals

- **Not a real-time monitor** — weekly cadence only in Phase 2; configurable cadence in Phase 3
- **Not a PR-level reviewer** — that is Mode 8 (PR Reviewer)
- **Not a compliance tracker** — Drift Monitor tracks architectural patterns, not compliance controls
- **Does not generate a new full Review** — compares against the last full Review baseline

---

## 5. User Stories

### Happy Path
**As a** CTO on the Team plan,
**I want to** receive a weekly email summarising architectural drift since the last review,
**so that** I can see whether my team is improving or degrading the architecture without doing a full review every week.

**Acceptance Criteria:**
```
Given a repo connected to ARCHON on the Team plan with Drift Monitor enabled
When the weekly scheduled run triggers (Monday 9am UTC by default)
Then ARCHON runs a lightweight architecture diff against the last full Review baseline
And emails the configured recipients a drift report within 2 hours of trigger
And the report shows: new findings since last review, resolved findings, unchanged findings, architectural health score trend
And each new finding includes severity, description, and codebase reference
```

### Edge Case — No Prior Review Baseline
**As a** new Team plan user enabling Drift Monitor before running a full Review,
**I want to** receive a clear explanation that a baseline Review is required first,
**so that** I understand why Drift Monitor cannot start immediately.

**Acceptance Criteria:**
```
Given Drift Monitor enabled with no prior full Review on the repo
When the first scheduled run triggers
Then ARCHON sends an email: "Drift Monitor requires a full Review baseline. Run archon --mode review first to establish a baseline."
And queues the first diff report for the following week after a Review is completed
```

---

## 6. Functional Requirements

**Must:**
1. Run automatically on a weekly schedule (Monday 9am UTC default)
2. Compare current codebase against the last full Review baseline
3. Produce a drift report showing new, resolved, and unchanged findings
4. Include an architectural health score trend (up/stable/down vs last week)
5. Email the report to configured recipients
6. Require a full Review baseline before first run
7. Produce a report within 2 hours of trigger

**Should:**
8. Allow configuring report recipients and schedule per repo
9. Allow configuring severity threshold for email alerts (e.g., only email if new CRITICAL findings)
10. Show a 4-week trend of architectural health score in the report
11. Link each finding to the relevant section of the last full Review

**May:**
12. Support Slack notification in addition to email in Phase 3
13. Support configurable cadence (daily/weekly/monthly) in Phase 3

---

## 7. Non-Functional Requirements

- **Performance:** Drift report delivered within 2 hours of scheduled trigger
- **Reliability:** If drift run fails, send failure notification email; never silent failure
- **Cost:** Average cost per weekly run under $5 (lightweight vs full Review)
- **Baseline integrity:** Always compare against the most recent full Review; re-baseline after each new full Review

---

## 8. Success Metrics

**Primary:** At least 50% of Drift Monitor users open the weekly email report
**Secondary:** Average architectural health score improves over 8 weeks for active users; at least 30% of new findings actioned within 1 week

---

## 9. Open Questions

| Question | Owner | Due |
|---|---|---|
| Should Drift Monitor re-index the full repo weekly or use an incremental diff-based index? | Engineering | Phase 2 kickoff |
| What constitutes an architectural health score — finding count, severity-weighted, or something else? | Product | Phase 2 planning |
| Should the weekly report be in-app only, email only, or both? | Product | Phase 2 planning |

---

## 10. Dependencies and Risks

**Dependencies:** Last full Review baseline stored per repo; scheduler (cron); email delivery service; lightweight RAG re-index pipeline

**Risks:**

| Risk | Impact | Mitigation |
|---|---|---|
| No baseline means first-week users cannot use Drift Monitor | Medium | Clear onboarding prompt; auto-trigger full Review when Drift Monitor is enabled |
| Weekly run cost accumulates for large repos | Medium | Use lightweight diff-based run with cached RAG; cap per-run cost at $5 |
| Health score metric is gamed or misleading | Low-Medium | Define score formula transparently; show finding counts alongside score |

---

**Complexity:** M (scheduler + baseline comparison adds state management complexity)
**Suggested first sprint scope:** Phase 2 mode. Requires full Review pipeline working first. Build incremental diff comparison on top of existing Review output.
