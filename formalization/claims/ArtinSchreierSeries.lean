/-
Claim: lem:artin-schreier-additive-root
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#artin-schreier-additive-root
Scope: Over F_2 = ZMod 2, the power series A = Σ_{s≥0} Y^(2^s) (coefficient 1 exactly at the powers of
two) solves the Artin–Schreier equation A² + A = Y in F_2[[Y]], and its truncation below degree 2^K is
the partial sum x̂_K(Y) = Σ_{s<K} Y^(2^s), which satisfies x̂_K² + x̂_K = Y + Y^(2^K).
Declarations: MathResearch.ArtinSchreierSeries.xhatPoly MathResearch.ArtinSchreierSeries.xhatPoly_sq_add MathResearch.ArtinSchreierSeries.asRoot MathResearch.ArtinSchreierSeries.coeff_asRoot_eq_one_iff MathResearch.ArtinSchreierSeries.asRoot_sq_add MathResearch.ArtinSchreierSeries.trunc_asRoot
-/
import claims.BinaryDigitSums
import Mathlib.RingTheory.PowerSeries.Trunc

namespace MathResearch.ArtinSchreierSeries

open MathResearch.TruncatedProduct MathResearch.BinaryDigitSums

noncomputable section

/-- The partial sum `x̂_K(Y) = Σ_{s<K} Y^(2^s)`. -/
def xhatPoly (K : ℕ) : Polynomial (ZMod 2) :=
  ∑ s ∈ Finset.range K, Polynomial.X ^ (2 ^ s)

theorem two_eq_zero_poly : (2 : Polynomial (ZMod 2)) = 0 := CharTwo.two_eq_zero

/-- `x̂_K² + x̂_K = Y + Y^(2^K)`. -/
theorem xhatPoly_sq_add (K : ℕ) :
    xhatPoly K ^ 2 + xhatPoly K = Polynomial.X + Polynomial.X ^ (2 ^ K) := by
  induction K with
  | zero =>
    simp only [xhatPoly, Finset.range_zero, Finset.sum_empty, pow_zero, pow_one]
    linear_combination (-(Polynomial.X : Polynomial (ZMod 2))) * two_eq_zero_poly
  | succ K ih =>
    simp only [xhatPoly, Finset.sum_range_succ] at ih ⊢
    rw [pow_succ 2 K, pow_mul]
    linear_combination ih + ((∑ s ∈ Finset.range K, (Polynomial.X : Polynomial (ZMod 2)) ^ 2 ^ s) *
      Polynomial.X ^ 2 ^ K + Polynomial.X ^ 2 ^ K) * two_eq_zero_poly

theorem coeff_xhatPoly (K d : ℕ) :
    (xhatPoly K).coeff d = if s2 d = 1 ∧ d < 2 ^ K then 1 else 0 := by
  simp only [xhatPoly, Polynomial.finsetSum_coeff, Polynomial.coeff_X_pow]
  by_cases h : s2 d = 1 ∧ d < 2 ^ K
  · obtain ⟨t, rfl⟩ := (s2_eq_one_iff d).1 h.1
    have ht : t < K := (Nat.pow_lt_pow_iff_right (by norm_num)).1 h.2
    rw [ite_eq_left h, Finset.sum_eq_single t]
    · simp
    · intro s _ hst
      refine ite_eq_right (fun heq => ?_)
      exact absurd (Nat.pow_right_injective (le_refl 2) heq).symm hst
    · intro hmem; exact absurd (Finset.mem_range.2 ht) hmem
  · rw [ite_eq_right h]
    apply Finset.sum_eq_zero
    intro s hs
    refine ite_eq_right (fun heq => ?_)
    subst heq
    exact h ⟨s2_two_pow s, (Nat.pow_lt_pow_iff_right (by norm_num)).2 (Finset.mem_range.1 hs)⟩

/-- The series `A = Σ_{s≥0} Y^(2^s)`. -/
def asRoot : PowerSeries (ZMod 2) := PowerSeries.mk fun d => if s2 d = 1 then 1 else 0

theorem coeff_asRoot (d : ℕ) : PowerSeries.coeff d asRoot = if s2 d = 1 then 1 else 0 := by
  simp [asRoot]

/-- The coefficients of `A` are `1` exactly at the powers of two. -/
theorem coeff_asRoot_eq_one_iff (d : ℕ) : PowerSeries.coeff d asRoot = 1 ↔ ∃ s, d = 2 ^ s := by
  rw [coeff_asRoot, ← s2_eq_one_iff]
  by_cases h : s2 d = 1 <;> simp [h]

/-- **The Artin–Schreier root.** `A² + A = Y` in `𝔽₂[[Y]]`. -/
theorem asRoot_sq_add : asRoot ^ 2 + asRoot = PowerSeries.X := by
  ext d
  have hd : d < 2 ^ (d + 1) := Nat.lt_two_pow_self.trans (Nat.pow_lt_pow_right (by norm_num) (by omega))
  obtain ⟨P, hPdef⟩ : ∃ P : PowerSeries (ZMod 2), P = (xhatPoly (d + 1) : PowerSeries (ZMod 2)) :=
    ⟨_, rfl⟩
  have hdvd : (PowerSeries.X : PowerSeries (ZMod 2)) ^ (2 ^ (d + 1)) ∣ asRoot - P := by
    rw [PowerSeries.X_pow_dvd_iff]
    intro m hm
    rw [hPdef, map_sub, coeff_asRoot, Polynomial.coeff_coe, coeff_xhatPoly]
    by_cases h : s2 m = 1 <;> simp [h, hm]
  obtain ⟨B, hB⟩ := hdvd
  have hA : asRoot = P + PowerSeries.X ^ (2 ^ (d + 1)) * B := by rw [← hB]; ring
  have hP : P ^ 2 + P = PowerSeries.X + PowerSeries.X ^ (2 ^ (d + 1)) := by
    rw [hPdef, ← Polynomial.coe_pow, ← Polynomial.coe_add, xhatPoly_sq_add, Polynomial.coe_add,
      Polynomial.coe_pow, Polynomial.coe_X]
  have hexp : (P + PowerSeries.X ^ (2 ^ (d + 1)) * B) ^ 2 + (P + PowerSeries.X ^ (2 ^ (d + 1)) * B) =
      (P ^ 2 + P) + PowerSeries.X ^ (2 ^ (d + 1)) *
        (2 * P * B + PowerSeries.X ^ (2 ^ (d + 1)) * B ^ 2 + B) := by
    ring
  have hne : ¬ 2 ^ (d + 1) ≤ d := by omega
  rw [hA, hexp, hP, add_assoc, ← mul_one_add, map_add, PowerSeries.coeff_X_pow_mul']
  simp [hne]

/-- The truncation of `A` below degree `2^K` is `x̂_K`. -/
theorem trunc_asRoot (K : ℕ) : PowerSeries.trunc (2 ^ K) asRoot = xhatPoly K := by
  ext m
  rw [PowerSeries.coeff_trunc, coeff_xhatPoly]
  by_cases hm : m < 2 ^ K
  · rw [coeff_asRoot]
    by_cases h : s2 m = 1 <;> simp [h, hm]
  · simp [hm]

end

end MathResearch.ArtinSchreierSeries
