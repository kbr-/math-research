/-
Claim: third-party:chessboard-homological-bound
Source: https://kbr.is-a.dev/math-research/#lean-chessboard-homological-bound
Scope: Full F₂ homological chessboard bound for every positive rectangular board, expressed as augmented cycle filling in every cell count k < min(a,b,floor((a+b+1)/3)). Homotopical connectivity is not claimed.
Declarations: MathResearch.ThirdParty.Augmented.chessboard_homological_bound
-/
import «third-party-claims».HomologicalCover
import «third-party-claims».ChessboardStarNerve
import claims.ChessboardParameterArithmetic

namespace MathResearch.ThirdParty.Augmented
noncomputable section

private theorem exact_at_zero {V : Type*} [Fintype V] [DecidableEq V]
    (K : Complex V) (v : V) (hv : {v} ∈ K.faces) : ExactAt K 0 := by
  intro c hc hz
  refine ⟨cone v c, ?_, ?_⟩
  · intro s hs
    by_cases hvs : v ∈ s
    · simp only [cone, hvs, ↓reduceIte]
      by_cases he : s.erase v = ∅
      · have hsingle : s = {v} := by simpa [he] using (Finset.insert_erase hvs).symm
        subst s
        rcases hs with hn | hn
        · exact False.elim (hn hv)
        · simp at hn
      · exact hc _ (Or.inr (fun hcard => he (Finset.card_eq_zero.mp hcard)))
    · simp [cone, hvs]
  · have h := cone_identity v c
    have hzero : cone v (0 : Coeff V) = 0 := by funext s; simp [cone]
    simpa only [hz, hzero, add_zero] using h

private theorem transpose_exact (a b k : ℕ) (h : ExactAt (chessboardComplex a b) k) :
    ExactAt (chessboardComplex b a) k := by
  intro c hc hz
  let e := Equiv.prodComm (Fin b) (Fin a)
  have hd := push_supported e.toEmbedding (chessboardComplex b a) (chessboardComplex a b)
    (transpose_faces b a) k c hc
  have hdz : boundary (push e.toEmbedding c) = 0 := by
    rw [boundary_push, hz]
    exact (pushLinear e.toEmbedding).map_zero
  obtain ⟨f, hf, hdf⟩ := h _ hd hdz
  refine ⟨push e.symm.toEmbedding f,
    push_supported e.symm.toEmbedding _ _ (transpose_faces a b) (k+1) f hf, ?_⟩
  rw [boundary_push, hdf, push_equiv_inverse]

private theorem complex_ext {V : Type*} (K L : Complex V) (h : K.faces = L.faces) : K = L := by
  cases K
  cases L
  cases h
  rfl

theorem chessboard_homological_bound (a b : ℕ) (ha : 1 ≤ a) (hb : 1 ≤ b) :
    AcyclicThrough (chessboardComplex a b) (chessboardNu a b) := by
  suffices hall : ∀ m a b : ℕ, min a b = m → 1 ≤ a → 1 ≤ b →
      AcyclicThrough (chessboardComplex a b) (chessboardNu a b) from
    hall (min a b) a b rfl ha hb
  intro m
  induction m using Nat.strong_induction_on with
  | h m ih =>
    intro a b hab ha hb
    have ordered : ∀ a b : ℕ, min a b = m → 1 ≤ a → a ≤ b →
        AcyclicThrough (chessboardComplex a b) (chessboardNu a b) := by
      intro a b hab ha hab'
      cases a with
      | zero => omega
      | succ a =>
        by_cases hzero : a = 0
        · subst a
          rw [chessboardNu_one (by omega)]
          intro k hk
          have hk0 : k = 0 := by omega
          subst k
          apply exact_at_zero _ (0, ⟨0, by omega⟩)
          constructor <;> intro x hx y hy _ <;>
            exact (Finset.mem_singleton.mp hx).trans (Finset.mem_singleton.mp hy).symm
        · have ha2 : 2 ≤ a + 1 := by omega
          apply homological_cover (chessboardComplex (a+1) b) (firstRowStar a b)
            (fun j => closedStar_subcomplex _ _ _) (firstRowStars_cover a b hab')
            (chessboardNu (a+1) b)
          · apply firstRowStar_nerve_acyclic a b (by omega) (by omega)
            have hnu := chessboardNu_ordered_bound ha2 hab'
            omega
          · intro J hJ hN r hr
            by_cases hj1 : J.card = 1
            · obtain ⟨j, rfl⟩ := Finset.card_eq_one.mp hj1
              have he : intersection (firstRowStar a b) {j} = firstRowStar a b j := by
                apply complex_ext
                ext S
                simp [intersection]
              rw [he]
              exact firstRowStar_exact a b j r
            · have hj2 : 2 ≤ J.card := by have := hJ.card_pos; omega
              have hjlt : J.card < b := by
                have hsub := (firstRowStar_nerve_faces a b (by omega) (by omega) J).mp hN
                simpa using Finset.card_lt_card hsub
              apply starIntersection_exactAt a b J hj2 r
              have hsm : min a (b - J.card) < m := by
                rw [← hab]
                simpa using (chessboard_induction_decrease (t := J.card) (by omega) hab').1
              apply ih _ hsm a (b - J.card) rfl (by omega) (by omega) r
              have hn := chessboardNu_intersection ha2 hab' hj2 hjlt
              simp only [Nat.add_sub_cancel] at hn
              omega
    by_cases h : a ≤ b
    · exact ordered a b hab ha h
    · have ht := ordered b a (by simpa [Nat.min_comm] using hab) hb (by omega)
      intro k hk
      apply transpose_exact b a k
      apply ht k
      rw [chessboardNu_symm b a]
      exact hk

end
end MathResearch.ThirdParty.Augmented
