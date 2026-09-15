/-
Claim: lem:affine-exclusion-parameter-bounds
Source: https://kbr.is-a.dev/math-research/#lean-affine-exclusion-parameter-bounds
Scope: Uniform square-condition and degree/board room for polynomial inventories and arbitrary fixed polynomial bounds in the bit length.
Declarations: MathResearch.eventually_affine_parameters
-/
import claims.RestrictionKernelBounds
import Mathlib.Analysis.SpecificLimits.Normed

namespace MathResearch
noncomputable section
open Filter
open scoped Topology

def uniformKernel (ℓ : ℕ) : ℕ := ⌈((ℓ:ℝ)+1)*(Real.sqrt 2)^ℓ⌉₊

private theorem sqrt_two_gt_one : 1 < Real.sqrt 2 := by
  nlinarith [Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 2), Real.sqrt_nonneg (2:ℝ)]

private theorem sqrt_two_pow_square (ℓ : ℕ) : ((Real.sqrt 2)^ℓ)^2 = (2:ℝ)^ℓ := by
  rw [← pow_mul, Nat.mul_comm ℓ 2, pow_mul, Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 2)]

private theorem shifted_pow_ratio (d : ℕ) {q : ℝ} (hq : 1 < q) :
    Tendsto (fun ℓ : ℕ => ((ℓ:ℝ)+1)^d/q^ℓ) atTop (𝓝 0) := by
  have h := ((tendsto_pow_const_div_const_pow_of_one_lt d hq).comp
    (tendsto_add_atTop_nat 1)).const_mul q
  convert h using 1
  · ext ℓ
    simp only [Function.comp_apply, Nat.cast_add, Nat.cast_one, pow_succ]
    field_simp
  · simp

private theorem eventually_polynomial_lt_geometric (d : ℕ) (C : ℝ) {q : ℝ}
    (hq : 1 < q) : ∀ᶠ ℓ : ℕ in atTop, C*((ℓ:ℝ)+1)^d < q^ℓ := by
  have h := ((shifted_pow_ratio d hq).const_mul C).eventually
    (gt_mem_nhds (by simp : C*(0:ℝ)<1))
  filter_upwards [h] with ℓ hℓ
  apply (div_lt_one (pow_pos (lt_trans zero_lt_one hq) ℓ)).mp
  simpa only [mul_div_assoc] using hℓ

private theorem uniformKernel_bounds (ℓ : ℕ) :
    1 ≤ uniformKernel ℓ ∧
    (((ℓ:ℝ)+1)*(Real.sqrt 2)^ℓ ≤ (uniformKernel ℓ:ℝ)) ∧
    (uniformKernel ℓ:ℝ) ≤ 2*((ℓ:ℝ)+1)*(Real.sqrt 2)^ℓ := by
  have hq : 1 ≤ (Real.sqrt 2)^ℓ := one_le_pow₀ sqrt_two_gt_one.le
  have hn : 0 ≤ (ℓ:ℝ) := Nat.cast_nonneg _
  have hu : 0 < ((ℓ:ℝ)+1)*(Real.sqrt 2)^ℓ := by positivity
  refine ⟨Nat.one_le_ceil_iff.mpr hu, Nat.le_ceil _, ?_⟩
  have h := Nat.ceil_lt_add_one hu.le
  change (uniformKernel ℓ:ℝ) < _ at h
  nlinarith

private theorem inventory_log_bound (a A ℓ : ℕ) :
    Real.log (4*((A*2^(a*ℓ)+1:ℕ):ℝ)) ≤
      Real.log (4*((A:ℝ)+1)) + (a:ℝ)*(ℓ:ℝ) := by
  have hp : (1:ℝ) ≤ (2:ℝ)^(a*ℓ) := one_le_pow₀ (by norm_num)
  have hcast : ((A*2^(a*ℓ)+1:ℕ):ℝ) ≤ ((A:ℝ)+1)*(2:ℝ)^(a*ℓ) := by
    push_cast
    nlinarith
  have hl : Real.log (2:ℝ) ≤ 1 := by have h := Real.log_le_sub_one_of_pos (by norm_num : (0:ℝ)<2); norm_num at h; exact h
  calc
    _ ≤ Real.log (4*((A:ℝ)+1)*(2:ℝ)^(a*ℓ)) := by
      apply Real.log_le_log (by positivity)
      nlinarith [mul_le_mul_of_nonneg_left hcast (by norm_num : (0:ℝ)≤4)]
    _ = Real.log (4*((A:ℝ)+1)) + (a*ℓ:ℕ)*Real.log 2 := by
      rw [Real.log_mul (by positivity) (by positivity), Real.log_pow]
    _ ≤ _ := by
      have ht := mul_le_mul_of_nonneg_left hl (by positivity : (0:ℝ)≤(a*ℓ:ℕ))
      push_cast at ht ⊢
      nlinarith

 theorem eventually_affine_parameters (a A d : ℕ) :
    ∀ᶠ ℓ : ℕ in atTop,
      2 ≤ ℓ ∧ 1 ≤ uniformKernel ℓ ∧ uniformKernel ℓ ≤ 2^ℓ+1 ∧
      (((2^ℓ+1:ℕ):ℝ)*Real.log (4*((A*2^(a*ℓ)+1:ℕ):ℝ)) ≤ (uniformKernel ℓ:ℝ)^2) ∧
      4*(uniformKernel ℓ-1) < 2^ℓ ∧
      2*(uniformKernel ℓ*(A*(ℓ+1)^d+1))-1 ≤ 2^ℓ := by
  have ha : ∀ᶠ ℓ : ℕ in atTop, 2*(a:ℝ) ≤ (ℓ:ℝ) :=
    tendsto_natCast_atTop_atTop.eventually (eventually_ge_atTop _)
  have hc : ∀ᶠ ℓ : ℕ in atTop, Real.log (4*((A:ℝ)+1)) ≤ (ℓ:ℝ) :=
    tendsto_natCast_atTop_atTop.eventually (eventually_ge_atTop _)
  have hg := eventually_polynomial_lt_geometric (d+1) (8*((A:ℝ)+1)) sqrt_two_gt_one
  filter_upwards [ha,hc,hg,eventually_ge_atTop 2] with ℓ ha hc hg hℓ
  have hk := uniformKernel_bounds ℓ
  have hq : 0 < (Real.sqrt 2)^ℓ := pow_pos (lt_trans zero_lt_one sqrt_two_gt_one) ℓ
  have hn : (1:ℝ) ≤ (2:ℝ)^ℓ := one_le_pow₀ (by norm_num)
  have ht : (1:ℝ) ≤ (ℓ:ℝ)+1 := by exact_mod_cast Nat.le_add_left 1 ℓ
  have htp : (1:ℝ) ≤ ((ℓ:ℝ)+1)^d := one_le_pow₀ ht
  have hlog := inventory_log_bound a A ℓ
  have hsquare : 2*Real.log (4*((A*2^(a*ℓ)+1:ℕ):ℝ)) ≤ ((ℓ:ℝ)+1)^2 := by
    have hm := mul_le_mul_of_nonneg_right ha (Nat.cast_nonneg ℓ)
    nlinarith
  have hu : (0:ℝ) ≤ (uniformKernel ℓ:ℝ) := Nat.cast_nonneg _
  have hs := sqrt_two_pow_square ℓ
  have hsq : (((2^ℓ+1:ℕ):ℝ)*Real.log (4*((A*2^(a*ℓ)+1:ℕ):ℝ)) ≤ (uniformKernel ℓ:ℝ)^2) := by
    have hl0 : 0 ≤ Real.log (4*((A*2^(a*ℓ)+1:ℕ):ℝ)) := Real.log_nonneg (by norm_cast; omega)
    have hm := mul_le_mul_of_nonneg_right hsquare (by positivity : (0:ℝ)≤(2:ℝ)^ℓ)
    have hu2 := mul_self_le_mul_self (by positivity : (0:ℝ)≤((ℓ:ℝ)+1)*(Real.sqrt 2)^ℓ) hk.2.1
    simp only [← pow_two] at hu2
    rw [mul_pow,hs] at hu2
    have hnn := mul_le_mul_of_nonneg_right (by linarith : (2:ℝ)^ℓ+1 ≤ 2*(2:ℝ)^ℓ) hl0
    have result : ((2:ℝ)^ℓ+1)*Real.log (4*((A*2^(a*ℓ)+1:ℕ):ℝ)) ≤ (uniformKernel ℓ:ℝ)^2 := by
      nlinarith
    simpa only [Nat.cast_add,Nat.cast_pow,Nat.cast_ofNat,Nat.cast_one] using result
  have hdeg : (A:ℝ)*((ℓ:ℝ)+1)^d+1 ≤ ((A:ℝ)+1)*((ℓ:ℝ)+1)^d := by nlinarith
  have hprod := mul_le_mul hk.2.2 hdeg (by positivity) (by positivity)
  have hgeom := mul_lt_mul_of_pos_right hg hq
  rw [pow_succ] at hgeom
  have hroomR : 4*(uniformKernel ℓ:ℝ)*((A:ℝ)*((ℓ:ℝ)+1)^d+1) < (2:ℝ)^ℓ := by
    nlinarith
  have hroom : 4*uniformKernel ℓ*(A*(ℓ+1)^d+1) < 2^ℓ := by exact_mod_cast hroomR
  have hfour : 4*uniformKernel ℓ < 2^ℓ :=
    lt_of_le_of_lt (Nat.le_mul_of_pos_right _ (Nat.succ_pos _)) hroom
  have hroom' : 4*(uniformKernel ℓ*(A*(ℓ+1)^d+1)) < 2^ℓ := by
    simpa only [Nat.mul_assoc] using hroom
  refine ⟨hℓ,hk.1,?_,hsq,?_,?_⟩ <;> omega
end
end MathResearch
