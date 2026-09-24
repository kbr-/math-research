/-
Claim: thm:catalan-truncation-per-order-construction
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#catalan-truncation-per-order-construction
Scope: Over F_2 with a finite variable type σ and a chosen variable x₁ (so n = |σ| ≥ 1): for all k and
ℓ < k, P = (x₁² + x₁)^ℓ · g_{k−ℓ} has Hasse multiplicity ≥ k at every nonzero point, origin order exactly
ℓ, and total degree ≤ n + 2k − 2 − s₂(k − ℓ − 1). The degree-equality clause is not claimed.
Declarations: MathResearch.PerOrderConstruction.mult_zero_y_pow MathResearch.PerOrderConstruction.per_order_construction
-/
import claims.TruncatedProduct

namespace MathResearch.PerOrderConstruction

open MvPolynomial MathResearch.HasseMultiplicity MathResearch.TruncatedProduct

noncomputable section

variable {σ : Type*} [Fintype σ] [DecidableEq σ]

local notation "P2" => MvPolynomial σ (ZMod 2)

omit [Fintype σ] in
/-- `x² + x` has origin order exactly one, so its `ℓ`-th power has origin order `ℓ`. -/
theorem mult_zero_y_pow (i : σ) (ℓ : ℕ) : mult 0 ((X i ^ 2 + X i : P2) ^ ℓ) = ℓ := by
  have hy : mult 0 (X i ^ 2 + X i : P2) = 1 := by
    apply le_antisymm
    · have hc : (shift 0 (X i ^ 2 + X i : P2)).coeff (Finsupp.single i 1) ≠ 0 := by
        have : shift (0 : σ → ZMod 2) (X i ^ 2 + X i : P2) = X i ^ 2 + X i := by simp
        have hne : Finsupp.single i 2 ≠ Finsupp.single i 1 := by
          intro h
          have := congrArg (fun f => f i) h
          simp at this
        rw [this, AddMonoidAlgebra.coeff_add, Finsupp.add_apply, coeff_X_pow, coeff_X]
        simp [hne]
      have := mult_le_degree 0 _ hc
      simpa using this
    · exact one_le_mult_y 0 i
  induction ℓ with
  | zero =>
    rw [pow_zero, Nat.cast_zero, mult_eq_zero_iff]
    simp
  | succ ℓ ih =>
    rw [pow_succ, mult_mul, ih, hy]
    push_cast
    ring

theorem per_order_construction (i1 : σ) {k ℓ : ℕ} (hℓ : ℓ < k) :
    (∀ a : σ → ZMod 2, a ≠ 0 →
        (k : ℕ∞) ≤ mult a ((X i1 ^ 2 + X i1 : P2) ^ ℓ * g (k - ℓ))) ∧
      mult 0 ((X i1 ^ 2 + X i1 : P2) ^ ℓ * g (k - ℓ)) = ℓ ∧
      ((X i1 ^ 2 + X i1 : P2) ^ ℓ * g (k - ℓ)).totalDegree ≤
        Fintype.card σ + 2 * k - 2 - s2 (k - ℓ - 1) := by
  refine ⟨?_, ?_, ?_⟩
  · intro a ha
    refine le_trans ?_ (add_le_mult_mul a _ _)
    have h1 : (ℓ : ℕ∞) ≤ mult a ((X i1 ^ 2 + X i1 : P2) ^ ℓ) := by
      calc (ℓ : ℕ∞) = ℓ * 1 := by ring
        _ ≤ ℓ * mult a (X i1 ^ 2 + X i1 : P2) := by gcongr; exact one_le_mult_y a i1
        _ ≤ _ := le_mult_pow a _ _
    have h2 := mult_g_ge (σ := σ) (k - ℓ) a ha
    calc (k : ℕ∞) = ℓ + ((k - ℓ : ℕ) : ℕ∞) := by
          rw [← Nat.cast_add, Nat.add_sub_cancel' hℓ.le]
      _ ≤ _ := add_le_add h1 h2
  · rw [mult_mul, mult_zero_y_pow, (mult_eq_zero_iff 0 _).2 (by rw [eval_zero_g]; exact one_ne_zero),
      add_zero]
  · apply (totalDegree_mul _ _).trans
    have hy : ((X i1 ^ 2 + X i1 : P2) ^ ℓ).totalDegree ≤ 2 * ℓ := by
      apply (totalDegree_pow _ _).trans
      rw [mul_comm]
      gcongr
      apply (totalDegree_add _ _).trans
      apply max_le
      · apply (totalDegree_pow _ _).trans
        simp [totalDegree_X]
      · simp [totalDegree_X]
    have hg := totalDegree_g_le (σ := σ) (k - ℓ)
    have hs := s2_le_self (k - ℓ - 1)
    omega

end

end MathResearch.PerOrderConstruction
