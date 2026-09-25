/-
Claim: lem:per-order-all-dimension-minimum (part (ii), the paper's digit argument; and the extremal orders)
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#per-order-all-dimension-minimum
Scope: For n, k ≥ 1, with h(m) = 2⌊m/2^n⌋ + s₂(m mod 2^n) (so Φ(n,k,ℓ) + h(k−ℓ−1) = n + 2(k−1)):
the largest value of h on 0 ≤ m ≤ k − 1 is n + 2(k−1) − D(n,k), where D = degreeMin is the closed form;
hence min_{ℓ<k} Φ(n,k,ℓ) = D(n,k), proved by the digit argument of the preprint (largest digit sum up
to R is ⌊log₂(R+1)⌋, and the case analysis on k − 1 = Q2^n + R), without the Schwartz–Zippel route.
Also: Φ(n,k,ℓ) = D(n,k) iff h(k−ℓ−1) is maximal; for 1 ≤ k ≤ 2^n, iff s₂(k−ℓ−1) = ⌊log₂k⌋; and
ℓ = k − 2^⌊log₂k⌋ is such an order.
Declarations: MathResearch.PerOrderMinimumDirect.hval MathResearch.PerOrderMinimumDirect.phi_add_hval MathResearch.PerOrderMinimumDirect.hval_le MathResearch.PerOrderMinimumDirect.hval_attain MathResearch.PerOrderMinimumDirect.min_phi_direct MathResearch.PerOrderMinimumDirect.phi_eq_degreeMin_iff MathResearch.PerOrderMinimumDirect.extremal_of_le_two_pow MathResearch.PerOrderMinimumDirect.extremal_example
-/
import claims.PerOrderArithmetic
import claims.BinaryMultiplicityDegreeComplete

namespace MathResearch.PerOrderMinimumDirect

open MathResearch.TruncatedProduct MathResearch.BinaryDigitSums MathResearch.PerOrderUpperBound
open MathResearch.PerOrderArithmetic MathResearch.BinaryMultiplicityDegreeComplete
open MathResearch.BinaryMultiplicityDegreeFormula

/-- `h(m) = 2⌊m/2^n⌋ + s₂(m mod 2^n)`. -/
def hval (n m : ℕ) : ℕ := 2 * (m / 2 ^ n) + s2 (m % 2 ^ n)

theorem hval_eq (n q : ℕ) {r : ℕ} (hr : r < 2 ^ n) : hval n (q * 2 ^ n + r) = 2 * q + s2 r := by
  unfold hval
  rw [show q * 2 ^ n + r = r + q * 2 ^ n by ring, Nat.add_mul_div_right _ _ (by positivity),
    Nat.add_mul_mod_self_right, Nat.div_eq_of_lt hr, Nat.mod_eq_of_lt hr, zero_add]

theorem phi_add_hval {n k ℓ : ℕ} (hℓ : ℓ < k) : Phi n k ℓ + hval n (k - ℓ - 1) = n + 2 * (k - 1) := by
  have := phi_add_eq (n := n) hℓ
  unfold hval
  omega

theorem pow_pred_mul {n : ℕ} (hn : 1 ≤ n) : 2 ^ n = 2 * 2 ^ (n - 1) := by
  rw [← pow_succ']; congr 1; omega

/-- For `2^(n−1) ≤ x ≤ 2^n`: `⌊log₂x⌋ + 2 = n + ⌊x/2^(n−1)⌋`. -/
theorem log_add_two_eq {n x : ℕ} (hn : 1 ≤ n) (hlo : 2 ^ (n - 1) ≤ x) (hx : x ≤ 2 ^ n) :
    Nat.log 2 x + 2 = n + x / 2 ^ (n - 1) := by
  have hp := pow_pred_mul hn
  have hpos : 1 ≤ 2 ^ (n - 1) := Nat.one_le_two_pow
  rcases Nat.lt_or_ge x (2 ^ n) with hlt | hge
  · have hl : Nat.log 2 x = n - 1 :=
      Nat.log_eq_of_pow_le_of_lt_pow hlo (by rw [show n - 1 + 1 = n by omega]; exact hlt)
    have ht : x / 2 ^ (n - 1) = 1 :=
      Nat.div_eq_of_lt_le (by rw [one_mul]; exact hlo) (by rw [show 1 + 1 = 2 by rfl, ← hp]; exact hlt)
    rw [hl, ht]; omega
  · have hxe : x = 2 ^ n := le_antisymm hx hge
    have hl : Nat.log 2 x = n := by rw [hxe, Nat.log_pow (by norm_num)]
    have ht : x / 2 ^ (n - 1) = 2 := by
      rw [hxe, hp, Nat.mul_div_cancel _ (by positivity)]
    rw [hl, ht]

/-- For `1 ≤ x ≤ 2^n`: `⌊log₂x⌋ + 2 ≤ n + ⌊x/2^(n−1)⌋`. -/
theorem log_add_two_le {n x : ℕ} (hn : 1 ≤ n) (hx1 : 1 ≤ x) (hx : x ≤ 2 ^ n) :
    Nat.log 2 x + 2 ≤ n + x / 2 ^ (n - 1) := by
  rcases Nat.lt_or_ge x (2 ^ (n - 1)) with hlt | hge
  · have hl : Nat.log 2 x < n - 1 := Nat.log_lt_of_lt_pow (by omega) hlt
    have hn2 : 2 ≤ n := by
      by_contra hc
      rw [show n - 1 = 0 by omega, pow_zero] at hlt
      omega
    generalize x / 2 ^ (n - 1) = u
    omega
  · exact (log_add_two_eq hn hge hx).le

/-- `2 ≤ n + ⌊(R+1)/2^(n−1)⌋` for `n ≥ 1`. -/
theorem two_le_n_add {n R : ℕ} (hn : 1 ≤ n) : 2 ≤ n + (R + 1) / 2 ^ (n - 1) := by
  rcases Nat.lt_or_ge n 2 with h1 | h2
  · have hn1 : n = 1 := by omega
    subst hn1
    simp only [Nat.sub_self, pow_zero, Nat.div_one]
    omega
  · generalize (R + 1) / 2 ^ (n - 1) = t
    omega

/-- `⌊(R+1)/2^(n−1)⌋ ≤ 2` for `R < 2^n`. -/
theorem div_le_two {n R : ℕ} (hn : 1 ≤ n) (hR : R < 2 ^ n) : (R + 1) / 2 ^ (n - 1) ≤ 2 := by
  have hp := pow_pred_mul hn
  rw [Nat.div_le_iff_le_mul_add_pred (by positivity)]
  generalize 2 ^ (n - 1) = P at hp ⊢
  omega

/-- The maximum of `h` on `0 ≤ m ≤ k − 1`, in closed form. -/
def hmax (n k : ℕ) : ℕ :=
  if (k - 1) / 2 ^ n = 0 then Nat.log 2 k
  else 2 * ((k - 1) / 2 ^ n) + (n + ((k - 1) % 2 ^ n + 1) / 2 ^ (n - 1) - 2)

/-- `D(n,k) + h_max = n + 2(k − 1)`. -/
theorem degreeMin_add_hmax {n k : ℕ} (hn : 1 ≤ n) (hk : 1 ≤ k) :
    degreeMin n k + hmax n k = n + 2 * (k - 1) := by
  have hp := pow_pred_mul hn
  have hpos : 1 ≤ 2 ^ (n - 1) := Nat.one_le_two_pow
  have hQR := Nat.div_add_mod' (k - 1) (2 ^ n)
  have hR : (k - 1) % 2 ^ n < 2 ^ n := Nat.mod_lt _ (by positivity)
  unfold hmax degreeMin
  by_cases hQ : (k - 1) / 2 ^ n = 0
  · rw [ite_eq_left hQ]
    rw [hQ, zero_mul, zero_add] at hQR
    have hk2 : k ≤ 2 ^ n := by omega
    by_cases hs : k < 2 ^ (n - 1)
    · rw [ite_eq_left hs]
      have hl : Nat.log 2 k < n - 1 := Nat.log_lt_of_lt_pow (by omega) hs
      omega
    · rw [ite_eq_right hs]
      have hl := log_add_two_eq hn (by omega) hk2
      have ht := div_le_two (R := k - 1) hn (by omega)
      rw [show k - 1 + 1 = k by omega] at ht
      generalize k / 2 ^ (n - 1) = u at hl ht ⊢
      omega
  · rw [ite_eq_right hQ]
    have hQ1 : 1 ≤ (k - 1) / 2 ^ n := Nat.one_le_iff_ne_zero.2 hQ
    have hQn : 2 ^ n ≤ (k - 1) / 2 ^ n * 2 ^ n := Nat.le_mul_of_pos_left _ (by omega)
    have hs : ¬ k < 2 ^ (n - 1) := by omega
    rw [ite_eq_right hs]
    have hkdiv : k / 2 ^ (n - 1) = 2 * ((k - 1) / 2 ^ n) + ((k - 1) % 2 ^ n + 1) / 2 ^ (n - 1) := by
      have hk' : k = 2 ^ (n - 1) * (2 * ((k - 1) / 2 ^ n)) + ((k - 1) % 2 ^ n + 1) := by
        have : 2 ^ (n - 1) * (2 * ((k - 1) / 2 ^ n)) = (k - 1) / 2 ^ n * 2 ^ n := by rw [hp]; ring
        omega
      conv_lhs => rw [hk']
      rw [Nat.mul_add_div (by positivity)]
    have ht2 := div_le_two (R := (k - 1) % 2 ^ n) hn hR
    have hnt := two_le_n_add (R := (k - 1) % 2 ^ n) hn
    have hkd : k / 2 ^ (n - 1) ≤ k := Nat.div_le_self _ _
    generalize ((k - 1) % 2 ^ n + 1) / 2 ^ (n - 1) = t at hkdiv ht2 hnt ⊢
    generalize k / 2 ^ (n - 1) = u at hkdiv hkd ⊢
    generalize (k - 1) / 2 ^ n = Q at hkdiv hQ1 ⊢
    omega

/-- `h(m) ≤ h_max` for `0 ≤ m ≤ k − 1`. -/
theorem hval_le {n k : ℕ} (hn : 1 ≤ n) (hk : 1 ≤ k) {m : ℕ} (hm : m ≤ k - 1) :
    hval n m ≤ hmax n k := by
  have hQR := Nat.div_add_mod' (k - 1) (2 ^ n)
  have hR : (k - 1) % 2 ^ n < 2 ^ n := Nat.mod_lt _ (by positivity)
  have hqr := Nat.div_add_mod' m (2 ^ n)
  have hr : m % 2 ^ n < 2 ^ n := Nat.mod_lt _ (by positivity)
  have hqQ : m / 2 ^ n ≤ (k - 1) / 2 ^ n := Nat.div_le_div_right hm
  have hs := s2_le_log (m % 2 ^ n)
  unfold hval hmax
  by_cases hQ : (k - 1) / 2 ^ n = 0
  · rw [ite_eq_left hQ]
    rw [hQ, zero_mul, zero_add] at hQR
    have hmlt : m < 2 ^ n := by omega
    have hq0 : m / 2 ^ n = 0 := Nat.div_eq_of_lt hmlt
    have hr0 : m % 2 ^ n = m := Nat.mod_eq_of_lt hmlt
    rw [hq0, hr0]
    rw [hr0] at hs
    have hlog : Nat.log 2 (m + 1) ≤ Nat.log 2 k := Nat.log_mono_right (by omega)
    omega
  · rw [ite_eq_right hQ]
    have hnt := two_le_n_add (R := (k - 1) % 2 ^ n) hn
    rcases Nat.lt_or_ge (m / 2 ^ n) ((k - 1) / 2 ^ n) with hlt | hge
    · have hlog : Nat.log 2 (m % 2 ^ n + 1) ≤ n := by
        calc Nat.log 2 (m % 2 ^ n + 1) ≤ Nat.log 2 (2 ^ n) := Nat.log_mono_right (by omega)
          _ = n := Nat.log_pow (by norm_num) n
      generalize ((k - 1) % 2 ^ n + 1) / 2 ^ (n - 1) = t at hnt ⊢
      omega
    · have hqe : m / 2 ^ n = (k - 1) / 2 ^ n := le_antisymm hqQ hge
      rw [hqe] at hqr
      have hrR : m % 2 ^ n ≤ (k - 1) % 2 ^ n := by
        generalize (k - 1) / 2 ^ n * 2 ^ n = A at hqr hQR
        omega
      have hlog : Nat.log 2 (m % 2 ^ n + 1) ≤ Nat.log 2 ((k - 1) % 2 ^ n + 1) :=
        Nat.log_mono_right (by omega)
      have hb := log_add_two_le hn (show 1 ≤ (k - 1) % 2 ^ n + 1 by omega)
        (show (k - 1) % 2 ^ n + 1 ≤ 2 ^ n by omega)
      rw [hqe]
      generalize ((k - 1) % 2 ^ n + 1) / 2 ^ (n - 1) = t at hnt hb ⊢
      omega

/-- `h_max` is attained at some `0 ≤ m ≤ k − 1`. -/
theorem hval_attain {n k : ℕ} (hn : 1 ≤ n) (hk : 1 ≤ k) :
    ∃ m, m ≤ k - 1 ∧ hval n m = hmax n k := by
  have hp := pow_pred_mul hn
  have hQR := Nat.div_add_mod' (k - 1) (2 ^ n)
  have hR : (k - 1) % 2 ^ n < 2 ^ n := Nat.mod_lt _ (by positivity)
  unfold hmax
  by_cases hQ : (k - 1) / 2 ^ n = 0
  · rw [ite_eq_left hQ]
    rw [hQ, zero_mul, zero_add] at hQR
    have hJ : 2 ^ Nat.log 2 k ≤ k := Nat.pow_log_le_self 2 (by omega)
    have hJ1 : 1 ≤ 2 ^ Nat.log 2 k := Nat.one_le_two_pow
    have hlt : 2 ^ Nat.log 2 k - 1 < 2 ^ n := by omega
    refine ⟨2 ^ Nat.log 2 k - 1, by omega, ?_⟩
    have := hval_eq n 0 hlt
    rw [zero_mul, zero_add, mul_zero, zero_add] at this
    rw [this, s2_two_pow_sub_one]
  · rw [ite_eq_right hQ]
    have hQ1 : 1 ≤ (k - 1) / 2 ^ n := Nat.one_le_iff_ne_zero.2 hQ
    rcases Nat.lt_or_ge ((k - 1) % 2 ^ n + 1) (2 ^ (n - 1)) with hsmall | hbig
    · -- t = 0: take m = (Q−1)·2^n + (2^n − 1) = Q·2^n − 1
      have ht : ((k - 1) % 2 ^ n + 1) / 2 ^ (n - 1) = 0 := Nat.div_eq_of_lt hsmall
      have hn2 : 2 ≤ n := by
        by_contra hc
        rw [show n - 1 = 0 by omega, pow_zero] at hsmall
        omega
      have hpos : 1 ≤ 2 ^ n := Nat.one_le_two_pow
      refine ⟨((k - 1) / 2 ^ n - 1) * 2 ^ n + (2 ^ n - 1), ?_, ?_⟩
      · have hsplit : ((k - 1) / 2 ^ n - 1) * 2 ^ n + 2 ^ n = (k - 1) / 2 ^ n * 2 ^ n := by
          rw [← Nat.succ_mul, Nat.succ_eq_add_one, Nat.sub_add_cancel hQ1]
        generalize ((k - 1) / 2 ^ n - 1) * 2 ^ n = B at hsplit ⊢
        generalize (k - 1) / 2 ^ n * 2 ^ n = A at hsplit hQR
        omega
      · rw [hval_eq n _ (by omega), s2_two_pow_sub_one, ht]
        generalize (k - 1) / 2 ^ n = Q at hQ1 ⊢
        omega
    · -- t ≥ 1: take m = Q·2^n + (2^λ − 1), λ = ⌊log₂(R+1)⌋
      have hl := log_add_two_eq hn hbig (show (k - 1) % 2 ^ n + 1 ≤ 2 ^ n by omega)
      have hlam : 2 ^ Nat.log 2 ((k - 1) % 2 ^ n + 1) ≤ (k - 1) % 2 ^ n + 1 :=
        Nat.pow_log_le_self 2 (by omega)
      have hlam1 : 1 ≤ 2 ^ Nat.log 2 ((k - 1) % 2 ^ n + 1) := Nat.one_le_two_pow
      refine ⟨(k - 1) / 2 ^ n * 2 ^ n + (2 ^ Nat.log 2 ((k - 1) % 2 ^ n + 1) - 1), ?_, ?_⟩
      · generalize (k - 1) / 2 ^ n * 2 ^ n = A at hQR ⊢
        omega
      · rw [hval_eq n _ (by omega), s2_two_pow_sub_one]
        generalize ((k - 1) % 2 ^ n + 1) / 2 ^ (n - 1) = t at hl ⊢
        omega

/-- **The minimum over the origin order, by the digit argument.** `min_{ℓ<k} Φ(n,k,ℓ) = D(n,k)`. -/
theorem min_phi_direct {n k : ℕ} (hn : 1 ≤ n) (hk : 1 ≤ k) :
    (∀ ℓ, ℓ < k → degreeMin n k ≤ Phi n k ℓ) ∧ ∃ ℓ, ℓ < k ∧ Phi n k ℓ = degreeMin n k := by
  have hD := degreeMin_add_hmax hn hk
  refine ⟨fun ℓ hℓ => ?_, ?_⟩
  · have h1 := phi_add_hval (n := n) hℓ
    have h2 := hval_le hn hk (m := k - ℓ - 1) (by omega)
    omega
  · obtain ⟨m, hm, hmax⟩ := hval_attain hn hk
    refine ⟨k - 1 - m, by omega, ?_⟩
    have h1 := phi_add_hval (n := n) (k := k) (ℓ := k - 1 - m) (by omega)
    rw [show k - (k - 1 - m) - 1 = m by omega] at h1
    omega

/-- **Which origin orders are extremal.** `Φ(n,k,ℓ) = D(n,k)` iff `h(k − ℓ − 1)` is maximal. -/
theorem phi_eq_degreeMin_iff {n k ℓ : ℕ} (hn : 1 ≤ n) (hℓ : ℓ < k) :
    Phi n k ℓ = degreeMin n k ↔ ∀ ℓ', ℓ' < k → hval n (k - ℓ' - 1) ≤ hval n (k - ℓ - 1) := by
  have hk : 1 ≤ k := by omega
  have hmin := min_phi_direct hn hk
  have h := phi_add_hval (n := n) hℓ
  constructor
  · intro heq ℓ' hℓ'
    have h' := phi_add_hval (n := n) hℓ'
    have := hmin.1 ℓ' hℓ'
    omega
  · intro hall
    obtain ⟨ℓ0, hℓ0, heq0⟩ := hmin.2
    have h0 := phi_add_hval (n := n) hℓ0
    have := hall ℓ0 hℓ0
    have := hmin.1 ℓ hℓ
    omega

/-- For `1 ≤ k ≤ 2^n`: `Φ(n,k,ℓ) = D(n,k)` iff `s₂(k − ℓ − 1) = ⌊log₂k⌋`. -/
theorem extremal_of_le_two_pow {n k ℓ : ℕ} (hn : 1 ≤ n) (hk2 : k ≤ 2 ^ n) (hℓ : ℓ < k) :
    Phi n k ℓ = degreeMin n k ↔ s2 (k - ℓ - 1) = Nat.log 2 k := by
  have hk : 1 ≤ k := by omega
  have hD := degreeMin_add_hmax hn hk
  have hQ : (k - 1) / 2 ^ n = 0 := Nat.div_eq_of_lt (by omega)
  unfold hmax at hD
  rw [ite_eq_left hQ] at hD
  have h := phi_add_hval (n := n) hℓ
  have hv : hval n (k - ℓ - 1) = s2 (k - ℓ - 1) := by
    have := hval_eq n 0 (show k - ℓ - 1 < 2 ^ n by omega)
    rwa [zero_mul, zero_add, mul_zero, zero_add] at this
  rw [hv] at h
  omega

/-- For `1 ≤ k ≤ 2^n`, the origin order `ℓ = k − 2^⌊log₂k⌋` attains `D(n,k)`. -/
theorem extremal_example {n k : ℕ} (hn : 1 ≤ n) (hk : 1 ≤ k) (hk2 : k ≤ 2 ^ n) :
    k - 2 ^ Nat.log 2 k < k ∧ Phi n k (k - 2 ^ Nat.log 2 k) = degreeMin n k := by
  have hJ : 2 ^ Nat.log 2 k ≤ k := Nat.pow_log_le_self 2 (by omega)
  have hJ1 : 1 ≤ 2 ^ Nat.log 2 k := Nat.one_le_two_pow
  have hlt : k - 2 ^ Nat.log 2 k < k := by omega
  refine ⟨hlt, (extremal_of_le_two_pow hn hk2 hlt).2 ?_⟩
  rw [show k - (k - 2 ^ Nat.log 2 k) - 1 = 2 ^ Nat.log 2 k - 1 by omega, s2_two_pow_sub_one]

end MathResearch.PerOrderMinimumDirect
