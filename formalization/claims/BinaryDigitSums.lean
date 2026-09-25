/-
Claim: lem:binary-digit-sum-identities
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#binary-digit-sum-identities
Scope: For the binary digit sum s₂ (MathResearch.TruncatedProduct.s2, the sum of Nat.digits 2):
(1) s₂(q·2^n + r) = s₂(q) + s₂(r) for r < 2^n; (2) 2^(s₂ r) ≤ r + 1, hence s₂(r) ≤ ⌊log₂(r+1)⌋;
(3) s₂(r) ≥ 1 for r ≥ 1; (4) s₂(x) = 1 iff x is a power of two; (5) s₂(n+1) + v₂(n+1) = s₂(n) + 1,
with v₂ the 2-adic valuation (padicValNat 2).
Declarations: MathResearch.BinaryDigitSums.s2_mul_two_pow_add MathResearch.BinaryDigitSums.two_pow_s2_le MathResearch.BinaryDigitSums.s2_le_log MathResearch.BinaryDigitSums.s2_pos MathResearch.BinaryDigitSums.s2_eq_one_iff MathResearch.BinaryDigitSums.s2_succ_add_padicValNat
-/
import claims.TruncatedProduct
import Mathlib.NumberTheory.Padics.PadicVal.Basic
import Mathlib.Data.Nat.Log

namespace MathResearch.BinaryDigitSums

open MathResearch.TruncatedProduct

/-- `s₂(q·2^n + r) = s₂(q) + s₂(r)` for `r < 2^n`. -/
theorem s2_mul_two_pow_add (q : ℕ) {n r : ℕ} (hr : r < 2 ^ n) : s2 (q * 2 ^ n + r) = s2 q + s2 r := by
  induction n generalizing r with
  | zero =>
    have : r = 0 := by simpa using hr
    subst this
    simp [s2]
  | succ n ih =>
    have h2 : r / 2 < 2 ^ n := by rw [pow_succ] at hr; omega
    rw [s2_rec (q * 2 ^ (n + 1) + r), s2_rec r]
    have hmod : (q * 2 ^ (n + 1) + r) % 2 = r % 2 := by
      rw [pow_succ, ← mul_assoc]; omega
    have hdiv : (q * 2 ^ (n + 1) + r) / 2 = q * 2 ^ n + r / 2 := by
      rw [pow_succ, ← mul_assoc]; omega
    rw [hmod, hdiv, ih h2]
    ring

/-- `2^(s₂ r) ≤ r + 1`. -/
theorem two_pow_s2_le (r : ℕ) : 2 ^ s2 r ≤ r + 1 := by
  induction r using Nat.strong_induction_on with
  | _ r ih =>
    rcases Nat.eq_zero_or_pos r with rfl | hr
    · simp [s2]
    · have h := ih (r / 2) (by omega)
      rw [s2_rec r, pow_add]
      rcases Nat.mod_two_eq_zero_or_one r with h0 | h1
      · rw [h0, pow_zero, one_mul]; omega
      · rw [h1, pow_one]; omega

/-- `s₂(r) ≤ ⌊log₂(r + 1)⌋`. -/
theorem s2_le_log (r : ℕ) : s2 r ≤ Nat.log 2 (r + 1) :=
  Nat.le_log_of_pow_le (by norm_num) (two_pow_s2_le r)

/-- `s₂(r) ≥ 1` for `r ≥ 1`. -/
theorem s2_pos {r : ℕ} (hr : 0 < r) : 0 < s2 r := by
  induction r using Nat.strong_induction_on with
  | _ r ih =>
    rw [s2_rec r]
    rcases Nat.mod_two_eq_zero_or_one r with h0 | h1
    · have := ih (r / 2) (by omega) (by omega); omega
    · omega

/-- `s₂(x) = 1` iff `x` is a power of two. -/
theorem s2_eq_one_iff (x : ℕ) : s2 x = 1 ↔ ∃ s, x = 2 ^ s := by
  constructor
  · intro h
    induction x using Nat.strong_induction_on with
    | _ x ih =>
      rcases Nat.eq_zero_or_pos x with rfl | hx
      · simp [s2] at h
      · rw [s2_rec x] at h
        rcases Nat.mod_two_eq_zero_or_one x with h0 | h1
        · rw [h0, zero_add] at h
          obtain ⟨s, hs⟩ := ih (x / 2) (by omega) h
          exact ⟨s + 1, by rw [pow_succ]; omega⟩
        · rw [h1] at h
          have h0 : s2 (x / 2) = 0 := by omega
          have hx2 : x / 2 = 0 := by
            by_contra hne
            have := s2_pos (Nat.pos_of_ne_zero hne); omega
          exact ⟨0, by omega⟩
  · rintro ⟨s, rfl⟩
    exact s2_two_pow s

/-- `s₂(n+1) + v₂(n+1) = s₂(n) + 1`. -/
theorem s2_succ_add_padicValNat (n : ℕ) : s2 (n + 1) + padicValNat 2 (n + 1) = s2 n + 1 := by
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    rcases Nat.even_or_odd' n with ⟨a, rfl | rfl⟩
    · have hv : padicValNat 2 (2 * a + 1) = 0 :=
        padicValNat.eq_zero_of_not_dvd (by omega)
      rw [hv, s2_rec (2 * a + 1), s2_rec (2 * a), show (2 * a + 1) % 2 = 1 by omega,
        show (2 * a + 1) / 2 = a by omega, show 2 * a % 2 = 0 by omega,
        show 2 * a / 2 = a by omega]
      ring
    · rcases Nat.eq_zero_or_pos a with rfl | ha
      · -- n = 1: s₂(2) + v₂(2) = 1 + 1 = s₂(1) + 1
        have h2 : padicValNat 2 2 = 1 := padicValNat_self
        have hs2 : s2 2 = 1 := by simpa using s2_two_pow 1
        simp only [mul_zero, zero_add, Nat.reduceAdd, h2, hs2, s2_one]
      · have hih := ih a (by omega)
        have hv : padicValNat 2 (2 * a + 1 + 1) = 1 + padicValNat 2 (a + 1) := by
          rw [show 2 * a + 1 + 1 = 2 * (a + 1) by ring, padicValNat.mul (by norm_num) (by omega),
            padicValNat_self]
        rw [hv, s2_rec (2 * a + 1 + 1), s2_rec (2 * a + 1), show (2 * a + 1 + 1) % 2 = 0 by omega,
          show (2 * a + 1 + 1) / 2 = a + 1 by omega, show (2 * a + 1) % 2 = 1 by omega,
          show (2 * a + 1) / 2 = a by omega]
        omega

end MathResearch.BinaryDigitSums
