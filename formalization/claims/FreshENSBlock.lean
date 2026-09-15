/-
Claim: lem:fresh-ENS-block-degree
Source: https://kbr.is-a.dev/math-research/#lean-fresh-ENS-block-degree
Scope: Canonical disjoint fresh-variable ENS factors, products and companions with exact ordinary total degrees and injective-registry renaming compatibility.
Declarations: MathResearch.totalDegree_rename_injective MathResearch.freshENSFactor_degree MathResearch.freshENSProduct_degree MathResearch.freshENSCompanion_degree MathResearch.freshENSProduct_rename MathResearch.freshENSFactor_degree_le MathResearch.freshENSProduct_degree_le MathResearch.freshENSCompanion_degree_le
-/
import claims.PolynomialCalculusSubstitution

namespace MathResearch
noncomputable section
open MvPolynomial
open scoped BigOperators
variable {K σ ι : Type*} [Field K] [Fintype ι] {h : ℕ}

abbrev FreshENSVars (σ ι : Type*) (h : ℕ) := σ ⊕ (Fin h × ι)

def freshENSFactor (g : ι → MvPolynomial σ K) (u : Fin h) :
    MvPolynomial (FreshENSVars σ ι h) K :=
  1 - ∑ i, X (Sum.inr (u, i)) * rename Sum.inl (g i)

def freshENSProduct (g : ι → MvPolynomial σ K) (h : ℕ) :
    MvPolynomial (FreshENSVars σ ι h) K := ∏ u : Fin h, freshENSFactor g u

def freshENSCompanion (g : ι → MvPolynomial σ K) (h : ℕ) (i : ι) :
    MvPolynomial (FreshENSVars σ ι h) K := rename Sum.inl (g i) * freshENSProduct g h

private def renamePullback {α β : Type*} (e : α ↪ β) (b : β) : MvPolynomial α K := by
  classical
  exact if h : b ∈ Set.range e then X (Classical.choose h) else 0

private theorem renamePullback_image {α β : Type*} (e : α ↪ β) (a : α) :
    renamePullback (K := K) e (e a) = X a := by
  rw [renamePullback, dite_eq_left (Set.mem_range_self a)]
  congr 1
  exact e.injective (Classical.choose_spec (Set.mem_range_self a))

theorem totalDegree_rename_injective {α β : Type*} (e : α ↪ β) (p : MvPolynomial α K) :
    (rename e p).totalDegree = p.totalDegree := by
  apply le_antisymm (totalDegree_rename_le e p)
  have hr : aeval (renamePullback (K := K) e) (rename e p) = p := by
    rw [aeval_rename]
    have he : renamePullback (K := K) e ∘ e = X := funext (renamePullback_image e)
    rw [he]
    exact aeval_X_left_apply p

  have hg : ∀ b, (renamePullback (K := K) e b).totalDegree ≤ 1 := by
    intro b
    unfold renamePullback
    split <;> simp
  simpa only [Nat.one_mul, hr] using PolynomialCalculus.substitution_degree (renamePullback e) 1 hg (rename e p)

private theorem one_sub_degree {τ : Type*} (p : MvPolynomial τ K) (hp : 0 < p.totalDegree) :
    (1 - p).totalDegree = p.totalDegree := by
  rw [sub_eq_add_neg, totalDegree_add_eq_right_of_totalDegree_lt]
  · exact totalDegree_neg p
  · simpa using hp

private def selectENSCoefficient (u : Fin h) (j : ι) :
    FreshENSVars σ ι h → MvPolynomial (FreshENSVars σ ι h) K := by
  classical
  exact fun
    | Sum.inl x => X (Sum.inl x)
    | Sum.inr v => if v = (u, j) then X (Sum.inr v) else 0

omit [Fintype ι] in
private theorem selectENS_old (u : Fin h) (j : ι) (p : MvPolynomial σ K) :
    aeval (selectENSCoefficient u j) (rename Sum.inl p) = rename Sum.inl p := by
  rw [aeval_rename]
  apply AlgHom.congr_fun
  ext x
  simp [selectENSCoefficient, Function.comp_def]

private theorem selectENS_factor (g : ι → MvPolynomial σ K) (u : Fin h) (j : ι) :
    aeval (selectENSCoefficient u j) (freshENSFactor g u) =
      1 - X (Sum.inr (u, j)) * rename Sum.inl (g j) := by
  classical
  simp [freshENSFactor, selectENS_old, selectENSCoefficient, Prod.mk.injEq]

theorem freshENSFactor_degree_le (g : ι → MvPolynomial σ K)
    (hg : ∀ i, (g i).totalDegree ≤ 1) (u : Fin h) :
    (freshENSFactor g u).totalDegree ≤ 2 := by
  apply (totalDegree_sub _ _).trans
  apply max_le
  · simp
  · apply totalDegree_finsetSum_le
    intro i _
    exact (totalDegree_mul _ _).trans (by
      have hgi := (totalDegree_rename_le (Sum.inl : σ → FreshENSVars σ ι h) (g i)).trans (hg i)
      simpa using Nat.add_le_add_left hgi 1)

theorem freshENSFactor_degree (g : ι → MvPolynomial σ K)
    (hg : ∀ i, (g i).totalDegree ≤ 1) (j : ι) (hj : (g j).totalDegree = 1) (u : Fin h) :
    (freshENSFactor g u).totalDegree = 2 := by
  have hold : (rename Sum.inl (g j) : MvPolynomial (FreshENSVars σ ι h) K).totalDegree = 1 := by
    exact (totalDegree_rename_injective ⟨Sum.inl, Sum.inl_injective⟩ (g j)).trans hj
  have hn : (rename Sum.inl (g j) : MvPolynomial (FreshENSVars σ ι h) K) ≠ 0 := by
    intro hh
    simp [hh] at hold
  have hsel : (1 - X (Sum.inr (u, j)) * rename Sum.inl (g j) :
      MvPolynomial (FreshENSVars σ ι h) K).totalDegree = 2 := by
    have hd : (X (Sum.inr (u, j)) * rename Sum.inl (g j) :
      MvPolynomial (FreshENSVars σ ι h) K).totalDegree = 2 := by
      rw [totalDegree_mul_of_isDomain (X_ne_zero _) hn, totalDegree_X, hold]
    rw [one_sub_degree _ (by rw [hd]; decide), hd]
  apply le_antisymm
  · exact freshENSFactor_degree_le g hg u
  · rw [← hsel, ← selectENS_factor g u j]
    have hs : ∀ v, (selectENSCoefficient (σ := σ) (K := K) u j v).totalDegree ≤ 1 := by
      intro v
      cases v with
      | inl x => simp [selectENSCoefficient]
      | inr v =>
        classical
        by_cases hv : v = (u, j) <;> simp [selectENSCoefficient, hv]
    simpa using PolynomialCalculus.substitution_degree _ 1 hs (freshENSFactor g u)

private theorem prod_degree_eq_sum {τ α : Type*} (s : Finset α) (f : α → MvPolynomial τ K)
    (hf : ∀ i ∈ s, f i ≠ 0) :
    (∏ i ∈ s, f i).totalDegree = ∑ i ∈ s, (f i).totalDegree := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | @insert i s hi ih =>
    rw [Finset.prod_insert hi, Finset.sum_insert hi]
    rw [totalDegree_mul_of_isDomain (hf i (Finset.mem_insert_self _ _))
      (Finset.prod_ne_zero_iff.mpr (fun j hj => hf j (Finset.mem_insert_of_mem hj)))]
    rw [ih (fun j hj => hf j (Finset.mem_insert_of_mem hj))]

private theorem freshENSFactor_ne_zero (g : ι → MvPolynomial σ K)
    (hg : ∀ i, (g i).totalDegree ≤ 1) (j : ι) (hj : (g j).totalDegree = 1) (u : Fin h) :
    freshENSFactor g u ≠ 0 := by
  intro hz
  have hd := freshENSFactor_degree g hg j hj u
  simp [hz] at hd

theorem freshENSProduct_degree (g : ι → MvPolynomial σ K)
    (hg : ∀ i, (g i).totalDegree ≤ 1) (j : ι) (hj : (g j).totalDegree = 1) (h : ℕ) :
    (freshENSProduct g h).totalDegree = 2 * h := by
  rw [freshENSProduct, prod_degree_eq_sum _ _ (fun u _ => freshENSFactor_ne_zero g hg j hj u)]
  simp [freshENSFactor_degree g hg j hj, Nat.mul_comm]

theorem freshENSCompanion_degree (g : ι → MvPolynomial σ K)
    (hg : ∀ i, (g i).totalDegree ≤ 1) (j : ι) (hj : (g j).totalDegree = 1) (h : ℕ) :
    (freshENSCompanion g h j).totalDegree = 2 * h + 1 := by
  have hn : g j ≠ 0 := by intro hz; simp [hz] at hj
  have hp : freshENSProduct g h ≠ 0 :=
    Finset.prod_ne_zero_iff.mpr (fun u _ => freshENSFactor_ne_zero g hg j hj u)
  rw [freshENSCompanion, totalDegree_mul_of_isDomain
    ((rename_eq_zero_iff_of_injective _ Sum.inl_injective).not.mpr hn) hp]
  have hr : (rename Sum.inl (g j) : MvPolynomial (FreshENSVars σ ι h) K).totalDegree =
      (g j).totalDegree := totalDegree_rename_injective ⟨Sum.inl, Sum.inl_injective⟩ (g j)
  rw [hr, freshENSProduct_degree g hg j hj, hj, Nat.add_comm]

theorem freshENSProduct_rename {τ : Type*} (g : ι → MvPolynomial σ K) (h : ℕ)
    (ρ : FreshENSVars σ ι h → τ) :
    rename ρ (freshENSProduct g h) =
      ∏ u : Fin h, (1 - ∑ i, X (ρ (Sum.inr (u, i))) * rename (ρ ∘ Sum.inl) (g i)) := by
  simp [freshENSProduct, freshENSFactor, rename_rename]

theorem freshENSProduct_degree_le (g : ι → MvPolynomial σ K)
    (hg : ∀ i, (g i).totalDegree ≤ 1) (h : ℕ) :
    (freshENSProduct g h).totalDegree ≤ 2 * h := by
  apply (totalDegree_finsetProd _ _).trans
  calc
    _ ≤ ∑ _u : Fin h, 2 := Finset.sum_le_sum (fun u _ => freshENSFactor_degree_le g hg u)
    _ = 2 * h := by simp [Nat.mul_comm]

theorem freshENSCompanion_degree_le (g : ι → MvPolynomial σ K)
    (hg : ∀ i, (g i).totalDegree ≤ 1) (h : ℕ) (i : ι) :
    (freshENSCompanion g h i).totalDegree ≤ 2 * h + 1 := by
  apply (totalDegree_mul _ _).trans
  have hi := (totalDegree_rename_le (Sum.inl : σ → FreshENSVars σ ι h) (g i)).trans (hg i)
  have hp := freshENSProduct_degree_le g hg h
  omega

end
end MathResearch
