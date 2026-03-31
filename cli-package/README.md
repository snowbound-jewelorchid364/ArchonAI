# ARCHON CLI

Your Frontier AI Architect, from the terminal.

## Install

```bash
pip install archon-cli
```

## Quick Start

```bash
# Configure
archon configure

# Run a review
archon run https://github.com/org/repo --mode review

# List all modes
archon modes

# View history
archon history
```

## Modes

| Mode | Description |
|---|---|
| review | Audit existing codebase |
| design | New product from scratch |
| migration_planner | Modernisation project |
| compliance_auditor | SOC2/HIPAA/GDPR audit |
| due_diligence | Fundraise / M&A |
| incident_responder | P0/P1 outage |
| cost_optimiser | Cloud bill spike |
| pr_reviewer | Pull request opened |
| scaling_advisor | Traffic growing |
| drift_monitor | Weekly architecture check |
| feature_feasibility | "Can we build X?" |
| vendor_evaluator | Database / cloud choice |
| onboarding_accelerator | New CTO / senior hire |
| sunset_planner | Decommission a service |

## Configuration

```bash
# Interactive setup
archon configure

# Or use environment variables
export ARCHON_API_URL=https://api.archon.dev
export ARCHON_API_KEY=your_key_here
```
