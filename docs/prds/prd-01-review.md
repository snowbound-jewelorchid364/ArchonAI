# PRD-01: Review Mode

**Mode:** Review
**Phase:** Phase 1
**Status:** Draft
**Pricing:** On-demand (included in all plans)
**Last updated:** 2026-03-31

---

## 1. One-Line Summary

ARCHON Review gives engineering teams at startups a complete, cited architecture review package — produced by 6 specialist AI agents in parallel — in under 60 minutes, for the cost of a coffee.

---

## 2. Problem Statement

**What problem does this solve?**
Engineering teams ship systems without architecture reviews because reviews are expensive, slow, and gatekept behind senior talent. Architectural mistakes compound — an unreviewed decision at month 1 becomes a $200k rewrite at month 18.

**Who experiences this problem?**
- Solo founders who are strong product engineers but don't have deep architecture expertise across security, cloud, data, and integration simultaneously
- CTOs at Series A/B startups with a 5–15 person team — no dedicated principal architect
- Engineering leads inheriting an existing codebase they didn't design

**How are they solving it today — and why is that insufficient?**
- Asking ChatGPT/Claude directly — gets generic advice, no codebase awareness, no citations, outdated information
- External consultants — $5–15k per engagement, 2–4 week turnaround, inconsistent quality
- Senior hire — $250–350k/year, takes 3+ months to hire and ramp
- Nothing — most startups skip reviews entirely

**Cost of NOT solving this:**
Average architectural mistake costs $50–500k to fix post-production (rewrite, outage, compliance failure, re-platforming). Skipping a review is a deferred liability.

---

## 3. Goals

**30 days:** 10 completed reviews with ≥ 60% rated 4/5 or higher on finding quality
**60 days:** 50% of users who complete a review run a second review within 30 days
**90 days:** Review mode is the top acquisition driver — $5k MRR from Review alone

---

## 4. Non-Goals

- **Not a code review tool** — ARCHON reviews architecture, not line-by-line code quality (that's GitHub Copilot's job)
- **Not real-time** — Review mode is a batch job (15–60 min), not an interactive assistant
- **Not a compliance certification** — findings inform compliance prep but do not constitute a formal audit
- **Not a replacement for human judgement** — ARCHON produces recommendations; the engineering team decides what to implement
- **Phase 1 has no web UI** — CLI only; web UI ships in Phase 2

---

## 5. User Stories

### Happy Path
**As an** engineering lead at a 10-person startup,
**I want to** submit our GitHub repo URL and get a complete architecture review in under an hour,
**so that** I can present a prioritised list of architecture risks to my CTO without spending $10k on a consultant.

**Acceptance Criteria:**
```
Given a valid public or private GitHub repo URL
When I run: python main.py --repo <url> --mode review
Then ARCHON indexes the codebase, runs all 6 agents in parallel,
  and outputs archon-review.md within 60 minutes
And the output contains ≥ 1 finding per agent domain
And every HIGH or CRITICAL finding includes a citation (source URL + excerpt)
And the executive summary correctly rates overall health as GREEN / AMBER / RED
```

### Error Case
**As a** user whose review fails mid-run (agent timeout or API error),
**I want to** receive partial output with whatever was completed,
**so that** I don't lose everything after 30 minutes of processing.

**Acceptance Criteria:**
```
Given an agent run that fails after ≥ 1 agent has completed
When the failure occurs (timeout, API error, or exception)
Then ARCHON writes a partial archon-review.md with completed agent outputs
And logs which agents failed and why
And exits with a non-zero status code
And the partial output is clearly marked [PARTIAL — X/6 agents completed]
```

### Edge Case
**As a** user with a large monorepo (500k+ LOC),
**I want to** receive a clear error and guidance rather than a silent hang,
**so that** I can use the zip upload or subdirectory flag instead.

**Acceptance Criteria:**
```
Given a repo exceeding 500,000 lines of code
When I submit it for review
Then ARCHON rejects it with: "Repo exceeds 500k LOC limit. Use --path to specify a subdirectory."
And suggests the --path flag to scope to a specific service or module
And does NOT begin indexing before checking the limit
```

---

## 6. Functional Requirements

**Must:**
1. Must accept a GitHub repo URL (`--repo`) or local path (`--path`) as input
2. Must clone/read the repo and build an in-memory RAG index using sentence-transformers/all-MiniLM-L6-v2
3. Must run all 6 specialist agents in parallel using `asyncio.gather()`
4. Must pass each agent its domain-specific system prompt from `prompts/<agent>.md`
5. Must give each agent access to RAG search (codebase) and web search (Tavily + Exa)
6. Must collect all agent outputs and pass to supervisor for merge and deduplication
7. Must deduplicate findings using Jaccard similarity (threshold: 0.75, same domain only)
8. Must cross-reference findings confirmed by 2+ agents and elevate them
9. Must produce a single `archon-review.md` output file in the current directory
10. Must deliver partial output if any agent fails — never return nothing
11. Must reject repos exceeding 500k LOC with a clear error message
12. Must skip binary files, `node_modules/`, `.git/`, `dist/`, `*.lock` files during indexing

**Should:**
13. Should complete within 60 minutes for repos under 100k LOC
14. Should display live agent status in the terminal (agent name + status + finding count)
15. Should support `--output` flag to specify output file path
16. Should support `--path` flag to scope review to a subdirectory

**May:**
17. May support `--skip-agents` flag to exclude specific agents (e.g., `--skip-agents ai-architect` if no AI in the codebase)

---

## 7. Non-Functional Requirements

- **Performance:** Full review completes in < 60 min for repos ≤ 100k LOC at p75
- **Cost:** LLM cost per review < $15 (6 agents × claude-opus-4-6)
- **Reliability:** Partial output delivered even if 2/6 agents fail
- **Indexing speed:** RAG index built in < 2 min for repos ≤ 50k LOC
- **Finding quality:** Every CRITICAL finding must include file + line number; every HIGH+ finding must include ≥ 1 citation
- **Security:** GitHub tokens never logged; cloned repos stored in `/tmp/archon-<job-id>/` and deleted after run

---

## 8. Success Metrics

**Primary:** Finding quality rating ≥ 4/5 by ≥ 60% of users (post-review survey)

**Secondary:**
- Review completion rate (started → output delivered) > 80%
- Median time to first finding < 15 minutes
- Cost per review < $15 (LLM + search API calls)

**Guard metrics (must not degrade):**
- False positive rate on CRITICAL findings < 10% (verified by user feedback)
- Output file always delivered (even partial) — 0% silent failures

---

## 9. Open Questions

| Question | Owner | Due |
|---|---|---|
| Should Phase 1 support private repos via GitHub token, or public only? | Engineering | Before Phase 1 start |
| What is the exact token cost per agent run at claude-opus-4-6 prices? | Engineering | Before Phase 1 start |
| Should the RAG index be cached between runs on the same repo? | Engineering | Phase 1 |
| What test repos should we use to validate finding quality? | Product | Phase 1 |
| Should we support GitLab / Bitbucket at Phase 1 or GitHub only? | Product | Before Phase 1 |

---

## 10. Dependencies and Risks

**Dependencies:**
- Strands Agents SDK — must validate tool availability (tavily_search, exa_search, file_read) before build
- Tavily API key + Exa API key — required at runtime
- Anthropic API key (claude-opus-4-6) — required at runtime
- sentence-transformers/all-MiniLM-L6-v2 — ~90MB download on first run

**Risks:**

| Risk | Impact | Mitigation |
|---|---|---|
| Strands SDK breaking changes | High — blocks entire build | Pin version in pyproject.toml; abstract behind ArchonRunner interface |
| claude-opus-4-6 cost exceeds $15/review | Medium — pricing model breaks | Run cost benchmark on 3 test repos before setting pricing |
| Agent run exceeds 60 min on large repos | Medium — poor UX | Hard 20-min timeout per agent; partial output fallback |
| RAG quality poor on large repos | High — finding quality drops | Test on repos 10k / 50k / 100k LOC; tune chunk size |
| Tavily/Exa rate limits during parallel agent runs | Medium — missing citations | Stagger search calls; cache results within a run |

---

**Complexity:** M
**Suggested first sprint scope:** RAG indexer + 1 agent (software-architect) end-to-end → `archon-review.md` with software findings only. Prove the pipeline before adding all 6 agents.
