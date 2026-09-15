/-
Claim: def:finite-complex-cover
Source: https://kbr.is-a.dev/math-research/#lean-chessboard-star-cover
Scope: Finite augmented intersections, covers, and vertex-nonempty nerves; empty faces retained.
Kind: interface
Declarations: MathResearch.ThirdParty.Augmented.intersection MathResearch.ThirdParty.Augmented.nerve MathResearch.ThirdParty.Augmented.Covers
-/
import claims.AugmentedChainMaps
namespace MathResearch.ThirdParty.Augmented
noncomputable section
variable {V I : Type*} [DecidableEq V] [DecidableEq I]
def intersection (L : I → Complex V) (J : Finset I) : Complex V where
  faces := {s | ∀ i ∈ J, s ∈ (L i).faces}
  empty_mem := by intro i _; exact (L i).empty_mem
  downward := by intro s t h ht i hi; exact (L i).downward h (ht i hi)
def nerve (L : I → Complex V) : Complex I where
  faces := {J | J = ∅ ∨ ∃ v, ∀ i ∈ J, {v} ∈ (L i).faces}
  empty_mem := Or.inl rfl
  downward := by
    intro S T h hT
    rcases hT with rfl | ⟨v, hv⟩
    · exact Or.inl (Finset.subset_empty.mp h)
    · exact Or.inr ⟨v, fun i hi => hv i (h hi)⟩
def Covers (K : Complex V) (L : I → Complex V) : Prop :=
  ∀ s ∈ K.faces, ∃ i, s ∈ (L i).faces
end
end MathResearch.ThirdParty.Augmented
