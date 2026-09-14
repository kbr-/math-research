/-
Claim: third-party:chessboard-star-intersections
Source: https://kbr.is-a.dev/math-research/#lean-chessboard-star-intersections
Scope: Intersections of at least two distinct first-row stars are exactly smaller rectangular boards, with boundary-compatible augmented chain equivalences, including zero remaining columns.
Declarations: MathResearch.ThirdParty.Augmented.star_intersection_faces MathResearch.ThirdParty.Augmented.starIntersectionChainEquiv MathResearch.ThirdParty.Augmented.differential_starIntersectionChainEquiv MathResearch.ThirdParty.Augmented.starIntersection_exactAt
-/
import «third-party-claims».ChessboardStarCover
import claims.AugmentedSubcomplexRelabeling
import Mathlib.Data.Fintype.EquivFin
namespace MathResearch.ThirdParty.Augmented
noncomputable section

theorem star_intersection_faces (a b : ℕ) (J : Finset (Fin b)) (hJ : 2 ≤ J.card)
    (M : Finset (Fin (a+1) × Fin b)) :
    M ∈ (intersection (firstRowStar a b) J).faces ↔
      M ∈ (chessboardComplex (a+1) b).faces ∧ ∀ x ∈ M, x.1 ≠ 0 ∧ x.2 ∉ J := by
  obtain ⟨j,hj,k,hk,hjk⟩ := Finset.one_lt_card.mp hJ
  constructor
  · intro h
    have hstar (i : Fin b) (hi : i ∈ J) :
        insert (0,i) M ∈ (chessboardComplex (a+1) b).faces := h i hi
    have hrow : ∀ x ∈ M, x.1 ≠ 0 := by
      intro x hx he
      have hxj := (hstar j hj).1 (Finset.mem_insert_of_mem hx) (Finset.mem_insert_self _ _) he
      have hxk := (hstar k hk).1 (Finset.mem_insert_of_mem hx) (Finset.mem_insert_self _ _) he
      exact hjk (congrArg Prod.snd (hxj.symm.trans hxk))
    refine ⟨(chessboardComplex (a+1) b).downward (Finset.subset_insert _ _) (hstar j hj), ?_⟩
    intro x hx
    refine ⟨hrow x hx, ?_⟩
    intro hc
    have hxj := (hstar x.2 hc).2 (Finset.mem_insert_of_mem hx) (Finset.mem_insert_self _ _) rfl
    exact hrow x hx (congrArg Prod.fst hxj)
  · rintro ⟨hM,hr⟩ i hi
    exact extend_matching M hM i (fun x hx => (hr x hx).1)
      (fun x hx he => (hr x hx).2 (he ▸ hi))

def remainingColumns (b : ℕ) (J : Finset (Fin b)) :
    {j : Fin b // j ∉ J} ≃ Fin (b-J.card) :=
  Fintype.equivFinOfCardEq (by simp [Fintype.card_subtype_compl])

def smallerBoardEmbedding (a b : ℕ) (J : Finset (Fin b)) :
    (Fin a × Fin (b-J.card)) ↪ (Fin (a+1) × Fin b) where
  toFun := fun x => (x.1.succ, ((remainingColumns b J).symm x.2).val)
  inj' := by
    intro x y h
    apply Prod.ext
    · exact Fin.succ_injective a (congrArg Prod.fst h)
    · apply (remainingColumns b J).symm.injective
      exact Subtype.ext (congrArg Prod.snd h)

private theorem smaller_map_faces (a b : ℕ) (J : Finset (Fin b)) (hJ : 2 ≤ J.card)
    (S : Finset (Fin a × Fin (b-J.card))) :
    S ∈ (chessboardComplex a (b-J.card)).faces ↔
      S.map (smallerBoardEmbedding a b J) ∈ (intersection (firstRowStar a b) J).faces := by
  rw [star_intersection_faces a b J hJ]
  constructor
  · intro hS
    constructor
    · constructor
      · intro x hx y hy h
        obtain ⟨u,hu,rfl⟩ := Finset.mem_map.mp hx
        obtain ⟨v,hv,rfl⟩ := Finset.mem_map.mp hy
        apply congrArg (smallerBoardEmbedding a b J)
        exact hS.1 hu hv (Fin.succ_injective a h)
      · intro x hx y hy h
        obtain ⟨u,hu,rfl⟩ := Finset.mem_map.mp hx
        obtain ⟨v,hv,rfl⟩ := Finset.mem_map.mp hy
        apply congrArg (smallerBoardEmbedding a b J)
        exact hS.2 hu hv ((remainingColumns b J).symm.injective (Subtype.ext h))
    · intro x hx
      obtain ⟨u,hu,rfl⟩ := Finset.mem_map.mp hx
      exact ⟨Fin.succ_ne_zero _, ((remainingColumns b J).symm u.2).property⟩
  · rintro ⟨hS,_⟩
    constructor
    · intro x hx y hy h
      apply (smallerBoardEmbedding a b J).injective
      apply hS.1 (Finset.mem_map.mpr ⟨x,hx,rfl⟩) (Finset.mem_map.mpr ⟨y,hy,rfl⟩)
      exact congrArg Fin.succ h
    · intro x hx y hy h
      apply (smallerBoardEmbedding a b J).injective
      apply hS.2 (Finset.mem_map.mpr ⟨x,hx,rfl⟩) (Finset.mem_map.mpr ⟨y,hy,rfl⟩)
      exact congrArg (fun j => ((remainingColumns b J).symm j).val) h

private theorem smaller_range (a b : ℕ) (J : Finset (Fin b)) (hJ : 2 ≤ J.card)
    (T : Finset (Fin (a+1) × Fin b)) (hT : T ∈ (intersection (firstRowStar a b) J).faces) :
    InRange (smallerBoardEmbedding a b J) T := by
  intro x hx
  have hh := ((star_intersection_faces a b J hJ T).mp hT).2 x hx
  refine ⟨(x.1.pred hh.1, remainingColumns b J ⟨x.2,hh.2⟩), ?_⟩
  apply Prod.ext
  · exact Fin.succ_pred _ hh.1
  · exact congrArg Subtype.val ((remainingColumns b J).symm_apply_apply _)

def starIntersectionChainEquiv (a b : ℕ) (J : Finset (Fin b)) (hJ : 2 ≤ J.card) (k : ℕ) :
    chains (chessboardComplex a (b-J.card)) k ≃ₗ[ZMod 2]
      chains (intersection (firstRowStar a b) J) k :=
  subcomplexChainEquiv (smallerBoardEmbedding a b J) _ _
    (smaller_map_faces a b J hJ) (smaller_range a b J hJ) k

theorem differential_starIntersectionChainEquiv (a b : ℕ) (J : Finset (Fin b))
    (hJ : 2 ≤ J.card) (k : ℕ) (c : chains (chessboardComplex a (b-J.card)) (k+1)) :
    differential (intersection (firstRowStar a b) J) k
      (starIntersectionChainEquiv a b J hJ (k+1) c) =
    starIntersectionChainEquiv a b J hJ k (differential (chessboardComplex a (b-J.card)) k c) :=
  differential_subcomplexChainEquiv _ _ _ _ _ k c
theorem starIntersection_exactAt (a b : ℕ) (J : Finset (Fin b)) (hJ : 2 ≤ J.card)
    (k : ℕ) (h : ExactAt (chessboardComplex a (b-J.card)) k) :
    ExactAt (intersection (firstRowStar a b) J) k :=
  exactAt_subcomplex (smallerBoardEmbedding a b J) _ _
    (smaller_map_faces a b J hJ) (smaller_range a b J hJ) k h
end
end MathResearch.ThirdParty.Augmented
