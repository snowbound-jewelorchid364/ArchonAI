# Testing Guide

ARCHON's test strategy: unit tests for logic, integration tests for service boundaries, no mocking of the database.

---

## Test Stack

| Tool | Purpose |
|---|---|
| `pytest` | Python test runner |
| `pytest-asyncio` | Async test support |
| `httpx` | Async HTTP client for API integration tests |
| `factory-boy` | Test data factories |
| `pytest-mock` | Mock external APIs (Tavily, Exa, Claude, GitHub) |
| `testcontainers` | Ephemeral Postgres + Redis for integration tests |
| `vitest` | Frontend unit tests |
| `playwright` | E2E browser tests (Phase 3+) |

---

## Test Pyramid

```
         /\
        /E2E\         ← Few (Playwright, Phase 3+)
       /------\
      /  Integ  \     ← Some (full HTTP round-trips, real DB)
     /------------\
    /    Unit      \  ← Many (logic, tools, output builders)
   /________________\
```

---

## Running Tests

```bash
# All tests
make test

# API only
make test-api

# Worker only
make test-worker

# With coverage
cd apps/api && uv run pytest --cov=archon --cov-report=html

# Specific test file
cd workers/agent && uv run pytest tests/unit/test_adr_builder.py -v

# Specific test
uv run pytest tests/unit/test_adr_builder.py::test_adr_from_finding -v
```

---

## Unit Tests

Unit tests cover isolated logic with no I/O. External APIs are always mocked.

### What to unit test

**Output builders** — deterministic logic, easy to test:
```python
# tests/unit/test_adr_builder.py
def test_adr_from_security_finding():
    finding = FindingFactory.build(
        domain="security",
        severity=Severity.HIGH,
        title="No encryption at rest"
    )
    adr = build_adr(finding)
    assert adr.title == "ADR-001: Enable Encryption at Rest"
    assert "AES-256" in adr.content
    assert adr.status == "Proposed"
```

**Chunker** — deterministic text splitting:
```python
def test_chunk_respects_function_boundaries():
    code = load_fixture("python_with_classes.py")
    chunks = chunk_code(code, language="python", max_tokens=512)
    # No chunk should split a function definition
    for chunk in chunks:
        assert not has_split_function(chunk)
```

**Research query generator** — verifiable domain-specific output:
```python
def test_security_agent_generates_cve_queries():
    context = ReviewContextFactory.build(agent_type="security")
    queries = generate_queries(context)
    assert any("CVE" in q or "vulnerability" in q for q in queries)
    assert len(queries) >= 3
```

### Mocking external APIs

```python
# conftest.py
@pytest.fixture
def mock_tavily(mocker):
    return mocker.patch(
        "archon_agent.tools.web_research.TavilyClient.search",
        return_value=TavilyResultFactory.build_batch(5)
    )

@pytest.fixture
def mock_anthropic(mocker):
    return mocker.patch(
        "strands.Agent.__call__",
        return_value=AgentResponseFactory.build()
    )
```

---

## Integration Tests

Integration tests use a real database and Redis. External APIs (Claude, Tavily, Exa, GitHub) are mocked.

### Test database setup

```python
# conftest.py
@pytest.fixture(scope="session")
def test_db():
    with PostgresContainer("postgres:16") as pg:
        engine = create_engine(pg.get_connection_url())
        # Run migrations
        alembic_upgrade(engine, "head")
        yield engine

@pytest.fixture(autouse=True)
def rollback_after_test(test_db):
    with test_db.begin() as conn:
        yield conn
        conn.rollback()  # Each test gets a clean state
```

### API integration tests

```python
# tests/integration/test_projects_api.py
async def test_create_project_returns_201(client, auth_headers):
    response = await client.post(
        "/api/v1/projects",
        json={"name": "My API", "repo_url": "https://github.com/test/repo"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "My API"
    assert "id" in response.json()

async def test_create_project_validates_github_url(client, auth_headers):
    response = await client.post(
        "/api/v1/projects",
        json={"name": "Bad", "repo_url": "https://gitlab.com/test/repo"},
        headers=auth_headers
    )
    assert response.status_code == 422
    assert "github.com" in response.json()["detail"]
```

### Worker integration tests

```python
# tests/integration/test_run_analysis_job.py
def test_full_analysis_job_completes(test_db, mock_anthropic, mock_tavily, mock_exa):
    analysis = AnalysisFactory.create(project__repo_url=TEST_REPO_URL)

    run_analysis(analysis.id)

    # Verify all 6 agents completed
    agent_runs = test_db.query(AgentRun).filter_by(analysis_id=analysis.id).all()
    assert len(agent_runs) == 6
    assert all(run.status == "completed" for run in agent_runs)

    # Verify outputs were generated
    outputs = test_db.query(Output).filter_by(analysis_id=analysis.id).all()
    output_types = {o.output_type for o in outputs}
    assert "executive_summary" in output_types
    assert "risk_register" in output_types
```

---

## Test Fixtures

Small sample repos in `workers/agent/tests/fixtures/test-repos/` for integration tests:

```
fixtures/test-repos/
├── simple-fastapi/          ← ~20 files, 1 service, Python
│   ├── main.py
│   ├── models.py
│   └── requirements.txt
└── microservices/           ← ~60 files, 3 services, mixed
    ├── auth-service/
    ├── api-service/
    └── worker-service/
```

---

## Coverage Targets

| Package | Minimum Coverage |
|---|---|
| `apps/api` — services/ | 85% |
| `apps/api` — routers/ | 70% |
| `workers/agent` — agents/ | 75% |
| `workers/agent` — outputs/ | 90% |
| `workers/agent` — rag/ | 80% |

Coverage is enforced in CI — PRs that drop below threshold are blocked.

---

## What NOT to Test

- shadcn/ui components (third-party)
- Alembic migration files (test by running migrations)
- Configuration classes (tested implicitly)
- `__init__.py` barrel files
- Direct SQL queries (tested via service integration tests)
