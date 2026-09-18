@AGENTS.md

# Claude-specific instructions

These apply to Claude Code sessions in addition to the shared rules above.

## Verification gate before committing a mathematical result

Once the question, argument, and evidence of a cycle are stable, pass every new
lemma, theorem, tree rule, or encoding through this gate before writing its
status line: (1) re-read the exact statement and proof of each earlier result the
argument uses, from the notebook, never from a summary or memory, including its
probability convention (per reader or per source) before restating it; (2) test the
claim against every counterexample, refutation, or obstruction recorded in
research/CLAIM_INDEX.md for the same objects (rules, trees, reader families);
(3) run the exhaustive checker for any rule, tree, or encoding change before
relying on it; (4) have a fresh-context reviewer, a subagent given only the draft
and the dependency anchors, try to break the argument and name the hypotheses
the argument never uses; resolve every gap it reports and drop or justify every
unused hypothesis. Before drafting a corollary, check whether an earlier result
already gives it under fewer hypotheses than the cycle's own route; corollaries
have twice inherited route hypotheses that their statements did not need. A result
stated as a composition of recorded results is written as a lemma whose hypotheses
name one probability space and one tree; a reference to a sketch is not a proof. Keep one reviewer subagent on standby for the whole session
and continue it with SendMessage for each new draft; a new subagent would have
to re-establish the dependency context every time. Record the gate in a short
"Verification gate." paragraph of the entry (dependencies re-read, checks run,
the reviewer's verdict), not in the status line; a result whose gate is
incomplete is recorded as conditional, not as a working proof. A slower cycle
with a verified result is wanted; a fast cycle followed by a correction is not.

## Status lines

Keep an entry's `entry-meta` status line short: the status (working proof,
conditional result, conjecture, finite check, refutation) and at most one
clause of scope, then the cycle label. Details belong in the entry's sections.

## Shell hygiene

Never put a tool's file name in a Bash command that also runs `pkill -f` or
`pgrep -f`: the pattern matches the shell running the command and kills it
(exit 144), so nothing after it runs. Kill or check in one command, restart in
another.
