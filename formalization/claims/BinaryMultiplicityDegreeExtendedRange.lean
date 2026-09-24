/-
Claim: cor:binary-multiplicity-degree-extended-range
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-09-24-extended-range
Scope: For n ≥ 1 and 1 ≤ k < 3·2^(n−1), the minimum degree of a k-admissible polynomial over F_2 in n
variables is exactly 2k + n − 2 − ⌊log₂ k⌋. Below 2^(n−1) this is the degree formula; for
2^(n−1) ≤ k < 3·2^(n−1) the note's bound 2k − ⌊k/2^(n−1)⌋ meets the construction.
Declarations: MathResearch.BinaryMultiplicityDegreeExtendedRange.degree_formula_extended
-/
import claims.BinaryMultiplicityDegreeFormula

namespace MathResearch.BinaryMultiplicityDegreeExtendedRange

open MvPolynomial MathResearch.BinaryMultiplicityDegreeFormula

theorem degree_formula_extended {k n : ℕ} (hk : 1 ≤ k) (hn : 1 ≤ n) (hkn : k < 3 * 2 ^ (n - 1)) :
    (∃ P : MvPolynomial (Fin n) (ZMod 2), Admissible n k P ∧
        P.totalDegree = 2 * k + n - 2 - Nat.log 2 k) ∧
      ∀ P : MvPolynomial (Fin n) (ZMod 2), Admissible n k P →
        2 * k + n - 2 - Nat.log 2 k ≤ P.totalDegree := by
  by_cases hsmall : k < 2 ^ (n - 1)
  · exact degree_formula_of_lt_two_pow hk hsmall
  push Not at hsmall
  have h2n : 2 ^ n = 2 * 2 ^ (n - 1) := by
    rw [← pow_succ']; congr 1; omega
  have hform : 2 * k + n - 2 - Nat.log 2 k = 2 * k - k / 2 ^ (n - 1) := by
    rcases lt_or_ge k (2 ^ n) with hlt | hge
    · have hlog : Nat.log 2 k = n - 1 :=
        Nat.log_eq_of_pow_le_of_lt_pow hsmall (by rw [show n - 1 + 1 = n by omega]; exact hlt)
      have hdiv : k / 2 ^ (n - 1) = 1 :=
        Nat.div_eq_of_lt_le (by omega) (by omega)
      rw [hlog, hdiv]; omega
    · have hlog : Nat.log 2 k = n :=
        Nat.log_eq_of_pow_le_of_lt_pow hge (by rw [pow_succ]; omega)
      have hdiv : k / 2 ^ (n - 1) = 2 :=
        Nat.div_eq_of_lt_le (by omega) (by omega)
      rw [hlog, hdiv]; omega
  have hlower : ∀ P : MvPolynomial (Fin n) (ZMod 2), Admissible n k P →
      2 * k + n - 2 - Nat.log 2 k ≤ P.totalDegree := by
    intro P hP
    rw [hform]
    exact BinaryMultiplicityCoverBound.cover_bound_of_origin (by omega) k hP.1 hP.2
  obtain ⟨P, hP, hdeg⟩ := upper_bound hk hn
  exact ⟨⟨P, hP, le_antisymm hdeg (hlower P hP)⟩, hlower⟩

end MathResearch.BinaryMultiplicityDegreeExtendedRange
