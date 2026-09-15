/-
Claim: lem:matching-marginal-cycle
Source: https://kbr.is-a.dev/math-research/#lean-matching-marginal-cycle
Scope: For s≥1, compatible lower matching moments form an augmented F₂ cycle in cell count s−1; checked chessboard homology supplies fillings when N≥2s−1, including s=1 and s=2.
Declarations: MathResearch.PolynomialCalculus.momentLayer_supported MathResearch.PolynomialCalculus.rowBoundary_unused MathResearch.PolynomialCalculus.rowBoundary_occupied MathResearch.PolynomialCalculus.rowUnused_iff_not_mem_image MathResearch.PolynomialCalculus.unused_rows_card MathResearch.PolynomialCalculus.momentLayer_boundary_marginals MathResearch.PolynomialCalculus.matching_moment_cycle MathResearch.PolynomialCalculus.matching_moment_filling MathResearch.PolynomialCalculus.MatchingMarginals.mono
-/
import claims.MatchingMomentCompleteness
import «third-party-claims».ChessboardFillingProof
namespace MathResearch.PolynomialCalculus
noncomputable section
open scoped BigOperators Classical
open MathResearch.ThirdParty
open MathResearch.ThirdParty.Augmented

def momentLayer (m N k : ℕ) (z : Finset (Cell m N) → ZMod 2) : Coeff (Cell m N) :=
  fun T => if IsMatching T ∧ T.card=k then z T else 0

theorem momentLayer_supported (m N k : ℕ) (z : Finset (Cell m N) → ZMod 2) :
    Supported (chessboardComplex m N) k (momentLayer m N k z) := by
  intro T hT
  by_cases h : IsMatching T ∧ T.card=k
  · exact False.elim (hT.elim (fun hT => hT h.1) (fun hT => hT h.2))
  · simp [momentLayer,h]

def rowBoundary (m N k : ℕ) (z : Finset (Cell m N) → ZMod 2)
    (U : Finset (Cell m N)) (i : Fin m) : ZMod 2 :=
  ∑ j : Fin N, if (i,j) ∈ U then 0 else momentLayer m N (k+1) z (insert (i,j) U)

theorem rowBoundary_unused (m N k : ℕ) (z : Finset (Cell m N) → ZMod 2)
    (U : Finset (Cell m N)) (hU : IsMatching U) (hcard : U.card=k)
    (i : Fin m) (hi : RowUnused i U) :
    rowBoundary m N k z U i = ∑ j : Fin N, if ColUnused j U then z (insert (i,j) U) else 0 := by
  apply Finset.sum_congr rfl
  intro j _
  have hij : (i,j) ∉ U := fun h => hi (i,j) h rfl
  have hd : (insert (i,j) U).card=k+1 := by rw [Finset.card_insert_of_notMem hij,hcard]
  simp only [hij,↓reduceIte,momentLayer,hd,and_true]
  rw [matching_insert_unused U hU i hi j]

theorem rowBoundary_occupied (m N k : ℕ) (z : Finset (Cell m N) → ZMod 2)
    (U : Finset (Cell m N)) (hU : IsMatching U)
    (i : Fin m) (hi : ¬RowUnused i U) : rowBoundary m N k z U i=0 := by
  change ¬(∀ x ∈ U, x.1 ≠ i) at hi
  push Not at hi
  obtain ⟨⟨i',j₀⟩,hj₀,he⟩ := hi
  change i'=i at he
  subst i'
  apply Finset.sum_eq_zero
  intro j _
  by_cases hj : (i,j) ∈ U
  · simp [hj]
  · have hm : ¬IsMatching (insert (i,j) U) := by
      intro h
      have he := (matching_insert_occupied U hU i j₀ hj₀ j).mp h
      exact hj (he.symm ▸ hj₀)
    simp [hj,momentLayer,hm]

theorem rowUnused_iff_not_mem_image {m N : ℕ} (U : Finset (Cell m N)) (i : Fin m) :
    RowUnused i U ↔ i ∉ U.image Prod.fst := by
  constructor
  · intro h hn
    obtain ⟨x,hx,he⟩ := Finset.mem_image.mp hn
    exact h x hx he
  · intro h x hx he
    exact h (Finset.mem_image.mpr ⟨x,hx,he⟩)

theorem unused_rows_card {m N : ℕ} (U : Finset (Cell m N)) (hU : IsMatching U) :
    (Finset.univ.filter (fun i : Fin m => RowUnused i U)).card=m-U.card := by
  have he : Finset.univ.filter (fun i : Fin m => RowUnused i U) = Finset.univ \ U.image Prod.fst := by
    ext i
    simp [rowUnused_iff_not_mem_image]
  rw [he,Finset.card_sdiff_of_subset (Finset.subset_univ _),Finset.card_image_of_injOn hU.1]
  simp

theorem momentLayer_boundary_marginals (m N k : ℕ) (z : Finset (Cell m N) → ZMod 2)
    (hz : MatchingMarginals m N (k+1) z) (U : Finset (Cell m N))
    (hU : IsMatching U) (hcard : U.card=k) :
    boundary (momentLayer m N (k+1) z) U =
      ∑ i : Fin m, if RowUnused i U then z U else 0 := by
  change (∑ x : Fin m × Fin N, if x ∈ U then 0 else momentLayer m N (k+1) z (insert x U))=_
  rw [Fintype.sum_prod_type]
  apply Finset.sum_congr rfl
  intro i _
  change rowBoundary m N k z U i=_
  by_cases hi : RowUnused i U
  · simp only [hi,↓reduceIte]
    rw [rowBoundary_unused m N k z U hU hcard i hi]
    exact hz U hU (by omega) i hi
  · simpa [hi] using rowBoundary_occupied m N k z U hU i hi

private theorem matching_moment_cycle_two (s N : ℕ) (hs : 2≤s) (z : Finset (Cell s N) → ZMod 2)
    (hz : MatchingMarginals s N (s-1) z) : boundary (momentLayer s N (s-1) z)=0 := by
  funext U
  by_cases h : IsMatching U ∧ U.card=s-2
  · have he : s-2+1=s-1 := by omega
    have hb := momentLayer_boundary_marginals s N (s-2) z (by simpa [he] using hz) U h.1 h.2
    rw [he] at hb
    rw [hb]
    have hc : (Finset.univ.filter (fun i : Fin s => RowUnused i U)).card=2 := by
      rw [unused_rows_card U h.1,h.2]
      omega
    rw [← Finset.sum_filter]
    rw [Finset.sum_const,hc,two_nsmul]
    exact ZModModule.add_self _
  · have he : s-2+1=s-1 := by omega
    have hsupp : Supported (chessboardComplex s N) (s-2+1) (momentLayer s N (s-1) z) := by
      simpa [he] using momentLayer_supported s N (s-1) z
    have hd := boundary_supported (chessboardComplex s N) (s-2) (momentLayer s N (s-1) z) hsupp
    apply hd
    simpa only [IsMatching,not_and_or] using h
theorem matching_moment_cycle (s N : ℕ) (hs : 1≤s) (z : Finset (Cell s N) → ZMod 2)
    (hz : MatchingMarginals s N (s-1) z) : boundary (momentLayer s N (s-1) z)=0 := by
  by_cases h : s=1
  · subst s
    exact boundary_empty (chessboardComplex 1 N) _ (momentLayer_supported 1 N 0 z)
  · exact matching_moment_cycle_two s N (by omega) z hz

theorem matching_moment_filling (s N : ℕ) (hs : 1≤s) (hN : 2*s-1≤N)
    (z : Finset (Cell s N) → ZMod 2) (hz : MatchingMarginals s N (s-1) z) :
    ∃ y : Coeff (Cell s N), Supported (chessboardComplex s N) s y ∧
      boundary y=momentLayer s N (s-1) z := by
  have hac := chessboard_homological_bound s N (by omega) (by omega)
  rw [chessboardNu_stable_range hN] at hac
  obtain ⟨y,hy,he⟩ := hac (s-1) (by omega) (momentLayer s N (s-1) z)
    (momentLayer_supported s N (s-1) z) (matching_moment_cycle s N hs z hz)
  exact ⟨y,by simpa [Nat.sub_add_cancel (show 1≤s by omega)] using hy,he⟩

theorem MatchingMarginals.mono {m N B C : ℕ} {z : Finset (Cell m N) → ZMod 2}
    (hz : MatchingMarginals m N B z) (hCB : C≤B) : MatchingMarginals m N C z := by
  intro S hS hcard i hi
  exact hz S hS (lt_of_lt_of_le hcard hCB) i hi
end
end MathResearch.PolynomialCalculus
