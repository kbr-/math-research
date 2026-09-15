# R13 row-linear and ordinary-restriction dimensions

Completed 15 September 2026 on formal-r-restriction, based on the pinned R01
release `76cc94b`. Timing/evidence ID `r13_restriction_20260916` is an identifier;
the work and notebook entry are dated 15 September in the host timezone.

## Exact scope and evidence

Two newly extracted claims, both in claims/ under the statement-provenance rule:

- `lem:row-linear-polynomial-space`: exact dimension, degree bound and top
  coefficient of the ordinary row-linear polynomial space. Four audited results
  in `formalization/claims/RowLinearPolynomialSpace.lean`.
- `lem:ordinary-restriction-dimension`: ordinary polynomial degree-space bound,
  affine-substitution degree preservation and image dimension bound. Three
  audited results in `formalization/claims/OrdinaryRestrictionDimension.lean`.

Both hold over any field. Natural parameters may be zero; the dimension sum
also covers k>m. No Boolean quotient, pointwise-zero identification, or assumed
PC separation appears. R15, quotient injection and the larger separation
claims remain separate. The complete mathematical statements and proofs are
in notebook entry `entry-2026-09-15-lean-row-linear-restriction-dimension`.
The initial map is `scope.md`; no new mathematical discrepancy was found.

`row-linear-verification.txt` and `restriction-verification.txt` contain complete
pinned dependency revisions, build output, exact theorem types and transitive
axiom reports. All seven declarations pass with standard foundations only.
`provenance.json` hashes the two sources, scope and canonical reports. Full
protected command evidence is archived under
`research/provenance/session-records/r13_restriction_20260916/`.

## Reproduction

From the repository root with its pinned Lean environment:

```bash
./formalization/verify.sh --target claims/RowLinearPolynomialSpace.lean --out /tmp/row-linear-verification.txt
./formalization/verify.sh --target claims/OrdinaryRestrictionDimension.lean --out /tmp/restriction-verification.txt
```

Outputs must be new paths. The recorded calls additionally used
`--session r13_restriction_20260916` and the committed canonical report paths.
The audits use incremental Lake builds and inspect compiled theorem types and
transitive axioms; unchanged dependencies were not re-elaborated.

Initial direct `lake env lean` checks found a missing pinned Sym cache module,
embedding-membership simplification issues, a finite-subtype instance mismatch,
and style warnings. These were corrected, and both files then passed direct
warning-as-error checks before their final audits. No false arithmetic or
polynomial claim was encountered. All failed outputs are retained. A targeted
`lake exe cache get Mathlib.Data.Sym.Card` restored the missing approved module
and four dependencies; no version upgrade or new dependency was introduced.

The first shell check ran both independent files sequentially, so its nonzero
status reports both first-check diagnostics. Later file checks were separate.
The private .lake directory was restored by the coordinator before any Lean
check. A scoped stash/rebase/pop incorporated the pinned foundation checkpoint
without changing drafts; it did not alter any other worktree.

## Process and timing

The ordinary-restriction dimension claim has a separate file because it does
not depend on row structure and is directly reusable for R15. Small counting,
exponent and embedding helpers remain local. The source proof and Lean proof
both use coefficient independence and elementary counting; the degree-bound
embedding uses only injectivity, since target-space dimension equality is not
required. Printed types were reviewed against the exact notebook statements.
No guidance addition was warranted.

Initial rules/source reading preceded instrumentation. The explicit wait for
cache readiness is marked overhead; short operational integration work during
that wait remains within that overhead window. Every Lean workload uses the
formal_verification category and protected shared limits. Preparation includes
metadata review; final commit work follows the instrumented snapshot.

The coordinator owns the notebook living sections and route. This worker
appends its full record and updates the claim index only; R13 completion and
unchanged gap status are reported for coordinated integration. R15 is pending
R04/R07, and the worker pauses cleanly after this release.
