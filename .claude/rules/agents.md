# Agent Rules — ARCHON

## Agent Design

- Every specialist agent wraps a Strands `Agent` instance
- System prompts live in `agents/prompts/<agent_name>.md` — never inline strings
- All agent outputs MUST be Pydantic models — never raw strings
- Agents must be stateless — all context injected at call time
- Never let an agent call another agent directly — supervisor only

## Required Output Fields

Every agent output must include:
```python
findings: list[Finding]       # domain-specific findings
citations: list[Citation]     # web sources used
artifacts: list[Artifact]     # ADRs, IaC, diagrams
confidence: float             # 0.0 - 1.0 overall confidence
domain: str                   # agent domain name
duration_seconds: float       # how long the agent ran
```

## Citation Rules

- Every HIGH or CRITICAL finding requires ≥ 1 citation
- Citations must include: url, title, excerpt (≤ 300 chars), published_date
- No hallucinated URLs — only URLs returned by Tavily or Exa
- Credibility score must be computed and stored per citation

## Tool Usage

- Always use `think` tool before producing final findings — structured reasoning
- Always search with both Tavily and Exa — never just one
- File reads should be targeted — read specific files, not entire repos
- Use `python_repl` only for parsing/analysis — no side effects

## Timeouts & Failures

- Hard timeout per agent: 20 minutes
- On timeout: return whatever findings were produced so far
- On tool failure: log, skip that tool, continue with available data
- On LLM error: retry up to 3 times with exponential backoff
- Never return an empty findings list — always produce something

## Prompt Quality

- System prompts must specify output format explicitly
- Include examples of good findings in the prompt
- Instruct agents to be specific — "use encryption" is bad, "enable AES-256 at rest via AWS KMS with key rotation every 90 days" is good
- Instruct agents to distinguish between "found in codebase" vs "best practice recommendation"

## Supervisor (team-architecture)

- Fan out all 6 agents using `asyncio.gather()` — true parallel execution
- Collect all outputs before merging
- Deduplicate findings that appear in multiple agents (same issue, different domain)
- Cross-reference findings — note when security + cloud agents agree on the same risk
- Produce executive summary last, after all agent outputs are merged
