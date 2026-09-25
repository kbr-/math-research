/-
Claim: lem:per-order-all-dimension-minimum (the Legendre form and part (i))
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#per-order-all-dimension-minimum
Scope: For m = q 2^n + r with 0 ≤ r < 2^n: Σ_{j<n} ⌊m/2^j⌋ + 2q + s₂(r) = 2m (the Legendre form of Φ),
hence part (i): for ℓ < k with k − ℓ − 1 < 2^n, Φ(n,k,ℓ) = n + 2k − 2 − s₂(k − ℓ − 1). Also, for n ≥ 1
and r < 2^n, the decomposition of m into exactly 2q + s₂(r) powers of two, each at most 2^(n−1), used by
the lower bound.
Part (ii) (the minimum over ℓ) is not formalized here.
Declarations: MathResearch.PerOrderLegendre.legendre MathResearch.PerOrderLegendre.phi_of_lt_two_pow MathResearch.PerOrderLegendre.bits MathResearch.PerOrderLegendre.length_bits MathResearch.PerOrderLegendre.sum_bits MathResearch.PerOrderLegendre.lt_of_mem_bits
-/
import claims.TruncatedProduct
import Mathlib.Data.Nat.BitIndices

namespace MathResearch.PerOrderLegendre

open MathResearch.TruncatedProduct

theorem length_bitIndices (r : ℕ) : r.bitIndices.length = s2 r := by
  induction r using Nat.strong_induction_on with
  | _ r ih =>
    rcases Nat.even_or_odd' r with ⟨a, rfl | rfl⟩
    · rcases Nat.eq_zero_or_pos a with rfl | ha
      · simp [s2]
      · rw [Nat.bitIndices_two_mul, List.length_map, ih a (by omega), s2_rec (2 * a),
          show 2 * a % 2 = 0 by omega, show 2 * a / 2 = a by omega, zero_add]
    · rw [Nat.bitIndices_two_mul_add_one, List.length_cons, List.length_map, ih a (by omega),
        s2_rec (2 * a + 1), show (2 * a + 1) % 2 = 1 by omega, show (2 * a + 1) / 2 = a by omega]
      ring

/-- **Legendre form.** For `m = q 2^n + r`, `0 ≤ r < 2^n`:
`Σ_{j<n} ⌊m/2^j⌋ + 2q + s₂(r) = 2m`. -/
theorem legendre (n q r : ℕ) (hr : r < 2 ^ n) :
    ∑ j ∈ Finset.range n, (q * 2 ^ n + r) / 2 ^ j + 2 * q + s2 r = 2 * (q * 2 ^ n + r) := by
  induction n generalizing r with
  | zero =>
    have : r = 0 := by simpa using hr
    subst this
    simp [s2]
  | succ n ih =>
    have hr2 : r / 2 < 2 ^ n := by
      rw [pow_succ] at hr; omega
    have ih' := ih (r / 2) hr2
    rw [Finset.sum_range_succ']
    have hshift : ∀ j, (q * 2 ^ (n + 1) + r) / 2 ^ (j + 1) = (q * 2 ^ n + r / 2) / 2 ^ j := by
      intro j
      rw [pow_succ 2 j, mul_comm (2 ^ j) 2, ← Nat.div_div_eq_div_mul]
      congr 1
      rw [pow_succ, show q * (2 ^ n * 2) + r = r + 2 * (q * 2 ^ n) by ring,
        Nat.add_mul_div_left _ _ (by norm_num)]
      ring
    simp_rw [hshift]
    rw [s2_rec r, pow_zero, Nat.div_one]
    have h2 : q * 2 ^ (n + 1) = 2 * (q * 2 ^ n) := by rw [pow_succ]; ring
    rw [h2]
    omega

/-- The exponents of the decomposition `m = Σ_a 2^{s_a}`: `2q` copies of `n − 1` and the binary
digits of `r`. -/
def bits (n q r : ℕ) : List ℕ := List.replicate (2 * q) (n - 1) ++ r.bitIndices

theorem length_bits (n q r : ℕ) : (bits n q r).length = 2 * q + s2 r := by
  simp [bits, length_bitIndices]

theorem sum_bits {n : ℕ} (hn : 1 ≤ n) (q r : ℕ) :
    ((bits n q r).map (2 ^ ·)).sum = q * 2 ^ n + r := by
  simp only [bits, List.map_append, List.sum_append, List.map_replicate, List.sum_replicate,
    smul_eq_mul, Nat.sum_map_two_pow_bitIndices]
  have : 2 ^ n = 2 * 2 ^ (n - 1) := by
    rw [← pow_succ']; congr 1; omega
  rw [this]; ring

theorem lt_of_mem_bits {n q r : ℕ} (hn : 1 ≤ n) (hr : r < 2 ^ n) {x : ℕ} (hx : x ∈ bits n q r) :
    x < n := by
  rcases List.mem_append.1 hx with h | h
  · rw [List.eq_of_mem_replicate h]; omega
  · have := Nat.two_pow_le_of_mem_bitIndices h
    exact (Nat.pow_lt_pow_iff_right (by norm_num)).1 (lt_of_le_of_lt this hr)

/-- **Part (i)** of the minimum lemma: for `k − ℓ − 1 < 2^n`,
`n + 2ℓ + Σ_{j<n} ⌊(k−ℓ−1)/2^j⌋ = n + 2k − 2 − s₂(k − ℓ − 1)`. -/
theorem phi_of_lt_two_pow {n k ℓ : ℕ} (hℓ : ℓ < k) (hm : k - ℓ - 1 < 2 ^ n) :
    n + 2 * ℓ + ∑ j ∈ Finset.range n, (k - ℓ - 1) / 2 ^ j = n + 2 * k - 2 - s2 (k - ℓ - 1) := by
  have h := legendre n 0 (k - ℓ - 1) hm
  simp only [zero_mul, zero_add, mul_zero] at h
  have hs := s2_le_self (k - ℓ - 1)
  omega

end MathResearch.PerOrderLegendre
