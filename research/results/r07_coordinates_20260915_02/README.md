# Affine coordinate completion (R07 dependency)

Completed 15 September 2026 on formal-r-affine-removal, base e738178927208bce1ffd3c7406490ac6700e7219.
Claim `lem:affine-coordinate-completion`, source `claims/AffineCoordinates.lean`.
Full statement and proof: notebook entry `entry-2026-09-15-lean-affine-coordinates`.

The four audited declarations give an affine equivalence with designated input
coordinates, an injective affine zero-flat parametrization with exact range,
and free-coordinate count n-r. The completion works for any independent family
whose span excludes one; the resulting embedding into Fin n enforces finiteness.
Free variables are indexed by `AffineFreeIndex e`, the complement of the selected
coordinate range. Relabeling that finite type gives Fin(n-r) when needed.
No pointwise-zero identification of ordinary polynomials is used.

`lean-verification.txt` retains the incremental build, exact types, dependency
revisions and transitive axiom reports; all four declarations pass with standard
foundations. Reproduce from the repository root, using a fresh output path:

```bash
./formalization/verify.sh --target claims/AffineCoordinates.lean --out /tmp/affine-coordinates-check.txt
```

The recorded call used `--session r07_coordinates_20260915_02` and the canonical
report path. Initial Lean checks found basis-reindex application, translation
API direction, dependent-if simplification, and deprecated lemma-name issues.
The corrected implementation uses the inverse of `vaddConst`, i.e. x-x0, as the
mathematical proof requires. No new mathematical discrepancy was found.
The complete failed and successful outputs remain in the session archive.

`scope.md` preserves the initial proof/dependency map; `provenance.json` hashes
source, scope and report. Timing and complete outputs are archived under
`research/provenance/session-records/r07_coordinates_20260915_02/`.
The canonical report is referenced rather than duplicated in that archive.
Printed theorem types were reviewed against the full notebook statement.
Existing Mathlib basis extension and finite duality provide checked dependencies.
No new packages or dependency upgrades were needed.

Fresh-companion exact degree and scalar PC cleanup still remain in R07;
R08/R16 remain assigned. Living notebook sections and route were not edited:
the coordinator receives the exact release scope for integration. No additional
framework guidance was necessary. Final commit work is after the measured snapshot.
