# Verification workflow regression evidence

This is framework validation, not a new mathematical research result.

The final theorem passed the new targeted command:

```bash
./formalization/verify.sh --target third-party-claims/ChessboardFillingProof.lean --session verification_workflow_20260915 --out research/results/verification_workflow_20260915/chessboard-filling.txt
```

[chessboard-filling.txt](chessboard-filling.txt) is the complete canonical report.
It checks the selected declaration and its transitive axioms; it does not assert
a fresh audit of unrelated modules. Changing the interface module's metadata
caused Lake to rebuild its affected local dependents; other cached modules were
reused. No mathematical statement or proof was changed.

The [session manifest](../../provenance/session-records/verification_workflow_20260915/manifest.json)
references this report by `canonical_path` and SHA-256. Its captured command
output was byte-identical, so no second output file was archived. The stopped
session measures this command and its surrounding regression preparation only,
not the entire framework-editing task.

Focused tests also passed:

- `formalization/tests/test_verification_cache.py`: cached unfinished proof
  rejection, rebuild after correction, targeted cached checks, explicit fresh
  source check, interface/legacy metadata, and missing-target rejection.
- `tools/tests/`: 13 tests covering canonical-report archival, refusal of changed
  or missing evidence, unchanged existing archives, finish-turn, and append merging.
- `tools.test_repository_tools.RepositoryTools.test_archiver_preserves_full_output_and_refuses_replacement`:
  the existing eight-megabyte output preservation and immutability regression.

These tests run through `compute.sh`; the Lean test also requires sourcing the
existing elan environment. Their fixtures are temporary and are never claims.
