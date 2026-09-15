/-
Claim: lem:finite-affine-map-span-witnesses
Source: https://kbr.is-a.dev/math-research/#lean-finite-affine-map-span-witnesses
Scope: Constant affine-map coefficient witnesses for zero-flat vanishing and inconsistency on arbitrary finite coordinate types, obtained from the verified Fin n affine-system theorem by reindexing.
Declarations: MathResearch.finite_affine_vanishing_coefficients MathResearch.finite_affine_unit_coefficients
-/
import claims.FiniteAffinePolynomial
import claims.AffineSystemLinearAlgebra
import Mathlib.Data.Fintype.EquivFin

namespace MathResearch
noncomputable section
open scoped BigOperators
variable {K σ ι : Type} [Field K] [Fintype σ] [Fintype ι]

private def finiteCoordinateMap : (Fin (Fintype.card σ) → K) →ₗ[K] (σ → K) where
  toFun x i := x (Fintype.equivFin σ i)
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

private theorem finiteCoordinateMap_surjective : Function.Surjective (finiteCoordinateMap (K := K) (σ := σ)) := by
  intro x
  exact ⟨fun j => x ((Fintype.equivFin σ).symm j), by ext i; simp [finiteCoordinateMap]⟩

private def reindexedAffine (f : (σ → K) →ᵃ[K] K) : (Fin (Fintype.card σ) → K) →ᵃ[K] K :=
  f.comp (finiteCoordinateMap.toAffineMap)

private theorem affine_coefficient_evaluation
    (f : (σ → K) →ᵃ[K] K) (g : ι → (σ → K) →ᵃ[K] K) (c : ι → K)
    (hc : affineFormOfMap (reindexedAffine f) = ∑ i, c i • affineFormOfMap (reindexedAffine (g i))) :
    f = ∑ i, c i • g i := by
  ext x
  obtain ⟨y,hy⟩ := finiteCoordinateMap_surjective (K := K) x
  have he := congrArg (affineEvaluation y) hc
  simp only [map_sum, map_smul, affineEvaluation, LinearMap.coe_mk, AddHom.coe_mk,
    affineFormOfMap_value, reindexedAffine, AffineMap.comp_apply] at he
  let ev : ((σ → K) →ᵃ[K] K) →ₗ[K] K := {
    toFun := fun a => a x
    map_add' := by intros; rfl
    map_smul' := by intros; rfl
  }
  change ev f = ev (∑ i, c i • g i)
  rw [map_sum]
  simp only [map_smul]
  simpa [ev, hy, smul_eq_mul] using he

theorem finite_affine_vanishing_coefficients (g : ι → (σ → K) →ᵃ[K] K)
    (x : σ → K) (hx : ∀ i, g i x = 0) (f : (σ → K) →ᵃ[K] K)
    (hf : ∀ y, (∀ i, g i y = 0) → f y = 0) :
    ∃ c : ι → K, f = ∑ i, c i • g i := by
  obtain ⟨x',hx'⟩ := finiteCoordinateMap_surjective (K := K) x
  obtain ⟨c,hc⟩ := affine_vanishing_coefficients
    (fun i => affineFormOfMap (reindexedAffine (g i))) x'
    (by intro i; simpa [affineFormOfMap_value, reindexedAffine, hx'] using hx i)
    (affineFormOfMap (reindexedAffine f)) (by
      intro y hy
      apply (show affineValue (affineFormOfMap (reindexedAffine f)) y =
          f (finiteCoordinateMap y) from affineFormOfMap_value _ _).trans
      apply hf
      intro i
      simpa [affineFormOfMap_value, reindexedAffine] using hy i)
  exact ⟨c, affine_coefficient_evaluation f g c hc⟩

theorem finite_affine_unit_coefficients (g : ι → (σ → K) →ᵃ[K] K)
    (h : ¬ ∃ x : σ → K, ∀ i, g i x = 0) :
    ∃ c : ι → K, AffineMap.const K (σ → K) 1 = ∑ i, c i • g i := by
  obtain ⟨c,hc⟩ := affine_inconsistent_unit_coefficients
    (fun i => affineFormOfMap (reindexedAffine (g i))) (by
      rintro ⟨x,hx⟩
      apply h
      refine ⟨finiteCoordinateMap x, ?_⟩
      intro i
      simpa [affineFormOfMap_value, reindexedAffine] using hx i)
  refine ⟨c, affine_coefficient_evaluation _ g c ?_⟩
  convert hc using 1
  funext i
  cases i <;> simp [affineFormOfMap, reindexedAffine, affineUnit]

end
end MathResearch
