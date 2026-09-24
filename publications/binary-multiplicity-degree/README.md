# The minimum degree of binary polynomials vanishing to high order off the origin

**Preprint, version 1 (24 September 2026); main theorem and all dependencies verified in Lean.**

For 1 ≤ k < 3·2^(n−1), the least degree of a polynomial over F₂ in n variables with Hasse
multiplicity at least k at every nonzero point and less than k at the origin is
2k + n − 2 − ⌊log₂ k⌋
([Lean](https://github.com/kbr-/math-research/blob/0bb1f4101d1a4e47364ffc773b38edba6ea20ddb/formalization/claims/BinaryMultiplicityDegreeExtendedRange.lean)).
The Schwartz–Zippel bound 2k − ⌊k/2^(n−1)⌋ asked for by Bishnoi, Boyadzhiyska, Das and Mészáros is
attained exactly for 2^(n−2) ≤ k < 3·2^(n−1).
The upper bound holds in every dimension, and for each prescribed origin order ℓ the paper gives
a polynomial of degree at most n + 2k − 2 − s₂(k − ℓ − 1).

The lower bound combines the multiplicity Schwartz–Zippel lemma of Dvir, Kopparty, Saraf and Sudan
with a one-dimension step that lowers the degree by one while keeping the origin order. The upper
bound specializes Menezes' Catalan truncation (arXiv:2609.19009) to F₂, with a telescoping proof
valid in every dimension. Menezes determines the per-order minimum for n ≥ k − 1; this paper
adds the range ⌊log₂ k⌋ + 2 ≤ n < k − 1.

Every statement links to its Lean source at commit `0bb1f410`. The external Schwartz–Zippel lemma is
stated without proof in the text, but it is formalized as well, so the formal verification has no
unchecked premise. The paper supersedes the deduction of the earlier
[note](../binary-polynomial-multiplicity/), which reappears as its Proposition 3.1.

## Verify the formal proofs

From the repository root, after the one-time Lean setup in
[formalization/README.md](../../formalization/README.md):

~~~sh
./formalization/verify.sh --target claims/BinaryMultiplicityDegreeExtendedRange.lean
~~~

The expected axiom report for the main theorem is

~~~
'MathResearch.BinaryMultiplicityDegreeExtendedRange.degree_formula_extended' depends on axioms: [propext, Classical.choice, Quot.sound]
~~~

Appendix A of the paper gives the statement-to-declaration map and commands for a fresh checkout.

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
