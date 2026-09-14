# Lean formalization: ENS telescoping

The [Lean source](../../../formalization/claims/MpTelescoping.lean) formalizes
`lem:mp-telescoping`. The notebook entry
`entry-2026-09-14-lean-mp-telescoping` contains the complete human-readable proof,
statement review, and correction to the source's companion-degree equality.

## Verified scope

- `MathResearch.mp_telescoping`: the explicit finite-sum/product identity over
  every commutative ring, for any finite input index type and every h≥0.
- `MathResearch.mp_coefficient_degree`: ordinary joint total degree at most
  1+(h-1)(δ+1), when all inputs have total degree at most δ and coefficient
  polynomials have total degree at most one. Subtraction on natural numbers
  is truncated; h=0 gives the zero coefficient and satisfies the bound.
- `MathResearch.mp_companion_degree`: the companion degree is **at most**
  deg(f_i)+h(δ+1) under the same assumptions.
- `MathResearch.mp_companion_equality_counterexample`: over any nontrivial
  commutative ring, h=1, f=1, and a fresh coefficient X satisfy the hypotheses
  with δ=1, but the displayed companion degree is not 2.

All polynomial degrees are `MvPolynomial.totalDegree` before domain reduction.
Fresh independent coefficient variables are a special case of the more general
degree-at-most-one coefficient polynomials used in the bounds. The identity has
no degree, field, freshness, or Booleanity assumptions. No earlier notebook or
project Lean theorem is imported. Exact companion-degree claims under tighter
hypotheses, input-coordinate merging, and downstream NS/PC applications are not
additional formalized assertions here.

## Reproduction and evidence

Restore the pinned dependencies using the [project guide](../../../formalization/README.md).
From the repository root run:

```bash
./formalization/verify.sh --out research/results/NEW_RUN/verification.txt
```

During this turn the final command was:

```bash
./formalization/verify.sh --session lean_mp_telescoping_20260914_02 --out research/results/lean_mp_telescoping_20260914_02/verification-final.txt
```

[Final output](verification-final.txt) includes dependency revisions, full build
and elaboration output, printed theorem types, and axiom reports. All four new
declarations depend only on `propext`, `Classical.choice`, and `Quot.sound`.
The first pass also succeeded; [its output](verification-01.txt) has the same
identity and bounds but specializes the counterexample to integer coefficients.
The final pass generalized that counterexample to all nontrivial commutative
rings, directly covering the notebook's finite-field setting. The existing
interpolation theorem was also checked by the project-wide verifier; this is
a regression check, not a new result about that claim.

No Lean proof checks failed and no numerical experiments were run. Full command
logs and measured timing are archived in
`research/provenance/session-records/lean_mp_telescoping_20260914_02/`.
The provenance manifest hashes the source, verifier, dependency configuration,
and both verification outputs.
