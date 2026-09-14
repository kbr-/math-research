# Binary affine-cover formalization

This turn formalizes the indexed logical rule-convention bridge
`lem:binary-semantic-affine-cover` and extracts two reusable dependency claims.
The full alternative proof and exact scope are in notebook entry
`entry-2026-09-14-lean-binary-affine-cover`.

## Files and dependency graph

- [BinaryAffineZeroCover.lean](../../../formalization/claims/BinaryAffineZeroCover.lean):
  `lem:binary-affine-zero-cover`; binary affine-clause definitions, a separator
  chosen from the first clause, exact restricted fibers, and a translation
  equivalence between them. No finite-dimensional assumption.
- [AffineClauseCompression.lean](../../../formalization/claims/AffineClauseCompression.lean):
  `lem:affine-clause-basis-compression`; imports the clause definitions above and
  proves equivalent subclauses of width at most dim(V)+1, plus a finite-registry
  coefficient-slot bound. Requires finite dimension.
- [BinarySemanticAffineCover.lean](../../../formalization/claims/BinarySemanticAffineCover.lean):
  imports both dependencies; proves the weakening/resolution reduction, a
  concrete basic-rule derivation with at most three new steps, soundness of that
  derivation system, at most two auxiliary clauses (each of width at most |D|+1),
  affine-restriction preservation, and compressed-rule simulation.

The separator's fiber equations and explicit bijective translation are the
formal geometric certificate. There is no separate theorem stated using
Mathlib's `AffineSubspace` codimension terminology. For a nonempty affine W,
the two nonempty fibers of a nonconstant affine functional are exactly its
parallel hyperplanes; the notebook explains this interpretation.

## Scope limits

The [original passage](original-claim.html) also states a PC degree ceiling
4h+1. The concrete PC weakening and resolution results it invokes are not
formalized by these files; their exact passages are retained in
[remaining-pc-weakening.html](remaining-pc-weakening.html) and
[remaining-pc-resolution.html](remaining-pc-resolution.html). No custom axiom
or hypothesis standing in for these results was inserted to claim their
verification. Thus the whole original paragraph, read as including that PC
corollary, is not yet fully formalized.

The formalized size statements are local inference counts, literal counts,
and a finite-registry coefficient-slot bound. A global DAG serialization and
its bit-string encoding are not implemented. Fresh-variable restriction is
covered by precomposition with arbitrary affine maps; no separate syntactic
constant-pivot rewrite routine is provided. No PHP lower bound is formalized.

## Reproduction and verification

Restore dependencies using [the Lean project guide](../../../formalization/README.md),
then run from the repository root:

```bash
./formalization/verify.sh --out research/results/NEW_RUN/verification.txt
```

The final command for this turn was:

```bash
./formalization/verify.sh --session lean_affine_cover_20260914_04 --out research/results/lean_affine_cover_20260914_04/verification-final.txt
```

[Complete output](verification-final.txt) records the pinned toolchain and
dependencies, builds, fresh elaborations, theorem types, and axiom reports.
All ten new declarations report only `propext`, `Classical.choice`, and
`Quot.sound`. The six earlier declarations were regression-checked, not newly
formalized. Source/type review matched clause truth to a disjunction of affine
forms equal to one, zero sets to simultaneous zeroes, and basic derivations to
premises, semantic weakening, and complementary-parity resolution only.

Initial Lean checks exposed finite-field case-split elaboration, missing
classical equality and field instances, equivalence-structure syntax, and
finite-set/subtype coercion issues. These were fixed; they were not mathematical
counterexamples. Cache warnings concern local modules absent from upstream
Mathlib's cache. Full diagnostics are archived with the measured session in
`research/provenance/session-records/lean_affine_cover_20260914_04/`.
No external numerical experiments were run. Provenance hashes cover the Lean
sources, verifier, dependency configuration, excerpts, and final report.
