# ARCHON API Reference

**Base URL:** `https://api.archon.ai/api/v1`

All requests require authentication via Clerk JWT:
```
Authorization: Bearer <clerk_jwt>
```

---

## Authentication

ARCHON uses Clerk for authentication. Include the JWT from Clerk in every request header.

**Getting a token (frontend):**
```typescript
import { useAuth } from '@clerk/nextjs'

const { getToken } = useAuth()
const token = await getToken()

fetch('/api/v1/projects', {
  headers: { Authorization: `Bearer ${token}` }
})
```

---

## Rate Limits

| Limit | Value |
|---|---|
| Requests per minute | 100 per user |
| Concurrent active reviews | 5 per user |
| Repo size limit | 500k lines of code |

Rate limit headers returned on every response:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1743422400
```

---

## Error Format

All errors follow this format:
```json
{
  "detail": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE",
  "request_id": "req_abc123"
}
```

Common error codes:
| Code | HTTP Status | Meaning |
|---|---|---|
| `UNAUTHORIZED` | 401 | Missing or invalid JWT |
| `FORBIDDEN` | 403 | Valid JWT but no access to this resource |
| `NOT_FOUND` | 404 | Resource does not exist |
| `VALIDATION_ERROR` | 422 | Request body failed validation |
| `RATE_LIMITED` | 429 | Too many requests |
| `REVIEW_LIMIT_REACHED` | 402 | Monthly review limit on current plan |
| `REPO_TOO_LARGE` | 422 | Repository exceeds 500k LOC limit |

---

## Projects

### List Projects
```
GET /projects
```

Response:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "My API",
      "repo_url": "https://github.com/org/repo",
      "repo_branch": "main",
      "repo_ingested": true,
      "latest_analysis": { "id": "uuid", "status": "completed", "created_at": "..." },
      "created_at": "2026-03-31T10:00:00Z"
    }
  ],
  "total": 3
}
```

### Create Project
```
POST /projects
```

Body:
```json
{
  "name": "My API",
  "repo_url": "https://github.com/org/repo",
  "repo_branch": "main",
  "description": "Optional context for agents"
}
```

### Trigger Repo Ingestion
```
POST /projects/:id/ingest
```

Enqueues a background job to clone, chunk, and embed the repository. Takes 2–10 minutes depending on repo size.

Poll `GET /projects/:id/ingest/status` for completion.

---

## Analyses

### Start Analysis
```
POST /projects/:id/analyses
```

Body:
```json
{
  "checkpoint_mode": "balanced",
  "requirements_text": "Focus on security for SOC2 compliance. We use AWS only."
}
```

`checkpoint_mode` values: `autopilot` | `balanced` | `supervised`

Response: `202 Accepted` with analysis object.

### Stream Progress (SSE)
```
GET /analyses/:id/events?token=<clerk_jwt>
```

Note: Token passed as query param because `EventSource` does not support custom headers.

Event types:
```
event: agent_progress
data: {"agent_type": "security", "progress_pct": 45, "current_step": "Searching for CVEs..."}

event: checkpoint_ready
data: {"checkpoint_id": "uuid", "checkpoint_num": 2, "title": "Findings Review"}

event: analysis_complete
data: {"analysis_id": "uuid", "finding_count": 23, "output_count": 12}

event: error
data: {"message": "Agent failed: ...", "agent_type": "cloud"}
```

---

## Checkpoints

### Approve Checkpoint
```
POST /checkpoints/:id/approve
```

Body (optional):
```json
{ "feedback": "Looks good, focus more on the data layer" }
```

### Edit and Approve
```
POST /checkpoints/:id/edit
```

Body:
```json
{
  "edited_payload": { "scope": { "excluded_services": ["legacy-php"] } },
  "feedback": "Excluding the legacy service from analysis"
}
```

### Reject Checkpoint
```
POST /checkpoints/:id/reject
```

Body:
```json
{ "feedback": "Scope is wrong — this is not a microservices architecture" }
```

---

## Outputs

### Get All Outputs
```
GET /analyses/:id/outputs/summary
```

Returns all output types in one response:
```json
{
  "executive_summary": { "id": "uuid", "content": "..." },
  "adrs": [{ "id": "uuid", "title": "ADR-001: ...", "content": "..." }],
  "terraform": [{ "id": "uuid", "title": "main.tf", "content": "..." }],
  "diagrams": [{ "id": "uuid", "title": "system-context", "content": "..." }],
  "risk_register": { "id": "uuid", "content_json": { "items": [...] } }
}
```

---

## Exports

### Export as PDF
```
POST /analyses/:id/export/pdf
```

Returns:
```json
{ "job_id": "export_abc123" }
```

Poll status:
```
GET /exports/export_abc123/status
→ { "status": "pending" | "processing" | "complete" | "failed" }
```

Download when complete:
```
GET /exports/export_abc123/download
→ Binary PDF stream
   Content-Type: application/pdf
   Content-Disposition: attachment; filename="archon-review-2026-03-31.pdf"
```

---

## Billing

### Get Current Plan
```
GET /billing/plan
```

Response:
```json
{
  "plan": "starter",
  "status": "active",
  "analyses_used": 2,
  "analyses_limit": 3,
  "period_end": "2026-04-30T00:00:00Z"
}
```

### Upgrade Plan
```
POST /billing/checkout
```

Body:
```json
{ "plan": "pro" }
```

Response:
```json
{ "checkout_url": "https://checkout.stripe.com/..." }
```

Redirect user to `checkout_url`.
