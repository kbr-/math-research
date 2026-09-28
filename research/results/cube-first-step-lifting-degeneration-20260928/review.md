# Focused correctness review — 28 September 2026

Verdict: **Pass. No blocking mathematical gap or unused substantive hypothesis found.**

This was the cycle's single fresh-context review, performed at medium reasoning.
The reviewed draft was `/tmp/bmd-first-step-duality-entry.html`, with the supplied
first-post-boundary, marked-deflation, normalization-resolution, binary-face and
two-root-boundary dependency excerpts. The exact notebook statements and proofs
of `cube-normalized-first-step-sheaf` and
`cube-degree-two-normalization-quotient` were also read. The Macaulay2 driver,
sizing output and retained modular rank output were inspected; no computation
was rerun.

- **Exact Ext formula.** The excess shift is `p+1`, and dualizing it shifts Ext
  back by `-(p+1)`, so its initial degree becomes `p+1+e_N`. The rank-two
  determinant is `S(-lambda+1)`, giving the stated self-duality. The unique
  degree-zero source dual functional is nonzero because the target dual has
  strictly positive generator degrees. It annihilates the primitive boundary
  vector; the alternating pairing and primitivity identify its inverse image
  with exactly that old boundary line. Negative degrees contain no old line.
  At degree zero the Ext quotient removes precisely that line. The next possible
  new degree is bounded by transport at excess `lambda`. These facts prove (ED),
  including the cases of zero, positive or negative shifted Ext initial degree.
- **Normalization bound and conditional equality.** The full-defect quotient
  has exactly the shift `D22(-4)`. Since the actual prefix cokernel and its
  submodule kernel have codimension at least two, the asserted Ext injection
  has the correct direction. The largest last-resolution shift is `4N-5`;
  minimality ensures survival of a generator in its negative degree. This gives
  the unconditional upper bound. Codimension at least three makes the injection
  an isomorphism. Separately, elementary comparison in (ED) shows that (WG),
  together with the injection bound, is equivalent to the numerical equality;
  stabilization is correctly presented as a stronger sufficient mechanism.
- **Confluent monic relation.** The three-dimensional cross-row kernel follows
  by divisibility by the two monic prime factors over the polynomial ring.
  For clarity, its coefficient-vector convention is local column index
  `k=j-r`: the full moment polynomial is `u^r L_M(u)(A+Bu+Cu^2)`.
  The nonzero factors `s^r,t^r` are cancelled first over the fraction field,
  and monic division returns polynomial coefficients. The homogeneous
  finite-difference identity and the three-term recurrence give the displayed
  degree-two, degree-one and constant coefficients, respectively. Multiplying
  cross rows by powers of `s,t` does not change their polynomial kernel over
  this domain. The warning that this enlarged limit kernel is not a specialized
  actual kernel is essential and correctly retained.
- **Six-root computation.** The recurrence constructs the universal pair
  columns with all five coefficient variables retained. Source and target
  weights, the constant pivot determinant, polynomial Schur complement and
  exact coefficient reconstruction match the claim. The saved ranks equal
  the complete source dimensions at both excesses 41 and 42. The rational
  denominators and pivot remain invertible at the chosen prime, so modular
  injectivity implies rational injectivity. Multiplication by a power of `c2`
  reaches one of these two parity degrees from every smaller excess, while
  remaining nonzero in the free source. Together with the proved upper bound,
  this establishes the characteristic-zero value 43. It does not establish
  stabilization, and the draft makes no such inference.

No required correction. The local column-index convention above is an optional
clarification; it changes neither the polynomial kernel nor its excess.
