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
specify a "core" or enumerate conclusions. Aim to formalize the complete indexed
claim. If only part can be completed, record the exact verified portion and
remaining obligations explicitly, without presenting partial verification as
completion of the whole claim.
If the reference is ambiguous, ask which claim is intended rather than selecting
a different target.

Carry the assigned formalization through statement review, proof verification,
evidence retention, a notebook research-record entry, and a claim-index link under
those rules. Report the exact verified scope and any remaining gap honestly;
do not silently weaken the requested claim. Commit the checkpoint locally on the
current branch and stop; this prompt does not authorize a push or a Spin loop.
After compaction, restore the original claim argument and continue this assignment.

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
