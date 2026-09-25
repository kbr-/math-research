/-
Claim: supporting module for thm:per-order-value-all-dimensions
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#binary-origin-jet-parametrization
Scope: Over F_2 in n variables, with y_i = x_i^2 + x_i: every P has an expansion
P = Σ_ε x^ε A_ε(y) (ε ranging over subsets of the variables, A_ε polynomials), and a nonzero
coefficient of y^e in A_ε forces |ε| + 2|e| ≤ totalDegree P. This is the direction of part (a) of
lem:binary-origin-jet-parametrization used by the per-order lower bound (uniqueness of the expansion is
not stated). Also an order toolkit at the origin: substitution of elements of positive order does not
lower the order, and the ideal of polynomials of order ≥ k.
Declarations: MathResearch.PerOrderExpansion.le_mult_zero_aeval MathResearch.PerOrderExpansion.lowIdeal MathResearch.PerOrderExpansion.homogeneousComponent_mul_of_le MathResearch.PerOrderExpansion.yv MathResearch.PerOrderExpansion.xmon MathResearch.PerOrderExpansion.exists_expansion MathResearch.PerOrderExpansion.weight_le_totalDegree
-/
import claims.OneDimensionStep
import claims.TruncatedProduct
import Mathlib.RingTheory.MvPolynomial.Homogeneous

namespace MathResearch.PerOrderExpansion

open MvPolynomial MathResearch.HasseMultiplicity MathResearch.TruncatedProduct
open MathResearch.OneDimensionStep

noncomputable section

variable {σ : Type*} [Fintype σ] [DecidableEq σ]

local notation "P2" => MvPolynomial σ (ZMod 2)

/-! ### Order at the origin -/

omit [Fintype σ] [DecidableEq σ] in
/-- Substituting elements of positive order does not lower the order at the origin. -/
theorem le_mult_zero_aeval (z : σ → P2) (hz : ∀ i, 1 ≤ mult 0 (z i)) (f : P2) :
    mult 0 f ≤ mult 0 (aeval z f) := by
  conv_rhs => rw [f.as_sum, map_sum]
  apply le_mult_sum
  intro e he
  rw [aeval_monomial]
  have hdeg : mult 0 f ≤ e.degree := by
    apply mult_le_degree
    rw [shift_zero]
    exact mem_support_iff.1 he
  refine hdeg.trans (le_trans ?_ (add_le_mult_mul 0 _ _))
  refine le_trans ?_ le_add_self
  refine le_trans ?_ (le_mult_prod 0 e.support _)
  rw [Finsupp.degree_apply, Nat.cast_sum]
  apply Finset.sum_le_sum
  intro i _
  calc ((e i : ℕ) : ℕ∞) = e i * 1 := by ring
    _ ≤ e i * mult 0 (z i) := by gcongr; exact hz i
    _ ≤ _ := le_mult_pow 0 _ _

/-- Polynomials of order at least `k` at the origin. -/
def lowIdeal (k : ℕ) : Ideal P2 where
  carrier := {f | (k : ℕ∞) ≤ mult 0 f}
  add_mem' := fun {a b} ha hb => le_trans (le_min ha hb) (min_le_mult_add 0 a b)
  zero_mem' := by simp
  smul_mem' := fun c f hf => le_trans (le_trans hf le_add_self) (add_le_mult_mul 0 c f)

omit [Fintype σ] [DecidableEq σ] in
theorem mem_lowIdeal {k : ℕ} {f : P2} : f ∈ lowIdeal k ↔ (k : ℕ∞) ≤ mult 0 f := Iff.rfl

/-! ### Homogeneous components of products -/

omit [Fintype σ] [DecidableEq σ] in
/-- The component of degree `a + b` of `f * g`, when `deg f ≤ a` and `deg g ≤ b`, is the product of
the components of degrees `a` and `b`. -/
theorem homogeneousComponent_mul_of_le {R : Type*} [CommRing R] {f g : MvPolynomial σ R} {a b : ℕ}
    (hf : f.totalDegree ≤ a) (hg : g.totalDegree ≤ b) :
    homogeneousComponent (a + b) (f * g) = homogeneousComponent a f * homogeneousComponent b g := by
  classical
  ext d
  rw [coeff_homogeneousComponent]
  split_ifs with hd
  · rw [coeff_mul, coeff_mul]
    apply Finset.sum_congr rfl
    intro uv huv
    rw [Finset.mem_antidiagonal] at huv
    have hsum : uv.1.degree + uv.2.degree = a + b := by
      rw [← hd, ← huv, map_add]
    rw [coeff_homogeneousComponent, coeff_homogeneousComponent]
    by_cases hu : uv.1.degree = a
    · have hv : uv.2.degree = b := by omega
      simp [hu, hv]
    · simp only [hu, ↓reduceIte, zero_mul]
      rcases lt_or_gt_of_ne hu with hlt | hgt
      · have hv : b < uv.2.degree := by omega
        rw [coeff_eq_zero_of_totalDegree_lt (lt_of_le_of_lt hg hv), mul_zero]
      · rw [coeff_eq_zero_of_totalDegree_lt (lt_of_le_of_lt hf hgt), zero_mul]
  · symm
    exact ((homogeneousComponent_isHomogeneous a f).mul
      (homogeneousComponent_isHomogeneous b g)).coeff_eq_zero hd

/-! ### The expansion in `x^ε y^e` -/

/-- `y_i = x_i² + x_i`. -/
def yv (i : σ) : P2 := X i ^ 2 + X i

/-- `x^ε = ∏_{i ∈ ε} x_i`. -/
def xmon (ε : Finset σ) : P2 := ∏ i ∈ ε, X i

/-- `P` is represented by the family `A`: `P = Σ_ε x^ε A_ε(y)`. -/
def Rep (P : P2) : Prop := ∃ A : Finset σ → P2, P = ∑ ε, xmon ε * aeval yv (A ε)

theorem rep_single (ε : Finset σ) (B : P2) : Rep (xmon ε * aeval yv B) := by
  refine ⟨fun ε' => if ε' = ε then B else 0, ?_⟩
  rw [Finset.sum_eq_single ε]
  · simp
  · intro b _ hb; simp [hb]
  · simp

omit [DecidableEq σ] in
theorem rep_add {P Q : P2} (hP : Rep P) (hQ : Rep Q) : Rep (P + Q) := by
  obtain ⟨A, rfl⟩ := hP
  obtain ⟨B, rfl⟩ := hQ
  refine ⟨A + B, ?_⟩
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro ε _
  simp [mul_add]

omit [DecidableEq σ] in
theorem rep_zero : Rep (0 : P2) := ⟨0, by simp⟩

omit [DecidableEq σ] in
theorem rep_sum {ι : Type*} (s : Finset ι) (f : ι → P2) (h : ∀ i ∈ s, Rep (f i)) :
    Rep (∑ i ∈ s, f i) := by
  classical
  induction s using Finset.induction_on with
  | empty => rw [Finset.sum_empty]; exact rep_zero
  | insert a s ha ih =>
    rw [Finset.sum_insert ha]
    exact rep_add (h a (Finset.mem_insert_self _ _))
      (ih fun i hi => h i (Finset.mem_insert_of_mem hi))

omit [Fintype σ] [DecidableEq σ] in
theorem two_eq_zero_P2 : (2 : P2) = 0 := by
  have := CharP.cast_eq_zero P2 2
  exact_mod_cast this

theorem rep_mul_X {P : P2} (hP : Rep P) (j : σ) : Rep (P * X j) := by
  obtain ⟨A, rfl⟩ := hP
  rw [Finset.sum_mul]
  apply rep_sum
  intro ε _
  by_cases hj : j ∈ ε
  · -- x^ε x_j = x^{ε \ j} x_j² = x^{ε \ j} (y_j + x_j)
    have hsplit : xmon ε = xmon (ε.erase j) * X j := by
      rw [xmon, xmon, ← Finset.prod_erase_mul _ _ hj]
    have hsq : (X j : P2) * X j = yv j + X j := by
      rw [yv, add_assoc, ← two_mul, two_eq_zero_P2, zero_mul, add_zero, sq]
    have : xmon ε * aeval yv (A ε) * X j =
        xmon (ε.erase j) * aeval yv (X j * A ε) + xmon ε * aeval yv (A ε) := by
      rw [map_mul, aeval_X, hsplit]
      linear_combination (xmon (ε.erase j) * aeval yv (A ε)) * hsq
    rw [this]
    exact rep_add (rep_single _ _) (rep_single _ _)
  · have : xmon ε * aeval yv (A ε) * X j = xmon (insert j ε) * aeval yv (A ε) := by
      rw [xmon, xmon, Finset.prod_insert hj]; ring
    rw [this]
    exact rep_single _ _

/-- **Existence of the expansion** `P = Σ_ε x^ε A_ε(y)`. -/
theorem exists_expansion (P : P2) : ∃ A : Finset σ → P2, P = ∑ ε, xmon ε * aeval yv (A ε) := by
  show Rep P
  induction P using MvPolynomial.induction_on with
  | C c =>
    have h := rep_single (∅ : Finset σ) (C c)
    simpa [xmon] using h
  | add p q hp hq => exact rep_add hp hq
  | mul_X p j hp => exact rep_mul_X hp j

/-! ### The degree of an expansion -/

omit [Fintype σ] [DecidableEq σ] in
theorem totalDegree_yv_le (i : σ) : (yv i : P2).totalDegree ≤ 2 := by
  unfold yv
  apply (totalDegree_add _ _).trans
  apply max_le
  · exact (totalDegree_pow _ _).trans (by simp [totalDegree_X])
  · simp [totalDegree_X]

omit [Fintype σ] [DecidableEq σ] in
theorem homogeneousComponent_two_yv (i : σ) : homogeneousComponent 2 (yv i : P2) = X i ^ 2 := by
  unfold yv
  rw [map_add, homogeneousComponent_eq_self (by simpa using (isHomogeneous_X (ZMod 2) i).pow 2),
    homogeneousComponent_eq_zero 2 (X i : P2) (by simp [totalDegree_X]), add_zero]

omit [Fintype σ] [DecidableEq σ] in
theorem yv_pow_top (i : σ) (b : ℕ) :
    (yv i ^ b : P2).totalDegree ≤ 2 * b ∧
      homogeneousComponent (2 * b) (yv i ^ b : P2) = X i ^ (2 * b) := by
  induction b with
  | zero => simp
  | succ b ih =>
    refine ⟨?_, ?_⟩
    · rw [pow_succ]
      apply (totalDegree_mul _ _).trans
      have := totalDegree_yv_le (σ := σ) i
      have := ih.1
      omega
    · rw [pow_succ, show 2 * (b + 1) = 2 * b + 2 by ring,
        homogeneousComponent_mul_of_le ih.1 (totalDegree_yv_le i), ih.2,
        homogeneousComponent_two_yv, ← pow_add]

/-- `y^e = ∏ y_i^{e_i}`. -/
def yvpow (e : σ →₀ ℕ) : P2 := aeval yv (monomial e 1)

omit [Fintype σ] [DecidableEq σ] in
theorem yvpow_top (e : σ →₀ ℕ) :
    (yvpow e : P2).totalDegree ≤ 2 * e.degree ∧
      homogeneousComponent (2 * e.degree) (yvpow e : P2) = monomial (2 • e) 1 := by
  induction e using Finsupp.induction with
  | zero => simp [yvpow]
  | single_add i b f hi hb ih =>
    have hy : (yvpow (Finsupp.single i b + f) : P2) = yv i ^ b * yvpow f := by
      rw [yvpow, yvpow, monomial_single_add, map_mul, map_pow, aeval_X]
    have hdeg : (Finsupp.single i b + f).degree = b + f.degree := by
      rw [map_add, Finsupp.degree_single]
    obtain ⟨h1, h2⟩ := yv_pow_top (σ := σ) i b
    refine ⟨?_, ?_⟩
    · rw [hy, hdeg]
      apply (totalDegree_mul _ _).trans
      have := ih.1
      omega
    · rw [hy, hdeg, show 2 * (b + f.degree) = 2 * b + 2 * f.degree by ring,
        homogeneousComponent_mul_of_le h1 ih.1, h2, ih.2, smul_add, Finsupp.smul_single,
        monomial_single_add, smul_eq_mul]

/-- The exponent vector of `x^ε`. -/
def indic (ε : Finset σ) : σ →₀ ℕ := ∑ i ∈ ε, Finsupp.single i 1

omit [Fintype σ] in
theorem indic_apply (ε : Finset σ) (i : σ) : indic ε i = if i ∈ ε then 1 else 0 := by
  simp [indic, Finsupp.finsetSum_apply, Finsupp.single_apply]

omit [Fintype σ] [DecidableEq σ] in
theorem degree_indic (ε : Finset σ) : (indic ε).degree = ε.card := by
  simp [indic, map_sum, Finsupp.degree_single]

omit [Fintype σ] [DecidableEq σ] in
theorem xmon_eq (ε : Finset σ) : (xmon ε : P2) = monomial (indic ε) 1 := by
  rw [xmon, indic, monomial_sum_one]
  apply Finset.prod_congr rfl
  intro i _
  rw [X]

omit [Fintype σ] in
theorem indic_add_injective {ε ε' : Finset σ} {e e' : σ →₀ ℕ}
    (h : indic ε + 2 • e = indic ε' + 2 • e') : ε = ε' ∧ e = e' := by
  have key : ∀ i, (i ∈ ε ↔ i ∈ ε') ∧ e i = e' i := by
    intro i
    have := congrArg (fun f => f i) h
    simp only [Finsupp.add_apply, Finsupp.smul_apply, smul_eq_mul, indic_apply] at this
    split_ifs at this with h1 h2 h2 <;> first | omega | exact ⟨by tauto, by omega⟩
  exact ⟨Finset.ext fun i => (key i).1, Finsupp.ext fun i => (key i).2⟩

omit [Fintype σ] [DecidableEq σ] in
theorem term_top (ε : Finset σ) (e : σ →₀ ℕ) :
    (xmon ε * yvpow e : P2).totalDegree ≤ ε.card + 2 * e.degree ∧
      homogeneousComponent (ε.card + 2 * e.degree) (xmon ε * yvpow e : P2) =
        monomial (indic ε + 2 • e) 1 := by
  classical
  have hx : (xmon ε : P2).totalDegree ≤ ε.card := by
    rw [xmon_eq]; exact (totalDegree_monomial_le _ _).trans (by rw [← degree_indic]; rfl)
  obtain ⟨h1, h2⟩ := yvpow_top (σ := σ) e
  refine ⟨(totalDegree_mul _ _).trans (by omega), ?_⟩
  rw [homogeneousComponent_mul_of_le hx h1, h2,
    homogeneousComponent_eq_self (by rw [xmon_eq]; exact isHomogeneous_monomial _ (degree_indic ε)),
    xmon_eq, monomial_mul_monomial, one_mul]

/-- **The degree of an expansion.** If `P = Σ_ε x^ε A_ε(y)`, every monomial `y^e` present in `A_ε`
has `|ε| + 2|e| ≤ deg P`. -/
theorem weight_le_totalDegree (P : P2) (A : Finset σ → P2)
    (hP : P = ∑ ε, xmon ε * aeval yv (A ε)) (ε : Finset σ) (e : σ →₀ ℕ)
    (he : (A ε).coeff e ≠ 0) : ε.card + 2 * e.degree ≤ P.totalDegree := by
  classical
  -- pairs (ε, e) with e in the support of A ε, and their weights
  set S : Finset (Σ _ : Finset σ, σ →₀ ℕ) := Finset.univ.sigma fun ε => (A ε).support
  set W : (Σ _ : Finset σ, σ →₀ ℕ) → ℕ := fun p => p.1.card + 2 * p.2.degree
  have hmem : (⟨ε, e⟩ : Σ _ : Finset σ, σ →₀ ℕ) ∈ S := by
    simp [S, mem_support_iff.2 he]
  obtain ⟨p0, hp0, hmax⟩ := S.exists_max_image W ⟨_, hmem⟩
  obtain ⟨ε0, e0⟩ := p0
  set μ0 : σ →₀ ℕ := indic ε0 + 2 • e0
  have hμ0 : μ0.degree = W ⟨ε0, e0⟩ := by
    simp only [μ0, W, map_add, map_nsmul, degree_indic, smul_eq_mul]
  -- expand P as a combination of the terms x^ε y^e
  have hmono : ∀ (e : σ →₀ ℕ) (c : ZMod 2), aeval yv (monomial e c : P2) = C c * yvpow e := by
    intro e c
    rw [yvpow, aeval_monomial, aeval_monomial, algebraMap_eq, map_one, one_mul]
  have hexp : P = ∑ ε, ∑ e ∈ (A ε).support, C ((A ε).coeff e) * (xmon ε * yvpow e) := by
    rw [hP]
    apply Finset.sum_congr rfl
    intro ε _
    conv_lhs => rw [(A ε).as_sum, map_sum, Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro e _
    rw [hmono]
    ring
  have hterm : ∀ ε e, (⟨ε, e⟩ : Σ _ : Finset σ, σ →₀ ℕ) ∈ S →
      (xmon ε * yvpow e : P2).coeff μ0 = if ε = ε0 ∧ e = e0 then 1 else 0 := by
    intro ε e hS
    obtain ⟨ht1, ht2⟩ := term_top (σ := σ) ε e
    have hW := hmax _ hS
    have hd0 : (∑ i ∈ μ0.support, μ0 i) = W ⟨ε0, e0⟩ := by rw [← Finsupp.degree_apply, hμ0]
    rcases lt_or_eq_of_le hW with hlt | heq
    · rw [coeff_eq_zero_of_totalDegree_lt (lt_of_le_of_lt ht1 (by rw [hd0]; exact hlt)),
        ite_eq_right]
      rintro ⟨rfl, rfl⟩
      exact lt_irrefl _ hlt
    · have hc := coeff_homogeneousComponent (ε.card + 2 * e.degree) (xmon ε * yvpow e : P2) μ0
      rw [ite_eq_left (by rw [hμ0]; exact heq.symm), ht2, coeff_monomial] at hc
      rw [← hc]
      by_cases hq : indic ε + 2 • e = μ0
      · obtain ⟨h1, h2⟩ := indic_add_injective hq
        rw [ite_eq_left hq, ite_eq_left ⟨h1, h2⟩]
      · rw [ite_eq_right hq, ite_eq_right]
        rintro ⟨rfl, rfl⟩
        exact hq rfl
  have hcoeff : P.coeff μ0 = (A ε0).coeff e0 := by
    rw [hexp, coeff_sum, Finset.sum_eq_single ε0]
    · rw [coeff_sum, Finset.sum_eq_single e0]
      · rw [coeff_C_mul, hterm _ _ hp0, ite_eq_left ⟨rfl, rfl⟩, mul_one]
      · intro b hb hne
        rw [coeff_C_mul, hterm _ _ (by simp [S, hb]), ite_eq_right (by tauto), mul_zero]
      · intro h0
        exact absurd (Finset.mem_sigma.1 hp0).2 h0
    · intro b _ hne
      rw [coeff_sum]
      apply Finset.sum_eq_zero
      intro c hc
      rw [coeff_C_mul, hterm _ _ (by simp [S, hc]), ite_eq_right (by tauto), mul_zero]
    · simp
  have hne : P.coeff μ0 ≠ 0 := by
    rw [hcoeff]; exact mem_support_iff.1 (Finset.mem_sigma.1 hp0).2
  have hle := le_totalDegree (mem_support_iff.2 hne)
  have : W ⟨ε, e⟩ ≤ W ⟨ε0, e0⟩ := hmax _ hmem
  rw [← hμ0] at this
  simp only [W] at this
  rw [Finsupp.degree_apply] at this
  exact this.trans hle

end

end MathResearch.PerOrderExpansion
