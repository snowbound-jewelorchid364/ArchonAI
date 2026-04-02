# ARCHON CLI

Your Frontier AI Architect, from the terminal.

## Install

```bash
pip install archon-cli
```

## Quick Start

```bash
archon login
archon status
archon run https://github.com/org/repo --mode review
archon run https://github.com/org/repo --no-stream
archon modes
archon history
```

## Authentication

The CLI uses the same bearer token model as the ARCHON web app/API.

```bash
archon login --api-url https://api.archon.dev --api-key <token>
archon status
archon logout
```

## Streaming

By default the CLI shows a live Rich SSE table for agent progress. Use `--no-stream` in CI or shells where streaming output is undesirable.

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
| feature_feasibility | Can we build X? |
| vendor_evaluator | Database / cloud choice |
| onboarding_accelerator | New CTO / senior hire |
| sunset_planner | Decommission a service |
