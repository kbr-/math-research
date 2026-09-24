/-
Claim: lem:binary-linear-form-avoidance
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-09-24-lean-linear-form-avoidance
Scope: Over F_2 with a finite variable type σ, a nonzero polynomial of total degree below 2^|σ| - 1 is not
divisible by some nonzero linear form Σ v_i x_i; and over any field, every nonzero linear form becomes any
chosen variable x_{i0} under an invertible linear substitution x_i ↦ Σ_j A_ij x_j. Helper for the
one-dimension step (lem:one-dimension-degree-step), where it is applied to the lowest homogeneous
component at the origin, of degree at most k - 1 < 2^n - 1.
Declarations: MathResearch.LinearFormAvoidance.linForm MathResearch.LinearFormAvoidance.coeff_linForm_single MathResearch.LinearFormAvoidance.linForm_injective MathResearch.LinearFormAvoidance.totalDegree_linForm MathResearch.LinearFormAvoidance.prime_linForm MathResearch.LinearFormAvoidance.units_subsingleton_zmod_two MathResearch.LinearFormAvoidance.exists_linForm_not_dvd MathResearch.LinearFormAvoidance.subst MathResearch.LinearFormAvoidance.subst_linForm MathResearch.LinearFormAvoidance.exists_subst_linForm_eq_X
-/
import Mathlib.RingTheory.MvPolynomial.IrreducibleQuadratic
import Mathlib.RingTheory.Polynomial.UniqueFactorization
import Mathlib.Algebra.MvPolynomial.Nilpotent
import Mathlib.Algebra.BigOperators.Associated
import Mathlib.LinearAlgebra.FiniteDimensional.Basic
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.LinearAlgebra.Determinant
import Mathlib.Algebra.Field.ZMod
import Mathlib.Data.Nat.Prime.Defs

namespace MathResearch.LinearFormAvoidance

open MvPolynomial

noncomputable section

variable {σ F : Type*} [Fintype σ] [Field F]

/-- The linear form `Σ v_i x_i`. -/
def linForm (v : σ → F) : MvPolynomial σ F := ∑ i, C (v i) * X i

theorem coeff_linForm_single [DecidableEq σ] (v : σ → F) (i : σ) :
    (linForm v).coeff (Finsupp.single i 1) = v i := by
  simp only [linForm, coeff_sum, coeff_C_mul, coeff_X, Finsupp.single_left_inj one_ne_zero]
  simp

theorem linForm_injective : Function.Injective (linForm : (σ → F) → MvPolynomial σ F) := by
  classical
  intro v w h
  funext i
  rw [← coeff_linForm_single v i, ← coeff_linForm_single w i, h]

theorem totalDegree_linForm {v : σ → F} (hv : v ≠ 0) : (linForm v).totalDegree = 1 := by
  classical
  apply le_antisymm
  · apply (totalDegree_finsetSum _ _).trans
    apply Finset.sup_le
    intro i _
    apply (totalDegree_mul _ _).trans
    simp [totalDegree_C, totalDegree_X]
  · obtain ⟨i, hi⟩ := Function.ne_iff.1 hv
    have hmem : Finsupp.single i 1 ∈ (linForm v).support := by
      rw [mem_support_iff, coeff_linForm_single]
      exact hi
    have := le_totalDegree hmem
    simpa using this

theorem prime_linForm {v : σ → F} (hv : v ≠ 0) : Prime (linForm v) := by
  classical
  apply UniqueFactorizationMonoid.irreducible_iff_prime.1
  apply irreducible_of_totalDegree_eq_one (totalDegree_linForm hv)
  intro x hx
  obtain ⟨i, hi⟩ := Function.ne_iff.1 hv
  have hxi := hx (Finsupp.single i 1)
  rw [coeff_linForm_single] at hxi
  have hx0 : x ≠ 0 := by
    rintro rfl
    exact hi (zero_dvd_iff.1 hxi)
  exact isUnit_iff_ne_zero.2 hx0

omit [Fintype σ] in
/-- The only unit of `𝔽₂[x_σ]` is `1`. -/
theorem units_subsingleton_zmod_two : Subsingleton (MvPolynomial σ (ZMod 2))ˣ := by
  constructor
  intro u w
  have key : ∀ u : (MvPolynomial σ (ZMod 2))ˣ, (u : MvPolynomial σ (ZMod 2)) = 1 := by
    intro u
    obtain ⟨r, hr, hru⟩ := (isUnit_iff_eq_C_of_isReduced).1 u.isUnit
    have : r = 1 := by
      have h0 : r ≠ 0 := hr.ne_zero
      fin_cases r
      · exact absurd rfl h0
      · rfl
    rw [hru, this, C_1]
  exact Units.ext ((key u).trans (key w).symm)

/-- Over `𝔽₂`, a nonzero polynomial of total degree below `2^|σ| - 1` is not divisible by some
nonzero linear form: the product of all `2^|σ| - 1` of them, pairwise non-associated primes, would
divide it. -/
theorem exists_linForm_not_dvd {P : MvPolynomial σ (ZMod 2)} (hP : P ≠ 0)
    (hdeg : P.totalDegree < 2 ^ Fintype.card σ - 1) :
    ∃ v : σ → ZMod 2, v ≠ 0 ∧ ¬ linForm v ∣ P := by
  classical
  by_contra h
  push Not at h
  have := units_subsingleton_zmod_two (σ := σ)
  set s := (Finset.univ.filter (fun v : σ → ZMod 2 => v ≠ 0)).image linForm
  have hprime : ∀ p ∈ s, Prime p := by
    intro p hp
    obtain ⟨v, hv, rfl⟩ := Finset.mem_image.1 hp
    exact prime_linForm (Finset.mem_filter.1 hv).2
  have hdvd : ∀ p ∈ s, p ∣ P := by
    intro p hp
    obtain ⟨v, hv, rfl⟩ := Finset.mem_image.1 hp
    exact h v (Finset.mem_filter.1 hv).2
  have hprod := Finset.prod_primes_dvd P hprime hdvd
  have hcard : s.card = 2 ^ Fintype.card σ - 1 := by
    rw [Finset.card_image_of_injective _ linForm_injective, Finset.filter_ne',
      Finset.card_erase_of_mem (Finset.mem_univ _), Finset.card_univ, Fintype.card_fun,
      ZMod.card]
  have hdegprod : (∏ p ∈ s, p).totalDegree = s.card := by
    have : ∀ t : Finset (MvPolynomial σ (ZMod 2)), t ⊆ s → (∏ p ∈ t, p).totalDegree = t.card := by
      intro t
      induction t using Finset.induction_on with
      | empty => intro _; simp
      | insert a t ha ih =>
        intro hts
        have has : a ∈ s := hts (Finset.mem_insert_self a t)
        have hts' : t ⊆ s := (Finset.subset_insert a t).trans hts
        rw [Finset.prod_insert ha, totalDegree_mul_of_isDomain (hprime a has).ne_zero
          (Finset.prod_ne_zero_iff.2 fun p hp => (hprime p (hts' hp)).ne_zero), ih hts',
          Finset.card_insert_of_notMem ha]
        obtain ⟨v, hv, rfl⟩ := Finset.mem_image.1 has
        rw [totalDegree_linForm (Finset.mem_filter.1 hv).2]
        ring
    exact this s le_rfl
  obtain ⟨c, hc⟩ := hprod
  have hc0 : c ≠ 0 := by
    rintro rfl
    exact hP (by rw [hc, mul_zero])
  have hle : (∏ p ∈ s, p).totalDegree ≤ P.totalDegree := by
    rw [hc, totalDegree_mul_of_isDomain
      (Finset.prod_ne_zero_iff.2 fun p hp => (hprime p hp).ne_zero) hc0]
    exact Nat.le_add_right _ _
  omega

/-- The linear substitution `x_i ↦ Σ_j A_ij x_j`. -/
def subst (A : Matrix σ σ F) : MvPolynomial σ F →ₐ[F] MvPolynomial σ F :=
  aeval fun i => linForm (A i)

theorem subst_linForm (A : Matrix σ σ F) (v : σ → F) :
    subst A (linForm v) = linForm (Matrix.vecMul v A) := by
  simp only [subst, linForm, map_sum, map_mul, aeval_C, aeval_X, algebraMap_eq, Finset.mul_sum,
    Matrix.vecMul, dotProduct, map_sum, Finset.sum_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro j _
  apply Finset.sum_congr rfl
  intro i _
  ring

/-- Every nonzero linear form becomes any chosen variable under an invertible substitution. -/
theorem exists_subst_linForm_eq_X [DecidableEq σ] {v : σ → F} (hv : v ≠ 0) (i0 : σ) :
    ∃ A : Matrix σ σ F, IsUnit A ∧ subst A (linForm v) = X i0 := by
  set e : σ → F := Pi.single i0 1
  have he : e ≠ 0 := by
    intro h
    have := congr_fun h i0
    simp [e] at this
  let f : (F ∙ v) ≃ₗ[F] (F ∙ e) :=
    (LinearEquiv.toSpanNonzeroSingleton F (σ → F) v hv).symm ≪≫ₗ
      LinearEquiv.toSpanNonzeroSingleton F (σ → F) e he
  obtain ⟨g, hg⟩ := Submodule.exists_linearEquiv_restrict_eq f
  have hgv : g v = e := by
    have := hg ⟨v, Submodule.mem_span_singleton_self v⟩
    rw [← this]
    simp only [f, LinearEquiv.trans_apply]
    rw [show (⟨v, Submodule.mem_span_singleton_self v⟩ : F ∙ v) =
      LinearEquiv.toSpanNonzeroSingleton F (σ → F) v hv 1 from
        (LinearEquiv.toSpanNonzeroSingleton_one F (σ → F) v hv).symm,
      LinearEquiv.symm_apply_apply, LinearEquiv.toSpanNonzeroSingleton_one]
  refine ⟨(LinearMap.toMatrix' g.toLinearMap).transpose, ?_, ?_⟩
  · rw [Matrix.isUnit_transpose, Matrix.isUnit_iff_isUnit_det, LinearMap.det_toMatrix']
    exact LinearEquiv.isUnit_det' g
  · rw [subst_linForm, Matrix.vecMul_transpose, LinearMap.toMatrix'_mulVec]
    simp only [LinearEquiv.coe_coe, hgv, linForm, e]
    rw [Finset.sum_eq_single i0]
    · simp
    · intro j _ hj
      simp [hj]
    · intro h
      exact absurd (Finset.mem_univ i0) h

end

end MathResearch.LinearFormAvoidance
