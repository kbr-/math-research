# Dependency and scope map: density form and short-proof control

Assignment: user request of 17 September 2026 to formalize the readable exponential form of
the generic proof-size criterion, extended mid-cycle by the user to the short-proof control
remark of the 16 September entry.

## Targets

- cor:generic-CNF-density-exponential-form: C(a+k,k) <= C(a+r+k,k) exp(-rk/(a+r+k)); and under
  the criterion's hypotheses with r = h(k+1)+1 <= v,
  dim U <= (3S+|J|) C(v+k,k) exp(-rk/(v+k)), with the weaker exponent -hk^2/(v+k).
- obs:generic-criterion-short-proof-control: a base deriving one through d derives every
  polynomial of degree <= B for d <= B; a complementary pair L, 1-L derives one through
  degree one; hence no nonzero separated subspace exists over such a base.

## Boundary cases inspected

- k = 0 in the binomial estimate: both sides are one. K = 0 forces k = 0.
- r = 0: the factor is one and the estimate is an equality.
- r > v is excluded by the explicit hypothesis h(k+1)+1 <= v; there the criterion's
  truncated subtraction makes the binomial one and the exponential form is not claimed.
- The density dim U / C(v+k,k) is not a Lean term; the statement avoids division.
- Short-proof control: B >= 1 is needed because the complementary pair has degree one.

## Reused verified results

`generic_CNF_subspace_criterion`, `Derives.mul_polynomial`, Mathlib `Nat.add_one_mul_choose_eq`,
`Real.add_one_le_exp`, `Real.exp_nat_mul`.

## Outside the assignment

Any asymptotic statement, the heuristic relation k ~ d/(4h) between k and a separation
degree, and an audit of known short Res(+) refutations.
