# ADR-001: Monorepo with Independent Service Boundaries

**Status:** Accepted
**Date:** 2026-03-31
**Deciders:** ARCHON founding team

---

## Context

ARCHON consists of four deployable processes: a Next.js web app, a FastAPI API server, a Python agent worker, and a Node.js PDF exporter. We need to decide how to organise these across repositories.

Options considered:
1. **Monorepo** — all services in one repo, deployed independently
2. **Polyrepo** — each service in its own repository
3. **Hybrid** — web + API in one repo, worker separate

---

## Decision

Use a **monorepo** with clearly defined service boundaries. Each service is independently deployable. Shared code is minimal and explicit (shared TypeScript types only).

---

## Rationale

**Contract enforcement at build time.** The TypeScript types shared between the web app and API are enforced by the compiler, not documentation. In a polyrepo, these drift silently and cause production bugs.

**Single source of truth for environment configuration.** All service `.env.example` files live in one place — onboarding a new developer is one `git clone`, not four.

**Simplified CI/CD.** Path-filtered GitHub Actions workflows run only the affected service's tests on each PR. A change to `workers/agent` does not trigger web app tests.

**Team size justifies it.** A polyrepo is appropriate when multiple autonomous teams own different services with incompatible release cadences. At ARCHON's founding team size, the coordination overhead of four separate repos exceeds the benefit.

---

## Consequences

- Railway deploys four separate services from one repo using the `rootDirectory` per service config
- CI uses path filters: `on: paths: ['apps/api/**']` per workflow
- The Python worker and API are separate pyproject.toml projects — they do not share a virtual environment
- `packages/shared-types` is the only cross-service shared package; it must have a stable, versioned interface
- No direct imports across service boundaries — all communication via HTTP or Redis

---

## Alternatives Rejected

**Polyrepo:** Rejected due to contract drift risk and onboarding friction at early stage.

**Hybrid (web+API together):** Rejected because the API and web app scale independently and have different deployment constraints. The API needs to be accessible by the worker; the web app does not.
