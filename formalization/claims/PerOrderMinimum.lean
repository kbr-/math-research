/-
Claim: lem:per-order-all-dimension-minimum (part (ii))
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#per-order-all-dimension-minimum
Scope: For n ≥ 1 and k ≥ 1, the minimum over 0 ≤ ℓ < k of Φ(n,k,ℓ) = n + 2ℓ + Σ_{j<n} ⌊(k−ℓ−1)/2^j⌋
is D(n,k) = 2k + n − 2 − ⌊log₂ k⌋ for k < 2^(n−1) and 2k − ⌊k/2^(n−1)⌋ for k ≥ 2^(n−1): every Φ(n,k,ℓ)
is at least D(n,k), and some ℓ < k attains it. Deduced from the per-order theorem and the complete
degree formula (both verified), not by the notebook's direct digit-sum argument.
Declarations: MathResearch.PerOrderMinimum.min_phi
-/
import claims.PerOrderValue
import claims.BinaryMultiplicityDegreeComplete

namespace MathResearch.PerOrderMinimum

open MvPolynomial MathResearch.HasseMultiplicity MathResearch.PerOrderUpperBound
open MathResearch.PerOrderValue MathResearch.BinaryMultiplicityDegreeFormula
open MathResearch.BinaryMultiplicityDegreeComplete

/-- **The minimum over the origin order.** `min_{ℓ<k} Φ(n,k,ℓ) = D(n,k)`. -/
theorem min_phi {n k : ℕ} (hn : 1 ≤ n) (hk : 1 ≤ k) :
    (∀ ℓ, ℓ < k → degreeMin n k ≤ Phi n k ℓ) ∧ ∃ ℓ, ℓ < k ∧ Phi n k ℓ = degreeMin n k := by
  have hle : ∀ ℓ, ℓ < k → degreeMin n k ≤ Phi n k ℓ := by
    intro ℓ hℓ
    obtain ⟨⟨P, hP, h0, hdeg⟩, _⟩ := per_order_value hn hℓ
    have hadm : Admissible n k P := ⟨hP, by rw [h0]; exact_mod_cast hℓ⟩
    rw [← hdeg]
    exact (degree_complete hn hk).2 P hadm
  refine ⟨hle, ?_⟩
  obtain ⟨⟨P, hadm, hdeg⟩, _⟩ := degree_complete hn hk
  have hfin : mult 0 P ≠ ⊤ := ne_top_of_lt hadm.2
  set ℓ := (mult 0 P).toNat with hℓdef
  have h0 : mult 0 P = ℓ := (ENat.natCast_toNat hfin).symm
  have hℓ : ℓ < k := by
    have := hadm.2
    rw [h0] at this
    exact_mod_cast this
  refine ⟨ℓ, hℓ, le_antisymm ?_ (hle ℓ hℓ)⟩
  rw [← hdeg]
  exact (per_order_value hn hℓ).2 P hadm.1 h0

end MathResearch.PerOrderMinimum
