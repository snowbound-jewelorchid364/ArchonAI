# ARCHON Security Model

---

## Security Principles

1. **Tenant isolation is absolute** — no user can ever access another user's data or codebase
2. **Least privilege everywhere** — every component gets only the access it needs
3. **Secrets never in plaintext** — encrypted at rest, never logged
4. **Defence in depth** — multiple independent controls, no single point of failure
5. **Secure by default** — the secure path is the easy path

---

## Authentication Architecture

ARCHON uses Clerk for identity management.

```
Browser → Clerk (login) → JWT issued
Browser → API (request with JWT in Authorization header)
API → Clerk JWKS endpoint (verify JWT signature)
API → Extract user_id from JWT sub claim
API → All DB queries filter by user_id
```

**JWT verification:**
- Algorithm: RS256 (asymmetric — private key never leaves Clerk)
- JWKS cached with 1-hour TTL, refreshed on 401
- Token expiry: 1 hour (Clerk manages refresh)
- No session cookies — stateless JWT only

---

## Multi-Tenant Data Isolation

Every database table that contains user data includes a `user_id` or `project_id` foreign key. Every query in every service MUST include this filter.

**Enforced patterns:**

```python
# services/project_service.py — CORRECT
async def get_project(project_id: UUID, user_id: UUID) -> Project:
    return await db.scalar(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.user_id == user_id)  # ← REQUIRED
    )

# NEVER do this — no user_id filter
async def get_project_insecure(project_id: UUID) -> Project:
    return await db.scalar(select(Project).where(Project.id == project_id))
```

**pgvector isolation:**
- `code_chunks` table has `project_id` column
- All vector similarity searches filter by `project_id` — no cross-tenant RAG

**Redis isolation:**
- All Redis keys prefixed with `user:{user_id}:` or `analysis:{analysis_id}:`
- Rate limit keys: `ratelimit:{user_id}:{endpoint}`

---

## Secrets Management

| Secret | Storage | Access |
|---|---|---|
| GitHub PAT (user) | DB — encrypted with `SECRET_KEY` | Decrypted in worker at job execution time only |
| API keys (Anthropic, Tavily, Exa) | Railway environment variables | Loaded at process start via `pydantic-settings` |
| Clerk keys | Railway environment variables | API process only |
| Stripe keys | Railway environment variables | API process only |
| PDF exporter API key | Railway environment variables (both services) | Internal service auth |
| DB password | Railway managed secret | Injected as `DATABASE_URL` |

**GitHub token encryption:**
```python
from cryptography.fernet import Fernet

def encrypt_token(token: str) -> str:
    f = Fernet(settings.SECRET_KEY)
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted: str) -> str:
    f = Fernet(settings.SECRET_KEY)
    return f.decrypt(encrypted.encode()).decode()
```

---

## Agent Sandboxing

Agent workers have constrained network access:

| Destination | Allowed | Why |
|---|---|---|
| `api.anthropic.com` | ✅ | Claude API |
| `api.tavily.com` | ✅ | Web research |
| `api.exa.ai` | ✅ | Web research |
| `api.github.com` | ✅ | Repo access |
| `voyage.ai` | ✅ | Embeddings |
| Internal DB + Redis | ✅ | Data storage |
| Internet (general) | ❌ | Block via Railway private networking |
| File system | `/tmp/archon-{job-id}/` only | Cleaned after job |

Agent tool calls that would write to arbitrary filesystem paths or make arbitrary HTTP requests are not exposed.

---

## Input Validation

**Repo URLs:**
- Allow-list: `https://github.com/` prefix only (MVP)
- Validate format before any network call
- Max repo size: 500k LOC — reject with 422 if exceeded

**Prompt injection defence:**
- User-provided requirements text is injected into agent system prompts with sanitisation
- Delimiters: `<user_requirements>` tags prevent content from modifying the system prompt structure
- All agent outputs are validated against Pydantic schemas before storage

**API rate limiting:**
- 100 requests/minute per user (all endpoints)
- 5 concurrent active reviews per user
- Implemented via Redis token bucket in middleware

---

## Data Handling

See [data-handling.md](./data-handling.md) for complete details.

**Summary:**
- Codebase data: embeddings only stored, never raw files
- Embeddings deleted when project is deleted
- Review packages retained 90 days, then deleted
- No codebase content ever logged
- TLS 1.3 in transit, AES-256 at rest (PostgreSQL TDE via Railway)

---

## Compliance Posture

| Framework | Status | Notes |
|---|---|---|
| SOC 2 Type II | Designed for | Architecture supports all Trust Service Criteria. Formal audit pending. |
| GDPR | Designed for | Right-to-erasure: `DELETE /users/me` cascades to all project + analysis data |
| HIPAA | Not certified | Do not store PHI. Enterprise plan with BAA: roadmap. |
| PCI-DSS | N/A | No card data processed (Stripe handles all card data) |

---

## Security Incident Response

See [incident-response.md](../runbooks/incident-response.md) for the general runbook.

**Security-specific steps:**

1. **Suspected data breach** → immediately rotate all API keys + DB password + SECRET_KEY
2. **Compromised GitHub token** → revoke token in GitHub, delete encrypted value from DB, notify user
3. **Prompt injection detected** → log payload for analysis, reject request, add pattern to blocklist
4. **Dependency vulnerability (CVE)** → assess exploitability, patch within 48h if CVSS ≥ 7.0
