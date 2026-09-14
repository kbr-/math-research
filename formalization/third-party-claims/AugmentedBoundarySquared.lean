/-
Claim: third-party:augmented-boundary-squared-zero
Source: https://kbr.is-a.dev/math-research/#lean-augmented-boundary-squared-zero
Scope: The ambient finite F₂ insertion boundary squares to zero; hence so does the supported graded differential, including edges to augmentation and the outgoing zero boundary.
Declarations: MathResearch.ThirdParty.Augmented.boundary_boundary MathResearch.ThirdParty.Augmented.differential_squared
-/
import claims.AugmentedChains

namespace MathResearch.ThirdParty.Augmented
noncomputable section
open scoped BigOperators
variable {V : Type*} [Fintype V] [DecidableEq V]

theorem boundary_boundary (c : Coeff V) : boundary (boundary c) = 0 := by
  classical
  funext s
  let f : V × V → ZMod 2 := fun p =>
    if p.1 ∈ s ∨ p.2 ∈ s ∨ p.1 = p.2 then 0 else c (insert p.2 (insert p.1 s))
  have heq : boundary (boundary c) s = ∑ p : V × V, f p := by
    rw [Fintype.sum_prod_type]
    apply Finset.sum_congr rfl
    intro v _
    by_cases hv : v ∈ s
    · simp [f, hv]
    · simp only [boundary, hv, ↓reduceIte]
      apply Finset.sum_congr rfl
      intro w _
      by_cases hw : w ∈ s <;> by_cases hvw : v = w <;>
        simp_all [f, Finset.mem_insert, eq_comm]
  rw [heq]
  apply Finset.sum_involution (fun p _ => (p.2, p.1))
  · intro p _
    by_cases hp : p.1 ∈ s ∨ p.2 ∈ s ∨ p.1 = p.2
    · have hp' : p.2 ∈ s ∨ p.1 ∈ s ∨ p.2 = p.1 := by tauto
      simp [f, hp, hp']
    · have hp' : ¬ (p.2 ∈ s ∨ p.1 ∈ s ∨ p.2 = p.1) := by tauto
      simp only [f, hp, hp', ↓reduceIte, Finset.insert_comm]
      exact ZModModule.add_self _
  · intro p _ hp he
    have : p.1 = p.2 := (congrArg Prod.snd he)
    exact hp (by simp [f, this])
  · intro p _
    exact Finset.mem_univ _
  · intro p _
    rfl

theorem differential_squared (K : Complex V) (k : ℕ) (c : chains K (k + 1 + 1)) :
    differential K k (differential K (k + 1) c) = 0 := by
  apply Subtype.ext
  exact boundary_boundary c.val

end
end MathResearch.ThirdParty.Augmented
