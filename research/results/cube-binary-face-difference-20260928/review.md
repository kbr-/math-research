# Consolidated correctness review — 28 September 2026

One fresh-context Codex reviewer, explicitly medium reasoning, reviewed the full
general proof, exact dependency excerpts, PARI driver and accepted output.
It ran no computations and spawned no other agents.

Verdict: no blocking mathematical gap. The all-m,r proof is valid independently
of the single symbolic calibration.

Checked:
- Column normalization and confluent cofactor reduction, including every power of x.
- Lower support and upper degree bounds.
- Double-sum coefficients and both Pfaff–Saalschutz substitutions.
- Rational cancellation before endpoint specialization.
- Nonzero constants at alpha=3/2.
- Differential-equation proof of simple roots, and exclusion of zero and one.
- Transfer through the supplied induction and exact boundary degree accounting.
- Consistency of the driver with accepted output.

The reviewer independently checked the small endpoints: in dimension one,
delta=k+ell gives saving h=m=3 at the boundary; in dimension two,
h=ceil(m/2)=3 at m=5. Both start at ell=0.
These computations are incorporated explicitly instead of attributing the
one-dimensional case to the square theorem.

Characteristic zero is essential to this proof. The condition r>=m-1 supports
the matrix indexing and regular normalization.

The theorem gives one specified degree-two boundary in every dimension.
It does not settle later orders, higher savings or positive characteristic.
No literature novelty conclusion is part of the correctness review.
