/-
Claim: lem:fresh-ENS-scalar-cleanup
Source: https://kbr.is-a.dev/math-research/#lean-fresh-ENS-scalar-cleanup
Scope: Degree-preserving ordinary PC deletion of zero and binary unit-span fresh blocks, with all companion and coefficient Boolean axioms; retained polynomials unchanged.
Declarations: MathResearch.freshENSScalar_old MathResearch.freshENS_scalar_cleanup MathResearch.freshENS_zero_cleanup MathResearch.freshENS_unit_cleanup MathResearch.freshENS_unitSpan_cleanup
-/
import claims.FreshENSBlock
import Mathlib.FieldTheory.Finite.Basic

namespace MathResearch
noncomputable section
open MvPolynomial PolynomialCalculus
open scoped BigOperators
variable {K σ ι : Type*} [Field K] [Fintype ι] {h : ℕ}

def freshENSBlockAxioms (g : ι → MvPolynomial σ K) (h : ℕ) :
    Set (MvPolynomial (FreshENSVars σ ι h) K) :=
  {p | ∃ i, p = freshENSCompanion g h i} ∪
  {p | ∃ u : Fin h, ∃ i : ι, p = X (Sum.inr (u, i)) ^ 2 - X (Sum.inr (u, i))}

def freshENSScalarVars (c : Fin h × ι → K) : FreshENSVars σ ι h → MvPolynomial σ K
  | Sum.inl x => X x
  | Sum.inr v => C (c v)

def freshENSScalar (c : Fin h × ι → K) :
    MvPolynomial (FreshENSVars σ ι h) K →ₐ[K] MvPolynomial σ K := aeval (freshENSScalarVars c)

omit [Fintype ι] in
theorem freshENSScalar_old (c : Fin h × ι → K) (p : MvPolynomial σ K) :
    freshENSScalar c (rename Sum.inl p) = p := by
  rw [freshENSScalar, aeval_rename]
  change aeval X p = p
  exact aeval_X_left_apply p

omit [Fintype ι] in
private theorem scalar_degree (c : Fin h × ι → K) (p : MvPolynomial (FreshENSVars σ ι h) K) :
    (freshENSScalar c p).totalDegree ≤ p.totalDegree := by
  have hc : ∀ v, (freshENSScalarVars (σ := σ) c v).totalDegree ≤ 1 := by
    intro v; cases v <;> simp [freshENSScalarVars]
  simpa [freshENSScalar] using substitution_degree (freshENSScalarVars c) 1 hc p

theorem freshENS_scalar_cleanup (g : ι → MvPolynomial σ K) (h : ℕ)
    (F : Set (MvPolynomial σ K)) (c : Fin h × ι → K)
    (hc : ∀ v, c v ^ 2 = c v)
    (hcomp : ∀ i, freshENSScalar c (freshENSCompanion g h i) = 0)
    {D : ℕ} {p : MvPolynomial (FreshENSVars σ ι h) K}
    (hp : Derives ((rename Sum.inl) '' F ∪ freshENSBlockAxioms g h) D p) :
    Derives F D (freshENSScalar c p) := by
  have hvars : ∀ v, (freshENSScalarVars (σ := σ) c v).totalDegree ≤ 1 := by
    intro v; cases v <;> simp [freshENSScalarVars]
  have hh := hp.substitute_weighted (freshENSScalarVars c) 1 hvars F 1 (by
    intro a ha hd
    simp only [totalDegree_one, Nat.add_zero, one_mul]
    change Derives F D (freshENSScalar c a)
    rcases ha with ha | ha
    · obtain ⟨q, hq, rfl⟩ := ha
      have hdeg := (scalar_degree c (rename Sum.inl q)).trans hd
      rw [freshENSScalar_old] at hdeg ⊢
      exact .hyp hq hdeg
    · rcases ha with ⟨i, rfl⟩ | ⟨u, i, rfl⟩
      · rw [hcomp]; exact .zero
      · have hz : freshENSScalar (σ := σ) c
            (X (Sum.inr (u, i)) ^ 2 - X (Sum.inr (u, i))) = 0 := by
          simp only [freshENSScalar, map_sub, map_pow, aeval_X, freshENSScalarVars]
          rw [← map_pow, hc, sub_self]
        rw [hz]; exact .zero)
  simpa [freshENSScalar] using hh

theorem freshENS_zero_cleanup (g : ι → MvPolynomial σ K) (h : ℕ)
    (hg : ∀ i, g i = 0) (F : Set (MvPolynomial σ K))
    {D : ℕ} {p : MvPolynomial (FreshENSVars σ ι h) K}
    (hp : Derives ((rename Sum.inl) '' F ∪ freshENSBlockAxioms g h) D p) :
    Derives F D (freshENSScalar (fun _ => 0) p) := by
  apply freshENS_scalar_cleanup g h F (fun _ => 0) (by simp)
  · intro i
    simp [freshENSCompanion, hg]
  · exact hp

def freshENSUnitScalars {h : ℕ} (c : ι → K) : Fin h × ι → K :=
  fun v => if v.1.val = 0 then c v.2 else 0

private theorem unitScalar_product (g : ι → MvPolynomial σ K) (h : ℕ)
    (hh : 0 < h) (c : ι → K) (hc : ∑ i, c i • g i = 1) :
    freshENSScalar (freshENSUnitScalars c) (freshENSProduct g h) = 0 := by
  classical
  rw [freshENSProduct, map_prod]
  apply Finset.prod_eq_zero (Finset.mem_univ (⟨0, hh⟩ : Fin h))
  simp only [freshENSFactor, map_sub, map_one, map_sum, map_mul, freshENSScalar_old]
  simp only [freshENSScalar, aeval_X, freshENSScalarVars]
  simpa [freshENSUnitScalars, ← MvPolynomial.smul_eq_C_mul] using sub_eq_zero.mpr hc.symm

theorem freshENS_unit_cleanup (g : ι → MvPolynomial σ (ZMod 2)) (h : ℕ)
    (hh : 0 < h) (c : ι → ZMod 2) (hc : ∑ i, c i • g i = 1)
    (F : Set (MvPolynomial σ (ZMod 2)))
    {D : ℕ} {p : MvPolynomial (FreshENSVars σ ι h) (ZMod 2)}
    (hp : Derives ((rename Sum.inl) '' F ∪ freshENSBlockAxioms g h) D p) :
    Derives F D (freshENSScalar (freshENSUnitScalars c) p) := by
  apply freshENS_scalar_cleanup g h F (freshENSUnitScalars c)
  · intro v
    exact ZMod.pow_card _
  · intro i
    rw [freshENSCompanion, map_mul, unitScalar_product g h hh c hc, mul_zero]
  · exact hp

theorem freshENS_unitSpan_cleanup (g : ι → MvPolynomial σ (ZMod 2)) (h : ℕ)
    (hh : 0 < h) (hunit : (1 : MvPolynomial σ (ZMod 2)) ∈ Submodule.span (ZMod 2) (Set.range g))
    (F : Set (MvPolynomial σ (ZMod 2)))
    {D : ℕ} {p : MvPolynomial (FreshENSVars σ ι h) (ZMod 2)}
    (hp : Derives ((rename Sum.inl) '' F ∪ freshENSBlockAxioms g h) D p) :
    ∃ c : ι → ZMod 2, Derives F D (freshENSScalar (freshENSUnitScalars c) p) := by
  obtain ⟨c, hc⟩ := (Submodule.mem_span_range_iff_exists_fun (ZMod 2)).mp hunit
  exact ⟨c, freshENS_unit_cleanup g h hh c hc F hp⟩

end
end MathResearch
