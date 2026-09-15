/-
Claim: lem:binary-degree-controlled-Boolean-reduction
Source: https://kbr.is-a.dev/math-research/#lean-binary-degree-controlled-Boolean-reduction
Scope: Binary squarefree reduction and original-total-degree ordinary NS witnesses; extracted binary scope of historical field reduction.
Declarations: MathResearch.PolynomialCalculus.supportMonomial_degree MathResearch.PolynomialCalculus.supportMonomial_restricted MathResearch.PolynomialCalculus.squarefreePart_degree MathResearch.PolynomialCalculus.squarefreePart_restricted MathResearch.PolynomialCalculus.squarefreePart_eval MathResearch.PolynomialCalculus.squarefreePart_eq_zero_of_eval_zero MathResearch.PolynomialCalculus.squarefreePart_ns MathResearch.PolynomialCalculus.boolean_vanishing_ns MathResearch.PolynomialCalculus.boolean_vanishing_ns_bound MathResearch.PolynomialCalculus.polynomial_boolean_ns MathResearch.PolynomialCalculus.squarefreePart_ns_bound MathResearch.PolynomialCalculus.polynomial_boolean_ns_bound
-/
import claims.PolynomialCalculusReuse
import Mathlib.Tactic.Ring
import Mathlib.FieldTheory.Finite.Polynomial
import Mathlib.Algebra.Field.ZMod
import Mathlib.Tactic.FinCases
namespace MathResearch.PolynomialCalculus
noncomputable section
open scoped BigOperators
open MvPolynomial
variable {V : Type} [DecidableEq V]

/-- The multilinear monomial on a finite support. -/
def supportMonomial (S : Finset V) : MvPolynomial V (ZMod 2) := ∏ i ∈ S, X i

def squarefreePart (P : MvPolynomial V (ZMod 2)) : MvPolynomial V (ZMod 2) :=
  ∑ d ∈ P.support, P.coeff d • supportMonomial d.support

omit [DecidableEq V] in
theorem supportMonomial_degree (S : Finset V) : (supportMonomial S).totalDegree ≤ S.card := by
  simpa [supportMonomial] using totalDegree_finsetProd S (fun i => (X i : MvPolynomial V (ZMod 2)))

theorem supportMonomial_restricted (S : Finset V) :
    supportMonomial S ∈ restrictDegree V (ZMod 2) 1 := by
  rw [mem_restrictDegree_iff_sup]
  intro i
  rw [← degreeOf_def]
  have h := degreeOf_prod_le i S (fun j => (X j : MvPolynomial V (ZMod 2)))
  by_cases hi : i ∈ S
  · simpa [supportMonomial, degreeOf_X, hi] using h
  · exact (by simpa [supportMonomial, degreeOf_X, hi] using h :
      (supportMonomial S).degreeOf i ≤ 0).trans (by decide)

omit [DecidableEq V] in
private theorem support_card_le_sum (d : V →₀ ℕ) : d.support.card ≤ d.sum (fun _ n => n) := by
  classical
  change d.support.card ≤ ∑ i ∈ d.support, d i
  calc
    d.support.card = ∑ _i ∈ d.support, 1 := by simp
    _ ≤ ∑ i ∈ d.support, d i := Finset.sum_le_sum (fun i hi => Nat.one_le_iff_ne_zero.mpr
      (Finsupp.mem_support_iff.mp hi))

omit [DecidableEq V] in
theorem squarefreePart_degree (P : MvPolynomial V (ZMod 2)) :
    (squarefreePart P).totalDegree ≤ P.totalDegree := by
  apply totalDegree_finsetSum_le
  intro d hd
  apply (totalDegree_smul_le _ _).trans
  apply (supportMonomial_degree _).trans
  apply (support_card_le_sum d).trans
  exact le_totalDegree hd

theorem squarefreePart_restricted (P : MvPolynomial V (ZMod 2)) :
    squarefreePart P ∈ restrictDegree V (ZMod 2) 1 := by
  apply Submodule.sum_mem
  intro d _
  exact Submodule.smul_mem _ _ (supportMonomial_restricted _)

private theorem binary_pow (x : ZMod 2) (n : ℕ) (hn : n ≠ 0) : x^n = x := by
  fin_cases x
  · exact zero_pow hn
  · exact one_pow n

omit [DecidableEq V] in
theorem squarefreePart_eval (P : MvPolynomial V (ZMod 2)) (v : V → ZMod 2) :
    eval v (squarefreePart P) = eval v P := by
  classical
  conv_rhs => rw [P.as_sum]
  simp only [squarefreePart, map_sum, smul_eval]
  apply Finset.sum_congr rfl
  intro d hd
  rw [monomial_eq]
  simp only [map_mul, eval_C, supportMonomial, Finsupp.prod, eval_prod, eval_X, eval_pow]
  congr 1
  apply Finset.prod_congr rfl
  intro i hi
  exact (binary_pow (v i) (d i) (Finsupp.mem_support_iff.mp hi)).symm

theorem squarefreePart_eq_zero_of_eval_zero [Fintype V] (P : MvPolynomial V (ZMod 2))
    (hP : ∀ v : V → ZMod 2, eval v P = 0) : squarefreePart P = 0 := by
  apply MvPolynomial.eq_zero_of_eval_eq_zero V (ZMod 2)
  · intro v
    rw [squarefreePart_eval, hP]
  · simpa using squarefreePart_restricted P
omit [DecidableEq V] in
private theorem variable_power_reduction (i : V) (n : ℕ) :
    (X i : Poly (ZMod 2) V)^(n+1) - X i ∈ nsSpace booleanBase (n+1) := by
  induction n with
  | zero => simp
  | succ n ih =>
    have hg : (X i : Poly (ZMod 2) V)^n * (X i^2-X i) ∈ nsSpace booleanBase (n+2) := by
      apply nsSpace_generator (F := booleanBase)
        (f := (X i : Poly (ZMod 2) V)^2-X i) (q := X i^n)
        (by exact ⟨i,rfl⟩)
      apply (totalDegree_mul _ _).trans
      have hpow := totalDegree_pow (X i : Poly (ZMod 2) V) 2
      have hsub := totalDegree_sub (X i^2 : Poly (ZMod 2) V) (X i)
      simp only [totalDegree_X_pow, totalDegree_X] at *
      omega
    have hi : (X i : Poly (ZMod 2) V)^(n+1)-X i ∈ nsSpace booleanBase (n+2) :=
      nsSpace_mono (Set.Subset.refl _) (by omega) ih
    have he : (X i : Poly (ZMod 2) V)^(n+1+1)-X i =
        X i^n*(X i^2-X i)+(X i^(n+1)-X i) := by
      simp only [pow_succ]
      ring
    rw [he]
    exact Submodule.add_mem _ hg hi
private theorem product_power_reduction (S : Finset V) (d : V → ℕ)
    (hd : ∀ i ∈ S, 1 ≤ d i) :
    (∏ i ∈ S, (X i : Poly (ZMod 2) V)^(d i)) - supportMonomial S ∈
      nsSpace booleanBase (∑ i ∈ S, d i) := by
  classical
  revert hd
  induction S using Finset.induction_on with
  | empty => intro _; simp [supportMonomial]
  | @insert i S hi ih =>
    intro hd
    have hdS : ∀ j ∈ S, 1 ≤ d j := fun j hj => hd j (Finset.mem_insert_of_mem hj)
    have hdi := hd i (Finset.mem_insert_self _ _)
    have hvar : (X i : Poly (ZMod 2) V)^(d i)-X i ∈ nsSpace booleanBase (d i) := by
      simpa [Nat.sub_add_cancel hdi] using variable_power_reduction i (d i-1)
    have hfirst : (X i : Poly (ZMod 2) V)^(d i) *
        ((∏ j ∈ S, (X j : Poly (ZMod 2) V)^(d j))-supportMonomial S) ∈
        nsSpace booleanBase (d i + ∑ j ∈ S, d j) := by
      exact nsSpace_mono (Set.Subset.refl _) (by simp [totalDegree_X_pow, Nat.add_comm])
        (nsSpace_mul (ih hdS) (X i^(d i)))
    have hcard : S.card ≤ ∑ j ∈ S, d j := by
      calc
        S.card = ∑ _j ∈ S, 1 := by simp
        _ ≤ ∑ j ∈ S, d j := Finset.sum_le_sum hdS
    have hsecond : supportMonomial S * ((X i : Poly (ZMod 2) V)^(d i)-X i) ∈
        nsSpace booleanBase (d i + ∑ j ∈ S, d j) :=
      nsSpace_mono (Set.Subset.refl _) (Nat.add_le_add_left
        ((supportMonomial_degree S).trans hcard) _) (nsSpace_mul hvar (supportMonomial S))
    rw [Finset.sum_insert hi, Finset.prod_insert hi]
    have he : (X i : Poly (ZMod 2) V)^(d i) *
        (∏ j ∈ S, (X j : Poly (ZMod 2) V)^(d j)) - supportMonomial (insert i S) =
        X i^(d i)*((∏ j ∈ S, (X j : Poly (ZMod 2) V)^(d j))-supportMonomial S) +
          supportMonomial S*(X i^(d i)-X i) := by
      rw [supportMonomial, Finset.prod_insert hi]
      change _ - X i * supportMonomial S = _
      ring
    rw [he]
    exact Submodule.add_mem _ hfirst hsecond

private theorem monomial_reduction (d : V →₀ ℕ) :
    monomial d (1 : ZMod 2) - supportMonomial d.support ∈
      nsSpace booleanBase (d.sum (fun _ n => n)) := by
  rw [monomial_eq, C_1, one_mul]
  exact product_power_reduction d.support d
    (fun i hi => Nat.one_le_iff_ne_zero.mpr (Finsupp.mem_support_iff.mp hi))

theorem squarefreePart_ns (P : Poly (ZMod 2) V) :
    P-squarefreePart P ∈ nsSpace booleanBase P.totalDegree := by
  classical
  have he : P-squarefreePart P = ∑ d ∈ P.support,
      P.coeff d • (monomial d (1 : ZMod 2)-supportMonomial d.support) := by
    conv_lhs => lhs; rw [P.as_sum]
    rw [squarefreePart, ← Finset.sum_sub_distrib]
    apply Finset.sum_congr rfl
    intro d _
    simp [smul_sub, smul_eq_C_mul, C_mul_monomial]
  rw [he]
  apply Submodule.sum_mem
  intro d hd
  apply Submodule.smul_mem
  exact nsSpace_mono (Set.Subset.refl _) (le_totalDegree hd) (monomial_reduction d)

theorem boolean_vanishing_ns [Fintype V] (P : Poly (ZMod 2) V)
    (hP : ∀ v : V → ZMod 2, eval v P = 0) : P ∈ nsSpace booleanBase P.totalDegree := by
  simpa [squarefreePart_eq_zero_of_eval_zero P hP] using squarefreePart_ns P

theorem boolean_vanishing_ns_bound [Fintype V] (P : Poly (ZMod 2) V) (d : ℕ)
    (hd : P.totalDegree ≤ d) (hP : ∀ v : V → ZMod 2, eval v P = 0) :
    P ∈ nsSpace booleanBase d := nsSpace_mono (Set.Subset.refl _) hd (boolean_vanishing_ns P hP)

theorem polynomial_boolean_ns [Fintype V] (q : Poly (ZMod 2) V) :
    q^2-q ∈ nsSpace booleanBase (2*q.totalDegree) := by
  apply boolean_vanishing_ns_bound
  · exact (totalDegree_sub _ _).trans (max_le (totalDegree_pow q 2) (by omega))
  · intro v
    simp only [map_sub, map_pow]
    have h : eval v q ^ 2 = eval v q := ZMod.pow_card _
    rw [h, sub_self]

theorem squarefreePart_ns_bound (P : Poly (ZMod 2) V) (d : ℕ) (hd : P.totalDegree ≤ d) :
    P-squarefreePart P ∈ nsSpace booleanBase d :=
  nsSpace_mono (Set.Subset.refl _) hd (squarefreePart_ns P)

theorem polynomial_boolean_ns_bound [Fintype V] (q : Poly (ZMod 2) V) (k : ℕ)
    (hk : q.totalDegree ≤ k) : q^2-q ∈ nsSpace booleanBase (2*k) :=
  nsSpace_mono (Set.Subset.refl _) (Nat.mul_le_mul_left 2 hk) (polynomial_boolean_ns q)
end
end MathResearch.PolynomialCalculus


