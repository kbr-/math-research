/-
Claim: lem:coordinate-restriction-ideal
Source: https://kbr.is-a.dev/math-research/#lean-coordinate-restriction-ideal
Scope: Zero ordinary coordinate restriction gives literal selected-variable coefficients with degree at most k-1, including k=0 and empty selected families.
Declarations: MathResearch.coordinate_restriction_coefficients
-/
import claims.PolynomialCalculus
import Mathlib.Algebra.MvPolynomial.Rename

namespace MathResearch
noncomputable section
open MvPolynomial
open scoped BigOperators
variable {K σ ι : Type} [Field K] [Fintype σ] [Fintype ι]

abbrev CoordinateFreeIndex (e : ι ↪ σ) := {x : σ // x ∉ Set.range e}

def coordinateRestriction (e : ι ↪ σ) :
    MvPolynomial σ K →ₐ[K] MvPolynomial (CoordinateFreeIndex e) K :=
  killCompl (f := Subtype.val) Subtype.val_injective

omit [Fintype σ] in
private theorem selected_of_support (e : ι ↪ σ) (p : MvPolynomial σ K)
    (hp : coordinateRestriction e p = 0) (d : σ →₀ ℕ) (hd : d ∈ p.support) :
    ∃ i, 1 ≤ d (e i) := by
  classical
  by_contra hn
  push Not at hn
  have hs : (d.support : Set σ) ⊆ Set.range (Subtype.val : CoordinateFreeIndex e → σ) := by
    intro x hx
    refine ⟨⟨x, ?_⟩, rfl⟩
    rintro ⟨i, rfl⟩
    have hdi := Finsupp.mem_support_iff.mp hx
    have hi := hn i
    omega
  have hc := congrArg (fun q => q.coeff (d.comapDomain
    (Subtype.val : CoordinateFreeIndex e → σ) Subtype.val_injective.injOn)) hp
  rw [coordinateRestriction, coeff_killCompl, Finsupp.mapDomain_comapDomain (Subtype.val : CoordinateFreeIndex e → σ) Subtype.val_injective d hs] at hc
  exact MvPolynomial.mem_support_iff.mp hd (by simpa using hc)

private def removedMonomial (d : σ →₀ ℕ) (i : σ) (c : K) : MvPolynomial σ K :=
  monomial (d - Finsupp.single i 1) c

omit [Fintype σ] in
private theorem removedMonomial_identity (d : σ →₀ ℕ) (i : σ) (c : K) (hi : 1 ≤ d i) :
    removedMonomial d i c * X i = monomial d c := by
  have hle : Finsupp.single i 1 ≤ d := Finsupp.single_le_iff.mpr hi
  rw [removedMonomial, X, monomial_mul_monomial, mul_one, tsub_add_cancel_of_le hle]

omit [Fintype σ] in
private theorem removedMonomial_degree (d : σ →₀ ℕ) (i : σ) (c : K) (hi : 1 ≤ d i)
    (k : ℕ) (hk : d.sum (fun _ n => n) ≤ k) :
    (removedMonomial d i c).totalDegree ≤ k-1 := by
  have hle : Finsupp.single i 1 ≤ d := Finsupp.single_le_iff.mpr hi
  have he := congrArg (fun a : σ →₀ ℕ => a.sum (fun _ n => n)) (tsub_add_cancel_of_le hle)
  simp [Finsupp.sum_add_index'] at he
  apply (totalDegree_monomial_le _ _).trans
  change (d - Finsupp.single i 1).sum (fun _ n => n) ≤ k-1
  omega

omit [Fintype σ] in
theorem coordinate_restriction_coefficients (e : ι ↪ σ) (p : MvPolynomial σ K) (k : ℕ)
    (hdeg : p.totalDegree ≤ k) (hp : coordinateRestriction e p = 0) :
    ∃ a : ι → MvPolynomial σ K, (∀ i, (a i).totalDegree ≤ k-1) ∧ p = ∑ i, a i * X (e i) := by
  classical
  have hsel : ∀ d : p.support, ∃ i, 1 ≤ d.val (e i) := fun d => selected_of_support e p hp d.val d.property
  choose s hs using hsel
  let q : p.support → MvPolynomial σ K := fun d => removedMonomial d.val (e (s d)) (p.coeff d.val)
  let a : ι → MvPolynomial σ K := fun i => ∑ d : p.support, if s d = i then q d else 0
  refine ⟨a, ?_, ?_⟩
  · intro i
    apply totalDegree_finsetSum_le
    intro d _
    by_cases hi : s d = i
    · simp only [hi, ite_true]
      exact removedMonomial_degree d.val (e (s d)) _ (hs d) k ((le_totalDegree d.property).trans hdeg)
    · simp [hi]
  · have hsum : (∑ i, a i * X (e i)) = ∑ d : p.support, monomial d.val (p.coeff d.val) := by
      simp only [a, Finset.sum_mul]
      rw [Finset.sum_comm]
      apply Finset.sum_congr rfl
      intro d _
      simp only [ite_mul, zero_mul, Finset.sum_ite_eq, Finset.mem_univ, ite_true]
      exact removedMonomial_identity (K := K) d.val (e (s d)) (p.coeff d.val) (hs d)
    rw [hsum]
    rw [Finset.sum_coe_sort p.support (fun d : σ →₀ ℕ => monomial d (p.coeff d))]
    exact p.as_sum

end
end MathResearch
