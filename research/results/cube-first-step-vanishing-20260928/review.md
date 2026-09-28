# Focused correctness review

Reviewed 28 September 2026, as the cycle's single fresh-context reviewer at
medium reasoning. The parent cycle measures the overlapping review interval.
No numerical computation or additional reviewer was used.

Scope: `/tmp/bmd-star-projection-entry.html`, corresponding to notebook entry
`entry-2026-09-28-cube-star-projection-loss`. Dependencies read directly in the
binary-multiplicity-degree notebook: the full relevant statements and proofs at
`cube-epd-presentation-first-class`, `cube-centered-ore-recurrence`, and
`cube-marked-ore-block-presentation`; the marked-deflation statement; and the
Fischer paragraph of `entry-2026-09-27-cube-normalized-layer-route-review`.
The interpolation formula was checked from the draft's direct proof rather
than assumed from its external attribution.

Verdict: the mathematical claims pass. The recommended scope clarification
below has been incorporated and checked; no mathematical gap or unused
substantive hypothesis remains.

- The cardinal product evaluates to one at its own pair and zero at every
  different pair. Distinct roots imply distinct pair points and nonzero
  denominators. The ordinary dimension is exactly the number of pairs.
- Each denominator contains exactly the distinct edges incident to either
  member of its pair, excluding the edge joining that pair. Its degree is
  twice N minus four. Every edge occurs in some denominator for N at least
  three. In the polynomial ring on independent labeled roots their least
  common multiple is consequently the squarefree Vandermonde, up to a unit.
  The draft correctly distinguishes this parameter-ring statement from
  specialization to a fixed tuple and does not treat clearing it as free.
- The coefficients modulo v and modulo s squared are the stated nonzero
  binomial coefficients. In each weighted degree the respective quotient
  is one-dimensional and the harmonic line maps isomorphically onto it.
  This proves both direct sums and the asserted projected source images.
- The first evaluation rank follows by fixing one root: the generating
  function factors as (1+a_1 T)^(-3/2)(1+xT)^(-3/2), so its coefficient of
  index j has degree j in x with precisely the stated leading coefficient.
- For the second rank, the block theorem gives a polynomial basis containing
  all the first-block iterates, with length 2N-3. The recurrence changes this
  prefix to the pair-column prefix by an invertible triangular matrix.
  Dividing a pair column by its alternating factor gives H_j: the numerator
  generating function is
  y(1+xT)^(-1/2)(1+yT)^(-3/2)
  minus x(1+yT)^(-1/2)(1+xT)^(-3/2), which equals
  (y-x)((1+xT)(1+yT))^(-3/2).
  Evaluation of the full exterior target is invertible at distinct roots,
  and all these alternating factors are nonzero. Thus no exceptional
  separated tuple loses rank. The translation identity in the draft is exact
  and triangular with diagonal one, so centering introduces no restriction.
- For Q=A s squared+B v with A nonzero, ordinary degree is additive and the
  kernel intersection with the source is Q times the ordinary degree
  M-2 space. The image dimension is 2M+1, including M=1 with zero kernel.
  Grading places it inside the harmonic prefix of that same dimension,
  proving equality. The direct-sum condition on general Q is a necessary
  stated hypothesis; the draft does not claim it for every A,B.
- At N=3 the second image has dimension three, exactly all pair channels;
  the first has dimension two. The loss formulas and the zero remaining
  block rank are consistent. At N=4 the alternative loses one channel.
- The first-block identification is an equality of spans through the actual
  triangular source change, not just equality of dimensions. Its rank
  complement is the established marked-core rank. No higher-degree
  interpolation impossibility or new original threshold follows, and none
  is asserted. In particular this result alone does not determine the full
  binary odd-field degree function.

Recommended clarification: the cited EPD proposition is stated for N at least
five, while this theorem begins at three. Its harmonic-kernel proof is
independent of N and applies unchanged, but say this explicitly. Alternatively,
in weighted degree j, applying L to s^(j-2b)v^b gives the term
b(j-b+3/2)s^(j-2b)v^(b-1), besides the second-s derivative term.
For b from one to floor(j/2), these nonzero coefficients give a triangular
surjection onto degree j-2. The kernel is one-dimensional and contains H_j,
as direct differentiation of its generating series verifies. This covers
all j without any N assumption.

Correction check: the revised draft now includes exactly this monomial
formula and triangular-surjectivity argument, explicitly covering N=3,4.
The correction passes and closes the sole clarification.

The characteristic-zero assumption is used in the harmonic coefficients,
factorial source changes, centering, and the cited polynomial block theorem.
Distinctness is used for interpolation, Vandermonde evaluation, and division
by alternating factors. Neither may be silently dropped. Ordinary
interpolation alone has a broader field scope, which does not extend the
combined theorem to positive characteristic.
