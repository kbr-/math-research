# R07 first release: affine representations and system witnesses

Completed 15 September 2026 on formal-r-affine-removal, based on the integrated
R03 checkpoint `3b9669d04b0fbcb7772cb2c2703a9d00e45404c3`.

Two complete extracted claims are recorded in notebook entry
`entry-2026-09-15-lean-affine-system-witnesses`:

- `lem:affine-form-polynomial-interface`, `claims/AffineForm.lean`:
  seven checked representation/evaluation/degree/injectivity theorems.
- `lem:affine-system-linear-algebra`, `claims/AffineSystemLinearAlgebra.lean`:
  eight checked proper-span/vanishing/unit/linear-part/exact-input-degree theorems.

Full human-readable proofs, including the finite-coordinate duality argument,
are in the notebook. Source arguments are the paper's affine setup and recorded
semantic weakening/common-vanishing learning. These project supporting interfaces
make no novelty claim and do not formalize either larger source theorem.

## Verified scope and remaining assignment

Forms have type `AffineForm K n = Option (Fin n) → K`; `none` is the constant
coordinate. `affinePolynomial` is a linear injection into ordinary polynomials,
not a finite-field polynomial-function quotient. `affineFormOfMap` bridges the
existing AffineMap representation of clauses. All results hold over any field,
including zero ambient dimension and empty finite input families.

Proper spans have common zeros. Forms vanishing on a consistent common zero
set belong to the input span, with explicit constant coefficients for finite
families; inconsistent families have a unit certificate. Projection to linear
coefficients is injective on a proper span, preserves its finrank and independent
families, and every nonzero proper input has exact polynomial degree one.

R07 is not yet complete: full affine-coordinate completion/free-coordinate
parametrization, fresh-companion exact degree 2h+1, and scalar cleanup replay
remain. R08/R16 also remain assigned. This release unblocks consumers of affine
span witnesses only; no remaining dependency is assumed as an axiom.

## Evidence and reproduction

`affine-form-verification.txt` and `affine-system-verification.txt` preserve
pinned dependency revisions, incremental builds, all fifteen declaration types,
and transitive axiom reports. They passed using only propext, Classical.choice
and Quot.sound. Reproduce from the repository root with new output destinations:

```bash
./formalization/verify.sh --target claims/AffineForm.lean --out /tmp/affine-form-check.txt
./formalization/verify.sh --target claims/AffineSystemLinearAlgebra.lean --out /tmp/affine-system-check.txt
```

Recorded commands used `--session r07_affine_20260915_01` and the canonical
report paths above. All substantial jobs used the protected shared controls.
The initial cache lacked Mathlib.LinearAlgebra.Dual.Lemmas; a targeted cache
restoration fetched its pinned dependencies. Subsequent failures were explicit
rewrite/API, finite-sum normalization, function-coercion and linter issues;
the complete outputs are retained. No false mathematical claim was found.
No dependency version was changed.

`scope.md` is the initial pre-proof map. `provenance.json` hashes both source
files, the scope map and the canonical reports. Full command evidence/timing
is archived under `research/provenance/session-records/r07_affine_20260915_01/`.
The archive points to canonical verification reports instead of duplicating them.

## Review and process

The printed types were reviewed against the notebook's exact claims. The
representation module was separated because clause consumers and companion-degree
work need it independently of system duality. Small coordinate calculations
stay local. This follows existing guidance; no new framework rule was needed.
The coordinator owns living notebook sections and the route and receives the
exact completion boundary for integration.

Initial rule restoration preceded timing start. Formal proof design/coding,
underlying proof writing, verification, cache restoration and preparation are
measured separately. Final commit work is after the snapshot. Complete output
includes failed checks; these are not reported as failed mathematical attempts.
