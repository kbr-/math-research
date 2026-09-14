/-
Claim: third-party:chessboard-star-cover
Source: https://kbr.is-a.dev/math-research/#lean-chessboard-star-cover
Scope: Closed first-row stars are subcomplexes, have the cone closure property, and cover rectangular boards with at least as many columns as rows.
Declarations: MathResearch.ThirdParty.Augmented.closedStar MathResearch.ThirdParty.Augmented.closedStar_subcomplex MathResearch.ThirdParty.Augmented.closedStar_cone MathResearch.ThirdParty.Augmented.firstRowStars_cover MathResearch.ThirdParty.Augmented.extend_matching
-/
import claims.FiniteComplexCover
namespace MathResearch.ThirdParty.Augmented
noncomputable section
variable {V : Type*} [DecidableEq V]
def closedStar (K : Complex V) (v : V) (hv : {v} ∈ K.faces) : Complex V where
  faces := {s | insert v s ∈ K.faces}
  empty_mem := by simpa using hv
  downward := by intro s t h ht; exact K.downward (Finset.insert_subset_insert v h) ht
theorem closedStar_subcomplex (K : Complex V) (v : V) (hv : {v} ∈ K.faces) :
    (closedStar K v hv).faces ⊆ K.faces :=
  fun _ h => K.downward (Finset.subset_insert _ _) h
theorem closedStar_cone (K : Complex V) (v : V) (hv : {v} ∈ K.faces)
    (s : Finset V) (hs : s ∈ (closedStar K v hv).faces) :
    insert v s ∈ (closedStar K v hv).faces := by
  simpa only [closedStar, Set.mem_ofPred_eq, Finset.insert_idem] using hs

def firstRowStar (a b : ℕ) (j : Fin b) : Complex (Fin (a+1) × Fin b) :=
  closedStar (chessboardComplex (a+1) b) (0,j) (by
    constructor <;> intro x hx y hy _ <;>
      exact (Finset.mem_singleton.mp hx).trans (Finset.mem_singleton.mp hy).symm)

theorem extend_matching {a b : ℕ} (M : Finset (Fin (a+1) × Fin b))
    (hM : M ∈ (chessboardComplex (a+1) b).faces) (j : Fin b)
    (hr : ∀ x ∈ M, x.1 ≠ 0) (hc : ∀ x ∈ M, x.2 ≠ j) :
    insert (0,j) M ∈ (chessboardComplex (a+1) b).faces := by
  constructor
  · intro x hx y hy he
    rcases Finset.mem_insert.mp hx with rfl | hx
    · rcases Finset.mem_insert.mp hy with rfl | hy
      · rfl
      · exact False.elim (hr y hy he.symm)
    · rcases Finset.mem_insert.mp hy with rfl | hy
      · exact False.elim (hr x hx he)
      · exact hM.1 hx hy he
  · intro x hx y hy he
    rcases Finset.mem_insert.mp hx with rfl | hx
    · rcases Finset.mem_insert.mp hy with rfl | hy
      · rfl
      · exact False.elim (hc y hy he.symm)
    · rcases Finset.mem_insert.mp hy with rfl | hy
      · exact False.elim (hc x hx he)
      · exact hM.2 hx hy he

theorem firstRowStars_cover (a b : ℕ) (hab : a+1 ≤ b) :
    Covers (chessboardComplex (a+1) b) (firstRowStar a b) := by
  intro M hM
  classical
  by_cases hr : ∃ x ∈ M, x.1 = 0
  · obtain ⟨x, hx, he⟩ := hr
    refine ⟨x.2, ?_⟩
    change insert (0,x.2) M ∈ (chessboardComplex (a+1) b).faces
    have hx' : (0,x.2) ∈ M := by simpa [← he] using hx
    simpa [Finset.insert_eq_of_mem hx'] using hM
  · have hr' : ∀ x ∈ M, x.1 ≠ 0 := by
      intro x hx he
      exact hr ⟨x,hx,he⟩
    have hsub : M.image Prod.fst ⊆ Finset.univ.erase 0 := by
      intro r hr
      obtain ⟨x, hx, rfl⟩ := Finset.mem_image.mp hr
      simp [hr' x hx]
    have hcard : M.card ≤ a := by
      have := Finset.card_le_card hsub
      simpa [Finset.card_image_of_injOn hM.1] using this
    have hcol : (M.image Prod.snd).card < (Finset.univ : Finset (Fin b)).card := by
      rw [Finset.card_image_of_injOn hM.2]
      simpa using Nat.lt_of_le_of_lt hcard (Nat.lt_of_lt_of_le (Nat.lt_succ_self a) hab)
    obtain ⟨j, _, hj⟩ := Finset.exists_mem_notMem_of_card_lt_card hcol
    refine ⟨j, extend_matching M hM j hr' ?_⟩
    intro x hx he
    exact hj (Finset.mem_image.mpr ⟨x,hx,he⟩)
end
end MathResearch.ThirdParty.Augmented
