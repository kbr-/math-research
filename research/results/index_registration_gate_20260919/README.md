# Notebook claim registration gate

Baseline: 552e562f5253700258438272da90a9f4a31d00f6.
Session: index_registration_gate_20260919.
Notebook: entry-2026-09-19-index-registration-gate.

New-entry declarations, code/backtick labels and registry source links are checked
by claim_registration.py through the existing changed-claim command. Old entries
at the pinned activation baseline remain immutable. Unknown explicitly labelled
claims cannot evade the check with a no-claim annotation. Unlabelled novelty and
truthfulness still require editorial judgment.

Reproduce through `./compute.sh run SESSION --threads 1 --category local_processing
-- COMMAND`, saving fresh outputs:

- `python3 -m unittest discover -s tools/tests -p 'test_claim*.py'`: 52 passing.
- `python3 -m unittest discover -s tools/tests -p test_finish_turn.py`: 7 passing.
- `tools/claim-index.py changed --base 552e562 --out PATH`: includes this entry's
  explicit framework-only disposition.

No mathematical claims or metadata were changed. This closes the labelled
notebook-only omission gap, not the remaining curation or complete acceptance plan.
