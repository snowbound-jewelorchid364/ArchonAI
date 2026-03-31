# Python Rules — ARCHON

## Language & Runtime
- Python 3.11+ only
- Use `uv` for package management — never bare `pip`
- All dependencies in `pyproject.toml`

## Code Style
- `ruff` for linting and formatting — run before every commit
- Type hints on all functions — no untyped public functions
- No `Any` type unless explicitly justified with a comment
- Max line length: 100 characters
- Docstrings on all public classes and methods (Google style)

## Async
- All I/O must be async: database, HTTP, file system
- Use `asyncio.gather()` for parallel agent execution
- Never use `time.sleep()` — use `asyncio.sleep()`
- Use `httpx` for async HTTP — never `requests`

## Pydantic
- All agent inputs and outputs are Pydantic v2 models
- All API request/response schemas are Pydantic models
- Use `model_validator` not `validator` (v2 style)
- Never use `.dict()` — use `.model_dump()`

## Secrets & Config
- All secrets via environment variables
- Use `python-dotenv` for local dev
- Never commit `.env` files
- Config class using `pydantic-settings`

## Error Handling
- All agent errors must be caught and logged — never crash silently
- Use custom exception classes: `ArchonError`, `AgentError`, `RAGError`, `ResearchError`
- Always return partial output on timeout — never return nothing

## Testing
- `pytest` + `pytest-asyncio` for all tests
- Unit tests for: tools, output models, chunking, query generation
- Integration tests for: full agent run (use small test repo)
- Mock external APIs (Tavily, Exa, GitHub) in unit tests
- Never mock the database in integration tests — use test Postgres instance

## Imports
- Standard library first, then third-party, then local
- No wildcard imports (`from x import *`)
- Absolute imports only inside `api/` and `engine/`
