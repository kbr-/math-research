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

- Choose a target by what is true at the goal, not by what the tools at hand prove easily: a target
  the tools reach easily is first tried for refutation on its plainest counterexample.
- First draft the Plainest bound: the bare count or the oldest recorded lemma on the instance,
  before any method is chosen.
- Check a witness's or construction's constraints as functions of the growing parameter, in the
  limit, never at the size written for.
- Recheck each step's preconditions (independence, quantifier ranges, domains), not only its
  arithmetic.
- Write a negative sentence ("no estimate applies", "the record lacks it") only beside the attempt
  that failed.
- Write the Record comparison before New mathematics, the title or any sentence calling a result
  new: compare from the record's side (the entries a draft leans on, their dependencies and
  dependents), not from the draft's own wording, and only then decide what is new.
- Write every summary (title, New mathematics, Bearing, commit message, report) last, from the final
  statement with its hypotheses and qualifiers; relay what a reviewer, agent or tool found from its
  source, with its qualifiers word for word, and explain a failing check only by quoting the lines
  of its output that show the cause.
- When a computation agrees with what was expected, write next what it does not show, before the
  sentence that concludes from it; and before posing a statement drawn from one worked construction,
  write down the construction most unlike it and check the statement there.
- Before writing any durable text (docstring, commit message, entry, reply), list each figure and
  finding it will carry beside its source (a saved output, a named agent's report, a proof in the
  entry); one whose only source is another agent's report is written as that agent's, or recomputed
  and saved first.
- Run a required tool or check so that it does its job, never in the cheapest form that passes its
  gate (an output cut short, a paragraph filled with placeholder words, a search run only to be
  logged): if a gate's form is a burden, change the gate in the open, not its use.
- Before every reviewer brief, reread the draft once against each item of this list and against
  AGENTS.md's rules on statements (free parameters at their whole range, searches under other
  names), item by item, rather than relying on having known them while drafting.
