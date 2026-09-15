/-
Claim: def:affine-clause-PC-system
Source: https://kbr.is-a.dev/math-research/#lean-affine-clause-PC-system
Scope: One fixed finite registry of old-affine binary clauses, disjoint fresh accuracy-h coefficient blocks, complete companion and Boolean domains, empty-clause value one without coefficient variables, and full prefix/value/companion upper bounds for h≥1. Clause values are not added as axioms.
Declarations: MathResearch.PolynomialCalculus.registry_fresh_value MathResearch.PolynomialCalculus.registry_coefficient_scope MathResearch.PolynomialCalculus.registry_input_degree MathResearch.PolynomialCalculus.registry_prefix_identity MathResearch.PolynomialCalculus.registry_value_degree MathResearch.PolynomialCalculus.registry_prefix_degree MathResearch.PolynomialCalculus.registry_companion_degree MathResearch.PolynomialCalculus.registry_empty_value MathResearch.PolynomialCalculus.registry_clause_data
-/
import claims.MpTelescoping
import claims.FiniteAffinePolynomial
import claims.FreshENSBlock
import claims.BinarySemanticAffineCover
import claims.PolynomialCalculusSubstitution

namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial
open scoped BigOperators

/-- Sufficient concrete certificate data for primitive clause-rule simulation.
The registry below constructs these fields from actual ENS products. -/
structure PCClause {σ : Type} (F : Set (Poly (ZMod 2) σ)) (h : ℕ)
    (ι : Type) [Fintype ι] where
  input : ι → Poly (ZMod 2) σ
  value : Poly (ZMod 2) σ
  cofactor : ι → Poly (ZMod 2) σ
  input_degree : ∀ i, (input i).totalDegree ≤ 1
  value_degree : value.totalDegree ≤ 2*h
  prefix_degree : ∀ i, (cofactor i).totalDegree ≤ 2*h-1
  identity : 1-value = ∑ i, cofactor i * input i
  companion : ∀ i, Derives F (2*h+1) (input i * value)

abbrev FiniteParityClause (σ : Type) := MathResearch.ParityClause (σ → ZMod 2)
abbrev ClauseRegistryVars {σ : Type} {N : ℕ} (C : Fin N → FiniteParityClause σ) (h : ℕ) :=
  σ ⊕ (Σ c : Fin N, Fin h × (C c))

variable {σ : Type} [Fintype σ] {N : ℕ} (C : Fin N → FiniteParityClause σ) (h : ℕ)

def registryOld : Poly (ZMod 2) σ →ₐ[ZMod 2] Poly (ZMod 2) (ClauseRegistryVars C h) :=
  aeval (fun i => X (Sum.inl i))

def registryInput (c : Fin N) (g : C c) : Poly (ZMod 2) (ClauseRegistryVars C h) :=
  registryOld C h (MathResearch.finiteAffinePolynomial g.val)

def registryCoefficient (c : Fin N) (u : ℕ) (g : C c) : Poly (ZMod 2) (ClauseRegistryVars C h) :=
  if hu : u < h then X (Sum.inr ⟨c,(⟨u,hu⟩,g)⟩) else 0

def registryValue (c : Fin N) : Poly (ZMod 2) (ClauseRegistryVars C h) :=
  MathResearch.ensProduct (registryInput C h c) (registryCoefficient C h c) h

def registryPrefix (c : Fin N) (g : C c) : Poly (ZMod 2) (ClauseRegistryVars C h) :=
  MathResearch.ensCoefficient (registryInput C h c) (registryCoefficient C h c) h g

def registrySystem (old : Set (Poly (ZMod 2) σ)) : Set (Poly (ZMod 2) (ClauseRegistryVars C h)) :=
  registryOld C h '' old ∪ booleanBase ∪
    {p | ∃ c : Fin N, ∃ g : C c, p = registryInput C h c g * registryValue C h c}

theorem registry_input_degree (c : Fin N) (g : C c) :
    (registryInput C h c g).totalDegree ≤ 1 := by
  have hd := substitution_degree (fun i : σ => (X (Sum.inl i) :
    Poly (ZMod 2) (ClauseRegistryVars C h))) 1 (by intro i; simp)
    (MathResearch.finiteAffinePolynomial g.val)
  apply (show (registryInput C h c g).totalDegree ≤
      (MathResearch.finiteAffinePolynomial g.val).totalDegree from
    by simpa only [Nat.one_mul, registryInput, registryOld] using hd).trans
  exact MathResearch.finiteAffinePolynomial_degree _

omit [Fintype σ] in
private theorem registry_coefficient_degree (c : Fin N) (u : ℕ) (g : C c) :
    (registryCoefficient C h c u g).totalDegree ≤ 1 := by
  unfold registryCoefficient
  split_ifs <;> simp

theorem registry_prefix_identity (c : Fin N) :
    1 - registryValue C h c = ∑ g : C c, registryPrefix C h c g * registryInput C h c g :=
  MathResearch.mp_telescoping _ _ _

theorem registry_value_degree (c : Fin N) : (registryValue C h c).totalDegree ≤ 2*h := by
  simpa only [Nat.mul_comm, Nat.reduceAdd, registryValue] using MathResearch.ensProduct_degree
    (registryInput C h c) (registryCoefficient C h c) 1 h
    (registry_input_degree C h c) (fun u _ g => registry_coefficient_degree C h c u g)

theorem registry_prefix_degree (hh : 1 ≤ h) (c : Fin N) (g : C c) :
    (registryPrefix C h c g).totalDegree ≤ 2*h-1 := by
  have hd := MathResearch.mp_coefficient_degree (registryInput C h c) (registryCoefficient C h c)
    1 h g (registry_input_degree C h c) (fun u _ g => registry_coefficient_degree C h c u g)
  exact hd.trans (by omega)

theorem registry_companion_degree (c : Fin N) (g : C c) :
    (registryInput C h c g * registryValue C h c).totalDegree ≤ 2*h+1 :=
  (totalDegree_mul _ _).trans (by
    have hi := registry_input_degree C h c g
    have hv := registry_value_degree C h c
    omega)

theorem registry_empty_value (c : Fin N) (hc : C c = ∅) : registryValue C h c = 1 := by
  have : IsEmpty (C c) := ⟨fun g => by simpa [hc] using g.property⟩
  simp [registryValue, MathResearch.ensProduct]

def registryClauseData (old : Set (Poly (ZMod 2) σ)) (hh : 1 ≤ h) (c : Fin N) :
    PCClause (registrySystem C h old) h (C c) where
  input := registryInput C h c
  value := registryValue C h c
  cofactor := registryPrefix C h c
  input_degree := registry_input_degree C h c
  value_degree := registry_value_degree C h c
  prefix_degree := registry_prefix_degree C h hh c
  identity := registry_prefix_identity C h c
  companion := fun g => Derives.hyp (Or.inr ⟨c,g,rfl⟩) (registry_companion_degree C h c g)

theorem registry_clause_data (old : Set (Poly (ZMod 2) σ)) (hh : 1 ≤ h) (c : Fin N) :
    (registryClauseData C h old hh c).value = registryValue C h c ∧
    (registryClauseData C h old hh c).input = registryInput C h c ∧
    (registryClauseData C h old hh c).cofactor = registryPrefix C h c := ⟨rfl,rfl,rfl⟩

def registryFreshEmbedding (c : Fin N) :
    MathResearch.FreshENSVars σ (C c) h ↪ ClauseRegistryVars C h where
  toFun := fun z => match z with
    | Sum.inl x => Sum.inl x
    | Sum.inr r => Sum.inr ⟨c,r⟩
  inj' := by
    intro a b hab
    cases a <;> cases b <;> simp_all

set_option maxHeartbeats 800000 in
theorem registry_fresh_value (c : Fin N) :
    registryValue C h c = rename (registryFreshEmbedding C h c)
      (MathResearch.freshENSProduct (fun g : C c => MathResearch.finiteAffinePolynomial g.val) h) := by
  rw [MathResearch.freshENSProduct_rename]
  unfold registryValue MathResearch.ensProduct
  rw [← Fin.prod_univ_eq_prod_range]
  apply Finset.prod_congr rfl
  intro u _
  congr 1
  apply Finset.sum_congr rfl
  intro g _
  simp [registryCoefficient, registryFreshEmbedding, registryInput, registryOld,
    Function.comp_def, rename_eq_aeval]
  rfl

omit [Fintype σ] in
theorem registry_coefficient_scope {c d : Fin N} (hcd : c ≠ d)
    (u : Fin h) (g : C c) (w : Fin h) (k : C d) :
    (Sum.inr ⟨c,(u,g)⟩ : ClauseRegistryVars C h) ≠ Sum.inr ⟨d,(w,k)⟩ := by
  intro he
  have hs := Sum.inr.inj he
  exact hcd (congrArg Sigma.fst hs)

end
end MathResearch.PolynomialCalculus
