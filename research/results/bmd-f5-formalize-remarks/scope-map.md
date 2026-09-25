# Scope map: every unformalized mathematical claim of preprint v2

Assignment (user, 25 September 2026): the binary-multiplicity preprint should contain no
unformalized mathematical claim. Inventory of the claims of version 2 (after the checklist pass)
that no Lean declaration covered, with the decision for each. "Formalize" names the new module;
"rephrase" removes a claim the paper does not need; "cited" marks a statement about another
paper's content, which the paper attributes rather than asserts.

| # | Where | Claim | Decision |
|---|---|---|---|
| A | §1.1, §1.3, Lemma 3.2 | Φ = n + 2k − 2 − 2q − s₂(r) for k − ℓ − 1 = q2ⁿ + r | formalize (PerOrderArithmetic) |
| B | used by C | s₂(q2ⁿ + r) = s₂(q) + s₂(r) for r < 2ⁿ | formalize (BinaryDigitSums) |
| C | abstract, §1.1, Changes | Φ < n + 2k − 2 − s₂(k − ℓ − 1) when k − ℓ − 1 ≥ 2ⁿ; the construction does better than Menezes' form there | formalize (PerOrderArithmetic) |
| D | §1.1 bullet | Φ grows by 2ⁿ⁺¹ − 2 per block of 2ⁿ in k − ℓ | formalize (PerOrderArithmetic) |
| E | §1.2 Menezes, reals bullet | n ≥ k − 1 ⇒ Φ = n + 2k − 2 − s₂(k − ℓ − 1); also for n ≥ 2k − 3, k ≥ 2 | formalize (PerOrderArithmetic) |
| F | §1.2 SW bullet | Φ(n, k, k − 1) = n + 2k − 2 | formalize (PerOrderArithmetic) |
| G | reals bullet | s₂(k − ℓ − 1) ≥ 1 for ℓ ≤ k − 2 | formalize (BinaryDigitSums, s2_pos) |
| H | §1.1 bullet, Alon bullet | D(n,1) = n, D(n,4) = n + 4, D(n,8) = n + 11, D(n,15) = n + 25 for n ≥ ⌊log₂k⌋ + 2 | formalize (DegreeFormulaArithmetic) |
| I | §1.1 bullet | for k < 2ⁿ⁻², D exceeds the Schwartz–Zippel bound by n − 2 − ⌊log₂k⌋ ≥ 1; D(n+1,k) = D(n,k) + 1 for n ≥ ⌊log₂k⌋ + 2 | formalize (DegreeFormulaArithmetic) |
| J | §5 | at k = 3·2ⁿ⁻¹ the logarithmic expression is 2k − 2 and D = 2k − 3 | formalize (DegreeFormulaArithmetic) |
| K | Theorem 6.6 remark | D(n − 1, k) ≤ D(n, k) − 1 and δ(n − 1, k, ℓ) ≤ δ(n, k, ℓ) − 1 | formalize (DegreeFormulaArithmetic, PerOrderArithmetic) |
| L | Lemma 5.1 proof, Remark 5.3 | the digit argument (largest digit sum up to R is ⌊log₂(R + 1)⌋, the case analysis); extremal orders maximize 2q + s₂(r); for k ≤ 2ⁿ they are the ℓ with s₂(k − ℓ − 1) = ⌊log₂k⌋, e.g. ℓ = k − 2^⌊log₂k⌋ | formalize (PerOrderMinimumDirect): a direct formal proof of Lemma 5.1 following the text, and the characterization |
| M | §1.1 | n = 1, k = 3, ℓ = 0: δ = 3, attained by (1 + x)³, Menezes' form 4; n = 2, k = 5, ℓ = 0: 8 against 9 | formalize (PerOrderArithmetic) |
| N | §4 intro | Σ_{s≥0} Y^(2^s) solves X² + X = Y in F₂[[Y]] | formalize (ArtinSchreierSeries) |
| O | §3.2 | C_{a−1} is odd iff a is a power of two | formalize (CatalanParity) |
| P | §2 last paragraph | substitutions without constant term do not lower the origin order | link existing PerOrderExpansion.le_mult_zero_aeval |
| Q | §3.4 remark | the construction has degree exactly Φ | formalize (PerOrderArithmetic, from construction_spec and lower_bound) |
| R | §1.1 bullet | F² has degree 2ⁿ⁺¹ − 2 and multiplicity 2ⁿ (exact) | rephrase to "at most / at least", which Lemma 3.6 gives |
| S | §4 plan, outline, end remark | a form of degree ≥ 2ⁿ can vanish on V without being zero; for q = 0 the reduction is not needed | rephrase (claims not needed by the argument) |
| T | §3.2 remark | g₀ = g₁ in Lean | rephrase (drop; only s ≥ 1 is used) |
| U | §4 intro | x̂_K² + x̂_K = Y + Y^(2^K) | link existing PerOrderYCoefficient.xhat_sq_add |
| — | §1.2, §3.2, §6.5 | statements about the content of Menezes, Sauermann–Wigderson and BBDM (their theorems, their polynomials, the identification of g_s with Menezes' truncation) | cited; the paper will state that cited results of other papers are not formalized unless linked |

Existing coverage: per_order_value, construction_spec, lower_bound, min_phi, degree_complete,
cover_bound_attained_iff, degree_formula_extended, phi_of_lt_two_pow, legendre, s2 lemmas in
TruncatedProduct, Mathlib's Kummer theorem in digit form (sub_one_mul_padicValNat_choose_eq_sub_sum_digits),
Mathlib's catalan and succ_mul_catalan_eq_centralBinom, Nat.log.

Downstream results outside the assignment: none; the new modules are leaves under the paper's
aggregate module.
