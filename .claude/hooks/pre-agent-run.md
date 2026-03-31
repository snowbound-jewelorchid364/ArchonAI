# Pre-Agent-Run Hook

Before running or modifying any agent:

1. Read `.claude/rules/agents.md` — verify the agent follows all rules
2. Check `.claude/rules/output.md` — confirm output format compliance
3. Verify required tools are listed: `think`, `tavily_search`, `exa_search`, `file_read`
4. Confirm system prompt file exists at `agents/prompts/<agent_name>.md`

Flag any violations before proceeding.