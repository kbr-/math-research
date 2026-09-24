/-
Claim: third-party:BBDM-hyperplane-cover-large-k
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-09-24-complete-degree
Scope: Polynomial form of the upper bound in Bishnoi, Boyadzhiyska, Das and Mészáros, "Subspace coverings
with multiplicities" (arXiv:2101.11947v1, Theorem 1.2(a) with d = 1), for k ≥ 2^(n−1): writing
k = a·2^(n−1) + b with 0 ≤ b < 2^(n−1), the product of a copies of all 2^n − 1 affine hyperplanes avoiding
the origin, u·x = 1 (u ≠ 0), and b copies of the parallel pair x₁ = 0, x₁ = 1, is a k-admissible
polynomial over F_2 of total degree at most 2k − ⌊k/2^(n−1)⌋. (Their range 2^(n−2) ≤ k < 2^(n−1) is
covered by claims/PerOrderConstruction.lean.)
Declarations: MathResearch.ThirdParty.HyperplaneCoverUpperBound.card_dot_eq_one MathResearch.ThirdParty.HyperplaneCoverUpperBound.hyperplane_cover_upper_bound
-/
import claims.BinaryMultiplicityDegreeFormula

namespace MathResearch.ThirdParty.HyperplaneCoverUpperBound

open MvPolynomial MathResearch.HasseMultiplicity MathResearch.LinearFormAvoidance
open MathResearch.TruncatedProduct MathResearch.BinaryMultiplicityDegreeFormula

noncomputable section

/-- The dot product `u · x` over `𝔽₂`. -/
def dot {n : ℕ} (u x : Fin n → ZMod 2) : ZMod 2 := ∑ i, u i * x i

/-- For `x ≠ 0`, exactly half of all `u` satisfy `u · x = 1`. -/
theorem card_dot_eq_one {n : ℕ} {x : Fin n → ZMod 2} (hx : x ≠ 0) :
    (Finset.univ.filter (fun u : Fin n → ZMod 2 => dot u x = 1)).card = 2 ^ (n - 1) := by
  classical
  obtain ⟨i, hi⟩ := Function.ne_iff.1 hx
  have hxi : x i = 1 := by
    generalize hxv : x i = v at hi
    fin_cases v
    · exact absurd rfl hi
    · rfl
  set flip : (Fin n → ZMod 2) → (Fin n → ZMod 2) := fun u => Function.update u i (u i + 1)
  have hflip : ∀ u, dot (flip u) x = dot u x + 1 := by
    intro u
    simp only [dot, flip]
    rw [← Finset.add_sum_erase _ _ (Finset.mem_univ i), ← Finset.add_sum_erase _ _ (Finset.mem_univ i)]
    have hrest : ∑ j ∈ Finset.univ.erase i, Function.update u i (u i + 1) j * x j =
        ∑ j ∈ Finset.univ.erase i, u j * x j := by
      apply Finset.sum_congr rfl
      intro j hj
      rw [Function.update_of_ne (Finset.ne_of_mem_erase hj)]
    rw [hrest, Function.update_self, hxi]
    ring
  have hinv : ∀ u, flip (flip u) = u := by
    intro u
    funext j
    by_cases hj : j = i
    · subst hj
      simp only [flip, Function.update_self]
      rw [add_assoc, show (1 : ZMod 2) + 1 = 0 from rfl, add_zero]
    · simp [flip, Function.update_of_ne hj]
  have hbij : (Finset.univ.filter (fun u : Fin n → ZMod 2 => dot u x = 1)).card =
      (Finset.univ.filter (fun u : Fin n → ZMod 2 => ¬ dot u x = 1)).card := by
    apply Finset.card_nbij' flip flip
    · intro u hu
      simp only [Finset.coe_filter, Finset.mem_univ, true_and, Set.mem_ofPred_eq] at hu ⊢
      rw [hflip, hu]; decide
    · intro u hu
      simp only [Finset.coe_filter, Finset.mem_univ, true_and, Set.mem_ofPred_eq] at hu ⊢
      rw [hflip]
      generalize hd : dot u x = d at hu
      fin_cases d
      · decide
      · exact absurd rfl hu
    · intro u _; exact hinv u
    · intro u _; exact hinv u
  have htotal := Finset.card_filter_add_card_filter_not (s := (Finset.univ : Finset (Fin n → ZMod 2)))
    (fun u => dot u x = 1)
  rw [Finset.card_univ, Fintype.card_fun, ZMod.card, Fintype.card_fin, ← hbij] at htotal
  have hn : 1 ≤ n := by
    rcases Nat.eq_zero_or_pos n with rfl | h
    · exact absurd (Subsingleton.elim x 0) hx
    · exact h
  have h2 : 2 ^ n = 2 * 2 ^ (n - 1) := by
    rw [← pow_succ']; congr 1; omega
  omega

theorem eval_linForm {n : ℕ} (u x : Fin n → ZMod 2) : eval x (linForm u) = dot u x := by
  simp [linForm, dot]

theorem totalDegree_linForm_le {n : ℕ} (u : Fin n → ZMod 2) : (linForm u).totalDegree ≤ 1 := by
  apply (totalDegree_finsetSum _ _).trans
  apply Finset.sup_le
  intro i _
  apply (totalDegree_mul _ _).trans
  simp [totalDegree_C, totalDegree_X]

/-- **Hyperplane covers** (polynomial form of [BBDM, Theorem 1.2(a)], `d = 1`, `k ≥ 2^(n−1)`). -/
theorem hyperplane_cover_upper_bound {n k : ℕ} (hn : 1 ≤ n) (hk : 2 ^ (n - 1) ≤ k) :
    ∃ P : MvPolynomial (Fin n) (ZMod 2), Admissible n k P ∧
      P.totalDegree ≤ 2 * k - k / 2 ^ (n - 1) := by
  classical
  set m := 2 ^ (n - 1) with hm
  have hmpos : 0 < m := Nat.two_pow_pos _
  set a := k / m
  set b := k % m
  have hka : a * m + b = k := by rw [mul_comm]; exact Nat.div_add_mod k m
  have hb : b < m := Nat.mod_lt k hmpos
  have ha : 1 ≤ a := Nat.one_le_div_iff hmpos |>.2 hk
  set T := Finset.univ.filter (fun u : Fin n → ZMod 2 => u ≠ 0)
  set F : MvPolynomial (Fin n) (ZMod 2) := ∏ u ∈ T, (1 + linForm u)
  set i1 : Fin n := ⟨0, hn⟩
  set P := F ^ a * (X i1 ^ 2 + X i1) ^ b
  have hF : ∀ x : Fin n → ZMod 2, x ≠ 0 → (m : ℕ∞) ≤ mult x F := by
    intro x hx
    refine le_trans ?_ (le_mult_prod x T _)
    have hcount : (T.filter (fun u => dot u x = 1)).card = m := by
      rw [hm, ← card_dot_eq_one hx]
      congr 1
      ext u
      simp only [T, Finset.mem_filter, Finset.mem_univ, true_and]
      constructor
      · rintro ⟨_, h⟩; exact h
      · intro h
        refine ⟨?_, h⟩
        rintro rfl
        simp [dot] at h
    calc (m : ℕ∞) = ((T.filter (fun u => dot u x = 1)).card : ℕ∞) := by rw [hcount]
      _ = ∑ u ∈ T, (if dot u x = 1 then (1 : ℕ∞) else 0) := by
          rw [Finset.sum_boole]
      _ ≤ ∑ u ∈ T, mult x (1 + linForm u) := by
          apply Finset.sum_le_sum
          intro u _
          split_ifs with h
          · rw [one_le_mult_iff, map_add, map_one, eval_linForm, h]; decide
          · exact zero_le
  have hF0 : mult 0 F = 0 := by
    have h0 : ∀ u : Fin n → ZMod 2, eval 0 (1 + linForm u) = 1 := by
      intro u; rw [map_add, map_one, eval_linForm]; simp [dot]
    rw [mult_eq_zero_iff, map_prod, Finset.prod_congr rfl (fun u _ => h0 u), Finset.prod_const_one]
    exact one_ne_zero
  refine ⟨P, ⟨?_, ?_⟩, ?_⟩
  · intro x hx
    refine le_trans ?_ (add_le_mult_mul x _ _)
    have h1 : ((a * m : ℕ) : ℕ∞) ≤ mult x (F ^ a) := by
      calc ((a * m : ℕ) : ℕ∞) = (a : ℕ∞) * m := by push_cast; ring
        _ ≤ a * mult x F := by gcongr; exact hF x hx
        _ ≤ _ := le_mult_pow x _ _
    have h2 : (b : ℕ∞) ≤ mult x ((X i1 ^ 2 + X i1 : MvPolynomial (Fin n) (ZMod 2)) ^ b) := by
      calc (b : ℕ∞) = b * 1 := by ring
        _ ≤ b * mult x (X i1 ^ 2 + X i1 : MvPolynomial (Fin n) (ZMod 2)) := by
            gcongr; exact one_le_mult_y x i1
        _ ≤ _ := le_mult_pow x _ _
    calc (k : ℕ∞) = ((a * m : ℕ) : ℕ∞) + b := by rw [← hka]; push_cast; ring
      _ ≤ _ := add_le_add h1 h2
  · have hFa : mult 0 (F ^ a) = 0 := by
      rw [mult_eq_zero_iff, map_pow]
      have : eval 0 F ≠ 0 := (mult_eq_zero_iff 0 F).1 hF0
      exact pow_ne_zero _ this
    rw [mult_mul, hFa, PerOrderConstruction.mult_zero_y_pow, zero_add]
    exact_mod_cast (show b < k by omega)
  · have hdegF : F.totalDegree ≤ 2 ^ n - 1 := by
      apply (totalDegree_finsetProd _ _).trans
      calc ∑ u ∈ T, (1 + linForm u).totalDegree ≤ ∑ u ∈ T, 1 := by
            apply Finset.sum_le_sum
            intro u _
            apply (totalDegree_add _ _).trans
            apply max_le
            · simp
            · exact totalDegree_linForm_le u
        _ = 2 ^ n - 1 := by
            simp only [T]
            rw [Finset.sum_const, smul_eq_mul, mul_one, Finset.filter_ne',
              Finset.card_erase_of_mem (Finset.mem_univ _), Finset.card_univ, Fintype.card_fun,
              ZMod.card, Fintype.card_fin]
    have hdegY : ((X i1 ^ 2 + X i1 : MvPolynomial (Fin n) (ZMod 2)) ^ b).totalDegree ≤ 2 * b := by
      apply (totalDegree_pow _ _).trans
      rw [mul_comm]
      gcongr
      apply (totalDegree_add _ _).trans
      apply max_le
      · apply (totalDegree_pow _ _).trans
        simp [totalDegree_X]
      · simp [totalDegree_X]
    have h2n : 2 ^ n = 2 * m := by
      rw [hm, ← pow_succ']; congr 1; omega
    have hdegFa : (F ^ a).totalDegree ≤ a * (2 ^ n - 1) :=
      (totalDegree_pow _ _).trans (Nat.mul_le_mul_left a hdegF)
    have ham : a ≤ a * m := Nat.le_mul_of_pos_right a hmpos
    have hexp : a * (2 ^ n - 1) = 2 * (a * m) - a := by
      rw [h2n, Nat.mul_sub, mul_one]; ring_nf
    apply (totalDegree_mul _ _).trans
    omega

end

end MathResearch.ThirdParty.HyperplaneCoverUpperBound
