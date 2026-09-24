# Binary multiplicity degree formalization route

Dependency-first plan for `thm:binary-multiplicity-degree-formula`, based on its
[proof](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#binary-multiplicity-degree-formula-theorem)
in the side notebook, down to the imported multiplicity Schwartz–Zippel lemma. Everything
the proof uses is formalized, including that input. Planning phase only (24 September 2026):
this file fixes the target, the dependency order and the obligations. It assigns no work and
is not evidence of verification. `Mxx` identifiers are planning references, not claim-index
labels.

## Target

For every `k ≥ 1` and `n ≥ m(k) = ⌊log₂ k⌋ + 2`, the least total degree of a formal
polynomial `P ∈ 𝔽₂[x₁,…,xₙ]` with Hasse multiplicity at least `k` at every nonzero point of
`𝔽₂ⁿ` and less than `k` at the origin is `2k + n − 2 − ⌊log₂ k⌋`. The upper bound also holds
for every `n ≥ 1`.

Intended Lean form: with `Admissible n k P := (∀ a ≠ 0, k ≤ mult a P) ∧ mult 0 P < k`
over `ZMod 2`, prove both conjuncts:

- (i) every admissible `P` has `totalDegree P ≥ 2k + n − 2 − Nat.log 2 k` when `n ≥ m(k)`;
- (ii) some admissible `P` has `totalDegree P ≤ 2k + n − 2 − Nat.log 2 k` for every `n ≥ 1`.

Together they give the exact minimum. "Minimum" is stated through these two conjuncts, not
through `sInf`, so the statement shows directly which direction each hypothesis serves.
`mult 0 P < k` excludes `P = 0`, because `mult a 0 = ⊤`.

Indexed claims that the same proofs cover, recorded when the target is done:
- `conj:binary-multiplicity-degree-formula`, the same statement;
- `thm:binary-multiplicity-lower-bound` (M11);
- `lem:one-dimension-degree-step` (M10);
- `lem:catalan-truncation-vanishing` (M13);
- `thm:catalan-truncation-per-order-construction` (M14);
- `audit:binary-multiplicity-cover-question` (M07).

Separately indexed downstream results are not targets. These include the corollaries through
15 and through 31, the certificate lemmas, `cor:power-of-two-factor-construction`, the
conditional theorems and the per-order corollary.

## Conventions fixed before any proof

- **Multiplicity.** `shift a P := aeval (fun i => X i + C (a i)) P`.
  `mult a P : ℕ∞` is the least total degree of a monomial in the support of `shift a P`,
  and `⊤` for `P = 0`. This is the notebook's and the note's Hasse multiplicity; no
  reduction modulo `xᵢ² − xᵢ`. Equivalent characterization to prove: `m ≤ mult a P` iff
  every coefficient of `shift a P` of total degree below `m` vanishes.
- **Degree.** Joint total degree `MvPolynomial.totalDegree`, never the degree in one variable.
- **Points.** `Fin n → ZMod 2`; the nonzero points are the `2ⁿ − 1` vectors other than `0`.
- **Binary digit sum** `s₂`. Use the Mathlib notion to be identified in M12 (`Nat.digits 2`
  sum or a bit-count function), with one bridge lemma if two notions meet.

## Ordered obligations

Rows are in topological order. "Helper" means a statement used inside a larger proof, to be
extracted with its own Lean declaration; it gets a claim label only when it is reused across
files or already indexed. Provisional marks an API guess not yet checked against the pinned
Mathlib (commit `67248ba3`); no local Mathlib checkout exists yet.

| Order | Obligation | Direct prerequisites | Source, scope and notes |
| --- | --- | --- | --- |
| M01 | **Multiplicity foundations.** `shift`, `mult`. Characterization by coefficients below `m`; `mult a (P+Q) ≥ min`; `mult a 0 = ⊤`; `mult a c = 0` for a nonzero constant; `mult a P ≤ totalDegree P` for `P ≠ 0`. `shift` is an algebra automorphism with inverse `shift (−a)`, preserving `totalDegree`. `lowest a P`: the lowest homogeneous component of `shift a P`. | — | [Note §1 definition](../publications/binary-polynomial-multiplicity/sections/01-question.tex). Any commutative ring where possible, fields where needed. Mathlib: `aeval`, `homogeneousComponent`, `IsHomogeneous`, `totalDegree_add` (provisional names). |
| M02 | **Products (fact A).** `mult a (P*Q) ≥ mult a P + mult a Q` over any commutative ring. Equality over an integral domain, because the product of the lowest components is nonzero and homogeneous. | M01 | Notebook [facts (A)–(C)](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#power-of-two-factor-reduction), stated there without a separate label. Equality is needed for the exact origin order in M14 and the lowest component in M10. |
| M03 | **Elementary factors over `𝔽₂` (facts B, C).** `mult a (1+xᵢ)^M ≥ M·aᵢ` (`aᵢ ∈ {0,1}` as a natural number), hence `mult a (∏ᵢ (1+xᵢ)^M) ≥ M·|a|`. `mult a (xᵢ²+xᵢ) ≥ 1` at every point of `𝔽₂ⁿ`. `mult 0 (x₁²+x₁)^ℓ = ℓ`. | M01, M02 | Same facts. Only the displayed directions are used; the exact `mult_a F_n = |a|` is not needed for the target. |
| M04 | **Hasse coefficient polynomials.** For a multi-index `β`, a polynomial `D^β P` with `eval a (D^β P)` equal to the coefficient of `z^β` in `shift a P`. `totalDegree (D^β P) ≤ totalDegree P − |β|`. `mult a (D^β P) ≥ mult a P − |β|`, via the binomial identity for coefficients of `shift a (D^β P)`. | M01 | Standard Hasse-derivative facts; DKSS Proposition 2.5-type statements (provisional reference; read DKSS before use). Needed only inside M06. Mathlib has univariate `Polynomial.hasseDeriv`; the multivariate version is expected to be missing (provisional). |
| M05 | **Univariate bridge.** For `g ∈ F[y]`, Hasse multiplicity at `c` equals `Polynomial.rootMultiplicity c g`. For finite `S ⊆ F` and `g ≠ 0`, `Σ_{c∈S} rootMultiplicity c g ≤ natDegree g`. Restricting to a coordinate line does not lower multiplicity: `mult c (P restricted to (a', y)) ≥ mult (a',c) P`. | M01 | Mathlib: `rootMultiplicity` through `taylor`/trailing degree, `Polynomial.count_roots`, `card_roots'` (provisional names). |
| M06 | **Multiplicity Schwartz–Zippel (third party).** For any field `F`, `n ≥ 1`, nonzero `P` of total degree `d` and finite nonempty `S ⊆ F`: `Σ_{a∈Sⁿ} mult a P ≤ d·|S|^{n−1}`. | M01, M02, M04, M05 | Dvir–Kopparty–Saraf–Sudan, SICOMP 2013, Definition 2.2 and Lemma 2.7, as quoted in the [note](../publications/binary-polynomial-multiplicity/sections/01-question.tex). Not yet indexed: register as `third-party:DKSS-multiplicity-schwartz-zippel` in `third-party-claims/`, with attribution. Before drafting, read the DKSS proof and compare its multiplicity definition and hypotheses with M01. Planned proof, induction on `n` (their argument): write `P = Σ_{j≤t} P_j(x′) x_nʲ` with `P_t ≠ 0`, `deg P_t ≤ d−t`. For each `a′`, take `β′` with `|β′| = mult a′ P_t` and `D^{β′}P_t(a′) ≠ 0`. The univariate `g(y) = D^{(β′,0)}P(a′,y)` has degree `t`, and `mult (a′,c) P ≤ |β′| + mult c g`. This needs `D^{(β′,0)}P = Σ_j (D^{β′}P_j) x_nʲ`, so that `g ≠ 0` has leading coefficient `D^{β′}P_t(a′)`. Sum over `c` (M05), then over `a′` (induction). Base `n = 1`: M05. Faithful general statement, not only `S = 𝔽₂`. |
| M07 | **The note's deduction** (`audit:binary-multiplicity-cover-question`). For positive `n,k` and nonzero `P ∈ 𝔽₂[x₁,…,xₙ]` with `mult a P ≥ k` at every nonzero `a`: `totalDegree P ≥ 2k − ⌊k/2^{n−1}⌋`. | M06 | [Note §2](../publications/binary-polynomial-multiplicity/sections/02-deduction.tex). State it with `P ≠ 0`, the weaker hypothesis the note's remark allows, so the origin bound is a corollary. Arithmetic: `k(2ⁿ−1) ≤ d·2^{n−1}` gives `d ≥ 2k − ⌊k/2^{n−1}⌋` in `ℕ`. |
| M08 | **Invertible linear substitutions over `𝔽₂`.** For invertible `A : Matrix (Fin n) (Fin n) (ZMod 2)`, `P ∘ A` is defined by `aeval` of the linear forms. It preserves `totalDegree`, and `mult a (P ∘ A) = mult (A a) P`. `A` permutes the nonzero points. The lowest component at `0` of `P ∘ A` is the lowest component of `P` composed with `A`. | M01 | Helper extracted from the [one-dimension step](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#one-dimension-degree-step) proof. Degree preservation uses `A⁻¹` for both directions. |
| M09 | **A linear form not dividing the lowest component.** A nonzero homogeneous `L ∈ 𝔽₂[x₁,…,xₙ]` of degree `ℓ < 2ⁿ − 1` is not divisible by some nonzero linear form `y`. For every nonzero linear form `y` there is an invertible `A` with `y ∘ A = xₙ`. | M08 | Same proof. Route: `MvPolynomial (Fin n) (ZMod 2)` is a UFD (Mathlib instance, provisional). A degree-one polynomial is irreducible, hence prime. Over `𝔽₂` distinct nonzero linear forms are not associated, because the units are `1`. So the product of all `2ⁿ − 1` forms would divide `L`, contradicting degree `ℓ`. Basis completion via Mathlib `Basis`/`Matrix` API (provisional). Boundary case `ℓ = 0` must pass. |
| M10 | **The one-dimension step** (`lem:one-dimension-degree-step`). For `n ≥ 2`, `1 ≤ k < 2ⁿ` and admissible `P` in dimension `n` with origin order `ℓ`, there is an admissible `S` in dimension `n−1` with `totalDegree S + 1 ≤ totalDegree P` and origin order exactly `ℓ`. | M01, M02, M08, M09 | [Statement and proof](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#one-dimension-degree-step), with the order-preserving form of the [per-order step](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#per-order-dimension-step) at no extra cost. Parts: (a) degree drop of `S = P(x′,0) + P(x′,1)` is the one-group case of `cubeDifference_degree`; reuse [BinaryCubeDegreeDrop.lean](claims/BinaryCubeDegreeDrop.lean) after checking its statement, or prove the one-variable case directly. (b) Specializing a variable to a constant keeps multiplicity. (c) `lowest 0 (P(x′,0)) = L(x′,0) ≠ 0` when `xₙ ∤ L`, and `P(z′,1)` has order `≥ k > ℓ`. Split off the last variable with `finSuccEquiv` or `Fin.snoc` (provisional). |
| M11 | **The lower bound** (`thm:binary-multiplicity-lower-bound`). For `k ≥ 1`, `n ≥ m(k)` and admissible `P`: `totalDegree P ≥ 2k + n − m(k)`. | M07, M10 | [Statement and proof](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#binary-multiplicity-lower-bound). Base at `n = m(k)`: M07 with `⌊k/2^{m−1}⌋ = 0`, because `k < 2^{m−1}`. Induction upward, applying M10 at each `n′ > m(k)`, where `k < 2^{n′}`. `m(k)` is `Nat.log 2 k + 2`. |
| M12 | **Binary digit arithmetic.** `s₂(2ʲ) = 1`, `s₂(a+b) ≤ s₂ a + s₂ b`, so `r` powers of two summing to `σ` need `r ≥ s₂ σ`. `s₂(σ+1) ≤ s₂ σ + 1`, so `σ ↦ 2σ − s₂ σ` is monotone. `s₂(2ʲ − 1) = j`. `2^{Nat.log 2 k} ≤ k < 2^{Nat.log 2 k + 1}`. | — | Used by M13–M15. Mathlib `Nat.digits`/bit lemmas (provisional). |
| M13 | **The truncated product** (`lem:catalan-truncation-vanishing`). Over `𝔽₂`, `g_s` is the sum, over maps `c : Fin n → Option (Fin (J+1))` with cost `Σ 2^{c i} ≤ s−1`, of `∏_{c i = some j} yᵢ^{2ʲ} · ∏_{c i = none} (1+xᵢ)`. It satisfies `mult a g_s ≥ s` at nonzero `a`, `eval 0 g_s = 1`, and `totalDegree g_s ≤ n + 2(s−1) − s₂(s−1)`. | M01, M02, M03, M12 | [Statement and proof](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#catalan-truncation-vanishing); Menezes' construction (arXiv 2609.19009, §3), specialized and proved independently, so it goes in `claims/`, with attribution in the header. Steps: telescoping `(1+x) + Σ_{j≤J} y^{2ʲ} = (1+x)^{2^{J+1}}` (Frobenius in characteristic two, `add_pow_char_pow`); `∏ᵢ Nₛ(xᵢ) = g_s + R` by `Finset.prod_univ_sum` and a filter split; `mult R ≥ s` (M02, M03); M03 for the product. The degree-equality clause is not used and is omitted. Boundary cases `s = 1` (empty `T_s`, `g₁ = ∏(1+xᵢ)`) and `J` defined by `2ᴶ ≤ s−1 < 2^{J+1}`. |
| M14 | **The per-order construction** (`thm:catalan-truncation-per-order-construction`). For `n ≥ 1`, `k ≥ 1` and `ℓ < k`, `P = y₁^ℓ · g_{k−ℓ}` has `mult a P ≥ k` at nonzero `a`, `mult 0 P = ℓ` and `totalDegree P ≤ n + 2k − 2 − s₂(k−ℓ−1)`. | M02, M03, M13 | [Statement and proof](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#catalan-truncation-per-order-construction). The exact origin order uses M02 equality and `mult 0 g = 0`. |
| M15 | **Final theorem** (`thm:binary-multiplicity-degree-formula`). Conjuncts (i) and (ii) of the target. | M11, M12, M14 | [Statement and proof](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#binary-multiplicity-degree-formula-theorem). (ii): `ℓ = k − 2^J`, `J = Nat.log 2 k`, `s₂(2ᴶ−1) = J`, for every `n ≥ 1`. (i): M11. |

```text
M01 → M02 → M03 ─────────────┐
M01 → M04, M05 → M06 → M07 ──┼→ M11 ──┐
M01 → M08 → M09 → M10 ───────┘        ├→ M15
M12 → M13 → M14 ──────────────────────┘
```

The table, not this sketch, specifies all prerequisites.

## Third-party boundary

Only **M06**, the multiplicity Schwartz–Zippel lemma of Dvir–Kopparty–Saraf–Sudan, is an
imported result, and it is formalized, not assumed. Menezes' construction enters M13 as an
attributed idea with an independent proof. His theorem (`imp:menezes-characteristic-drop-degree`)
is not used: the target's lower bound comes from M06, M07 and M10, not from his paper.
Alon–Füredi is not needed. The case `k = 1` follows from M11 through M07 at `n = 2`.

## Necessary results and conveniences

- **Necessary:** M01–M15 as listed.
- **Conveniences not required:**
  - exact `mult_a ∏(1+xᵢ) = |a|`;
  - degree equality in M13;
  - the per-order upper bound below `k − 1` as a separate theorem (M14 already gives it);
  - `cor:power-of-two-factor-construction`;
  - symmetric-function certificates.
- **Alternative arguments:** M09 could avoid unique factorization by a direct argument over
  `𝔽₂`; choose it only if the UFD route has concrete friction. M04 could be replaced by
  arguing with coefficients of `shift` directly; keep whichever makes M06's induction shorter.

## Open planning questions

These are provisional and to be settled when proof-writing starts:
- the exact Mathlib names for the items marked provisional;
- whether `BinaryCubeDegreeDrop` fits M10(a) without adapting its tagging interface;
- the Lean statement of M06's index set `Sⁿ` (`Fintype.piFinset`);
- the `ℕ∞` arithmetic in M06's sums. The sum is finite because `P ≠ 0` makes every
  multiplicity at most `d`.
