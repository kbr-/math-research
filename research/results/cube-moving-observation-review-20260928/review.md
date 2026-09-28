# Correctness review: moving observation controls

Reviewed the full draft `/tmp/bmd-moving-observation-review-entry.html` and
the exact dependency excerpts `/tmp/bmd-observation-review-dependencies.html`.
This was a read-only mathematical review; no numerical reruns were needed.

## Verdict

The three new mathematical claims pass, subject to one minor scope correction
in the explanatory Outside-lead text. No new mathematical gap or unused
hypothesis was found. These controls do not settle the degree-at-least-two
goal, and the draft accurately preserves that distinction.

## Required correction

- Outside lead 2 says common clearing “raises the function degree from one to
  n−1” without qualifying n. Say “changes the function degree from one to
  n−1, raising it when n≥3.” For n=2 the cost is zero; for n=1 it decreases
  the degree. The proposition's stated cost n−2 for n≥2 is already correct.

## Checks

1. **Cartier determinant and singular specialization.** The coefficient index
   pi−j in (CM) is correct: the retained exponent in the numerator of
   X^(j−1) f^((p−1)/2) dX/Y^p is pi−1. Its maximum degree is
   pg+(p−3)/2, so an output index greater than g is impossible. The same
   identity is valid in the function field at the proposed nonsquare singular
   polynomial, because X=z² remains separating in odd characteristic. On that
   normalization the stated g rational differentials are independent, and the
   logarithmic forms have numerators 2r_i times the Lagrange polynomials.
   These multipliers are nonzero. Cartier fixes the logarithmic basis and is
   semilinearly bijective on its span. Thus the polynomial determinant really
   is nonzero at that singular coefficient tuple; intersecting its nonvanishing
   locus with the squarefree locus is legitimate. No smoothness of the test
   tuple is assumed.

2. **All-character decomposition.** Distinct nonzero branch parameters give
   independent square classes. The indicated quotient differentials are
   independent, pull back regularly, and have the correct sign characters.
   The quotient genera sum to 1+(n−3)2^(n−2); tame Riemann–Hurwitz gives the
   same genus, with zero-dimensional differential spaces for the small cases.
   Infinity has inertia of order two, so it supplies the required additional
   branch point. Each subset's parameter projection is dominant onto its
   branch-configuration family; the normalized constant coefficient does not
   obstruct the generic hyperelliptic conclusion. The finitely many nonempty
   open ordinary loci consequently intersect. Cartier preserves the sign
   decomposition because p is odd and commutes with separable pullback.

3. **Digit gaps and completeness.** Squaring a finite truncation of (BD)
   telescopes, with the remaining factor tending to one in the formal-series
   topology. Digit uniqueness gives precisely the stated support. For p=3
   the units digit has no gap and the first missing exponent is 6; for p≥5
   it is (p+3)/2. A zero row among orders 0 through n makes the square jet
   determinant vanish. Transport makes this a generic-point obstruction, not
   only a special-point failure. The generalized Vandermonde argument for
   the exact generic orders is valid even in positive characteristic: its
   distinct permutation monomials cannot cancel. The complete-intersection
   compactification is linearly normal by its Koszul resolution, so the
   complete-series conclusion is correct.

   Optional self-contained clarification: display its equations
   a_1 X_i²−a_i X_1²−(a_1−a_i)X_0²=0 for i=2,...,n. In the affine chart
   at most one root coordinate vanishes. At infinity all X_i are nonzero.
   The Jacobian therefore has rank n−1 everywhere, verifying directly that
   this projective complete intersection is the smooth compactification used
   in the argument. For n=1 it is P¹. This is an exposition improvement,
   not a change in the theorem.

4. **Exact Cartier source change.** In characteristic three,
   w=(1−aT+a²T²)/w³, so the stated a^(2/3)/w output is exact with the
   correct sign. The coefficient function 1/w has a finite branch pole,
   although the differential dT/w itself is regular there; the draft properly
   makes its exclusion statement about the polynomial function space.
   Common multiplication by W gives the complementary square-class monomial.
   The supplied transport lemma's filtered basis proves its minimum polynomial
   degree is exactly n−1. This refutes the specified unqualified operation,
   not every possible twist or degree-specific Cartier argument.

5. **All-prime cancellation.** With coefficient columns ordered by exponents,
   the four nonzero coefficient minors all equal one. The pairs {0,p+1} and
   {1,p} have binomial Hasse minors p+1 and p−1, respectively, hence 1 and
   −1. They have equal exponent sum and cancel at every point. The pairs
   {0,p} and {1,p+1} have zero Hasse minors. This includes p=2, where the
   two equal nonzero contributions sum to zero. Each surviving exponent pair
   is residue-balanced at every power of p. Direct differentiation independently
   confirms the identically zero determinant.

6. **Bridge controls.** The nonzero column (1,i)^t with i²=−1 has rank one
   and zero symmetric Gram matrix over the specified algebraically closed odd
   field. This only defeats the replacement of positive Hermitian reasoning
   by that symmetric Gram test, as claimed. The symbolic transfer matrix has
   determinant uv−uv over every field. Its support assertion is over the
   polynomial ring/generic parameter field, rather than at every specialization;
   the draft's word “symbolic” makes that scope clear. Neither example claims
   to rule out actual algebraic left inverses or a correlated-weight construction.

## Source check

Read [Hidalgo, version 4, Section 5.1 and Section 5.4/Theorem 5.3](https://arxiv.org/html/1710.01349v4).
The source's Cartier definition and coefficient extraction agree with the
draft. The draft does not use the source's incorrect general identification of
p-rank zero with zero one-step Cartier. Its ordinary conclusion instead uses
bijective Cartier and the stable-rank characterization, and its determinant
argument is supplied directly.

## Review limits

This review covers the new mathematics and the supplied dependencies, not the
registry, historical novelty, all older follow-up entries, or the proposed next
research cycle. It introduces no stronger claim and requires no new numerical
evidence.
