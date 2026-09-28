# Balanced-cluster correctness review

Reviewed 28 September 2026, fresh context, medium reasoning. Scope: the complete
draft `/tmp/bmd-balanced-cluster-entry.html`, dependency excerpt
`/tmp/bmd-balanced-cluster-dependency.html`, both balanced-cluster GP scripts,
and both complete retained computation outputs. No computation was rerun.

Verdict: **Pass, with two small presentation clarifications below.** No blocking
mathematical gap or unused substantive hypothesis was found. This is a review of
the stated uniform rank lemma, sequential obstruction, and one finite exact
simultaneous certificate; it does not verify the all-dimensional conjecture.

## Mathematical checks

- The triangular replacement by `w_i^3, T w_i^3, T^2 w_i` has determinant one.
  The first two groups fill precisely their supported residue-coordinate spaces.
  The identity `gamma_(j-1) = 2j beta_j` makes every unwanted residue-zero/one
  component of the third group eliminable. Generalized Vandermonde independence
  applies to every prefix used, including one anchored zero parameter. Thus
  `2B(L)+A(L)` is a joint rank calculation, not an invalid addition of overlapping
  ranks. Square-class independence supplies the asserted function-space dimension.
  The missing gamma coefficient at 2 and beta coefficient at 6 cover all L >= 3.
- The displayed W3 residual determinant is indeed
  `z^2 w^2 (w-z)^2 (b+c)` after `z=b^3, w=c^3` in characteristic three.
  Together with the prefix ranks it gives orders 0 through 7 and 9. Genericity
  is used: the displayed minor need not work at the exceptional specialization
  `b+c=0`. The internal three-label determinant also has the stated sign and
  value `b^3 c^3 (c-b)^3`.
- At the first confluence the polynomial, mixed, and exterior-pair blocks have
  dimensions 5, 9, and 3. At the second confluence the two internal blocks share
  exactly `1,T`; their sum is the eight-dimensional even Laurent space. For the
  mixed block, `T=U/(1-aU)` and `x^2=(1-aU)^(-1)` give
  `T^e x / x^5 = U^e(1-aU)^(2-e)`. These three polynomials form an invertible
  basis of degree at most two. Rescaling by powers of eta is legitimate over
  the smoothing fraction field. The order sequence therefore gives precisely
  the nine-dimensional odd space claimed. Distinct Laurent exponents give the
  finite unit minor required for full saturation at each stage.
- In characteristic three `(x-t)^18 = x^18+t^9 x^9+t^18`, so the witness belongs
  to the displayed space and has exact order 18 at every nonzero t. The
  coordinate change to T is unramified there because `2t/a` is nonzero. The
  sequential failure is consequently a full-limit obstruction.

## Finite certificate and precision audit

- The GP coefficients are the original pair expansions after `T=x^2-1`.
  For smoothing degree m <= 24, multiplying by x^48 places every term within
  exponents 0 through 98: the 99 retained columns contain the whole coefficient,
  not a spatial truncation of it. The field modulus and slopes printed in both
  outputs agree with the stated path; each cluster has distinct slopes.
- `matindexrank` selects independent residue rows. The kernel rows, together
  with those pivot rows, form the invertible constant transformation checked by
  the script. Only zero-residue rows are divided. The update discards one known
  precision level from all rows, safely retaining exact coefficients through
  degree 24 minus the step count. The final precision is 16 after eight steps;
  no omitted coefficient can affect any residue calculation. Independence of
  the final residue functions gives a unit coefficient minor and hence the
  full coefficientwise regular lattice, not just an unsaturated sublattice.
- The retained output reports ranks 3,5,9,11,13,15,15,16,17, final jet rank 17,
  determinant 2, and zero left kernel. The jet matrix uses nonnegative
  exponents of the x^48-multiplied basis. Since this multiplier has value one
  at x=1, it preserves this determinant as well as rank. The sequential control
  has rank 16 and the consecutive control has rank 17.
- The direct computation uses exactly pair coefficients T^2 through T^16,
  after the identity pivots supplied by 1,T. Its full output has initial term
  `2 eps^49`. The saturation divisibility count is 49 as asserted. Changing
  from T to x-1 multiplies the 17-jet determinant by `2^(0+...+16)=1` in
  characteristic three. The intervening saturation row transformations also
  have constant unit determinants, so the division count predicts the valuation;
  their product was not printed as an accumulated normalization and is not
  needed for the stated nonvanishing conclusion.
- The single specialization proves the reported mechanism certificate and
  nonvanishing of the original six-label determinant. It does not prove generic
  simultaneous-limit normality in all dimensions. The conjecture and its
  implication to original generic normality are explicitly distinguished from
  the finite result. No characteristic-zero claim is inferred from this field.

## Presentation clarifications

1. The negative-control exponent list is the exponent set in (SL) shifted by
   +13, rather than literally that Laurent exponent set. Say explicitly that
   the script multiplies by x^13, a unit at x=1, to use nonnegative exponents.
2. In the opening description, say that the direct determinant confirms the
   predicted *valuation* (and independently supplies its leading coefficient).
   The saturation trace alone has not recorded the accumulated unit factor
   converting its final determinant into the original determinant coefficient.

No further tests or optional extensions are requested.

## Scope clarification checked

The revised scope is correct: the computation certifies only the specified
specialized saturated limit. Its nonzero original determinant also proves
nonvanishing of the original six-label determinant polynomial, hence original
generic six-label normality. It does not establish generic saturated-limit
normality even for six labels: specialization of slopes can change the
coefficient-lattice valuations, so saturation and specialization need not
commute. No openness assertion for saturated-limit rank is needed or inferred.
The conjecture remains unproved for generic six-label slopes as well as for
general dimension. This narrower wording resolves the identified scope concern.
