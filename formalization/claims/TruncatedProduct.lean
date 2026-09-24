/-
Claim: lem:catalan-truncation-vanishing
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#catalan-truncation-vanishing
Scope: Over F_2 = ZMod 2 with a finite variable type σ, for every s: the truncated product
g_s = Σ_c ∏_i f_i(c_i), over maps c : σ → Option (Fin s) of cost Σ_{c_i = some j} 2^j ≤ s - 1, where
f_i(none) = 1 + x_i and f_i(some j) = (x_i^2 + x_i)^(2^j), has Hasse multiplicity ≥ s at every nonzero
point of F_2^σ, value 1 at the origin, and total degree ≤ |σ| + 2(s-1) - s_2(s-1) with s_2 the binary
digit sum. The maps c with cost ≤ s - 1 correspond exactly to the notebook's pairs (S, a) with
a_i ∈ T_s (powers of two ≤ s - 1) and Σ a_i ≤ s - 1 (c_i = some j ↔ i ∈ S, a_i = 2^j; j < s holds
automatically), so this is the notebook's g_s. The degree-equality clause of the notebook's degree
remark is not claimed (it is not used downstream).
Declarations: MathResearch.TruncatedProduct.s2 MathResearch.TruncatedProduct.s2_add_le MathResearch.TruncatedProduct.s2_two_pow MathResearch.TruncatedProduct.s2_le_self MathResearch.TruncatedProduct.two_mul_add_s2_le MathResearch.TruncatedProduct.s2_sum_two_pow_le MathResearch.TruncatedProduct.telescope MathResearch.TruncatedProduct.g MathResearch.TruncatedProduct.prod_expansion MathResearch.TruncatedProduct.mult_g_ge MathResearch.TruncatedProduct.eval_zero_g MathResearch.TruncatedProduct.totalDegree_g_le MathResearch.TruncatedProduct.truncated_product
-/
import claims.HasseMultiplicity
import Mathlib.Data.Nat.Digits.Defs
import Mathlib.Algebra.CharP.Lemmas
import Mathlib.Algebra.Field.ZMod
import Mathlib.Algebra.MvPolynomial.Degrees
import Mathlib.Algebra.MvPolynomial.CommRing
import Mathlib.RingTheory.MvPolynomial.Basic
import Mathlib.Data.Fintype.Option
import Mathlib.Data.Fintype.Pi
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.IntervalCases
import Mathlib.Tactic.FinCases

namespace MathResearch.TruncatedProduct

open MvPolynomial MathResearch.HasseMultiplicity

/-! ### Binary digit sums -/

/-- The binary digit sum `s₂`. -/
def s2 (n : ℕ) : ℕ := (Nat.digits 2 n).sum

theorem s2_rec (n : ℕ) : s2 n = n % 2 + s2 (n / 2) := by
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · simp [s2]
  · rw [s2, Nat.digits_def' (by norm_num) hn, List.sum_cons]
    rfl

theorem s2_le_self (n : ℕ) : s2 n ≤ n := Nat.digit_sum_le 2 n

theorem s2_one : s2 1 = 1 := by simp [s2]

theorem s2_add_le (a b : ℕ) : s2 (a + b) ≤ s2 a + s2 b := by
  induction h : a + b using Nat.strong_induction_on generalizing a b with
  | _ n ih =>
    subst h
    rcases Nat.eq_zero_or_pos (a + b) with h0 | hpos
    · have ha : a = 0 := by omega
      have hb : b = 0 := by omega
      subst ha; subst hb; simp
    set c := (a % 2 + b % 2) / 2 with hc
    have hdiv : (a + b) / 2 = (a / 2 + b / 2) + c := by omega
    have hc1 : c ≤ 1 := by omega
    have hsc : s2 c = c := by
      interval_cases c <;> simp [s2]
    have h1 : s2 ((a / 2 + b / 2) + c) ≤ s2 (a / 2 + b / 2) + s2 c :=
      ih _ (by omega) _ _ rfl
    have h2 : s2 (a / 2 + b / 2) ≤ s2 (a / 2) + s2 (b / 2) :=
      ih _ (by omega) _ _ rfl
    rw [s2_rec (a + b), s2_rec a, s2_rec b, hdiv]
    omega

theorem s2_two_pow (j : ℕ) : s2 (2 ^ j) = 1 := by
  induction j with
  | zero => exact s2_one
  | succ j ih =>
    rw [s2_rec, pow_succ, Nat.mul_div_cancel _ (by norm_num), ih]
    simp

theorem s2_succ_le (n : ℕ) : s2 (n + 1) ≤ s2 n + 1 :=
  (s2_add_le n 1).trans (by rw [s2_one])

/-- `σ ↦ 2σ - s₂(σ)` is monotone, stated without subtraction. -/
theorem two_mul_add_s2_le {a b : ℕ} (hab : a ≤ b) : 2 * a + s2 b ≤ 2 * b + s2 a := by
  induction b, hab using Nat.le_induction with
  | base => exact le_refl _
  | succ b _ ih =>
    have := s2_succ_le b
    omega

/-- A sum of `|S|` powers of two has digit sum at most `|S|`. -/
theorem s2_sum_two_pow_le {ι : Type*} (S : Finset ι) (j : ι → ℕ) :
    s2 (∑ i ∈ S, 2 ^ j i) ≤ S.card := by
  classical
  induction S using Finset.induction_on with
  | empty => simp [s2]
  | insert a S ha ih =>
    rw [Finset.sum_insert ha, Finset.card_insert_of_notMem ha]
    have := s2_add_le (2 ^ j a) (∑ i ∈ S, 2 ^ j i)
    rw [s2_two_pow] at this
    omega

/-! ### The telescoping identity in characteristic two -/

theorem telescope {R : Type*} [CommRing R] [CharP R 2] (t : R) (K : ℕ) :
    ∑ j ∈ Finset.range K, (t ^ 2 + t) ^ (2 ^ j) = t ^ (2 ^ K) + t := by
  induction K with
  | zero =>
    simp only [Finset.range_zero, Finset.sum_empty, pow_zero, pow_one]
    exact (CharTwo.add_self_eq_zero t).symm
  | succ K ih =>
    rw [Finset.sum_range_succ, ih, add_pow_char_pow, ← pow_mul,
      show 2 ^ (K + 1) = 2 * 2 ^ K by ring]
    have := CharTwo.add_self_eq_zero (t ^ 2 ^ K)
    linear_combination this

/-! ### The truncated product -/

noncomputable section

variable {σ : Type*} [Fintype σ] [DecidableEq σ]

local notation "P2" => MvPolynomial σ (ZMod 2)

/-- The factor chosen at coordinate `i`. -/
def factor {s : ℕ} (i : σ) : Option (Fin s) → P2
  | none => 1 + X i
  | some j => (X i ^ 2 + X i) ^ (2 ^ (j : ℕ))

/-- The cost `Σ_{c_i = some j} 2^j` of a choice map. -/
def cost {s : ℕ} (c : σ → Option (Fin s)) : ℕ :=
  ∑ i, (c i).elim 0 (fun j => 2 ^ (j : ℕ))

/-- The term of a choice map. -/
def term {s : ℕ} (c : σ → Option (Fin s)) : P2 :=
  ∏ i, factor i (c i)

/-- The truncated product `g_s`. -/
def g (s : ℕ) : P2 :=
  ∑ c ∈ (Finset.univ : Finset (σ → Option (Fin s))).filter (fun c => cost c ≤ s - 1), term c

/-- `∏_i N_s(x_i) = ∏_i (1 + x_i)^(2^s)` expands into all choice terms. -/
theorem prod_expansion (s : ℕ) :
    ∏ i : σ, (1 + X i : P2) ^ (2 ^ s) = ∑ c : σ → Option (Fin s), term c := by
  have hN : ∀ i : σ, (1 + X i : P2) ^ (2 ^ s) =
      ∑ o : Option (Fin s), factor i o := by
    intro i
    rw [Fintype.sum_option]
    simp only [factor]
    rw [Fin.sum_univ_eq_sum_range (fun j => (X i ^ 2 + X i : P2) ^ (2 ^ j)) s]
    have ht := telescope (1 + X i : P2) s
    have hy : ((1 + X i : P2) ^ 2 + (1 + X i)) = X i ^ 2 + X i := by
      have h2 : (2 : P2) = 0 := CharP.cast_eq_zero P2 2
      linear_combination (1 + X i) * h2
    rw [hy] at ht
    rw [ht]
    have := CharTwo.add_self_eq_zero (1 + X i : P2)
    linear_combination -this
  simp_rw [hN]
  rw [Finset.prod_univ_sum]
  simp [Fintype.piFinset_univ, term]

/-! ### Multiplicity bounds -/

omit [Fintype σ] [DecidableEq σ] in
theorem le_mult_pow (a : σ → ZMod 2) (P : P2) (n : ℕ) : n * mult a P ≤ mult a (P ^ n) := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [pow_succ]
    calc ((n + 1 : ℕ) : ℕ∞) * mult a P = n * mult a P + mult a P := by push_cast; ring
      _ ≤ mult a (P ^ n) + mult a P := by gcongr
      _ ≤ mult a (P ^ n * P) := add_le_mult_mul a _ _

omit [Fintype σ] [DecidableEq σ] in
theorem le_mult_prod {ι : Type*} (a : σ → ZMod 2) (T : Finset ι) (f : ι → P2) :
    ∑ i ∈ T, mult a (f i) ≤ mult a (∏ i ∈ T, f i) := by
  classical
  induction T using Finset.induction_on with
  | empty => simp
  | insert b T hb ih =>
    rw [Finset.sum_insert hb, Finset.prod_insert hb]
    calc mult a (f b) + ∑ i ∈ T, mult a (f i) ≤ mult a (f b) + mult a (∏ i ∈ T, f i) := by gcongr
      _ ≤ _ := add_le_mult_mul a _ _

omit [Fintype σ] [DecidableEq σ] in
theorem le_mult_sum {ι : Type*} (a : σ → ZMod 2) (T : Finset ι) (f : ι → P2) (m : ℕ∞)
    (h : ∀ i ∈ T, m ≤ mult a (f i)) : m ≤ mult a (∑ i ∈ T, f i) := by
  classical
  induction T using Finset.induction_on with
  | empty => simp
  | insert b T hb ih =>
    rw [Finset.sum_insert hb]
    exact le_trans (le_min (h b (Finset.mem_insert_self b T))
      (ih fun i hi => h i (Finset.mem_insert_of_mem hi))) (min_le_mult_add a _ _)

omit [Fintype σ] [DecidableEq σ] in
theorem one_le_mult_y (a : σ → ZMod 2) (i : σ) : 1 ≤ mult a (X i ^ 2 + X i : P2) := by
  rw [one_le_mult_iff]
  simp only [map_add, map_pow, eval_X]
  generalize a i = x
  fin_cases x <;> decide

omit [Fintype σ] [DecidableEq σ] in
theorem one_le_mult_one_add_X (a : σ → ZMod 2) (i : σ) (hi : a i = 1) :
    1 ≤ mult a (1 + X i : P2) := by
  rw [one_le_mult_iff]
  simp [hi]
  decide

omit [DecidableEq σ] in
theorem cost_le_mult_term {s : ℕ} (a : σ → ZMod 2) (c : σ → Option (Fin s)) :
    (cost c : ℕ∞) ≤ mult a (term c) := by
  refine le_trans ?_ (le_mult_prod a Finset.univ _)
  rw [cost, Nat.cast_sum]
  apply Finset.sum_le_sum
  intro i _
  rcases hc : c i with _ | j
  · simp
  · simp only [Option.elim_some, factor, Nat.cast_pow, Nat.cast_ofNat]
    calc ((2 : ℕ∞) ^ (j : ℕ)) = ((2 ^ (j : ℕ) : ℕ) : ℕ∞) * 1 := by push_cast; ring
      _ ≤ ((2 ^ (j : ℕ) : ℕ) : ℕ∞) * mult a (X i ^ 2 + X i) := by
          gcongr; exact one_le_mult_y a i
      _ ≤ _ := le_mult_pow a _ _

/-- `g_s` has multiplicity at least `s` at every nonzero point. -/
theorem mult_g_ge (s : ℕ) (a : σ → ZMod 2) (ha : a ≠ 0) : (s : ℕ∞) ≤ mult a (g s : P2) := by
  classical
  obtain ⟨i0, hi0⟩ := Function.ne_iff.1 ha
  have hai0 : a i0 = 1 := by
    generalize hx : a i0 = x at hi0
    fin_cases x
    · exact absurd rfl hi0
    · rfl
  set R := ∑ c ∈ (Finset.univ : Finset (σ → Option (Fin s))).filter (fun c => ¬ cost c ≤ s - 1),
    term c
  have hsplit : (g s : P2) = ∏ i : σ, (1 + X i : P2) ^ (2 ^ s) + R := by
    rw [prod_expansion, ← Finset.sum_filter_add_sum_filter_not Finset.univ
      (fun c : σ → Option (Fin s) => cost c ≤ s - 1), g]
    have := CharTwo.add_self_eq_zero R
    linear_combination -this
  have hprod : (s : ℕ∞) ≤ mult a (∏ i : σ, (1 + X i : P2) ^ (2 ^ s)) := by
    refine le_trans ?_ (le_mult_prod a Finset.univ _)
    refine le_trans ?_ (Finset.single_le_sum (fun _ _ => zero_le) (Finset.mem_univ i0))
    calc (s : ℕ∞) ≤ ((2 ^ s : ℕ) : ℕ∞) * 1 := by
          rw [mul_one]; exact_mod_cast (Nat.lt_two_pow_self).le
      _ ≤ ((2 ^ s : ℕ) : ℕ∞) * mult a (1 + X i0) := by
          gcongr; exact one_le_mult_one_add_X a i0 hai0
      _ ≤ _ := le_mult_pow a _ _
  have hR : (s : ℕ∞) ≤ mult a R := by
    apply le_mult_sum
    intro c hc
    have hcost : s ≤ cost c := by
      have := (Finset.mem_filter.1 hc).2
      omega
    exact le_trans (by exact_mod_cast hcost) (cost_le_mult_term a c)
  rw [hsplit]
  exact le_trans (le_min hprod hR) (min_le_mult_add a _ _)

/-- `g_s(0) = 1`. -/
theorem eval_zero_g (s : ℕ) : eval 0 (g s : P2) = 1 := by
  classical
  rw [g, map_sum]
  rw [Finset.sum_eq_single (fun _ => none)]
  · simp [term, factor]
  · intro c _ hc
    obtain ⟨i, hi⟩ : ∃ i, c i ≠ none := by
      by_contra h
      push Not at h
      exact hc (funext h)
    obtain ⟨j, hj⟩ := Option.ne_none_iff_exists'.1 hi
    rw [term, map_prod]
    apply Finset.prod_eq_zero (Finset.mem_univ i)
    simp [hj, factor]
  · intro h
    exfalso
    exact h (Finset.mem_filter.2 ⟨Finset.mem_univ _, by simp [cost]⟩)

/-- `deg g_s ≤ |σ| + 2(s-1) - s₂(s-1)`. -/
theorem totalDegree_g_le (s : ℕ) :
    (g s : P2).totalDegree ≤ Fintype.card σ + 2 * (s - 1) - s2 (s - 1) := by
  classical
  apply (totalDegree_finsetSum _ _).trans
  apply Finset.sup_le
  intro c hc
  have hcost : cost c ≤ s - 1 := (Finset.mem_filter.1 hc).2
  set S := Finset.univ.filter (fun i => c i ≠ none)
  have hfac : ∀ i, (factor i (c i)).totalDegree ≤
      (c i).elim 1 (fun j => 2 * 2 ^ (j : ℕ)) := by
    intro i
    rcases c i with _ | j
    · simp only [factor, Option.elim_none]
      apply (totalDegree_add _ _).trans
      simp [totalDegree_X]
    · simp only [factor, Option.elim_some]
      apply (totalDegree_pow _ _).trans
      rw [mul_comm]
      gcongr
      apply (totalDegree_add _ _).trans
      apply max_le
      · apply (totalDegree_pow _ _).trans
        simp [totalDegree_X]
      · simp [totalDegree_X]
  have hterm : (term c).totalDegree ≤ ∑ i, (c i).elim 1 (fun j => 2 * 2 ^ (j : ℕ)) :=
    (totalDegree_finsetProd _ _).trans (Finset.sum_le_sum fun i _ => hfac i)
  have hsum : ∑ i, (c i).elim 1 (fun j => 2 * 2 ^ (j : ℕ)) =
      (Fintype.card σ - S.card) + 2 * cost c := by
    have hpt : ∀ i, (c i).elim 1 (fun j => 2 * 2 ^ (j : ℕ)) =
        (if c i = none then 1 else 0) + 2 * (c i).elim 0 (fun j => 2 ^ (j : ℕ)) := by
      intro i
      rcases c i with _ | j <;> simp
    rw [Finset.sum_congr rfl (fun i _ => hpt i), Finset.sum_add_distrib, ← Finset.mul_sum,
      Finset.sum_boole]
    have hsplit := Finset.card_filter_add_card_filter_not (s := Finset.univ)
      (fun i => c i = none)
    rw [Finset.card_univ] at hsplit
    simp only [S, cost, Nat.cast_id, ne_eq] at hsplit ⊢
    omega
  have hS : s2 (cost c) ≤ S.card := by
    have hcost_eq : cost c = ∑ i ∈ S, 2 ^ ((c i).elim 0 (fun j => (j : ℕ))) := by
      rw [cost, ← Finset.sum_filter_of_ne (p := fun i => c i ≠ none)]
      · apply Finset.sum_congr rfl
        intro i hi
        rcases h : c i with _ | j
        · simp [h] at hi
        · simp
      · intro i _ hne h
        rw [h] at hne
        exact hne rfl
    rw [hcost_eq]
    exact s2_sum_two_pow_le S _
  have hScard : S.card ≤ Fintype.card σ := Finset.card_filter_le _ _
  have hmono := two_mul_add_s2_le hcost
  have hle := s2_le_self (s - 1)
  rw [hsum] at hterm
  omega

theorem truncated_product (s : ℕ) :
    (∀ a : σ → ZMod 2, a ≠ 0 → (s : ℕ∞) ≤ mult a (g s : P2)) ∧ eval 0 (g s : P2) = 1 ∧
      (g s : P2).totalDegree ≤ Fintype.card σ + 2 * (s - 1) - s2 (s - 1) :=
  ⟨mult_g_ge s, eval_zero_g s, totalDegree_g_le s⟩

end

end MathResearch.TruncatedProduct
