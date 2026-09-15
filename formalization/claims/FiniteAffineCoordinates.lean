/-
Claim: lem:finite-affine-coordinate-completion
Source: https://kbr.is-a.dev/math-research/#lean-finite-affine-coordinate-completion
Scope: Complete proper independent affine-map families on any finite coordinate type to an affine equivalence with designated coordinates; generalizes the Fin n coefficient-form interface.
Declarations: MathResearch.finite_affine_coordinate_completion
-/
import claims.FiniteAffineSpan
import Mathlib.LinearAlgebra.AffineSpace.AffineEquiv
import Mathlib.LinearAlgebra.Dual.Lemmas

namespace MathResearch
noncomputable section
open scoped BigOperators
open Module
variable {K σ ι : Type} [Field K] [Fintype σ] [Fintype ι]

private def affineLinearProjection : ((σ → K) →ᵃ[K] K) →ₗ[K] Module.Dual K (σ → K) where
  toFun f := f.linear
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

omit [Fintype σ] in
private theorem affineLinearProjection_injOn (S : Submodule K ((σ → K) →ᵃ[K] K))
    (x0 : σ → K) (hx : ∀ f ∈ S, f x0 = 0) :
    Set.InjOn affineLinearProjection (S : Set ((σ → K) →ᵃ[K] K)) := by
  intro f hf g hg hfg
  have hlin : f.linear = g.linear := hfg
  have h0 : f 0 = g 0 := by
    have hf0 := congrFun f.decomp x0
    have hg0 := congrFun g.decomp x0
    change f x0 = f.linear x0 + f 0 at hf0
    change g x0 = g.linear x0 + g 0 at hg0
    rw [hx f hf, hlin] at hf0
    rw [hx g hg] at hg0
    exact add_left_cancel (hf0.symm.trans hg0)
  ext x
  have hf0 := congrFun f.decomp x
  have hg0 := congrFun g.decomp x
  change f x = f.linear x + f 0 at hf0
  change g x = g.linear x + g 0 at hg0
  rw [hf0, hg0, hlin, h0]

omit [Fintype ι] in
private theorem finite_dual_extend (L : ι → Module.Dual K (σ → K)) (hL : LinearIndependent K L) :
    ∃ (B : Basis σ K (Module.Dual K (σ → K))) (e : ι ↪ σ), ∀ i, B (e i) = L i := by
  classical
  let I := hL.linearIndepOn_id.extend (Set.subset_univ _)
  let b : Basis I K (Module.Dual K (σ → K)) := Basis.extend hL.linearIndepOn_id
  let re := b.indexEquiv (Pi.basisFun K σ).dualBasis
  let emb (i : ι) : I := ⟨L i, hL.linearIndepOn_id.subset_extend _ (Set.mem_range_self i)⟩
  have hi : Function.Injective emb := fun _ _ h => hL.injective (congrArg Subtype.val h)
  refine ⟨b.reindex re, ⟨fun i => re (emb i), re.injective.comp hi⟩, ?_⟩
  intro i
  rw [Basis.reindex_apply]
  simp only [Function.Embedding.coeFn_mk, re.symm_apply_apply]
  exact Basis.extend_apply_self hL.linearIndepOn_id (emb i)

theorem finite_affine_coordinate_completion (g : ι → (σ → K) →ᵃ[K] K)
    (hg : LinearIndependent K g)
    (hproper : AffineMap.const K (σ → K) 1 ∉ Submodule.span K (Set.range g)) :
    ∃ (e : ι ↪ σ) (E : (σ → K) ≃ᵃ[K] (σ → K)), ∀ i x, E x (e i) = g i x := by
  classical
  let S := Submodule.span K (Set.range g)
  have hz : ∃ x, ∀ i, g i x = 0 := by
    by_contra hn
    obtain ⟨c,hc⟩ := finite_affine_unit_coefficients g hn
    exact hproper ((Submodule.mem_span_range_iff_exists_fun K).mpr ⟨c,hc.symm⟩)
  obtain ⟨x0,hx0⟩ := hz
  let ev : ((σ → K) →ᵃ[K] K) →ₗ[K] K :=
    { toFun := fun f => f x0, map_add' := by intros; rfl, map_smul' := by intros; rfl }
  have hS : S ≤ ev.ker := by
    apply Submodule.span_le.mpr
    rintro _ ⟨i,rfl⟩
    exact hx0 i
  have hL := hg.map_injOn affineLinearProjection
    (affineLinearProjection_injOn S x0 (fun f hf => hS hf))
  obtain ⟨B,e,he⟩ := finite_dual_extend (fun i => (g i).linear) hL
  let T : (σ → K) ≃ₗ[K] (σ → K) := (Module.evalEquiv K (σ → K)).trans B.dualBasis.equivFun
  let E := (AffineEquiv.vaddConst K x0).symm.trans T.toAffineEquiv
  refine ⟨e,E,?_⟩
  intro i x
  change T (x-x0) (e i) = g i x
  have ht : T (x-x0) (e i) = (g i).linear (x-x0) := by
    simp [T, Basis.dualBasis_equivFun, he]
  rw [ht]
  have hv := (g i).linearMap_vsub x x0
  simpa [hx0 i] using hv

end
end MathResearch
