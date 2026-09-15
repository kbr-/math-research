/-
Claim: third-party:linear-annihilator-extension
Source: https://kbr.is-a.dev/math-research/#lean-linear-annihilator-extension
Scope: Standard algebraic linear separation and extension of a functional on U annihilating U∩S to an ambient functional annihilating S, over any field. Uses Mathlib's algebraic basis-extension results; no finite-dimensional assumption is needed.
Declarations: MathResearch.LinearSeparation.normalized_annihilator_iff MathResearch.LinearSeparation.annihilator_extension
-/
import Mathlib.LinearAlgebra.Basis.VectorSpace

namespace MathResearch.LinearSeparation
noncomputable section
variable {K M : Type*} [Field K] [AddCommGroup M] [Module K M]

theorem normalized_annihilator_iff (S : Submodule K M) (v : M) :
    (∃ l : M →ₗ[K] K, l v = 1 ∧ ∀ x ∈ S, l x = 0) ↔ v ∉ S := by
  constructor
  · rintro ⟨l, hl, hS⟩ hv
    exact one_ne_zero (hl.symm.trans (hS v hv))
  · intro hv
    obtain ⟨l, hS, hl⟩ :=
      LinearMap.exists_extend_of_notMem (0 : S →ₗ[K] K) hv 1
    refine ⟨l, hl, ?_⟩
    intro x hx
    have h := LinearMap.congr_fun hS ⟨x, hx⟩
    exact h

theorem annihilator_extension (U S : Submodule K M) (l : U →ₗ[K] K)
    (hcompat : ∀ x : U, (x : M) ∈ S → l x = 0) :
    ∃ L : M →ₗ[K] K, (∀ x : U, L x = l x) ∧ ∀ x ∈ S, L x = 0 := by
  let f : M →ₗ.[K] K := ⟨U, l⟩
  let g : M →ₗ.[K] K := ⟨S, 0⟩
  have hc : ∀ (x : f.domain) (y : g.domain), (x : M) = y → f x = g y := by
    intro x y hxy
    apply hcompat x
    exact hxy ▸ y.property
  let h := f.sup g hc
  obtain ⟨L, hL⟩ := h.toFun.exists_extend
  refine ⟨L, ?_, ?_⟩
  · intro x
    let z : ↥(U ⊔ S) := ⟨x, (le_sup_left : U ≤ U ⊔ S) x.property⟩
    have hz : (x : M) + ((0 : S) : M) = (z : M) := by simp [z]
    have hh := LinearPMap.sup_apply hc x (0 : S) z hz
    have he := LinearMap.congr_fun hL z
    change L (x : M) = h z at he
    exact he.trans (by simpa [f, g, h] using hh)
  · intro x hx
    let y : S := ⟨x, hx⟩
    let z : ↥(U ⊔ S) := ⟨x, (le_sup_right : S ≤ U ⊔ S) hx⟩
    have hz : ((0 : U) : M) + (y : M) = (z : M) := by simp [y, z]
    have hh := LinearPMap.sup_apply hc (0 : U) y z hz
    have he := LinearMap.congr_fun hL z
    change L x = h z at he
    exact he.trans (by simpa [f, g, h] using hh)

end
end MathResearch.LinearSeparation
