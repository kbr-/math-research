# Fossick: incremental significance screening

Run only when explicitly assigned. Preparing a resume or building the notebook
does not execute Fossick. The [implementation plan](../research/notes/FOSSICK_PLAN.md)
tracks features; the first real scan is a separate assignment.

The tracked `research/notes/FOSSICK_STATE.json` starts empty. Its `ended_at` is the
last contiguous screened article, not the last article opened. Each ledger row
keeps source/metadata fingerprints and links to reviews or attention decisions.
Pending candidate audits do not prevent an article from being screened. Claim
significance lives in the registry; candidates use the existing
[attention workflow](../research/claims/README.md#significance-check-and-attention).

## Assigned scan

1. Start a measured cycle under the computation policy. Run commands through
   `compute.sh run TURN --threads 1 --category local_processing -- ...`.
2. `python3 tools/fossick.py next --limit 20 --out research/results/TURN/batch.json`
   saves a pending batch and prints titles/statuses and claim classifications.
   `--compact` prints category counts instead; use small batches or adequate output
   allowance. Reading the output does not advance `ended_at`. The complete JSON
   includes every selected entry and its claim IDs; obtain summaries/exact statements
   with the existing claim and notebook tools when needed.
3. Read each entry's relevant scope, including unindexed entries and negative
   results. Reuse current source-backed significance reviews; open full arguments
   for plausible candidates or ambiguity. Consult the benchmark map for targeted
   comparisons. Do not infer novelty from a title or treat a no-claim declaration
   as proof that nothing useful is present.
   For formalization records, compare the actual verified statement with its source:
   weaker hypotheses, broader domains or stronger conclusions may merit attention
   even when the original special case does not. Separate these from routine API
   and empty-case extensions; verification status alone is not the assessment.
4. Save an edited copy of the batch with a disposition and reason for each screened
   row: `already_assessed` lists every source-linked claim under `reviews`;
   `candidate_linked` also lists persisted claim IDs under `attention`;
   `no_candidate` explains the screening result. Preserve known candidate references
   even when an earlier attention decision is already reviewed/actioned/dismissed.
   No duplicate mathematical assessments belong in the ledger. A batch can leave
   unfinished rows with a null disposition.
5. `python3 tools/fossick.py complete --batch research/results/TURN/decisions.json
   --out research/results/TURN/completion.json` validates fingerprints, review evidence,
   persisted candidate references and the expected state before atomic advancement.
   Use the ordinary notebook/timing/finalization/commit checkpoint. Continue with
   the remaining batch, or another bounded cycle, only within the assignment.

`next` retries the active selection; use a new output filename if the state changed.
Exact completion retries return the saved receipt without adding decisions. Stale
writers are rejected and state writers share a lock. `refresh` discards only an
unfinished selection after sources change; it preserves all completed ledger rows.
It is not a reset command. Never erase progress to suppress a discrepancy.

## Scope, changes and recovery

Each pass pins a Git revision and terminal article. The endpoint fixes its scope;
per-item fingerprints record the actual screened source and metadata, and completion
records HEAD as provenance. Relevant changes within that scope must be rescreened.
When a pass is complete, the next `next` invocation includes a later suffix. A
Fossick cycle therefore does not chase its own new notebook entry indefinitely.

Changed old content, cited evidence or incident relationships reenter the worklist;
insertions before the frontier are not skipped. Matching content at a new position
retains its review. Missing anchors or a divergent Git ancestry fail without resetting
state: reconcile the appropriate branch first. Generated timing/producer markup
uses existing versioned normalization; malformed legacy HTML uses conservative raw
hashing only when no generated decoration is present. Ignored inventory caches are
keyed by source/evidence content and can be deleted without losing progress.

`python3 tools/fossick.py status` and the resume bundle show only saved progress and
last-scan counts, explicitly labelled; neither scans sources nor claims those counts
reflect later edits. `next` refreshes them. Detailed state is read only during Fossick.
Selection and completion use one tracked ledger; batch reports preserve screening
evidence, not a second candidate queue. The tools check accountability, not the
truth of an agent's screening judgment or mathematical correctness.
