# Human-in-the-Loop (HITL) Modes

ARCHON's Human-in-the-Loop system gives you control over how autonomously the agents work. You choose when they pause and ask for your input — and when they run straight through.

---

## The 4 Checkpoints

Every review has 4 potential checkpoints. Depending on your HITL mode, some or all of these will pause and wait for your decision.

### Checkpoint 1 — Scope Confirmation
**When:** After initial codebase ingestion, before deep analysis begins.

ARCHON presents what it found:
- Services, repositories, and technologies detected
- Proposed focus areas based on codebase signals
- Estimated review depth and duration

**Your options:**
- **Approve** — Proceed with detected scope
- **Edit** — Correct misidentified services, add missing context
- **Add constraints** — "Ignore the legacy PHP monolith, focus only on new Go services"

---

### Checkpoint 2 — Findings Preview
**When:** After all 6 agents complete their initial research phase.

ARCHON presents:
- Top findings by severity (Critical, High, Medium)
- Which domains have the most issues
- Estimated effort to address each cluster

**Your options:**
- **Approve** — All agents proceed to deep analysis
- **Redirect** — Shift focus ("prioritise security over cost")
- **Reject** — Stop the review if findings are off-target

---

### Checkpoint 3 — Architecture Decisions
**When:** When agents encounter decision points requiring human judgement.

ARCHON presents alternatives with trade-offs:
```
API Layer Decision:
  Option A: GraphQL Federation
    ✓ Best for your frontend team's velocity
    ✗ Higher complexity, new skill required
    Cost: Medium

  Option B: REST + API Gateway
    ✓ Simpler, team already knows it
    ✗ Less flexible for future requirements
    Cost: Low

  Option C: gRPC
    ✓ Best performance for internal services
    ✗ Harder to adopt, no browser support
    Cost: Medium
```

**Your options:**
- **Choose an option** — Agents proceed with chosen direction
- **Provide custom direction** — "None of the above, we'll keep REST but add versioning"
- **Ask for more analysis** — "Show me the cost implications of Option A in more detail"

---

### Checkpoint 4 — Final Review
**When:** After all agents complete and the package is assembled.

ARCHON presents:
- Complete review summary
- Finding count by severity and domain
- Package contents preview

**Your options:**
- **Approve and export** — Download/share the package
- **Request revisions** — "The Terraform skeleton is missing our VPC module, please add it"

---

## HITL Modes

### Autopilot
**Checkpoints active:** 1 and 4 only

Best for:
- Teams that have run ARCHON before and trust the output
- Repeat reviews of the same codebase
- Time-sensitive situations

Agents run with maximum autonomy. You confirm scope at the start and review the final package at the end. Checkpoints 2 and 3 are auto-approved with sensible defaults.

---

### Balanced (Default)
**Checkpoints active:** All 4

Best for:
- Most users, most of the time
- First review of a new codebase
- Important architectural decisions where you want input

You stay informed and in control at every major decision point without approving every individual agent action. Recommended for teams new to ARCHON.

---

### Supervised
**Checkpoints active:** All 4 + per-agent approvals

Best for:
- High-stakes reviews (pre-fundraising, compliance audits)
- Highly regulated industries (healthcare, fintech)
- Teams that want to understand how each agent reasons

In Supervised mode, you review and approve each individual agent's findings before they contribute to the final package. This gives maximum control and transparency but requires more active participation.

---

## Checkpoint Timeout

If you don't respond to a checkpoint within 24 hours, ARCHON auto-approves with the default recommendation and continues. You'll receive an email notification before the timeout.

To disable auto-approval, upgrade to Enterprise plan and set `checkpoint_timeout = never` in your project settings.

---

## Redirect vs Reject

**Redirect** modifies the agents' direction without stopping the review:
- "Shift focus from performance to cost"
- "The payment service is out of scope — ignore it"
- "We're migrating off AWS next quarter, don't recommend AWS-specific solutions"

**Reject** stops the review entirely. Use this if the scope is wrong and a fresh start with better requirements would produce better results. Rejected reviews do not count against your monthly limit.
