@AGENTS.md

# Claude-specific instructions

These apply to Claude Code sessions in addition to the shared rules above.

## Verification gate before committing a mathematical result

Once the question, argument, and evidence of a cycle are stable, pass every new
lemma, theorem, tree rule, or encoding through this gate before writing its
status line: (1) re-read the exact statement and proof of each earlier result the
argument uses, from the notebook, never from a summary or memory; (2) test the
claim against every counterexample, refutation, or obstruction recorded in
research/CLAIM_INDEX.md for the same objects (rules, trees, reader families);
(3) run the exhaustive checker for any rule, tree, or encoding change before
relying on it; (4) have a fresh-context reviewer, a subagent given only the draft
and the dependency anchors, try to break the argument, and resolve every gap it
reports. State in the entry which dependencies were re-read, which checks ran, and
the reviewer's verdict; a result whose gate is incomplete is recorded as
conditional, not as a working proof. A slower cycle with a verified result is
wanted; a fast cycle followed by a correction is not.
