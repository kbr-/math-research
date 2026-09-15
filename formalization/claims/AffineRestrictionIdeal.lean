/-
Claim: lem:ordinary-affine-restriction-ideal
Source: https://kbr.is-a.dev/math-research/#lean-ordinary-affine-restriction-ideal
Scope: Binary ordinary affine coordinate pullbacks and inverse identities; zero ordinary free-coordinate restriction gives literal degree-(k-1) affine-generator coefficients.
Declarations: MathResearch.polynomialPullback_degree MathResearch.polynomialPullback_eval MathResearch.polynomialPullback_comp MathResearch.polynomialPullback_id MathResearch.polynomialPullback_inverse MathResearch.affine_restriction_coefficients MathResearch.coordinateRestriction_degree MathResearch.affineRestriction_degree MathResearch.coordinateFreeIndex_card MathResearch.affineRestriction_image_finrank_le
-/
import claims.FiniteAffineCoordinates
import claims.CoordinateRestrictionIdeal
import claims.OrdinaryRestrictionDimension
import Mathlib.FieldTheory.Finite.Polynomial

namespace MathResearch
noncomputable section
open MvPolynomial
open scoped BigOperators
variable {σ τ υ ι : Type} [Fintype σ] [Fintype τ] [Fintype υ] [Fintype ι]

private theorem affine_poly_ext (p q : MvPolynomial σ (ZMod 2))
    (hp : p.totalDegree ≤ 1) (hq : q.totalDegree ≤ 1)
    (he : ∀ x, eval x p = eval x q) : p = q := by
  classical
  apply sub_eq_zero.mp
  apply MvPolynomial.eq_zero_of_eval_eq_zero σ (ZMod 2) (p-q)
  · intro x; simp [he]
  · have hd : (p-q).totalDegree ≤ 1 := (totalDegree_sub _ _).trans (max_le hp hq)
    simp only [ZMod.card, Nat.reduceSub]
    apply (mem_restrictDegree_iff_sup σ (p-q) 1).mpr
    intro i
    change (p-q).degreeOf i ≤ 1
    exact (degreeOf_le_totalDegree _ _).trans hd

def polynomialPullback (A : (τ → ZMod 2) →ᵃ[ZMod 2] (σ → ZMod 2)) :
    MvPolynomial σ (ZMod 2) →ₐ[ZMod 2] MvPolynomial τ (ZMod 2) :=
  aeval (fun i => finiteAffinePolynomial ((AffineMap.proj i).comp A))

omit [Fintype σ] in
private theorem polynomialPullback_X (A : (τ → ZMod 2) →ᵃ[ZMod 2] (σ → ZMod 2)) (i : σ) :
    polynomialPullback A (X i) = finiteAffinePolynomial ((AffineMap.proj i).comp A) := aeval_X _ i

omit [Fintype σ] in
theorem polynomialPullback_degree (A : (τ → ZMod 2) →ᵃ[ZMod 2] (σ → ZMod 2))
    (p : MvPolynomial σ (ZMod 2)) : (polynomialPullback A p).totalDegree ≤ p.totalDegree :=
  affineSubstitution_totalDegree_le _ (fun _ => finiteAffinePolynomial_degree _) p

omit [Fintype σ] in
theorem polynomialPullback_eval (A : (τ → ZMod 2) →ᵃ[ZMod 2] (σ → ZMod 2))
    (p : MvPolynomial σ (ZMod 2)) (x : τ → ZMod 2) :
    eval x (polynomialPullback A p) = eval (A x) p := by
  change aeval x (aeval (fun i => finiteAffinePolynomial ((AffineMap.proj i).comp A)) p) = _
  rw [comp_aeval_apply]
  have he : (fun i => aeval x (finiteAffinePolynomial ((AffineMap.proj i).comp A))) = A x := by
    funext i
    exact finiteAffinePolynomial_eval _ x
  rw [he]
  rfl

omit [Fintype σ] in
theorem polynomialPullback_comp (A : (τ → ZMod 2) →ᵃ[ZMod 2] (σ → ZMod 2))
    (B : (υ → ZMod 2) →ᵃ[ZMod 2] (τ → ZMod 2)) :
    (polynomialPullback B).comp (polynomialPullback A) = polynomialPullback (A.comp B) := by
  apply MvPolynomial.algHom_ext
  intro i
  rw [AlgHom.comp_apply, polynomialPullback_X, polynomialPullback_X]
  apply affine_poly_ext
  · exact (polynomialPullback_degree _ _).trans (finiteAffinePolynomial_degree _)
  · exact finiteAffinePolynomial_degree _
  · intro x
    rw [polynomialPullback_eval, finiteAffinePolynomial_eval, finiteAffinePolynomial_eval]
    rfl

theorem polynomialPullback_id :
    polynomialPullback (AffineMap.id (ZMod 2) (σ → ZMod 2)) = AlgHom.id (ZMod 2) _ := by
  apply MvPolynomial.algHom_ext
  intro i
  rw [polynomialPullback_X, AlgHom.id_apply]
  apply affine_poly_ext (hp := finiteAffinePolynomial_degree _) (hq := by simp)
  intro x
  simp [finiteAffinePolynomial_eval]

theorem polynomialPullback_inverse (E : (σ → ZMod 2) ≃ᵃ[ZMod 2] (σ → ZMod 2))
    (p : MvPolynomial σ (ZMod 2)) :
    polynomialPullback E.toAffineMap (polynomialPullback E.symm.toAffineMap p) = p := by
  have he : E.symm.toAffineMap.comp E.toAffineMap = AffineMap.id (ZMod 2) _ := by
    ext x; simp
  rw [← AlgHom.comp_apply, polynomialPullback_comp, he, polynomialPullback_id]
  rfl

def affineRestriction (e : ι ↪ σ) (E : (σ → ZMod 2) ≃ᵃ[ZMod 2] (σ → ZMod 2)) :
    MvPolynomial σ (ZMod 2) →ₐ[ZMod 2] MvPolynomial (CoordinateFreeIndex e) (ZMod 2) :=
  (coordinateRestriction e).comp (polynomialPullback E.symm.toAffineMap)

theorem affine_restriction_coefficients (g : ι → (σ → ZMod 2) →ᵃ[ZMod 2] (ZMod 2))
    (e : ι ↪ σ) (E : (σ → ZMod 2) ≃ᵃ[ZMod 2] (σ → ZMod 2))
    (he : ∀ i x, E x (e i) = g i x) (p : MvPolynomial σ (ZMod 2)) (k : ℕ)
    (hp : p.totalDegree ≤ k) (hz : affineRestriction e E p = 0) :
    ∃ a : ι → MvPolynomial σ (ZMod 2),
      (∀ i, (a i).totalDegree ≤ k-1) ∧ p = ∑ i, a i * finiteAffinePolynomial (g i) := by
  classical
  obtain ⟨a,ha,heq⟩ := coordinate_restriction_coefficients e
    (polynomialPullback E.symm.toAffineMap p) k
    ((polynomialPullback_degree _ _).trans hp) hz
  refine ⟨fun i => polynomialPullback E.toAffineMap (a i),
    fun i => (polynomialPullback_degree _ _).trans (ha i), ?_⟩
  have hi (i : ι) : polynomialPullback E.toAffineMap (X (e i)) = finiteAffinePolynomial (g i) := by
    have hh : (AffineMap.proj (e i)).comp E.toAffineMap = g i := by
      ext x; exact he i x
    change aeval _ (X (e i)) = _
    rw [aeval_X, hh]
  have hh := congrArg (polynomialPullback E.toAffineMap) heq
  rw [polynomialPullback_inverse, map_sum] at hh
  simpa only [map_mul, hi] using hh

omit [Fintype σ] [Fintype ι] in
theorem coordinateRestriction_degree (e : ι ↪ σ) (p : MvPolynomial σ (ZMod 2)) :
    (coordinateRestriction e p).totalDegree ≤ p.totalDegree := by
  classical
  unfold coordinateRestriction MvPolynomial.killCompl
  apply affineSubstitution_totalDegree_le
  intro i
  split <;> simp

omit [Fintype ι] in
theorem affineRestriction_degree (e : ι ↪ σ)
    (E : (σ → ZMod 2) ≃ᵃ[ZMod 2] (σ → ZMod 2)) (p : MvPolynomial σ (ZMod 2)) :
    (affineRestriction e E p).totalDegree ≤ p.totalDegree :=
  (coordinateRestriction_degree e _).trans (polynomialPullback_degree _ p)

private theorem finite_degreeSpace_finrank_le (k : ℕ) :
    Module.finrank (ZMod 2) (restrictTotalDegree σ (ZMod 2) k) ≤
      (Fintype.card σ+k).choose k := by
  classical
  let e := Fintype.equivFin σ
  let T : restrictTotalDegree σ (ZMod 2) k →ₗ[ZMod 2]
      restrictTotalDegree (Fin (Fintype.card σ)) (ZMod 2) k :=
    { toFun := fun p => ⟨rename e p.val, (mem_restrictTotalDegree _ _ _).mpr
        ((totalDegree_rename_le e p.val).trans ((mem_restrictTotalDegree _ _ _).mp p.property))⟩
      map_add' := by intro p q; apply Subtype.ext; exact map_add (rename e) p.val q.val
      map_smul' := by intro c p; apply Subtype.ext; exact map_smul (rename e) c p.val }
  have hi : Function.Injective T := by
    intro p q hpq
    apply Subtype.ext
    exact (rename_injective e e.injective) (congrArg Subtype.val hpq)
  exact (LinearMap.finrank_le_finrank_of_injective hi).trans
    (ordinary_degreeSpace_finrank_le (ZMod 2) _ k)

theorem coordinateFreeIndex_card (e : ι ↪ σ) :
    Nat.card (CoordinateFreeIndex e) = Fintype.card σ-Fintype.card ι := by
  classical
  rw [Nat.card_eq_fintype_card]
  change Fintype.card {x : σ // ¬x ∈ Set.range e} = _
  rw [Fintype.card_subtype_compl]
  congr 1
  exact (Fintype.card_congr (Equiv.ofInjective e e.injective)).symm

theorem affineRestriction_image_finrank_le (e : ι ↪ σ)
    (E : (σ → ZMod 2) ≃ᵃ[ZMod 2] (σ → ZMod 2))
    (U : Submodule (ZMod 2) (MvPolynomial σ (ZMod 2))) (k : ℕ)
    (hU : ∀ p ∈ U, p.totalDegree ≤ k) :
    Module.finrank (ZMod 2) (U.map (affineRestriction e E).toLinearMap) ≤
      (Fintype.card σ-Fintype.card ι+k).choose k := by
  classical
  have hle : U.map (affineRestriction e E).toLinearMap ≤
      restrictTotalDegree (CoordinateFreeIndex e) (ZMod 2) k := by
    rintro p ⟨q,hq,rfl⟩
    exact (mem_restrictTotalDegree _ _ _).mpr ((affineRestriction_degree e E q).trans (hU q hq))
  have hb := (Submodule.finrank_mono hle).trans
    (finite_degreeSpace_finrank_le (σ := CoordinateFreeIndex e) k)
  have hc : Fintype.card (CoordinateFreeIndex e) = Fintype.card σ-Fintype.card ι := by
    simpa only [Nat.card_eq_fintype_card] using coordinateFreeIndex_card e
  simpa only [hc] using hb

end
end MathResearch
