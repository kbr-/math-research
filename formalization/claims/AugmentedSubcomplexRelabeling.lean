/-
Claim: lem:augmented-subcomplex-relabeling
Source: https://kbr.is-a.dev/math-research/#lean-chessboard-star-intersections
Scope: An injective vertex map exhausting exactly a subcomplex gives an all-degree augmented chain equivalence commuting with differential.
Declarations: MathResearch.ThirdParty.Augmented.subcomplexChainEquiv MathResearch.ThirdParty.Augmented.differential_subcomplexChainEquiv MathResearch.ThirdParty.Augmented.exactAt_subcomplex
-/
import claims.AugmentedCone
namespace MathResearch.ThirdParty.Augmented
noncomputable section
variable {V W : Type*} [Fintype V] [DecidableEq V] [Fintype W] [DecidableEq W]
variable (e : V ↪ W) (K : Complex V) (L : Complex W)
  (hf : ∀ S, S ∈ K.faces ↔ S.map e ∈ L.faces)
  (hr : ∀ T ∈ L.faces, InRange e T)

def pullChain (k : ℕ) (c : chains L k) : chains K k := by
  refine ⟨fun S => c.val (S.map e), ?_⟩
  intro S hS
  apply c.property
  rcases hS with hS | hS
  · exact Or.inl (fun h => hS ((hf S).mpr h))
  · exact Or.inr (by simpa using hS)

omit [Fintype V] [DecidableEq V] [Fintype W] [DecidableEq W] in
include hr in
theorem push_pullChain (k : ℕ) (c : chains L k) :
    push e (pullChain e K L hf k c).val = c.val := by
  funext T
  classical
  by_cases hT : InRange e T
  · simp only [push, hT, ↓reduceIte, pullChain]
    rw [map_preimage e T hT]
  · simp only [push, hT, ↓reduceIte]
    symm
    exact c.property T (Or.inl (fun ht => hT (hr T ht)))

def subcomplexChainEquiv (k : ℕ) : chains K k ≃ₗ[ZMod 2] chains L k where
  toFun := chainMap e K L (fun S hs => (hf S).mp hs) k
  invFun := pullChain e K L hf k
  left_inv := by
    intro c
    apply Subtype.ext
    funext S
    exact push_apply_map e c.val S
  right_inv := by
    intro c
    apply Subtype.ext
    exact push_pullChain e K L hf hr k c
  map_add' := (chainMap e K L (fun S hs => (hf S).mp hs) k).map_add
  map_smul' := (chainMap e K L (fun S hs => (hf S).mp hs) k).map_smul

theorem differential_subcomplexChainEquiv (k : ℕ) (c : chains K (k+1)) :
    differential L k (subcomplexChainEquiv e K L hf hr (k+1) c) =
      subcomplexChainEquiv e K L hf hr k (differential K k c) :=
  differential_chainMap e K L (fun S hs => (hf S).mp hs) k c

include e hf hr in
theorem exactAt_subcomplex (k : ℕ) (hK : ExactAt K k) : ExactAt L k := by
  intro c hc hz
  let d := pullChain e K L hf k ⟨c,hc⟩
  have he : push e d.val = c := push_pullChain e K L hf hr k ⟨c,hc⟩
  have hd : boundary d.val = 0 := by
    apply push_injective e
    rw [← boundary_push, he, hz]
    exact (pushLinear e).map_zero.symm
  obtain ⟨f,hf',hdf⟩ := hK d.val d.property hd
  refine ⟨push e f, push_supported e K L (fun S hs => (hf S).mp hs) (k+1) f hf', ?_⟩
  rw [boundary_push, hdf, he]
end
end MathResearch.ThirdParty.Augmented
