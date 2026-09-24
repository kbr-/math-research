/-
Claim: lem:one-dimension-degree-step
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#one-dimension-degree-step
Scope: Over F_2 with variables Option σ (σ finite, |Option σ| = n): if k < 2^n and P has Hasse
multiplicity ≥ k at every nonzero point and origin order < k, then some S in the variables σ has
multiplicity ≥ k at every nonzero point, the same origin order as P, and totalDegree S + 1 ≤ totalDegree P.
This is the order-preserving form (it also covers lem:per-order-dimension-step); the claim's statement
D(n-1,k) ≤ D(n,k) - 1 follows by taking P of least degree. Includes the invertible-substitution facts
(route item M08): homogeneous components commute with substitution, degree does not increase, origin
order is preserved, and mult_a(P ∘ A) = mult_{A a}(P).
Declarations: MathResearch.OneDimensionStep.subst_comp MathResearch.OneDimensionStep.homogeneousComponent_subst MathResearch.OneDimensionStep.totalDegree_subst_le MathResearch.OneDimensionStep.mult_zero_subst MathResearch.OneDimensionStep.mult_subst MathResearch.OneDimensionStep.mult_restrict MathResearch.OneDimensionStep.step_core MathResearch.OneDimensionStep.one_dimension_step
-/
import claims.LinearFormAvoidance
import «third-party-claims».MultiplicitySchwartzZippel
import Mathlib.RingTheory.MvPolynomial.Homogeneous
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse

namespace MathResearch.OneDimensionStep

open MvPolynomial MathResearch.HasseMultiplicity MathResearch.LinearFormAvoidance
open MathResearch.ThirdParty.MultiplicitySchwartzZippel

noncomputable section

/-! ### Multiplicity at the origin -/

section origin

variable {τ R : Type*} [CommRing R]

theorem shift_zero (f : MvPolynomial τ R) : shift 0 f = f := by
  have h : shift (0 : τ → R) = AlgHom.id R (MvPolynomial τ R) := by
    apply MvPolynomial.algHom_ext
    intro i
    simp
  rw [h]
  rfl

theorem mult_eq_mult_zero_shift (a : τ → R) (f : MvPolynomial τ R) :
    mult a f = mult 0 (shift a f) := by
  simp only [mult, shift_zero]

/-- `m ≤ mult₀ f` iff the homogeneous components of degree below `m` vanish. -/
theorem coe_le_mult_zero_iff (f : MvPolynomial τ R) (m : ℕ) :
    (m : ℕ∞) ≤ mult 0 f ↔ ∀ j < m, homogeneousComponent j f = 0 := by
  rw [coe_le_mult_iff, shift_zero]
  constructor
  · intro h j hj
    ext d
    rw [coeff_homogeneousComponent]
    split_ifs with hd
    · rw [h d (by rw [Finsupp.degree_eq_weight_one] at *; omega)]; simp
    · simp
  · intro h d hd
    have := congrArg (fun p : MvPolynomial τ R => p.coeff d) (h d.degree hd)
    simpa [coeff_homogeneousComponent, Finsupp.degree_eq_weight_one] using this

theorem mult_eq_of_forall {f g : MvPolynomial τ R}
    (h : ∀ m : ℕ, (m : ℕ∞) ≤ mult 0 f ↔ (m : ℕ∞) ≤ mult 0 g) : mult 0 f = mult 0 g := by
  apply le_antisymm
  · induction h' : mult 0 g using ENat.recTopCoe with
    | top => exact le_top
    | coe n =>
      by_contra hlt
      push Not at hlt
      have : ((n + 1 : ℕ) : ℕ∞) ≤ mult 0 f := by
        rw [Nat.cast_add, Nat.cast_one]; exact Order.add_one_le_of_lt hlt
      have := (h (n + 1)).1 this
      rw [h'] at this
      exact absurd this (by norm_cast; omega)
  · induction h' : mult 0 f using ENat.recTopCoe with
    | top => exact le_top
    | coe n =>
      by_contra hlt
      push Not at hlt
      have : ((n + 1 : ℕ) : ℕ∞) ≤ mult 0 g := by
        rw [Nat.cast_add, Nat.cast_one]; exact Order.add_one_le_of_lt hlt
      have := (h (n + 1)).2 this
      rw [h'] at this
      exact absurd this (by norm_cast; omega)

end origin

/-! ### Invertible linear substitutions (route item M08) -/

section subst

variable {τ F : Type*} [Fintype τ] [DecidableEq τ] [Field F]

omit [DecidableEq τ] in
theorem isHomogeneous_linForm (v : τ → F) : (linForm v).IsHomogeneous 1 := by
  apply IsHomogeneous.sum
  intro i _
  simpa using (isHomogeneous_C_mul_X (v i) i)

omit [DecidableEq τ] in
theorem subst_isHomogeneous (A : Matrix τ τ F) {f : MvPolynomial τ F} {d : ℕ}
    (hf : f.IsHomogeneous d) : (subst A f).IsHomogeneous d := by
  have := hf.aeval (fun i => linForm (A i)) (fun i => isHomogeneous_linForm (A i))
  simpa [subst] using this

omit [DecidableEq τ] in
theorem subst_comp (A B : Matrix τ τ F) (f : MvPolynomial τ F) :
    subst B (subst A f) = subst (A * B) f := by
  have h : (subst B).comp (subst A) = subst (A * B) := by
    apply MvPolynomial.algHom_ext
    intro i
    simp only [AlgHom.comp_apply]
    rw [show subst A (X i) = linForm (A i) by simp [subst], subst_linForm,
      show subst (A * B) (X i) = linForm ((A * B) i) by simp [subst]]
    congr 1
  exact AlgHom.congr_fun h f

theorem subst_one (f : MvPolynomial τ F) : subst (1 : Matrix τ τ F) f = f := by
  have h : subst (1 : Matrix τ τ F) = AlgHom.id F _ := by
    apply MvPolynomial.algHom_ext
    intro i
    simp only [subst, aeval_X, AlgHom.coe_id, id_eq, linForm, Matrix.one_apply]
    rw [Finset.sum_eq_single i]
    · simp
    · intro j _ hj; simp [Ne.symm hj]
    · simp
  rw [h]; rfl

theorem subst_injective {A : Matrix τ τ F} (hA : IsUnit A) : Function.Injective (subst A) := by
  intro f g h
  have hinv : A * A⁻¹ = 1 := Matrix.mul_nonsing_inv A ((Matrix.isUnit_iff_isUnit_det A).1 hA)
  rw [← subst_one f, ← subst_one g, ← hinv, ← subst_comp, ← subst_comp, h]

omit [DecidableEq τ] in
theorem homogeneousComponent_subst (A : Matrix τ τ F) (f : MvPolynomial τ F) (j : ℕ) :
    homogeneousComponent j (subst A f) = subst A (homogeneousComponent j f) := by
  classical
  conv_lhs => rw [← sum_homogeneousComponent f]
  rw [map_sum, map_sum]
  simp_rw [homogeneousComponent_of_mem (subst_isHomogeneous A (homogeneousComponent_isHomogeneous _ _))]
  rw [Finset.sum_ite_eq]
  split_ifs with hj
  · rfl
  · rw [homogeneousComponent_eq_zero, map_zero]
    simp only [Finset.mem_range, not_lt] at hj
    omega

omit [DecidableEq τ] in
theorem totalDegree_subst_le (A : Matrix τ τ F) (f : MvPolynomial τ F) :
    (subst A f).totalDegree ≤ f.totalDegree := by
  conv_lhs => rw [← sum_homogeneousComponent f]
  rw [map_sum]
  apply (totalDegree_finsetSum _ _).trans
  apply Finset.sup_le
  intro i hi
  exact ((subst_isHomogeneous A (homogeneousComponent_isHomogeneous i f)).totalDegree_le).trans
    (by simp at hi; omega)

theorem mult_zero_subst {A : Matrix τ τ F} (hA : IsUnit A) (f : MvPolynomial τ F) :
    mult 0 (subst A f) = mult 0 f := by
  apply mult_eq_of_forall
  intro m
  rw [coe_le_mult_zero_iff, coe_le_mult_zero_iff]
  constructor
  · intro h j hj
    apply subst_injective hA
    rw [← homogeneousComponent_subst, h j hj, map_zero]
  · intro h j hj
    rw [homogeneousComponent_subst, h j hj, map_zero]

omit [DecidableEq τ] in
theorem shift_subst (A : Matrix τ τ F) (a : τ → F) (f : MvPolynomial τ F) :
    shift a (subst A f) = subst A (shift (A.mulVec a) f) := by
  have h : (shift a).comp (subst A) = (subst A).comp (shift (A.mulVec a)) := by
    apply MvPolynomial.algHom_ext
    intro i
    simp only [AlgHom.comp_apply, shift_X, map_add]
    rw [show subst A (X i) = linForm (A i) by simp [subst]]
    simp only [linForm, map_sum, map_mul, shift_C, shift_X, subst, aeval_C, algebraMap_eq,
      Matrix.mulVec, dotProduct, map_sum, mul_add, Finset.sum_add_distrib]
  exact AlgHom.congr_fun h f

theorem mult_subst {A : Matrix τ τ F} (hA : IsUnit A) (a : τ → F) (f : MvPolynomial τ F) :
    mult a (subst A f) = mult (A.mulVec a) f := by
  rw [mult_eq_mult_zero_shift, shift_subst, mult_zero_subst hA, ← mult_eq_mult_zero_shift]

end subst

/-! ### The core step -/

section core

variable {σ : Type*} [Fintype σ] [DecidableEq σ]

local notation "P2" => MvPolynomial σ (ZMod 2)
local notation "Q2" => MvPolynomial (Option σ) (ZMod 2)

/-- Restriction `Q(x', c)`: the variable `none` set to `c`. -/
def restrict (c : ZMod 2) (Q : Q2) : P2 := Polynomial.eval (C c) (optionEquivLeft (ZMod 2) σ Q)

omit [Fintype σ] [DecidableEq σ] in
theorem coeff_restrict_zero (Q : Q2) (β : σ →₀ ℕ) :
    (restrict 0 Q).coeff β = Q.coeff (Finsupp.optionElim 0 β) := by
  rw [restrict, map_zero, ← Polynomial.coeff_zero_eq_eval_zero,
    ← optionEquivLeft_coeff_some_coeff_none (ZMod 2) σ (Finsupp.optionElim 0 β)]
  simp

omit [Fintype σ] [DecidableEq σ] in
theorem shift_restrict (c : ZMod 2) (a' : σ → ZMod 2) (Q : Q2) :
    shift a' (restrict c Q) = restrict 0 (shift (pt c a') Q) := by
  rw [restrict, restrict, optionEquivLeft_shift, map_zero, Polynomial.taylor_eval, zero_add,
    Polynomial.eval_map]
  have hc : (C c : P2) = (shift a').toRingHom (C c) := (shift_C a' c).symm
  conv_rhs => rw [hc]
  exact (Polynomial.eval₂_at_apply _ _).symm

omit [Fintype σ] [DecidableEq σ] in
theorem degree_optionElim_zero (β : σ →₀ ℕ) : (Finsupp.optionElim 0 β).degree = β.degree := by
  have hsplit : Finsupp.optionElim 0 β = β.embDomain .some := by
    ext o
    cases o with
    | none => simp
    | some x => simp [Finsupp.embDomain_some_some]
  rw [hsplit, Finsupp.embDomain_eq_mapDomain, Finsupp.degree_mapDomain]

omit [Fintype σ] [DecidableEq σ] in
/-- Restricting a variable never lowers multiplicity. -/
theorem mult_restrict (c : ZMod 2) (a' : σ → ZMod 2) (Q : Q2) :
    mult (pt c a') Q ≤ mult a' (restrict c Q) := by
  by_cases h : restrict c Q = 0
  · rw [h, mult_zero]; exact le_top
  obtain ⟨β, hβ, hdeg⟩ := exists_coeff_ne_zero_degree_eq_mult a' h
  rw [← hdeg]
  rw [shift_restrict, coeff_restrict_zero] at hβ
  have := mult_le_degree (pt c a') Q hβ
  rwa [degree_optionElim_zero] at this

omit [Fintype σ] [DecidableEq σ] in
theorem pt_zero_zero : pt (0 : ZMod 2) (0 : σ → ZMod 2) = 0 := by
  funext o; cases o <;> rfl

omit [Fintype σ] [DecidableEq σ] in
theorem pt_ne_zero_of_left (a' : σ → ZMod 2) : pt (1 : ZMod 2) a' ≠ 0 := by
  intro h
  have := congrFun h none
  simp [pt] at this

omit [Fintype σ] [DecidableEq σ] in
theorem pt_ne_zero_of_right (c : ZMod 2) {a' : σ → ZMod 2} (ha : a' ≠ 0) : pt c a' ≠ 0 := by
  intro h
  apply ha
  funext i
  exact congrFun h (some i)

omit [Fintype σ] [DecidableEq σ] in
/-- The step for a polynomial whose lowest component at the origin is not divisible by `x_none`. -/
theorem step_core (k : ℕ) (Q : Q2) (hQ : ∀ a : Option σ → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a Q)
    (h0 : mult 0 Q < k)
    (hL : ¬ (X none : Q2) ∣ homogeneousComponent (mult 0 Q).toNat Q) :
    ∃ S : P2, (∀ a : σ → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a S) ∧ mult 0 S = mult 0 Q ∧
      S.totalDegree + 1 ≤ Q.totalDegree := by
  set ℓ := (mult 0 Q).toNat with hℓdef
  have hℓ : (ℓ : ℕ∞) = mult 0 Q := ENat.natCast_toNat (ne_top_of_lt h0)
  have hℓk : ℓ < k := by
    have : (ℓ : ℕ∞) < k := hℓ ▸ h0
    exact_mod_cast this
  set S := restrict 0 Q + restrict 1 Q with hSdef
  -- restriction at `none = 1` vanishes to order `k` at the origin
  have h1 : (k : ℕ∞) ≤ mult 0 (restrict 1 Q) :=
    (hQ _ (pt_ne_zero_of_left 0)).trans (mult_restrict 1 0 Q)
  have h00 : mult 0 Q ≤ mult 0 (restrict 0 Q) := by
    have := mult_restrict 0 (0 : σ → ZMod 2) Q
    rwa [pt_zero_zero] at this
  -- multiplicity off the origin
  have hmult : ∀ a : σ → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a S := by
    intro a ha
    exact le_trans (le_min ((hQ _ (pt_ne_zero_of_right 0 ha)).trans (mult_restrict 0 a Q))
      ((hQ _ (pt_ne_zero_of_right 1 ha)).trans (mult_restrict 1 a Q))) (min_le_mult_add a _ _)
  -- a coefficient of degree ℓ survives in `S`
  set L := homogeneousComponent ℓ Q
  have hL0 : restrict 0 L ≠ 0 := by
    intro h
    apply hL
    have hc : (optionEquivLeft (ZMod 2) σ L).coeff 0 = 0 := by
      rw [Polynomial.coeff_zero_eq_eval_zero]
      have h' := h
      simp only [restrict, map_zero] at h'
      exact h'
    have hX := Polynomial.X_dvd_iff.2 hc
    have := map_dvd (optionEquivLeft (ZMod 2) σ).symm hX
    rwa [optionEquivLeft_symm_X, AlgEquiv.symm_apply_apply] at this
  obtain ⟨β, hβ⟩ := (MvPolynomial.ne_zero_iff).1 hL0
  rw [coeff_restrict_zero, coeff_homogeneousComponent] at hβ
  have hβdeg : (Finsupp.optionElim 0 β).degree = ℓ := by
    by_contra hne
    simp [hne] at hβ
  simp only [hβdeg, ↓reduceIte] at hβ
  have hβS : S.coeff β ≠ 0 := by
    rw [hSdef, AddMonoidAlgebra.coeff_add, Finsupp.add_apply, coeff_restrict_zero]
    have hz : (restrict 1 Q).coeff β = 0 := by
      have := (coe_le_mult_iff 0 (restrict 1 Q) k).1 h1 β
        (by rw [← degree_optionElim_zero, hβdeg]; exact hℓk)
      rwa [shift_zero] at this
    rw [hz, add_zero]
    exact hβ
  have hSle : mult 0 S ≤ ℓ := by
    have := mult_le_degree 0 S (d := β) (by rwa [shift_zero])
    rwa [← degree_optionElim_zero, hβdeg] at this
  have hSeq : mult 0 S = mult 0 Q := by
    apply le_antisymm
    · rw [← hℓ]; exact hSle
    · refine le_trans ?_ (min_le_mult_add 0 _ _)
      exact le_min h00 (le_trans h0.le h1)
  -- degree
  have hS0 : S ≠ 0 := by
    intro h
    rw [h, mult_zero] at hSeq
    exact absurd h0 (by rw [← hSeq]; exact not_lt.2 le_top)
  set Q' := optionEquivLeft (ZMod 2) σ Q
  have hNdeg : Q'.natDegree ≤ Q.totalDegree := by
    simp only [Q', natDegree_optionEquivLeft]
    exact degreeOf_le_totalDegree Q none
  have hSsum : S = ∑ i ∈ Finset.range (Q'.natDegree + 1),
      Q'.coeff i * C ((0 : ZMod 2) ^ i + 1 ^ i) := by
    rw [hSdef, restrict, restrict, Polynomial.eval_eq_sum_range, Polynomial.eval_eq_sum_range,
      ← Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro i _
    rw [C_add, C_pow, C_pow, mul_add]
  have hterm : ∀ i ∈ Finset.range (Q'.natDegree + 1),
      (Q'.coeff i * C ((0 : ZMod 2) ^ i + 1 ^ i)).totalDegree ≤ Q.totalDegree - 1 := by
    intro i hi
    rcases Nat.eq_zero_or_pos i with rfl | hipos
    · have : ((0 : ZMod 2) ^ 0 + 1 ^ 0) = 0 := by decide
      rw [this, C_0, mul_zero, totalDegree_zero]
      exact Nat.zero_le _
    · have hile : i ≤ Q.totalDegree := (Finset.mem_range_succ_iff.1 hi).trans hNdeg
      have := totalDegree_coeff_optionEquivLeft_add_le (ZMod 2) σ Q i hile
      change (Q'.coeff i).totalDegree + i ≤ _ at this
      apply (totalDegree_mul _ _).trans
      rw [totalDegree_C, add_zero]
      omega
  have hSdeg : S.totalDegree ≤ Q.totalDegree - 1 := by
    rw [hSsum]
    exact (totalDegree_finsetSum _ _).trans (Finset.sup_le hterm)
  have hQpos : 1 ≤ Q.totalDegree := by
    by_contra hQ0
    push Not at hQ0
    apply hS0
    have hN : Q'.natDegree = 0 := by omega
    rw [hSsum, hN, zero_add, Finset.sum_range_one, pow_zero, pow_zero,
      show ((1 : ZMod 2) + 1) = 0 by decide, C_0, mul_zero]
  exact ⟨S, hmult, hSeq, by omega⟩

end core

/-- **The one-dimension step.** Over `𝔽₂`, with `n = |σ| + 1` variables and `k < 2^n`, every
polynomial with multiplicity `≥ k` off the origin and origin order `< k` yields one in `n - 1`
variables with the same properties, the same origin order, and total degree at least one lower. -/
theorem one_dimension_step {σ : Type*} [Fintype σ] [DecidableEq σ] (k : ℕ)
    (hk : k < 2 ^ (Fintype.card σ + 1)) (P : MvPolynomial (Option σ) (ZMod 2))
    (hP : ∀ a : Option σ → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P) (h0 : mult 0 P < k) :
    ∃ S : MvPolynomial σ (ZMod 2), (∀ a : σ → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a S) ∧
      mult 0 S = mult 0 P ∧ S.totalDegree + 1 ≤ P.totalDegree := by
  classical
  have hPne : P ≠ 0 := by
    rintro rfl
    rw [mult_zero] at h0
    exact absurd h0 (not_lt.2 le_top)
  set ℓ := (mult 0 P).toNat
  have hℓ : (ℓ : ℕ∞) = mult 0 P := ENat.natCast_toNat (ne_top_of_lt h0)
  have hℓk : ℓ < k := by
    have : (ℓ : ℕ∞) < k := hℓ ▸ h0
    exact_mod_cast this
  set L := homogeneousComponent ℓ P
  have hL0 : L ≠ 0 := by
    obtain ⟨β, hβ, hdeg⟩ := exists_coeff_ne_zero_degree_eq_mult 0 hPne
    rw [shift_zero] at hβ
    intro h
    have := congrArg (fun p : MvPolynomial (Option σ) (ZMod 2) => p.coeff β) h
    have hdβ : β.degree = ℓ := by exact_mod_cast (hdeg.trans hℓ.symm)
    simp only [L, coeff_homogeneousComponent, hdβ, ↓reduceIte] at this
    exact hβ (by simpa using this)
  have hLdeg : L.totalDegree < 2 ^ Fintype.card (Option σ) - 1 := by
    have : L.totalDegree ≤ ℓ := (homogeneousComponent_isHomogeneous ℓ P).totalDegree_le
    rw [Fintype.card_option]
    have h2 : 1 ≤ 2 ^ (Fintype.card σ + 1) := Nat.one_le_two_pow
    omega
  obtain ⟨v, hv, hnd⟩ := exists_linForm_not_dvd hL0 hLdeg
  obtain ⟨A, hA, hAv⟩ := exists_subst_linForm_eq_X hv none
  have hdet : IsUnit A.det := (Matrix.isUnit_iff_isUnit_det A).1 hA
  set Q := subst A P
  have hQ : ∀ a : Option σ → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a Q := by
    intro a ha
    rw [mult_subst hA]
    apply hP
    intro h
    apply ha
    calc a = A⁻¹.mulVec (A.mulVec a) := by
          rw [Matrix.mulVec_mulVec, Matrix.nonsing_inv_mul A hdet, Matrix.one_mulVec]
      _ = 0 := by rw [h, Matrix.mulVec_zero]
  have h0Q : mult 0 Q = mult 0 P := mult_zero_subst hA P
  have hLQ : ¬ (X none : MvPolynomial (Option σ) (ZMod 2)) ∣
      homogeneousComponent (mult 0 Q).toNat Q := by
    rw [h0Q, homogeneousComponent_subst]
    intro hdvd
    apply hnd
    have := map_dvd (subst A⁻¹) hdvd
    rwa [← hAv, subst_comp, subst_comp, Matrix.mul_nonsing_inv A hdet, subst_one, subst_one]
      at this
  obtain ⟨S, hS1, hS2, hS3⟩ := step_core k Q hQ (h0Q ▸ h0) hLQ
  exact ⟨S, hS1, hS2.trans h0Q, hS3.trans (totalDegree_subst_le A P)⟩

end

end MathResearch.OneDimensionStep
