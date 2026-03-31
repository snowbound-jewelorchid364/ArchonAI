# Output Rules — ARCHON

## Finding Quality

Every finding must be:
- **Specific** — reference actual files, line numbers, or service names from the codebase
- **Actionable** — include a concrete recommendation, not generic advice
- **Evidenced** — backed by either codebase analysis or a citation
- **Scoped** — clearly state if it's from code analysis vs best-practice recommendation

Bad: "You should improve your security."
Good: "services/auth/jwt.py:47 uses HS256 algorithm with a hardcoded secret. Replace with RS256 and load the private key from AWS Secrets Manager. [CVE-2023-xxxxx]"

## Severity Calibration

| Severity | When to use |
|---|---|
| CRITICAL | Production data at risk, active exploit possible, system down |
| HIGH | Significant security gap, major cost issue (>$10k/mo), data loss risk |
| MEDIUM | Best practice violation, moderate performance impact, compliance gap |
| LOW | Minor improvement, optional optimisation, nice-to-have |
| INFO | Observation with no action required |

## ADR Format

Every ADR must follow this structure:
```markdown
# ADR-NNN: [Title]
**Status:** Proposed
**Date:** YYYY-MM-DD
**Agents:** [which agents contributed]

## Context
[What is the situation that requires a decision?]

## Decision
[What are we doing?]

## Rationale
[Why this over alternatives? Cite sources.]

## Alternatives Considered
[What else was evaluated and why rejected?]

## Consequences
[What changes as a result? Trade-offs?]

## Citations
[Source URLs]
```

## Terraform Output

- Skeleton only — not meant to be applied directly
- Include comments explaining every resource
- Use variables for all configurable values
- Include `outputs.tf` with key resource IDs
- Mark sensitive values with `sensitive = true`
- Always include a README explaining what the skeleton covers

## Diagram Format

- Use Mermaid C4 diagrams for system context and container views
- Use Mermaid flowchart for data flows and integration patterns
- Label all relationships with the protocol/technology used
- Max 15 nodes per diagram — split into multiple if larger

## Package Assembly

Final review package must always include:
1. `README.md` — executive summary + navigation guide
2. `findings/` — one .md per agent domain
3. `adrs/` — one .md per decision
4. `terraform/` — IaC skeletons
5. `diagrams/` — .mmd Mermaid files
6. `risk-register.md` — all findings sorted by severity
7. `citations.md` — all sources consolidated + deduplicated
