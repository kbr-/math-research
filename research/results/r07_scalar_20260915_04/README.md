# Complete fresh ENS scalar cleanup

Completed 15 September 2026, base2322c6d710493f59c8ac81558b4e03ab48e4bdaf.
Claim `lem:fresh-ENS-scalar-cleanup`, `claims/FreshENSScalarCleanup.lean`.
Full mathematical proof: notebook `entry-2026-09-15-lean-fresh-ENS-scalar-cleanup`.

The source set contains every companion and every coefficient Boolean equation;
it does not add the product equation. General scalar cleanup over any field
requires idempotent assigned constants and zero companion images. It preserves
the original PC ceiling and fixes arbitrary retained polynomials, so retained
F may contain other blocks using only retained variables. No affine-degree
assumption is needed for this generic replay statement.

Zero inputs permit all-zero constants for every field and h>=0. Unit-span
cleanup is specifically over ZMod2, requires h>0, and uses a unit combination
in row0 and zero elsewhere. Every scalar of ZMod2 is idempotent. Characteristic
two alone is not substituted for this field condition. The unit-span wrapper
extracts finite coefficients using Mathlib's span criterion.

All five audited declarations pass with standard axioms. `lean-verification.txt`
contains exact types, dependency revisions and incremental build/axiom output.
Reproduce from repository root with a new output destination:

```bash
./formalization/verify.sh --target claims/FreshENSScalarCleanup.lean --out /tmp/scalar-cleanup-check.txt
```

The recorded audit used `--session r07_scalar_20260915_04` and the canonical
report path. First checks built missing pinned finite-field imports locally,
then exposed retained-variable type inference, finite-index linter assumptions
and scalar-image simplification issues. These were fixed without changing the
mathematical claims or dependency versions. Full output, including failures,
is retained under `research/provenance/session-records/r07_scalar_20260915_04/`.
Its manifest references the canonical verifier report without duplicating it.

`scope.md` is the pre-proof dependency/boundary map. `provenance.json` hashes
source, scope and report. Printed types were reviewed against the complete
notebook statement. R07 is now covered by this release plus the previously
verified affine system, coordinate and fresh-degree claims. R08/R16 remain.
No living notebook sections or route were changed; the coordinator receives
completion status. No framework rule addition was necessary. The final commit
follows the instrumented snapshot.
