# Local Development Setup

Get ARCHON running locally in under 15 minutes.

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Docker Desktop | Latest | docker.com/get-started |
| Python | 3.11+ | python.org |
| Node.js | 20+ | nodejs.org |
| uv | Latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| pnpm | 9+ | `npm install -g pnpm` |
| Git | Latest | git-scm.com |

---

## Step 1 — Clone and Bootstrap

```bash
git clone https://github.com/your-org/archon.git
cd archon
cp .env.example .env
```

Edit `.env` and fill in the required API keys (see [env-vars.md](./env-vars.md)).

---

## Step 2 — Start Infrastructure

```bash
docker-compose up -d postgres redis
```

This starts:
- PostgreSQL 16 with pgvector + pg_trgm extensions (port 5432)
- Redis 7 (port 6379)

Wait for both to be healthy:
```bash
docker-compose ps
# Both should show "healthy"
```

---

## Step 3 — API Setup

```bash
cd apps/api

# Install dependencies
uv sync

# Run database migrations
uv run alembic upgrade head

# Start API server
uv run uvicorn archon.main:app --reload --port 8000
```

API is now running at `http://localhost:8000`.
Swagger docs: `http://localhost:8000/docs`

---

## Step 4 — Agent Worker Setup

```bash
cd workers/agent

# Install dependencies
uv sync

# Start worker (in a new terminal)
uv run rq worker archon:analysis archon:ingest \
  --url redis://localhost:6379 \
  --with-scheduler
```

The worker is now consuming jobs from Redis.

---

## Step 5 — PDF Exporter Setup

```bash
cd services/pdf-exporter

# Install dependencies
pnpm install

# Install Puppeteer browser
pnpm exec puppeteer browsers install chrome

# Start service (in a new terminal)
pnpm dev
```

PDF exporter running at `http://localhost:3001`.

---

## Step 6 — Web App Setup

```bash
cd apps/web

# Install dependencies
pnpm install

# Copy env file
cp .env.local.example .env.local
# Edit .env.local with your Clerk keys

# Start dev server
pnpm dev
```

Web app running at `http://localhost:3000`.

---

## Step 7 — Verify Everything

```bash
# Check API health
curl http://localhost:8000/health/ready
# → {"status": "ready", "database": "ok", "redis": "ok"}

# Check PDF exporter
curl http://localhost:3001/health
# → {"status": "ok"}

# Check worker
cd workers/agent && uv run rq info
# → Should show worker connected and queues available
```

Open `http://localhost:3000` in your browser — you should see the ARCHON dashboard.

---

## Using the Makefile

```bash
make dev          # Start all services (requires Docker)
make test         # Run all test suites
make test-api     # Run API tests only
make test-worker  # Run worker tests only
make migrate      # Run pending database migrations
make migrate-down # Rollback last migration
make lint         # Run ruff + eslint
make format       # Auto-format all code
make seed         # Seed database with test data
```

---

## Common Issues

**pgvector extension missing**
```bash
docker-compose down -v
docker-compose up -d postgres redis
# The init.sql runs on first startup, creating extensions
```

**rq worker not picking up jobs**
```bash
# Verify Redis connection
redis-cli -u redis://localhost:6379 ping
# → PONG

# Check queue names match
rq info --url redis://localhost:6379
```

**Alembic migration error**
```bash
# Check current revision
uv run alembic current

# If head doesn't match
uv run alembic stamp head
uv run alembic upgrade head
```

**Clerk auth not working locally**
- Ensure `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` starts with `pk_test_` (not `pk_live_`)
- Check that `CLERK_SECRET_KEY` in `apps/api/.env` matches the same Clerk application

---

## Development Workflow

1. Make changes to a service
2. The relevant dev server auto-reloads (uvicorn `--reload`, Next.js HMR)
3. Run tests: `make test-api` or `make test-worker`
4. Commit with conventional commit message: `feat:`, `fix:`, `chore:`, `docs:`

See [testing-guide.md](./testing-guide.md) for the full test strategy.
