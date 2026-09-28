# Consolidated correctness review

Reviewed the stable draft `/tmp/bmd-odd-schur-entry.html`, the supplied exact
Schur-hull, marked-block, Motzkin-network and ternary-pair dependency excerpts,
and the completed GP control source and full output. No computation was rerun.

Verdict: the raw full-series hull theorem and the stated path obstruction pass
this correctness review. No mathematical repair is required.

- Dyadic recursion and the zero value and first derivative on the diagonal
  justify division by the square of the difference without any factorial.
  Monic reduction preserves alternation and the claimed grading.
- The integral compound identity has exponent N-1; removing one difference
  and restoring its square gives the frame determinant V_N^N with the stated
  common pair ordering.
- At a non-dummy collision, the transformed rows have denominator exponents
  1 repeated N-2 times and 2 once. Their reductions are correct. Independent
  square classes separate the sign characters; within each repeated character,
  the two rational factors are independent over the residue field. The three
  trivial-character functions are also independent. Dummy collisions give
  the analogous pairs w_k, T w_k and trivial functions 1, T, T^2. These
  arguments include N=2 and require no odd-prime size bound.
- Independence supplies a finite unit minor of the transformed coefficient
  matrix. Thus the original full coefficient module has collision colength N.
  Off collisions, the same square-class argument gives a unit minor directly.
  Noetherian finiteness and the normal-domain intersection description then
  justify the embedded double-dual identity.
- The normalized determinant has homogeneous degree 3 binomial(N,4), allowing
  zero. Root transpositions give the same sign in the raw determinant and
  V_N^N. The common translated-series transformation is unitriangular on
  finite coefficient prefixes and has a determinant-one correction on 1,T.
  Hence symmetry and translation invariance hold in the asserted range.
- The path exchange transfers both output lengths and excursion shapes between
  two private copies with the same least-valued endpoint. It preserves weight
  and initial coefficient, reverses permutation sign, and has no fixed point.
  It works for every N at least three. It does not imply full determinant
  vanishing.
- The saved control reports all 54 coefficient-entry checks, nine original
  coefficient checks, the frame determinant identity, and detection of the
  altered column. Its displayed normalized determinant agrees with
  e_1^3-e_1 e_2-e_3 in characteristic three.

Hypothesis audit: pairwise distinct root valuations in the observation are
stronger than its involution needs. Only a unique strictly smallest valuation
among the nonzero roots is needed; all other sources remain unchanged by the
exchange. Either weaken that hypothesis, or explicitly retain it as the
particular separated-valuation ordering being tested. The hull theorem's
characteristic restriction is used throughout; the characteristic-three
restriction identifies the path network and q_l with the original coefficients.

The new claim is only the raw hull range extension. The supplied old theorem
also asserts companion descent, and the newer marked-block theorem uses
characteristic-zero scalar strings. Neither extra conclusion is proved or
silently transferred here. Finite-prefix nonvanishing remains open.
