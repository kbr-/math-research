@AGENTS.md

# Claude-specific instructions

Shared research and framework rules are in AGENTS.md; computation policy is in
[COMPUTATION_RULES.md](COMPUTATION_RULES.md). Every rule and improvement goes there, not here (user,
17 October 2026: "Please don't perform improvements in CLAUDE.md. the place is AGENTS.md"); the
order of work for proofs, tests and summaries is AGENTS.md's "Order of work" section.

In a Spin loop driven by ScheduleWakeup, the delay is only a fallback re-entry point. Continue work
under AGENTS.md's Spin rules and re-arm with a short delay (about 60 seconds). Use long delays only
for genuinely blocked waits, such as a running reviewer or background batch.

Persistent worktrees and after-commit local synchronization follow AGENTS.md.
