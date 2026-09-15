/-
Claim: third-party:BLVZ-chessboard-filling
Source: https://kbr.is-a.dev/math-research/#third-party-chessboard-filling-interface
Scope: Exact finite F₂ reduced-cycle filling interface H for s≥2 and N≥2s-1. Definitions only in this module; ChessboardFillingProof.lean proves H.
Kind: interface
Declarations: MathResearch.ThirdParty.ChessboardFilling
-/
import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Fintype.Powerset
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

namespace MathResearch.ThirdParty
noncomputable section
open scoped BigOperators

/-- A face with exactly k nonattacking rooks on an s by N board.
The empty face (k = 0) is included for reduced chains. -/
abbrev ChessboardFace (s N k : ℕ) :=
  {M : Finset (Fin s × Fin N) //
    M.card = k ∧ Set.InjOn Prod.fst (M : Set (Fin s × Fin N)) ∧
      Set.InjOn Prod.snd (M : Set (Fin s × Fin N))}

instance (s N k : ℕ) : Fintype (ChessboardFace s N k) :=
  Fintype.ofFinite _

/-- k-cell chains have simplicial degree k-1. All face sets are finite,
so ordinary functions and finitely supported coefficient vectors agree. -/
abbrev ChessboardChain (s N k : ℕ) := ChessboardFace s N k → ZMod 2

/-- The augmented simplicial boundary over F₂. For k>0, each codimension-one
subface receives its coefficient once. At k=1 this is the augmentation to
the empty face; the outgoing boundary from the empty face is zero. -/
def chessboardBoundary {s N k : ℕ} (c : ChessboardChain s N k) :
    ChessboardChain s N (k - 1) := by
  classical
  exact fun τ => if k = 0 then 0 else
    ∑ σ : ChessboardFace s N k, if τ.val ⊆ σ.val then c σ else 0

/-- The precise consequence of BLVZ Theorem 1.1 needed for matching moments.
This module defines the proposition; ChessboardFillingProof.lean proves it.
Reference: Björner, Lovász, Vrećica, Živaljević (1994),
Chessboard complexes and matching complexes, DOI 10.1112/jlms/49.1.25. -/
def ChessboardFilling : Prop :=
  ∀ (s N : ℕ), 2 ≤ s → 2 * s - 1 ≤ N →
    ∀ c : ChessboardChain s N (s - 1), chessboardBoundary c = 0 →
      ∃ b : ChessboardChain s N s, chessboardBoundary b = c

end
end MathResearch.ThirdParty
