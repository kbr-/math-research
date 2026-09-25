/-
Claim: lem:degree-formula-arithmetic
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#degree-formula-arithmetic
Scope: Consequences of the value D(n,k) = degreeMin n k (2k + n − 2 − ⌊log₂k⌋ for k < 2^(n−1), else
2k − ⌊k/2^(n−1)⌋) used in the preprint's remarks: (1) D(n,1) = n for n ≥ 2, D(n,4) = n + 4 for n ≥ 4,
D(n,8) = n + 11 and D(n,15) = n + 25 for n ≥ 5; (2) for 1 ≤ k < 2^(n−2), D exceeds the Schwartz–Zippel
bound 2k − ⌊k/2^(n−1)⌋ by n − 2 − ⌊log₂k⌋ ≥ 1; (3) D(n+1,k) = D(n,k) + 1 for n ≥ ⌊log₂k⌋ + 2, k ≥ 1;
(4) for n ≥ 1 and k = 3·2^(n−1): ⌊log₂k⌋ = n, so 2k + n − 2 − ⌊log₂k⌋ = 2k − 2, while D(n,k) = 2k − 3;
(5) D(n,k) + 1 ≤ D(n+1,k) for n, k ≥ 1.
Declarations: MathResearch.DegreeFormulaArithmetic.degreeMin_one MathResearch.DegreeFormulaArithmetic.degreeMin_four MathResearch.DegreeFormulaArithmetic.degreeMin_eight MathResearch.DegreeFormulaArithmetic.degreeMin_fifteen MathResearch.DegreeFormulaArithmetic.degreeMin_excess MathResearch.DegreeFormulaArithmetic.degreeMin_succ MathResearch.DegreeFormulaArithmetic.degreeMin_three_mul MathResearch.DegreeFormulaArithmetic.degreeMin_add_one_le
-/
import claims.PerOrderMinimum
import claims.PerOrderArithmetic

namespace MathResearch.DegreeFormulaArithmetic

open MathResearch.BinaryMultiplicityDegreeComplete MathResearch.PerOrderUpperBound
open MathResearch.PerOrderMinimum MathResearch.PerOrderArithmetic

theorem two_pow_ge {a b : ℕ} (h : a ≤ b) : 2 ^ a ≤ 2 ^ b := Nat.pow_le_pow_right (by norm_num) h

theorem degreeMin_one {n : ℕ} (hn : 2 ≤ n) : degreeMin n 1 = n := by
  have h : 1 < 2 ^ (n - 1) := Nat.one_lt_two_pow (by omega)
  unfold degreeMin
  rw [ite_eq_left h, Nat.log_one_right]
  omega

theorem degreeMin_four {n : ℕ} (hn : 4 ≤ n) : degreeMin n 4 = n + 4 := by
  have h : 4 < 2 ^ (n - 1) := lt_of_lt_of_le (by norm_num) (two_pow_ge (show 3 ≤ n - 1 by omega))
  have hl : Nat.log 2 4 = 2 := by rw [show (4 : ℕ) = 2 ^ 2 by norm_num, Nat.log_pow (by norm_num)]
  unfold degreeMin
  rw [ite_eq_left h, hl]
  omega

theorem degreeMin_eight {n : ℕ} (hn : 5 ≤ n) : degreeMin n 8 = n + 11 := by
  have h : 8 < 2 ^ (n - 1) := lt_of_lt_of_le (by norm_num) (two_pow_ge (show 4 ≤ n - 1 by omega))
  have hl : Nat.log 2 8 = 3 := by rw [show (8 : ℕ) = 2 ^ 3 by norm_num, Nat.log_pow (by norm_num)]
  unfold degreeMin
  rw [ite_eq_left h, hl]
  omega

theorem degreeMin_fifteen {n : ℕ} (hn : 5 ≤ n) : degreeMin n 15 = n + 25 := by
  have h : 15 < 2 ^ (n - 1) := lt_of_lt_of_le (by norm_num) (two_pow_ge (show 4 ≤ n - 1 by omega))
  have hl : Nat.log 2 15 = 3 := Nat.log_eq_of_pow_le_of_lt_pow (by norm_num) (by norm_num)
  unfold degreeMin
  rw [ite_eq_left h, hl]
  omega

/-- For `1 ≤ k < 2^(n−2)`, `D(n,k)` exceeds the Schwartz–Zippel bound by `n − 2 − ⌊log₂k⌋ ≥ 1`. -/
theorem degreeMin_excess {n k : ℕ} (hk : 1 ≤ k) (h : k < 2 ^ (n - 2)) :
    degreeMin n k = (2 * k - k / 2 ^ (n - 1)) + (n - 2 - Nat.log 2 k) ∧
      1 ≤ n - 2 - Nat.log 2 k := by
  have hn2 : 1 ≤ n - 2 := by
    by_contra hc
    rw [show n - 2 = 0 by omega, pow_zero] at h
    omega
  have hle : 2 ^ (n - 2) ≤ 2 ^ (n - 1) := two_pow_ge (by omega)
  have hsmall : k < 2 ^ (n - 1) := lt_of_lt_of_le h hle
  have hdiv : k / 2 ^ (n - 1) = 0 := Nat.div_eq_of_lt hsmall
  have hlog : Nat.log 2 k < n - 2 := Nat.log_lt_of_lt_pow (by omega) h
  unfold degreeMin
  rw [ite_eq_left hsmall, hdiv]
  omega

/-- **Each further dimension costs one degree.** For `k ≥ 1` and `n ≥ ⌊log₂k⌋ + 2`,
`D(n+1,k) = D(n,k) + 1`. -/
theorem degreeMin_succ {n k : ℕ} (hk : 1 ≤ k) (hn : Nat.log 2 k + 2 ≤ n) :
    degreeMin (n + 1) k = degreeMin n k + 1 := by
  have hlt : k < 2 ^ (Nat.log 2 k + 1) := Nat.lt_pow_succ_log_self (by norm_num) k
  have h1 : k < 2 ^ (n - 1) := lt_of_lt_of_le hlt (two_pow_ge (by omega))
  have h2 : k < 2 ^ (n + 1 - 1) := lt_of_lt_of_le h1 (two_pow_ge (by omega))
  unfold degreeMin
  rw [ite_eq_left h1, ite_eq_left h2]
  omega

/-- At `k = 3·2^(n−1)`: `⌊log₂k⌋ = n` and `D(n,k) = 2k − 3`. -/
theorem degreeMin_three_mul {n : ℕ} (hn : 1 ≤ n) :
    Nat.log 2 (3 * 2 ^ (n - 1)) = n ∧ degreeMin n (3 * 2 ^ (n - 1)) = 2 * (3 * 2 ^ (n - 1)) - 3 := by
  have hp : 2 ^ n = 2 * 2 ^ (n - 1) := by
    rw [← pow_succ']; congr 1; omega
  have hp1 : 2 ^ (n + 1) = 4 * 2 ^ (n - 1) := by
    rw [pow_succ, hp]; ring
  have hpos : 1 ≤ 2 ^ (n - 1) := Nat.one_le_two_pow
  refine ⟨Nat.log_eq_of_pow_le_of_lt_pow (by rw [hp]; omega) (by rw [hp1]; omega), ?_⟩
  unfold degreeMin
  rw [ite_eq_right (by omega), Nat.mul_div_cancel _ (by positivity)]

/-- `D(n,k) + 1 ≤ D(n+1,k)` for `n, k ≥ 1`. -/
theorem degreeMin_add_one_le {n k : ℕ} (hn : 1 ≤ n) (hk : 1 ≤ k) :
    degreeMin n k + 1 ≤ degreeMin (n + 1) k := by
  obtain ⟨ℓ, hℓ, heq⟩ := (min_phi (n := n + 1) (by omega) hk).2
  have hle := (min_phi hn hk).1 ℓ hℓ
  rw [phi_succ] at heq
  generalize (k - ℓ - 1) / 2 ^ n = d at heq
  omega

end MathResearch.DegreeFormulaArithmetic
