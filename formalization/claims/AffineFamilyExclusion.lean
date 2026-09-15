/-
Claim: audit:ordinary-restriction-affine-family
Source: https://kbr.is-a.dev/math-research/#lean-affine-family-exclusion
Scope: Finite-parameter binary affine-family exclusion from the actual kernel, weighted removal, and cube separator. Includes polynomial proper inventory and arbitrary fixed polylogarithmic degree, by a uniform parameter argument.
Declarations: MathResearch.affine_family_exclusion_of_square MathResearch.affine_family_exclusion MathResearch.affine_family_polylog_exclusion
-/
import claims.AffineParameterBounds
import claims.CommonAffineRestrictionKernel
import claims.AffineFamilyRemovalWithUnits
import claims.CubeResidualDualSeparation

namespace MathResearch
noncomputable section
open MvPolynomial PolynomialCalculus

 theorem affine_family_exclusion_of_square {κ : Type} [Fintype κ] {ι : κ → Type}
    [∀ b, Fintype (ι b)] (m ℓ M k D : ℕ)
    (hm : 0 < m) (hℓ : 2 ≤ ℓ) (hM : 1 ≤ M) (hkpos : 1 ≤ k) (hk : k ≤ m)
    (hsq : (m:ℝ)*Real.log (4*(M:ℝ)) ≤ (k:ℝ)^2)
    (hD : 2*(3*ℓ)+1 ≤ D) (hpack : 4*(k-1) < 2^ℓ)
    (hB : 2*(k*(D+1))-1 ≤ 2^ℓ)
    (g : ∀ b, ι b → AffineInputMap (Fin m × Fin ℓ))
    (hcount : Nat.card (ProperHighIndex g k) ≤ M) :
    ¬ Derives (ensFamilySystem (fun b i => finiteAffinePolynomial (g b i)) (3*ℓ)
      (compactBitBase m ℓ)) D 1 := by
  intro href
  obtain ⟨f,hf,hne,hw⟩ := common_affine_kernel_of_square m ℓ M k hm (by omega)
    hM hkpos hk hsq g hcount
  have hp := affine_family_removal_with_units
    (fun b i => finiteAffinePolynomial (g b i)) (fun b i => finiteAffinePolynomial_degree (g b i))
    (3*ℓ) k D (by omega) hkpos hD (compactBitBase m ℓ)
    (fun _ h => Or.inl h) f (rowLinearSpace_totalDegree_le hf) hw href
  obtain ⟨_,_,_,_,_,_,hn⟩ := cube_residual_dual_separation m ℓ k (k*(D+1)) hℓ hkpos
    (by nlinarith) hpack hB f hf hne
  exact hn hp

 theorem affine_family_exclusion {κ : Type} [Fintype κ] {ι : κ → Type}
    [∀ b, Fintype (ι b)] (m ℓ M D : ℕ)
    (hm : 0 < m) (hℓ : 2 ≤ ℓ) (hM : 1 ≤ M)
    (hk : kernelDegree m M ≤ m) (hD : 2*(3*ℓ)+1 ≤ D)
    (hpack : 4*(kernelDegree m M-1) < 2^ℓ)
    (hB : 2*(kernelDegree m M*(D+1))-1 ≤ 2^ℓ)
    (g : ∀ b, ι b → AffineInputMap (Fin m × Fin ℓ))
    (hcount : Nat.card (ProperBlockIndex g) ≤ M) :
    ¬ Derives (ensFamilySystem (fun b i => finiteAffinePolynomial (g b i)) (3*ℓ)
      (compactBitBase m ℓ)) D 1 :=
  affine_family_exclusion_of_square m ℓ M _ D hm hℓ hM (kernelDegree_pos m M hm hM)
    hk (kernel_ceil_square m M hm hM) hD hpack hB g
    ((proper_high_count_le_proper_count g _).trans hcount)

/-- Polynomial proper-block inventory and any polynomial degree bound in bit length. -/
theorem affine_family_polylog_exclusion (a A d : ℕ) :
    ∀ᶠ ℓ : ℕ in Filter.atTop, ∀ {κ : Type} [Fintype κ] {ι : κ → Type}
      [∀ b, Fintype (ι b)]
      (g : ∀ b, ι b → AffineInputMap (Fin (2^ℓ+1) × Fin ℓ)),
      Nat.card (ProperBlockIndex g) ≤ A*2^(a*ℓ)+1 →
      ∀ D : ℕ, D ≤ A*(ℓ+1)^d →
      ¬ Derives (ensFamilySystem (fun b i => finiteAffinePolynomial (g b i)) (3*ℓ)
        (compactBitBase (2^ℓ+1) ℓ)) D 1 := by
  filter_upwards [eventually_affine_parameters a (A+7) (d+1)] with ℓ hp
  intro κ _ ι _ g hcount D hD href
  obtain ⟨hℓ,hkpos,hk,hsq,hpack,hB⟩ := hp
  have ht : 1 ≤ ℓ+1 := by omega
  have hpow : (ℓ+1)^d ≤ (ℓ+1)^(d+1) := pow_le_pow_right₀ ht (Nat.le_succ d)
  have htbig : ℓ+1 ≤ (ℓ+1)^(d+1) := le_self_pow₀ ht (by omega)
  have hcap : max D (2*(3*ℓ)+1) ≤ (A+7)*(ℓ+1)^(d+1) := by
    apply max_le <;> nlinarith
  have hcount' : Nat.card (ProperHighIndex g (uniformKernel ℓ)) ≤ (A+7)*2^(a*ℓ)+1 :=
    (proper_high_count_le_proper_count g _).trans (hcount.trans (Nat.add_le_add_right (Nat.mul_le_mul_right _ (by omega : A ≤ A+7)) 1))
  have hB' : 2*(uniformKernel ℓ*(max D (2*(3*ℓ)+1)+1))-1 ≤ 2^ℓ := by
    exact (Nat.sub_le_sub_right (Nat.mul_le_mul_left 2
      (Nat.mul_le_mul_left _ (Nat.add_le_add_right hcap 1))) 1).trans hB
  exact affine_family_exclusion_of_square (2^ℓ+1) ℓ ((A+7)*2^(a*ℓ)+1) (uniformKernel ℓ)
    (max D (2*(3*ℓ)+1)) (by omega) hℓ (by omega) hkpos hk hsq
    (le_max_right _ _) hpack hB' g hcount'
    (href.mono (fun _ h => h) (le_max_left _ _))
end
end MathResearch
