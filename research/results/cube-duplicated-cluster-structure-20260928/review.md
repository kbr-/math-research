# Moving-point limit correctness review

Reviewed the stable draft `/tmp/bmd-moving-point-entry.html` against the exact
dependency excerpts in `/tmp/bmd-moving-point-dependencies.html`. Read-only
mathematical review; no numerical reruns or external results used.

**Verdict:** The three mathematical claims and their arguments are sound, subject
to correcting the determinant-coordinate normalization and clarifying the dummy
zero label noted below. The supplied draft also needs its broken inline MathJax
escaping repaired before publication.

## Required corrections and clarification

- The transport dependency evaluates the original universal determinant at
  `a'/4`, not at `a'`: the latter are root-normalized parameters. State that the
  observed determinant specializes the root-normalized determinant at `a'`,
  equivalently the original determinant at `a'/4`. This does not affect the
  nonvanishing conclusion in odd characteristic.
- Explain that the six-label paths use a dummy zero label with constant root
  `w_0=1`. The nonzero-branch condition of the general criterion applies to the
  actual root variables, excluding this label. The displayed 17-dimensional
  quadratic space is the five-variable degree-two space. Without this
  clarification, the assertion that the two-cluster model meets the stated
  hypotheses appears to contradict its zero label.
- The reviewed temporary HTML has lost inline MathJax delimiters and many
  backslashes, including control characters in `varepsilon`. Repair the source
  encoding. Displayed MP, MK, MC, and ST were legible and reviewed as written.

## Checks

- Cauchy–Binet gives MP, including Laurent exponents; use matching column/row
  orders in its two minors. A distinct-largest-exponent basis has a unique
  top-degree contribution, so residue balance suffices; the smallest-exponent
  proof is identical. The two-dimensional control works for every prime,
  including two: the first Hasse derivative is exactly `t^p`, while both
  extremal sets fail modulo `p`.
- Regular jets reducing to an invertible jet matrix give a unit determinant.
  Undoing a coefficient-field basis change preserves generic rank. The local
  parameter substitution is invertible since `2t` is nonzero. Translation of
  `T` only lowers its exponent, and root scaling preserves total degree, so
  transport does not increase the degree budget. This argument uses no claim
  that saturation commutes with specialization.
- In characteristic three, `(x-t)^18 = x^18 + t^9 x^9 + t^18`.
  Both displayed kernel vectors therefore lie in the ambient space and vanish
  to order 18. The balanced 17-column minor proves ambient rank exactly 17 at
  every nonzero point; the two vectors are independent. Intersecting their
  endpoint plane with the stated endpoint rows gives exactly
  `AC + B D_0 t^36 = 0`. Equal and mirror frames yield respectively
  `1+t^36` and `1-t^36`, so the mirror failure at 1 coexists with generic
  classicality. The alternative largest-exponent argument also checks out.
- For `M=9h+5`, `L` is 8 modulo 9, the tail has `9h+3` terms, and its extra
  residue classes are 0, 2, and 4. The total counts in classes 0 and 8 differ
  by two. This proves the infinite-family monomial obstruction. The count of
  ST and its derivation from the hypothetical even/odd profile agree. The draft
  correctly does not infer that this profile is realized by an all-size
  lattice, or that lower terms cannot restore the determinant.

## Hypothesis audit

No harmful unused mathematical assumptions found. Independence of the reduced
basis is automatic once its full jet determinant is nonzero, but is appropriate
to state the limiting space and apply the separate sufficient pole tests. The
all-four-nonzero endpoint assumption is stronger than necessary for some
individual planes, but explicitly specifies the inherited open frame; it is
not presented as necessary for every possible endpoint plane. The old
transport and residue criterion are correctly identified as reused results.
