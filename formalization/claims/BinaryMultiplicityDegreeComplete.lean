/-
Claim: thm:binary-multiplicity-degree-complete
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-09-24-complete-degree
Scope: For all n ≥ 1 and k ≥ 1, the minimum degree D(n,k) of a k-admissible polynomial over F_2 in n
variables is 2k + n − 2 − ⌊log₂ k⌋ when k < 2^(n−1) and 2k − ⌊k/2^(n−1)⌋ when k ≥ 2^(n−1); an
admissible polynomial of exactly this degree exists. The Schwartz–Zippel bound 2k − ⌊k/2^(n−1)⌋ is
attained by an admissible polynomial if and only if 2^(n−2) ≤ k.
Declarations: MathResearch.BinaryMultiplicityDegreeComplete.degreeMin MathResearch.BinaryMultiplicityDegreeComplete.degree_complete MathResearch.BinaryMultiplicityDegreeComplete.cover_bound_attained_iff
-/
import claims.BinaryMultiplicityDegreeFormula
import claims.BinaryMultiplicityDegreeExtendedRange
import «third-party-claims».HyperplaneCoverUpperBound

namespace MathResearch.BinaryMultiplicityDegreeComplete

open MvPolynomial MathResearch.BinaryMultiplicityDegreeFormula

/-- The value of `D(n,k)`. -/
def degreeMin (n k : ℕ) : ℕ :=
  if k < 2 ^ (n - 1) then 2 * k + n - 2 - Nat.log 2 k else 2 * k - k / 2 ^ (n - 1)

/-- **The complete degree formula.** For `n ≥ 1` and `k ≥ 1`, `degreeMin n k` is the least total
degree of a `k`-admissible polynomial over `𝔽₂` in `n` variables, and it is attained. -/
theorem degree_complete {n k : ℕ} (hn : 1 ≤ n) (hk : 1 ≤ k) :
    (∃ P : MvPolynomial (Fin n) (ZMod 2), Admissible n k P ∧ P.totalDegree = degreeMin n k) ∧
      ∀ P : MvPolynomial (Fin n) (ZMod 2), Admissible n k P → degreeMin n k ≤ P.totalDegree := by
  unfold degreeMin
  split_ifs with hsmall
  · exact degree_formula_of_lt_two_pow hk hsmall
  push Not at hsmall
  have hlower : ∀ P : MvPolynomial (Fin n) (ZMod 2), Admissible n k P →
      2 * k - k / 2 ^ (n - 1) ≤ P.totalDegree := fun P hP =>
    BinaryMultiplicityCoverBound.cover_bound_of_origin (by omega) k hP.1 hP.2
  obtain ⟨P, hP, hdeg⟩ := ThirdParty.HyperplaneCoverUpperBound.hyperplane_cover_upper_bound hn hsmall
  exact ⟨⟨P, hP, le_antisymm hdeg (hlower P hP)⟩, hlower⟩

/-- **When the Schwartz–Zippel bound is attained.** For `n ≥ 1` and `k ≥ 1`, some `k`-admissible
polynomial has total degree exactly `2k − ⌊k/2^(n−1)⌋` if and only if `2^(n−2) ≤ k`. -/
theorem cover_bound_attained_iff {n k : ℕ} (hn : 1 ≤ n) (hk : 1 ≤ k) :
    (∃ P : MvPolynomial (Fin n) (ZMod 2), Admissible n k P ∧
        P.totalDegree = 2 * k - k / 2 ^ (n - 1)) ↔ 2 ^ (n - 2) ≤ k := by
  have hpow : 2 ^ (n - 2) ≤ 2 ^ (n - 1) := Nat.pow_le_pow_right (by norm_num) (by omega)
  constructor
  · rintro ⟨P, hP, hdeg⟩
    by_contra hlt
    push Not at hlt
    have hsmall : k < 2 ^ (n - 1) := lt_of_lt_of_le hlt hpow
    have hlog : Nat.log 2 k < n - 2 := Nat.log_lt_of_lt_pow (by omega) hlt
    have hdiv : k / 2 ^ (n - 1) = 0 := Nat.div_eq_of_lt hsmall
    have := (degree_formula_of_lt_two_pow hk hsmall).2 P hP
    omega
  · intro hge
    by_cases hsmall : k < 2 ^ (n - 1)
    · obtain ⟨⟨P, hP, hdeg⟩, _⟩ := degree_formula_of_lt_two_pow hk hsmall
      have hn2 : 2 ≤ n := by
        by_contra h
        have : n - 1 = 0 := by omega
        rw [this] at hsmall; omega
      have hlog : Nat.log 2 k = n - 2 :=
        Nat.log_eq_of_pow_le_of_lt_pow hge (by rw [show n - 2 + 1 = n - 1 by omega]; exact hsmall)
      have hdiv : k / 2 ^ (n - 1) = 0 := Nat.div_eq_of_lt hsmall
      refine ⟨P, hP, ?_⟩
      rw [hdeg, hlog, hdiv]; omega
    · obtain ⟨⟨P, hP, hdeg⟩, _⟩ := degree_complete hn hk
      refine ⟨P, hP, ?_⟩
      rw [hdeg]; simp [degreeMin, hsmall]

end MathResearch.BinaryMultiplicityDegreeComplete
