/-
Claim: lem:semantic-weakening-PC-degree
Source: https://kbr.is-a.dev/math-research/#lean-semantic-weakening-PC-degree
Scope: Semantic weakening in the actual fixed affine registry preserves max(K,4h); tautological conclusions are derived through2h+1. General constant-span certificate engines are instantiated using complete affine zero-flat/unit witnesses.
Declarations: MathResearch.PolynomialCalculus.PCClause.weaken_span MathResearch.PolynomialCalculus.PCClause.tautology_span MathResearch.PolynomialCalculus.registry_semantic_weakening MathResearch.PolynomialCalculus.registry_tautology
-/
import claims.AffineClauseRegistry
import claims.FiniteAffineSpan
import Mathlib.Tactic.LinearCombination

namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial
open scoped BigOperators
variable {σ ι τ : Type} [Fintype ι] [Fintype τ]
variable {F : Set (Poly (ZMod 2) σ)} {h K : ℕ}

private theorem input_times_value (A : PCClause F h ι) (T : PCClause F h τ)
    (c : ι → τ → ZMod 2) (he : ∀ i, A.input i = ∑ j, c i j • T.input j) (i : ι) :
    Derives F (2*h+1) (A.input i * T.value) := by
  rw [he, Finset.sum_mul]
  change (∑ j, (c i j • T.input j) * T.value) ∈ pcSpace F (2*h+1)
  apply Submodule.sum_mem
  intro j _
  simpa only [smul_mul_assoc, mem_pcSpace] using Derives.smul (c i j) (T.companion j)

theorem PCClause.weaken_span (A : PCClause F h ι) (T : PCClause F h τ) (hh : 1 ≤ h)
    (c : ι → τ → ZMod 2) (he : ∀ i, A.input i = ∑ j, c i j • T.input j)
    (hA : Derives F K A.value) : Derives F (max K (4*h)) T.value := by
  have hprod : Derives F (max K (4*h)) (A.value*T.value) := by
    have ha := A.value_degree
    have ht := T.value_degree
    have hx := (hA.mul_polynomial T.value).mono (fun _ h => h)
      (show max K (T.value.totalDegree+A.value.totalDegree) ≤ max K (4*h) by omega)
    simpa only [mul_comm] using hx
  have hsum : (∑ i, A.cofactor i * (A.input i*T.value)) ∈ pcSpace F (max K (4*h)) := by
    apply Submodule.sum_mem
    intro i _
    have hp := input_times_value A T c he i
    have hc := A.prefix_degree i
    have hd : (A.input i*T.value).totalDegree ≤ 2*h+1 := hp.degree_le
    exact (hp.mul_polynomial (A.cofactor i)).mono (fun _ h => h) (by omega)
  have heq : T.value = A.value*T.value + ∑ i, A.cofactor i*(A.input i*T.value) := by
    have hx := congrArg (fun p => p*T.value) A.identity
    rw [sub_mul, one_mul, Finset.sum_mul] at hx
    simp only [mul_assoc] at hx
    linear_combination hx
  rw [heq]
  exact Derives.add hprod hsum

theorem PCClause.tautology_span (T : PCClause F h τ)
    (c : τ → ZMod 2) (he : 1 = ∑ j, c j • T.input j) : Derives F (2*h+1) T.value := by
  have heq : T.value = ∑ j, c j • (T.input j*T.value) := by
    have hx := congrArg (fun p => p*T.value) he
    simpa only [one_mul, Finset.sum_mul, smul_mul_assoc] using hx
  rw [heq]
  change (∑ j, c j • (T.input j*T.value)) ∈ pcSpace F (2*h+1)
  exact Submodule.sum_mem _ (fun j _ => Derives.smul (c j) (T.companion j))

private theorem registry_input_span {ν : Type} [Fintype ν] {N : ℕ}
    (C : Fin N → FiniteParityClause ν) (h : ℕ) (a t : Fin N)
    (c : C a → C t → ZMod 2)
    (hc : ∀ i : C a, i.val = ∑ j : C t, c i j • j.val) :
    ∀ i : C a, registryInput C h a i = ∑ j : C t, c i j • registryInput C h t j := by
  intro i
  conv_lhs => unfold registryInput; rw [hc i]
  simp only [map_sum, map_smul, registryInput]

private theorem registry_unit_span {ν : Type} [Fintype ν] {N : ℕ}
    (C : Fin N → FiniteParityClause ν) (h : ℕ) (t : Fin N)
    (c : C t → ZMod 2)
    (hc : AffineMap.const (ZMod 2) (ν → ZMod 2) 1 = ∑ j : C t, c j • j.val) :
    (1 : Poly (ZMod 2) (ClauseRegistryVars C h)) =
      ∑ j : C t, c j • registryInput C h t j := by
  have h := congrArg (fun f => registryOld C h (MathResearch.finiteAffinePolynomial f)) hc
  have hconst : MathResearch.finiteAffinePolynomial (AffineMap.const (ZMod 2) (ν → ZMod 2) 1) = 1 := by
    simp [MathResearch.finiteAffinePolynomial]
  rw [hconst, map_one] at h
  simpa only [map_sum, map_smul, registryInput] using h

theorem registry_tautology {ν : Type} [Fintype ν] {N : ℕ}
    (C : Fin N → FiniteParityClause ν) (h : ℕ) (old : Set (Poly (ZMod 2) ν))
    (hh : 1 ≤ h) (t : Fin N)
    (ht : ¬ ∃ x : ν → ZMod 2, MathResearch.clauseZero (C t) x) :
    Derives (registrySystem C h old) (2*h+1) (registryValue C h t) := by
  obtain ⟨c,hc⟩ := MathResearch.finite_affine_unit_coefficients (fun j : C t => j.val) (by
    rintro ⟨x,hx⟩
    exact ht ⟨x, fun f hf => hx ⟨f,hf⟩⟩)
  exact PCClause.tautology_span (registryClauseData C h old hh t) c (registry_unit_span C h t c hc)

theorem registry_semantic_weakening {ν : Type} [Fintype ν] {N : ℕ}
    (C : Fin N → FiniteParityClause ν) (h : ℕ) (old : Set (Poly (ZMod 2) ν))
    (hh : 1 ≤ h) (a t : Fin N) (hent : MathResearch.clauseEntails (C a) (C t))
    {K : ℕ} (hA : Derives (registrySystem C h old) K (registryValue C h a)) :
    Derives (registrySystem C h old) (max K (4*h)) (registryValue C h t) := by
  classical
  by_cases ht : ∃ x : ν → ZMod 2, MathResearch.clauseZero (C t) x
  · obtain ⟨x,hx⟩ := ht
    have hc (i : C a) : ∃ c : C t → ZMod 2, i.val = ∑ j : C t, c j • j.val := by
      apply MathResearch.finite_affine_vanishing_coefficients (fun j : C t => j.val) x
        (fun j => hx j.val j.property) i.val
      intro y hy
      have htz : MathResearch.clauseZero (C t) y := fun f hf => hy ⟨f,hf⟩
      have haz : MathResearch.clauseZero (C a) y :=
        (MathResearch.clause_not_holds (C a) y).mp
          (fun ha => (MathResearch.clause_not_holds (C t) y).mpr htz (hent y ha))
      exact haz i.val i.property
    choose c hc using hc
    exact PCClause.weaken_span (registryClauseData C h old hh a) (registryClauseData C h old hh t)
      hh c (registry_input_span C h a t c hc) hA
  · exact (registry_tautology C h old hh t ht).mono (fun _ h => h) (by omega)

end
end MathResearch.PolynomialCalculus
