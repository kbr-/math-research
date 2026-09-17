/-
Claim: thm:generic-affine-subspace-consequence-transfer
Source: https://kbr.is-a.dev/math-research/#generic-affine-subspace-consequence-transfer
Scope: Full indexed theorem over the binary field, for an arbitrary finite variable type, an arbitrary old base containing the Boolean equations, a finite complete one-level affine ENS family of accuracy h ≥ 1, and an arbitrary linear subspace U of polynomials of total degree at most k. The dimension inequality is stated without natural subtraction as dim U ≤ dim(U ⊓ pcSpace F (k(D+1))) + R, where R sums the ordinary restriction bounds over blocks whose input span omits one and has rank above h(k+1). Includes the nonzero-consequence and exclusion corollaries, the uniform rank-threshold bound on R, and emptiness of the high index when h(k+1)+1 exceeds the number of variables. The CNF initial-value bridge and the short-proof control of the source entry are separate remarks and are not covered.
Declarations: MathResearch.GenericProperHighIndex MathResearch.generic_affine_subspace_consequence MathResearch.generic_affine_subspace_nonzero_consequence MathResearch.generic_affine_subspace_exclusion MathResearch.generic_proper_high_restriction_sum_le MathResearch.generic_proper_high_isEmpty
-/
import claims.AffineBlockRestriction
import claims.AffineFamilyRemovalWithUnits

namespace MathResearch
noncomputable section
open MvPolynomial Module PolynomialCalculus
open scoped BigOperators

/-- Blocks whose input span omits one and has rank above `h*(k+1)`. -/
abbrev GenericProperHighIndex {σ κ : Type} [Fintype σ] {ι : κ → Type} [∀ b, Fintype (ι b)]
    (g : ∀ b, ι b → AffineInputMap σ) (h k : ℕ) :=
  {b : κ // h*(k+1) < affineInputRank (g b) ∧
    (1 : MvPolynomial σ (ZMod 2)) ∉
      Submodule.span (ZMod 2) (Set.range (fun i => finiteAffinePolynomial (g b i)))}

open scoped Classical in
/-- The generic dimension-budget consequence theorem. -/
theorem generic_affine_subspace_consequence {σ κ : Type} [Fintype σ] [Fintype κ]
    {ι : κ → Type} [∀ b, Fintype (ι b)]
    (g : ∀ b, ι b → AffineInputMap σ) (h k D : ℕ)
    (hh : 1 ≤ h) (hk : 1 ≤ k) (hD : 2*h+1 ≤ D)
    (F : Set (MvPolynomial σ (ZMod 2))) (hF : booleanBase ⊆ F)
    (U : Submodule (ZMod 2) (MvPolynomial σ (ZMod 2))) (hU : ∀ p ∈ U, p.totalDegree ≤ k)
    (href : Derives (ensFamilySystem (fun b i => finiteAffinePolynomial (g b i)) h F) D 1) :
    Module.finrank (ZMod 2) U ≤
      Module.finrank (ZMod 2) ↥(U ⊓ pcSpace F (k*(D+1))) +
        ∑ b : GenericProperHighIndex g h k,
          (Fintype.card σ - affineInputRank (g b.val) + k).choose k := by
  have hUle : U ≤ restrictTotalDegree σ (ZMod 2) k :=
    fun p hp => (mem_restrictTotalDegree _ _ _).mpr (hU p hp)
  have : FiniteDimensional (ZMod 2) U := Submodule.finiteDimensional_of_le hUle
  let R : ∀ b : GenericProperHighIndex g h k, BlockRestrictionData (g b.val) :=
    fun b => Classical.choice (blockRestrictionData_exists (g b.val) b.property.2)
  let L (b : GenericProperHighIndex g h k) : U →ₗ[ZMod 2]
      MvPolynomial (CoordinateFreeIndex (R b).embedding) (ZMod 2) :=
    (affineRestriction (R b).embedding (R b).coordinates).toLinearMap.comp U.subtype
  let T : U →ₗ[ZMod 2] (∀ b : GenericProperHighIndex g h k, (L b).range) :=
    LinearMap.pi (fun b => (L b).rangeRestrict)
  -- Every member of the joint kernel is derivable from the old base.
  have hker : ∀ p : U, T p = 0 → Derives F (k*(D+1)) p.val := by
    intro p hp
    have hzero : ∀ b : GenericProperHighIndex g h k, L b p = 0 :=
      fun b => congrArg Subtype.val (congrFun hp b)
    apply affine_family_removal_with_units
      (fun b i => finiteAffinePolynomial (g b i)) (fun b i => finiteAffinePolynomial_degree (g b i))
      h k D hh hk hD F hF p.val (hU p.val p.property) ?_ href
    intro b hb
    by_cases hu : (1 : MvPolynomial σ (ZMod 2)) ∈
        Submodule.span (ZMod 2) (Set.range (fun i => finiteAffinePolynomial (g b i)))
    · exact Or.inl hu
    · have hb' : h*(k+1) < affineInputRank (g b) := hb
      let b' : GenericProperHighIndex g h k := ⟨b,hb',hu⟩
      exact Or.inr ((R b').literal p.val k (hU p.val p.property) (hzero b'))
  -- The kernel embeds in the derivable part of U.
  let J : LinearMap.ker T →ₗ[ZMod 2] ↥(U ⊓ pcSpace F (k*(D+1))) :=
    { toFun := fun p => ⟨p.val.val, Submodule.mem_inf.mpr
        ⟨p.val.property, hker p.val (LinearMap.mem_ker.mp p.property)⟩⟩
      map_add' := fun _ _ => rfl
      map_smul' := fun _ _ => rfl }
  have hJ : Function.Injective J := by
    intro p q hpq
    apply Subtype.ext
    apply Subtype.ext
    exact congrArg (fun z : ↥(U ⊓ pcSpace F (k*(D+1))) => z.val) hpq
  have hkerdim := LinearMap.finrank_le_finrank_of_injective hJ
  -- Each restriction image obeys the ordinary dimension bound.
  have himage (b : GenericProperHighIndex g h k) : Module.finrank (ZMod 2) (L b).range ≤
      (Fintype.card σ - affineInputRank (g b.val) + k).choose k := by
    have he : (L b).range =
        U.map (affineRestriction (R b).embedding (R b).coordinates).toLinearMap := by
      ext p
      constructor
      · rintro ⟨a,rfl⟩; exact ⟨a.val,a.property,rfl⟩
      · rintro ⟨a,ha,rfl⟩; exact ⟨⟨a,ha⟩,rfl⟩
    rw [he]
    have hb := affineRestriction_image_finrank_le (R b).embedding (R b).coordinates U k hU
    simpa only [Fintype.card_fin] using hb
  have hrange : Module.finrank (ZMod 2) (LinearMap.range T) ≤
      ∑ b : GenericProperHighIndex g h k,
        (Fintype.card σ - affineInputRank (g b.val) + k).choose k := by
    calc
      _ ≤ Module.finrank (ZMod 2) (∀ b : GenericProperHighIndex g h k, (L b).range) :=
        Submodule.finrank_le _
      _ = ∑ b : GenericProperHighIndex g h k, Module.finrank (ZMod 2) (L b).range :=
        Module.finrank_pi_fintype _
      _ ≤ _ := Finset.sum_le_sum (fun b _ => himage b)
  have hrank := LinearMap.finrank_range_add_finrank_ker T
  omega

open scoped Classical in
/-- If the restriction budget is below `dim U`, a nonzero member of `U` is derivable. -/
theorem generic_affine_subspace_nonzero_consequence {σ κ : Type} [Fintype σ] [Fintype κ]
    {ι : κ → Type} [∀ b, Fintype (ι b)]
    (g : ∀ b, ι b → AffineInputMap σ) (h k D : ℕ)
    (hh : 1 ≤ h) (hk : 1 ≤ k) (hD : 2*h+1 ≤ D)
    (F : Set (MvPolynomial σ (ZMod 2))) (hF : booleanBase ⊆ F)
    (U : Submodule (ZMod 2) (MvPolynomial σ (ZMod 2))) (hU : ∀ p ∈ U, p.totalDegree ≤ k)
    (hdim : (∑ b : GenericProperHighIndex g h k,
      (Fintype.card σ - affineInputRank (g b.val) + k).choose k) < Module.finrank (ZMod 2) U)
    (href : Derives (ensFamilySystem (fun b i => finiteAffinePolynomial (g b i)) h F) D 1) :
    ∃ f ∈ U, f ≠ 0 ∧ Derives F (k*(D+1)) f := by
  have hUle : U ≤ restrictTotalDegree σ (ZMod 2) k :=
    fun p hp => (mem_restrictTotalDegree _ _ _).mpr (hU p hp)
  have : FiniteDimensional (ZMod 2) U := Submodule.finiteDimensional_of_le hUle
  have hmain := generic_affine_subspace_consequence g h k D hh hk hD F hF U hU href
  have hpos : 0 < Module.finrank (ZMod 2) ↥(U ⊓ pcSpace F (k*(D+1))) := by omega
  obtain ⟨x,hx⟩ := Module.finrank_pos_iff_exists_ne_zero.mp hpos
  obtain ⟨hxU,hxpc⟩ := Submodule.mem_inf.mp x.property
  exact ⟨x.val,hxU,fun hz => hx (Subtype.ext hz),hxpc⟩

open scoped Classical in
/-- A separated subspace larger than the restriction budget excludes the refutation. -/
theorem generic_affine_subspace_exclusion {σ κ : Type} [Fintype σ] [Fintype κ]
    {ι : κ → Type} [∀ b, Fintype (ι b)]
    (g : ∀ b, ι b → AffineInputMap σ) (h k D : ℕ)
    (hh : 1 ≤ h) (hk : 1 ≤ k) (hD : 2*h+1 ≤ D)
    (F : Set (MvPolynomial σ (ZMod 2))) (hF : booleanBase ⊆ F)
    (U : Submodule (ZMod 2) (MvPolynomial σ (ZMod 2))) (hU : ∀ p ∈ U, p.totalDegree ≤ k)
    (hsep : ∀ f ∈ U, Derives F (k*(D+1)) f → f = 0)
    (hdim : (∑ b : GenericProperHighIndex g h k,
      (Fintype.card σ - affineInputRank (g b.val) + k).choose k) < Module.finrank (ZMod 2) U) :
    ¬ Derives (ensFamilySystem (fun b i => finiteAffinePolynomial (g b i)) h F) D 1 := by
  intro href
  obtain ⟨f,hfU,hne,hder⟩ :=
    generic_affine_subspace_nonzero_consequence g h k D hh hk hD F hF U hU hdim href
  exact hne (hsep f hfU hder)

open scoped Classical in
/-- The uniform rank-threshold form of the restriction budget. -/
theorem generic_proper_high_restriction_sum_le {σ κ : Type} [Fintype σ] [Fintype κ]
    {ι : κ → Type} [∀ b, Fintype (ι b)]
    (g : ∀ b, ι b → AffineInputMap σ) (h k : ℕ) :
    (∑ b : GenericProperHighIndex g h k,
      (Fintype.card σ - affineInputRank (g b.val) + k).choose k) ≤
    Fintype.card (GenericProperHighIndex g h k) *
      (Fintype.card σ - (h*(k+1)+1) + k).choose k := by
  calc
    _ ≤ ∑ _b : GenericProperHighIndex g h k, (Fintype.card σ - (h*(k+1)+1) + k).choose k := by
      apply Finset.sum_le_sum
      intro b _
      apply Nat.choose_le_choose k
      apply Nat.add_le_add_right
      exact Nat.sub_le_sub_left (Nat.succ_le_of_lt b.property.1) _
    _ = _ := by simp

/-- With more required rank than variables there are no proper high blocks. -/
theorem generic_proper_high_isEmpty {σ κ : Type} [Fintype σ] {ι : κ → Type}
    [∀ b, Fintype (ι b)] (g : ∀ b, ι b → AffineInputMap σ) (h k : ℕ)
    (hv : Fintype.card σ < h*(k+1)+1) : IsEmpty (GenericProperHighIndex g h k) := by
  constructor
  intro b
  have hr := affineInputRank_le (g b.val) b.property.2
  have hhigh := b.property.1
  omega

end
end MathResearch
