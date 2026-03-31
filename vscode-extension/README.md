# ARCHON — VS Code Extension

Run architecture reviews directly from VS Code. Powered by 6 specialist AI agents.

## Features

- **Run Review** — Trigger an ARCHON review on the current workspace
- **Mode Selection** — Choose from 14 review modes
- **Live Progress** — Watch agent progress in real-time via SSE
- **Findings Panel** — Browse findings by severity with file references
- **Review History** — Access past reviews from the sidebar

## Setup

1. Install from VS Code Marketplace
2. Set your API key: `Cmd+Shift+P` > `ARCHON: Configure`
3. Open a Git repository
4. Run: `Cmd+Shift+P` > `ARCHON: Run Review`

## Configuration

| Setting | Description | Default |
|---|---|---|
| `archon.apiUrl` | ARCHON API endpoint | `https://api.archon.dev` |
| `archon.apiKey` | Your API key | — |
| `archon.mode` | Default review mode | `review` |

## Requirements

- An ARCHON account with API access
- A workspace with a Git repository
