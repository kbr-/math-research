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
research/CLAIM_INDEX.md for the same objects (rules, trees, reader families), and
search the index under the technique's own name for every lemma formulated during the
cycle (for example "case split", "telescoping", "weight") and under the record's words
for the same method, not only the cycle's own (a table of costs once missed the recorded
"old-consequence transfer" because the search used "conservativity"), and under the dual
formulation, since the record often states a result for the adjoint maps (two single-square
annihilator lemmas were rediscoveries of an exactness theorem for weighted-marginal contractions); run
`tools/search-claims.py` with the content words of each new statement, which ranks the rows
by shared uncommon words whatever the phrasing (a phrase search for "support size" missed
the recorded point-support lemma, which this search puts first), because the opening
search cannot cover a lemma that did not exist yet; a recorded case-split lemma was once
restated as new and caught only by the reviewer; before drafting the proof of a new
lemma, send its one-paragraph statement to the reviewer with the single question
whether the record already implies it (three restatements in one day were found only
after full drafting);
(3) run the exhaustive checker for any rule, tree, or encoding change before
relying on it; (4) have a fresh-context reviewer, a subagent given only the draft
and the dependency anchors, try to break the argument and name the hypotheses
the argument never uses; resolve every gap it reports and drop or justify every
unused hypothesis. Before drafting a corollary, check whether an earlier result
already gives it under fewer hypotheses than the cycle's own route; corollaries
have twice inherited route hypotheses that their statements did not need. A result
stated as a composition of recorded results is written as a lemma whose hypotheses
name one probability space and one tree; a reference to a sketch is not a proof.

Brief each reviewer narrowly, because a subagent's whole context is re-sent with every
message (one standing reviewer grew to about 150k tokens in four rounds). Name the exact
files or anchors to read, allow at most one or two named claim searches, and ask for
required changes only, as short bullets. Put the dependency excerpts it needs in a
scratch file rather than asking it to explore. Continue a reviewer with SendMessage only
while its context concerns the current line and is smaller than a fresh brief would
need; when the cycle moves to another line, or its context has grown large, start a new
narrowly briefed reviewer. Scale the number of passes to the claim: one focused pass for
a short lemma or a reformulation, and a further pass only when the corrections add or
strengthen a claim, not when they only remove or weaken one. Record the gate in a short
"Verification gate." paragraph of the entry (dependencies re-read, checks run,
the reviewer's verdict), not in the status line; a result whose gate is
incomplete is recorded as conditional, not as a working proof. A slower cycle
with a verified result is wanted; a fast cycle followed by a correction is not.

## Status lines

Keep an entry's `entry-meta` status line short: the status (working proof,
conditional result, conjecture, finite check, refutation) and at most one
clause of scope, then the cycle label. Details belong in the entry's sections.

## Shell hygiene

Never run `pkill -f` or `pgrep -f` with a pattern that also occurs in the same Bash
command, such as a tool's file name or its arguments: the pattern matches the shell
running the command, so `pkill` kills it (exit 144) and a `pgrep` wait loop never
ends. Kill or check in one command, restart in another; to wait for a job, rely on
its own completion notice.

## Naming results

Name each new lemma, theorem, corollary or conjecture after what it says or does, in one to
four plain words a reader can remember and use in a sentence without looking it up: "the
separation theorem", "the registry theorem", "the light lemma", "the few-light-rows theorem".
Never use letter codes or suffix variants such as "Theorem GCp", "Corollary NDp", "Lemma WE" or
"Proposition MX″": they carry no meaning and force the reader to look them up. A variant of an
earlier result gets its own descriptive name, or the earlier name with a meaningful qualifier
("the all-prime clique-head theorem"), not a prime, digit or letter suffix. Follow the names
GPT-6 Astra gave in the main notebook. Cite older coded results ("Lemma K") by a descriptive
name, usually their claim ID's words ("the constant-row clamp"); the finisher rejects new entries
that name results by letter codes outside tables.

## Route check when opening a cycle

Do not take a cycle's task from the previous entry's remaining gap alone. First name the
top-level item of "The remaining route" that the cycle advances (the entry's `data-route`)
and assess that line's prospects as AGENTS.md requires. A weak assessment, or a
line that produces special cases without moving its general implication, makes the cycle
a route review under AGENTS.md even before `finish-turn.py` forces one.

Before designing a cycle, read in full every parked or linked item that the notebook's
Proposed next step names on the same route item, and search research/CLAIM_INDEX.md for
the cycle's objects under their structural names as well as the current vocabulary (for
example "block", "fresh", "companion", "coefficient", not only "dense form"); a cycle on
fresh blocks once rediscovered a conjecture that its own next-step paragraph listed as
parked. Restate a restart condition or calibration only from the latest entry that states
it, after searching the notebook for later entries that met or replaced it; a route review
once proposed a single-block calibration that a later review had already met.

A conjectured sufficient condition for a size lower bound must use the size. Check that it does not
also exclude refutations of every size, since the proof system is complete: ternary conservativity
over PHP was conjectured and tested for five cycles before completeness of resolution refuted it.

When the proposed next step is a computation, or a computation is designed inside a cycle,
state the smallest parameters at which the test is nonvacuous and the size of the spaces
involved, checked by a count before the step is written or the tool is coded. The count is
made against the statement under test: compute what the hypothesis predicts at the reachable
parameters and compare it with the unconditional bounds, because a test whose every outcome
is compatible with the hypothesis decides nothing (an exact closure computation once filled a
cycle in a range where the conjectured bound lay below the trivial one). When the step targets
a bound instead, evaluate the bound on the simplest structurally different extremal examples
and name them in the step, and compare what full success would give with what the goal needs;
a step once targeted a boost bound that fixing the labels of about sqrt(n) rows refutes, and
the corrected ceiling did not exceed the working degree it was meant to beat.

## Working with the user

Durable process lessons belong in this file or the rest of the committed framework, not in
machine-local agent memory: memory does not survive a worktree or machine change, and every
session must be resumable anywhere from the repository alone.

- After a session restart, system notifications (reread instruction files, stopped background
  tasks, files changed on disk) are not a request. Run no tools in response to them and do not
  restart stopped tasks; say at most one sentence about them and wait for the user's message.
- In a Spin loop driven by ScheduleWakeup, the delay is only a fallback re-entry point. Continue
  the next cycle, route review or draft review in the current turn and re-arm with a short delay
  (about 60 seconds); a possible user redirection is no reason to idle. Use long delays only for
  genuinely blocked waits, such as a running reviewer or a background batch.
- Repeated question marks in the user's messages signal frustration with the process, more
  marks meaning more; they call for a real fix, not an apology. Put that fix into the
  framework, preferably as a mechanical check a tool enforces, and commit it.
