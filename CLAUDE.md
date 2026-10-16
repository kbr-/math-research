@AGENTS.md

# Claude-specific instructions

Shared research and framework rules are in AGENTS.md; computation policy is in
[COMPUTATION_RULES.md](COMPUTATION_RULES.md).

In a Spin loop driven by ScheduleWakeup, the delay is only a fallback re-entry point. Continue work
under AGENTS.md's Spin rules and re-arm with a short delay (about 60 seconds). Use long delays only
for genuinely blocked waits, such as a running reviewer or background batch.

Persistent worktrees and after-commit local synchronization follow AGENTS.md.

Order of work for any proof, test, witness, next attempt or summary (each line from a mistake of 16
October 2026; a rule added after a mistake is applied at once to the next text written):

- First draft the Plainest bound: the bare count or the oldest recorded lemma on the instance,
  before any method is chosen.
- Check a witness's or construction's constraints as functions of the growing parameter, in the
  limit, never at the size written for.
- Recheck each step's preconditions (independence, quantifier ranges, domains), not only its
  arithmetic.
- Write a negative sentence ("no estimate applies", "the record lacks it") only beside the attempt
  that failed.
- Write every summary (title, New mathematics, Bearing, commit message, report) last, from the final
  statement with its hypotheses and qualifiers; relay what a reviewer, agent or tool found from its
  source, with its qualifiers word for word.
