/-
Claim: third-party:simplex-boundary-acyclicity
Source: https://kbr.is-a.dev/math-research/#lean-simplex-boundary-acyclicity
Scope: The boundary of a nonempty finite simplex is augmented F₂-exact in cell count k whenever k+1 is strictly less than the number of vertices, excluding its top reduced homology.
Declarations: MathResearch.ThirdParty.Augmented.simplex_cone MathResearch.ThirdParty.Augmented.simplexBoundary_exact MathResearch.ThirdParty.Augmented.simplexBoundary_acyclic
-/
import claims.AugmentedCone

namespace MathResearch.ThirdParty.Augmented
noncomputable section
variable {V : Type*} [Fintype V] [DecidableEq V]

def simplex (T : Finset V) : Complex V where
  faces := {s | s ⊆ T}
  empty_mem := Finset.empty_subset T
  downward := fun h hT => h.trans hT

def simplexBoundary (T : Finset V) (hT : T.Nonempty) : Complex V where
  faces := {s | s ⊂ T}
  empty_mem := Finset.empty_ssubset.mpr hT
  downward := fun h hT => lt_of_le_of_lt h hT

omit [Fintype V] in
theorem simplex_cone (T : Finset V) (v : V) (hv : v ∈ T) :
    IsCone (simplex T) v := by
  intro s hs
  exact Finset.insert_subset hv hs

theorem simplexBoundary_exact (T : Finset V) (hT : T.Nonempty) (k : ℕ)
    (hk : k+1 < T.card) : ExactAt (simplexBoundary T hT) k := by
  intro c hc hz
  obtain ⟨v, hv⟩ := hT
  have hs : Supported (simplex T) k c := by
    intro s h
    apply hc
    rcases h with h | h
    · left
      intro hs
      apply h
      exact (Finset.ssubset_iff_subset_ne.mp hs).1
    · exact Or.inr h
  obtain ⟨b, hb, hbc⟩ := cone_exact (simplex T) v (simplex_cone T v hv) k c hs hz
  refine ⟨b, ?_, hbc⟩
  intro s h
  apply hb
  rcases h with h | h
  · by_cases hsub : s ⊆ T
    · right
      intro hcard
      apply h
      exact Finset.ssubset_iff_subset_ne.mpr ⟨hsub, by
        intro he
        have : T.card = k+1 := he ▸ hcard
        omega⟩
    · exact Or.inl hsub
  · exact Or.inr h

theorem simplexBoundary_acyclic (T : Finset V) (hT : T.Nonempty) (n : ℕ)
    (hn : n < T.card) : AcyclicThrough (simplexBoundary T hT) n := by
  intro k hk
  apply simplexBoundary_exact T hT k
  omega

end
end MathResearch.ThirdParty.Augmented
