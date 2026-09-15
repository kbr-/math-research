/-
Claim: lem:finite-affine-map-polynomial-bridge
Source: https://kbr.is-a.dev/math-research/#lean-finite-affine-map-polynomial-bridge
Scope: Faithful linear conversion of affine maps on an arbitrary finite coordinate type to ordinary degree-at-most-one polynomials, generalizing the existing Fin n affine-form interface without changing it.
Declarations: MathResearch.finiteAffinePolynomial_fin MathResearch.finiteAffinePolynomial_eval MathResearch.finiteAffinePolynomial_degree MathResearch.finiteAffinePolynomial_injective
-/
import claims.AffineForm

namespace MathResearch
noncomputable section
open scoped BigOperators
variable {K σ : Type} [Field K] [Fintype σ]
local instance : DecidableEq σ := Classical.decEq σ

def finiteAffinePolynomial : ((σ → K) →ᵃ[K] K) →ₗ[K] MvPolynomial σ K where
  toFun f := MvPolynomial.C (f 0) +
    ∑ i, f.linear (fun j => if i = j then 1 else 0) • MvPolynomial.X i
  map_add' f g := by
    simp [map_add, add_smul, Finset.sum_add_distrib]
    abel
  map_smul' c f := by
    simp [smul_add, Finset.smul_sum, MvPolynomial.smul_eq_C_mul, map_mul, mul_assoc]

theorem finiteAffinePolynomial_eval (f : (σ → K) →ᵃ[K] K) (x : σ → K) :
    MvPolynomial.eval x (finiteAffinePolynomial f) = f x := by
  have h := congrFun f.decomp x
  change f x = f.linear x + f 0 at h
  rw [LinearMap.pi_apply_eq_sum_univ f.linear x] at h
  simpa [finiteAffinePolynomial, MvPolynomial.smul_eq_C_mul, add_comm, mul_comm] using h.symm

theorem finiteAffinePolynomial_degree (f : (σ → K) →ᵃ[K] K) :
    (finiteAffinePolynomial f).totalDegree ≤ 1 := by
  apply (MvPolynomial.totalDegree_add _ _).trans
  apply max_le
  · simp
  · apply MvPolynomial.totalDegree_finsetSum_le
    intro i _
    exact (MvPolynomial.totalDegree_smul_le _ _).trans (by simp)

theorem finiteAffinePolynomial_injective : Function.Injective (finiteAffinePolynomial (K := K) (σ := σ)) := by
  intro f g h
  ext x
  rw [← finiteAffinePolynomial_eval, ← finiteAffinePolynomial_eval, h]

theorem finiteAffinePolynomial_fin {n : ℕ} (f : (Fin n → K) →ᵃ[K] K) :
    finiteAffinePolynomial f = affinePolynomial (affineFormOfMap f) := by
  simp only [finiteAffinePolynomial, LinearMap.coe_mk, AddHom.coe_mk,
    affinePolynomial, affineFormOfMap]
  congr 1
  apply Finset.sum_congr rfl
  intro i _
  congr 1
  apply congrArg f.linear
  funext j
  by_cases he : i = j <;> simp [he]

end
end MathResearch
