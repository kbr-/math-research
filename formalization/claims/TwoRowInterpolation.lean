/-
Claim: lem:two-functional-row-state-interpolation
Source: https://kbr.is-a.dev/math-research/#lean-two-functional-row-interpolation
Scope: Ordinary degree-complete bilinear state interpolation for two binary functional rows, without cross-row collision axioms, through max(original degree,2).
Declarations: MathResearch.PolynomialCalculus.twoRow_interpolation
-/
import claims.SquarefreePairDivisibility
import Mathlib.Tactic.Push
import Mathlib.Tactic.SplitIfs
import Mathlib.Tactic.FinCases

namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial
open scoped BigOperators
abbrev TwoRowVar (n : ℕ) := Fin 2 × Fin n
abbrev TwoRowPoly (n : ℕ) := Poly (ZMod 2) (TwoRowVar n)

def twoRowSum (n : ℕ) (r : Fin 2) : TwoRowPoly n := ∑ j : Fin n, X (r,j)
def twoRowBase (n : ℕ) : Set (TwoRowPoly n) :=
  booleanBase ∪ {f | ∃ r, f = twoRowSum n r - 1} ∪
    {f | ∃ r j k, j ≠ k ∧ f = X (r,j) * X (r,k)}
def twoRowPoint {n : ℕ} (j k : Fin n) (v : TwoRowVar n) : ZMod 2 :=
  if v.1 = 0 then if v.2 = j then 1 else 0 else if v.2 = k then 1 else 0

def twoRowInterp (n : ℕ) : TwoRowPoly n →ₗ[ZMod 2] TwoRowPoly n where
  toFun P := ∑ j : Fin n, ∑ k : Fin n,
    (eval (twoRowPoint j k) P) • (X (0,j) * X (1,k))
  map_add' := by intros; simp [map_add, add_smul, Finset.sum_add_distrib]
  map_smul' := by intros; simp [smul_eval, mul_smul, Finset.smul_sum]

private theorem interp_one (n : ℕ) : twoRowInterp n 1 = twoRowSum n 0 * twoRowSum n 1 := by
  simp only [twoRowInterp, LinearMap.coe_mk, AddHom.coe_mk, map_one, one_smul,
    twoRowSum, Finset.sum_mul, Finset.mul_sum]
  rw [Finset.sum_comm]
private theorem interp_X_zero {n : ℕ} (j : Fin n) :
    twoRowInterp n (X (0,j)) = X (0,j) * twoRowSum n 1 := by
  simp [twoRowInterp, twoRowPoint, twoRowSum, Finset.mul_sum, ite_smul]
private theorem interp_X_one {n : ℕ} (k : Fin n) :
    twoRowInterp n (X (1,k)) = twoRowSum n 0 * X (1,k) := by
  simp [twoRowInterp, twoRowPoint, twoRowSum, Finset.sum_mul, ite_smul]
private theorem interp_pair {n : ℕ} (j k : Fin n) :
    twoRowInterp n (X (0,j) * X (1,k)) = X (0,j) * X (1,k) := by
  simp [twoRowInterp, twoRowPoint, ite_smul]

private theorem twoRowSum_degree (n : ℕ) (r : Fin 2) :
    (twoRowSum n r).totalDegree ≤ 1 := by
  apply totalDegree_finsetSum_le
  intro j _
  simp

private theorem row_generator (n : ℕ) (r : Fin 2) :
    twoRowSum n r - 1 ∈ nsSpace (twoRowBase n) 1 := by
  have hd : (twoRowSum n r - 1).totalDegree ≤ 1 :=
    (totalDegree_sub _ _).trans (max_le (twoRowSum_degree n r) (by simp))
  simpa only [one_mul] using nsSpace_generator (q := (1 : TwoRowPoly n))
    (F := twoRowBase n) (B := 1) (f := twoRowSum n r - 1)
    (Or.inl (Or.inr ⟨r, rfl⟩)) (by simpa using hd)

private theorem one_error (n : ℕ) :
    1 - twoRowInterp n 1 ∈ nsSpace (twoRowBase n) 2 := by
  have h0 := nsSpace_mono (Set.Subset.refl _) (show 1 ≤ 2 by decide) (row_generator n 0)
  have h1 := nsSpace_mono (Set.Subset.refl _)
    (show 1 + (twoRowSum n 0).totalDegree ≤ 2 by have := twoRowSum_degree n 0; omega)
    (nsSpace_mul (row_generator n 1) (twoRowSum n 0))
  rw [interp_one]
  have he : (1 : TwoRowPoly n) - twoRowSum n 0 * twoRowSum n 1 =
      -(twoRowSum n 0 - 1) - twoRowSum n 0 * (twoRowSum n 1 - 1) := by ring
  rw [he]
  exact Submodule.sub_mem _ (Submodule.neg_mem _ h0) h1

private theorem variable_error {n : ℕ} (v : TwoRowVar n) :
    X v - twoRowInterp n (X v) ∈ nsSpace (twoRowBase n) 2 := by
  rcases v with ⟨r,j⟩
  fin_cases r
  · change X ((0 : Fin 2),j) - twoRowInterp n (X (0,j)) ∈ nsSpace (twoRowBase n) 2
    have h := nsSpace_mul (row_generator n 1) (X (0,j))
    have hh : X (0,j) * (twoRowSum n 1 - 1) ∈ nsSpace (twoRowBase n) 2 := by
      simpa using h
    rw [interp_X_zero]
    have he : (X (0,j) : TwoRowPoly n) - X (0,j) * twoRowSum n 1 =
        -(X (0,j) * (twoRowSum n 1 - 1)) := by ring
    rw [he]
    exact Submodule.neg_mem _ hh
  · change X ((1 : Fin 2),j) - twoRowInterp n (X (1,j)) ∈ nsSpace (twoRowBase n) 2
    have h := nsSpace_mul (row_generator n 0) (X (1,j))
    have hh : X (1,j) * (twoRowSum n 0 - 1) ∈ nsSpace (twoRowBase n) 2 := by
      simpa using h
    rw [interp_X_one]
    have he : (X (1,j) : TwoRowPoly n) - twoRowSum n 0 * X (1,j) =
        -(X (1,j) * (twoRowSum n 0 - 1)) := by ring
    rw [he]
    exact Submodule.neg_mem _ hh

private theorem point_pair_zero {n : ℕ} (j k a b : Fin n) (r : Fin 2) (hab : a ≠ b) :
    twoRowPoint j k (r,a) * twoRowPoint j k (r,b) = 0 := by
  fin_cases r <;> simp only [twoRowPoint] <;> split_ifs <;> simp_all

private theorem support_error {n : ℕ} (S : Finset (TwoRowVar n)) :
    supportMonomial S - twoRowInterp n (supportMonomial S) ∈
      nsSpace (twoRowBase n) (max S.card 2) := by
  classical
  by_cases hgood : ∀ x ∈ S, ∀ y ∈ S, x.1 = y.1 → x = y
  · have hc : S.card ≤ 2 := by
      calc
        S.card ≤ (Finset.univ : Finset (Fin 2)).card :=
          Finset.card_le_card_of_injOn Prod.fst (by simp) hgood
        _ = 2 := by simp
    have hcases : S.card = 0 ∨ S.card = 1 ∨ S.card = 2 := by omega
    rcases hcases with h0 | h1 | h2
    · have hs := Finset.card_eq_zero.mp h0
      subst S
      simpa [supportMonomial] using one_error n
    · obtain ⟨v, rfl⟩ := Finset.card_eq_one.mp h1
      simpa [supportMonomial] using variable_error v
    · obtain ⟨x, y, hxy, rfl⟩ := Finset.card_eq_two.mp h2
      have hr : x.1 ≠ y.1 := by
        intro heq
        exact hxy (hgood x (by simp) y (by simp) heq)
      rcases x with ⟨r,j⟩
      rcases y with ⟨t,k⟩
      fin_cases r <;> fin_cases t
      · exact False.elim (hr rfl)
      · have he : supportMonomial ({((0 : Fin 2),j), ((1 : Fin 2),k)} :
            Finset (TwoRowVar n)) = X (0,j) * X (1,k) := by simp [supportMonomial]
        change supportMonomial ({((0 : Fin 2),j), ((1 : Fin 2),k)} : Finset (TwoRowVar n)) -
          twoRowInterp n (supportMonomial {((0 : Fin 2),j), ((1 : Fin 2),k)}) ∈ _
        rw [he, interp_pair, sub_self]
        exact Submodule.zero_mem _
      · have he : supportMonomial ({((1 : Fin 2),j), ((0 : Fin 2),k)} :
            Finset (TwoRowVar n)) = X (0,k) * X (1,j) := by
          simp [supportMonomial, mul_comm]
        change supportMonomial ({((1 : Fin 2),j), ((0 : Fin 2),k)} : Finset (TwoRowVar n)) -
          twoRowInterp n (supportMonomial {((1 : Fin 2),j), ((0 : Fin 2),k)}) ∈ _
        rw [he, interp_pair, sub_self]
        exact Submodule.zero_mem _
      · exact False.elim (hr rfl)
  · push Not at hgood
    obtain ⟨x, hx, y, hy, hr, hxy⟩ := hgood
    rcases x with ⟨r,a⟩
    rcases y with ⟨t,b⟩
    change r = t at hr
    subst t
    have hab : a ≠ b := by intro heq; apply hxy; cases heq; rfl
    have hF : (X (r,a) : TwoRowPoly n) * X (r,b) ∈ twoRowBase n :=
      Or.inr ⟨r,a,b,hab,rfl⟩
    have hS := supportMonomial_pair_ns (twoRowBase n) S (r,a) (r,b) hx hy hxy hF
    have heval (j k : Fin n) : eval (twoRowPoint j k) (supportMonomial S) = 0 := by
      rw [supportMonomial_pair_factor S (r,a) (r,b) hx hy hxy]
      simp only [map_mul, eval_X, point_pair_zero j k a b r hab, mul_zero]
    have hI : twoRowInterp n (supportMonomial S) = 0 := by
      simp [twoRowInterp, heval]
    rw [hI, sub_zero]
    exact nsSpace_mono (Set.Subset.refl _) (le_max_left _ _) hS

theorem twoRow_interpolation {n : ℕ} (P : TwoRowPoly n) :
    P - twoRowInterp n P ∈ nsSpace (twoRowBase n) (max P.totalDegree 2) := by
  classical
  have hbool : booleanBase ⊆ twoRowBase n := fun _ h => Or.inl (Or.inl h)
  have hfirst := nsSpace_mono hbool (le_max_left P.totalDegree 2) (squarefreePart_ns P)
  have hI : twoRowInterp n (squarefreePart P) = twoRowInterp n P := by
    simp only [twoRowInterp, LinearMap.coe_mk, AddHom.coe_mk, squarefreePart_eval]
  have hsecond : squarefreePart P - twoRowInterp n (squarefreePart P) ∈
      nsSpace (twoRowBase n) (max P.totalDegree 2) := by
    have he : squarefreePart P - twoRowInterp n (squarefreePart P) =
        ∑ d ∈ P.support, P.coeff d •
          (supportMonomial d.support - twoRowInterp n (supportMonomial d.support)) := by
      simp only [squarefreePart, map_sum, map_smul, smul_sub, Finset.sum_sub_distrib]
    rw [he]
    apply Submodule.sum_mem
    intro d hd
    apply Submodule.smul_mem
    apply nsSpace_mono (Set.Subset.refl _) (max_le_max ?_ le_rfl) (support_error d.support)
    calc
      d.support.card = ∑ _i ∈ d.support, 1 := by simp
      _ ≤ d.sum (fun _ n => n) := Finset.sum_le_sum (fun i hi =>
        Nat.one_le_iff_ne_zero.mpr (Finsupp.mem_support_iff.mp hi))
      _ ≤ P.totalDegree := le_totalDegree hd
  have he : P - twoRowInterp n P = (P - squarefreePart P) +
      (squarefreePart P - twoRowInterp n (squarefreePart P)) := by rw [hI]; ring
  rw [he]
  exact Submodule.add_mem _ hfirst hsecond

end
end MathResearch.PolynomialCalculus
