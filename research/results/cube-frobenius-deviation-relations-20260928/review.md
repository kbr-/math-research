# Frobenius contact correctness review

Reviewed 28 September 2026 in one fresh context at medium reasoning.

Verdict: **Pass. No required mathematical fixes.** The argument establishes the
stated lower bounds, including for generically singular matrices. It establishes
neither generic nonnormality nor eventual invertibility nor a complete Smith form.

## Material read

The stable draft `/tmp/bmd-frobenius-contact-entry.html` and the exact supplied
dependency excerpts with anchors `cube-ternary-pair-algebra`,
`cube-ternary-digit-blocks`, `cube-finite-field-branch-defect`, and
`hasse-lattice-valuation`. No broad notebook or claim search, numerical rerun,
or additional reviewer was used.

## Checks

- **Polynomial identity and syzygy.** Both indices `m` and `mq` are distinct and
  present when `mq < R`. Deleting column `mq` leaves its cofactors unchanged by
  the column subtraction. Their degree is the sum of the other column indices,
  namely `R(R-1)/2 - mq`. Grouping their signed values by incident labels gives
  exactly the stated homogeneous `F_i`. Replacing the deleted column with
  column `m` makes two columns equal, yielding the asserted syzygy. Thus the
  apparently inhomogeneous ideal generators are fully compatible with the
  homogeneous determinant. No distinctness or localization is needed here.
- **Primitive vector and Smith exponent.** Frobenius deviations lie in
  `epsilon A`; their `m`th powers lie in `epsilon^m A`. The two-coordinate
  difference is primitive. In Smith coordinates at least one coordinate stays
  a unit, so its diagonal exponent is at least `m`; a zero diagonal entry is
  correctly treated as infinite. This remains valid without assuming the
  generic determinant is nonzero. Unit pair discriminants and the two pivot
  rows transfer the bound to the full observation matrix.
- **Five-index identity.** For `q >= 9`, offsets zero and one are inside the
  digit-block range. They give precisely `s`, `s^q`, `s^(q+1)`, `v^q`, and
  `s v^q`. The digit monomials have the same values at precisely these indices.
  For any positive power `m` of three, the recurrence gives
  `Q_(ml) = h_l^m = Q_l^m` there. No extension to arbitrary indices is used.
- **Moving marking and arbitrary deformations.** The central unramified
  hypothesis makes every `1+a_i tau` a unit. The central finite-field
  calculation forces `B` to have zero reduction for every pair, even though
  its generic value need not vanish. Its Frobenius power is therefore in
  `epsilon^m A`, with a common primitive coefficient vector. All five indices
  are distinct and lie in the prefix under the stated largest-index bound.
  Root normalization uses square roots of units; they exist over the stated
  algebraically closed residue field since two is invertible. Translation
  replaces `T` by a local coordinate without changing the span of `1,T`.
  These operations preserve the integral observation equivalence.
- **Complete-label bounds.** For `q >= 9`, `q/3` and `q/9` are allowed powers of
  three. The fixed-point inequality reduces to `q > 3`; the moving-point
  margin is exactly `q(5q-11)/18`. At `q=9` the moving bound is only one, so it
  does not by itself imply a first-order obstruction. The draft correctly
  restricts that moving-center consequence to `q >= 27`.
- **Function lattice.** Distinct nonzero central branch labels give independent
  square classes over `K(T)`: each factor has its own simple zero, which a
  square cannot have. The single-root and distinct pair-root characters are
  different and nontrivial; `1,T` are independent in the trivial character.
  Thus the full functions are independent. Their expansion at an unramified
  point is injective, so a finite coefficient minor is nonzero centrally.
  Its deformation is a unit minor, proving the stated saturation by solving
  for basis coefficients in those columns. This justifies zero function
  valuation independently of the deficient initial observation prefix.
- **Frozen vector and normal map.** For `m >= 3`, replacing `c(epsilon)^m` and
  `c(epsilon)^(2m)` by their central constants changes them only in order at
  least `m`. Hence the same central nonzero vector kills both `M_0` and `M_1`
  for every direction. The normal-map class vanishes; changes of integral
  matrix frames preserve this kernel-to-cokernel assertion. At the fixed
  point the two-coordinate vector is already constant. The stated thresholds
  for the fixed and moving cases are therefore valid.

## Hypotheses and scope

Characteristic three, powers of three, distinct central labels, unramified
central marking, and the strict prefix-index inequalities all have explicit
uses. Algebraic closedness is stronger than the algebraic column identities
need, but supplies all normalizing root values and keeps the curve setting
uniform; it is justified rather than an unexplained extra restriction.
Distinct finite-field reductions automatically imply `N <= q` in the
deformation clauses, while the polynomial clause correctly has no such bound.
No unused hypothesis requires removal.
