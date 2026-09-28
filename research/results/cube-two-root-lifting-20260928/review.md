# First-order confluent lifting review

One fresh-context Codex reviewer, explicitly medium reasoning.
Reviewed /tmp/bmd-first-jet-entry.html against bounded excerpts of the binary
factorization, monic-limit and marked-deflation proofs. No other reviewer was used.

Verdict: PASS on the algebra for every M >= 3, with one required scope clarification.

- State the weight assertion first over the formal centered localization obtained
  by inverting det U and det V, graded by deg b_i = 1. Then specialize at any
  admissible tuple in K. Arbitrary specialized elements of K do not carry that grading.
- Describe zero excess as formal localized weight accounting; it supplies no
  globally polynomial witness or original degree bound.

Checked: exact internal elimination; absence of a linear cross-row term;
the factor zeta_r/zeta_(r-1) in kappa; both starting indices of the finite-difference
identity; recurrence constants; P(0) = -c; and the positive sign in W0 Q1 = c w_(r-1).
The smaller moment degree of Q1 preserves the constant highest coordinate.
Undoing row multiplications remains valid modulo epsilon^2.

No s,t denominator or additional parameter localization is introduced.
Distinctness follows from invertibility of U for M >= 3, but keeping it explicit
is justified by the Vandermonde normalization. No substantive unused hypothesis
or further correctness gap was found.

Parent resolution: both scope clarifications are incorporated in the statement,
weight paragraph and assessment before assigning working-proof status.
