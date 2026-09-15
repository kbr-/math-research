# R15 dependency release: ordinary restriction and concrete bounds

Completed supporting work on 15 September 2026 in formal-r-restriction.
Base: fab325d6b95fe4c94b43fcac8610c60fae09dd63. R15 itself remains incomplete;
this release checks four required dependencies, not an abstract substitute for
the requested concrete common-kernel theorem.

## Claims, proofs and reports

Full mathematical statements and proofs appear in notebook entry
`entry-2026-09-15-lean-restriction-kernel-dependencies`.

| Claim | Lean module | Final verification report |
| --- | --- | --- |
| lem:finite-affine-coordinate-completion | claims/FiniteAffineCoordinates.lean | coordinates-verification.txt |
| lem:coordinate-restriction-ideal | claims/CoordinateRestrictionIdeal.lean | coordinate-ideal-verification.txt |
| lem:ordinary-affine-restriction-ideal | claims/AffineRestrictionIdeal.lean | affine-ideal-verification-final.txt |
| lem:ordinary-restriction-kernel-bound | claims/RestrictionKernelBounds.lean | bounds-verification.txt |

The four final audits cover twenty declarations and pass with standard
foundations only. Reports retain exact types, dependency revisions and
incremental build/axiom output. The earlier affine-ideal-verification.txt is a
failed report, preserved separately; use the explicitly named final report.

The coordinate helper allows any field and arbitrary ambient variable type,
with finitely many selected variables. The finite affine completion also works
over any field. Polynomial affine pullbacks/ideal transport use F2: equality
of degree-at-most-one polynomial images of generators is checked by finite-field
interpolation, then algebra-homomorphism extensionality extends the inverse
identities to all ordinary polynomials. General pointwise polynomial zero is
never treated as ordinary zero. Exact n-r free-coordinate image dimensions
follow from ordinary degree-space bounds and finite variable reindexing.

The analytic proof uses a sufficient factorial comparison, different from the
paper's exact product-ratio identity, and its full argument is in the notebook.
It delivers the same exp(-k²/m) estimate at r*=3ell(k+1)+1 and a quarter budget
for k²>=m log(4M). The original k=ceil(sqrt(m log(4M))) is proved to satisfy
that condition. Both square-condition and ceiling interfaces are available.
The numeric bound requires r*<=m*ell; absence of high blocks when this fails
must still be handled by the final assembly.

## Reproduction

From repository root, use the pinned environment and new report paths:

```bash
./formalization/verify.sh --target claims/FiniteAffineCoordinates.lean --out /tmp/finite-coordinates.txt
./formalization/verify.sh --target claims/CoordinateRestrictionIdeal.lean --out /tmp/coordinate-ideal.txt
./formalization/verify.sh --target claims/AffineRestrictionIdeal.lean --out /tmp/affine-ideal.txt
./formalization/verify.sh --target claims/RestrictionKernelBounds.lean --out /tmp/kernel-bounds.txt
```

Recorded calls use `--session r15_kernel_20260915_01` and the canonical reports
listed above. All substantial jobs obey shared resource limits. Targeted pinned
Mathlib analytic modules were restored with cache get. An initial broad tactic
import nevertheless triggered unrelated builds; that exact job was stopped
and the source replaced with targeted tactic imports. The interrupted output
is retained. Other failures were API argument order, dependent coefficient
indices, algebra-generator extensionality, arithmetic normalization and linter
issues, not false mathematical claims. No dependency version changed.

`scope.md` preserves the initial complete-target map. `provenance.json` hashes
all four sources, scope and final reports. Complete command outputs and timing
are archived under `research/provenance/session-records/r15_kernel_20260915_01/`;
canonical verifier reports are referenced rather than duplicated.

## Remaining R15 work

Choose a restriction for each proper input span on actual bit variables, relate
affine-map and polynomial-span ranks, form the finite joint map on rowLinearSpace,
prove a nonzero common kernel using the checked concrete bound, and transport
coefficients back to each original input tuple. The no-high-block case and
unit-span alternative required by the full clause registry remain explicit.
The coordinator assigned the separate R16 unit-or-literal generalization to
another worker. No assumption of its integration is needed by these helpers.

All printed types were reviewed against the notebook claims. The helpers are
separately indexed and preserve full arguments; no mathematical discrepancy
was found. Existing targeted-import guidance suffices, so no extra framework
rule was added. Living notebook sections and route were left to the coordinator.
Final commit work follows the instrumented snapshot.
