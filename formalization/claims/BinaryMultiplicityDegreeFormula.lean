/-
Claim: thm:binary-multiplicity-degree-formula
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#binary-multiplicity-degree-formula-theorem
Scope: For every k ≥ 1: (i) for n ≥ ⌊log₂ k⌋ + 2, every P ∈ F_2[x_1,…,x_n] with Hasse multiplicity ≥ k at
every nonzero point and < k at the origin has total degree ≥ 2k + n − 2 − ⌊log₂ k⌋; (ii) for every n ≥ 1
some such P has total degree ≤ 2k + n − 2 − ⌊log₂ k⌋. Hence for n ≥ ⌊log₂ k⌋ + 2 (equivalently
1 ≤ k < 2^(n−1), the range of conj:binary-multiplicity-degree-formula) the minimum degree is exactly
2k + n − 2 − ⌊log₂ k⌋. Everything used is verified in Lean, down to multiplicity Schwartz–Zippel.
Declarations: MathResearch.BinaryMultiplicityDegreeFormula.Admissible MathResearch.BinaryMultiplicityDegreeFormula.s2_two_pow_sub_one MathResearch.BinaryMultiplicityDegreeFormula.upper_bound MathResearch.BinaryMultiplicityDegreeFormula.degree_formula MathResearch.BinaryMultiplicityDegreeFormula.degree_formula_exact MathResearch.BinaryMultiplicityDegreeFormula.degree_formula_of_lt_two_pow
-/
import claims.BinaryMultiplicityLowerBound
import claims.PerOrderConstruction

namespace MathResearch.BinaryMultiplicityDegreeFormula

open MvPolynomial MathResearch.HasseMultiplicity MathResearch.TruncatedProduct

/-- Multiplicity at least `k` at every nonzero point of `𝔽₂ⁿ` and less than `k` at the origin. -/
def Admissible (n k : ℕ) (P : MvPolynomial (Fin n) (ZMod 2)) : Prop :=
  (∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P) ∧ mult 0 P < k

theorem s2_two_pow_sub_one (J : ℕ) : s2 (2 ^ J - 1) = J := by
  induction J with
  | zero => simp [s2]
  | succ J ih =>
    have hpos : 1 ≤ 2 ^ J := Nat.one_le_two_pow
    rw [s2_rec, show (2 ^ (J + 1) - 1) % 2 = 1 by rw [pow_succ]; omega,
      show (2 ^ (J + 1) - 1) / 2 = 2 ^ J - 1 by rw [pow_succ]; omega, ih]
    ring

/-- The upper bound, in every dimension `n ≥ 1`. -/
theorem upper_bound {k n : ℕ} (hk : 1 ≤ k) (hn : 1 ≤ n) :
    ∃ P : MvPolynomial (Fin n) (ZMod 2), Admissible n k P ∧
      P.totalDegree ≤ 2 * k + n - 2 - Nat.log 2 k := by
  set J := Nat.log 2 k
  have hJ : 2 ^ J ≤ k := Nat.pow_log_le_self 2 (by omega)
  have hJpos : 1 ≤ 2 ^ J := Nat.one_le_two_pow
  set ℓ := k - 2 ^ J
  have hℓ : ℓ < k := by omega
  obtain ⟨h1, h2, h3⟩ :=
    PerOrderConstruction.per_order_construction (σ := Fin n) ⟨0, hn⟩ hℓ
  refine ⟨_, ⟨h1, ?_⟩, ?_⟩
  · rw [h2]; exact_mod_cast hℓ
  · have hs : k - ℓ - 1 = 2 ^ J - 1 := by omega
    rw [hs, s2_two_pow_sub_one, Fintype.card_fin] at h3
    omega

/-- **The degree formula.** -/
theorem degree_formula {k : ℕ} (hk : 1 ≤ k) :
    (∀ n, Nat.log 2 k + 2 ≤ n → ∀ P : MvPolynomial (Fin n) (ZMod 2), Admissible n k P →
        2 * k + n - 2 - Nat.log 2 k ≤ P.totalDegree) ∧
      (∀ n, 1 ≤ n → ∃ P : MvPolynomial (Fin n) (ZMod 2), Admissible n k P ∧
        P.totalDegree ≤ 2 * k + n - 2 - Nat.log 2 k) :=
  ⟨fun _ hn P hP => BinaryMultiplicityLowerBound.lower_bound k hn P hP.1 hP.2,
    fun _ hn => upper_bound hk hn⟩

/-- The minimum is attained: for `n ≥ ⌊log₂ k⌋ + 2` some admissible polynomial has degree exactly
`2k + n − 2 − ⌊log₂ k⌋`, and none has smaller degree. -/
theorem degree_formula_exact {k n : ℕ} (hk : 1 ≤ k) (hn : Nat.log 2 k + 2 ≤ n) :
    (∃ P : MvPolynomial (Fin n) (ZMod 2), Admissible n k P ∧
        P.totalDegree = 2 * k + n - 2 - Nat.log 2 k) ∧
      ∀ P : MvPolynomial (Fin n) (ZMod 2), Admissible n k P →
        2 * k + n - 2 - Nat.log 2 k ≤ P.totalDegree := by
  obtain ⟨P, hP, hdeg⟩ := upper_bound hk (by omega : 1 ≤ n)
  exact ⟨⟨P, hP, le_antisymm hdeg ((degree_formula hk).1 n hn P hP)⟩,
    (degree_formula hk).1 n hn⟩

/-- The same statement in the conjecture's range `1 ≤ k < 2^(n−1)`. -/
theorem degree_formula_of_lt_two_pow {k n : ℕ} (hk : 1 ≤ k) (hkn : k < 2 ^ (n - 1)) :
    (∃ P : MvPolynomial (Fin n) (ZMod 2), Admissible n k P ∧
        P.totalDegree = 2 * k + n - 2 - Nat.log 2 k) ∧
      ∀ P : MvPolynomial (Fin n) (ZMod 2), Admissible n k P →
        2 * k + n - 2 - Nat.log 2 k ≤ P.totalDegree := by
  have hlog : Nat.log 2 k < n - 1 := Nat.log_lt_of_lt_pow (by omega) hkn
  exact degree_formula_exact hk (by omega)

end MathResearch.BinaryMultiplicityDegreeFormula
