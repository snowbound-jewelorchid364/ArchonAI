# Getting Started with ARCHON

This guide walks you through running your first architecture review in under 10 minutes.

---

## Prerequisites

- A GitHub account (public or private repos supported)
- An ARCHON account (sign up at archon.ai)

---

## Step 1 — Connect Your GitHub Repository

1. Sign in to ARCHON at `app.archon.ai`
2. Click **New Project** from the dashboard
3. Paste your GitHub repository URL:
   ```
   https://github.com/your-org/your-repo
   ```
4. Select the branch to analyse (default: `main`)
5. Click **Connect Repository**

ARCHON will request GitHub OAuth access to read your repository. For private repos, you'll need to authorise the ARCHON GitHub App.

> **No repo yet?** You can also describe your planned architecture in text — ARCHON runs a full review without needing code.

---

## Step 2 — Configure Your Review

### Requirements (Optional)
Add specific focus areas or constraints:
```
Focus on: security posture for HIPAA compliance
Constraints: we must stay on AWS, no Kubernetes, team is 3 engineers
Goal: validate architecture before Series A due diligence
```

The more context you provide, the more targeted the findings.

### HITL Mode
Choose how much control you want:

| Mode | Description |
|---|---|
| **Autopilot** | Agents run fully — you review only at the start and end |
| **Balanced** | 4 checkpoints at key decision points (recommended) |
| **Supervised** | Review and approve each agent's work individually |

---

## Step 3 — Start the Review

Click **Run Architecture Review**.

ARCHON will:
1. Index your codebase into its knowledge base (~2-5 minutes for most repos)
2. Fan out to all 6 specialist architect agents
3. Each agent researches your codebase + the live web in parallel
4. Pause at checkpoints for your input (if Balanced or Supervised mode)

You'll receive an email notification at each checkpoint and when the review is complete.

---

## Step 4 — Review Checkpoints

At each checkpoint, ARCHON presents findings and asks for your direction:

**Checkpoint 1 — Scope Confirmation**
Review what ARCHON found in your codebase. Correct any misidentified services or add context the agents may have missed.

**Checkpoint 2 — Findings Preview**
See the top issues discovered. You can:
- **Approve** — agents go deeper on all findings
- **Redirect** — shift focus ("prioritise cost over security")
- **Reject** — stop the review if findings are off-base

**Checkpoint 3 — Architecture Decisions**
For each major decision, ARCHON presents 2-3 alternatives with trade-offs. Choose the direction that fits your team and constraints.

**Checkpoint 4 — Final Review**
Review the complete package before export.

---

## Step 5 — Export Your Package

When the review is complete, export your Architecture Review Package:

- **PDF** — Formatted report for sharing with investors, board, or team
- **Markdown** — Raw files you can commit to your repo
- **JSON** — Structured data for your own tooling

The package includes:
- Executive summary
- Per-domain findings with citations
- Architecture Decision Records (ADRs)
- Terraform IaC skeleton
- Architecture diagrams (Mermaid)
- Risk register
- All web sources cited

---

## Tips for Better Reviews

**Be specific in requirements**
Instead of "review our backend", try "review the authentication and authorisation design of our FastAPI backend for SOC 2 compliance readiness".

**Provide constraints**
Tell ARCHON what you can't change: "we're locked into AWS, budget is $5k/month, team has no Kubernetes experience".

**Use Supervised mode for first review**
The first time you run ARCHON on a codebase, Supervised mode helps you understand how the agents reason — and lets you correct early misunderstandings before they propagate.

**Run reviews before major milestones**
- Before fundraising due diligence
- Before hiring your first platform engineer
- Before migrating to microservices
- Before launching in a new regulated market

---

## Next Steps

- [Understanding Your Review Package](./output-guide.md)
- [The 6 Architect Agents Explained](./agents.md)
- [HITL Modes Deep Dive](./hitl-modes.md)
