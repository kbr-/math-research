@AGENTS.md

# Claude-specific instructions

Shared research and framework rules are in AGENTS.md; computation policy is in
[COMPUTATION_RULES.md](COMPUTATION_RULES.md).

In a Spin loop driven by ScheduleWakeup, the delay is only a fallback re-entry point. Continue work
under AGENTS.md's Spin rules and re-arm with a short delay (about 60 seconds). Use long delays only
for genuinely blocked waits, such as a running reviewer or background batch.

Persistent worktrees and after-commit local synchronization follow AGENTS.md.

When relaying what another agent, a reviewer or a tool found, carry its qualifiers word for word
(unverified, sketched, at these sizes, for this instance) into every summary of it: a report, a
commit message, a status line, a next step. A finding relayed is restated from its source, not from
memory of its gist (16 October 2026: qualifiers dropped in relaying a reviewer's computation and in
summaries of corrected items).
