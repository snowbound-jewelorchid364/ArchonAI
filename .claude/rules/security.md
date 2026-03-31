# Security Rules — ARCHON

## Secrets Management
- All API keys in environment variables — never in code, never in logs
- Rotate keys immediately if accidentally committed
- GitHub tokens stored encrypted in database — never in plaintext
- Use separate API keys per environment (dev / staging / prod)

## Multi-Tenant Isolation
- Every database query MUST filter by `project_id` and `user_id`
- pgvector namespaces MUST be isolated per project — no cross-tenant RAG
- Redis job keys MUST be prefixed with user/project ID
- Never log user codebase content — only metadata

## Input Validation
- Validate all GitHub repo URLs before processing (allow-list github.com only at MVP)
- Validate repo size before indexing — reject > 500k LOC with clear error
- Sanitise all user-provided text before injecting into agent prompts
- Rate limit review triggers per user (max 5 concurrent reviews)

## Agent Sandboxing
- Agents must NOT have access to the production database directly
- Agents communicate via structured outputs — no shell access to host
- Outbound network from agents: Tavily, Exa, GitHub API, Claude API only
- No agent can write files outside `/tmp/archon-agent-<job-id>/`

## API Security
- All API routes require Clerk JWT authentication except `/health`
- Use HTTPS only — no HTTP in production
- CORS: allow-list frontend domain only
- Rate limiting: 100 req/min per user on API

## Data Retention
- User codebases are indexed per review — re-index on each new review
- Vector embeddings deleted when project is deleted
- Review packages stored max 90 days — notify user before deletion
- Never store raw codebase files — only embeddings + metadata
