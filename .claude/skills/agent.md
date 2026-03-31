Create a new ARCHON architect agent.

Given the agent name and domain from the arguments:

1. Create `agents/<agent_name>.py` — Python class wrapping Strands Agent
2. Create `agents/prompts/<agent_name>.md` — system prompt
3. Add the agent to `engine/supervisor.py` fan-out list
4. Register tools appropriate for the domain

Follow the agent structure in `.claude/rules/agents.md` exactly.
Follow the output model in `output/models.py`.

After creating, confirm what was created and what still needs to be done (tests, integration).