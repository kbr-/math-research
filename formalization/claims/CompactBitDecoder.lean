/-
Claim: lem:compact-bit-decoder-coordinates
Source: https://kbr.is-a.dev/math-research/#lean-compact-bit-decoder-coordinates
Scope: Explicit ordinary affine bit-to-unary decoder on arbitrary m rows and 2^ℓ labels, with a linear polynomial left inverse, injectivity, and exact ordinary total-degree preservation.
Declarations: MathResearch.PolynomialCalculus.decoderInput_degree MathResearch.PolynomialCalculus.compactDecoder_left_inverse MathResearch.PolynomialCalculus.compactDecoder_injective MathResearch.PolynomialCalculus.compactDecoder_degree
-/
import claims.PolynomialCalculusSubstitution
import Mathlib.Data.Fintype.EquivFin
import Mathlib.Tactic.Ring

namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial
open scoped BigOperators

abbrev BitLabel (ℓ : ℕ) := Fin ℓ → ZMod 2
def bitLabelEquiv (ℓ : ℕ) : Fin (2^ℓ) ≃ BitLabel ℓ :=
  (Fintype.equivFinOfCardEq (by simp : Fintype.card (BitLabel ℓ) = 2^ℓ)).symm

def decoderInput (m ℓ : ℕ) (v : Fin m × Fin ℓ) : Poly (ZMod 2) (Fin m × Fin (2^ℓ)) :=
  ∑ j : Fin (2^ℓ), if bitLabelEquiv ℓ j v.2 = 1 then X (v.1,j) else 0

def compactDecoder (m ℓ : ℕ) :
    Poly (ZMod 2) (Fin m × Fin ℓ) →ₐ[ZMod 2] Poly (ZMod 2) (Fin m × Fin (2^ℓ)) :=
  aeval (decoderInput m ℓ)

def decoderInverseInput (m ℓ : ℕ) (v : Fin m × Fin (2^ℓ)) : Poly (ZMod 2) (Fin m × Fin ℓ) :=
  ∑ t : Fin ℓ, if v.2 = (bitLabelEquiv ℓ).symm (Pi.single t 1) then X (v.1,t) else 0

theorem decoderInput_degree (m ℓ : ℕ) (v : Fin m × Fin ℓ) :
    (decoderInput m ℓ v).totalDegree ≤ 1 := by
  apply totalDegree_finsetSum_le
  intro j _
  split_ifs <;> simp

private theorem decoderInverseInput_degree (m ℓ : ℕ) (v : Fin m × Fin (2^ℓ)) :
    (decoderInverseInput m ℓ v).totalDegree ≤ 1 := by
  apply totalDegree_finsetSum_le
  intro j _
  split_ifs <;> simp

private theorem decoder_left_inverse_X (m ℓ : ℕ) (v : Fin m × Fin ℓ) :
    aeval (decoderInverseInput m ℓ) (decoderInput m ℓ v) = X v := by
  classical
  simp only [decoderInput, map_sum, apply_ite, aeval_X, map_zero, decoderInverseInput]
  have he (j : Fin (2^ℓ)) :
      (if bitLabelEquiv ℓ j v.2 = 1 then
        ∑ t : Fin ℓ, if j = (bitLabelEquiv ℓ).symm (Pi.single t 1) then
          (X (v.1,t) : Poly (ZMod 2) (Fin m × Fin ℓ)) else 0 else 0) =
      ∑ t : Fin ℓ, if j = (bitLabelEquiv ℓ).symm (Pi.single t 1) then
        (if bitLabelEquiv ℓ j v.2 = 1 then X (v.1,t) else 0) else 0 := by
    by_cases h : bitLabelEquiv ℓ j v.2 = 1 <;> simp [h]
  simp_rw [he]
  rw [Finset.sum_comm]
  simp [Pi.single_apply]

theorem compactDecoder_left_inverse (m ℓ : ℕ) (P : Poly (ZMod 2) (Fin m × Fin ℓ)) :
    aeval (decoderInverseInput m ℓ) (compactDecoder m ℓ P) = P := by
  have he : (aeval (decoderInverseInput m ℓ)).comp (compactDecoder m ℓ) = AlgHom.id _ _ := by
    apply MvPolynomial.algHom_ext
    intro v
    simpa only [AlgHom.comp_apply, compactDecoder, aeval_X, AlgHom.id_apply] using
      decoder_left_inverse_X m ℓ v
  exact AlgHom.congr_fun he P

theorem compactDecoder_injective (m ℓ : ℕ) : Function.Injective (compactDecoder m ℓ) :=
  Function.LeftInverse.injective (compactDecoder_left_inverse m ℓ)

theorem compactDecoder_degree (m ℓ : ℕ) (P : Poly (ZMod 2) (Fin m × Fin ℓ)) :
    (compactDecoder m ℓ P).totalDegree = P.totalDegree := by
  apply Nat.le_antisymm
  · simpa only [Nat.one_mul, compactDecoder] using substitution_degree (decoderInput m ℓ) 1
      (decoderInput_degree m ℓ) P
  · have h := substitution_degree (decoderInverseInput m ℓ) 1
      (decoderInverseInput_degree m ℓ) (compactDecoder m ℓ P)
    simpa only [Nat.one_mul, compactDecoder_left_inverse] using h

end
end MathResearch.PolynomialCalculus
