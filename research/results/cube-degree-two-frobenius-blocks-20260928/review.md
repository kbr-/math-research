# Sparse cluster correctness review

Reviewed the complete draft `/tmp/bmd-sparse-cluster-entry.html` and both supplied
degree-one and Frobenius dependency excerpts. Read the workspace instructions and
computation rules. This was a symbolic correctness review; no computations or
additional agents were used.

**Verdict:** The rank obstruction, generic-point extension, infinite family, and
conditional smoothing valuation are correct. No mathematical counterexample or
missing substantive hypothesis was found. The transfer to the original cube
remains conditional on the explicitly stated internal quadratic normality.
The result does not disprove generic normality of the original cube.

## Required wording correction

Replace “It does not mean that its length-D jet matrix is flat: (RK) proves the
contrary” with “The full function-space limit has dimension D, but its length-D
jet map has rank at most D-ML.” Flatness is not synonymous with constant rank of
a matrix: a submodule of a free module over the smoothing DVR can itself be flat
even when the ambient specialization map loses rank. Moreover, the draft does
not assume or prove that the generic length-D jet matrix has rank D, so it should
not assert an actual generic-to-special rank drop. The displayed special-fiber
rank bound is exactly what the proof needs.

For a fully explicit justification of the stated saturation, add the following
short argument (it fills in the existing valid implication, without adding a
hypothesis): independence of the D reduced formal series supplies some finite
set of D coefficient columns with nonzero reduced determinant. Their normalized
matrix has a unit minor over the coefficient-field DVR. If a Laurent-series row
combination is coefficientwise regular, restriction to these columns and
inversion of that unit minor show that all its row coefficients are regular.
Thus the displayed normalized rows span the full coefficientwise regular
lattice in their generic span. The columns witnessing this can occur beyond the
first D coefficients; this is consistent with the jet obstruction.

## Checks

- The Frobenius recurrence and infinite product are valid formal-series
  identities. Product exponents have unique base-three representations with
  units digit at most two and higher digits at most one. The support count below
  3^s and the open zero interval ((3^s+1)/2,3^s) are correct for s at least one.
- Independent square classes of the distinct linear branch factors give the
  required independent characters over the rational function field. This yields
  exactly r+ML+binomial(L,2)=D independent functions.
- For every mixed row and tail coordinate, r-e_* <= j-e <= D-1. The strict lower
  inequality in (GC) and D <= q put that complete interval in the zero gap.
  Polynomial elimination gives the claimed rank bound, with equality for L=1.
- The first M allowed exponents form a digitwise downset. The displayed
  characteristic-three translation expansion therefore preserves their span in
  both directions. Translation of an unramified branch root only changes its
  nonzero scalar and parameter; extending constants to include the scalar is
  harmless. The generic-point assertion is justified.
- The estimate e_* = O(M^(log_2 3)) is valid, including the ceiling factor three.
  With M=floor(sqrt(3q/2)), r/q tends to 3/4 and e_*/q tends to zero. Uniformly
  for L <= M/10, the upper bound (363/400)q+2 for D is correct. This establishes
  both gap hypotheses eventually and yields infinitely many dimensions.
- The original degree-two count for M+L branch labels is binomial(M+L,2)+2;
  the cube dimension is M+L-1. The internal block has r rows. Scaling its T row
  by epsilon makes its entire coefficient matrix homogeneous by column.
  Inverting its constant normality matrix then dividing row j by epsilon^j
  gives regular rows with the stated monomial reductions.
- The anchored generalized Vandermonde for the first M allowed exponents is
  nonzero: the zero anchor isolates exponent zero and the remaining determinant
  has distinct permutation monomials. Earlier allowed columns are eliminated
  before dividing by epsilon^e; forbidden columns vanish identically. Hence
  the degree-one normalized rows really are coefficientwise regular.
- The transformation determinant is a coefficient-field unit times
  epsilon^(1-r(r-1)/2-L sum(E_M)). Thus B0 has precisely the stated minus one
  for the original unscaled T row. Full-series saturation and length-D jet
  saturation must remain distinguished as above.
- Residue rank at most D-ML forces the determinant of the normalized regular
  square matrix to be divisible by epsilon^(ML), whether or not the generic
  determinant is nonzero. This proves ord(Delta_original) >= B0+ML, including
  infinite order. Dyadic normalization and parameter rescaling are units and
  preserve this valuation. The leading normalized coefficient and the next
  ML-1 positions consequently vanish.

No substantive unused hypothesis requires removal. Generic parameters ensure
the simultaneous branch and Vandermonde independence used in the transfer;
the abstract rank bound itself works under the weaker distinct nonzero branch
condition already explained in the proof. No new finite checks are needed.
