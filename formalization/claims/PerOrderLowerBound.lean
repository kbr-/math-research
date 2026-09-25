/-
Claim: thm:per-order-value-all-dimensions (lower half)
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#per-order-value-all-dimensions
Scope: Over F_2 with a finite variable type σ of cardinality n ≥ 1: for all 0 ≤ ℓ < k, every P with
Hasse multiplicity ≥ k at every nonzero point of F_2^σ and multiplicity exactly ℓ at the origin has
total degree ≥ n + 2ℓ + Σ_{j<n} ⌊(k−ℓ−1)/2^j⌋. The proof is the notebook's: the series w = P(xhat(y)) has
origin order ℓ; the conditions (C_t) from the degree of the expansion (PerOrderExpansion,
PerOrderYCoefficient); vanishing of the forms E^(t)_j on generator tuples by the repeated-argument
recursion (PerOrderForms) and then on the span V of y_1..y_n; the reduction modulo L_V
(PerOrderSubspaceReduction); and the coefficient of M* (the decomposition of PerOrderLegendre).
Declarations: MathResearch.PerOrderLowerBound.mult_wser MathResearch.PerOrderLowerBound.cond MathResearch.PerOrderLowerBound.E_vanish MathResearch.PerOrderLowerBound.lower_bound
-/
import claims.PerOrderForms
import claims.PerOrderLegendre
import claims.PerOrderSubspaceReduction

namespace MathResearch.PerOrderLowerBound

open MvPolynomial MathResearch.HasseMultiplicity MathResearch.TruncatedProduct
open MathResearch.OneDimensionStep MathResearch.PerOrderExpansion MathResearch.PerOrderYCoefficient
open MathResearch.PerOrderForms MathResearch.PerOrderLegendre MathResearch.PerOrderSubspaceReduction

noncomputable section

variable {σ : Type*} [Fintype σ] [DecidableEq σ]

local notation "P2" => MvPolynomial σ (ZMod 2)

/-! ### The series `w = P(xhat(y))` -/

omit [Fintype σ] [DecidableEq σ] in
theorem mult_neg (f : P2) : mult 0 (-f) = mult 0 f := by
  rw [neg_eq_neg_one_mul, mult_mul, (mult_eq_zero_iff 0 _).2 (by simp), zero_add]

omit [Fintype σ] [DecidableEq σ] in
/-- Adding a term of larger order does not change the order. -/
theorem mult_add_of_lt {a b : P2} (h : mult 0 a < mult 0 b) : mult 0 (a + b) = mult 0 a := by
  apply le_antisymm
  · by_contra hlt
    push Not at hlt
    have h1 := min_le_mult_add 0 (a + b) (-b)
    rw [add_neg_cancel_right, mult_neg] at h1
    exact absurd (lt_of_lt_of_le (lt_min hlt h) h1) (lt_irrefl _)
  · exact le_trans (by rw [min_eq_left h.le]) (min_le_mult_add 0 a b)

omit [Fintype σ] [DecidableEq σ] in
theorem mult_eq_of_sub_mem {k ℓ : ℕ} (hℓ : ℓ < k) {f g : P2} (hfg : f - g ∈ lowIdeal k)
    (hg : mult 0 g = ℓ) : mult 0 f = ℓ := by
  rw [mem_lowIdeal] at hfg
  have hlt : mult 0 g < mult 0 (f - g) := by
    rw [hg]; exact lt_of_lt_of_le (by exact_mod_cast hℓ) hfg
  rw [show f = g + (f - g) by ring, mult_add_of_lt hlt, hg]

/-- `w = P(xhat(y_1), …, xhat(y_n))` with `K = k`. -/
def wser (k : ℕ) (P : P2) : P2 := aeval (fun i => xhat k (X i)) P

omit [Fintype σ] [DecidableEq σ] in
theorem aeval_yv_xhat (k : ℕ) (i : σ) : aeval yv (xhat k (X i : P2)) = yh k i := by
  rw [xhat, map_sum]
  simp only [map_pow, aeval_X, yv]
  have : ∀ s, ((X i : P2) ^ 2 + X i) ^ (2 ^ s) = X i ^ (2 ^ (s + 1)) + X i ^ (2 ^ s) := by
    intro s
    rw [add_pow_char_pow, ← pow_mul, ← pow_succ']
  simp_rw [this]
  rw [Finset.sum_add_distrib, telescope_two_pow, yh]

omit [Fintype σ] [DecidableEq σ] in
/-- `w` has the origin order of `P`. -/
theorem mult_wser {k ℓ : ℕ} (hℓ : ℓ < k) (P : P2) (h0 : mult 0 P = ℓ) : mult 0 (wser k P) = ℓ := by
  apply le_antisymm
  · have hback : aeval yv (wser k P) = aeval (yh k) P := by
      rw [wser, ← AlgHom.comp_apply, comp_aeval]
      refine congrArg (fun f : σ → P2 => aeval f P) ?_
      funext i
      exact aeval_yv_xhat k i
    have hyh : mult 0 (aeval (yh k) P) = ℓ := by
      apply mult_eq_of_sub_mem hℓ _ h0
      rw [← Ideal.Quotient.eq]
      exact mk_aeval_yh (Nat.lt_two_pow_self).le P
    calc mult 0 (wser k P) ≤ mult 0 (aeval yv (wser k P)) :=
          le_mult_zero_aeval yv (fun i => one_le_mult_y 0 i) _
      _ = ℓ := by rw [hback, hyh]
  · rw [← h0]
    exact le_mult_zero_aeval _ (fun i => one_le_mult_xhat k i) P

omit [Fintype σ] [DecidableEq σ] in
theorem hc_wser_lt {k ℓ : ℕ} (hℓ : ℓ < k) (P : P2) (h0 : mult 0 P = ℓ) {d : ℕ} (hd : d < ℓ) :
    homogeneousComponent d (wser k P) = 0 :=
  (coe_le_mult_zero_iff _ ℓ).1 (by rw [mult_wser hℓ P h0]) d hd

omit [Fintype σ] [DecidableEq σ] in
theorem hc_wser_ne {k ℓ : ℕ} (hℓ : ℓ < k) (P : P2) (h0 : mult 0 P = ℓ) :
    homogeneousComponent ℓ (wser k P) ≠ 0 := by
  intro h
  have : ((ℓ + 1 : ℕ) : ℕ∞) ≤ mult 0 (wser k P) := by
    rw [coe_le_mult_zero_iff]
    intro j hj
    rcases lt_or_eq_of_le (Nat.le_of_lt_succ hj) with hj | rfl
    · exact hc_wser_lt hℓ P h0 hj
    · exact h
  rw [mult_wser hℓ P h0] at this
  have : ℓ + 1 ≤ ℓ := by exact_mod_cast this
  omega

/-! ### Step 1: the conditions `(C_t)` -/

/-- **Conditions `(C_t)`.** If `deg P + h + 1 ≤ n + 2(k−1)`, then for every `t < k` and every set `T`
of variables with `|T| + 2t ≤ h`, the component of degree `k−1−t` of `w ∏_{i∈T} xhat(y_i)` vanishes. -/
theorem cond {k h : ℕ} (P : P2) (hP : ∀ a : σ → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P)
    (hdeg : P.totalDegree + h + 1 ≤ Fintype.card σ + 2 * (k - 1)) {t : ℕ} (ht : t < k)
    (T : Finset σ) (hT : T.card + 2 * t ≤ h) :
    homogeneousComponent (k - 1 - t) (wser k P * ∏ i ∈ T, xhat k (X i)) = 0 := by
  obtain ⟨A, hA⟩ := exists_expansion P
  have hS : ∀ S : Finset σ, S.card + 2 * t ≤ h →
      homogeneousComponent (k - 1 - t) (wser k P * ∏ i ∈ S, (1 + xhat k (X i))) = 0 := by
    intro S hS
    ext e
    rw [coeff_homogeneousComponent, AddMonoidAlgebra.coeff_zero]
    split_ifs with he
    · have hfilt : Finset.univ.filter (· ∉ Sᶜ) = S := by ext i; simp
      have hc := coeff_expansion (K := k) (Nat.lt_two_pow_self).le P hP A hA Sᶜ e (by omega)
      rw [hfilt] at hc
      rw [wser, ← hc]
      by_contra hne
      have hw := weight_le_totalDegree P A hA Sᶜ e hne
      rw [Finset.card_compl, he] at hw
      have hSn : S.card ≤ Fintype.card σ := Finset.card_le_univ S
      omega
    · rfl
  have hprod : (∏ i ∈ T, xhat k (X i : P2)) = ∑ S ∈ T.powerset, ∏ i ∈ S, (1 + xhat k (X i)) := by
    have : ∀ i, xhat k (X i : P2) = (1 + xhat k (X i)) + 1 := by
      intro i; linear_combination (-1 : P2) * two_eq_zero_P2
    conv_lhs => rw [Finset.prod_congr rfl (fun i _ => this i)]
    rw [Finset.prod_add]
    simp
  rw [hprod, Finset.mul_sum, map_sum]
  apply Finset.sum_eq_zero
  intro S hS'
  exact hS S (le_trans (by have := Finset.card_le_card (Finset.mem_powerset.1 hS'); omega) hT)


/-! ### Step 3: vanishing on generator tuples -/

/-- **Step 3: vanishing at generator tuples.** Under the degree hypothesis, `E^{(t)}_j` vanishes at every
tuple of generators `y_i` whenever `j + 2t ≤ h`. -/
theorem E_vanish {k h : ℕ} (hk : 1 ≤ k) (hhk : h ≤ k - 1) (P : P2)
    (hP : ∀ a : σ → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P)
    (hdeg : P.totalDegree + h + 1 ≤ Fintype.card σ + 2 * (k - 1)) :
    ∀ j t, j + 2 * t ≤ h → ∀ i : Fin j → σ, E k (wser k P) t j (fun a => X (i a)) = 0 := by
  intro j
  induction j using Nat.strong_induction_on with
  | _ j ih =>
    intro t hjt i
    have ht : t < k := by omega
    by_cases hinj : Function.Injective i
    · rw [E_eval ht]
      have hc := cond P hP hdeg ht (Finset.univ.image i) (by
        rw [Finset.card_image_of_injective _ hinj, Finset.card_univ, Fintype.card_fin]; omega)
      rwa [Finset.prod_image (fun a _ b _ hab => hinj hab)] at hc
    · simp only [Function.Injective, not_forall] at hinj
      obtain ⟨a, b, hab, hne⟩ := hinj
      obtain ⟨j', rfl⟩ : ∃ j', j = j' + 2 := by
        have ha := a.isLt
        have hb := b.isLt
        have : (a : ℕ) ≠ b := fun h => hne (Fin.ext h)
        exact ⟨j - 2, by omega⟩
      set g1 := Equiv.swap (0 : Fin (j' + 2)) a
      set b1 := g1 b
      have hb1 : b1 ≠ 0 := by
        intro h
        rw [Equiv.swap_apply_eq_iff, Equiv.swap_apply_left] at h
        exact hne h.symm
      set g2 := Equiv.swap (1 : Fin (j' + 2)) b1
      set π : Equiv.Perm (Fin (j' + 2)) := g2.trans g1
      have hπ0 : i (π 0) = i a := by
        simp only [π, Equiv.trans_apply, g2, g1]
        rw [Equiv.swap_apply_of_ne_of_ne (by rw [Ne, Fin.ext_iff]; simp) (Ne.symm hb1), Equiv.swap_apply_left]
      have hπ1 : i (π 1) = i a := by
        simp only [π, Equiv.trans_apply, g2]
        rw [Equiv.swap_apply_left]
        simp only [b1, g1, Equiv.swap_apply_self]
        exact hab.symm
      set rest : Fin j' → σ := fun c => i (π c.succ.succ)
      have hfun : (fun c => (X (i c) : P2)) ∘ π =
          Fin.cons (X (i a)) (Fin.cons (X (i a)) (fun c => X (rest c))) := by
        funext c
        refine Fin.cases ?_ (fun c' => ?_) c
        · simp [hπ0]
        · refine Fin.cases ?_ (fun c'' => ?_) c'
          · simp only [Function.comp_apply, Fin.cons_succ, Fin.cons_zero]
            rw [show (Fin.succ 0 : Fin (j' + 2)) = 1 from rfl, hπ1]
          · simp [rest]
      rw [← E_perm k _ t (j' + 2) _ π, hfun, E_rec hk]
      have h1 : E k (wser k P) t (j' + 1) (Fin.cons (X (i a)) (fun c => X (rest c))) = 0 := by
        have := ih (j' + 1) (by omega) t (by omega) (Fin.cons (i a) rest)
        rwa [show (fun c => (X ((Fin.cons (i a) rest : Fin (j' + 1) → σ) c) : P2)) =
          Fin.cons (X (i a)) (fun c => X (rest c)) by
            funext c; refine Fin.cases ?_ (fun c' => ?_) c <;> simp] at this
      have h2 : E k (wser k P) (t + 1) j' (fun c => X (rest c)) = 0 :=
        ih j' (by omega) (t + 1) (by omega) rest
      rw [h1, h2, mul_zero, add_zero]

/-! ### The span `V` of `y_1, …, y_n` -/

/-- The element `Σ_{i ∈ A} y_i` of the span `V`. -/
def lin (A : Finset σ) : P2 := ∑ i ∈ A, X i

omit [Fintype σ] in
theorem lin_injective : Function.Injective (lin : Finset σ → P2) := by
  intro A B h
  ext i
  have hc := congrArg (fun f : P2 => f.coeff (Finsupp.single i 1)) h
  simp only [lin, coeff_sum, coeff_X, Finsupp.single_left_inj one_ne_zero] at hc
  by_cases hA : i ∈ A <;> by_cases hB : i ∈ B <;> simp_all

/-- The span `V = {Σ_{i∈A} y_i}`, with `2^n` elements. -/
def Vset : Finset P2 := Finset.univ.image (lin (σ := σ))

theorem card_Vset : (Vset (σ := σ)).card = 2 ^ Fintype.card σ := by
  rw [Vset, Finset.card_image_of_injective _ lin_injective, Finset.card_univ, Fintype.card_finset]

/-- **The lower bound.** For `n ≥ 1` and `ℓ < k`, every `P` over `𝔽₂` with multiplicity `≥ k` at
every nonzero point and multiplicity exactly `ℓ` at the origin has
`deg P ≥ n + 2ℓ + Σ_{j<n} ⌊(k − ℓ − 1)/2^j⌋`. -/
theorem lower_bound (hn : 1 ≤ Fintype.card σ) {k ℓ : ℕ} (hℓ : ℓ < k) (P : P2)
    (hP : ∀ a : σ → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P) (h0 : mult 0 P = ℓ) :
    Fintype.card σ + 2 * ℓ + ∑ j ∈ Finset.range (Fintype.card σ), (k - ℓ - 1) / 2 ^ j ≤
      P.totalDegree := by
  classical
  set n := Fintype.card σ with hn_def
  set m := k - ℓ - 1 with hm
  set q := m / 2 ^ n with hq
  set r := m % 2 ^ n with hr_def
  have hqr : q * 2 ^ n + r = m := by rw [mul_comm]; exact Nat.div_add_mod m (2 ^ n)
  have hr : r < 2 ^ n := Nat.mod_lt _ (by positivity)
  have hleg := legendre n q r hr
  rw [hqr] at hleg
  have hk : 1 ≤ k := by omega
  have h2n : 2 ≤ 2 ^ n := by
    calc 2 = 2 ^ 1 := by norm_num
      _ ≤ 2 ^ n := Nat.pow_le_pow_right (by norm_num) hn
  -- the decomposition m = Σ_a 2^{s_a}, with H = 2q + s₂(r) parts
  set L := bits n q r with hL
  set H := L.length with hH
  have hHval : H = 2 * q + s2 r := length_bits n q r
  have hHm : H ≤ m := by
    have := s2_le_self r
    have : 2 * q ≤ q * 2 ^ n := by nlinarith
    omega
  by_contra hlt
  push Not at hlt
  have hdeg : P.totalDegree + H + 1 ≤ n + 2 * (k - 1) := by omega
  have hHk : H ≤ k - 1 := by omega
  set s : Fin H → ℕ := fun a => L[a.1] with hs
  have hs_lt : ∀ a, s a < n := fun a => lt_of_mem_bits hn hr (List.getElem_mem _)
  have hs_sum : ∑ a, 2 ^ s a = m := by
    have h1 := sum_bits hn q r
    rw [hqr] at h1
    rw [← h1, ← Fin.sum_univ_fun_getElem]
  have hs_k : ∀ a, s a < k := by
    intro a
    have h1 : 2 ^ s a ≤ m := by
      rw [← hs_sum]
      exact Finset.single_le_sum (f := fun a => 2 ^ s a) (fun _ _ => Nat.zero_le _)
        (Finset.mem_univ a)
    have h2 : s a < 2 ^ s a := Nat.lt_two_pow_self
    omega
  set w := wser k P with hw
  have hVne : (Vset (σ := σ)).Nonempty := ⟨lin ∅, Finset.mem_image_of_mem _ (Finset.mem_univ _)⟩
  have hVcard : (Vset (σ := σ)).card = 2 ^ n := card_Vset
  -- Steps 4–5: the reduction modulo L_V applied to E^{(0)}_H, which vanishes on V^H
  have hred := coeff_reduction (V := Vset (σ := σ)) (fun τ : Fin H → Fin k => hcw k w (∑ a, 2 ^ (τ a : ℕ)))
    (fun τ a => 2 ^ (τ a : ℕ)) (by
      intro v hv
      have heval : ∑ τ : Fin H → Fin k, hcw k w (∑ a, 2 ^ (τ a : ℕ)) * ∏ a, v a ^ 2 ^ (τ a : ℕ) =
          E k w 0 H v := by
        rw [E]
        apply Finset.sum_congr rfl
        intro τ _
        rw [mul_comm, zero_add]
      rw [heval]
      have hA : ∀ a, ∃ A : Finset σ, lin A = v a := fun a => by
        simpa [Vset] using hv a
      choose A hA using hA
      have hv' : v = fun a => ∑ i ∈ A a, X i := by
        funext a; rw [← hA a]; rfl
      rw [hv', E_span]
      apply Finset.sum_eq_zero
      intro f _
      exact E_vanish hk hHk P hP hdeg H 0 (by omega) f)
    (fun a => 2 ^ s a) (fun a => by rw [hVcard]; exact Nat.pow_lt_pow_right (by norm_num) (hs_lt a))
  -- only τ = s contributes, with value w_ℓ
  set s' : Fin H → Fin k := fun a => ⟨s a, hs_k a⟩ with hs'
  rw [Finset.sum_eq_single s'] at hred
  · have hsum' : ∑ a, 2 ^ ((s' a : Fin k) : ℕ) = m := hs_sum
    rw [hsum', hcw, ite_eq_left (by omega : m < k), show k - 1 - m = ℓ by omega,
      Finset.prod_eq_one, mul_one] at hred
    · exact hc_wser_ne hℓ P h0 hred
    · intro a _
      rw [rho_of_lt (by rw [hVcard]; exact Nat.pow_lt_pow_right (by norm_num) (hs_lt a)),
        Polynomial.coeff_X_pow_self]
  · intro τ _ hτ
    by_contra hne
    obtain ⟨h1, h2⟩ := mul_ne_zero_iff.1 hne
    have hge : ∀ a, s a ≤ τ a := by
      intro a
      have hca := Finset.prod_ne_zero_iff.1 h2 a (Finset.mem_univ a)
      have h3 := Polynomial.le_natDegree_of_ne_zero hca
      have h4 := natDegree_rho_le hVne (2 ^ (τ a : ℕ))
      exact (Nat.pow_le_pow_iff_right (by norm_num)).1 (h3.trans h4)
    rw [hcw] at h1
    split_ifs at h1 with hlt'
    · have hdl : ℓ ≤ k - 1 - ∑ a, 2 ^ (τ a : ℕ) := by
        by_contra hlt2
        push Not at hlt2
        exact h1 (hc_wser_lt hℓ P h0 hlt2)
      have hex : ∃ a, s a < τ a := by
        by_contra hall
        push Not at hall
        apply hτ
        funext a
        exact Fin.ext (le_antisymm (hall a) (hge a))
      obtain ⟨a0, ha0⟩ := hex
      have hlt3 : ∑ a, 2 ^ s a < ∑ a, 2 ^ (τ a : ℕ) :=
        Finset.sum_lt_sum (fun a _ => Nat.pow_le_pow_right (by norm_num) (hge a))
          ⟨a0, Finset.mem_univ _, Nat.pow_lt_pow_right (by norm_num) ha0⟩
      omega
    · exact h1 rfl
  · intro hnot
    exact absurd (Finset.mem_univ _) hnot

end

end MathResearch.PerOrderLowerBound
