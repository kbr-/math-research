/-
Claim: lem:per-order-value-arithmetic
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#per-order-value-arithmetic
Scope: Consequences of the per-order value Φ(n,k,ℓ) = n + 2ℓ + Σ_{j<n} ⌊(k−ℓ−1)/2^j⌋ (ℓ < k) used in the
preprint's remarks: (1) Φ + 2q + s₂(r) = n + 2(k−1) for k − ℓ − 1 = q2^n + r, 0 ≤ r < 2^n;
(2) Φ + s₂(k−ℓ−1) < n + 2(k−1) when k − ℓ − 1 ≥ 2^n, and the construction y₁^ℓ F^(2q) g_(r+1) has degree
below n + 2k − 2 − s₂(k−ℓ−1) there; (3) Φ(n, k + 2^n, ℓ) = Φ(n,k,ℓ) + 2^(n+1) − 2; (4) Φ = n + 2k − 2 −
s₂(k−ℓ−1) when k − 1 ≤ n, in particular when k ≥ 2 and n ≥ 2k − 3; (5) Φ(n,k,k−1) = n + 2k − 2;
(6) Φ(n+1,k,ℓ) = Φ(n,k,ℓ) + 1 + ⌊(k−ℓ−1)/2^n⌋; (7) the construction has total degree exactly Φ;
(8) for k − ℓ − 1 < 2^n every admissible P of origin order ℓ has degree ≥ n + 2k − 2 − s₂(k−ℓ−1);
(9) s₂(k−ℓ−1) ≥ 1 for ℓ + 1 < k; (10) the examples Φ(1,3,0) = 3 with (1 + x)³ of degree 3, multiplicity
≥ 3 at 1 and order 0 at 0, against 1 + 6 − 2 − s₂(2) = 4, and Φ(2,5,0) = 8 against 2 + 10 − 2 − s₂(4) = 9;
(11) mult_a(P) ≤ ord₀ P(a + z) for every substitution z whose entries have no constant term;
(12) F has 2^n − 1 factors, and F² has multiplicity ≥ 2^n at nonzero points and degree
≤ 2^(n+1) − 2; (13) with δ(n,k,ℓ) the least element of deltaSet (degrees of polynomials with
multiplicity ≥ k off the origin and exactly ℓ at it), δ = Φ, and items (4)–(6), (10) restated for δ.
Declarations: MathResearch.PerOrderArithmetic.phi_add_eq MathResearch.PerOrderArithmetic.phi_lt_menezes MathResearch.PerOrderArithmetic.construction_lt_menezes MathResearch.PerOrderArithmetic.phi_add_block MathResearch.PerOrderArithmetic.phi_of_le MathResearch.PerOrderArithmetic.phi_of_real_range MathResearch.PerOrderArithmetic.phi_top MathResearch.PerOrderArithmetic.phi_succ MathResearch.PerOrderArithmetic.totalDegree_construction MathResearch.PerOrderArithmetic.menezes_form_optimal MathResearch.PerOrderArithmetic.one_le_s2 MathResearch.PerOrderArithmetic.example_one MathResearch.PerOrderArithmetic.cube_example MathResearch.PerOrderArithmetic.example_two MathResearch.PerOrderArithmetic.mult_le_mult_zero_subst MathResearch.PerOrderArithmetic.card_nonzero MathResearch.PerOrderArithmetic.mult_hypProd_sq MathResearch.PerOrderArithmetic.totalDegree_hypProd_sq MathResearch.PerOrderArithmetic.deltaSet MathResearch.PerOrderArithmetic.isLeast_deltaSet MathResearch.PerOrderArithmetic.delta_succ MathResearch.PerOrderArithmetic.delta_of_real_range MathResearch.PerOrderArithmetic.delta_top MathResearch.PerOrderArithmetic.delta_examples
-/
import claims.PerOrderValue
import claims.BinaryDigitSums

namespace MathResearch.PerOrderArithmetic

open MvPolynomial MathResearch.HasseMultiplicity MathResearch.TruncatedProduct
open MathResearch.BinaryDigitSums MathResearch.PerOrderLegendre MathResearch.PerOrderUpperBound
open MathResearch.PerOrderValue MathResearch.PerOrderExpansion MathResearch.OneDimensionStep

/-- Substitutions without constant term do not lower the order: `mult_a(P) ≤ ord₀ P(a + z)`. -/
theorem mult_le_mult_zero_subst {σ : Type*} (a : σ → ZMod 2) (z : σ → MvPolynomial σ (ZMod 2))
    (hz : ∀ i, 1 ≤ mult 0 (z i)) (P : MvPolynomial σ (ZMod 2)) :
    mult a P ≤ mult 0 (aeval (fun i => C (a i) + z i) P) := by
  have hcomp : aeval (fun i => C (a i) + z i) P = aeval z (shift a P) := by
    rw [shift, ← AlgHom.comp_apply, comp_aeval]
    refine congrArg (fun f : σ → MvPolynomial σ (ZMod 2) => aeval f P) ?_
    funext i
    simp [add_comm]
  rw [hcomp, mult_eq_mult_zero_shift]
  exact le_mult_zero_aeval z hz _

/-- **Legendre form of Φ.** With `q = ⌊(k−ℓ−1)/2^n⌋` and `r = (k−ℓ−1) mod 2^n`:
`Φ + 2q + s₂(r) = n + 2(k − 1)`. -/
theorem phi_add_eq {n k ℓ : ℕ} (hℓ : ℓ < k) :
    Phi n k ℓ + 2 * ((k - ℓ - 1) / 2 ^ n) + s2 ((k - ℓ - 1) % 2 ^ n) = n + 2 * (k - 1) := by
  have h := legendre n ((k - ℓ - 1) / 2 ^ n) ((k - ℓ - 1) % 2 ^ n)
    (Nat.mod_lt _ (by positivity))
  rw [Nat.div_add_mod' (k - ℓ - 1) (2 ^ n)] at h
  unfold Phi
  omega

/-- **Below Menezes' form.** If `k − ℓ − 1 ≥ 2^n`, then `Φ < n + 2k − 2 − s₂(k − ℓ − 1)`. -/
theorem phi_lt_menezes {n k ℓ : ℕ} (hℓ : ℓ < k) (h : 2 ^ n ≤ k - ℓ - 1) :
    Phi n k ℓ + s2 (k - ℓ - 1) < n + 2 * (k - 1) := by
  have hq : 1 ≤ (k - ℓ - 1) / 2 ^ n := (Nat.one_le_div_iff (by positivity)).2 h
  have hs : s2 (k - ℓ - 1) = s2 ((k - ℓ - 1) / 2 ^ n) + s2 ((k - ℓ - 1) % 2 ^ n) := by
    conv_lhs => rw [← Nat.div_add_mod' (k - ℓ - 1) (2 ^ n)]
    exact s2_mul_two_pow_add _ (Nat.mod_lt _ (by positivity))
  have hle := s2_le_self ((k - ℓ - 1) / 2 ^ n)
  have := phi_add_eq (n := n) hℓ
  omega

/-- The construction `y₁^ℓ F^(2q) g_(r+1)` beats Menezes' form when `k − ℓ − 1 ≥ 2^n`. -/
theorem construction_lt_menezes {n k ℓ : ℕ} (hℓ : ℓ < k) (h : 2 ^ n ≤ k - ℓ - 1) (i1 : Fin n) :
    (construction n k ℓ i1).totalDegree + s2 (k - ℓ - 1) < n + 2 * (k - 1) :=
  lt_of_le_of_lt (Nat.add_le_add_right (construction_spec hℓ i1).2.2 _) (phi_lt_menezes hℓ h)

/-- **Blocks of `2^n`.** `Φ(n, k + 2^n, ℓ) = Φ(n, k, ℓ) + 2^(n+1) − 2`. -/
theorem phi_add_block {n k ℓ : ℕ} (hℓ : ℓ < k) :
    Phi n (k + 2 ^ n) ℓ = Phi n k ℓ + (2 ^ (n + 1) - 2) := by
  have h1 := phi_add_eq (n := n) hℓ
  have h2 := phi_add_eq (n := n) (k := k + 2 ^ n) (ℓ := ℓ)
    (lt_of_lt_of_le hℓ (Nat.le_add_right k _))
  have hm : k + 2 ^ n - ℓ - 1 = (k - ℓ - 1) + 2 ^ n := by
    generalize 2 ^ n = N; omega
  rw [hm, Nat.add_div_right _ (by positivity), Nat.add_mod_right] at h2
  have hp : 2 ^ (n + 1) = 2 * 2 ^ n := by rw [pow_succ]; ring
  have hpos : 1 ≤ 2 ^ n := Nat.one_le_two_pow
  have hk2 : k + 2 ^ n - 1 = (k - 1) + 2 ^ n := by
    generalize 2 ^ n = N at hpos ⊢; omega
  rw [hk2] at h2
  rw [hp]
  generalize 2 ^ n = N at h1 h2 hpos ⊢
  omega

/-- **Menezes' range.** For `k − 1 ≤ n`, `Φ = n + 2k − 2 − s₂(k − ℓ − 1)`. -/
theorem phi_of_le {n k ℓ : ℕ} (hℓ : ℓ < k) (h : k - 1 ≤ n) :
    Phi n k ℓ = n + 2 * k - 2 - s2 (k - ℓ - 1) :=
  phi_of_lt_two_pow hℓ (lt_of_le_of_lt (by omega) Nat.lt_two_pow_self)

/-- The range of Sauermann–Wigderson, `k ≥ 2` and `n ≥ 2k − 3`, lies in Menezes' range. -/
theorem phi_of_real_range {n k ℓ : ℕ} (hℓ : ℓ < k) (hk : 2 ≤ k) (h : 2 * k - 3 ≤ n) :
    Phi n k ℓ = n + 2 * k - 2 - s2 (k - ℓ - 1) :=
  phi_of_le hℓ (by omega)

/-- **The top origin order.** `Φ(n, k, k − 1) = n + 2k − 2`. -/
theorem phi_top {n k : ℕ} (hk : 1 ≤ k) : Phi n k (k - 1) = n + 2 * k - 2 := by
  unfold Phi
  rw [show k - (k - 1) - 1 = 0 by omega]
  simp only [Nat.zero_div, Finset.sum_const_zero]
  omega

/-- **One more dimension.** `Φ(n+1, k, ℓ) = Φ(n, k, ℓ) + 1 + ⌊(k−ℓ−1)/2^n⌋`. -/
theorem phi_succ (n k ℓ : ℕ) : Phi (n + 1) k ℓ = Phi n k ℓ + 1 + (k - ℓ - 1) / 2 ^ n := by
  unfold Phi
  rw [Finset.sum_range_succ]
  ring

/-- The construction has total degree exactly `Φ`. -/
theorem totalDegree_construction {n k ℓ : ℕ} (hℓ : ℓ < k) (i1 : Fin n) :
    (construction n k ℓ i1).totalDegree = Phi n k ℓ := by
  have hn : 1 ≤ n := Nat.one_le_iff_ne_zero.2 (fun h => by subst h; exact i1.elim0)
  have hspec := construction_spec hℓ i1
  exact le_antisymm hspec.2.2 ((per_order_value hn hℓ).2 _ hspec.1 hspec.2.1)

/-- **Menezes' form is optimal when `k − ℓ − 1 < 2^n`.** -/
theorem menezes_form_optimal {n k ℓ : ℕ} (hn : 1 ≤ n) (hℓ : ℓ < k) (hm : k - ℓ - 1 < 2 ^ n)
    (P : MvPolynomial (Fin n) (ZMod 2)) (hP : ∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P)
    (h0 : mult 0 P = ℓ) : n + 2 * k - 2 - s2 (k - ℓ - 1) ≤ P.totalDegree := by
  rw [← phi_of_lt_two_pow hℓ hm]
  exact (per_order_value hn hℓ).2 P hP h0

/-- `s₂(k − ℓ − 1) ≥ 1` for `ℓ + 1 < k`. -/
theorem one_le_s2 {k ℓ : ℕ} (h : ℓ + 1 < k) : 1 ≤ s2 (k - ℓ - 1) := s2_pos (by omega)

/-- `Φ(1, 3, 0) = 3`, while Menezes' form gives `1 + 6 − 2 − s₂(2) = 4`. -/
theorem example_one : Phi 1 3 0 = 3 ∧ 1 + 2 * 3 - 2 - s2 (3 - 0 - 1) = 4 := by
  refine ⟨by decide, ?_⟩
  rw [show 3 - 0 - 1 = 2 ^ 1 by norm_num, s2_two_pow]

/-- `(1 + x)³` over `𝔽₂` in one variable: multiplicity `≥ 3` at `1`, order `0` at `0`, total degree `3`. -/
theorem cube_example :
    let P : MvPolynomial (Fin 1) (ZMod 2) := (1 + X 0) ^ 3
    (∀ a : Fin 1 → ZMod 2, a ≠ 0 → ((3 : ℕ) : ℕ∞) ≤ mult a P) ∧ mult 0 P = 0 ∧ P.totalDegree = 3 := by
  intro P
  have hlin : ∀ a : Fin 1 → ZMod 2, a ≠ 0 → 1 ≤ mult a (1 + X 0 : MvPolynomial (Fin 1) (ZMod 2)) := by
    intro a ha
    rw [one_le_mult_iff]
    have h0 : a 0 = 1 := by
      have hne : a 0 ≠ 0 := fun h => ha (funext fun i => by fin_cases i; exact h)
      have key : ∀ x : ZMod 2, x ≠ 0 → x = 1 := by decide
      exact key _ hne
    simp only [map_add, map_one, eval_X, h0]
    decide
  have hmult : ∀ a : Fin 1 → ZMod 2, a ≠ 0 → ((3 : ℕ) : ℕ∞) ≤ mult a P := by
    intro a ha
    have h1 := hlin a ha
    show ((3 : ℕ) : ℕ∞) ≤ mult a ((1 + X 0) ^ 3)
    rw [pow_three, mult_mul, mult_mul]
    calc ((3 : ℕ) : ℕ∞) = 1 + (1 + 1) := by norm_num
      _ ≤ _ := add_le_add h1 (add_le_add h1 h1)
  have hzero : mult 0 P = 0 := by
    rw [mult_eq_zero_iff]
    simp [P]
  refine ⟨hmult, hzero, le_antisymm ?_ ?_⟩
  · calc P.totalDegree ≤ 3 * (1 + X 0 : MvPolynomial (Fin 1) (ZMod 2)).totalDegree :=
          totalDegree_pow _ _
      _ ≤ 3 * 1 := by
          apply Nat.mul_le_mul_left
          calc (1 + X 0 : MvPolynomial (Fin 1) (ZMod 2)).totalDegree
              ≤ max (1 : MvPolynomial (Fin 1) (ZMod 2)).totalDegree (X 0).totalDegree :=
                totalDegree_add _ _
            _ ≤ 1 := by simp [totalDegree_X]
      _ = 3 := by norm_num
  · have := (per_order_value (n := 1) (k := 3) (ℓ := 0) le_rfl (by norm_num)).2 P hmult
      (by rw [hzero]; rfl)
    rwa [example_one.1] at this

/-- `Φ(2, 5, 0) = 8`, while Menezes' form gives `2 + 10 − 2 − s₂(4) = 9`. -/
theorem example_two : Phi 2 5 0 = 8 ∧ 2 + 2 * 5 - 2 - s2 (5 - 0 - 1) = 9 := by
  refine ⟨by decide, ?_⟩
  rw [show 5 - 0 - 1 = 2 ^ 2 by norm_num, s2_two_pow]

/-- `F` has `2^n − 1` factors, one for each hyperplane `u · x = 1` (`u ≠ 0`) avoiding the origin. -/
theorem card_nonzero (n : ℕ) :
    (Finset.univ.filter (fun u : Fin n → ZMod 2 => u ≠ 0)).card = 2 ^ n - 1 := by
  rw [Finset.filter_ne', Finset.card_erase_of_mem (Finset.mem_univ _), Finset.card_univ,
    Fintype.card_fun, ZMod.card, Fintype.card_fin]

/-- `F²` has multiplicity `≥ 2^n` at every nonzero point. -/
theorem mult_hypProd_sq {n : ℕ} (hn : 1 ≤ n) {x : Fin n → ZMod 2} (hx : x ≠ 0) :
    ((2 ^ n : ℕ) : ℕ∞) ≤ mult x (hypProd n ^ 2) := by
  rw [sq]
  refine le_trans ?_ (add_le_mult_mul x _ _)
  have h2 : (2 ^ n : ℕ) = 2 ^ (n - 1) + 2 ^ (n - 1) := by
    rw [← two_mul, ← pow_succ']; congr 1; omega
  rw [h2, Nat.cast_add]
  exact add_le_add (mult_hypProd hx) (mult_hypProd hx)

/-- `F²` has total degree `≤ 2^(n+1) − 2`. -/
theorem totalDegree_hypProd_sq (n : ℕ) : (hypProd n ^ 2).totalDegree ≤ 2 ^ (n + 1) - 2 := by
  have h := totalDegree_hypProd n
  have hp : 2 ^ (n + 1) = 2 * 2 ^ n := by rw [pow_succ']
  calc (hypProd n ^ 2).totalDegree ≤ 2 * (hypProd n).totalDegree := totalDegree_pow _ _
    _ ≤ 2 ^ (n + 1) - 2 := by rw [hp]; omega

/-- The degrees of polynomials with multiplicity `≥ k` at every nonzero point and exactly `ℓ` at the
origin; `δ(n,k,ℓ)` is its least element. -/
def deltaSet (n k ℓ : ℕ) : Set ℕ :=
  {d | ∃ P : MvPolynomial (Fin n) (ZMod 2), (∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P) ∧
    mult 0 P = ℓ ∧ P.totalDegree = d}

/-- `δ(n,k,ℓ) = Φ(n,k,ℓ)`, restating `per_order_value`. -/
theorem isLeast_deltaSet {n k ℓ : ℕ} (hn : 1 ≤ n) (hℓ : ℓ < k) :
    IsLeast (deltaSet n k ℓ) (Phi n k ℓ) := by
  obtain ⟨⟨P, hP, h0, hdeg⟩, hlow⟩ := per_order_value hn hℓ
  exact ⟨⟨P, hP, h0, hdeg⟩, by rintro d ⟨Q, hQ, hQ0, rfl⟩; exact hlow Q hQ hQ0⟩

/-- `δ(n+1,k,ℓ) = δ(n,k,ℓ) + 1 + ⌊(k−ℓ−1)/2^n⌋`, so `δ(n,k,ℓ) + 1 ≤ δ(n+1,k,ℓ)`. -/
theorem delta_succ {n k ℓ d d' : ℕ} (hn : 1 ≤ n) (hℓ : ℓ < k) (h : IsLeast (deltaSet n k ℓ) d)
    (h' : IsLeast (deltaSet (n + 1) k ℓ) d') : d' = d + 1 + (k - ℓ - 1) / 2 ^ n := by
  rw [h.unique (isLeast_deltaSet hn hℓ), h'.unique (isLeast_deltaSet (by omega) hℓ), phi_succ]

/-- In the real range `k ≥ 2`, `n ≥ 2k − 3`: `δ(n,k,ℓ) = n + 2k − 2 − s₂(k − ℓ − 1)`. -/
theorem delta_of_real_range {n k ℓ : ℕ} (hn : 1 ≤ n) (hℓ : ℓ < k) (hk : 2 ≤ k) (h : 2 * k - 3 ≤ n) :
    IsLeast (deltaSet n k ℓ) (n + 2 * k - 2 - s2 (k - ℓ - 1)) := by
  rw [← phi_of_real_range hℓ hk h]; exact isLeast_deltaSet hn hℓ

/-- `δ(n,k,k−1) = n + 2k − 2`. -/
theorem delta_top {n k : ℕ} (hn : 1 ≤ n) (hk : 1 ≤ k) : IsLeast (deltaSet n k (k - 1)) (n + 2 * k - 2) := by
  rw [← phi_top hk]; exact isLeast_deltaSet hn (by omega)

/-- The examples: `δ(1,3,0) = 3` and `δ(2,5,0) = 8`. -/
theorem delta_examples : IsLeast (deltaSet 1 3 0) 3 ∧ IsLeast (deltaSet 2 5 0) 8 := by
  refine ⟨?_, ?_⟩
  · have h := isLeast_deltaSet (n := 1) (k := 3) (ℓ := 0) le_rfl (by norm_num)
    rwa [example_one.1] at h
  · have h := isLeast_deltaSet (n := 2) (k := 5) (ℓ := 0) (by norm_num) (by norm_num)
    rwa [example_two.1] at h

end MathResearch.PerOrderArithmetic
