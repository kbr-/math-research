/-
Claim: lem:reuse
Source: https://kbr.is-a.dev/math-research/#lean-pc-completed-line-reuse
Scope: Completed-line polynomial multiplication with max(old ceiling, degree multiplier + degree line), NS flattening multiplication, and ordinary NS-to-PC inclusion over any field; zero inputs included.
Declarations: MathResearch.PolynomialCalculus.Derives.mul_polynomial MathResearch.PolynomialCalculus.nsSpace_mul MathResearch.PolynomialCalculus.nsSpace_le_pcSpace
-/
import claims.PolynomialCalculus
import Mathlib.Algebra.MvPolynomial.NoZeroDivisors
import Lean.Elab.Tactic.Omega

namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial
open scoped BigOperators
variable {K V : Type*} [Field K]
variable {F : Set (Poly K V)} {B : ℕ}

private theorem mul_monomial (f : Poly K V) (hf : Derives F B f)
    (s : V →₀ ℕ) (a : K) :
    Derives F (max B ((monomial s a).totalDegree + f.totalDegree))
      (monomial s a * f) := by
  apply induction_on_monomial (motive := fun q : Poly K V =>
    Derives F (max B (q.totalDegree + f.totalDegree)) (q * f))
  · intro c
    simpa only [totalDegree_C, zero_add, C_mul'] using
      (Derives.smul c hf).mono (fun _ h => h) (le_max_left B f.totalDegree)
  · intro q v ih
    by_cases hq : q = 0
    · simp only [hq, zero_mul]
      exact .zero
    have hv : (X v : Poly K V) ≠ 0 := X_ne_zero v
    have hd : (q * X v).totalDegree = q.totalDegree + 1 := by
      rw [totalDegree_mul_of_isDomain hq hv, totalDegree_X]
    have hbound : (X v * (q * f)).totalDegree ≤
        max B ((q * X v).totalDegree + f.totalDegree) := by
      apply (totalDegree_mul _ _).trans
      rw [totalDegree_X]
      apply (Nat.add_le_add_left (totalDegree_mul q f) 1).trans
      rw [hd]
      omega
    have hprev := ih.mono (fun _ h => h)
      (show max B (q.totalDegree + f.totalDegree) ≤
        max B ((q * X v).totalDegree + f.totalDegree) by rw [hd]; omega)
    simpa only [mul_assoc, mul_left_comm, mul_comm] using Derives.mul_var v hprev hbound

theorem Derives.mul_polynomial {f : Poly K V} (hf : Derives F B f) (q : Poly K V) :
    Derives F (max B (q.totalDegree + f.totalDegree)) (q * f) := by
  classical
  have heq : q * f = ∑ s ∈ q.support, monomial s (q.coeff s) * f := by
    conv_lhs => rw [q.as_sum, Finset.sum_mul]
  rw [heq]
  change (∑ s ∈ q.support, monomial s (q.coeff s) * f) ∈
    pcSpace F (max B (q.totalDegree + f.totalDegree))
  apply Submodule.sum_mem
  intro s hs
  have hm := mul_monomial f hf s (q.coeff s)
  apply hm.mono (fun _ h => h)
  apply max_le_max le_rfl
  exact Nat.add_le_add_right ((totalDegree_monomial_le s _).trans (le_totalDegree hs)) _

theorem nsSpace_mul {p : Poly K V} (hp : p ∈ nsSpace F B) (q : Poly K V) :
    q * p ∈ nsSpace F (B + q.totalDegree) := by
  induction hp using Submodule.span_induction with
  | mem p hp =>
    rcases hp with ⟨f, hf, r, rfl, hd⟩
    rw [← mul_assoc]
    apply nsSpace_generator hf
    rw [mul_assoc]
    exact (totalDegree_mul _ _).trans (by omega)
  | zero => simp
  | add x y _ _ ih jh =>
    simpa only [mul_add] using (nsSpace F (B + q.totalDegree)).add_mem ih jh
  | smul a x _ ih =>
    simpa only [mul_smul_comm] using (nsSpace F (B + q.totalDegree)).smul_mem a ih

theorem nsSpace_le_pcSpace (F : Set (Poly K V)) (B : ℕ) :
    nsSpace F B ≤ pcSpace F B := by
  apply Submodule.span_le.mpr
  rintro p ⟨f, hf, q, rfl, hd⟩
  by_cases hz : q * f = 0
  · rw [hz]
    exact .zero
  have hq : q ≠ 0 := left_ne_zero_of_mul hz
  have hfn : f ≠ 0 := right_ne_zero_of_mul hz
  have heq := totalDegree_mul_of_isDomain hq hfn
  have hfd : f.totalDegree ≤ B := by omega
  have h := (Derives.hyp hf hfd).mul_polynomial q
  exact h.mono (fun _ h => h) (by omega)

end
end MathResearch.PolynomialCalculus
