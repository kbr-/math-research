/-
Claim: lem:substitution
Source: https://kbr.is-a.dev/math-research/#lean-pc-degree-substitution
Scope: Ordinary PC substitution and fixed-weight replay from supplied weighted axiom-image proofs, with ceiling T*D+degree(weight), over any field. Variable images have total degree at most T; T=0 and zero predecessors are included.
Declarations: MathResearch.PolynomialCalculus.substitution_degree MathResearch.PolynomialCalculus.Derives.substitute_weighted MathResearch.PolynomialCalculus.Derives.substitute
-/
import claims.PolynomialCalculusReuse

namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial
open scoped BigOperators
variable {K V W : Type*} [Field K]

private theorem substitution_monomial_degree (g : V → Poly K W) (T : ℕ)
    (hg : ∀ v, (g v).totalDegree ≤ T) (s : V →₀ ℕ) (a : K) :
    (aeval g (monomial s a)).totalDegree ≤ T * s.sum (fun _ n => n) := by
  classical
  rw [aeval_monomial]
  apply (totalDegree_mul _ _).trans
  change (C a : Poly K W).totalDegree + _ ≤ _
  rw [totalDegree_C, zero_add, Finsupp.prod]
  apply (totalDegree_finsetProd _ _).trans
  calc
    _ ≤ ∑ v ∈ s.support, T * s v := by
      apply Finset.sum_le_sum
      intro v _
      exact (totalDegree_pow (g v) (s v)).trans (by simpa only [Nat.mul_comm] using Nat.mul_le_mul_right (s v) (hg v))
    _ = T * s.sum (fun _ n => n) := by rw [Finsupp.sum, Finset.mul_sum]

theorem substitution_degree (g : V → Poly K W) (T : ℕ)
    (hg : ∀ v, (g v).totalDegree ≤ T) (f : Poly K V) :
    (aeval g f).totalDegree ≤ T * f.totalDegree := by
  classical
  have heq : aeval g f = ∑ s ∈ f.support, aeval g (monomial s (f.coeff s)) := by
    conv_lhs => rw [f.as_sum, map_sum]
  rw [heq]
  apply totalDegree_finsetSum_le
  intro s hs
  exact (substitution_monomial_degree g T hg s _).trans
    (Nat.mul_le_mul_left T (le_totalDegree hs))

theorem Derives.substitute_weighted {F : Set (Poly K V)} {D : ℕ} {f : Poly K V}
    (hf : Derives F D f) (g : V → Poly K W) (T : ℕ)
    (hg : ∀ v, (g v).totalDegree ≤ T) (G : Set (Poly K W)) (weight : Poly K W)
    (haxioms : ∀ a ∈ F, a.totalDegree ≤ D →
      Derives G (T * D + weight.totalDegree) (weight * aeval g a)) :
    Derives G (T * D + weight.totalDegree) (weight * aeval g f) := by
  induction hf with
  | zero => simpa only [map_zero, mul_zero] using
      (Derives.zero : Derives G (T * D + weight.totalDegree) 0)
  | hyp ha hd => exact haxioms _ ha hd
  | add _ _ ih jh => simpa only [map_add, mul_add] using Derives.add ih jh
  | smul a _ ih => simpa only [map_smul, mul_smul_comm] using Derives.smul a ih
  | @mul_var v p hp hdp ih =>
    by_cases hz : p = 0
    · simp only [hz, mul_zero, map_zero]
      exact .zero
    have hpred : p.totalDegree + 1 ≤ D := by
      rwa [totalDegree_mul_of_isDomain (X_ne_zero v) hz, totalDegree_X, Nat.add_comm] at hdp
    have himage : (weight * aeval g p).totalDegree ≤
        weight.totalDegree + T * p.totalDegree :=
      (totalDegree_mul _ _).trans
        (Nat.add_le_add_left (substitution_degree g T hg p) _)
    have hcost : (g v).totalDegree + (weight * aeval g p).totalDegree ≤
        T * D + weight.totalDegree := by
      have hgv := hg v
      have ht := Nat.mul_le_mul_left T hpred
      rw [Nat.mul_add, Nat.mul_one] at ht
      omega
    have hh := (ih.mul_polynomial (g v)).mono (fun _ h => h)
      (max_le le_rfl hcost)
    simpa only [map_mul, aeval_X, mul_assoc, mul_left_comm] using hh

theorem Derives.substitute {F : Set (Poly K V)} {D : ℕ} {f : Poly K V}
    (hf : Derives F D f) (g : V → Poly K W) (T : ℕ)
    (hg : ∀ v, (g v).totalDegree ≤ T) :
    Derives ((aeval g) '' F) (T * D) (aeval g f) := by
  have h := hf.substitute_weighted g T hg ((aeval g) '' F) 1 (by
    intro a ha hd
    simp only [totalDegree_one, Nat.add_zero, one_mul]
    exact Derives.hyp ⟨a, ha, rfl⟩
      ((substitution_degree g T hg a).trans (Nat.mul_le_mul_left T hd)))
  simpa only [totalDegree_one, Nat.add_zero, one_mul] using h

end
end MathResearch.PolynomialCalculus
