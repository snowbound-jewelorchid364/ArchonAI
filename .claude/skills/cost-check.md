Estimate the Claude API cost per architecture review for ARCHON.

Calculate based on:
- 6 agents running in parallel
- Each agent: system prompt (~2k tokens) + RAG context (~3k tokens) + web research (~5k tokens) + reasoning (~2k tokens) = ~12k input tokens
- Each agent output: ~3k tokens
- Supervisor merge: ~10k input + ~5k output tokens
- Total per review: input + output tokens × claude-opus-4-6 pricing

Show:
1. Token breakdown per agent and supervisor
2. Cost at current claude-opus-4-6 pricing
3. Cost if research phases use claude-sonnet-4-6 instead
4. Recommended pricing for Starter ($49/3 reviews) and Pro ($199/unlimited) plans
5. COGS margin at each plan tier

Use current Anthropic API pricing from the web if needed.