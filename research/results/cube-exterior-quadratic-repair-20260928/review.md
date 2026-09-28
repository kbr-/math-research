# Polynomial quadratic jets: correctness review

One fresh-context Codex reviewer, explicitly set to medium reasoning, reviewed the
complete draft and exact channel, interpolation, elimination and Schur-frame excerpts.
No additional reviewer or computation was used.

Verdict: PASS. No correctness gap or substantive unused hypothesis found.

- The Euler inverse gives x^(r+M) dividing the node moment, so all prescribed
  jets are polynomial on the axes. Hermite inversion has only collision
  denominators, removed by the local criterion.
- With first correction zero and the first retained coordinate zero, the only
  low quadratic target is -mu times the next retained coefficient at index r-1.
- (stz)^(q-1) clears the truncated inverse of L. Multiplication preserves prior repairs.
- The exact exterior row factors are c_M(xy)^M. Multiplication by (stz)^M and
  the nonzero columns-1,2,3 minor, followed by its adjugate, repairs every row.
- Repair u-degree is at most D-1, and the highest initial coefficient is nonzero.
  The minor has degree 3q+6; total external excess is 9q+9M.
- The polynomial Schur frame cancels internal Vandermonde denominators directly.
  One F_M clears all internal coefficients because dependence is linear in eta,mu.
- Internal degrees lambda_M and lambda_M+2 make the epsilon expression an
  actual substitution of homogeneous polynomial source coefficients.
- The strict threshold difference is 9 binom(M,3)-15M > 0 for M>=5.

The conclusion is a complete normalized quadratic jet, not an actual kernel
witness. Nonzero eta is unnecessary for this sufficiency construction and is
appropriately absent from its assumptions.
