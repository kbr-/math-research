# Binary polynomials vanishing to high order off the origin: the minimum degree at every origin order

**Preprint, version 2 (25 September 2026); all results and their dependencies verified in Lean.**

For n ≥ 1 and 0 ≤ ℓ < k, the least degree δ(n,k,ℓ) of a polynomial over F₂ in n variables with
Hasse multiplicity at least k at every nonzero point and exactly ℓ at the origin is

  δ(n,k,ℓ) = n + 2ℓ + Σ_{j<n} ⌊(k − ℓ − 1)/2^j⌋ = n + 2k − 2 − 2q − s₂(r),  where k − ℓ − 1 = q·2^n + r, 0 ≤ r < 2^n

([Lean](https://github.com/kbr-/math-research/blob/4f43ed20ae088e3a27ceae94bca7f0ec92d7c7b3/formalization/claims/PerOrderValue.lean)).
Menezes (arXiv:2609.19009) determined δ over every field for n ≥ k − 1, where k − ℓ − 1 < 2^n and
the value is n + 2k − 2 − s₂(k − ℓ − 1). Over F₂ the theorem extends this to every dimension. When k − ℓ − 1 ≥ 2^n
the formula changes form: each block of 2^n in k − ℓ − 1 is paid for by the square of
the product F of the 2^n − 1 affine forms that avoid the origin.

Minimizing over ℓ gives the least degree D(n,k) with multiplicity less than k at the origin:
2k + n − 2 − ⌊log₂ k⌋ for k < 2^(n−1), and the Schwartz–Zippel bound 2k − ⌊k/2^(n−1)⌋ for
k ≥ 2^(n−1). The bound, asked for by Bishnoi, Boyadzhiyska, Das and Mészáros, is attained if and
only if k ≥ 2^(n−2).

- **Upper bound.** The polynomial y₁^ℓ F^(2q) g_(r+1), where y₁ = x₁² + x₁ and g is Menezes'
  Catalan truncation specialized to F₂, with a telescoping proof valid in every dimension.
- **Lower bound.** Expand P in the basis x^ε (x² + x)^e and invert x² + x locally by the additive
  series Σ y^(2^s). The multiplicity conditions become additive forms that vanish on the span of
  x₁² + x₁, …, xₙ² + xₙ. Reducing modulo the vanishing polynomial of that span, with the
  combinatorial Nullstellensatz, exposes the lowest part of P at the origin.
- **Second proof of D(n,k).** Version 1's route, kept as Section 6: the multiplicity
  Schwartz–Zippel lemma of Dvir, Kopparty, Saraf and Sudan with a one-dimension step.

Every statement links to its Lean source at commit `4f43ed20`. The external inputs are stated
without proof in the text, but they are formalized as well, so the formal verification has no
unchecked premise. The paper supersedes version 1 and the deduction of the earlier
[note](../binary-polynomial-multiplicity/), which reappears as its Proposition 6.2.

## Verify the formal proofs

From the repository root, after the one-time Lean setup in
[formalization/README.md](../../formalization/README.md):

~~~sh
./formalization/verify.sh --target claims/BinaryMultiplicityDegreePaper2.lean
~~~

The expected axiom report for the main theorem is

~~~
'MathResearch.PerOrderValue.per_order_value' depends on axioms: [propext, Classical.choice, Quot.sound]
~~~

and the same for the other listed declarations. Appendix A of the paper gives the
statement-to-declaration map and commands for a fresh checkout.

- [Rendered PDF](whitepaper.pdf)
- [Main TeX source](whitepaper.tex), with the argument in [sections](sections)
- [Bibliography](references.tex)
- [Research notebook](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/)

Author: Kamil Braun, with assistance from Claude Opus 5.5 (mathematics, formalization and drafting,
in Claude Code) and GPT-6 Astra (the earlier note). The paper has not been externally peer reviewed.

## Build

~~~sh
./publications/binary-multiplicity-degree/build.sh
~~~
