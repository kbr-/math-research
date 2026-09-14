/-
Claim: third-party:chessboard-star-nerve
Source: https://kbr.is-a.dev/math-research/#lean-chessboard-star-nerve
Scope: On boards with at least two rows and columns, first-row star nerve is the simplex boundary; full intersection has only the empty face; exactness below top degree and cone exactness use checked H04/H05.
Declarations: MathResearch.ThirdParty.Augmented.proper_star_intersection_vertex MathResearch.ThirdParty.Augmented.full_star_intersection_empty MathResearch.ThirdParty.Augmented.firstRowStar_nerve_faces MathResearch.ThirdParty.Augmented.firstRowStar_nerve_eq MathResearch.ThirdParty.Augmented.firstRowStar_nerve_exact MathResearch.ThirdParty.Augmented.firstRowStar_nerve_acyclic MathResearch.ThirdParty.Augmented.firstRowStar_exact
-/
import «third-party-claims».ChessboardStarIntersections
import «third-party-claims».SimplexBoundary
namespace MathResearch.ThirdParty.Augmented
noncomputable section

theorem proper_star_intersection_vertex (a b : ℕ) (ha : 1 ≤ a)
    (J : Finset (Fin b)) (hJ : J ≠ Finset.univ) :
    ∃ v, {v} ∈ (intersection (firstRowStar a b) J).faces := by
  classical
  have hj : ∃ j : Fin b, j ∉ J := by
    by_contra h
    apply hJ
    ext j
    simp only [Finset.mem_univ, iff_true]
    exact Classical.not_not.mp (fun hn => h ⟨j,hn⟩)
  obtain ⟨j,hj⟩ := hj
  let r : Fin a := ⟨0,ha⟩
  let v : Fin (a+1) × Fin b := (r.succ,j)
  refine ⟨v, ?_⟩
  intro i hi
  refine extend_matching {v} ?_ i ?_ ?_
  · constructor <;> intro x hx y hy _ <;>
      exact (Finset.mem_singleton.mp hx).trans (Finset.mem_singleton.mp hy).symm
  · intro x hx
    rw [Finset.mem_singleton.mp hx]
    exact Fin.succ_ne_zero r
  · intro x hx he
    rw [Finset.mem_singleton.mp hx] at he
    have he' : j = i := he
    exact hj (he'.symm ▸ hi)

theorem full_star_intersection_empty (a b : ℕ) (hb : 2 ≤ b)
    (M : Finset (Fin (a+1) × Fin b)) :
    M ∈ (intersection (firstRowStar a b) Finset.univ).faces ↔ M = ∅ := by
  constructor
  · intro h
    apply Finset.eq_empty_iff_forall_notMem.mpr
    intro x hx
    have hh := ((star_intersection_faces a b Finset.univ (by simpa using hb) M).mp h).2 x hx
    exact hh.2 (Finset.mem_univ _)
  · rintro rfl
    exact (intersection (firstRowStar a b) Finset.univ).empty_mem

theorem firstRowStar_nerve_faces (a b : ℕ) (ha : 1 ≤ a) (hb : 2 ≤ b)
    (J : Finset (Fin b)) :
    J ∈ (nerve (firstRowStar a b)).faces ↔ J ⊂ Finset.univ := by
  rw [Finset.ssubset_iff_subset_ne]
  simp only [Finset.subset_univ, true_and]
  constructor
  · intro h he
    subst J
    rcases h with h | ⟨v,hv⟩
    · have hc := congrArg Finset.card h
      simp at hc
      omega
    · have hh := (full_star_intersection_empty a b hb {v}).mp hv
      exact Finset.singleton_ne_empty v hh
  · intro h
    obtain ⟨v,hv⟩ := proper_star_intersection_vertex a b ha J h
    exact Or.inr ⟨v,hv⟩

private theorem complex_ext {V : Type*} (K L : Complex V) (h : K.faces = L.faces) : K = L := by
  cases K
  cases L
  cases h
  rfl

theorem firstRowStar_nerve_eq (a b : ℕ) (ha : 1 ≤ a) (hb : 2 ≤ b) :
    nerve (firstRowStar a b) = simplexBoundary (Finset.univ : Finset (Fin b))
      (by exact ⟨⟨0,by omega⟩, Finset.mem_univ _⟩) := by
  have hf : (nerve (firstRowStar a b)).faces =
      (simplexBoundary (Finset.univ : Finset (Fin b))
        (by exact ⟨⟨0,by omega⟩, Finset.mem_univ _⟩)).faces := by
    ext J
    exact firstRowStar_nerve_faces a b ha hb J
  exact complex_ext _ _ hf

theorem firstRowStar_nerve_exact (a b : ℕ) (ha : 1 ≤ a) (hb : 2 ≤ b)
    (k : ℕ) (hk : k+1 < b) : ExactAt (nerve (firstRowStar a b)) k := by
  rw [firstRowStar_nerve_eq a b ha hb]
  apply simplexBoundary_exact
  simpa using hk

theorem firstRowStar_nerve_acyclic (a b : ℕ) (ha : 1 ≤ a) (hb : 2 ≤ b)
    (n : ℕ) (hn : n < b) : AcyclicThrough (nerve (firstRowStar a b)) n := by
  intro k hk
  apply firstRowStar_nerve_exact a b ha hb k
  omega

theorem firstRowStar_exact (a b : ℕ) (j : Fin b) (k : ℕ) :
    ExactAt (firstRowStar a b j) k := by
  apply cone_exact _ (0,j)
  exact closedStar_cone _ _ _
end
end MathResearch.ThirdParty.Augmented
