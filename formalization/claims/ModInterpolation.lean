/-
Claim: lem:mod-interpolation
Source: https://kbr.is-a.dev/math-research/#mod-pruned-polynomial
Scope: Full interpolation identity, zero case p = 2, and joint total-degree bound p - 3 for p ≥ 3; generalized to every nontrivial commutative coefficient ring and every natural number p ≥ 3. Does not formalize the surrounding MOD axiom certificate or source substitution.
Declarations: MathResearch.mod_interpolation MathResearch.mod_interpolation_two
-/
import Mathlib.Algebra.MvPolynomial.CommRing
import Mathlib.Tactic.Ring

namespace MathResearch

noncomputable section

open MvPolynomial

variable {R : Type*} [CommRing R]

/- Variables 0 and 1 are t and a, respectively. All degrees below are joint
total degrees in these two independent indeterminates, not degrees in a alone. -/
abbrev modT : MvPolynomial (Fin 2) R := X 0
abbrev modA : MvPolynomial (Fin 2) R := X 1

def powerDifference (n : ℕ) : MvPolynomial (Fin 2) R :=
  match n with
  | 0 => 1
  | n + 1 => modT * powerDifference n + (modT - 1) ^ (n + 1)

lemma powerDifference_eq (n : ℕ) :
    powerDifference (R := R) n = modT ^ (n + 1) - (modT - 1) ^ (n + 1) := by
  induction n with
  | zero => simp [powerDifference]
  | succ n ih =>
    rw [powerDifference, ih]
    simp only [pow_succ]
    ring

def interpolationQuotient (n : ℕ) : MvPolynomial (Fin 2) R :=
  match n with
  | 0 => 1
  | n + 1 => (modT + modA - 1) * interpolationQuotient n + powerDifference (n + 1)

lemma interpolationQuotient_identity (n : ℕ) :
    (modT + modA - 1) ^ (n + 2) - modA * modT ^ (n + 2) -
      (1 - modA) * (modT - 1) ^ (n + 2) =
      (modA ^ 2 - modA) * interpolationQuotient (R := R) n := by
  induction n with
  | zero => simp only [interpolationQuotient]; ring
  | succ n ih =>
    rw [interpolationQuotient, powerDifference_eq]
    calc
      _ = (modT + modA - 1) *
          ((modT + modA - 1) ^ (n + 2) - modA * modT ^ (n + 2) -
            (1 - modA) * (modT - 1) ^ (n + 2)) +
          (modA ^ 2 - modA) * (modT ^ (n + 2) - (modT - 1) ^ (n + 2)) := by
            simp only [show n + 1 + 2 = (n + 2) + 1 by omega, pow_succ]
            ring
      _ = _ := by rw [ih]; ring

variable [Nontrivial R]

private lemma degree_t_sub_one : (modT (R := R) - 1).totalDegree ≤ 1 := by
  exact (totalDegree_sub _ _).trans (by simp [modT])

private lemma degree_shift : (modT (R := R) + modA - 1).totalDegree ≤ 1 := by
  apply (totalDegree_sub _ _).trans
  apply max_le
  · exact (totalDegree_add _ _).trans (by simp [modT, modA])
  · simp

lemma powerDifference_degree (n : ℕ) :
    (powerDifference (R := R) n).totalDegree ≤ n := by
  induction n with
  | zero => simp [powerDifference]
  | succ n ih =>
    rw [powerDifference]
    apply (totalDegree_add _ _).trans
    apply max_le
    · exact (totalDegree_mul _ _).trans (by simpa [modT, Nat.add_comm] using Nat.add_le_add_left ih 1)
    · exact (totalDegree_pow _ _).trans (by simpa using Nat.mul_le_mul_left (n + 1) (degree_t_sub_one (R := R)))

lemma interpolationQuotient_degree (n : ℕ) :
    (interpolationQuotient (R := R) n).totalDegree ≤ n := by
  induction n with
  | zero => simp [interpolationQuotient]
  | succ n ih =>
    rw [interpolationQuotient]
    apply (totalDegree_add _ _).trans
    apply max_le
    · exact (totalDegree_mul _ _).trans (by simpa [Nat.add_comm] using Nat.add_le_add (degree_shift (R := R)) ih)
    · exact powerDifference_degree (n + 1)

theorem mod_interpolation (p : ℕ) (hp : 3 ≤ p) :
    ∃ q : MvPolynomial (Fin 2) R,
      (modT + modA - 1) ^ (p - 1) - modA * modT ^ (p - 1) -
        (1 - modA) * (modT - 1) ^ (p - 1) = (modA ^ 2 - modA) * q ∧
      q.totalDegree ≤ p - 3 := by
  refine ⟨interpolationQuotient (p - 3), ?_, interpolationQuotient_degree (p - 3)⟩
  simpa only [show p - 3 + 2 = p - 1 by omega] using
    interpolationQuotient_identity (R := R) (p - 3)

omit [Nontrivial R] in
theorem mod_interpolation_two :
    (modT + modA - 1) ^ (2 - 1) - modA * modT ^ (2 - 1) -
      (1 - modA) * (modT - 1) ^ (2 - 1) = (0 : MvPolynomial (Fin 2) R) := by
  norm_num
  ring

end

end MathResearch
