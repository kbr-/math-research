/-
Claim: lem:affine-coordinate-completion
Source: https://kbr.is-a.dev/math-research/#lean-affine-coordinate-completion
Scope: Complete finite independent proper affine families to affine coordinates, with exact designated coordinate values and free-coordinate parametrization.
Declarations: MathResearch.affine_coordinate_completion MathResearch.affineFlatParam_injective MathResearch.affineFlatParam_range MathResearch.affineFreeIndex_card
-/
import claims.AffineSystemLinearAlgebra
import Mathlib.LinearAlgebra.AffineSpace.AffineEquiv

namespace MathResearch
noncomputable section
open scoped BigOperators
open Module
variable {K : Type*} [Field K] {n : ℕ}

private def coefficientDual : (Fin n → K) →ₗ[K] Module.Dual K (Fin n → K) where
  toFun a :=
    { toFun := fun x => ∑ i, a i * x i
      map_add' := by intro x y; simp [mul_add, Finset.sum_add_distrib]
      map_smul' := by intro c x; simp [Finset.mul_sum, mul_left_comm] }
  map_add' := by intro a b; ext x; simp [add_mul, Finset.sum_add_distrib]
  map_smul' := by intro c a; ext x; simp [Finset.mul_sum, mul_assoc]

private theorem coefficientDual_injective : Function.Injective (coefficientDual (K := K) (n := n)) := by
  intro a b h
  funext i
  have hi := LinearMap.congr_fun h (fun j => if i = j then 1 else 0)
  simpa [coefficientDual, mul_ite] using hi

private theorem extend_dual_family {ι : Type*} (L : ι → Module.Dual K (Fin n → K))
    (hL : LinearIndependent K L) :
    ∃ (B : Basis (Fin n) K (Module.Dual K (Fin n → K))) (e : ι ↪ Fin n),
      ∀ i, B (e i) = L i := by
  let I := hL.linearIndepOn_id.extend (Set.subset_univ _)
  let b : Basis I K (Module.Dual K (Fin n → K)) := Basis.extend hL.linearIndepOn_id
  let b0 := (Pi.basisFun K (Fin n)).dualBasis
  let re := b.indexEquiv b0
  let emb (i : ι) : I := ⟨L i, hL.linearIndepOn_id.subset_extend _ (Set.mem_range_self i)⟩
  have hi : Function.Injective emb := by
    intro i j h
    exact hL.injective (congrArg Subtype.val h)
  refine ⟨b.reindex re, ⟨fun i => re (emb i), re.injective.comp hi⟩, ?_⟩
  intro i
  rw [Basis.reindex_apply]
  simp only [Function.Embedding.coeFn_mk, re.symm_apply_apply]
  exact Basis.extend_apply_self hL.linearIndepOn_id (emb i)

theorem affine_coordinate_completion {ι : Type*} (g : ι → AffineForm K n)
    (hg : LinearIndependent K g)
    (hproper : affineUnit none ∉ Submodule.span K (Set.range g)) :
    ∃ (e : ι ↪ Fin n) (E : (Fin n → K) ≃ᵃ[K] (Fin n → K)),
      ∀ i x, E x (e i) = affineValue (g i) x := by
  let L : ι → Module.Dual K (Fin n → K) := fun i => coefficientDual (affineLinearPart (g i))
  have hL : LinearIndependent K L :=
    (affine_independent_linearParts g hg hproper).map' coefficientDual
      (LinearMap.ker_eq_bot.mpr coefficientDual_injective)
  obtain ⟨B, e, he⟩ := extend_dual_family L hL
  obtain ⟨x0, hx0⟩ := affine_proper_common_zero (Submodule.span K (Set.range g)) hproper
  let T : (Fin n → K) ≃ₗ[K] (Fin n → K) :=
    (Module.evalEquiv K (Fin n → K)).trans B.dualBasis.equivFun
  let E := (AffineEquiv.vaddConst K x0).symm.trans T.toAffineEquiv
  refine ⟨e, E, ?_⟩
  intro i x
  have ht : T (x - x0) (e i) = L i (x - x0) := by
    simp [T, Basis.dualBasis_equivFun, he]
  change T (x - x0) (e i) = affineValue (g i) x
  rw [ht]
  have hz := hx0 _ (Submodule.subset_span (Set.mem_range_self i))
  simp only [affineValue] at hz
  change (∑ j, g i (some j) * (x j - x0 j)) = _
  simp only [mul_sub, Finset.sum_sub_distrib, affineValue]
  have hh : -(∑ j, g i (some j) * x0 j) = g i none := by
    exact neg_eq_iff_add_eq_zero.mpr (by simpa [add_comm] using hz)
  rw [sub_eq_add_neg, hh, add_comm]

abbrev AffineFreeIndex {ι : Type*} (e : ι ↪ Fin n) := {j : Fin n // j ∉ Set.range e}

def affineZeroExtend {ι : Type*} (e : ι ↪ Fin n) :
    (AffineFreeIndex e → K) →ₗ[K] (Fin n → K) := by
  classical
  exact
    { toFun := fun y j => if h : j ∈ Set.range e then 0 else y ⟨j, h⟩
      map_add' := by
        intro y z; funext j
        by_cases h : j ∈ Set.range e <;> simp only [h, dite_true, dite_false, Pi.add_apply, add_zero]
      map_smul' := by
        intro c y; funext j
        by_cases h : j ∈ Set.range e <;> simp only [h, dite_true, dite_false, Pi.smul_apply, smul_zero, RingHom.id_apply] }

def affineFlatParam {ι : Type*} (e : ι ↪ Fin n)
    (E : (Fin n → K) ≃ᵃ[K] (Fin n → K)) :
    (AffineFreeIndex e → K) →ᵃ[K] (Fin n → K) :=
  E.symm.toAffineMap.comp (affineZeroExtend e).toAffineMap

theorem affineFlatParam_injective {ι : Type*} (e : ι ↪ Fin n)
    (E : (Fin n → K) ≃ᵃ[K] (Fin n → K)) :
    Function.Injective (affineFlatParam e E) := by
  classical
  intro y z h
  have hh : affineZeroExtend e y = affineZeroExtend e z := E.symm.injective h
  funext j
  have hv := congrFun hh j.val
  simpa only [affineZeroExtend, LinearMap.coe_mk, AddHom.coe_mk, dite_eq_right j.property] using hv

theorem affineFlatParam_range {ι : Type*} (g : ι → AffineForm K n)
    (e : ι ↪ Fin n) (E : (Fin n → K) ≃ᵃ[K] (Fin n → K))
    (he : ∀ i x, E x (e i) = affineValue (g i) x) :
    Set.range (affineFlatParam e E) = {x | ∀ i, affineValue (g i) x = 0} := by
  classical
  ext x
  constructor
  · rintro ⟨y, rfl⟩ i
    rw [← he]
    change E (E.symm (affineZeroExtend e y)) (e i) = 0
    rw [E.apply_symm_apply]
    simp [affineZeroExtend]
  · intro hx
    refine ⟨fun j => E x j.val, ?_⟩
    apply E.injective
    change E (E.symm (affineZeroExtend e (fun j => E x j.val))) = E x
    rw [E.apply_symm_apply]
    funext j
    by_cases hj : j ∈ Set.range e
    · obtain ⟨i, rfl⟩ := hj
      simp [affineZeroExtend, he, hx i]
    · simp only [affineZeroExtend, LinearMap.coe_mk, AddHom.coe_mk, dite_eq_right hj]

theorem affineFreeIndex_card {r : ℕ} (e : Fin r ↪ Fin n) :
    Nat.card (AffineFreeIndex e) = n - r := by
  classical
  rw [Nat.card_eq_fintype_card]
  change Fintype.card {j : Fin n // ¬j ∈ Set.range e} = n - r
  rw [Fintype.card_subtype_compl, Fintype.card_fin]
  congr 1
  exact (Fintype.card_congr (Equiv.ofInjective e e.injective)).symm.trans (Fintype.card_fin r)

end
end MathResearch
