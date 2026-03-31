Review an ARCHON agent definition for quality.

Read the agent file specified in the arguments (or ask which agent to review).

Check against `.claude/rules/agents.md`:
- Does the system prompt specify output format?
- Are all required output fields present?
- Does it use both tavily_search and exa_search?
- Does it use the `think` tool?
- Are citation rules enforced?
- Is timeout handling in place?
- Are findings specific and actionable (per `.claude/rules/output.md`)?

Produce a short review: what's good, what needs fixing, specific changes to make.