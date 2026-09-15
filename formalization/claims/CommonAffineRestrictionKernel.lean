/-
Claim: lem:common-affine-restriction-kernel
Source: https://kbr.is-a.dev/math-research/#lean-common-affine-restriction-kernel
Scope: Concrete bit-variable common ordinary kernel and literal degree-(k-1) witnesses at rank>3ell(k+1), with square-condition and original ceil-sqrt-log parameters; unit-span blocks handled separately.
Declarations: MathResearch.common_affine_kernel_of_square MathResearch.common_affine_restriction_kernel MathResearch.common_affine_kernel_inventory MathResearch.proper_high_count_le_proper_count
-/
import claims.AffineBlockRestriction
import claims.RestrictionKernelBounds
import claims.RowLinearPolynomialSpace

namespace MathResearch
noncomputable section
open MvPolynomial Module
open scoped BigOperators

private theorem nonzero_joint_kernel {K V J : Type} [Field K] [AddCommGroup V] [Module K V]
    [FiniteDimensional K V] [Fintype J] {W : J → Type}
    [∀ j, AddCommGroup (W j)] [∀ j, Module K (W j)]
    (L : ∀ j, V →ₗ[K] W j)
    (h : (∑ j, Module.finrank K (L j).range) < Module.finrank K V) :
    ∃ v : V, v ≠ 0 ∧ ∀ j, L j v = 0 := by
  classical
  let T : V →ₗ[K] (∀ j, (L j).range) := LinearMap.pi (fun j => (L j).rangeRestrict)
  have hn : ¬ Function.Injective T := by
    intro hi
    have hd := LinearMap.finrank_le_finrank_of_injective hi
    rw [Module.finrank_pi_fintype] at hd
    omega
  obtain ⟨v,w,he,hne⟩ := Function.not_injective_iff.mp hn
  refine ⟨v-w,sub_ne_zero.mpr hne,?_⟩
  have hz : T (v-w) = 0 := by rw [map_sub,he,sub_self]
  intro j
  have hh := congrArg Subtype.val (congrFun hz j)
  exact hh

abbrev ProperHighIndex {κ : Type} {ι : κ → Type} [∀ b, Fintype (ι b)] {m ℓ : ℕ}
    (g : ∀ b, ι b → AffineInputMap (Fin m × Fin ℓ)) (k : ℕ) :=
  {b : κ // 3*ℓ*(k+1) < affineInputRank (g b) ∧
    (1 : MvPolynomial (Fin m × Fin ℓ) (ZMod 2)) ∉
      Submodule.span (ZMod 2) (Set.range (fun i => finiteAffinePolynomial (g b i)))}

abbrev ProperBlockIndex {κ : Type} {ι : κ → Type} [∀ b, Fintype (ι b)] {m ℓ : ℕ}
    (g : ∀ b, ι b → AffineInputMap (Fin m × Fin ℓ)) :=
  {b : κ // 0 < affineInputRank (g b) ∧
    (1 : MvPolynomial (Fin m × Fin ℓ) (ZMod 2)) ∉
      Submodule.span (ZMod 2) (Set.range (fun i => finiteAffinePolynomial (g b i)))}

theorem proper_high_count_le_proper_count {κ : Type} [Fintype κ] {ι : κ → Type}
    [∀ b, Fintype (ι b)] {m ℓ : ℕ}
    (g : ∀ b, ι b → AffineInputMap (Fin m × Fin ℓ)) (k : ℕ) :
    Nat.card (ProperHighIndex g k) ≤ Nat.card (ProperBlockIndex g) := by
  classical
  let e : ProperHighIndex g k ↪ ProperBlockIndex g :=
    { toFun := fun b => ⟨b.val, Nat.lt_of_le_of_lt (Nat.zero_le _) b.property.1, b.property.2⟩
      inj' := fun _ _ h => Subtype.ext (congrArg (fun b : ProperBlockIndex g => b.val) h) }
  simpa only [Nat.card_eq_fintype_card] using Fintype.card_le_of_embedding e

theorem common_affine_kernel_of_square {κ : Type} [Fintype κ] {ι : κ → Type}
    [∀ b, Fintype (ι b)] (m ℓ M k : ℕ) (hm : 0 < m) (hℓ : 1 ≤ ℓ) (hM : 1 ≤ M)
    (_hkpos : 1 ≤ k) (hk : k ≤ m) (hsq : (m:ℝ)*Real.log (4*(M:ℝ)) ≤ (k:ℝ)^2)
    (g : ∀ b, ι b → AffineInputMap (Fin m × Fin ℓ))
    (hcount : Nat.card (ProperHighIndex g k) ≤ M) :
    ∃ f : MvPolynomial (Fin m × Fin ℓ) (ZMod 2),
      f ∈ rowLinearSpace (ZMod 2) m ℓ k ∧ f ≠ 0 ∧
      ∀ b, 3*ℓ*(k+1) < affineInputRank (g b) →
        (1 : MvPolynomial (Fin m × Fin ℓ) (ZMod 2)) ∈
          Submodule.span (ZMod 2) (Set.range (fun i => finiteAffinePolynomial (g b i))) ∨
        ∃ a : ι b → MvPolynomial (Fin m × Fin ℓ) (ZMod 2),
          (∀ i, (a i).totalDegree ≤ k-1) ∧ f = ∑ i, a i*finiteAffinePolynomial (g b i) := by
  classical
  let H := ProperHighIndex g k
  let U := rowLinearSpace (ZMod 2) m ℓ k
  let R : ∀ b : H, BlockRestrictionData (g b.val) :=
    fun b => Classical.choice (blockRestrictionData_exists (g b.val) b.property.2)
  let L (b : H) : U →ₗ[ZMod 2]
      MvPolynomial (CoordinateFreeIndex (R b).embedding) (ZMod 2) :=
    (affineRestriction (R b).embedding (R b).coordinates).toLinearMap.comp U.subtype
  have hbase : 0 < m.choose k * ℓ^k := Nat.mul_pos (Nat.choose_pos hk) (Nat.pow_pos (by omega))
  have hdim : m.choose k * ℓ^k ≤ Module.finrank (ZMod 2) U := by
    rw [rowLinearSpace_finrank]
    exact Finset.single_le_sum (f := fun j : ℕ => m.choose j * ℓ^j) (fun _ _ => Nat.zero_le _) (Finset.mem_range.mpr (Nat.lt_succ_self k))
  have hsum : (∑ b : H, Module.finrank (ZMod 2) (L b).range) < Module.finrank (ZMod 2) U := by
    by_cases hH : Nonempty H
    · obtain ⟨b0⟩ := hH
      have hr0 := affineInputRank_le (g b0.val) b0.property.2
      have hhigh := b0.property.1
      have hr : 3*ℓ*(k+1)+1 ≤ m*ℓ := by
        simp only [Fintype.card_prod,Fintype.card_fin] at hr0
        omega
      let Q := (m*ℓ-(3*ℓ*(k+1)+1)+k).choose k
      have himage (b : H) : Module.finrank (ZMod 2) (L b).range ≤ Q := by
        have he : (L b).range = U.map (affineRestriction (R b).embedding (R b).coordinates).toLinearMap := by
          ext p
          constructor
          · rintro ⟨a,rfl⟩; exact ⟨a.val,a.property,rfl⟩
          · rintro ⟨a,ha,rfl⟩; exact ⟨⟨a,ha⟩,rfl⟩
        rw [he]
        have hb := affineRestriction_image_finrank_le (R b).embedding (R b).coordinates U k
          (fun p hp => rowLinearSpace_totalDegree_le hp)
        simp only [Fintype.card_prod,Fintype.card_fin] at hb
        apply hb.trans
        apply Nat.choose_le_choose k
        apply Nat.add_le_add_right
        exact Nat.sub_le_sub_left (Nat.succ_le_of_lt b.property.1) (m*ℓ)
      have hsumN : (∑ b : H, Module.finrank (ZMod 2) (L b).range) ≤ M*Q := by
        calc
          _ ≤ ∑ _b : H, Q := Finset.sum_le_sum (fun b _ => himage b)
          _ = Fintype.card H * Q := by simp
          _ ≤ M*Q := Nat.mul_le_mul_right Q (by simpa only [Nat.card_eq_fintype_card] using hcount)
      have hn := kernel_dimension_bound_of_square m ℓ M k hm hℓ hM hsq hk hr
      have hsR : ((∑ b : H, Module.finrank (ZMod 2) (L b).range) : ℝ) ≤ (M:ℝ)*(Q:ℝ) := by exact_mod_cast hsumN
      have hbR : (0:ℝ) < (m.choose k : ℝ)*(ℓ:ℝ)^k := by exact_mod_cast hbase
      have hdR : (m.choose k : ℝ)*(ℓ:ℝ)^k ≤ (Module.finrank (ZMod 2) U : ℝ) := by exact_mod_cast hdim
      have ht : ((∑ b : H, Module.finrank (ZMod 2) (L b).range) : ℝ) < (Module.finrank (ZMod 2) U : ℝ) := by
        change (M:ℝ)*(Q:ℝ) ≤ _ at hn
        nlinarith
      exact_mod_cast ht
    · let _ : IsEmpty H := not_nonempty_iff.mp hH
      simpa using hbase.trans_le hdim
  obtain ⟨p,hp,hzero⟩ := nonzero_joint_kernel L hsum
  refine ⟨p.val,p.property,?_,?_⟩
  · intro hz
    exact hp (Subtype.ext hz)
  · intro b hb
    by_cases hu : (1 : MvPolynomial (Fin m × Fin ℓ) (ZMod 2)) ∈
        Submodule.span (ZMod 2) (Set.range (fun i => finiteAffinePolynomial (g b i)))
    · exact Or.inl hu
    · let b' : H := ⟨b,hb,hu⟩
      exact Or.inr ((R b').literal p.val k (rowLinearSpace_totalDegree_le p.property) (hzero b'))

theorem common_affine_restriction_kernel {κ : Type} [Fintype κ] {ι : κ → Type}
    [∀ b, Fintype (ι b)] (m ℓ M : ℕ) (hm : 0 < m) (hℓ : 1 ≤ ℓ) (hM : 1 ≤ M)
    (hk : kernelDegree m M ≤ m)
    (g : ∀ b, ι b → AffineInputMap (Fin m × Fin ℓ))
    (hcount : Nat.card (ProperHighIndex g (kernelDegree m M)) ≤ M) :
    ∃ f : MvPolynomial (Fin m × Fin ℓ) (ZMod 2),
      f ∈ rowLinearSpace (ZMod 2) m ℓ (kernelDegree m M) ∧ f ≠ 0 ∧
      ∀ b, 3*ℓ*(kernelDegree m M+1) < affineInputRank (g b) →
        (1 : MvPolynomial (Fin m × Fin ℓ) (ZMod 2)) ∈
          Submodule.span (ZMod 2) (Set.range (fun i => finiteAffinePolynomial (g b i))) ∨
        ∃ a : ι b → MvPolynomial (Fin m × Fin ℓ) (ZMod 2),
          (∀ i, (a i).totalDegree ≤ kernelDegree m M-1) ∧ f = ∑ i, a i*finiteAffinePolynomial (g b i) :=
  common_affine_kernel_of_square m ℓ M _ hm hℓ hM (kernelDegree_pos m M hm hM) hk
    (kernel_ceil_square m M hm hM) g hcount

theorem common_affine_kernel_inventory {κ : Type} [Fintype κ] {ι : κ → Type}
    [∀ b, Fintype (ι b)] (m ℓ M k : ℕ) (hm : 0 < m) (hℓ : 1 ≤ ℓ) (hM : 1 ≤ M)
    (hkpos : 1 ≤ k) (hk : k ≤ m) (hsq : (m:ℝ)*Real.log (4*(M:ℝ)) ≤ (k:ℝ)^2)
    (g : ∀ b, ι b → AffineInputMap (Fin m × Fin ℓ)) (hcount : Fintype.card κ ≤ M) :
    ∃ f : MvPolynomial (Fin m × Fin ℓ) (ZMod 2),
      f ∈ rowLinearSpace (ZMod 2) m ℓ k ∧ f ≠ 0 ∧
      ∀ b, 3*ℓ*(k+1) < affineInputRank (g b) →
        (1 : MvPolynomial (Fin m × Fin ℓ) (ZMod 2)) ∈
          Submodule.span (ZMod 2) (Set.range (fun i => finiteAffinePolynomial (g b i))) ∨
        ∃ a : ι b → MvPolynomial (Fin m × Fin ℓ) (ZMod 2),
          (∀ i, (a i).totalDegree ≤ k-1) ∧ f = ∑ i, a i*finiteAffinePolynomial (g b i) := by
  apply common_affine_kernel_of_square m ℓ M k hm hℓ hM hkpos hk hsq g
  classical
  rw [Nat.card_eq_fintype_card]
  exact (Fintype.card_subtype_le _).trans hcount

end
end MathResearch
