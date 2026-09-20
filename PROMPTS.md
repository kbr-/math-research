All prompts below, including ordinary research, Spin, Formalize and parallel
formalization, follow the root [index maintenance contract](AGENTS.md). Apply it
to new and affected existing claims within the assignment; do not expand an
assignment into unrelated formalization or metadata audits. For research claim
triage, use the root packet-orientation rule; selected excerpts do not replace
exact statement/proof reading before reliance.

# Dump

Dump all our findings, as a sequence of sweet self contained lemmas, together
with their proofs, plus remaining route to our goal, into a pdf.

# Resume

Run `python3 tools/resume.py`, then read every listed part with separate bounded
outputs. Retry truncated parts without preparing another resume. Follow the
included RESUME.md without rereading bundled files; load other sources only as needed.

# Branch

Create a side research notebook for the goal supplied with this protocol, optionally
identified by an existing notebook entry or claim. This invocation authorizes setup,
not an unbounded research run. Do not begin the mathematical investigation unless
also asked. Follow [the side-notebook workflow](tools/SIDE_NOTEBOOKS.md).

Read the named source and applicable claim/dependency/correction records. Choose a
stable thread name and an appropriate Git branch/worktree without disturbing
unrelated edits. Prepare the new goal, initial position, remaining obligations,
first test and stopping point, working context and applicable formalization gaps.
Use `tools/branch.py create` with reviewed context JSON; the research record starts
empty. Link inherited results rather than copying their records or upgrading their
status. Register/select the notebook, run its checks, commit setup and report its
path, local route and future public URL. A public route is not a deployment.

Subsequent Resume/Spin/research operates on the selected thread, preserving its
own living sections and using the shared claim registry. No additional permission
for formalization, parallel work or publication follows from creating a branch.

# Formalize

Invocation: `Execute the Formalize prompt against claim <reference-to-the-claim>`.
The reference supplied in the invocation is this prompt's argument: it may be
a claim-index label, a notebook anchor or link, or another unambiguous claim reference.

Formalize that claim in Lean. Follow [formalization/AGENTS.md](formalization/AGENTS.md)
and the root research protocol, restoring context through
[research/notes/RESUME.md](research/notes/RESUME.md) as needed. Resolve the reference
and read its exact statement and relevant proof. Identify its mathematical
components, hypotheses, dependencies, and downstream applications. Choose the
formalization order and supporting lemmas yourself; do not require the user to
specify a "core" or enumerate conclusions. Formalize the complete indexed claim
under the completion and dependency requirements in formalization/AGENTS.md.
If only part can be completed, record the exact verified portion and
remaining obligations explicitly, without presenting partial verification as
completion of the whole claim.
If the reference is ambiguous, ask which claim is intended rather than selecting
a different target.

Carry the assigned formalization through statement review, proof verification,
evidence retention, a notebook research-record entry, and a claim-index link under
those rules. Refresh **Gaps identified by formalization** under the formalization
maintenance policy. Report the exact verified scope and any remaining gap honestly;
do not silently weaken the requested claim. Commit the checkpoint locally on the
current branch and stop; this prompt does not authorize a push or a Spin loop.
After compaction, restore the original claim argument and continue this assignment.

# Spin-formalize

Invocation: `Execute the Spin-formalize prompt against claims <set-of-claim-references>`.
The supplied set is this assignment's target set. Resolve each reference as in
the Formalize prompt; ask only about genuinely ambiguous references. This is an
explicit formalization assignment, not a change to ordinary research or Spin.

Follow [formalization/AGENTS.md](formalization/AGENTS.md), the root research
protocol, and [COMPUTATION_RULES.md](COMPUTATION_RULES.md). Carry out the Formalize
workflow repeatedly, continuing after each checkpoint instead of stopping after
one claim. Work autonomously until every supplied claim and its required proof
dependencies meet the formalization completion rule, or the user interrupts.

Before proof-writing, preserve the supplied target set and a dependency-and-scope
map in the assignment's supporting evidence. Choose the order yourself:

- If an existing indexed claim A requires another indexed claim B, formalize B
  first, complete its own research-record entry and checkpoint, then formalize A
  in a separate entry. Apply this dependency-first ordering recursively to any
  chain of existing indexed claims, including necessary claims outside the
  originally supplied set. Do not bundle several existing claims into one entry.
- Reuse already verified dependencies without presenting them as new results.
  Check their exact statements and coverage. Identify circular dependencies and
  resolve them with a valid proof order or an alternative argument, not assumptions.
- A newly formulated dependency claim may share the research-record entry of
  the claim that introduced it. Give the new dependency its own Lean file and
  claim-index entry, with its complete human-readable statement and proof under
  the formalization rules. Keep small local helpers local when appropriate.
- Separately indexed downstream corollaries are not additional targets unless
  supplied by the user or required as proof dependencies.

For each claim, perform bounded, recorded research cycles. Verify the complete
statement and its dependencies, update its claim-index formalization links and
scope, and preserve the proof, theorem types, axiom reports, and measured evidence.
Each existing indexed claim gets its own research record; an unfinished or failed
cycle also gets an honest entry under the root rules. Retain alternative proofs
in full human-readable form. Use the formalization and verification timing
categories, switching to mathematics when developing the underlying argument.

After every cycle, assess what changed in the assigned claim's remaining proof
obligations and identify process friction, wasted effort, or difficulty checking
the formal statement. Include a one-sentence process assessment in its entry.
Implement clear, bounded framework improvements when warranted, revising existing
guidance rather than accumulating repetitive rules; otherwise explain briefly
why none is needed. Commit the research checkpoint before beginning the next
claim, and commit framework improvements separately.

Keep the current branch and commit locally. This prompt does not inherit Spin's
authorization to push or switch to main; publication requires separate explicit
authorization. Do not return merely because one claim or checkpoint is finished.
If a claim is false or blocked, record the counterexample or exact unresolved
obligation and continue independent targets. Never count a correction, weakened
statement, or conditional proof as completion of the original claim. If no valid
progress remains possible without user input, report the blocker and unfinished
targets rather than inventing completion or repeating stalled cycles.

After compaction, follow the Resume prompt, reread this prompt and the
formalization instructions, and restore the original target set, dependency map,
and completed/remaining work from the saved records. Continue the same assignment
without redoing completed claims. When all targets are verified, report the
completed claims and checkpoints, with any separately indexed corollaries left
outside the assignment clearly distinguished.

# Spin-formalize-parallel

Invocation: `Execute the Spin-formalize-parallel prompt against theorem <reference>`.
The reference identifies the complete target, not just a convenient component.
This explicitly authorizes parallel formalization. Follow Resume, then
[formalization/AGENTS.md](formalization/AGENTS.md) and Spin-formalize above;
the following adds coordination, not a separate proof or research-record policy.

Act as coordinator until the final assembly. Work autonomously through these steps:

1. Read the exact target and proof, recursively trace its required dependencies,
   and save a route in `formalization/<TARGET>_FORMALIZATION_ROUTE.md`. Reuse and
   revise an existing route when appropriate. Give a topological list with exact
   sources, hypotheses, direct prerequisites, existing verified coverage, and
   remaining obligations. Include third-party boundaries and extracted helpers;
   distinguish necessary results from stronger conveniences and alternative proofs.
   Mark uncertain steps as provisional. Planning IDs are not claim-index labels
   or evidence of verification. Record substantive route analysis under the usual
   research protocol.
2. Partition the route into shared foundations, independent branches, and final
   assembly. Save the assignments and required interfaces in the route, including
   intermediate checkpoints that unblock another branch. Choose the decomposition
   yourself; do not require the user to enumerate a theorem's components. Revise
   it when the actual proof dependencies change.
3. Use the current branch as the integration branch. Create or reuse one isolated
   worktree and branch per worker under a common directory agreed with the user
   or chosen alongside the checkout. Assign explicit paths and exclusive write
   ownership. A foundation worker may use this worktree while the coordinator
   refrains from editing it. Leave unrelated worktrees and research agents alone.
4. Spawn workers when their prerequisites are available, within available
   concurrency. Each must perform Resume and execute Spin-formalize restricted
   to its assigned subset, with its own records and local checkpoints. Coordinate
   additional dependencies through the parent instead of silently expanding into
   another worker's scope. Follow the root coordinator-ownership policy for
   notebook living sections. All workers share the resource limits in
   [COMPUTATION_RULES.md](COMPUTATION_RULES.md); use distinct timing/evidence IDs
   and private writable build caches. Existing dependency-installation rules apply.
5. Have workers agree on shared definitions and exact interfaces early and message
   one another about dependencies. Release verified intermediate checkpoints;
   do not make branches wait for each other's entire assignment. Coordinate clean
   pauses for sequential rebases onto pinned integration commits under the root
   Git policy, fast-forwarding the integration branch after each completed rebase.
   Record released commit IDs in the handoff. Preserve both sides' research
   records and evidence when resolving conflicts. For append-only notebook/index conflicts, use
   `python3 tools/merge-formalization-appends.py --help`; it requires manual review
   for other changes and never stages files or continues a rebase. Do not rebase
   a worktree while its worker is editing.
6. Once the workers finish, integrate all remaining checkpoints. Audit individual
   statement provenance and directory placement under formalization/AGENTS.md;
   defer cross-branch moves until this point, updating imports and links together.
   Check that every newly introduced mathematical claim is indexed with its full
   human-readable proof, Lean file, and exact verified scope. Keep small helpers
   local unless extraction has a concrete benefit. Verify the combined project.
7. Personally perform the final assembly on the integration branch under
   Spin-formalize, with its research records and verification. If assembly exposes
   a missing prerequisite, revise the route and coordinate its completion; do not
   substitute an assumption or silently weaken the target. Finish only when the
   complete target and all required dependencies are verified, or report a genuine
   impasse under Spin-formalize's blocking policy.

Commit locally. This prompt authorizes neither merging into `main` nor pushing;
honor separate explicit user instructions for those actions. After compaction,
restore the target, route, branch assignments, worker status, released interfaces,
and integrated checkpoints before continuing. Do not duplicate active workers or
restart completed proofs. Report the final verified scope and remaining gaps.

# Fossick

Invocation: `Execute the Fossick prompt` (optionally specify a bounded scope).
This explicitly authorizes a significance-screening pass, not publication or
formalization. Implementing/testing Fossick alone does not authorize this scan.

Follow [the Fossick workflow](tools/FOSSICK.md), starting a measured research cycle.
Use the tracked `research/notes/FOSSICK_STATE.json` and bounded `next` batches;
resume an unfinished batch rather than restarting. Reuse the structured claim
index, current significance reviews, exact source excerpts when needed, benchmark
map and shared attention history. Include unindexed entries and negative results.
Record screening dispositions through `complete`; never advance the cursor merely
because a packet was read. Keep candidate audits separate from screened coverage.
Stop at the pinned pass endpoint or the requested narrower scope, reporting the
ended-at marker, unresolved candidates and actual reading/audit limits. Record and
commit the measured cycle under the normal rules. Push only if separately authorized.
After compaction, restore this assignment and the saved batch; do not rescan
unchanged completed entries. Smoke tests use isolated state, leaving the real
ledger unchecked for the actual scan.

# Spin

I am now going to sleep. I won't be available to you for the next ~8 hours.
However, I would like for you to continue: both research and framework
improvements --- on your own.

Autonomously advance the current research goal stated at the top of
the selected research notebook (main by default) through bounded, fully recorded research cycles and clear, small
framework improvements.
Follow the repository rules for maintaining the notebook, measured evidence,
and checkpoints. Continue until the user explicitly interrupts.

So perform the following, in a loop:

- do a research turn, as if I prompted you to "do the next step"
- after EVERY research turn, assess its contribution and process: state what
  changed in the named remaining-route obligation (the top-level item of The
  remaining route that the entry is tagged with, not a sub-gap of the current
  line), including when nothing changed, and assess the current line's prospects
  qualitatively from evidence, following AGENTS.md; identify wasted time or context,
  repeated work, or difficulty checking the mathematics. Follow AGENTS.md's
  task-selection and dependency-checking guidance. When investigating overhead,
  use existing timing categories and, where relevant, the summary's
  [recovery evidence](tools/RECOVERY_EVIDENCE.md); these are observable proxies,
  not proof of wasted work or savings. Address repeated reading with existing
  bounded retrieval tools before adding infrastructure. Implement a concrete
  improvement for observed friction when warranted, or briefly explain why none
  is needed; do not run a separate framework audit every cycle. Review this
  yourself rather than waiting for me or inventing changes to satisfy this step.
- update the notebook as usual
- Apply the [cheap significance check](research/claims/README.md#significance-check-and-attention)
  through claim metadata and the finalizer; surface new/reopened candidates without
  rerunning a literature audit for every lemma.
- include a one-sentence process assessment in the research entry
- `git commit` the research step
- implement any clear, bounded framework improvement identified by that
  assessment, following AGENTS.md's guidance to keep the framework small, and
  `git commit` it separately
- Push reviewed research and framework checkpoints to origin/main only under
  an active explicit publication grant, following AGENTS.md's scope/expiry rules.
  A grant covering Spin applies to its checkpoints until it expires or is revoked;
  this reference does not renew an expired grant. Stay on main.
- regarding the above: I want to see https://kbr.is-a.dev/math-research/ updated
  with lots of delicious new research when I wake up
- **IMPORTANT: if compaction happens, do the resuming**, i.e. "Run python3 tools/resume.py, read every listed bounded part and the included restart guide, and load other
  sources only as needed without rereading the bundle." -- following the usual prompt.
- After compaction, reread the "Spin" prompt from `PROMPTS.md` and continue the
  active assignment.
- Do not return to the user. Think for as long as you like and work for as long
  as you like (until I explicitly interrupt you), just make sure to update the
  notebook `git commit` on visible research checkpoints. But **do not return to
  the user** -- I will not be present to reprompt you.
- rinse and repeat

Rules clear? GO.
