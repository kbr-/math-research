/-
Claim: third-party:catalan-two-adic-valuation
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#catalan-two-adic-valuation
Scope: Classical (Alter–Kubota 1973; stated as Theorem 2.1 of Deutsch–Sagan, arXiv:math/0407326):
the 2-adic valuation of the Catalan number C_n (Mathlib's `catalan`) is s₂(n+1) − 1, i.e.
v₂(C_n) + 1 = s₂(n+1); hence C_n is odd iff n + 1 is a power of two. Proved here from Kummer's theorem
(Mathlib, digit form) for the central binomial coefficient and (n+1) C_n = binom(2n, n).
Declarations: MathResearch.ThirdParty.CatalanParity.padicValNat_centralBinom MathResearch.ThirdParty.CatalanParity.padicValNat_catalan MathResearch.ThirdParty.CatalanParity.odd_catalan_iff
-/
import claims.BinaryDigitSums
import Mathlib.Combinatorics.Enumerative.Catalan.Basic

namespace MathResearch.ThirdParty.CatalanParity

open MathResearch.TruncatedProduct MathResearch.BinaryDigitSums

/-- `v₂(binom(2n, n)) = s₂(n)`. -/
theorem padicValNat_centralBinom (n : ℕ) : padicValNat 2 (Nat.centralBinom n) = s2 n := by
  have hk := sub_one_mul_padicValNat_choose_eq_sub_sum_digits (p := 2)
    (show n ≤ 2 * n by omega)
  have h2n : s2 (2 * n) = s2 n := by
    rw [s2_rec (2 * n), show 2 * n % 2 = 0 by omega, show 2 * n / 2 = n by omega, zero_add]
  rw [Nat.centralBinom_eq_two_mul_choose]
  change (2 - 1) * padicValNat 2 ((2 * n).choose n) = s2 n + s2 (2 * n - n) - s2 (2 * n) at hk
  rw [show 2 * n - n = n by omega, h2n, show (2 : ℕ) - 1 = 1 by rfl, one_mul] at hk
  omega

/-- `v₂(C_n) + 1 = s₂(n + 1)`. -/
theorem padicValNat_catalan (n : ℕ) : padicValNat 2 (catalan n) + 1 = s2 (n + 1) := by
  have hC : catalan n ≠ 0 := by
    intro h
    have := succ_mul_catalan_eq_centralBinom n
    rw [h, mul_zero] at this
    exact (Nat.centralBinom_ne_zero n) this.symm
  have hmul := congrArg (padicValNat 2) (succ_mul_catalan_eq_centralBinom n)
  rw [padicValNat.mul (by omega) hC, padicValNat_centralBinom] at hmul
  have := s2_succ_add_padicValNat n
  omega

/-- `C_n` is odd iff `n + 1` is a power of two. -/
theorem odd_catalan_iff (n : ℕ) : Odd (catalan n) ↔ ∃ s, n + 1 = 2 ^ s := by
  have hC : catalan n ≠ 0 := by
    intro h
    have := succ_mul_catalan_eq_centralBinom n
    rw [h, mul_zero] at this
    exact (Nat.centralBinom_ne_zero n) this.symm
  rw [← s2_eq_one_iff, Nat.odd_iff, ← padicValNat_catalan]
  constructor
  · intro h
    have : ¬ 2 ∣ catalan n := by omega
    rw [padicValNat.eq_zero_of_not_dvd this]
  · intro h
    have h0 : padicValNat 2 (catalan n) = 0 := by omega
    rcases (padicValNat.eq_zero_iff).1 h0 with h1 | h1 | h1
    · norm_num at h1
    · exact absurd h1 hC
    · omega
