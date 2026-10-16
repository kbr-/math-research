@AGENTS.md

# Claude-specific instructions

Shared research and framework rules are in AGENTS.md; computation policy is in
[COMPUTATION_RULES.md](COMPUTATION_RULES.md).

In a Spin loop driven by ScheduleWakeup, the delay is only a fallback re-entry point. Continue work
under AGENTS.md's Spin rules and re-arm with a short delay (about 60 seconds). Use long delays only
for genuinely blocked waits, such as a running reviewer or background batch.

Persistent worktrees and after-commit local synchronization follow AGENTS.md.

Order of drafting: before writing an entry's argument, write its cheapest competitor (the obvious
witness, the trivial bound, the positive control) and run the skeleton through
`tools/notebook-append.py DRAFT --check`; compare with the strongest result in view only after that.
