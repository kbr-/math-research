# Dependency and scope map: Lean formalization of thm:per-order-value-all-dimensions

Target (notebook anchor `per-order-value-all-dimensions`): for all n >= 1 and 0 <= l < k, the least
total degree of P in F_2[x_1..x_n] with Hasse multiplicity >= k at every nonzero point of F_2^n and
multiplicity exactly l at the origin is Phi(n,k,l) = n + 2l + sum_{j<n} floor((k-l-1)/2^j).

Conclusions to formalize:
1. Existence: some P with these properties has total degree exactly Phi (from the upper bound and 2).
2. Lower bound: every such P has total degree >= Phi.

Required supporting claims and planned coverage:
- thm:per-order-all-dimension-upper-bound (construction y_1^l F^(2q) g_(r+1)). Existing Lean covers
  its pieces: TruncatedProduct (mult_g_ge, eval_zero_g, totalDegree_g_le), PerOrderConstruction
  (mult_zero_y_pow), HyperplaneCoverUpperBound (card_dot_eq_one, the facts about F inside the proof;
  they will be restated as lemmas).
- lem:per-order-all-dimension-minimum, the Legendre form only: sum_{j<n} floor(m/2^j) = 2m - 2q - s_2(r)
  for m = q 2^n + r, 0 <= r < 2^n. Part (ii) (minimum over l) is not needed and not in scope.
- lem:binary-origin-jet-parametrization, part (a) only, in the direction used: every P has an
  expansion sum_eps x^eps A_eps(y), y_i = x_i^2 + x_i, and a nonzero coefficient of y^e in A_eps forces
  |eps| + 2|e| <= deg P. Parts (b), (c) are not needed by the formal route (see below).
- lem:y-coefficient-degree-formula, adapted: for P with multiplicity >= k at every nonzero point and
  any expansion as above, coeff_e(A_eps) = coeff_e(w prod_{i not in eps}(1 + xhat(y_i))) for |e| < k,
  with w = P(xhat(y)) and xhat(Y) = sum_{s<K} Y^(2^s) truncated (2^K >= k). This replaces the
  notebook's route through the jet polynomial P(v) (origin-jet lemma (b), (c)) by substituting
  x -> xhat(y) + delta directly into the expansion; the alternative argument will be recorded in
  full in the research entry.
- The lower-bound proof itself (steps 1-5 of the notebook entry): conditions (C_t), the forms
  E^(t)_j with their repeated-argument recursion, vanishing on the span V of y_1..y_n, reduction
  modulo the subspace polynomial L_V, and the coefficient of M*.

Existing Lean / Mathlib coverage used: HasseMultiplicity (mult, shift, coe_le_mult_iff,
add_le_mult_mul, mult_mul), OneDimensionStep (coe_le_mult_zero_iff, mult_eq_of_forall),
TruncatedProduct (s2, le_mult_sum, le_mult_pow, le_mult_prod), Mathlib's combinatorial
Nullstellensatz (MvPolynomial.eq_zero_of_eval_zero_at_prod_finset), Polynomial.modByMonic,
Nat.bitIndices, Frobenius on sums in characteristic 2.

Separately indexed downstream results outside this assignment: cor:per-order-all-dimensions-small-n,
thm:per-order-value-small-multiplicity (special cases, follow immediately but are separate targets),
conj:binary-multiplicity-per-order-all-dimensions (the same statement, proved by the target),
the q-ary theorem thm:q-ary-per-order-value (not in scope).
