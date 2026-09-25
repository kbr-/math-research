/-
Claim: lem:admissible-expansion-congruence (a variant of lem:y-coefficient-degree-formula)
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#y-coefficient-degree-formula
Scope: Over F_2 in n variables, fix K and put xhat(Y) = Σ_{s<K} Y^(2^s) (the truncated root of
X² + X = Y), with 2^K ≥ k. If P has Hasse multiplicity ≥ k at every nonzero point of F_2^n and
P = Σ_ε x^ε A_ε(y) with y_i = x_i² + x_i, then with w = P(xhat(y_1), …, xhat(y_n)),
A_ε ≡ w · ∏_{i ∉ ε} (1 + xhat(y_i)) modulo polynomials of order ≥ k at the origin; in particular the
coefficients of y^e, |e| < k, agree. The notebook states this for the jet polynomial P(v) of the
origin-jet lemma; here it is proved directly for P and any expansion, which is what the lower bound uses.
Declarations: MathResearch.PerOrderYCoefficient.xhat MathResearch.PerOrderYCoefficient.xhat_sq_add MathResearch.PerOrderYCoefficient.one_le_mult_xhat MathResearch.PerOrderYCoefficient.expansion_congr MathResearch.PerOrderYCoefficient.coeff_expansion
-/
import claims.PerOrderExpansion

namespace MathResearch.PerOrderYCoefficient

open MvPolynomial MathResearch.HasseMultiplicity MathResearch.TruncatedProduct
open MathResearch.OneDimensionStep MathResearch.PerOrderExpansion

noncomputable section

variable {σ : Type*} [Fintype σ] [DecidableEq σ]

local notation "P2" => MvPolynomial σ (ZMod 2)

/-- The truncated root `xhat(Y) = Σ_{s<K} Y^(2^s)` of `X² + X = Y`. -/
def xhat (K : ℕ) (Y : P2) : P2 := ∑ s ∈ Finset.range K, Y ^ (2 ^ s)

omit [Fintype σ] [DecidableEq σ] in
theorem telescope_two_pow (K : ℕ) (Y : P2) :
    ∑ s ∈ Finset.range K, Y ^ (2 ^ (s + 1)) + ∑ s ∈ Finset.range K, Y ^ (2 ^ s) = Y + Y ^ (2 ^ K) := by
  induction K with
  | zero => simp only [Finset.range_zero, Finset.sum_empty, add_zero, pow_zero, pow_one]
            linear_combination (-Y) * two_eq_zero_P2
  | succ K ih =>
    rw [Finset.sum_range_succ, Finset.sum_range_succ]
    linear_combination ih + Y ^ (2 ^ K) * two_eq_zero_P2

omit [Fintype σ] [DecidableEq σ] in
theorem xhat_sq_add (K : ℕ) (Y : P2) : xhat K Y ^ 2 + xhat K Y = Y + Y ^ (2 ^ K) := by
  unfold xhat
  have hsq : (∑ s ∈ Finset.range K, Y ^ (2 ^ s)) ^ 2 = ∑ s ∈ Finset.range K, Y ^ (2 ^ (s + 1)) := by
    rw [sum_pow_char]
    apply Finset.sum_congr rfl
    intro s _
    rw [← pow_mul, pow_succ]
  rw [hsq, telescope_two_pow]

omit [Fintype σ] [DecidableEq σ] in
theorem one_le_mult_xhat (K : ℕ) (i : σ) : 1 ≤ mult 0 (xhat K (X i : P2)) := by
  rw [one_le_mult_iff, xhat, map_sum]
  apply Finset.sum_eq_zero
  intro s _
  simp

omit [Fintype σ] [DecidableEq σ] in
/-- `(u + c)² + (u + c) = u² + u` for `c ∈ 𝔽₂`. -/
theorem sq_add_const (u : P2) (c : ZMod 2) : (u + C c) ^ 2 + (u + C c) = u ^ 2 + u := by
  have hc : C c ^ 2 + C c = (0 : P2) := by
    have h2 : ∀ c : ZMod 2, c ^ 2 + c = 0 := by decide
    rw [← map_pow, ← map_add, h2 c, map_zero]
  linear_combination (u * C c) * two_eq_zero_P2 + hc

/-- The substitution `x_i ↦ xhat(y_i) + δ_i`. -/
def zs (K : ℕ) (δ : σ → ZMod 2) (i : σ) : P2 := xhat K (X i) + C (δ i)

/-- `yhat_i = y_i + y_i^(2^K)`, the image of `x_i² + x_i`. -/
def yh (K : ℕ) (i : σ) : P2 := X i + X i ^ (2 ^ K)

omit [Fintype σ] [DecidableEq σ] in
theorem aeval_zs_yv (K : ℕ) (δ : σ → ZMod 2) (i : σ) : aeval (zs K δ) (yv i : P2) = yh K i := by
  simp only [yv, map_add, map_pow, aeval_X, zs, yh]
  rw [sq_add_const, xhat_sq_add]

omit [DecidableEq σ] in
theorem aeval_zs_expansion (K : ℕ) (δ : σ → ZMod 2) (P : P2) (A : Finset σ → P2)
    (hA : P = ∑ ε, xmon ε * aeval yv (A ε)) :
    aeval (zs K δ) P = ∑ ε, (∏ i ∈ ε, zs K δ i) * aeval (yh K) (A ε) := by
  conv_lhs => rw [hA]
  rw [map_sum]
  apply Finset.sum_congr rfl
  intro ε _
  rw [map_mul, xmon, map_prod]
  congr 1
  · simp
  · rw [← AlgHom.comp_apply, comp_aeval]
    refine congrArg (fun f : σ → P2 => aeval f (A ε)) ?_
    funext i
    exact aeval_zs_yv K δ i

omit [Fintype σ] [DecidableEq σ] in
theorem aeval_zs_mem {k : ℕ} (K : ℕ) (δ : σ → ZMod 2) (P : P2) (hk : (k : ℕ∞) ≤ mult δ P) :
    aeval (zs K δ) P ∈ lowIdeal k := by
  have hcomp : aeval (zs K δ) P = aeval (fun i => xhat K (X i)) (shift δ P) := by
    rw [shift, ← AlgHom.comp_apply, comp_aeval]
    refine congrArg (fun f : σ → P2 => aeval f P) ?_
    funext i
    simp [zs]
  rw [hcomp, mem_lowIdeal]
  refine le_trans ?_ (le_mult_zero_aeval _ (fun i => one_le_mult_xhat K i) _)
  rw [← mult_eq_mult_zero_shift]
  exact hk

/-- The per-variable inversion matrix. -/
def Nm (K : ℕ) (ε : Finset σ) (i : σ) (c : ZMod 2) : P2 :=
  if i ∈ ε then 1 else if c = 0 then 1 + xhat K (X i) else xhat K (X i)

omit [Fintype σ] in
theorem cell (K : ℕ) (ε ε' : Finset σ) (i : σ) :
    (∑ c : ZMod 2, Nm K ε i c * if i ∈ ε' then xhat K (X i) + C c else 1) =
      if (i ∈ ε ↔ i ∈ ε') then 1 else 0 := by
  have huniv : (Finset.univ : Finset (ZMod 2)) = {0, 1} := rfl
  rw [huniv, Finset.sum_pair zero_ne_one]
  have h10 : (1 : ZMod 2) = 0 ↔ False := by decide
  set u := xhat K (X i : P2)
  by_cases h1 : i ∈ ε <;> by_cases h2 : i ∈ ε' <;>
    simp only [Nm, h1, h2, h10, ↓reduceIte, iff_true, iff_false, not_true_eq_false, map_zero, map_one,
      add_zero, mul_one, one_mul]
  · linear_combination u * two_eq_zero_P2
  · linear_combination two_eq_zero_P2
  · linear_combination (u + u ^ 2) * two_eq_zero_P2
  · linear_combination u * two_eq_zero_P2

theorem inversion (K : ℕ) (ε ε' : Finset σ) :
    (∑ δ : σ → ZMod 2, (∏ i, Nm K ε i (δ i)) * ∏ i ∈ ε', zs K δ i) = if ε' = ε then 1 else 0 := by
  have hstep : ∀ δ : σ → ZMod 2, (∏ i, Nm K ε i (δ i)) * ∏ i ∈ ε', zs K δ i =
      ∏ i, (Nm K ε i (δ i) * if i ∈ ε' then xhat K (X i) + C (δ i) else 1) := by
    intro δ
    rw [Finset.prod_mul_distrib]
    congr 1
    rw [← Fintype.prod_ite_mem]
    rfl
  simp_rw [hstep]
  rw [← Fintype.prod_sum (fun i c => Nm K ε i c * if i ∈ ε' then xhat K (X i) + C c else 1)]
  simp_rw [cell]
  by_cases he : ε' = ε
  · subst he
    simp
  · rw [ite_eq_right he]
    obtain ⟨i, hi⟩ : ∃ i, ¬(i ∈ ε ↔ i ∈ ε') := by
      by_contra hall
      push Not at hall
      exact he (Finset.ext fun i => (hall i).symm)
    exact Finset.prod_eq_zero (Finset.mem_univ i) (by rw [ite_eq_right hi])

omit [Fintype σ] [DecidableEq σ] in
theorem mk_aeval_yh {k K : ℕ} (hK : k ≤ 2 ^ K) (f : P2) :
    Ideal.Quotient.mk (lowIdeal k) (aeval (yh K) f) = Ideal.Quotient.mk (lowIdeal k) f := by
  rw [← Ideal.Quotient.mkₐ_eq_mk (ZMod 2), ← AlgHom.comp_apply, comp_aeval]
  conv_rhs => rw [← aeval_X_left_apply f, ← AlgHom.comp_apply, comp_aeval]
  refine congrArg (fun g => aeval g f) ?_
  funext i
  simp only [Ideal.Quotient.mkₐ_eq_mk, yh]
  rw [Ideal.Quotient.eq, add_sub_cancel_left, mem_lowIdeal]
  calc (k : ℕ∞) ≤ ((2 ^ K : ℕ) : ℕ∞) := by exact_mod_cast hK
    _ = (2 ^ K : ℕ) * 1 := by ring
    _ ≤ (2 ^ K : ℕ) * mult 0 (X i : P2) := by
        gcongr; rw [one_le_mult_iff]; simp
    _ ≤ _ := le_mult_pow 0 _ _

/-- **The expansion modulo order `k`.** For `P` of multiplicity `≥ k` at every nonzero point, with
`2^K ≥ k` and any expansion `P = Σ_ε x^ε A_ε(y)`, `A_ε ≡ w ∏_{i ∉ ε} (1 + xhat(y_i))` modulo order `k`,
where `w = P(xhat(y))`. -/
theorem expansion_congr {k K : ℕ} (hK : k ≤ 2 ^ K) (P : P2)
    (hP : ∀ a : σ → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P)
    (A : Finset σ → P2) (hA : P = ∑ ε, xmon ε * aeval yv (A ε)) (ε : Finset σ) :
    Ideal.Quotient.mk (lowIdeal k) (A ε) =
      Ideal.Quotient.mk (lowIdeal k)
        (aeval (fun i => xhat K (X i)) P * ∏ i ∈ Finset.univ.filter (· ∉ ε), (1 + xhat K (X i))) := by
  have hmain : aeval (yh K) (A ε) = ∑ δ : σ → ZMod 2, (∏ i, Nm K ε i (δ i)) * aeval (zs K δ) P := by
    calc aeval (yh K) (A ε) = ∑ ε', (if ε' = ε then 1 else 0) * aeval (yh K) (A ε') := by
          simp
      _ = ∑ ε', (∑ δ : σ → ZMod 2, (∏ i, Nm K ε i (δ i)) * ∏ i ∈ ε', zs K δ i) *
            aeval (yh K) (A ε') := by
          simp_rw [inversion]
      _ = ∑ δ : σ → ZMod 2, (∏ i, Nm K ε i (δ i)) *
            ∑ ε', (∏ i ∈ ε', zs K δ i) * aeval (yh K) (A ε') := by
          simp_rw [Finset.sum_mul, Finset.mul_sum]
          rw [Finset.sum_comm]
          simp_rw [mul_assoc]
      _ = _ := by simp_rw [aeval_zs_expansion K _ P A hA]
  rw [← mk_aeval_yh hK, hmain, map_sum, Finset.sum_eq_single (0 : σ → ZMod 2)]
  · have hz0 : zs K (0 : σ → ZMod 2) = fun i => xhat K (X i) := by funext i; simp [zs]
    rw [hz0, mul_comm, Finset.prod_filter]
    congr 2
    apply Finset.prod_congr rfl
    intro i _
    by_cases hi : i ∈ ε <;> simp [Nm, hi]
  · intro δ _ hδ
    rw [map_mul, (Ideal.Quotient.eq_zero_iff_mem).2 (aeval_zs_mem K δ P (hP δ hδ)), mul_zero]
  · simp

/-- The coefficient form: for `|e| < k`, the coefficient of `y^e` in `A_ε` is that of
`w ∏_{i ∉ ε} (1 + xhat(y_i))`. -/
theorem coeff_expansion {k K : ℕ} (hK : k ≤ 2 ^ K) (P : P2)
    (hP : ∀ a : σ → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P)
    (A : Finset σ → P2) (hA : P = ∑ ε, xmon ε * aeval yv (A ε)) (ε : Finset σ)
    (e : σ →₀ ℕ) (he : e.degree < k) :
    (A ε).coeff e =
      (aeval (fun i => xhat K (X i)) P *
        ∏ i ∈ Finset.univ.filter (· ∉ ε), (1 + xhat K (X i))).coeff e := by
  have h := expansion_congr hK P hP A hA ε
  rw [Ideal.Quotient.eq, mem_lowIdeal, coe_le_mult_iff, shift_zero] at h
  have := h e he
  rw [coeff_sub, sub_eq_zero] at this
  exact this

end

end MathResearch.PerOrderYCoefficient
