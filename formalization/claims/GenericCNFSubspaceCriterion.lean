/-
Claim: thm:generic-CNF-affine-DAG-subspace-criterion
Source: https://kbr.is-a.dev/math-research/#lean-generic-CNF-affine-DAG-subspace-criterion
Scope: Also covers lem:generic-CNF-initial-value-bridge. Binary field, arbitrary finite variable type. The ordinary clause polynomial and its evaluation characterization; derivability through 2h+w of the registry value of any slot holding a clause of width at most w whose clause polynomial is an old axiom; the composed transfer of a finite affine refutation DAG (semantic weakening, complementary resolution, binary semantic rules) whose initial clauses are semantically covered by |J| such clauses, giving exactly 3S+|J| registry slots and an ordinary PC refutation through max(2h+w,4h+1); and the proof-size criterion dim U ≤ (3S+|J|)·C(v-(h(k+1)+1)+k,k) for a degree-k subspace U with no nonzero member derivable from the old base through k(max(2h+w,4h+1)+1). A sufficient condition only: no formula other than bit PHP is shown to admit such a subspace, and the short-proof control remark of the source entry is not covered.
Declarations: MathResearch.PolynomialCalculus.clauseFalsityPolynomial MathResearch.PolynomialCalculus.clauseFalsityPolynomial_eval_eq_zero_iff MathResearch.PolynomialCalculus.registry_generic_initial MathResearch.PolynomialCalculus.generic_CNF_PC_transfer MathResearch.PolynomialCalculus.generic_CNF_subspace_criterion
-/
import claims.AffineDAGRegistry
import claims.AffineLiteralProduct
import claims.BitPHPClauseTransfer
import claims.GenericAffineSubspaceConsequence

namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial
open scoped BigOperators
local instance genericCNFClauseDecidableEq {σ : Type} :
    DecidableEq ((σ → ZMod 2) →ᵃ[ZMod 2] ZMod 2) := Classical.decEq _

/-- The ordinary polynomial of an affine clause: the product of `1 - g` over its literals.
It is the indicator that every literal is zero, so the clause axiom is this polynomial. -/
def clauseFalsityPolynomial {σ : Type} [Fintype σ] (A : FiniteParityClause σ) :
    Poly (ZMod 2) σ :=
  ∏ g ∈ A, (1 - MathResearch.finiteAffinePolynomial g)

/-- The clause polynomial vanishes exactly at the assignments satisfying the clause. -/
theorem clauseFalsityPolynomial_eval_eq_zero_iff {σ : Type} [Fintype σ]
    (A : FiniteParityClause σ) (x : σ → ZMod 2) :
    MvPolynomial.eval x (clauseFalsityPolynomial A) = 0 ↔ MathResearch.clauseHolds A x := by
  classical
  have hval : ∀ g ∈ A, MvPolynomial.eval x (1 - MathResearch.finiteAffinePolynomial g)
      = 1 - g x := by
    intro g _
    rw [map_sub, map_one, MathResearch.finiteAffinePolynomial_eval]
  simp only [clauseFalsityPolynomial, map_prod]
  rw [Finset.prod_congr rfl hval, Finset.prod_eq_zero_iff]
  constructor
  · rintro ⟨g, hg, hgz⟩
    exact ⟨g, hg, (sub_eq_zero.mp hgz).symm⟩
  · rintro ⟨g, hg, hgx⟩
    exact ⟨g, hg, by rw [hgx, sub_self]⟩

/-- Initial-value bridge: a registry slot holding a clause of width at most `w` whose
ordinary clause polynomial is an old axiom has its value derivable through `2h+w`. -/
theorem registry_generic_initial {σ : Type} [Fintype σ] {N : ℕ}
    (C : Fin N → FiniteParityClause σ) (h w : ℕ) (old : Set (Poly (ZMod 2) σ)) (c : Fin N)
    (hw : (C c).card ≤ w) (hold : clauseFalsityPolynomial (C c) ∈ old) :
    Derives (registrySystem C h old) (2*h+w) (registryValue C h c) := by
  classical
  let e : Fin (C c).card ≃ (C c) := (C c).equivFin.symm
  let g : Fin (C c).card → Poly (ZMod 2) (ClauseRegistryVars C h) :=
    fun t => registryInput C h c (e t)
  have hg (t : Fin (C c).card) : (g t).totalDegree ≤ 1 := registry_input_degree C h c (e t)
  obtain ⟨U,hU,hUd⟩ := affine_literal_product_prefix (C c).card g hg
  have hmap : registryOld C h (clauseFalsityPolynomial (C c))
      = ∏ f ∈ C c, (1 - registryOld C h (MathResearch.finiteAffinePolynomial f)) := by
    simp only [clauseFalsityPolynomial, map_prod]
    exact Finset.prod_congr rfl (fun f _ => by rw [map_sub, map_one])
  have hE : (∏ t : Fin (C c).card, (1 - g t))
      = registryOld C h (clauseFalsityPolynomial (C c)) := by
    rw [hmap, ← Finset.prod_coe_sort (C c)
        (fun f => 1 - registryOld C h (MathResearch.finiteAffinePolynomial f)),
      ← Equiv.prod_comp e
        (fun f : (C c) => 1 - registryOld C h (MathResearch.finiteAffinePolynomial f.val))]
    rfl
  have hEd : (∏ t : Fin (C c).card, (1 - g t)).totalDegree ≤ (C c).card := by
    apply (totalDegree_finsetProd _ _).trans
    calc
      _ ≤ ∑ _t : Fin (C c).card, 1 := Finset.sum_le_sum (fun t _ =>
        (totalDegree_sub _ _).trans (max_le (by simp) (hg t)))
      _ = (C c).card := by simp
  have hEw : (∏ t : Fin (C c).card, (1 - g t)).totalDegree ≤ w := hEd.trans hw
  have hEa : (∏ t : Fin (C c).card, (1 - g t)) ∈ registrySystem C h old := by
    rw [hE]
    exact Or.inl (Or.inl ⟨clauseFalsityPolynomial (C c), hold, rfl⟩)
  have hEP : Derives (registrySystem C h old) (2*h+w)
      ((∏ t : Fin (C c).card, (1 - g t))*registryValue C h c) := by
    have hp := registry_value_degree C h c
    have hmul := ((Derives.hyp hEa hEw).mul_polynomial (registryValue C h c)).mono
      (fun _ h => h) (show max w ((registryValue C h c).totalDegree+
        (∏ t : Fin (C c).card, (1-g t)).totalDegree) ≤ 2*h+w by omega)
    simpa only [mul_comm] using hmul
  have hsum : (∑ t : Fin (C c).card, U t*(g t*registryValue C h c)) ∈
      pcSpace (registrySystem C h old) (2*h+w) := by
    apply Submodule.sum_mem
    intro t _
    have ht := t.isLt
    have hcomp : Derives (registrySystem C h old) (2*h+1) (g t*registryValue C h c) :=
      Derives.hyp (Or.inr ⟨c,e t,rfl⟩) (registry_companion_degree C h c (e t))
    have hcd := hcomp.degree_le
    have hud := hUd t
    exact (hcomp.mul_polynomial (U t)).mono (fun _ h => h) (by omega)
  have heq : registryValue C h c =
      (∏ t : Fin (C c).card, (1 - g t))*registryValue C h c
        + ∑ t : Fin (C c).card, U t*(g t*registryValue C h c) := by
    have hx := congrArg (fun p => p*registryValue C h c) hU
    rw [sub_mul, one_mul, Finset.sum_mul] at hx
    simp only [mul_assoc] at hx
    linear_combination hx
  rw [heq]
  exact Derives.add hEP hsum

/-- Generic transfer: a refutation DAG from initial clauses covered by a finite family of
width-`w` clauses, whose clause polynomials are old axioms, gives one fixed registry with
`3S+|J|` slots and an ordinary PC refutation through `max (2h+w) (4h+1)`. -/
theorem generic_CNF_PC_transfer {σ J : Type} [Fintype σ] [Fintype J] {S : ℕ}
    (I : Set (FiniteParityClause σ)) (C : Fin S → FiniteParityClause σ)
    (dag : AffineDAG I C) (finish : Fin S) (hempty : C finish = ∅)
    (A : J → FiniteParityClause σ) (w : ℕ) (hwidth : ∀ j, (A j).card ≤ w)
    (cover : ∀ D ∈ I, ∃ j, MathResearch.clauseEntails (A j) D)
    (old : Set (Poly (ZMod 2) σ)) (hold : ∀ j, clauseFalsityPolynomial (A j) ∈ old)
    (h : ℕ) (hh : 1 ≤ h) :
    ∃ (N : ℕ) (R : Fin N → FiniteParityClause σ),
      N = 3*S + Fintype.card J ∧
      (∀ c, (R c).card ≤ max w (Fintype.card σ+2)) ∧
      Derives (registrySystem R h old) (max (2*h+w) (4*h+1)) 1 := by
  obtain ⟨N,R,initial,node,hN,hinit,hnode,hRwidth,replay⟩ :=
    affine_dag_registry I C dag A w hwidth cover
  refine ⟨N,R,hN,hRwidth,?_⟩
  have hi (j : J) : Derives (registrySystem R h old) (max (2*h+w) (4*h+1))
      (registryValue R h (initial j)) := by
    have hcard : (R (initial j)).card ≤ w := by rw [hinit j]; exact hwidth j
    have hoj : clauseFalsityPolynomial (R (initial j)) ∈ old := by rw [hinit j]; exact hold j
    exact (registry_generic_initial R h w old (initial j) hcard hoj).mono
      (fun _ h => h) (le_max_left _ _)
  have hp := replay h old (max (2*h+w) (4*h+1)) hh (le_max_right _ _) hi finish
  have hzero : R (node finish) = ∅ := by
    apply Finset.subset_empty.mp
    simpa only [hempty] using (hnode finish).1
  rwa [registry_empty_value R h (node finish) hzero] at hp

/-- Proof-size criterion: a separated degree-`k` subspace bounds the size of every
refutation DAG from below through the uniform restriction budget. -/
theorem generic_CNF_subspace_criterion {σ J : Type} [Fintype σ] [Fintype J] {S : ℕ}
    (I : Set (FiniteParityClause σ)) (C : Fin S → FiniteParityClause σ)
    (dag : AffineDAG I C) (finish : Fin S) (hempty : C finish = ∅)
    (A : J → FiniteParityClause σ) (w : ℕ) (hwidth : ∀ j, (A j).card ≤ w)
    (cover : ∀ D ∈ I, ∃ j, MathResearch.clauseEntails (A j) D)
    (old : Set (Poly (ZMod 2) σ)) (hF : booleanBase ⊆ old)
    (hold : ∀ j, clauseFalsityPolynomial (A j) ∈ old)
    (h k : ℕ) (hh : 1 ≤ h) (hk : 1 ≤ k)
    (U : Submodule (ZMod 2) (MvPolynomial σ (ZMod 2))) (hU : ∀ p ∈ U, p.totalDegree ≤ k)
    (hsep : ∀ f ∈ U, Derives old (k*(max (2*h+w) (4*h+1)+1)) f → f = 0) :
    Module.finrank (ZMod 2) U ≤
      (3*S + Fintype.card J) * (Fintype.card σ - (h*(k+1)+1) + k).choose k := by
  classical
  by_contra hcon
  rw [not_le] at hcon
  obtain ⟨N,R,hN,-,hpc⟩ :=
    generic_CNF_PC_transfer I C dag finish hempty A w hwidth cover old hold h hh
  rw [registry_system_eq_ensFamily] at hpc
  let gg : ∀ b : Fin N, {f // f ∈ R b} → MathResearch.AffineInputMap σ := fun _ i => i.val
  refine MathResearch.generic_affine_subspace_exclusion gg h k (max (2*h+w) (4*h+1))
    hh hk (by omega) old hF U hU hsep ?_ hpc
  have hsum := MathResearch.generic_proper_high_restriction_sum_le gg h k
  have hcard : Fintype.card (MathResearch.GenericProperHighIndex gg h k) ≤ N := by
    simpa only [Fintype.card_fin] using
      Fintype.card_le_of_injective
        (fun b : MathResearch.GenericProperHighIndex gg h k => b.val) Subtype.val_injective
  calc
    _ ≤ Fintype.card (MathResearch.GenericProperHighIndex gg h k) *
        (Fintype.card σ - (h*(k+1)+1) + k).choose k := hsum
    _ ≤ (3*S + Fintype.card J) * (Fintype.card σ - (h*(k+1)+1) + k).choose k :=
      Nat.mul_le_mul_right _ (hN ▸ hcard)
    _ < Module.finrank (ZMod 2) U := hcon

end
end MathResearch.PolynomialCalculus
