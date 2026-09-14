# Dump

Dump all our findings, as a sequence of sweet self contained lemmas, together
with their proofs, plus remaining route to our goal, into a pdf.

# Resume

Read research/notes/RESUME.md fully and follow its restart checklist. Load other
sources only as needed.

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

# Spin

I am now going to sleep. I won't be available to you for the next ~8 hours.
However, I would like for you to continue: both research and framework
improvements --- on your own.

So perform the following, in a loop:

- do a research turn, as if I prompted you to "do the next step"
- after EVERY research turn, assess its contribution and process: state what
  changed in the named remaining-route obligation, including when nothing
  changed; identify wasted time or context, repeated work, or difficulty
  checking the mathematics. Follow AGENTS.md's task-selection guidance.
  Implement a concrete improvement when warranted, or briefly explain why none
  is needed. Review this yourself; do not wait for me to identify friction or
  invent changes merely to satisfy this step.
- update the notebook as usual
- include a one-sentence process assessment in the research entry
- `git commit` the research step
- implement any clear, bounded framework improvement identified by that
  assessment, following AGENTS.md's guidance to keep the framework small, and
  `git commit` it separately
- Push reviewed research and framework checkpoints to origin/main under
  AGENTS.md's standing Spin publication authorization. It covers the entire
  active Spin task, not only the latest checkpoint. Stay on main.
- regarding the above: I want to see https://kbr.is-a.dev/math-research/ updated
  with lots of delicious new research when I wake up
- **IMPORTANT: if compaction happens, do the resuming**, i.e. "Read
  research/notes/RESUME.md fully and follow its restart checklist. Load other
  sources only as needed." -- following the usual prompt.
- After compaction, reread the "Spin" prompt from `PROMPTS.md` and continue the
  active assignment.
- Do not return to the user. Think for as long as you like and work for as long
  as you like (until I explicitly interrupt you), just make sure to update the
  notebook `git commit` on visible research checkpoints. But **do not return to
  the user** -- I will not be present to reprompt you.
- rinse and repeat

Rules clear? GO.
