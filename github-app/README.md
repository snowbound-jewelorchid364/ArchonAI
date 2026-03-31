# ARCHON GitHub App

GitHub App that automatically triggers architecture reviews on pull requests.

## How It Works

1. User installs the ARCHON GitHub App on their repository
2. When a PR is opened/updated, GitHub sends a webhook
3. The app triggers an ARCHON review via the API
4. When complete, findings are posted as a PR comment

## Setup

1. Register a GitHub App using `app-manifest.json`
2. Set environment variables (see `.env.example`)
3. Deploy with Docker:

```bash
docker build -t archon-github-app .
docker run -p 8080:8080 --env-file .env archon-github-app
```

## Webhook Events

| Event | Action | Behavior |
|---|---|---|
| `pull_request` | `opened` | Trigger full review |
| `pull_request` | `synchronize` | Trigger incremental review |
| `pull_request` | `reopened` | Trigger full review |
| `installation` | `created` | Log new installation |

## Environment Variables

| Variable | Description |
|---|---|
| `GITHUB_APP_ID` | GitHub App ID |
| `GITHUB_APP_PRIVATE_KEY` | PEM private key |
| `GITHUB_WEBHOOK_SECRET` | Webhook secret for signature verification |
| `ARCHON_API_URL` | ARCHON API endpoint |
| `ARCHON_INTERNAL_KEY` | Internal API key for service-to-service auth |
