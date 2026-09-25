/-
Claim: thm:per-order-value-all-dimensions
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#per-order-value-all-dimensions
Scope: For all n ≥ 1 and 0 ≤ ℓ < k, the least total degree of P ∈ F_2[x_1,…,x_n] with Hasse
multiplicity ≥ k at every nonzero point of F_2^n and multiplicity exactly ℓ at the origin is
Φ(n,k,ℓ) = n + 2ℓ + Σ_{j<n} ⌊(k−ℓ−1)/2^j⌋: such a P of total degree exactly Φ exists, and every such P
has total degree ≥ Φ. Combines PerOrderUpperBound.per_order_upper_bound
(thm:per-order-all-dimension-upper-bound) and PerOrderLowerBound.lower_bound.
Declarations: MathResearch.PerOrderValue.per_order_value
-/
import claims.PerOrderUpperBound
import claims.PerOrderLowerBound

namespace MathResearch.PerOrderValue

open MvPolynomial MathResearch.HasseMultiplicity MathResearch.PerOrderUpperBound
open MathResearch.PerOrderLowerBound

noncomputable section

/-- **The per-order value** (`thm:per-order-value-all-dimensions`). For `n ≥ 1` and `ℓ < k`, the least
total degree of `P ∈ 𝔽₂[x_1,…,x_n]` with multiplicity `≥ k` at every nonzero point and exactly `ℓ` at
the origin is `Φ(n, k, ℓ) = n + 2ℓ + Σ_{j<n} ⌊(k − ℓ − 1)/2^j⌋`, and it is attained. -/
theorem per_order_value {n k ℓ : ℕ} (hn : 1 ≤ n) (hℓ : ℓ < k) :
    (∃ P : MvPolynomial (Fin n) (ZMod 2), (∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P) ∧
        mult 0 P = ℓ ∧ P.totalDegree = Phi n k ℓ) ∧
      ∀ P : MvPolynomial (Fin n) (ZMod 2), (∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P) →
        mult 0 P = ℓ → Phi n k ℓ ≤ P.totalDegree := by
  have hlower : ∀ P : MvPolynomial (Fin n) (ZMod 2),
      (∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P) → mult 0 P = ℓ →
        Phi n k ℓ ≤ P.totalDegree := by
    intro P hP h0
    have := lower_bound (σ := Fin n) (by rw [Fintype.card_fin]; exact hn) hℓ P hP h0
    rw [Fintype.card_fin] at this
    exact this
  obtain ⟨P, hP, h0, hdeg⟩ := per_order_upper_bound hn hℓ
  exact ⟨⟨P, hP, h0, le_antisymm hdeg (hlower P hP h0)⟩, hlower⟩

end

end MathResearch.PerOrderValue
