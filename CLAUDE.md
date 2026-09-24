@AGENTS.md

# Claude-specific instructions

These apply to Claude Code sessions in addition to the shared rules above.

## Verification gate before committing a mathematical result

Once the question, argument, and evidence of a cycle are stable, pass every new
lemma, theorem, rule, or encoding through this gate before writing its status line:

1. Re-read the exact statement and proof of each earlier result the argument uses,
   from the notebook, never from a summary or memory, including its conventions
   (such as how probabilities are normalized) before restating it. When the user or a
   source points to a publication or a Lean file, read the theorem statement there
   first, and read every version that the "Newer versions" line of
   `tools/search-claims.py` lists. Compare their hypotheses one by one (field, ranges,
   encoding) and use the version whose hypotheses the argument meets: a later or
   formalized version can drop one hypothesis and add another, such as a narrower field.
   Record a `refines` edge only when one version implies the other.
2. Test the claim against every counterexample, refutation, or obstruction
   recorded in research/CLAIM_INDEX.md for the same objects. Search the index for
   every lemma formulated during the cycle in four ways:
   - under the technique's own name;
   - under the record's words for the same method, not only the cycle's own, since
     one search missed a recorded result because it used a synonym;
   - under the dual or adjoint formulation, since the record often states a result for
     the adjoint maps and restating it for the original maps is a rediscovery;
   - with `tools/search-claims.py` and the content words of the statement, which
     ranks rows by shared uncommon words whatever the phrasing.

   The opening search cannot cover a lemma that did not exist yet. Before drafting
   the proof of a new lemma, send its one-paragraph statement to the reviewer with
   the single question whether the record already implies it. Restatements are
   otherwise found only after full drafting.
3. Run the exhaustive checker for any rule, tree, or encoding change before relying
   on it.
4. Have a fresh-context reviewer, a subagent given only the draft and the dependency
   anchors, try to break the argument and name the hypotheses the argument never
   uses. Resolve every gap it reports, and drop or justify every unused hypothesis.

Before drafting a corollary, check whether an earlier result already gives it under
fewer hypotheses than the cycle's own route, since corollaries tend to inherit route
hypotheses that their statements do not need. A result stated as a composition of
recorded results is written as a lemma whose hypotheses name one common setting; a
reference to a sketch is not a proof.

Brief each reviewer narrowly, because a subagent's whole context is re-sent with every
message. Name the exact files or anchors to read, allow at most one or two named claim
searches, and ask for required changes only, as short bullets. Put the dependency
excerpts it needs in a scratch file rather than asking it to explore. Continue a
reviewer with SendMessage only while its context concerns the current line and is
smaller than a fresh brief would need; otherwise start a new narrowly briefed reviewer.
Scale the number of passes to the claim: one focused pass for a short lemma or a
reformulation, and a further pass only when the corrections add or strengthen a claim,
not when they only remove or weaken one.

Record the gate in a short "Verification gate." paragraph of the entry (dependencies
re-read, checks run, the reviewer's verdict), not in the status line. A result whose
gate is incomplete is recorded as conditional, not as a working proof. A slower cycle
with a verified result is wanted; a fast cycle followed by a correction is not.

## Status lines

Keep an entry's `entry-meta` status line short: the status (working proof,
conditional result, conjecture, finite check, refutation) and at most one
clause of scope, then the cycle label. Details belong in the entry's sections.

## Shell hygiene

- Never run `pkill -f` or `pgrep -f` with a pattern that also occurs in the same Bash
  command. The pattern matches the shell running the command, so `pkill` kills that
  shell and a `pgrep` wait loop never ends. Kill or check in one command, restart in
  another, and to wait for a job rely on its own completion notice.
- Read the output of `./compute.sh start` and `./tools/finish-turn.py` in full. Never pipe it through
  `head`, `tail` or `grep`: its turn guidance and warnings can appear anywhere in it.
- Never discard the output or exit status of a command whose failure would silently
  corrupt a record, such as `./compute.sh phase` or `start`: an invalid argument exits
  with an error that a redirection hides.

## Designing and running computations

Apply every rule below before launching a run.

1. **Decide first whether the test can decide.** Before coding, and in the same cycle:
   - state the smallest parameters at which the test is nonvacuous, and the sizes of
     the spaces involved;
   - count what the statement under test predicts at the reachable parameters, and
     compare it with the unconditional bounds;
   - check that the reachable parameters satisfy the statement's hypotheses.

   A test whose every outcome is compatible with the statement, or whose inputs lie
   outside its hypotheses, decides nothing. Put the count in the entry. When the step
   targets a bound, evaluate the bound on the simplest structurally different extremal
   examples, and compare what full success would give with what the goal needs.
2. **Compute the statement's own quantity, on inputs that meet its hypotheses.**
   Write the tested statement in the script's docstring, generate inputs that satisfy
   its hypotheses, and assert them in code. A stronger or weaker surrogate quantity
   answers a different question.
3. **Heavy loops belong in a compiled kernel.** This includes row and product
   generation, not only elimination. Use C or C++, with OpenMP where it parallelizes.
   Python only orchestrates, and a Python-only computation needs evidence that it runs
   in seconds. Validate a new kernel against a reference implementation on small cases
   before scaling it. Declare foreign-function argument types, since undeclared
   pointers are truncated.
4. **One pass per series, shared work once.** Compute every parameter of a series in
   one incremental pass, never one full recomputation per parameter: results for
   nested inputs continue from the previous ones. Compute shared prefixes, such as a
   common base or a common random sequence, once and copy them. Count the expensive
   operations the design performs (eliminations, closures, enumerations) and compare
   the count with the number of distinct objects involved: when several questions
   (cutoffs, orders, degree bounds) concern one object, order a single factorization
   so it answers all of them. For example, eliminating columns in ascending degree
   yields every prefix rank at once; one exact-degree run once used 2k+1 eliminations
   where three sufficed.
5. **No known waste at launch.** List the run's stages first (setup, generation, main
   loop, repeated series) and remove every piece of waste already identified. Time the
   largest case by extrapolating from a measured smaller run, never by guessing, and
   pass that figure to `--expect`. "It does
   not change the results" is not a reason: it changes the approach, and the user has
   rejected it.
   Design each run from the question it must answer, never from the nearest existing
   driver. Name the one output the conclusion uses, then cut everything else: skip the
   parameters that proved results or earlier runs already settle, start where they stop,
   and stop each computation as soon as its question is decided (a closure that only
   has to decide whether 1 is derivable stops when 1 enters). A reused driver carries
   the previous question's outputs, which are waste for the new one.
6. **Report only what the result files say.** Take every quoted number, case count and
   sampling grid from the saved output, read by a script rather than from memory.
7. **Keep long runs observable.** Print progress with flush, and do not pipe a long run
   through a filter that holds its output until the end.

8. **Answer refusals by optimizing, never by splitting.** When a guard refuses a run, make the computation
   itself efficient: move the loops into the compiled kernel, parallelize it, reuse shared work and stop
   early. Never split it into shorter invocations or drive a parameter series from a shell loop; that keeps
   the waste and defeats the guard.
9. **Stop testing cases once they have answered.** Before each further run, ask whether the finished runs
   already decide the model question. If they do, compute nothing more and state and prove the general
   proposition the cases point to.

`./compute.sh` enforces rules 3 to 5 and 8 in part. A Python computation allowed more than 120 s needs a
`--kernel-reason` of at least six words, naming the compiled kernel and the reuse. Because a stated reason
cannot be verified, `compute.sh` also scans the code such a run can reach (the script, and in its local imports
the module-level code and the names it uses) and refuses loops nested three deep over non-literal ranges. It also refuses a short Python run (at most 120 s) of a script that the
session has already run short with six different argument lists, since a parameter series belongs in one run.

After editing any framework tool (`compute.sh`, `tools/*.py`), run its tests before
committing: from `tools/tests`, `python3 -m unittest`.

## Naming results

Name each new lemma, theorem, corollary or conjecture after what it says or does, in one to
four plain words a reader can remember and use in a sentence without looking it up, such as
"the separation theorem" or "the light lemma". Never use letter codes or suffix variants such
as "Theorem GCp" or "Lemma WE": they carry no meaning and force the reader to look them up. A
variant of an earlier result gets its own descriptive name, or the earlier name with a
meaningful qualifier, not a prime, digit or letter suffix. Follow the names GPT-6 Astra gave
in the main notebook. Cite older coded results by a descriptive name, usually their claim
ID's words. The finisher rejects new entries that name results by letter codes outside
tables.

## Route check when opening a cycle

Do not take a cycle's task from the previous entry's remaining gap alone. First name the
top-level item of "The remaining route" that the cycle advances (the entry's `data-route`)
and assess that line's prospects as AGENTS.md requires. A weak assessment, or a line that
produces special cases without moving its general implication, makes the cycle a route
review under AGENTS.md even before `finish-turn.py` forces one.

Recheck a line's standing hypotheses against the instances the goal must handle at every
cycle, not only when the line opens. A recorded count or obstruction showing that the goal's
instances violate them ends the line's relevance, however sound each step is. On 24 September
2026 a locality line assumed identical-or-independent input forms, but a recorded count showed
that the band's forms are necessarily dependent.

To make such drift visible, the notebook's **Open statements** living section (AGENTS.md)
always holds the open part of the goal as a short list of self-contained statements. Each is
stated in full, readable without other entries, with its status and the instances it must
cover. Read it before designing a cycle and name the statement the cycle advances. When a line
has descended more than one reduction below every statement on the list, the next cycle is a
route review, which revises the list and places the line on it (user feedback, 24 September
2026).

Before designing a cycle:
- Read in full every parked or linked item that the notebook's Proposed next step names on
  the same route item.
- Search research/CLAIM_INDEX.md for the cycle's objects under their structural names as
  well as the current vocabulary, since a cycle can otherwise rediscover a conjecture that
  its own next-step paragraph listed as parked.
- Restate a restart condition or calibration only from the latest entry that states it,
  after searching the notebook for later entries that met or replaced it.
- Before taking up a question from an earlier entry, grep the notebook for later links to
  its anchor and read those entries. Later entries may already have computed, reduced or
  set aside the case.

A conjectured sufficient condition for a size lower bound must use the size. Check that it
does not also exclude refutations of every size, since the proof system is complete.

## Reusable tooling

When a cycle needs a helper that earlier cycles also wrote for the same job, extend the committed
framework tool instead of writing it again in scratch space, with tests, and use it from then on.
A script rebuilt every cycle is a missing framework feature. Claim registration uses
`tools/claim-index.py author build` with a compact spec (research/claims/README.md), not a
per-cycle builder script.

## Working with the user

Durable process lessons belong in this file or the rest of the committed framework, not in
machine-local agent memory: memory does not survive a worktree or machine change, and every
session must be resumable anywhere from the repository alone. State each lesson as a general
rule, not as a description of the mathematics that prompted it.

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
