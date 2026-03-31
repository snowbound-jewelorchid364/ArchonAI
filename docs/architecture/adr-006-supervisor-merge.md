# ADR-006: Supervisor Merge and Deduplication Strategy

**Status:** Accepted
**Date:** 2026-03-31

---

## Context

6 agents run in parallel and produce independent findings. Many findings will overlap — the security and cloud agents may both flag an unencrypted S3 bucket. The supervisor must merge these into a coherent package without losing nuance.

---

## Decision

**Three-step merge: Collect → Deduplicate → Cross-reference → Synthesise**

### Step 1 — Collect
Gather all `AgentFindings` objects. Log any agent failures without aborting. A review with 4/6 agents succeeding still delivers value.

### Step 2 — Deduplicate
Use **title + domain + severity fingerprint** for exact deduplication. For semantic deduplication, compare finding titles with simple string similarity (Jaccard on words). Threshold: 0.75 similarity = duplicate.

```python
def are_duplicate(a: Finding, b: Finding) -> bool:
    if a.domain == b.domain:
        return jaccard_similarity(a.title, b.title) > 0.75
    return False  # Cross-domain findings are never duplicates
```

When duplicating: **keep the finding with more citations + more detailed recommendation.** Merge the citation lists from both.

### Step 3 — Cross-Reference
Flag findings that appear in multiple domains as "confirmed by N agents". These are elevated in the risk register.

```python
# If security-architect AND cloud-architect both flag "No encryption at rest"
# → Create a cross-domain finding:
#   title: "No Encryption at Rest (confirmed by 2 agents)"
#   severity: max(security_finding.severity, cloud_finding.severity)
#   citations: union(security_citations, cloud_citations)
```

### Step 4 — Synthesise Executive Summary
Pass merged findings to supervisor agent (Claude) with prompt:
```
Given these findings from 6 architecture specialists,
write a 3-paragraph executive summary:
1. Overall architecture health (Green/Amber/Red)
2. Top 3 most critical issues
3. Recommended first steps

Findings: {json(merged_findings)}
```

---

## Contradiction Handling

If agents contradict each other (agent A recommends microservices, agent B recommends staying on the monolith):
- Both recommendations are preserved in the report
- Marked as `[CONFLICTING RECOMMENDATIONS]`
- Executive summary notes the trade-off and presents both views
- User decides at Checkpoint 3 (Phase 2+)

---

## Consequences

- Deduplication is imperfect — some near-duplicates may survive. That is acceptable.
- Cross-referencing requires all agents to use consistent entity names. System prompts must instruct agents to use exact service/file names from the codebase.
- Executive summary requires a final LLM call (~$0.05–0.20 additional cost).
