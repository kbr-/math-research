/-
Claim: third-party:finite-augmented-chain-api
Source: https://kbr.is-a.dev/math-research/#lean-finite-augmented-chain-api
Scope: Finite F₂ augmented chains on downward-closed face families, graded support, boundary linearity and augmentation, including the empty face.
Declarations: MathResearch.ThirdParty.Augmented.boundary_add MathResearch.ThirdParty.Augmented.boundary_smul MathResearch.ThirdParty.Augmented.boundary_supported MathResearch.ThirdParty.Augmented.boundary_empty MathResearch.ThirdParty.Augmented.faceChainEquiv MathResearch.ThirdParty.Augmented.chessboardComplex MathResearch.ThirdParty.Augmented.chessboardChainEquiv MathResearch.ThirdParty.Augmented.differential
-/
import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Fintype.Powerset
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.LinearAlgebra.Pi
import «third-party-claims».ChessboardFilling

namespace MathResearch.ThirdParty.Augmented
noncomputable section
open scoped BigOperators

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Finite abstract complex including its augmentation face. -/
structure Complex (V : Type*) where
  faces : Set (Finset V)
  empty_mem : ∅ ∈ faces
  downward : ∀ {s t}, s ⊆ t → t ∈ faces → s ∈ faces

abbrev Coeff (V : Type*) := Finset V → ZMod 2

/-- k is cell count, not simplicial dimension. -/
def Supported (K : Complex V) (k : ℕ) (c : Coeff V) : Prop :=
  ∀ s, s ∉ K.faces ∨ s.card ≠ k → c s = 0

/-- Ambient augmented boundary, simultaneously in all degrees. -/
def boundary (c : Coeff V) : Coeff V :=
  fun s => ∑ v : V, if v ∈ s then 0 else c (insert v s)

theorem boundary_add (c d : Coeff V) : boundary (c + d) = boundary c + boundary d := by
  funext s
  simp only [boundary, Pi.add_apply]
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro v _
  split_ifs <;> simp

theorem boundary_smul (a : ZMod 2) (c : Coeff V) :
    boundary (a • c) = a • boundary c := by
  funext s
  simp only [boundary, Pi.smul_apply, smul_eq_mul, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro v _
  split_ifs <;> simp

@[simp] theorem boundary_zero : boundary (0 : Coeff V) = 0 := by
  funext s
  simp [boundary]

def boundaryLinear : Coeff V →ₗ[ZMod 2] Coeff V where
  toFun := boundary
  map_add' := boundary_add
  map_smul' := boundary_smul

theorem boundary_supported (K : Complex V) (k : ℕ) (c : Coeff V)
    (hc : Supported K (k + 1) c) : Supported K k (boundary c) := by
  intro s hs
  apply Finset.sum_eq_zero
  intro v _
  by_cases hv : v ∈ s
  · simp [hv]
  · simp only [hv, ↓reduceIte]
    apply hc
    rcases hs with hs | hs
    · exact Or.inl (fun h => hs (K.downward (Finset.subset_insert v s) h))
    · exact Or.inr (by simpa [Finset.card_insert_of_notMem hv] using hs)

theorem boundary_empty (K : Complex V) (c : Coeff V)
    (hc : Supported K 0 c) : boundary c = 0 := by
  funext s
  apply Finset.sum_eq_zero
  intro v _
  by_cases hv : v ∈ s
  · simp [hv]
  · simp only [hv, ↓reduceIte]
    apply hc
    right
    simp [Finset.card_insert_of_notMem hv]

/-- Coefficient spaces are finite; support is a linear condition. -/
def chains (K : Complex V) (k : ℕ) : Submodule (ZMod 2) (Coeff V) where
  carrier := {c | Supported K k c}
  zero_mem' := by intro s _; rfl
  add_mem' := by intro c d hc hd s hs; simp [hc s hs, hd s hs]
  smul_mem' := by intro a c hc s hs; simp [hc s hs]

def differential (K : Complex V) (k : ℕ) :
    chains K (k + 1) →ₗ[ZMod 2] chains K k :=
  boundaryLinear.restrict (fun c hc => boundary_supported K k c hc)

abbrev Face (K : Complex V) (k : ℕ) := {s : Finset V // s ∈ K.faces ∧ s.card = k}

def extend (K : Complex V) (k : ℕ) (c : Face K k → ZMod 2) : chains K k := by
  classical
  refine ⟨fun s => if h : s ∈ K.faces ∧ s.card = k then c ⟨s, h⟩ else 0, ?_⟩
  intro s hs
  dsimp only
  split_ifs with h
  · exact False.elim (hs.elim (fun hn => hn h.1) (fun hn => hn h.2))
  · rfl

/-- Extension by zero identifies exact-face coordinates with supported chains. -/
def faceChainEquiv (K : Complex V) (k : ℕ) :
    (Face K k → ZMod 2) ≃ₗ[ZMod 2] chains K k where
  toFun := extend K k
  invFun := fun c s => c.val s.val
  left_inv := by intro c; funext s; simp [extend, s.property]
  right_inv := by
    intro c
    apply Subtype.ext
    funext s
    classical
    simp only [extend]
    split_ifs with hs
    · rfl
    · symm
      apply c.property
      simpa only [not_and_or, not_not] using hs
  map_add' := by
    intro c d
    apply Subtype.ext
    funext s
    classical
    by_cases hs : s ∈ K.faces ∧ s.card = k <;> simp [extend, hs]
  map_smul' := by
    intro a c
    apply Subtype.ext
    funext s
    classical
    by_cases hs : s ∈ K.faces ∧ s.card = k <;> simp [extend, hs]

/-- The downward-closed family of nonattacking rook sets, including ∅. -/
def chessboardComplex (s N : ℕ) : Complex (Fin s × Fin N) where
  faces := {M | Set.InjOn Prod.fst (M : Set (Fin s × Fin N)) ∧ Set.InjOn Prod.snd (M : Set (Fin s × Fin N))}
  empty_mem := by simp
  downward := by
    intro A B h hB
    exact ⟨hB.1.mono h, hB.2.mono h⟩

def chessboardFaceEquiv (s N k : ℕ) :
    ChessboardFace s N k ≃ Face (chessboardComplex s N) k where
  toFun := fun M => ⟨M.val, ⟨M.property.2, M.property.1⟩⟩
  invFun := fun M => ⟨M.val, ⟨M.property.2, M.property.1⟩⟩
  left_inv := by intro M; rfl
  right_inv := by intro M; rfl

/-- The original chessboard coefficient space and generic supported space agree.
Boundary compatibility is a separate theorem, not a consequence of this equivalence alone. -/
def chessboardChainEquiv (s N k : ℕ) :
    ChessboardChain s N k ≃ₗ[ZMod 2] chains (chessboardComplex s N) k :=
  (LinearEquiv.piCongrLeft (ZMod 2) (fun _ => ZMod 2)
    (chessboardFaceEquiv s N k)).trans (faceChainEquiv (chessboardComplex s N) k)

end
end MathResearch.ThirdParty.Augmented
