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

The first lines drafted for any proof, test, witness or next attempt are its Plainest bound: the
bare count or oldest recorded lemma evaluated on its instance, written before any method is chosen.
A rule written about this after a mistake does not change the order of work; drafting it first does
(16 October 2026: the baseline rule of the morning did not stop the same mistake in the evening).

A recheck of a proof reads each step's preconditions (independence, the range a quantifier covers,
the domain a construction needs) as well as its arithmetic: the numbers of a step can all be right
while the tool it uses does not apply (16 October 2026: a recheck confirmed every constant of a
concentration step whose summands were dependent).

A negative sentence ("no estimate applies", "nothing covers it", "the record lacks it") is a claim
like any other: write it only beside the attempt that failed, never as the plausible default when a
paragraph needs filling (16 October 2026: "no one-dimensional estimate applies" was false for a
sheared witness).
