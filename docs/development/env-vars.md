# Environment Variables

Complete reference for all environment variables across ARCHON services.

---

## Root `.env` (shared by docker-compose)

```bash
POSTGRES_USER=archon
POSTGRES_PASSWORD=archon
POSTGRES_DB=archon
POSTGRES_PORT=5432
REDIS_PORT=6379
```

---

## `apps/api`

### Application
| Variable | Required | Default | Description |
|---|---|---|---|
| `APP_ENV` | Yes | `development` | `development` / `staging` / `production` |
| `APP_VERSION` | No | `0.0.0` | Injected by CI from git tag |
| `LOG_LEVEL` | No | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `SECRET_KEY` | Yes | — | HMAC key for internal tokens — min 32 chars |

### Database
| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | `postgresql+asyncpg://user:pass@host:5432/archon` |
| `DATABASE_POOL_SIZE` | No | Async connection pool size (default: 10) |
| `DATABASE_MAX_OVERFLOW` | No | Max connections above pool size (default: 20) |

### Redis
| Variable | Required | Description |
|---|---|---|
| `REDIS_URL` | Yes | `redis://localhost:6379/0` |
| `REDIS_RATE_LIMIT_DB` | No | Separate Redis DB index for rate limits (default: 1) |

### Clerk (Auth)
| Variable | Required | Description |
|---|---|---|
| `CLERK_SECRET_KEY` | Yes | Backend secret key from Clerk dashboard (`sk_test_...`) |
| `CLERK_WEBHOOK_SECRET` | Yes | Webhook signing secret from Clerk dashboard (`whsec_...`) |

### Stripe (Billing)
| Variable | Required | Description |
|---|---|---|
| `STRIPE_SECRET_KEY` | Yes | Secret key (`sk_test_...` or `sk_live_...`) |
| `STRIPE_WEBHOOK_SECRET` | Yes | Webhook signing secret (`whsec_...`) |
| `STRIPE_PRICE_ID_STARTER` | Yes | Price ID for Starter plan (`price_...`) |
| `STRIPE_PRICE_ID_PRO` | Yes | Price ID for Pro plan (`price_...`) |
| `STRIPE_PRICE_ID_ENTERPRISE` | No | Price ID for Enterprise plan |

### Internal Services
| Variable | Required | Default | Description |
|---|---|---|---|
| `PDF_EXPORTER_URL` | Yes | `http://pdf-exporter:3001` | Internal URL for PDF exporter service |
| `PDF_EXPORTER_API_KEY` | Yes | — | Shared secret for internal service auth |

### Observability
| Variable | Required | Description |
|---|---|---|
| `SENTRY_DSN` | No | Sentry error tracking DSN |
| `PROMETHEUS_ENABLED` | No | Enable Prometheus metrics endpoint (default: true) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | No | OpenTelemetry collector endpoint |

---

## `workers/agent`

### Application
| Variable | Required | Default | Description |
|---|---|---|---|
| `APP_ENV` | Yes | `development` | Environment name |
| `LOG_LEVEL` | No | `INFO` | Log level |
| `WORKER_CONCURRENCY` | No | `4` | Number of concurrent rq workers |
| `WORKER_QUEUES` | No | `archon:analysis,archon:ingest` | Queues to consume (priority order) |

### Database
| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | `postgresql+psycopg2://user:pass@host:5432/archon` — **sync driver** |
| `DATABASE_POOL_SIZE` | No | Smaller pool than API (default: 5) |

### Redis
| Variable | Required | Description |
|---|---|---|
| `REDIS_URL` | Yes | `redis://localhost:6379/0` |
| `RQ_JOB_TIMEOUT` | No | Max seconds per job before rq kills it (default: 900) |
| `RQ_RESULT_TTL` | No | Keep job results in Redis for N seconds (default: 86400) |

### LLM
| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Claude API key (`sk-ant-...`) |
| `ANTHROPIC_MODEL` | No | Model ID (default: `claude-opus-4-6`) |
| `ANTHROPIC_MAX_TOKENS` | No | Max output tokens per agent call (default: 8192) |
| `ANTHROPIC_REQUESTS_PER_MINUTE` | No | Rate limit throttle (default: 50) |

### Web Research
| Variable | Required | Description |
|---|---|---|
| `TAVILY_API_KEY` | Yes | Tavily Search API key (`tvly-...`) |
| `EXA_API_KEY` | Yes | Exa Search API key |
| `WEB_RESEARCH_MAX_RESULTS` | No | Max results per search query (default: 10) |
| `WEB_RESEARCH_TIMEOUT_SECS` | No | HTTP timeout for search calls (default: 15) |

### Embeddings
| Variable | Required | Description |
|---|---|---|
| `VOYAGE_API_KEY` | Yes | Voyage AI API key (`pa-...`) — for code embeddings |
| `EMBEDDING_MODEL` | No | Embedding model (default: `voyage-code-2`) |
| `EMBEDDING_DIMENSIONS` | No | Vector dimensions — must match pgvector column (default: 1536) |
| `EMBEDDING_BATCH_SIZE` | No | Chunks per embedding API batch call (default: 32) |

### GitHub
| Variable | Required | Description |
|---|---|---|
| `GITHUB_TOKEN` | Yes | Personal Access Token for public repo access (`ghp_...`) |
| `GITHUB_APP_ID` | No | GitHub App ID for private repo access |
| `GITHUB_APP_PRIVATE_KEY` | No | GitHub App private key (base64-encoded PEM) |

### RAG
| Variable | Required | Default | Description |
|---|---|---|---|
| `RAG_CHUNK_SIZE_TOKENS` | No | `512` | Max tokens per code chunk |
| `RAG_CHUNK_OVERLAP_TOKENS` | No | `64` | Token overlap between adjacent chunks |
| `RAG_SEARCH_TOP_K` | No | `20` | Number of chunks retrieved per query |
| `RAG_HYBRID_ALPHA` | No | `0.7` | Blend weight: 1.0=pure vector, 0.0=pure BM25 |

### Checkpoint
| Variable | Required | Default | Description |
|---|---|---|---|
| `CHECKPOINT_POLL_INTERVAL_SECS` | No | `5` | How often worker polls DB for checkpoint decision |
| `CHECKPOINT_TIMEOUT_SECS` | No | `86400` | Auto-proceed after N seconds if no user response |

### Observability
| Variable | Required | Description |
|---|---|---|
| `SENTRY_DSN` | No | Sentry DSN — same as API for unified error tracking |
| `PROMETHEUS_PORT` | No | Metrics server port (default: 9000) |

---

## `apps/web`

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_APP_URL` | Yes | Full URL of the web app (e.g., `https://app.archon.ai`) |
| `NEXT_PUBLIC_API_URL` | Yes | Backend API base URL (e.g., `https://api.archon.ai/api/v1`) |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Yes | Clerk publishable key (`pk_test_...` or `pk_live_...`) |
| `CLERK_SECRET_KEY` | Yes | Clerk secret key (server-side only) |
| `NEXT_PUBLIC_CLERK_SIGN_IN_URL` | No | Sign-in page path (default: `/sign-in`) |
| `NEXT_PUBLIC_CLERK_SIGN_UP_URL` | No | Sign-up page path (default: `/sign-up`) |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Yes | Stripe publishable key |
| `NEXT_PUBLIC_POSTHOG_KEY` | No | PostHog analytics key |
| `NEXT_PUBLIC_POSTHOG_HOST` | No | PostHog host URL |

---

## `services/pdf-exporter`

| Variable | Required | Default | Description |
|---|---|---|---|
| `PORT` | No | `3001` | HTTP server port |
| `NODE_ENV` | No | `development` | Node environment |
| `LOG_LEVEL` | No | `info` | Log level |
| `INTERNAL_API_KEY` | Yes | — | Shared secret — must match `PDF_EXPORTER_API_KEY` in API |
| `PDF_TIMEOUT_MS` | No | `30000` | Max time to render one PDF |
| `PDF_MAX_CONCURRENT` | No | `3` | Max concurrent Puppeteer browser instances |
| `PUPPETEER_EXECUTABLE_PATH` | No | — | Custom Chrome binary path (for Alpine Linux containers) |

---

## Required for MVP (minimum viable set)

To run a complete local review end-to-end, you need at minimum:

```bash
ANTHROPIC_API_KEY=       # Agent LLM
TAVILY_API_KEY=          # Web research
EXA_API_KEY=             # Web research
VOYAGE_API_KEY=          # Code embeddings
GITHUB_TOKEN=            # Repo access
CLERK_SECRET_KEY=        # Auth (get from clerk.com)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=       # Billing (get from stripe.com, test mode OK)
STRIPE_WEBHOOK_SECRET=
PDF_EXPORTER_API_KEY=any-random-string
```

Sentry, PostHog, Prometheus, and GitHub App credentials are optional for local development.
