# Correctness review: ternary pair algebra

Verdict: the mathematical claims and proofs pass direct algebraic review.
One wording correction is needed in the degree accounting: describe the two
determinants as homogeneous of the stated degrees, possibly zero. Saying they
have those degrees literally presupposes their nonvanishing, which is deliberately
left open for general branch count.

Scope: sole fresh-context medium review of the draft in
`/tmp/bmd-ternary-pair-entry.html` and the supplied dependency excerpts in
`/tmp/bmd-ternary-pair-dependencies.html`. No numerical reruns, broader searches,
or additional claims were used. The coordinator's cycle covers this review;
no separate timing session was started.

## Checks

- The pair points are distinct because their sum and product determine their
  unordered roots. Their maximal ideals are comaximal, so the evaluation
  algebra is exactly a product of R copies of K. The cardinal product has the
  asserted evaluations in characteristic three, including the empty product
  when N=2. No characteristic-zero interpolation rank is needed.
- In characteristic three, delta=s^2-v evaluates to (a_i-a_j)^2 and is a unit
  in the evaluation algebra. Formal square roots with constant term one exist
  uniquely because 2 is invertible; no binomial denominators in characteristic
  zero are being imported.
- Substitution of G=1-sT+delta T^2 Q gives
  Q=1+sTQ+delta T^2 Q^2. Substitution into G^3=(1+sT+vT^2)G
  gives the second MQ identity after cancellation in the polynomial domain.
  Thus polynomiality of each q_l does not depend on dividing by delta.
- H=(1+sT+vT^2)H^3 gives the three digit recurrences and hence the single
  monomial digit formula. Expanding G=(1+sT+vT^2)^2 H^3 gives precisely the
  three displayed coefficient formulas, with h_{-1}=0. Shifting by two gives
  all three TC formulas with the stated signs. These are coefficientwise
  identities at every index; an incomplete final triple presents no exception.
- The rows 1,T eliminate just the constant and linear coefficients. Each
  remaining pair row contributes delta times q_0 through q_{R-1}, giving PD
  up to the stated ordering sign. The degree-two root-space basis agrees with
  the supplied transport lemma at n=N-1. The weight of q_l is l; consequently
  the determinant weights are R(R-1)/2 and R(R+3)/2. The distinction between
  root-parameter weight and original function degree is maintained.
- The field/algebra distinction is correct. The row-dependent multipliers in
  TC are multiplication operators in the pair algebra, not common K-scalars
  permitting a column-basis substitution. Cubing is Frobenius-semilinear even
  if K is imperfect; no Frobenius surjectivity is required in these proofs.

## Four-label control

Expanding (e1*s+e2)P(s) gives the four pure-s terms in IP, including
the coefficient e2-e1^2 of s^3 and e2^2-e1*e3 of s. At a nonzero pair,
P(s)=-v(s+e1), and the complementary-root equation is

    s^3+e1*s^2+(e1^2+e2)*s-e1*e2+e3=0.

It makes (e1*s+e2)P(s)/v equal to s^3+e1*e2+e3, verifying IP.
The coefficient of h5 is -1, so this is a nontrivial relation over K.

For independence of h0 through h4, divisibility by P and the missing s^2
coefficient force g=A(e1*s+e2)P when e1 is nonzero. This is a valid generic
hypothesis and is explicitly used. The three remaining sums are distinct,
and Frobenius is injective on a field, so the reduced expressions
A(s^3+e1*e2+e3)+c force A=c=0. This proves exactly generic rank five,
without asserting rank five at every specialization.

For the q-prefix, direct reduction gives the three quadratic coefficients
printed in the draft. The first two yield A4=-A5*e1 and A3=A5*e1^2 without
dividing by e1. The last gives A5*(e1^3-e1*e2-e3)=0. Thus the invertibility
criterion applies even when e1=0, provided the original labels are distinct
and nonzero. Conversely A5=1 gives a nontrivial relation whenever F=0.
Finally,

    product(e1+u) = 2*e1^3+e1*e2+e3 = -F

in characteristic three, verifying the factorization. Its linear factors
are nonzero polynomials, so F is generically nonzero.

No unused mathematical hypotheses or unaddressed proof gaps were found.
This review verifies the exact reduction and the stated symbolic control,
not an all-N normality theorem or a new dimension range.
