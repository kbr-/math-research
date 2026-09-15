/-
Claim: lem:ordinary-restriction-dimension
Source: https://kbr.is-a.dev/math-research/#lean-ordinary-restriction-dimension
Scope: Ordinary polynomial degree-space dimension bound and affine-substitution image bound; no Boolean quotient or pointwise-zero identification.
Declarations: MathResearch.ordinary_degreeSpace_finrank_le MathResearch.affineSubstitution_totalDegree_le MathResearch.ordinary_affine_restriction_finrank_le
-/
import Mathlib.RingTheory.MvPolynomial.Basic
import Mathlib.Data.Sym.Card
import Mathlib.LinearAlgebra.Dimension.Constructions

namespace MathResearch
open MvPolynomial
noncomputable section
open scoped BigOperators

private def degreeExponentEmbedding (d k : ℕ) :
    {e : Fin d →₀ ℕ // e.sum (fun _ n => n) ≤ k} ↪ Sym (Option (Fin d)) k where
  toFun e := (Sym.equivNatSumOfFintype (Option (Fin d)) k).symm
    ⟨fun i => match i with | none => k - e.val.sum (fun _ n => n) | some j => e.val j,
     by
       simp only [Fintype.sum_option]
       rw [← Finsupp.sum_fintype e.val (fun _ n => n) (by simp)]
       exact Nat.sub_add_cancel e.property⟩
  inj' := by
    intro e f h
    have hh := (Sym.equivNatSumOfFintype (Option (Fin d)) k).symm.injective h
    apply Subtype.ext
    apply Finsupp.ext
    intro i
    exact congrArg (fun x => x.val (some i)) hh

theorem ordinary_degreeSpace_finrank_le (K : Type*) [Field K] (d k : ℕ) :
    Module.finrank K (restrictTotalDegree (Fin d) K k) ≤ (d + k).choose k := by
  let _ : Finite {e : Fin d →₀ ℕ // e.sum (fun _ n => n) ≤ k} :=
    Finite.of_injective (degreeExponentEmbedding d k) (degreeExponentEmbedding d k).injective
  let _ : Fintype {e : Fin d →₀ ℕ // e.sum (fun _ n => n) ≤ k} := Fintype.ofFinite _
  rw [show restrictTotalDegree (Fin d) K k =
    restrictSupport K {e | e.sum (fun _ n => n) ≤ k} from rfl]
  rw [Module.finrank_eq_nat_card_basis (basisRestrictSupport K _)]
  change Nat.card {e : Fin d →₀ ℕ // e.sum (fun _ n => n) ≤ k} ≤ _
  rw [Nat.card_eq_fintype_card]
  have h := Fintype.card_le_of_injective (degreeExponentEmbedding d k)
    (degreeExponentEmbedding d k).injective
  simpa [Sym.card_sym_eq_choose] using h

theorem affineSubstitution_totalDegree_le {K σ τ : Type*} [Field K]
    (g : σ → MvPolynomial τ K) (hg : ∀ i, (g i).totalDegree ≤ 1)
    (p : MvPolynomial σ K) : (aeval g p).totalDegree ≤ p.totalDegree := by
  classical
  nth_rw 1 [p.as_sum]
  rw [map_sum]
  apply totalDegree_finsetSum_le
  intro e he
  rw [aeval_monomial]
  calc
    (algebraMap K (MvPolynomial τ K) (p.coeff e) * e.prod (fun i n => g i ^ n)).totalDegree
      ≤ (algebraMap K (MvPolynomial τ K) (p.coeff e)).totalDegree +
        (e.prod (fun i n => g i ^ n)).totalDegree := totalDegree_mul _ _
    _ ≤ 0 + e.sum (fun _ n => n) := by
      simp only [MvPolynomial.algebraMap_eq, totalDegree_C, zero_add]
      apply (totalDegree_finsetProd e.support _).trans
      apply Finset.sum_le_sum
      intro i _
      exact (totalDegree_pow _ _).trans (by simpa using Nat.mul_le_mul_left (e i) (hg i))
    _ ≤ p.totalDegree := by simpa using le_totalDegree he

theorem ordinary_affine_restriction_finrank_le {K σ : Type*} [Field K]
    (d k : ℕ) (U : Submodule K (MvPolynomial σ K))
    (hU : ∀ p ∈ U, p.totalDegree ≤ k)
    (g : σ → MvPolynomial (Fin d) K) (hg : ∀ i, (g i).totalDegree ≤ 1) :
    Module.finrank K (U.map (aeval g).toLinearMap) ≤ (d + k).choose k := by
  have hle : U.map (aeval g).toLinearMap ≤ restrictTotalDegree (Fin d) K k := by
    rintro p ⟨q, hq, rfl⟩
    apply (mem_restrictTotalDegree _ _ _).mpr
    exact (affineSubstitution_totalDegree_le g hg q).trans (hU q hq)
  exact (Submodule.finrank_mono hle).trans (ordinary_degreeSpace_finrank_le K d k)

end
end MathResearch
