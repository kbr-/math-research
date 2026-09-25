/-
Claim: lem:per-order-repeated-argument-forms
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#per-order-value-all-dimensions
Scope: Over F_2[y] (any finite variable type), for w and k the forms
E^(t)_j(u) = Σ_τ ∏_a u_a^(2^τ_a) · w_{k−1−t−Σ_a 2^τ_a} (τ_a < k, and w_d the degree-d component of w,
zero when the index is negative): symmetry, expansion in the first argument, the repeated-argument
recursion E^(t)_{j+2}(Y,Y,Z) = E^(t)_{j+1}(Y,Z) + Y E^(t+1)_j(Z) (for k ≥ 1), evaluation at generator
tuples, for t < k, as the degree-(k−1−t) component of w ∏_a xhat_k(y_{i_a}) (xhat truncated at K = k),
and multi-additivity on sums of generators. Step 2 of the per-order lower bound.
Declarations: MathResearch.PerOrderForms.sum_sym_char_two MathResearch.PerOrderForms.hcw MathResearch.PerOrderForms.E MathResearch.PerOrderForms.E_big MathResearch.PerOrderForms.E_cons MathResearch.PerOrderForms.E_perm MathResearch.PerOrderForms.E_rec MathResearch.PerOrderForms.hc_mul_homogeneous MathResearch.PerOrderForms.E_eval MathResearch.PerOrderForms.E_span
-/
import claims.PerOrderYCoefficient

namespace MathResearch.PerOrderForms

open MvPolynomial MathResearch.PerOrderExpansion MathResearch.PerOrderYCoefficient

noncomputable section

variable {σ : Type*} [Fintype σ] [DecidableEq σ]

local notation "P2" => MvPolynomial σ (ZMod 2)

omit [Fintype σ] [DecidableEq σ] in
/-- In characteristic two, a symmetric double sum equals its diagonal. -/
theorem sum_sym_char_two {ι : Type*} [Fintype ι] [DecidableEq ι] (f : ι → ι → P2)
    (hf : ∀ a b, f a b = f b a) : ∑ a, ∑ b, f a b = ∑ a, f a a := by
  rw [← Finset.sum_product']
  have hsplit : ∀ p : ι × ι, f p.1 p.2 =
      (if p.1 = p.2 then f p.1 p.2 else 0) + (if p.1 = p.2 then 0 else f p.1 p.2) := by
    intro p; split_ifs <;> simp
  rw [Finset.sum_congr rfl (fun p _ => hsplit p), Finset.sum_add_distrib]
  have hoff : ∑ p ∈ (Finset.univ : Finset ι) ×ˢ Finset.univ,
      (if p.1 = p.2 then 0 else f p.1 p.2) = 0 := by
    refine Finset.sum_involution (fun p _ => (p.2, p.1)) ?_ ?_ (by simp) (by simp)
    · intro p _
      by_cases h : p.1 = p.2
      · simp [h]
      · simp only [h, ↓reduceIte, Ne.symm h, hf p.2 p.1]
        linear_combination f p.1 p.2 * two_eq_zero_P2
    · intro p _ hne heq
      apply hne
      have : p.1 = p.2 := by
        have := congrArg Prod.fst heq; simpa [eq_comm] using this
      simp [this]
  rw [hoff, add_zero, Finset.sum_product]
  apply Finset.sum_congr rfl
  intro a _
  rw [Finset.sum_ite_eq]
  simp

/-- `hcw(s)`: the component of degree `k − 1 − s` of `w`, and `0` for `s ≥ k`. -/
def hcw (k : ℕ) (w : P2) (s : ℕ) : P2 := if s < k then homogeneousComponent (k - 1 - s) w else 0

/-- The form `E^{(t)}_j(u) = Σ_τ ∏_a u_a^{2^{τ_a}} · hcw(t + Σ_a 2^{τ_a})`, over `τ_a < k`. -/
def E (k : ℕ) (w : P2) (t j : ℕ) (u : Fin j → P2) : P2 :=
  ∑ τ : Fin j → Fin k, (∏ a, u a ^ (2 ^ (τ a : ℕ))) * hcw k w (t + ∑ a, 2 ^ (τ a : ℕ))

omit [Fintype σ] [DecidableEq σ] in
theorem E_big {k : ℕ} (w : P2) {t : ℕ} (ht : k ≤ t) (j : ℕ) (u : Fin j → P2) : E k w t j u = 0 := by
  apply Finset.sum_eq_zero
  intro τ _
  rw [hcw, ite_eq_right (by omega), mul_zero]

omit [Fintype σ] [DecidableEq σ] in
theorem E_cons (k : ℕ) (w : P2) (t j : ℕ) (y : P2) (u : Fin j → P2) :
    E k w t (j + 1) (Fin.cons y u) = ∑ s : Fin k, y ^ (2 ^ (s : ℕ)) * E k w (t + 2 ^ (s : ℕ)) j u := by
  rw [E, ← (Fin.consEquiv fun _ => Fin k).sum_comp, Fintype.sum_prod_type]
  apply Finset.sum_congr rfl
  intro s _
  rw [E, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro ρ _
  simp only [Fin.consEquiv, Equiv.coe_fn_mk, Fin.prod_univ_succ, Fin.sum_univ_succ, Fin.cons_zero,
    Fin.cons_succ]
  rw [add_assoc]
  ring

omit [Fintype σ] [DecidableEq σ] in
theorem E_perm (k : ℕ) (w : P2) (t j : ℕ) (u : Fin j → P2) (π : Equiv.Perm (Fin j)) :
    E k w t j (u ∘ π) = E k w t j u := by
  rw [E, E, ← (Equiv.arrowCongr π.symm (Equiv.refl (Fin k))).sum_comp]
  apply Finset.sum_congr rfl
  intro τ _
  simp only [Equiv.arrowCongr_apply, Equiv.symm_symm, Equiv.coe_refl, Function.comp_apply, id]
  congr 1
  · exact Equiv.prod_comp π (fun b => u b ^ (2 ^ (τ b : ℕ)))
  · congr 2
    exact Equiv.sum_comp π (fun b => 2 ^ (τ b : ℕ))

omit [Fintype σ] [DecidableEq σ] in
theorem E_diag (k : ℕ) (w : P2) (t j : ℕ) (y : P2) (u : Fin j → P2) :
    E k w t (j + 2) (Fin.cons y (Fin.cons y u)) =
      ∑ s : Fin k, y ^ (2 ^ ((s : ℕ) + 1)) * E k w (t + 2 ^ ((s : ℕ) + 1)) j u := by
  rw [E_cons]
  simp_rw [E_cons, Finset.mul_sum]
  rw [sum_sym_char_two (fun (a b : Fin k) => y ^ (2 ^ (a : ℕ)) * (y ^ (2 ^ (b : ℕ)) *
    E k w (t + 2 ^ (a : ℕ) + 2 ^ (b : ℕ)) j u))]
  · apply Finset.sum_congr rfl
    intro s _
    rw [← mul_assoc, ← pow_add, add_assoc, ← two_mul, ← pow_succ']
  · intro a b
    rw [add_right_comm t]
    ring

omit [Fintype σ] [DecidableEq σ] in
/-- **The repeated-argument recursion.** `E^{(t)}_{j+2}(Y, Y, Z) = E^{(t)}_{j+1}(Y, Z) + Y E^{(t+1)}_j(Z)`. -/
theorem E_rec {k : ℕ} (hk : 1 ≤ k) (w : P2) (t j : ℕ) (y : P2) (u : Fin j → P2) :
    E k w t (j + 2) (Fin.cons y (Fin.cons y u)) =
      E k w t (j + 1) (Fin.cons y u) + y * E k w (t + 1) j u := by
  obtain ⟨k', rfl⟩ : ∃ k', k = k' + 1 := ⟨k - 1, by omega⟩
  rw [E_diag, E_cons, Fin.sum_univ_castSucc, Fin.sum_univ_succ]
  have hlast : E (k' + 1) w (t + 2 ^ ((Fin.last k' : ℕ) + 1)) j u = 0 := by
    apply E_big
    have : k' + 1 < 2 ^ (k' + 1) := Nat.lt_two_pow_self
    simp only [Fin.val_last]
    omega
  rw [hlast, mul_zero, add_zero]
  simp only [Fin.val_zero, pow_zero, pow_one, Fin.val_castSucc, Fin.val_succ]
  linear_combination (-(y * E (k' + 1) w (t + 1) j u)) * two_eq_zero_P2

omit [Fintype σ] [DecidableEq σ] in
/-- The component of degree `d` of `w · M`, for `M` homogeneous of degree `S`. -/
theorem hc_mul_homogeneous (w M : P2) {S : ℕ} (hM : M.IsHomogeneous S) (d : ℕ) :
    homogeneousComponent d (w * M) =
      if S ≤ d then homogeneousComponent (d - S) w * M else 0 := by
  conv_lhs => rw [← sum_homogeneousComponent w, Finset.sum_mul, map_sum]
  have hterm : ∀ i, homogeneousComponent d (homogeneousComponent i w * M) =
      if i + S = d then homogeneousComponent i w * M else 0 := by
    intro i
    rw [homogeneousComponent_of_mem ((homogeneousComponent_isHomogeneous i w).mul hM)]
    split_ifs with h1 h2 h2 <;> first | rfl | omega
  simp_rw [hterm]
  split_ifs with hS
  · rw [Finset.sum_eq_single (d - S)]
    · rw [ite_eq_left (by omega)]
    · intro b _ hb; rw [ite_eq_right (by omega)]
    · intro hnot
      rw [ite_eq_left (by omega), homogeneousComponent_eq_zero _ _ (by
        simp only [Finset.mem_range, not_lt] at hnot; omega), zero_mul]
  · apply Finset.sum_eq_zero
    intro i _
    rw [ite_eq_right (by omega)]

omit [Fintype σ] [DecidableEq σ] in
/-- **Evaluation at generators.** `E^{(t)}_j(y_{i_1}, …, y_{i_j})` is the component of degree
`k − 1 − t` of `w ∏_a xhat(y_{i_a})`. -/
theorem E_eval {k t : ℕ} (ht : t < k) (w : P2) (j : ℕ) (i : Fin j → σ) :
    E k w t j (fun a => X (i a)) =
      homogeneousComponent (k - 1 - t) (w * ∏ a, xhat k (X (i a))) := by
  have hprod : (∏ a, xhat k (X (i a) : P2)) =
      ∑ τ : Fin j → Fin k, ∏ a, (X (i a) : P2) ^ (2 ^ (τ a : ℕ)) := by
    simp only [xhat, ← Fin.sum_univ_eq_sum_range (fun s => (X _ : P2) ^ (2 ^ s))]
    exact Fintype.prod_sum _
  rw [hprod, Finset.mul_sum, map_sum, E]
  apply Finset.sum_congr rfl
  intro τ _
  have hhom : (∏ a, (X (i a) : P2) ^ (2 ^ (τ a : ℕ))).IsHomogeneous (∑ a, 2 ^ (τ a : ℕ)) :=
    IsHomogeneous.prod _ _ _ (fun a _ => by simpa using (isHomogeneous_X (ZMod 2) (i a)).pow _)
  rw [hc_mul_homogeneous _ _ hhom, hcw, mul_comm]
  by_cases hS : t + ∑ a, 2 ^ (τ a : ℕ) < k
  · rw [ite_eq_left hS, ite_eq_left (by omega), show k - 1 - t - ∑ a, 2 ^ (τ a : ℕ) =
      k - 1 - (t + ∑ a, 2 ^ (τ a : ℕ)) by omega]
  · rw [ite_eq_right hS, ite_eq_right (by omega), zero_mul]

omit [Fintype σ] [DecidableEq σ] in
/-- **Multi-additivity on sums of generators.** -/
theorem E_span (k : ℕ) (w : P2) (t j : ℕ) (A : Fin j → Finset σ) :
    E k w t j (fun a => ∑ i ∈ A a, X i) =
      ∑ f ∈ Fintype.piFinset A, E k w t j (fun a => X (f a)) := by
  simp only [E]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro τ _
  rw [← Finset.sum_mul]
  congr 1
  simp_rw [sum_pow_char_pow]
  exact Finset.prod_univ_sum A (fun a i => (X i : P2) ^ (2 ^ (τ a : ℕ)))
end

end MathResearch.PerOrderForms
