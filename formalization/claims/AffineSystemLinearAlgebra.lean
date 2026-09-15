/-
Claim: lem:affine-system-linear-algebra
Source: https://kbr.is-a.dev/math-research/#lean-affine-system-linear-algebra
Scope: Finite affine coefficient systems: proper-span consistency, zero-flat vanishing witnesses, unit certificates, and independent linear parts. Polynomial/AffineMap bridges retain ordinary semantics.
Declarations: MathResearch.affine_proper_common_zero MathResearch.affine_vanishing_mem_span MathResearch.affine_vanishing_coefficients MathResearch.affine_inconsistent_unit_coefficients MathResearch.affineLinearPart_injOn_proper MathResearch.affine_independent_linearParts MathResearch.affine_proper_linearPart_finrank MathResearch.affine_proper_nonzero_degree_one
-/
import Mathlib.LinearAlgebra.Dual.Lemmas
import claims.AffineForm

namespace MathResearch
noncomputable section
open scoped BigOperators
variable {K : Type*} [Field K] {n : ℕ}

private theorem dual_affine_expansion (L : AffineForm K n →ₗ[K] K) (a : AffineForm K n) :
    L a = a none * L (affineUnit none) + ∑ i, a (some i) * L (affineUnit (some i)) := by
  rw [LinearMap.pi_apply_eq_sum_univ]
  simp only [Fintype.sum_option, smul_eq_mul]
  rfl

private theorem affineValue_dual_normalize (L : AffineForm K n →ₗ[K] K)
    (ht : L (affineUnit none) ≠ 0) (a : AffineForm K n) :
    affineValue a (fun i => L (affineUnit (some i)) / L (affineUnit none)) =
      L a / L (affineUnit none) := by
  rw [dual_affine_expansion L a]
  simp only [affineValue, div_eq_mul_inv, add_mul, Finset.sum_mul, mul_assoc,
    mul_inv_cancel₀ ht, mul_one]


private theorem affineValue_dual_shift (L : AffineForm K n →ₗ[K] K)
    (x : Fin n → K) (a : AffineForm K n) :
    affineValue a (fun i => L (affineUnit (some i)) +
      (1 - L (affineUnit none)) * x i) =
    L a + (1 - L (affineUnit none)) * affineValue a x := by
  rw [dual_affine_expansion L a]
  simp only [affineValue, mul_add, Finset.sum_add_distrib]
  rw [show (∑ i, a (some i) * ((1 - L (affineUnit none)) * x i)) =
    (1 - L (affineUnit none)) * ∑ i, a (some i) * x i by
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro i _
      ring]
  ring

theorem affine_proper_common_zero (S : Submodule K (AffineForm K n))
    (hS : affineUnit none ∉ S) :
    ∃ x : Fin n → K, ∀ a ∈ S, affineValue a x = 0 := by
  have hnot : ¬ ∀ L : Module.Dual K (AffineForm K n),
      L ∈ S.dualAnnihilator → L (affineUnit none) = 0 := by
    intro h
    exact hS ((Subspace.forall_mem_dualAnnihilator_apply_eq_zero_iff S _).mp h)
  push Not at hnot
  obtain ⟨L, hL, ht⟩ := hnot
  refine ⟨fun i => L (affineUnit (some i)) / L (affineUnit none), ?_⟩
  intro a ha
  rw [affineValue_dual_normalize L ht]
  rw [((S.mem_dualAnnihilator L).mp hL) a ha, zero_div]

theorem affine_vanishing_mem_span (S : Submodule K (AffineForm K n))
    (x : Fin n → K) (hx : ∀ a ∈ S, affineValue a x = 0)
    (f : AffineForm K n)
    (hf : ∀ y : Fin n → K, (∀ a ∈ S, affineValue a y = 0) → affineValue f y = 0) :
    f ∈ S := by
  apply (Subspace.forall_mem_dualAnnihilator_apply_eq_zero_iff S f).mp
  intro L hL
  have hy : ∀ a ∈ S, affineValue a (fun i => L (affineUnit (some i)) +
      (1 - L (affineUnit none)) * x i) = 0 := by
    intro a ha
    rw [affineValue_dual_shift, ((S.mem_dualAnnihilator L).mp hL) a ha, hx a ha]
    simp
  have hh := hf _ hy
  rw [affineValue_dual_shift, hf x hx] at hh
  simpa using hh

private theorem affine_span_zero {ι : Type*} (g : ι → AffineForm K n)
    (x : Fin n → K) (hx : ∀ i, affineValue (g i) x = 0) :
    ∀ a ∈ Submodule.span K (Set.range g), affineValue a x = 0 := by
  have hle : Submodule.span K (Set.range g) ≤ (affineEvaluation x).ker := by
    apply Submodule.span_le.mpr
    rintro _ ⟨i, rfl⟩
    exact hx i
  exact fun a ha => hle ha

theorem affine_vanishing_coefficients {ι : Type*} [Fintype ι]
    (g : ι → AffineForm K n) (x : Fin n → K)
    (hx : ∀ i, affineValue (g i) x = 0) (f : AffineForm K n)
    (hf : ∀ y, (∀ i, affineValue (g i) y = 0) → affineValue f y = 0) :
    ∃ c : ι → K, f = ∑ i, c i • g i := by
  have hm := affine_vanishing_mem_span (Submodule.span K (Set.range g)) x
    (affine_span_zero g x hx) f (by
      intro y hy
      exact hf y (fun i => hy _ (Submodule.subset_span ⟨i, rfl⟩)))
  obtain ⟨c, hc⟩ := (Submodule.mem_span_range_iff_exists_fun K).mp hm
  exact ⟨c, hc.symm⟩

theorem affine_inconsistent_unit_coefficients {ι : Type*} [Fintype ι]
    (g : ι → AffineForm K n)
    (h : ¬ ∃ x, ∀ i, affineValue (g i) x = 0) :
    ∃ c : ι → K, affineUnit none = ∑ i, c i • g i := by
  have hm : affineUnit none ∈ Submodule.span K (Set.range g) := by
    by_contra hn
    obtain ⟨x, hx⟩ := affine_proper_common_zero _ hn
    exact h ⟨x, fun i => hx _ (Submodule.subset_span ⟨i, rfl⟩)⟩
  obtain ⟨c, hc⟩ := (Submodule.mem_span_range_iff_exists_fun K).mp hm
  exact ⟨c, hc.symm⟩

theorem affineLinearPart_injOn_proper (S : Submodule K (AffineForm K n))
    (hS : affineUnit none ∉ S) : Set.InjOn affineLinearPart (S : Set (AffineForm K n)) := by
  obtain ⟨x, hx⟩ := affine_proper_common_zero S hS
  intro a ha b hb hab
  have hlin : ∀ i, a (some i) = b (some i) := fun i => congrFun hab i
  have hconst : a none = b none := by
    have hA := hx a ha
    have hB := hx b hb
    simp only [affineValue, hlin] at hA hB
    exact add_right_cancel (hA.trans hB.symm)
  funext i
  cases i with
  | none => exact hconst
  | some i => exact hlin i

theorem affine_independent_linearParts {ι : Type*} (g : ι → AffineForm K n)
    (hg : LinearIndependent K g)
    (hproper : affineUnit none ∉ Submodule.span K (Set.range g)) :
    LinearIndependent K (fun i => affineLinearPart (g i)) := by
  exact hg.map_injOn affineLinearPart (affineLinearPart_injOn_proper _ hproper)

theorem affine_proper_linearPart_finrank (S : Submodule K (AffineForm K n))
    (hS : affineUnit none ∉ S) :
    Module.finrank K (S.map affineLinearPart) = Module.finrank K S := by
  have hi : Function.Injective (affineLinearPart.comp S.subtype) := by
    intro a b h
    apply Subtype.ext
    exact affineLinearPart_injOn_proper S hS a.property b.property h
  have he : (affineLinearPart.comp S.subtype).range = S.map affineLinearPart := by
    ext p
    constructor
    · rintro ⟨a, rfl⟩
      exact ⟨a.val, a.property, rfl⟩
    · rintro ⟨a, ha, rfl⟩
      exact ⟨⟨a, ha⟩, rfl⟩
  rw [← he]
  exact LinearMap.finrank_range_of_inj hi

theorem affine_proper_nonzero_degree_one (S : Submodule K (AffineForm K n))
    (hS : affineUnit none ∉ S) (a : AffineForm K n) (ha : a ∈ S) (hne : a ≠ 0) :
    (affinePolynomial a).totalDegree = 1 := by
  have hd := affinePolynomial_degree a
  have hz : (affinePolynomial a).totalDegree ≠ 0 := by
    intro hz
    have hc := MvPolynomial.totalDegree_eq_zero_iff_eq_C.mp hz
    obtain ⟨x, hx⟩ := affine_proper_common_zero S hS
    have hev := congrArg (MvPolynomial.eval x) hc
    rw [affinePolynomial_eval, hx a ha, MvPolynomial.eval_C] at hev
    rw [← hev, map_zero] at hc
    exact hne (affinePolynomial_injective (hc.trans (map_zero affinePolynomial).symm))
  omega

end
end MathResearch
