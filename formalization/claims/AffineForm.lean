/-
Claim: lem:affine-form-polynomial-interface
Source: https://kbr.is-a.dev/math-research/#lean-affine-form-polynomial-interface
Scope: Canonical finite affine coefficient forms, their faithful ordinary polynomial representation and bridge from AffineMap; degree at most one over any field.
Declarations: MathResearch.affinePolynomial_eval MathResearch.affinePolynomial_degree MathResearch.affineValue_ext MathResearch.affinePolynomial_injective MathResearch.affineFormOfMap_value MathResearch.affineFormOfMap_polynomial_eval MathResearch.affinePolynomial_unit
-/
import Mathlib.LinearAlgebra.AffineSpace.AffineMap
import Mathlib.RingTheory.MvPolynomial.Basic
import Mathlib.Tactic.Ring

namespace MathResearch
noncomputable section
open scoped BigOperators

abbrev AffineForm (K : Type*) (n : ℕ) := Option (Fin n) → K

variable {K : Type*} [Field K] {n : ℕ}

def affineUnit (i : Option (Fin n)) : AffineForm K n := fun j => if i = j then 1 else 0

def affineValue (a : AffineForm K n) (x : Fin n → K) : K :=
  a none + ∑ i, a (some i) * x i

def affineEvaluation (x : Fin n → K) : AffineForm K n →ₗ[K] K where
  toFun a := affineValue a x
  map_add' a b := by
    simp [affineValue, add_mul, Finset.sum_add_distrib]
    ring
  map_smul' c a := by
    simp [affineValue, mul_add, Finset.mul_sum, mul_assoc]

def affineLinearPart : AffineForm K n →ₗ[K] (Fin n → K) where
  toFun a i := a (some i)
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

/-- Canonical ordinary polynomial represented by its affine coefficient vector. -/
def affinePolynomial : AffineForm K n →ₗ[K] MvPolynomial (Fin n) K where
  toFun a := MvPolynomial.C (a none) + ∑ i, a (some i) • MvPolynomial.X i
  map_add' a b := by
    simp [map_add, add_smul, Finset.sum_add_distrib]
    abel
  map_smul' c a := by
    simp [smul_add, Finset.smul_sum, MvPolynomial.smul_eq_C_mul, map_mul, mul_assoc]

theorem affinePolynomial_eval (a : AffineForm K n) (x : Fin n → K) :
    MvPolynomial.eval x (affinePolynomial a) = affineValue a x := by
  simp [affinePolynomial, affineValue, MvPolynomial.smul_eq_C_mul]

theorem affinePolynomial_degree (a : AffineForm K n) :
    (affinePolynomial a).totalDegree ≤ 1 := by
  apply (MvPolynomial.totalDegree_add _ _).trans
  apply max_le
  · simp
  · apply MvPolynomial.totalDegree_finsetSum_le
    intro i _
    exact (MvPolynomial.totalDegree_smul_le _ _).trans (by simp)

theorem affineValue_ext {a b : AffineForm K n}
    (h : ∀ x, affineValue a x = affineValue b x) : a = b := by
  have h0 : a none = b none := by simpa [affineValue] using h (fun _ => 0)
  funext i
  cases i with
  | none => exact h0
  | some j =>
    have hj := h (fun i => if j = i then 1 else 0)
    simp [affineValue, mul_ite, h0] at hj
    exact hj

theorem affinePolynomial_injective : Function.Injective (affinePolynomial (K := K) (n := n)) := by
  intro a b h
  apply affineValue_ext
  intro x
  rw [← affinePolynomial_eval, ← affinePolynomial_eval, h]

def affineFormOfMap (f : (Fin n → K) →ᵃ[K] K) : AffineForm K n :=
  fun i => match i with
    | none => f 0
    | some j => f.linear (fun i => if j = i then 1 else 0)

theorem affineFormOfMap_value (f : (Fin n → K) →ᵃ[K] K) (x : Fin n → K) :
    affineValue (affineFormOfMap f) x = f x := by
  have h := congrFun f.decomp x
  change f x = f.linear x + f 0 at h
  rw [LinearMap.pi_apply_eq_sum_univ f.linear x] at h
  simpa [affineValue, affineFormOfMap, smul_eq_mul, add_comm, mul_comm] using h.symm

theorem affineFormOfMap_polynomial_eval (f : (Fin n → K) →ᵃ[K] K) (x : Fin n → K) :
    MvPolynomial.eval x (affinePolynomial (affineFormOfMap f)) = f x := by
  rw [affinePolynomial_eval, affineFormOfMap_value]

theorem affinePolynomial_unit :
    affinePolynomial (affineUnit none : AffineForm K n) = 1 := by
  simp [affinePolynomial, affineUnit]


end
end MathResearch
