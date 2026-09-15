/-
Claim: lem:ordinary-restriction-kernel-bound
Source: https://kbr.is-a.dev/math-research/#lean-ordinary-restriction-kernel-bound
Scope: Concrete binomial/exponential and ceil-square-root-log bounds for the ordinary restriction dimension comparison.
Declarations: MathResearch.restriction_choose_exp_bound MathResearch.kernel_ceil_exp_bound MathResearch.restriction_high_rank_bound MathResearch.kernelDegree_pos MathResearch.kernel_dimension_bound MathResearch.kernel_square_exp_bound MathResearch.kernel_ceil_square MathResearch.kernel_dimension_bound_of_square
-/
import Mathlib.Data.Nat.Choose.Bounds
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Algebra.Order.Floor.Semiring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.GCongr
import Mathlib.Tactic.Ring

namespace MathResearch
noncomputable section
open scoped BigOperators

private theorem choose_ratio_bound (m ℓ k d : ℕ) (hm : 0 < m) (hk : k ≤ m)
    (hnum : (d+k : ℝ) ≤ (ℓ : ℝ) * ((m : ℝ)-2*k)) :
    ((d+k).choose k : ℝ) ≤ (m.choose k : ℝ) * (ℓ : ℝ)^k * (1-(k:ℝ)/m)^k := by
  have hmR : (0 : ℝ) < m := by exact_mod_cast hm
  have hkR : (k : ℝ) ≤ m := by exact_mod_cast hk
  have hfact : (0 : ℝ) < k.factorial := by exact_mod_cast Nat.factorial_pos k
  have htop : (k.factorial : ℝ) * ((d+k).choose k : ℝ) ≤ ((d+k : ℕ) : ℝ)^k := by
    exact_mod_cast (by simpa [Nat.descFactorial_eq_factorial_mul_choose] using
      Nat.descFactorial_le_pow (d+k) k)
  have hbot : ((m+1-k : ℕ) : ℝ)^k ≤ (k.factorial : ℝ) * (m.choose k : ℝ) := by
    exact_mod_cast (by simpa [Nat.descFactorial_eq_factorial_mul_choose] using Nat.pow_sub_le_descFactorial m k)
  have hcast : ((m+1-k : ℕ) : ℝ) = (m:ℝ)+1-k := by
    rw [Nat.cast_sub (by omega), Nat.cast_add, Nat.cast_one]
  have ht : (0 : ℝ) ≤ 1-(k:ℝ)/m := by
    have := (div_le_one hmR).mpr hkR
    linarith
  have hbase : ((d+k : ℕ) : ℝ) ≤ (ℓ : ℝ) * ((m+1-k : ℕ) : ℝ) * (1-(k:ℝ)/m) := by
    rw [hcast]
    have he : (ℓ:ℝ) * ((m:ℝ)+1-k) * (1-(k:ℝ)/m) =
        (ℓ:ℝ) * ((m:ℝ)+1-k) * (m-k) / m := by field_simp
    rw [he]
    apply (le_div_iff₀ hmR).mpr
    have hn := mul_le_mul_of_nonneg_right hnum (le_of_lt hmR)
    have hs : (0:ℝ) ≤ (ℓ:ℝ) * ((k:ℝ)^2 + ((m:ℝ)-k)) :=
      mul_nonneg (Nat.cast_nonneg _) (add_nonneg (sq_nonneg _) (sub_nonneg.mpr hkR))
    norm_num only [Nat.cast_add] at *
    nlinarith
  have hp := pow_le_pow_left₀ (by positivity : (0:ℝ) ≤ ((d+k:ℕ):ℝ)) hbase k
  rw [mul_pow, mul_pow] at hp
  have hmain : (k.factorial : ℝ) * ((d+k).choose k : ℝ) ≤
      (k.factorial : ℝ) * ((m.choose k : ℝ) * (ℓ:ℝ)^k * (1-(k:ℝ)/m)^k) := by
    calc
      _ ≤ ((d+k:ℕ):ℝ)^k := htop
      _ ≤ _ := hp
      _ ≤ (ℓ:ℝ)^k * ((k.factorial : ℝ) * (m.choose k : ℝ)) * (1-(k:ℝ)/m)^k := by
        gcongr
      _ = _ := by ring
  exact (mul_le_mul_iff_right₀ hfact).mp hmain

theorem restriction_choose_exp_bound (m ℓ k d : ℕ) (hm : 0 < m) (hk : k ≤ m)
    (hnum : (d+k : ℝ) ≤ (ℓ : ℝ) * ((m : ℝ)-2*k)) :
    ((d+k).choose k : ℝ) ≤ (m.choose k : ℝ) * (ℓ:ℝ)^k * Real.exp (-((k:ℝ)^2)/m) := by
  have hmR : (0:ℝ) < m := by exact_mod_cast hm
  have hkR : (k:ℝ) ≤ m := by exact_mod_cast hk
  have ht : (0:ℝ) ≤ 1-(k:ℝ)/m := by
    have := (div_le_one hmR).mpr hkR
    linarith
  have hsmall : 1-(k:ℝ)/m ≤ Real.exp (-(k:ℝ)/m) := by
    simpa only [neg_div, sub_eq_add_neg, add_comm] using Real.add_one_le_exp (-(k:ℝ)/m)
  have hp := pow_le_pow_left₀ ht hsmall k
  have he : Real.exp (-(k:ℝ)/m)^k = Real.exp (-((k:ℝ)^2)/m) := by
    rw [← Real.exp_nat_mul]
    congr 1
    ring
  rw [he] at hp
  exact (choose_ratio_bound m ℓ k d hm hk hnum).trans
    (mul_le_mul_of_nonneg_left hp (by positivity))

def kernelDegree (m M : ℕ) : ℕ := Nat.ceil (Real.sqrt ((m:ℝ) * Real.log (4*M)))

theorem kernel_square_exp_bound (m M k : ℕ) (hm : 0 < m) (hM : 1 ≤ M)
    (hq : (m:ℝ) * Real.log (4*(M:ℝ)) ≤ (k:ℝ)^2) :
    (M:ℝ) * Real.exp (-((k:ℝ)^2)/m) ≤ 1/4 := by
  have hmR : (0:ℝ) < m := by exact_mod_cast hm
  have hMR : (1:ℝ) ≤ M := by exact_mod_cast hM
  have he : -((k : ℝ)^2)/m ≤ -Real.log (4*(M:ℝ)) := by
    apply (div_le_iff₀ hmR).mpr
    nlinarith
  have heq : Real.exp (-Real.log (4*(M:ℝ))) = (4*(M:ℝ))⁻¹ := by
    rw [Real.exp_neg, Real.exp_log (by nlinarith)]
  have hh := mul_le_mul_of_nonneg_left (Real.exp_le_exp.mpr he) (by positivity : (0:ℝ) ≤ M)
  rw [heq] at hh
  have hid : (M:ℝ) * (4*(M:ℝ))⁻¹ = 1/4 := by field_simp
  rwa [hid] at hh

theorem kernel_ceil_square (m M : ℕ) (hm : 0 < m) (hM : 1 ≤ M) :
    (m:ℝ) * Real.log (4*(M:ℝ)) ≤ (kernelDegree m M : ℝ)^2 := by
  have hmR : (0:ℝ) < m := by exact_mod_cast hm
  have hMR : (1:ℝ) ≤ M := by exact_mod_cast hM
  have hlog : 0 ≤ Real.log (4*(M:ℝ)) := Real.log_nonneg (by nlinarith)
  have hx : 0 ≤ (m:ℝ) * Real.log (4*(M:ℝ)) := mul_nonneg (le_of_lt hmR) hlog
  have hc : Real.sqrt ((m:ℝ)*Real.log (4*(M:ℝ))) ≤ (kernelDegree m M : ℝ) := Nat.le_ceil _
  have hs := Real.sq_sqrt hx
  nlinarith [Real.sqrt_nonneg ((m:ℝ)*Real.log (4*(M:ℝ)))]

theorem kernel_ceil_exp_bound (m M : ℕ) (hm : 0 < m) (hM : 1 ≤ M) :
    (M:ℝ) * Real.exp (-((kernelDegree m M : ℝ)^2)/m) ≤ 1/4 :=
  kernel_square_exp_bound m M _ hm hM (kernel_ceil_square m M hm hM)

theorem restriction_high_rank_bound (m ℓ k : ℕ) (hm : 0 < m) (hℓ : 1 ≤ ℓ) (hk : k ≤ m)
    (hr : 3*ℓ*(k+1)+1 ≤ m*ℓ) :
    (((m*ℓ-(3*ℓ*(k+1)+1)+k).choose k) : ℝ) ≤
      (m.choose k : ℝ) * (ℓ:ℝ)^k * Real.exp (-((k:ℝ)^2)/m) := by
  apply restriction_choose_exp_bound m ℓ k _ hm hk
  have hd := Nat.sub_add_cancel hr
  have hlk := Nat.mul_le_mul_right k hℓ
  have hn : m*ℓ-(3*ℓ*(k+1)+1)+k+2*ℓ*k ≤ m*ℓ := by nlinarith
  have hh : ((m*ℓ-(3*ℓ*(k+1)+1) : ℕ) : ℝ) + k + 2*ℓ*k ≤ (m:ℝ)*ℓ := by exact_mod_cast hn
  nlinarith

theorem kernelDegree_pos (m M : ℕ) (hm : 0 < m) (hM : 1 ≤ M) : 1 ≤ kernelDegree m M := by
  apply Nat.one_le_ceil_iff.mpr
  apply Real.sqrt_pos.mpr
  apply mul_pos (by exact_mod_cast hm)
  apply Real.log_pos
  have hh : (1:ℝ) ≤ M := by exact_mod_cast hM
  nlinarith

theorem kernel_dimension_bound_of_square (m ℓ M k : ℕ) (hm : 0 < m) (hℓ : 1 ≤ ℓ) (hM : 1 ≤ M)
    (hsq : (m:ℝ)*Real.log (4*(M:ℝ)) ≤ (k:ℝ)^2) (hk : k ≤ m) (hr : 3*ℓ*(k+1)+1 ≤ m*ℓ) :
    (M:ℝ) * ((m*ℓ-(3*ℓ*(k+1)+1)+k).choose k : ℝ) ≤
      ((m.choose k : ℝ)*(ℓ:ℝ)^k)/4 := by
  have hc := restriction_high_rank_bound m ℓ k hm hℓ hk hr
  have he : (M:ℝ)*Real.exp (-((k:ℝ)^2)/m) ≤ 1/4 := by
    exact kernel_square_exp_bound m M k hm hM hsq
  calc
    _ ≤ (M:ℝ) * ((m.choose k : ℝ)*(ℓ:ℝ)^k*Real.exp (-((k:ℝ)^2)/m)) :=
      mul_le_mul_of_nonneg_left hc (by positivity)
    _ = ((m.choose k : ℝ)*(ℓ:ℝ)^k) * ((M:ℝ)*Real.exp (-((k:ℝ)^2)/m)) := by ring
    _ ≤ ((m.choose k : ℝ)*(ℓ:ℝ)^k) * (1/4) := mul_le_mul_of_nonneg_left he (by positivity)
    _ = _ := by ring

theorem kernel_dimension_bound (m ℓ M k : ℕ) (hm : 0 < m) (hℓ : 1 ≤ ℓ) (hM : 1 ≤ M)
    (hkdef : k = kernelDegree m M) (hk : k ≤ m) (hr : 3*ℓ*(k+1)+1 ≤ m*ℓ) :
    (M:ℝ) * ((m*ℓ-(3*ℓ*(k+1)+1)+k).choose k : ℝ) ≤
      ((m.choose k : ℝ)*(ℓ:ℝ)^k)/4 := by
  apply kernel_dimension_bound_of_square m ℓ M k hm hℓ hM _ hk hr
  simpa [hkdef] using kernel_ceil_square m M hm hM

end
end MathResearch
