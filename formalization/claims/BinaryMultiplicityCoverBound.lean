/-
Claim: audit:binary-multiplicity-cover-question
Source: https://kbr.is-a.dev/math-research/#binary-multiplicity-cover-question
Scope: For positive n and k, every nonzero P ∈ F_2[x_1,…,x_n] with Hasse multiplicity at least k at every
nonzero point of F_2^n has total degree at least 2k − ⌊k/2^(n−1)⌋ (the bound asked in BBDM 2023
Question 4.3, without its k ≥ 2^(n−2) threshold), by multiplicity Schwartz–Zippel with S = F_2. The
version with the question's hypothesis mult_0(P) ≤ k − 1 in place of P ≠ 0 is also stated.
Declarations: MathResearch.BinaryMultiplicityCoverBound.cover_bound MathResearch.BinaryMultiplicityCoverBound.cover_bound_of_origin
-/
import «third-party-claims».MultiplicitySchwartzZippel
import Mathlib.Algebra.Field.ZMod

namespace MathResearch.BinaryMultiplicityCoverBound

open MvPolynomial MathResearch.HasseMultiplicity MathResearch.ThirdParty.MultiplicitySchwartzZippel

/-- Integer form of the deduction: `k (2m − 1) ≤ d m` with `m ≥ 1` gives `2k − ⌊k/m⌋ ≤ d`. -/
theorem arith {k d m : ℕ} (hm : 0 < m) (h : k * (2 * m - 1) ≤ d * m) : 2 * k - k / m ≤ d := by
  by_contra hlt
  push Not at hlt
  have hq : k < (k / m + 1) * m := by
    have := Nat.lt_div_mul_add (a := k) hm
    linarith
  have h1 : d + k / m + 1 ≤ 2 * k := by omega
  have h2 : (d + k / m + 1) * m ≤ 2 * k * m := Nat.mul_le_mul_right m h1
  have h3 : k * (2 * m - 1) = 2 * k * m - k := by
    rw [Nat.mul_sub, mul_one]; ring_nf
  have h4 : k ≤ 2 * k * m := by nlinarith
  have : d * m + (k / m + 1) * m ≤ 2 * k * m := by nlinarith
  omega

/-- The note's deduction: nonzero `P` with multiplicity at least `k` at every nonzero point of
`𝔽₂ⁿ` has total degree at least `2k − ⌊k / 2^(n−1)⌋`. -/
theorem cover_bound {n : ℕ} (hn : 0 < n) (k : ℕ) {P : MvPolynomial (Fin n) (ZMod 2)} (hP : P ≠ 0)
    (hmult : ∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P) :
    2 * k - k / 2 ^ (n - 1) ≤ P.totalDegree := by
  classical
  have hsz := multiplicity_schwartz_zippel (by simpa using hn) (Finset.univ : Finset (ZMod 2)) hP
  rw [Fintype.piFinset_univ, Fintype.card_fin, Finset.card_univ, ZMod.card] at hsz
  have hlow : ((k * (2 ^ n - 1) : ℕ) : ℕ∞) ≤ ∑ a : Fin n → ZMod 2, mult a P := by
    calc ((k * (2 ^ n - 1) : ℕ) : ℕ∞)
        = ∑ a ∈ (Finset.univ : Finset (Fin n → ZMod 2)).erase 0, (k : ℕ∞) := by
          rw [Finset.sum_const, Finset.card_erase_of_mem (Finset.mem_univ _), Finset.card_univ,
            Fintype.card_fun, ZMod.card, Fintype.card_fin, nsmul_eq_mul]
          push_cast
          ring
      _ ≤ ∑ a ∈ (Finset.univ : Finset (Fin n → ZMod 2)).erase 0, mult a P :=
          Finset.sum_le_sum fun a ha => hmult a (Finset.ne_of_mem_erase ha)
      _ ≤ ∑ a : Fin n → ZMod 2, mult a P :=
          Finset.sum_le_sum_of_subset (Finset.erase_subset _ _)
  have hle : k * (2 ^ n - 1) ≤ P.totalDegree * 2 ^ (n - 1) := by
    exact_mod_cast hlow.trans hsz
  apply arith (Nat.two_pow_pos _)
  have h2 : 2 * 2 ^ (n - 1) = 2 ^ n := by
    rw [← pow_succ']
    congr 1
    omega
  rw [h2]
  exact hle

/-- The question's form: the origin condition `mult₀ P ≤ k − 1` only serves to exclude `P = 0`. -/
theorem cover_bound_of_origin {n : ℕ} (hn : 0 < n) (k : ℕ) {P : MvPolynomial (Fin n) (ZMod 2)}
    (hmult : ∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P) (horigin : mult 0 P < k) :
    2 * k - k / 2 ^ (n - 1) ≤ P.totalDegree := by
  apply cover_bound hn k _ hmult
  rintro rfl
  simp at horigin

end MathResearch.BinaryMultiplicityCoverBound
