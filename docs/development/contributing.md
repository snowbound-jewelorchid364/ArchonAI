# Contributing to ARCHON

---

## Development Workflow

1. Branch from `main`: `git checkout -b feat/your-feature`
2. Make changes, write tests
3. Run `make lint` and `make test`
4. Commit with conventional commits
5. Open a PR against `main`

---

## Conventional Commits

All commits must follow [Conventional Commits](https://conventionalcommits.org):

```
<type>(<scope>): <short description>

Types: feat | fix | chore | docs | refactor | test | perf
Scope: api | worker | web | pdf-exporter | rag | agents | db

Examples:
feat(agents): add retry logic to security architect agent
fix(rag): correct chunk overlap calculation for Python files
docs(api): update checkpoint endpoint request format
chore(deps): bump anthropic SDK to 0.40.0
```

---

## PR Requirements

- [ ] Tests written and passing (`make test`)
- [ ] Lint clean (`make lint`)
- [ ] No hardcoded secrets
- [ ] If DB schema changed: migration file included
- [ ] If new env var added: `env-vars.md` updated
- [ ] If architectural decision made: ADR added to `docs/architecture/`

---

## Code Review Standards

**Approve if:**
- Logic is correct and tests cover the change
- No security issues (injection, auth bypass, tenant isolation)
- Follows conventions in `.claude/rules/`

**Request changes if:**
- Missing tests for new logic
- Hardcoded secrets or config
- Cross-tenant data access possible
- Agent output not validated with Pydantic schema
- No citation on HIGH/CRITICAL findings

---

## Adding a New Architect Agent

1. Create `workers/agent/src/archon_agent/agents/<domain>_architect.py`
2. Create `workers/agent/src/archon_agent/prompts/<domain>_architect.md`
3. Add to `supervisor/orchestrator.py` fan-out list
4. Write unit tests in `tests/unit/test_<domain>_architect.py`
5. Run `/review-agent` skill to validate agent quality
6. Add agent to `docs/product/agents.md`
