# Correctness review — 28 September 2026

Verdict: passed, with no blocking issue. The new all-parameter obstruction and
the derivative identities are correct. The requested scope clarification is
verified in the canonical notebook: invocation of the invariant-prefix theorem
now explicitly assumes N >= 5; the new obstruction retains N >= 4.

Reviewed the stable entry draft, the supplied rectangular normal-map and local
Dunkl dependency excerpts, and the exact notebook statements and proofs at
`cube-invariant-prefix-stabilization` and `cube-double-pair-local-module`.
This was a symbolic proof review, with no numerical computation or literature
theorem imported.

- The normal pairing correctly freezes the right-kernel coefficients. Symmetry
  of H_j handles either ordering of each pair without a sign change.
- All three generating-function identities have the correct coefficients and
  signs. In the quadratic vector-field pairing, the term involving
  (a_i+a_j)h vanishes pair by pair; the left kernel kills every shifted column
  except V_(L+1), leaving exactly -(L+1)u_L omega V_(L+1).
- For V_1 the inside residue has N-2 terms and the outside residue has two.
  Equality of their corrected values forces c=1/N.
- For V_2 the displayed inside and outside residue sums are correct. Two
  outside pairs with distinct sums exist already when N=4. Subtracting their
  equations over K uniquely forces the displayed rational coefficients f,g;
  allowing denominators therefore creates no escape.
- Substitution of c=1/N leaves coefficient -A/N on every root variable outside
  the inside pair. Algebraic independence and characteristic zero make this
  nonzero, completing the contradiction for a single fixed label.
- The ramification warning correctly distinguishes the reduced full centered
  coefficient quotient from its root pullback with ideal (x^2,y^2). It does not
  substitute the nonreduced fixed-zero symmetric quotient for the centered one.

No unused substantive hypothesis was found. N >= 4 supplies the two outside
pairs; generic independent roots justify the rational-function comparison;
the specified K-linear pair permutations distinguish this action from scalar
root permutation. Characteristic zero is a sufficient common setting, without
any claim that it is the optimal characteristic restriction. The result excludes
only the stated lowering property for the stated connection and supplies no
normal-rank or cohomology-degree bound.
