# Post-Session Hook

At the end of every session, auto-save progress:

1. Update `.claude/memory/build_phases.md` — mark any completed tasks
2. Add any new architectural decisions to `.claude/memory/decisions.md`
3. Update `CLAUDE.md` build phase status table if phase changed
4. If new tech choices were made, update `.claude/memory/tech_stack.md`

This ensures the next session starts with full context.