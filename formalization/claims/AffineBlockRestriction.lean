/-
Claim: lem:proper-affine-block-restriction
Source: https://kbr.is-a.dev/math-research/#lean-proper-affine-block-restriction
Scope: Polynomial/affine span rank and unit equivalence, and actual rank-sized affine restriction data with literal original-input coefficients.
Declarations: MathResearch.affineInputRank_eq MathResearch.affinePolynomial_unit_span_iff MathResearch.blockRestrictionData_exists MathResearch.affineInputRank_le
-/
import claims.AffineRestrictionIdeal

namespace MathResearch
noncomputable section
open MvPolynomial Module
open scoped BigOperators
variable {σ ι : Type} [Fintype σ] [Fintype ι]

abbrev AffineInputMap (σ : Type) := (σ → ZMod 2) →ᵃ[ZMod 2] ZMod 2

def affineInputRank (g : ι → AffineInputMap σ) : ℕ :=
  Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range (fun i => finiteAffinePolynomial (g i))))

private theorem finiteAffinePolynomial_const_one :
    finiteAffinePolynomial (AffineMap.const (ZMod 2) (σ → ZMod 2) 1) = 1 := by
  simp [finiteAffinePolynomial]

theorem affinePolynomial_unit_span_iff (g : ι → AffineInputMap σ) :
    (1 : MvPolynomial σ (ZMod 2)) ∈ Submodule.span (ZMod 2) (Set.range (fun i => finiteAffinePolynomial (g i))) ↔
    AffineMap.const (ZMod 2) (σ → ZMod 2) 1 ∈ Submodule.span (ZMod 2) (Set.range g) := by
  classical
  rw [Submodule.mem_span_range_iff_exists_fun, Submodule.mem_span_range_iff_exists_fun]
  constructor
  · rintro ⟨c,hc⟩
    refine ⟨c,?_⟩
    apply finiteAffinePolynomial_injective
    simpa only [map_sum, map_smul, finiteAffinePolynomial_const_one] using hc
  · rintro ⟨c,hc⟩
    refine ⟨c,?_⟩
    have he := congrArg finiteAffinePolynomial hc
    simpa only [map_sum, map_smul, finiteAffinePolynomial_const_one] using he

omit [Fintype ι] in
theorem affineInputRank_eq (g : ι → AffineInputMap σ) :
    affineInputRank g = Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range g)) := by
  let S := Submodule.span (ZMod 2) (Set.range g)
  let T := finiteAffinePolynomial.comp S.subtype
  have hi : Function.Injective T := by
    intro a b h
    apply Subtype.ext
    exact finiteAffinePolynomial_injective h
  have he : T.range = S.map finiteAffinePolynomial := by
    ext p
    constructor
    · rintro ⟨a,rfl⟩; exact ⟨a.val,a.property,rfl⟩
    · rintro ⟨a,ha,rfl⟩; exact ⟨⟨a,ha⟩,rfl⟩
  have hs : S.map finiteAffinePolynomial =
      Submodule.span (ZMod 2) (Set.range (fun i => finiteAffinePolynomial (g i))) := by
    rw [Submodule.map_span, ← Set.range_comp]
    rfl
  unfold affineInputRank
  rw [← hs, ← he]
  exact LinearMap.finrank_range_of_inj hi

structure BlockRestrictionData (g : ι → AffineInputMap σ) where
  embedding : Fin (affineInputRank g) ↪ σ
  coordinates : (σ → ZMod 2) ≃ᵃ[ZMod 2] (σ → ZMod 2)
  zeroFlat : ∀ x, (∀ j, coordinates x (embedding j) = 0) ↔ ∀ i, g i x = 0
  literal : ∀ p : MvPolynomial σ (ZMod 2), ∀ k : ℕ, p.totalDegree ≤ k →
    affineRestriction embedding coordinates p = 0 →
    ∃ a : ι → MvPolynomial σ (ZMod 2),
      (∀ i, (a i).totalDegree ≤ k-1) ∧ p = ∑ i, a i * finiteAffinePolynomial (g i)

theorem blockRestrictionData_exists (g : ι → AffineInputMap σ)
    (hproper : (1 : MvPolynomial σ (ZMod 2)) ∉
      Submodule.span (ZMod 2) (Set.range (fun i => finiteAffinePolynomial (g i)))) :
    Nonempty (BlockRestrictionData g) := by
  classical
  let S := Submodule.span (ZMod 2) (Set.range g)
  let _ : FiniteDimensional (ZMod 2) S := FiniteDimensional.span_of_finite (ZMod 2) (Set.finite_range g)
  let B : Basis (Fin (affineInputRank g)) (ZMod 2) S :=
    (Module.finBasis (ZMod 2) S).reindex (finCongr (affineInputRank_eq g).symm)
  let G := fun j => (B j).val
  have hG : LinearIndependent (ZMod 2) G :=
    B.linearIndependent.map' S.subtype (Submodule.ker_subtype S)
  have hc : ∀ j, ∃ c : ι → ZMod 2, ∑ i, c i • g i = G j := by
    intro j
    exact (Submodule.mem_span_range_iff_exists_fun (ZMod 2)).mp (B j).property
  choose c hc using hc
  have hd : ∀ i, ∃ d : Fin (affineInputRank g) → ZMod 2, ∑ j, d j • G j = g i := by
    intro i
    let v : S := ⟨g i,Submodule.subset_span (Set.mem_range_self i)⟩
    refine ⟨fun j => B.repr v j,?_⟩
    simpa only [Submodule.coe_sum,Submodule.coe_smul] using congrArg Subtype.val (B.sum_repr v)
  choose d hd using hd
  have hGS : Submodule.span (ZMod 2) (Set.range G) ≤ S := by
    apply Submodule.span_le.mpr
    rintro _ ⟨j,rfl⟩; exact (B j).property
  have hGP : AffineMap.const (ZMod 2) (σ → ZMod 2) 1 ∉ Submodule.span (ZMod 2) (Set.range G) := by
    intro hm
    exact hproper ((affinePolynomial_unit_span_iff g).mpr (hGS hm))
  obtain ⟨e,E,he⟩ := finite_affine_coordinate_completion G hG hGP
  refine ⟨{ embedding := e, coordinates := E, zeroFlat := ?_, literal := ?_ }⟩
  · intro x
    have hzero : (∀ j, G j x = 0) ↔ ∀ i, g i x = 0 := by
      let ev : AffineInputMap σ →ₗ[ZMod 2] ZMod 2 :=
        { toFun := fun f => f x, map_add' := by intros; rfl, map_smul' := by intros; rfl }
      constructor
      · intro hx i
        have hv := congrArg ev (hd i)
        simp only [map_sum,map_smul] at hv
        simpa [ev,hx] using hv.symm
      · intro hx j
        have hv := congrArg ev (hc j)
        simp only [map_sum,map_smul] at hv
        simpa [ev,hx] using hv.symm
    simpa only [he] using hzero
  · intro p k hp hz
    obtain ⟨a,ha,hpA⟩ := affine_restriction_coefficients G e E he p k hp hz
    let a' : ι → MvPolynomial σ (ZMod 2) := fun i => ∑ j, c j i • a j
    refine ⟨a',?_,?_⟩
    · intro i
      apply totalDegree_finsetSum_le
      intro j _
      exact (totalDegree_smul_le _ _).trans (ha j)
    · rw [hpA]
      simp only [a',Finset.sum_mul]
      rw [Finset.sum_comm]
      apply Finset.sum_congr rfl
      intro j _
      have hpoly := congrArg finiteAffinePolynomial (hc j)
      simp only [map_sum,map_smul] at hpoly
      rw [← hpoly, Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro i _
      simp only [smul_eq_C_mul]
      ring

theorem affineInputRank_le (g : ι → AffineInputMap σ)
    (hproper : (1 : MvPolynomial σ (ZMod 2)) ∉
      Submodule.span (ZMod 2) (Set.range (fun i => finiteAffinePolynomial (g i)))) :
    affineInputRank g ≤ Fintype.card σ := by
  obtain ⟨R⟩ := blockRestrictionData_exists g hproper
  simpa using Fintype.card_le_of_embedding R.embedding

end
end MathResearch
