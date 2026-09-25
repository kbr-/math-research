/-
Claim: thm:per-order-all-dimension-upper-bound
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#per-order-all-dimension-upper-bound
Scope: For n ≥ 1 (a variable i₁) and ℓ < k, write k − ℓ − 1 = q 2^n + r with 0 ≤ r < 2^n. The polynomial
y_1^ℓ F^(2q) g_(r+1) over F_2, with y_1 = x_1² + x_1, F the product of the 2^n − 1 affine forms
1 + u·x (u ≠ 0) and g the truncated product, has Hasse multiplicity ≥ k at every nonzero point,
multiplicity exactly ℓ at the origin, and total degree ≤ Φ(n,k,ℓ) = n + 2ℓ + Σ_{j<n} ⌊(k−ℓ−1)/2^j⌋
(by the Legendre form) (construction_spec), hence some such P exists (per_order_upper_bound). Also the facts about F: multiplicity ≥ 2^(n−1) at nonzero points, value 1 at
the origin, total degree ≤ 2^n − 1 (the steps of the hyperplane-cover proof, restated as lemmas).
Declarations: MathResearch.PerOrderUpperBound.Phi MathResearch.PerOrderUpperBound.construction MathResearch.PerOrderUpperBound.construction_spec MathResearch.PerOrderUpperBound.hypProd MathResearch.PerOrderUpperBound.mult_hypProd MathResearch.PerOrderUpperBound.eval_zero_hypProd MathResearch.PerOrderUpperBound.totalDegree_hypProd MathResearch.PerOrderUpperBound.per_order_upper_bound
-/
import claims.PerOrderLegendre
import claims.PerOrderConstruction
import «third-party-claims».HyperplaneCoverUpperBound

namespace MathResearch.PerOrderUpperBound

open MvPolynomial MathResearch.HasseMultiplicity MathResearch.TruncatedProduct
open MathResearch.LinearFormAvoidance MathResearch.ThirdParty.HyperplaneCoverUpperBound
open MathResearch.PerOrderConstruction MathResearch.PerOrderLegendre

noncomputable section

/-- `Φ(n, k, ℓ) = n + 2ℓ + Σ_{j<n} ⌊(k − ℓ − 1)/2^j⌋`. -/
def Phi (n k ℓ : ℕ) : ℕ := n + 2 * ℓ + ∑ j ∈ Finset.range n, (k - ℓ - 1) / 2 ^ j

/-- The product `F = ∏_{u ≠ 0} (1 + u · x)` of all affine hyperplanes avoiding the origin. -/
def hypProd (n : ℕ) : MvPolynomial (Fin n) (ZMod 2) :=
  ∏ u ∈ Finset.univ.filter (fun u : Fin n → ZMod 2 => u ≠ 0), (1 + linForm u)

/-- `F` vanishes to order `≥ 2^(n−1)` at every nonzero point. -/
theorem mult_hypProd {n : ℕ} {x : Fin n → ZMod 2} (hx : x ≠ 0) :
    ((2 ^ (n - 1) : ℕ) : ℕ∞) ≤ mult x (hypProd n) := by
  classical
  set T := Finset.univ.filter (fun u : Fin n → ZMod 2 => u ≠ 0)
  refine le_trans ?_ (le_mult_prod x T _)
  have hcount : (T.filter (fun u => dot u x = 1)).card = 2 ^ (n - 1) := by
    rw [← card_dot_eq_one hx]
    congr 1
    ext u
    simp only [T, Finset.mem_filter, Finset.mem_univ, true_and]
    constructor
    · rintro ⟨_, h⟩; exact h
    · intro h
      refine ⟨?_, h⟩
      rintro rfl
      simp [dot] at h
  calc ((2 ^ (n - 1) : ℕ) : ℕ∞) = ((T.filter (fun u => dot u x = 1)).card : ℕ∞) := by
        rw [hcount]
    _ = ∑ u ∈ T, (if dot u x = 1 then (1 : ℕ∞) else 0) := by rw [Finset.sum_boole]
    _ ≤ ∑ u ∈ T, mult x (1 + linForm u) := by
        apply Finset.sum_le_sum
        intro u _
        split_ifs with h
        · rw [one_le_mult_iff, map_add, map_one, eval_linForm, h]; decide
        · exact zero_le

theorem eval_zero_hypProd (n : ℕ) : eval 0 (hypProd n) = 1 := by
  rw [hypProd, map_prod]
  apply Finset.prod_eq_one
  intro u _
  rw [map_add, map_one, eval_linForm]
  simp [dot]

theorem totalDegree_hypProd (n : ℕ) : (hypProd n).totalDegree ≤ 2 ^ n - 1 := by
  classical
  apply (totalDegree_finsetProd _ _).trans
  calc ∑ u ∈ Finset.univ.filter (fun u : Fin n → ZMod 2 => u ≠ 0), (1 + linForm u).totalDegree
        ≤ ∑ u ∈ Finset.univ.filter (fun u : Fin n → ZMod 2 => u ≠ 0), 1 := by
          apply Finset.sum_le_sum
          intro u _
          apply (totalDegree_add _ _).trans
          apply max_le
          · simp
          · exact totalDegree_linForm_le u
    _ = 2 ^ n - 1 := by
        rw [Finset.sum_const, smul_eq_mul, mul_one, Finset.filter_ne',
          Finset.card_erase_of_mem (Finset.mem_univ _), Finset.card_univ, Fintype.card_fun,
          ZMod.card, Fintype.card_fin]

/-- The construction `y_i^ℓ F^(2q) g_(r+1)` with `k − ℓ − 1 = q 2^n + r`, `0 ≤ r < 2^n`. -/
def construction (n k ℓ : ℕ) (i1 : Fin n) : MvPolynomial (Fin n) (ZMod 2) :=
  (X i1 ^ 2 + X i1) ^ ℓ * hypProd n ^ (2 * ((k - ℓ - 1) / 2 ^ n)) * g ((k - ℓ - 1) % 2 ^ n + 1)

/-- **The construction** (`thm:per-order-all-dimension-upper-bound`): `y_{i₁}^ℓ F^(2q) g_(r+1)` has
multiplicity `≥ k` at every nonzero point, multiplicity exactly `ℓ` at the origin, and total degree
`≤ Φ(n, k, ℓ)`. -/
theorem construction_spec {n k ℓ : ℕ} (hℓ : ℓ < k) (i1 : Fin n) :
    (∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a (construction n k ℓ i1)) ∧
      mult 0 (construction n k ℓ i1) = ℓ ∧ (construction n k ℓ i1).totalDegree ≤ Phi n k ℓ := by
  classical
  have hn : 1 ≤ n := Nat.one_le_iff_ne_zero.2 (fun h => by subst h; exact i1.elim0)
  unfold construction
  set m := k - ℓ - 1 with hm
  set q := m / 2 ^ n
  set r := m % 2 ^ n
  have hqr : q * 2 ^ n + r = m := by rw [mul_comm]; exact Nat.div_add_mod m (2 ^ n)
  have hr : r < 2 ^ n := Nat.mod_lt _ (by positivity)
  refine ⟨?_, ?_, ?_⟩
  · intro a ha
    have hAB := add_le_mult_mul a ((X i1 ^ 2 + X i1 : MvPolynomial (Fin n) (ZMod 2)) ^ ℓ)
      (hypProd n ^ (2 * q))
    have hABC := add_le_mult_mul a ((X i1 ^ 2 + X i1 : MvPolynomial (Fin n) (ZMod 2)) ^ ℓ *
      hypProd n ^ (2 * q)) (g (r + 1))
    refine le_trans ?_ hABC
    refine le_trans ?_ (add_le_add hAB le_rfl)
    have h1 : (ℓ : ℕ∞) ≤ mult a ((X i1 ^ 2 + X i1 : MvPolynomial (Fin n) (ZMod 2)) ^ ℓ) := by
      calc (ℓ : ℕ∞) = ℓ * 1 := by ring
        _ ≤ ℓ * mult a (X i1 ^ 2 + X i1 : MvPolynomial (Fin n) (ZMod 2)) := by
            gcongr; exact one_le_mult_y a i1
        _ ≤ _ := le_mult_pow a _ _
    have h2 : ((2 * q * 2 ^ (n - 1) : ℕ) : ℕ∞) ≤ mult a (hypProd n ^ (2 * q)) := by
      calc ((2 * q * 2 ^ (n - 1) : ℕ) : ℕ∞) = ((2 * q : ℕ) : ℕ∞) * ((2 ^ (n - 1) : ℕ) : ℕ∞) := by
            push_cast; ring
        _ ≤ ((2 * q : ℕ) : ℕ∞) * mult a (hypProd n) := by gcongr; exact mult_hypProd ha
        _ ≤ _ := le_mult_pow a _ _
    have h3 := mult_g_ge (σ := Fin n) (r + 1) a ha
    have hsum : 2 * q * 2 ^ (n - 1) = q * 2 ^ n := by
      have : 2 ^ n = 2 * 2 ^ (n - 1) := by rw [← pow_succ']; congr 1; omega
      rw [this]; ring
    calc (k : ℕ∞) = (ℓ : ℕ∞) + ((2 * q * 2 ^ (n - 1) : ℕ) : ℕ∞) + ((r + 1 : ℕ) : ℕ∞) := by
          rw [hsum]; push_cast
          have : (k : ℕ∞) = ((ℓ + (q * 2 ^ n + r) + 1 : ℕ) : ℕ∞) := by congr 1; omega
          rw [this]; push_cast; ring
      _ ≤ _ := add_le_add (add_le_add h1 h2) h3
  · rw [mult_mul, mult_mul, mult_zero_y_pow,
      (mult_eq_zero_iff 0 _).2 (by rw [map_pow, eval_zero_hypProd, one_pow]; exact one_ne_zero),
      (mult_eq_zero_iff 0 _).2 (by rw [eval_zero_g]; exact one_ne_zero), add_zero, add_zero]
  · have hy : ((X i1 ^ 2 + X i1 : MvPolynomial (Fin n) (ZMod 2)) ^ ℓ).totalDegree ≤ 2 * ℓ := by
      apply (totalDegree_pow _ _).trans
      rw [mul_comm]
      gcongr
      apply (totalDegree_add _ _).trans
      apply max_le
      · exact (totalDegree_pow _ _).trans (by simp [totalDegree_X])
      · simp [totalDegree_X]
    have hF : (hypProd n ^ (2 * q)).totalDegree ≤ 2 * q * (2 ^ n - 1) :=
      (totalDegree_pow _ _).trans (Nat.mul_le_mul_left _ (totalDegree_hypProd n))
    have hg := totalDegree_g_le (σ := Fin n) (r + 1)
    rw [Fintype.card_fin, Nat.add_sub_cancel] at hg
    have hleg := legendre n q r hr
    rw [hqr] at hleg
    have hs := s2_le_self r
    have h2n : 1 ≤ 2 ^ n := Nat.one_le_two_pow
    have hexp : 2 * q * (2 ^ n - 1) = 2 * (q * 2 ^ n) - 2 * q := by
      rw [Nat.mul_sub, mul_one]; ring_nf
    have hq2 : 2 * q ≤ 2 * (q * 2 ^ n) := by nlinarith
    have hm1 := totalDegree_mul ((X i1 ^ 2 + X i1 : MvPolynomial (Fin n) (ZMod 2)) ^ ℓ *
      hypProd n ^ (2 * q)) (g (r + 1))
    have hm2 := totalDegree_mul ((X i1 ^ 2 + X i1 : MvPolynomial (Fin n) (ZMod 2)) ^ ℓ)
      (hypProd n ^ (2 * q))
    unfold Phi
    rw [← hm]
    omega

/-- Hence `δ(n, k, ℓ) ≤ Φ(n, k, ℓ)`. -/
theorem per_order_upper_bound {n k ℓ : ℕ} (hn : 1 ≤ n) (hℓ : ℓ < k) :
    ∃ P : MvPolynomial (Fin n) (ZMod 2), (∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P) ∧
      mult 0 P = ℓ ∧ P.totalDegree ≤ Phi n k ℓ :=
  ⟨construction n k ℓ ⟨0, hn⟩, construction_spec hℓ ⟨0, hn⟩⟩

end

end MathResearch.PerOrderUpperBound
