# PRD-08: PR Reviewer

**Mode:** PR Reviewer
**Phase:** Phase 2
**Status:** Draft
**Pricing:** Included in Pro and Team plans
**Last updated:** 2026-03-31

---

## 1. One-Line Summary

ARCHON PR Reviewer automatically analyses a pull request against the existing codebase architecture, flagging architectural regressions, pattern violations, security gaps, and integration risks before the PR is merged.

---

## 2. Problem Statement

**What problem does this solve?**
Architecture debt accumulates one PR at a time. Individual code reviewers catch logic bugs and style issues but rarely catch architectural regressions — a new direct DB call that breaks the repository pattern, a sync HTTP call that should be async, or a new dependency that violates the service boundary model. These micro-regressions compound silently until the architecture is unrecognisable from the original design.

**Who experiences this problem?**
- Engineering leads at growing startups where PRs are reviewed by engineers who are not the original architects
- CTOs who established an architecture but are now too far from the code to review every PR
- Teams that have just completed an ARCHON Review and want to prevent drift from the recommended improvements

**How are they solving it today — and why is that insufficient?**
- Human code review — misses cross-cutting architectural concerns; reviewers focus on logic
- Linters and static analysis — catch style and security issues, not architectural pattern violations
- Architecture fitness functions — require upfront investment to define and maintain
- Post-merge architecture reviews — too late; the debt is already in main

**Cost of NOT solving this:**
Unchecked PRs are the primary source of architectural drift. Teams that complete an ARCHON Review but do not monitor PRs will return to the same state within 6–12 months.

---

## 3. Goals

**30 days:** PR Reviewer integrated with at least 3 customer repos via GitHub webhook
**60 days:** Average PR review completion (comment posted) under 5 minutes from PR open event
**90 days:** At least 50% of flagged architectural findings actioned (PR updated or finding dismissed) within 48 hours

---

## 4. Non-Goals

- **Not a replacement for human code review** — ARCHON flags architectural concerns, humans own the review
- **Not a linter or static analysis tool** — ARCHON does not replace ESLint, Pylint, or Semgrep
- **Not a CI/CD gate by default** — ARCHON posts review comments but does not block merges unless configured
- **Does not review every line of code** — focuses on architectural impact of the diff, not line-by-line logic

---

## 5. User Stories

### Happy Path
**As a** CTO who has set up ARCHON PR Reviewer on my repo,
**I want to** receive an architectural review comment within 5 minutes of a PR being opened,
**so that** architectural regressions are caught before they are merged.

**Acceptance Criteria:**
```
Given a GitHub PR opened on a repo with ARCHON PR Reviewer configured
When the PR diff is received via webhook
Then ARCHON analyses the diff against the base branch codebase
And posts a review comment within 5 minutes covering: architectural findings, pattern violations, security observations, integration risks
And each finding includes: severity, description, affected file/line, recommendation
And the comment links to the relevant ARCHON finding from the last full Review if one exists
```

### Error Case
**As a** user whose PR review run fails,
**I want to** see a clear failure indicator on the PR rather than silence,
**so that** I know ARCHON did not complete and can trigger a re-run.

**Acceptance Criteria:**
```
Given a PR review run that fails or times out
When the failure occurs
Then ARCHON posts a PR comment: "ARCHON review failed — re-run with /archon review"
And does not post partial or incomplete findings without labelling them as partial
```

### Edge Case — Large PR (500+ files changed)
**As a** user opening a large refactoring PR,
**I want to** receive a scoped architectural review rather than a timeout,
**so that** ARCHON is still useful for large changes.

**Acceptance Criteria:**
```
Given a PR with more than 500 files changed
When ARCHON starts the PR review
Then ARCHON warns: "Large PR detected (NNN files) — scoping review to highest-impact files"
And prioritises files by architectural significance (entry points, domain boundaries, config, auth, data access)
And completes within 5 minutes on the scoped file set
```

---

## 6. Functional Requirements

**Must:**
1. Must integrate with GitHub via webhook on PR open and PR synchronise events
2. Must analyse the PR diff (not the full codebase) with context from the base branch RAG index
3. Must run software-architect and integration-architect as lead agents for PR review
4. Must post a GitHub PR review comment with structured findings within 5 minutes
5. Must include in the comment: summary, findings table (severity / file / description / recommendation), any security observations
6. Must scope to changed files when PR exceeds 500 files
7. Must post a failure comment if the review does not complete
8. Must support `/archon review` command in PR comments to trigger a re-run
9. Must not block PR merges by default (comment only, not required check)
10. Must respect GitHub rate limits and queue reviews if multiple PRs open simultaneously

**Should:**
11. Should link findings to the last full ARCHON Review report if one exists for the repo
12. Should allow configuring severity threshold for posting (e.g., only post if HIGH or CRITICAL findings)
13. Should support opt-out per PR via `#archon-skip` in PR description
14. Should support configuring as a required GitHub status check in Phase 3

**May:**
15. May generate a weekly architectural drift summary across all PRs merged in the week
16. May support GitLab and Bitbucket in Phase 4

---

## 7. Non-Functional Requirements

- **Performance:** Review comment posted within 5 minutes of PR open event at p90
- **Reliability:** Failure comment always posted if review does not complete; no silent failures
- **Cost:** Average cost per PR review under $2
- **Precision:** False positive rate on CRITICAL architectural findings under 15%
- **Security:** PR diff content processed in isolated job; not stored after review; secrets in diff never quoted in comment

---

## 8. Success Metrics

**Primary:** Average time from PR open to ARCHON comment posted under 5 minutes at p90

**Secondary:**
- PR review completion rate greater than 95%
- At least 50% of HIGH/CRITICAL findings actioned within 48 hours
- False positive rate (findings dismissed as not relevant) under 20%
- At least 30% of Team plan users enable PR Reviewer within 30 days of plan activation

**Guard metrics:**
- Zero silent failures
- Zero secrets or credentials in posted PR comments
- PR review never blocks a merge without explicit opt-in configuration

---

## 9. Open Questions

| Question | Owner | Due |
|---|---|---|
| Should PR Reviewer rebuild the RAG index on every PR or use a cached index from the last Review run? | Engineering | Phase 2 kickoff |
| Should the GitHub App be a separate installation from the web UI auth, or unified? | Engineering | Phase 2 architecture |
| What is the right default severity threshold for posting a comment — any finding, or HIGH+ only? | Product | Phase 2 planning |
| Should PR Reviewer be a required check or advisory only? Should this be configurable? | Product | Phase 2 planning |
| How do we handle monorepos where only one service is relevant to a given PR? | Engineering | Phase 2 |

---

## 10. Dependencies and Risks

**Dependencies:**
- GitHub App with webhook and PR comment write permissions
- Software-architect and integration-architect agents with diff-aware prompts
- Cached or on-demand RAG index per repo
- Redis/BullMQ for queuing PR review jobs
- 5-minute hard timeout per PR review

**Risks:**

| Risk | Impact | Mitigation |
|---|---|---|
| High false positive rate leads to PR review comment fatigue | High — users disable the integration | Tune severity thresholds; allow configurable threshold; track dismiss rate as quality signal |
| RAG index is stale and produces irrelevant findings | Medium — poor review quality | Trigger re-index on push to default branch; warn if index is > 7 days old |
| 5-minute timeout causes incomplete reviews on large PRs | Medium — incomplete feedback | Scope to high-impact files for large PRs; always complete within 5 minutes with scoped review |
| GitHub API rate limits during high-volume PR periods | Medium — delayed reviews | Implement queue with rate limit awareness; post "review queued" comment immediately |

---

**Complexity:** M-L (GitHub App integration + diff-aware RAG adds engineering complexity)
**Suggested first sprint scope:** Not in Phase 1 or Phase 1 — Phase 2 mode. When building: start with webhook + software-architect only, validate 5-minute completion before adding integration-architect and additional agents.
