# Changed-claim maintenance contract

Baseline: d55e102. Session: index_maintenance_contract_20260919.
Notebook: entry-2026-09-19-index-maintenance-contract.

Implementation: tools/claim_maintenance.py, CLI changed command, finish-turn gate,
and CI comparison against the push/PR base. Root AGENTS.md owns the requirement;
research/claims/README.md describes scope and pending/backlog distinctions.

Reproduce through `./compute.sh run SESSION --threads 1 --category local_processing
-- COMMAND`, saving new reports rather than replacing checkpoint evidence:

- `python3 -m unittest discover -s tools/tests -p 'test_claim*.py'`: 43 passing.
- `python3 -m unittest discover -s tools/tests -p test_finish_turn.py`: 7 passing.
- `tools/claim-index.py changed --base d55e102 --out PATH`: no metadata changes in
  this checkpoint, with unchanged backlog reported separately.

The tests intentionally exercise incomplete new metadata, stale evidence and
correction status acknowledgment. Pending questions retain pending status; passing
is not semantic correctness or completion of the migration. No live claim record
was changed, and authoring-template/end-to-end acceptance work remains open.
