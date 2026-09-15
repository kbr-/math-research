/-
Claim: lem:finite-affine-DAG-registry
Source: https://kbr.is-a.dev/math-research/#lean-finite-affine-DAG-registry
Scope: A finite topologically indexed DAG with semantic weakening, complementary resolution, or binary semantic rules admits one compressed fixed registry with at most three slots per source node plus supplied initial clauses, bounded literal inventory, and height-independent primitive PC replay from actual initial-value proofs.
Declarations: MathResearch.PolynomialCalculus.registry_inventory_bound MathResearch.PolynomialCalculus.affine_dag_registry MathResearch.PolynomialCalculus.registry_variable_count
-/
import claims.AffineClauseResolution
import claims.AffineClauseWeakening
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.Data.Fintype.Prod

namespace MathResearch.PolynomialCalculus
noncomputable section
open scoped BigOperators
local instance dagClauseDecidableEq {σ : Type} : DecidableEq ((σ → ZMod 2) →ᵃ[ZMod 2] ZMod 2) := Classical.decEq _
variable {σ J : Type} [Fintype σ] [Fintype J] {S : ℕ}

/-- A source DAG node references only earlier nodes; references may be reused.
Both usual resolution/weakening and the stronger binary semantic convention
are explicit constructors. -/
inductive AffineDAGStep (I : Set (FiniteParityClause σ)) (C : Fin S → FiniteParityClause σ)
    (i : Fin S) : Type
  | initial : C i ∈ I → AffineDAGStep I C i
  | weaken (a : Fin S) : a < i → MathResearch.clauseEntails (C a) (C i) → AffineDAGStep I C i
  | resolve (a b : Fin S) (A B : FiniteParityClause σ) (u : (σ → ZMod 2) →ᵃ[ZMod 2] ZMod 2) :
      a < i → b < i → C a = insert u A → C b = insert (MathResearch.oppositeParity u) B →
      C i = A ∪ B → AffineDAGStep I C i
  | binary (a b : Fin S) : a < i → b < i →
      (∀ x, MathResearch.clauseHolds (C a) x → MathResearch.clauseHolds (C b) x →
        MathResearch.clauseHolds (C i) x) → AffineDAGStep I C i

structure AffineDAG (I : Set (FiniteParityClause σ)) (C : Fin S → FiniteParityClause σ) where
  step : ∀ i, AffineDAGStep I C i

omit [Fintype σ] in
private theorem resolution_semantic (A B : FiniteParityClause σ)
    (u : (σ → ZMod 2) →ᵃ[ZMod 2] ZMod 2) :
    ∀ x, MathResearch.clauseHolds (insert u A) x →
      MathResearch.clauseHolds (insert (MathResearch.oppositeParity u) B) x →
      MathResearch.clauseHolds (A ∪ B) x := by
  intro x ha hb
  rcases (MathResearch.clause_holds_insert A u x).mp ha with hu | ha
  · rcases (MathResearch.clause_holds_insert B (MathResearch.oppositeParity u) x).mp hb with hv | hb
    · simp [MathResearch.oppositeParity_apply, hu] at hv
    · obtain ⟨g,hg,hgx⟩ := hb
      exact ⟨g,Finset.mem_union_right A hg,hgx⟩
  · obtain ⟨g,hg,hgx⟩ := ha
    exact ⟨g,Finset.mem_union_left B hg,hgx⟩

private inductive DAGPlan (A : J → FiniteParityClause σ) (Q : Fin S → FiniteParityClause σ)
    (i : Fin S) : Type
  | initial (j : J) : MathResearch.clauseEntails (A j) (Q i) → DAGPlan A Q i
  | weaken (a : Fin S) : a < i → MathResearch.clauseEntails (Q a) (Q i) → DAGPlan A Q i
  | resolve (a b : Fin S) (u : (σ → ZMod 2) →ᵃ[ZMod 2] ZMod 2) :
      a < i → b < i → MathResearch.clauseEntails (Q a) (insert u (Q i)) →
      MathResearch.clauseEntails (Q b) (insert (MathResearch.oppositeParity u) (Q i)) → DAGPlan A Q i

omit [Fintype σ] [Fintype J] in
private theorem binary_plan_exists (A : J → FiniteParityClause σ) (Q : Fin S → FiniteParityClause σ)
    (i a b : Fin S) (ha : a < i) (hb : b < i)
    (hs : ∀ x, MathResearch.clauseHolds (Q a) x → MathResearch.clauseHolds (Q b) x →
      MathResearch.clauseHolds (Q i) x) : Nonempty (DAGPlan A Q i) := by
  rcases MathResearch.binary_semantic_affine_cover (Q a) (Q b) (Q i) hs with hA | hB | ⟨u,_,hA,hB⟩
  · exact ⟨.weaken a ha hA⟩
  · exact ⟨.weaken b hb hB⟩
  · exact ⟨.resolve a b u ha hb hA hB⟩

private def normalizeStep (I : Set (FiniteParityClause σ)) (C Q : Fin S → FiniteParityClause σ)
    (A : J → FiniteParityClause σ)
    (hQ : ∀ i x, MathResearch.clauseHolds (Q i) x ↔ MathResearch.clauseHolds (C i) x)
    (cover : ∀ D ∈ I, ∃ j, MathResearch.clauseEntails (A j) D)
    (i : Fin S) (step : AffineDAGStep I C i) : DAGPlan A Q i := by
  cases step with
  | initial hi =>
    let j := Classical.choose (cover (C i) hi)
    have hj := Classical.choose_spec (cover (C i) hi)
    exact .initial j (fun x hx => (hQ i x).mpr (hj x hx))
  | weaken a ha hent =>
    exact .weaken a ha (fun x hx => (hQ i x).mpr (hent x ((hQ a x).mp hx)))
  | binary a b ha hb hs =>
    exact Classical.choice (binary_plan_exists A Q i a b ha hb
      (fun x hx hy => (hQ i x).mpr (hs x ((hQ a x).mp hx) ((hQ b x).mp hy))))
  | resolve a b AA BB u ha hb heA heB heT =>
    have hs : ∀ x, MathResearch.clauseHolds (C a) x → MathResearch.clauseHolds (C b) x →
        MathResearch.clauseHolds (C i) x := by
      rw [heA,heB,heT]
      exact resolution_semantic AA BB u
    exact Classical.choice (binary_plan_exists A Q i a b ha hb
      (fun x hx hy => (hQ i x).mpr (hs x ((hQ a x).mp hx) ((hQ b x).mp hy))))

private def planLeft {A : J → FiniteParityClause σ} {Q : Fin S → FiniteParityClause σ}
    {i : Fin S} (p : DAGPlan A Q i) : FiniteParityClause σ :=
  match p with
  | .resolve _ _ u _ _ _ _ => insert u (Q i)
  | _ => Q i

private def planRight {A : J → FiniteParityClause σ} {Q : Fin S → FiniteParityClause σ}
    {i : Fin S} (p : DAGPlan A Q i) : FiniteParityClause σ :=
  match p with
  | .resolve _ _ u _ _ _ _ => insert (MathResearch.oppositeParity u) (Q i)
  | _ => Q i

omit [Fintype σ] [Fintype J] in
private theorem plan_width {A : J → FiniteParityClause σ} {Q : Fin S → FiniteParityClause σ}
    {i : Fin S} (p : DAGPlan A Q i) {d : ℕ} (hq : (Q i).card ≤ d+1) :
    (planLeft p).card ≤ d+2 ∧ (planRight p).card ≤ d+2 := by
  cases p with
  | initial j hj => exact ⟨hq.trans (by omega),hq.trans (by omega)⟩
  | weaken a ha hent => exact ⟨hq.trans (by omega),hq.trans (by omega)⟩
  | resolve a b u ha hb hA hB =>
    exact ⟨(Finset.card_insert_le _ _).trans (by omega), (Finset.card_insert_le _ _).trans (by omega)⟩

private def dagRawRegistry (A : J → FiniteParityClause σ) (Q : Fin S → FiniteParityClause σ)
    (p : ∀ i, DAGPlan A Q i) : J ⊕ (Fin S × Fin 3) → FiniteParityClause σ
  | Sum.inl j => A j
  | Sum.inr (i,k) => if k=0 then Q i else if k=1 then planLeft (p i) else planRight (p i)

private def dagRegistry (A : J → FiniteParityClause σ) (Q : Fin S → FiniteParityClause σ)
    (p : ∀ i, DAGPlan A Q i) : Fin (Fintype.card (J ⊕ (Fin S × Fin 3))) → FiniteParityClause σ :=
  fun c => dagRawRegistry A Q p ((Fintype.equivFin (J ⊕ (Fin S × Fin 3))).symm c)

private def dagInitialIndex (j : J) : Fin (Fintype.card (J ⊕ (Fin S × Fin 3))) :=
  Fintype.equivFin _ (Sum.inl j)
private def dagNodeIndex (i : Fin S) (k : Fin 3) : Fin (Fintype.card (J ⊕ (Fin S × Fin 3))) :=
  Fintype.equivFin _ (Sum.inr (i,k))

omit [Fintype σ] in
@[simp] private theorem dag_initial_eq (A : J → FiniteParityClause σ) (Q : Fin S → FiniteParityClause σ)
    (p : ∀ i, DAGPlan A Q i) (j : J) : dagRegistry A Q p (dagInitialIndex j) = A j := by
  simp [dagRegistry,dagInitialIndex,dagRawRegistry]
omit [Fintype σ] in
@[simp] private theorem dag_node_eq (A : J → FiniteParityClause σ) (Q : Fin S → FiniteParityClause σ)
    (p : ∀ i, DAGPlan A Q i) (i : Fin S) : dagRegistry A Q p (dagNodeIndex i 0) = Q i := by
  simp [dagRegistry,dagNodeIndex,dagRawRegistry]
omit [Fintype σ] in
@[simp] private theorem dag_left_eq (A : J → FiniteParityClause σ) (Q : Fin S → FiniteParityClause σ)
    (p : ∀ i, DAGPlan A Q i) (i : Fin S) : dagRegistry A Q p (dagNodeIndex i 1) = planLeft (p i) := by
  simp [dagRegistry,dagNodeIndex,dagRawRegistry]
omit [Fintype σ] in
@[simp] private theorem dag_right_eq (A : J → FiniteParityClause σ) (Q : Fin S → FiniteParityClause σ)
    (p : ∀ i, DAGPlan A Q i) (i : Fin S) : dagRegistry A Q p (dagNodeIndex i 2) = planRight (p i) := by
  simp [dagRegistry,dagNodeIndex,dagRawRegistry]

private theorem dag_replay (A : J → FiniteParityClause σ) (Q : Fin S → FiniteParityClause σ)
    (p : ∀ i, DAGPlan A Q i) (h : ℕ) (old : Set (Poly (ZMod 2) σ)) (D : ℕ)
    (hh : 1 ≤ h) (hD : 4*h+1 ≤ D)
    (hinit : ∀ j, Derives (registrySystem (dagRegistry A Q p) h old) D
      (registryValue (dagRegistry A Q p) h (dagInitialIndex j))) :
    ∀ i, Derives (registrySystem (dagRegistry A Q p) h old) D
      (registryValue (dagRegistry A Q p) h (dagNodeIndex i 0)) := by
  classical
  let R := dagRegistry A Q p
  have all : ∀ n : ℕ, ∀ i : Fin S, i.val = n →
      Derives (registrySystem R h old) D (registryValue R h (dagNodeIndex i 0)) := by
    intro n
    induction n using Nat.strong_induction_on with
    | h n ih =>
      intro i hi
      cases hp : p i with
      | initial j hent =>
        have he : MathResearch.clauseEntails (R (dagInitialIndex j)) (R (dagNodeIndex i 0)) := by
          simpa [R] using hent
        exact (registry_semantic_weakening R h old hh _ _ he (hinit j)).mono
          (fun _ h => h) (by omega)
      | weaken a ha hent =>
        have hpa := ih a.val (by change a.val < i.val at ha; omega) a rfl
        have he : MathResearch.clauseEntails (R (dagNodeIndex a 0)) (R (dagNodeIndex i 0)) := by
          simpa [R] using hent
        exact (registry_semantic_weakening R h old hh _ _ he hpa).mono
          (fun _ h => h) (by omega)
      | resolve a b u ha hb hentA hentB =>
        have hpa := ih a.val (by change a.val < i.val at ha; omega) a rfl
        have hpb := ih b.val (by change b.val < i.val at hb; omega) b rfl
        have heA : MathResearch.clauseEntails (R (dagNodeIndex a 0)) (R (dagNodeIndex i 1)) := by
          simpa [R,hp,planLeft] using hentA
        have heB : MathResearch.clauseEntails (R (dagNodeIndex b 0)) (R (dagNodeIndex i 2)) := by
          simpa [R,hp,planRight] using hentB
        have hauxA := (registry_semantic_weakening R h old hh _ _ heA hpa).mono
          (fun _ h => h) (show max D (4*h) ≤ D by omega)
        have hauxB := (registry_semantic_weakening R h old hh _ _ heB hpb).mono
          (fun _ h => h) (show max D (4*h) ≤ D by omega)
        have hr := registry_resolution R h old hh (dagNodeIndex i 1) (dagNodeIndex i 2)
          (dagNodeIndex i 0) (Q i) (Q i) u
          (by simp [R,hp,planLeft]) (by simp [R,hp,planRight]) (by simp [R]) hauxA hauxB
        exact hr.mono (fun _ h => h) (by omega)
  exact fun i => all i.val i rfl

theorem affine_dag_registry (I : Set (FiniteParityClause σ)) (C : Fin S → FiniteParityClause σ)
    (dag : AffineDAG I C) (A : J → FiniteParityClause σ) (w : ℕ)
    (hwidth : ∀ j, (A j).card ≤ w)
    (cover : ∀ D ∈ I, ∃ j, MathResearch.clauseEntails (A j) D) :
    ∃ (N : ℕ) (R : Fin N → FiniteParityClause σ) (initial : J → Fin N) (node : Fin S → Fin N),
      N = 3*S + Fintype.card J ∧
      (∀ j, R (initial j) = A j) ∧
      (∀ i, R (node i) ⊆ C i ∧ ∀ x, MathResearch.clauseHolds (R (node i)) x ↔ MathResearch.clauseHolds (C i) x) ∧
      (∀ c, (R c).card ≤ max w (Fintype.card σ+2)) ∧
      ∀ (h : ℕ) (old : Set (Poly (ZMod 2) σ)) (D : ℕ), 1 ≤ h → 4*h+1 ≤ D →
        (∀ j, Derives (registrySystem R h old) D (registryValue R h (initial j))) →
        ∀ i, Derives (registrySystem R h old) D (registryValue R h (node i)) := by
  classical
  choose Q hsub hcard hequiv using fun i => MathResearch.affine_clause_basis_compression (C i)
  have hQcard (i : Fin S) : (Q i).card ≤ Fintype.card σ+1 := by
    simpa only [Module.finrank_fintype_fun_eq_card] using hcard i
  let p (i : Fin S) := normalizeStep I C Q A hequiv cover i (dag.step i)
  let R := dagRegistry A Q p
  refine ⟨Fintype.card (J ⊕ (Fin S × Fin 3)),R,dagInitialIndex,(fun i => dagNodeIndex i 0),?_,?_,?_,?_,?_⟩
  · simp [Fintype.card_sum,Fintype.card_prod,Nat.mul_comm,Nat.add_comm]
  · exact dag_initial_eq A Q p
  · intro i
    simpa [R] using And.intro (hsub i) (hequiv i)
  · intro c
    change (dagRawRegistry A Q p ((Fintype.equivFin (J ⊕ (Fin S × Fin 3))).symm c)).card ≤ _
    cases hx : (Fintype.equivFin (J ⊕ (Fin S × Fin 3))).symm c with
    | inl j => exact (hwidth j).trans (le_max_left _ _)
    | inr z =>
      rcases z with ⟨i,k⟩
      have hpw := plan_width (p i) (hQcard i)
      have hq := hQcard i
      simp only [dagRawRegistry]
      split_ifs <;> omega
  · intro h old D hh hD hinit
    exact dag_replay A Q p h old D hh hD hinit

theorem registry_variable_count {N : ℕ} (R : Fin N → FiniteParityClause σ) (h : ℕ) :
    Fintype.card (ClauseRegistryVars R h) = Fintype.card σ + h * ∑ c, (R c).card := by
  simp [ClauseRegistryVars,Fintype.card_sigma,Finset.mul_sum]

theorem registry_inventory_bound {N : ℕ} (R : Fin N → FiniteParityClause σ) (h W : ℕ)
    (hW : ∀ c, (R c).card ≤ W) :
    (∑ c, (R c).card) ≤ N*W ∧
      Fintype.card (ClauseRegistryVars R h) ≤ Fintype.card σ + h*N*W := by
  have hsum : (∑ c, (R c).card) ≤ N*W := by
    calc
      _ ≤ ∑ _c : Fin N, W := Finset.sum_le_sum (fun c _ => hW c)
      _ = _ := by simp
  refine ⟨hsum, ?_⟩
  rw [registry_variable_count]
  simpa only [Nat.mul_assoc] using Nat.add_le_add_left (Nat.mul_le_mul_left h hsum) (Fintype.card σ)

end
end MathResearch.PolynomialCalculus
