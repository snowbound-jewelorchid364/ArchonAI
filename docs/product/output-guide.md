# Understanding Your Architecture Review Package

Every completed ARCHON review delivers a structured package of architecture artifacts. This guide explains each component and how to use it.

---

## Package Structure

```
Architecture Review Package
├── README.md                  ← Start here — executive summary + navigation
├── findings/
│   ├── software-architect.md  ← Application patterns + NFR findings
│   ├── cloud-architect.md     ← Infrastructure + cost findings
│   ├── security-architect.md  ← Security + compliance findings
│   ├── data-architect.md      ← Data model + governance findings
│   ├── integration-architect.md ← Service communication findings
│   └── ai-architect.md        ← AI/ML system findings (if applicable)
├── adrs/
│   ├── adr-001-[title].md     ← One ADR per key architectural decision
│   └── adr-NNN-[title].md
├── terraform/
│   ├── main.tf                ← Core infrastructure resources
│   ├── variables.tf           ← All configurable values
│   ├── outputs.tf             ← Key resource identifiers
│   └── README.md              ← What this skeleton covers + how to use it
├── diagrams/
│   ├── system-context.mmd     ← C4 Level 1: system in its environment
│   ├── container-view.mmd     ← C4 Level 2: major containers/services
│   └── [domain]-flow.mmd      ← Data/integration flow diagrams
├── risk-register.md           ← All findings ranked by severity
└── citations.md               ← All web sources used, consolidated
```

---

## Executive Summary (README.md)

The executive summary is written for decision-makers — CTOs, VPs of Engineering, investors. It covers:

- **Overall assessment** — Green / Amber / Red health signal
- **Critical findings** — Issues requiring immediate action
- **Top 3 recommendations** — Highest-impact changes to make first
- **Effort estimate** — Rough sizing of the full remediation backlog
- **Review metadata** — Date, codebase analysed, agents used, total citations

Use this for board reports, investor due diligence packets, and team briefings.

---

## Per-Domain Findings

Each agent produces a domain-specific findings report. Format for each finding:

```markdown
## F-001: [Finding Title]
**Severity:** CRITICAL | HIGH | MEDIUM | LOW | INFO
**Agent:** software-architect
**Type:** Code Analysis | Best Practice | Web Research

### Description
What was found and why it matters.

### Evidence
> From `services/auth/jwt.py:47`: uses HS256 with hardcoded secret

### Recommendation
Specific, actionable steps to fix this.

### Citations
- [JWT Security Best Practices 2025](https://source.url) — "excerpt from source"
- [CVE-2023-XXXX](https://nvd.nist.gov/...) — "relevant vulnerability detail"
```

**Severity definitions:**

| Severity | Meaning |
|---|---|
| CRITICAL | Production data at risk, active exploit possible, or system availability at risk |
| HIGH | Significant security gap, major cost issue, or data loss risk |
| MEDIUM | Best practice violation, moderate performance impact, or compliance gap |
| LOW | Minor improvement opportunity, optional optimisation |
| INFO | Observation, no action required |

---

## Architecture Decision Records (ADRs)

ADRs document key architectural decisions with full context and rationale. ARCHON generates one ADR per significant decision point.

**ADR format:**
```markdown
# ADR-001: [Decision Title]
**Status:** Proposed
**Date:** YYYY-MM-DD
**Domain:** cloud-architect

## Context
Why does this decision need to be made?

## Decision
What are we deciding?

## Rationale
Why this option over alternatives? (with citations)

## Alternatives Considered
What else was evaluated and why rejected?

## Consequences
What changes as a result? What are the trade-offs?

## Citations
Sources that informed this decision.
```

ADRs are designed to be committed directly into your repository's `docs/decisions/` folder — they become your team's architectural memory.

---

## Terraform IaC Skeleton

The Terraform skeleton is a starting point, not a complete configuration. It provides:

- Correct resource structure for your chosen architecture
- All configurable values extracted as variables
- Comments explaining every resource and key parameter
- Security best practices applied by default (encryption, least privilege)
- Output values for key resource IDs

**Important:** The skeleton is meant to be reviewed and adapted by your team before applying. Always run `terraform plan` and review the output before `terraform apply`.

---

## Diagrams (Mermaid)

Diagrams are provided as `.mmd` Mermaid source files. Render them with:

- [Mermaid Live Editor](https://mermaid.live) — paste and render online
- VS Code Mermaid extension — preview in editor
- GitHub — renders `.mmd` files natively in markdown

**Included diagram types:**

| Diagram | Description |
|---|---|
| `system-context.mmd` | C4 Level 1 — your system and its external dependencies |
| `container-view.mmd` | C4 Level 2 — major containers, services, and databases |
| `[domain]-flow.mmd` | Data flow, integration patterns, or request flows |

---

## Risk Register

The risk register consolidates all findings from all 6 agents into a single prioritised list.

| Column | Description |
|---|---|
| ID | Unique finding ID (e.g., F-023) |
| Domain | Which agent identified this |
| Severity | CRITICAL / HIGH / MEDIUM / LOW / INFO |
| Title | One-line summary |
| Effort | S / M / L / XL to remediate |
| Status | Open / In Progress / Resolved |
| Source | Code analysis or web research |

The risk register is designed to be imported into your issue tracker (GitHub Issues, Jira, Linear).

---

## Citations

All web sources used by agents are consolidated in `citations.md`:

```markdown
## Domain: security-architect

1. [CVE-2024-XXXXX — JWT Algorithm Confusion](https://nvd.nist.gov/...)
   Published: 2024-03-15 | Credibility: 1.0
   > "Excerpt of relevant content used by the agent"

2. [OWASP JWT Security Cheat Sheet](https://cheatsheetseries.owasp.org/...)
   Published: 2024-01-10 | Credibility: 0.95
   > "Relevant excerpt"
```

Citations are deduplicated across agents — the same source used by multiple agents appears once with all relevant agents noted.

---

## Editing and Versioning

You can edit any output directly in the ARCHON web app. Each edit creates a new version — the original agent output is always preserved. Version history is available via the output detail view.

When you export the package, you always get the latest version of each artifact.
