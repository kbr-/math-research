/-
Claim: lem:grid-reduction-coefficients
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#per-order-value-all-dimensions
Scope: Let D be an integral domain, V ⊆ D a finite set, L_V = ∏_{v∈V} (Y − v) and
ρ_N = Y^N mod L_V. If an expression Σ_i c_i ∏_a v_a^{d_{i,a}} (finitely many i, variables a < h)
vanishes for every v ∈ V^h, then for all exponents e_a < |V|,
Σ_i c_i ∏_a [Y^{e_a}] ρ_{d_{i,a}} = 0 (no nonemptiness assumed). Also: ρ_N(v) = v^N on V, deg ρ_N < |V| for V nonempty, deg ρ_N ≤ N, and
ρ_N = Y^N for N < |V|. This is the reduction modulo the subspace polynomial (steps 4–5 of the per-order
lower bound, where V is the F_2-span of y_1, …, y_n), stated for an arbitrary finite set.
Declarations: MathResearch.PerOrderSubspaceReduction.Lpoly MathResearch.PerOrderSubspaceReduction.rho MathResearch.PerOrderSubspaceReduction.eval_rho MathResearch.PerOrderSubspaceReduction.natDegree_rho_lt MathResearch.PerOrderSubspaceReduction.rho_of_lt MathResearch.PerOrderSubspaceReduction.natDegree_rho_le MathResearch.PerOrderSubspaceReduction.coeff_prod_aeval_X MathResearch.PerOrderSubspaceReduction.coeff_reduction
-/
import Mathlib.Combinatorics.Nullstellensatz
import Mathlib.Algebra.Polynomial.Div
import Mathlib.Algebra.Polynomial.BigOperators
import Mathlib.Algebra.MvPolynomial.Degrees

namespace MathResearch.PerOrderSubspaceReduction

noncomputable section

variable {D : Type*} [CommRing D] [IsDomain D]

/-- The vanishing polynomial `L_V = ∏_{v ∈ V} (Y − v)`. -/
def Lpoly (V : Finset D) : Polynomial D := ∏ v ∈ V, (Polynomial.X - Polynomial.C v)

omit [IsDomain D] in
theorem Lpoly_monic (V : Finset D) : (Lpoly V).Monic :=
  Polynomial.monic_prod_of_monic _ _ (fun v _ => Polynomial.monic_X_sub_C v)

theorem natDegree_Lpoly (V : Finset D) : (Lpoly V).natDegree = V.card := by
  rw [Lpoly, Polynomial.natDegree_prod_of_monic _ _ (fun v _ => Polynomial.monic_X_sub_C v)]
  simp

theorem Lpoly_ne_one {V : Finset D} (hV : V.Nonempty) : Lpoly V ≠ 1 := by
  intro h
  have := natDegree_Lpoly V
  rw [h, Polynomial.natDegree_one] at this
  exact absurd this.symm (Finset.card_ne_zero.2 hV)

omit [IsDomain D] in
theorem eval_Lpoly {V : Finset D} {v : D} (hv : v ∈ V) : (Lpoly V).eval v = 0 := by
  rw [Lpoly, Polynomial.eval_prod]
  exact Finset.prod_eq_zero hv (by simp)

/-- `ρ_N = Y^N mod L_V`. -/
def rho (V : Finset D) (N : ℕ) : Polynomial D := Polynomial.X ^ N %ₘ Lpoly V

omit [IsDomain D] in
theorem eval_rho (V : Finset D) (N : ℕ) {v : D} (hv : v ∈ V) : (rho V N).eval v = v ^ N := by
  rw [rho, Polynomial.modByMonic_eq_sub_mul_div, Polynomial.eval_sub, Polynomial.eval_mul,
    eval_Lpoly hv]
  simp

theorem natDegree_rho_lt {V : Finset D} (hV : V.Nonempty) (N : ℕ) : (rho V N).natDegree < V.card := by
  rw [← natDegree_Lpoly V]
  exact Polynomial.natDegree_modByMonic_lt _ (Lpoly_monic V) (Lpoly_ne_one hV)

theorem rho_of_lt {V : Finset D} {N : ℕ} (hN : N < V.card) : rho V N = Polynomial.X ^ N := by
  rw [rho, Polynomial.modByMonic_eq_self_iff (Lpoly_monic V), Polynomial.degree_X_pow,
    Polynomial.degree_eq_natDegree (Lpoly_monic V).ne_zero, natDegree_Lpoly]
  exact_mod_cast hN

theorem natDegree_rho_le {V : Finset D} (hV : V.Nonempty) (N : ℕ) : (rho V N).natDegree ≤ N := by
  by_cases hN : N < V.card
  · rw [rho_of_lt hN, Polynomial.natDegree_X_pow]
  · exact (natDegree_rho_lt hV N).le.trans (by omega)

omit [IsDomain D] in
theorem eval_aeval_X {h : ℕ} (v : Fin h → D) (a : Fin h) (p : Polynomial D) :
    MvPolynomial.eval v (Polynomial.aeval (MvPolynomial.X a : MvPolynomial (Fin h) D) p) =
      p.eval (v a) := by
  rw [Polynomial.aeval_def, Polynomial.hom_eval₂, MvPolynomial.eval_X]
  have : (MvPolynomial.eval v).comp (algebraMap D (MvPolynomial (Fin h) D)) = RingHom.id D :=
    RingHom.ext fun c => by simp [MvPolynomial.algebraMap_eq]
  rw [this]
  rfl

theorem degreeOf_aeval_X {h : ℕ} (a b : Fin h) (p : Polynomial D) :
    MvPolynomial.degreeOf a (Polynomial.aeval (MvPolynomial.X b : MvPolynomial (Fin h) D) p) ≤
      if a = b then p.natDegree else 0 := by
  rw [Polynomial.aeval_eq_sum_range]
  apply (MvPolynomial.degreeOf_sum_le _ _ _).trans
  apply Finset.sup_le
  intro c hc
  rw [MvPolynomial.smul_eq_C_mul]
  apply (MvPolynomial.degreeOf_C_mul_le _ _ _).trans
  split_ifs with hab
  · subst hab
    apply (MvPolynomial.degreeOf_pow_le _ _ _).trans
    have := MvPolynomial.degreeOf_X (R := D) a a
    simp only [↓reduceIte] at this
    rw [this, mul_one]
    exact Nat.lt_succ_iff.1 (Finset.mem_range.1 hc)
  · rw [MvPolynomial.degreeOf_X_pow_of_ne _ hab]

omit [IsDomain D] in
theorem prod_X_pow_eq_monomial {h : ℕ} (f : Fin h → ℕ) :
    (∏ a, (MvPolynomial.X a : MvPolynomial (Fin h) D) ^ f a) =
      MvPolynomial.monomial (Finsupp.equivFunOnFinite.symm f) 1 := by
  rw [MvPolynomial.monomial_eq, map_one, one_mul, Finsupp.prod_fintype _ _ (by simp)]
  simp

omit [IsDomain D] in
/-- The coefficient of `∏_a Y_a^{e_a}` in `∏_a p_a(Y_a)` is `∏_a [Y^{e_a}] p_a`. -/
theorem coeff_prod_aeval_X {h : ℕ} (N : ℕ) (p : Fin h → Polynomial D)
    (hp : ∀ a, (p a).natDegree < N) (e : Fin h → ℕ) (he : ∀ a, e a < N) :
    (∏ a, Polynomial.aeval (MvPolynomial.X a : MvPolynomial (Fin h) D) (p a)).coeff
        (Finsupp.equivFunOnFinite.symm e) =
      ∏ a, (p a).coeff (e a) := by
  classical
  simp_rw [Polynomial.aeval_eq_sum_range' (hp _), MvPolynomial.smul_eq_C_mul]
  rw [Finset.prod_univ_sum, MvPolynomial.coeff_sum, Finset.sum_eq_single e]
  · rw [Finset.prod_mul_distrib, ← map_prod, prod_X_pow_eq_monomial, MvPolynomial.C_mul_monomial,
      mul_one, MvPolynomial.coeff_monomial, ite_eq_left rfl]
  · intro f _ hf
    rw [Finset.prod_mul_distrib, ← map_prod, prod_X_pow_eq_monomial, MvPolynomial.C_mul_monomial,
      mul_one, MvPolynomial.coeff_monomial, ite_eq_right]
    intro heq
    exact hf (Finsupp.equivFunOnFinite.symm.injective heq)
  · intro hnot
    exact absurd (Fintype.mem_piFinset.2 fun a => Finset.mem_range.2 (he a)) hnot

/-- **Reduction of the coefficients.** If `Σ_i c_i ∏_a v_a^{d_{i,a}}` vanishes on `V^h`, then
`Σ_i c_i ∏_a [Y^{e_a}] ρ_{d_{i,a}} = 0` for all exponents `e_a < |V|`. -/
theorem coeff_reduction_of_nonempty {V : Finset D} (hV : V.Nonempty) {h : ℕ} {ι : Type*} [Fintype ι]
    (c : ι → D) (d : ι → Fin h → ℕ)
    (hvan : ∀ v : Fin h → D, (∀ a, v a ∈ V) → ∑ i, c i * ∏ a, v a ^ d i a = 0)
    (e : Fin h → ℕ) (he : ∀ a, e a < V.card) :
    ∑ i, c i * ∏ a, (rho V (d i a)).coeff (e a) = 0 := by
  classical
  set R : MvPolynomial (Fin h) D := ∑ i, MvPolynomial.C (c i) *
    ∏ a, Polynomial.aeval (MvPolynomial.X a : MvPolynomial (Fin h) D) (rho V (d i a)) with hR
  have hR0 : R = 0 := by
    apply MvPolynomial.eq_zero_of_eval_zero_at_prod_finset R (fun _ => V)
    · intro a
      apply lt_of_le_of_lt (MvPolynomial.degreeOf_sum_le _ _ _)
      rw [Finset.sup_lt_iff (Finset.card_pos.2 hV)]
      intro i _
      apply lt_of_le_of_lt (MvPolynomial.degreeOf_C_mul_le _ _ _)
      apply lt_of_le_of_lt (MvPolynomial.degreeOf_prod_le _ _ _)
      calc ∑ b, MvPolynomial.degreeOf a
              (Polynomial.aeval (MvPolynomial.X b : MvPolynomial (Fin h) D) (rho V (d i b)))
            ≤ ∑ b, (if a = b then (rho V (d i b)).natDegree else 0) :=
              Finset.sum_le_sum (fun b _ => degreeOf_aeval_X a b _)
        _ = (rho V (d i a)).natDegree := by rw [Finset.sum_ite_eq]; simp
        _ < V.card := natDegree_rho_lt hV _
    · intro v hv
      rw [hR, map_sum, ← hvan v hv]
      apply Finset.sum_congr rfl
      intro i _
      rw [map_mul, MvPolynomial.eval_C, map_prod]
      congr 1
      apply Finset.prod_congr rfl
      intro a _
      rw [eval_aeval_X, eval_rho _ _ (hv a)]
  have hc : R.coeff (Finsupp.equivFunOnFinite.symm e) = 0 := by rw [hR0]; simp
  rw [hR, MvPolynomial.coeff_sum] at hc
  simp only [MvPolynomial.coeff_C_mul] at hc
  rw [← hc]
  apply Finset.sum_congr rfl
  intro i _
  rw [coeff_prod_aeval_X V.card _ (fun a => natDegree_rho_lt hV _) _ he]

/-- **Coefficient identity from vanishing on a grid** (`lem:grid-reduction-coefficients`). No
nonemptiness is needed: for `V = ∅` there is no admissible exponent unless `h = 0`, and then both
sides are `∑ i, c i`. -/
theorem coeff_reduction {V : Finset D} {h : ℕ} {ι : Type*} [Fintype ι]
    (c : ι → D) (d : ι → Fin h → ℕ)
    (hvan : ∀ v : Fin h → D, (∀ a, v a ∈ V) → ∑ i, c i * ∏ a, v a ^ d i a = 0)
    (e : Fin h → ℕ) (he : ∀ a, e a < V.card) :
    ∑ i, c i * ∏ a, (rho V (d i a)).coeff (e a) = 0 := by
  rcases V.eq_empty_or_nonempty with hV | hV
  · subst hV
    rcases Nat.eq_zero_or_pos h with rfl | hh
    · simpa using hvan Fin.elim0 (fun a => a.elim0)
    · exact absurd (he ⟨0, hh⟩) (by simp)
  · exact coeff_reduction_of_nonempty hV c d hvan e he

end

end MathResearch.PerOrderSubspaceReduction
