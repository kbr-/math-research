/-
Claim: third-party:chessboard-parameter-arithmetic
Source: https://kbr.is-a.dev/math-research/#chessboard-parameter-arithmetic
Scope: Complete H11 parameter arithmetic for the classical chessboard star-cover proof, including integer degree and empty/one-side boundaries. No homology theorem is asserted.
Declarations: MathResearch.ThirdParty.chessboardNu_symm MathResearch.ThirdParty.chessboardNu_bounds MathResearch.ThirdParty.chessboardNu_pos MathResearch.ThirdParty.chessboardNu_zero MathResearch.ThirdParty.chessboardNu_one MathResearch.ThirdParty.chessboardNu_ordered_bound MathResearch.ThirdParty.chessboardNu_intersection MathResearch.ThirdParty.chessboardNu_intersection_degree MathResearch.ThirdParty.chessboard_induction_decrease MathResearch.ThirdParty.chessboardNu_stable_range MathResearch.ThirdParty.chessboard_cell_degree_iff MathResearch.ThirdParty.chessboard_degree_vacuous MathResearch.ThirdParty.chessboardNu_base_degree
-/

import Lean.Elab.Tactic.Omega

namespace MathResearch.ThirdParty

/-- The parameter in the homological chessboard bound. -/
def chessboardNu (a b : Nat) : Nat := min a (min b ((a + b + 1) / 3))

theorem chessboardNu_symm (a b : Nat) : chessboardNu a b = chessboardNu b a := by
  unfold chessboardNu
  omega

theorem chessboardNu_bounds (a b : Nat) :
    chessboardNu a b ≤ a ∧ chessboardNu a b ≤ b ∧
      3 * chessboardNu a b ≤ a + b + 1 := by
  unfold chessboardNu
  omega

theorem chessboardNu_pos {a b : Nat} (ha : 1 ≤ a) (hb : 1 ≤ b) :
    1 ≤ chessboardNu a b := by
  unfold chessboardNu
  omega

theorem chessboardNu_zero (b : Nat) :
    chessboardNu 0 b = 0 ∧ chessboardNu b 0 = 0 := by
  unfold chessboardNu
  omega

theorem chessboardNu_one {b : Nat} (hb : 1 ≤ b) : chessboardNu 1 b = 1 := by
  unfold chessboardNu
  omega

theorem chessboardNu_ordered_bound {a b : Nat} (ha : 2 ≤ a) (hab : a ≤ b) :
    chessboardNu a b ≤ b - 1 := by
  unfold chessboardNu
  omega

/-- Additive form of the signed bound mu >= nu-t+1; no truncated subtraction. -/
theorem chessboardNu_intersection {a b t : Nat}
    (ha : 2 ≤ a) (hab : a ≤ b) (ht : 2 ≤ t) (htb : t < b) :
    chessboardNu a b + 1 ≤ chessboardNu (a - 1) (b - t) + t := by
  have hb := chessboardNu_ordered_bound ha hab
  have hn := chessboardNu_bounds a b
  unfold chessboardNu at *
  omega

theorem chessboardNu_intersection_degree {a b t : Nat}
    (ha : 2 ≤ a) (hab : a ≤ b) (ht : 2 ≤ t) (htb : t < b) :
    (chessboardNu a b : Int) - 2 - t + 1 ≤
      (chessboardNu (a - 1) (b - t) : Int) - 2 := by
  have h := chessboardNu_intersection ha hab ht htb
  omega

/-- Either orientation of the intersection has smaller induction measure. -/
theorem chessboard_induction_decrease {a b t : Nat} (ha : 1 ≤ a) (hab : a ≤ b) :
    min (a - 1) (b - t) < min a b ∧ min (b - t) (a - 1) < min a b := by
  omega

theorem chessboardNu_stable_range {s N : Nat} (h : 2 * s - 1 ≤ N) :
    chessboardNu s N = s := by
  unfold chessboardNu
  omega

/-- k counts cells, and k-1 is an integer reduced simplicial degree. -/
theorem chessboard_cell_degree_iff (k n : Nat) :
    (-1 ≤ (k : Int) - 1 ∧ (k : Int) - 1 ≤ (n : Int) - 2) ↔ k < n := by
  omega

/-- A bound strictly below -1 requests no augmented chain degree. -/
theorem chessboard_degree_vacuous {q : Int} (hq : q < -1) (k : Nat) :
    ¬ ((k : Int) - 1 ≤ q) := by
  omega

/-- nu=1 requests only the empty-face coordinate; nu=0 requests none. -/
theorem chessboardNu_base_degree (k : Nat) :
    (((k : Int) - 1 ≤ (1 : Int) - 2) ↔ k = 0) ∧
    ¬ ((k : Int) - 1 ≤ (0 : Int) - 2) := by
  omega

end MathResearch.ThirdParty
