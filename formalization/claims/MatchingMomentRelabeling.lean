/-
Claim: lem:matching-moment-row-relabeling
Source: https://kbr.is-a.dev/math-research/#lean-matching-moment-row-relabeling
Scope: Injective row relabeling preserves matching faces, unused columns and row marginals; row-set embeddings exhaust precisely their retained rows.
Declarations: MathResearch.PolynomialCalculus.rowEmbedding_matching MathResearch.PolynomialCalculus.rowEmbedding_rowUnused MathResearch.PolynomialCalculus.rowEmbedding_colUnused MathResearch.PolynomialCalculus.matching_marginals_row_pullback MathResearch.PolynomialCalculus.rowSetEmbedding_mem MathResearch.PolynomialCalculus.rowSetEmbedding_range MathResearch.PolynomialCalculus.rowSetEmbedding_inRange
-/
import claims.MatchingMomentCycles
namespace MathResearch.PolynomialCalculus
noncomputable section
open scoped BigOperators Classical
open MathResearch.ThirdParty.Augmented

def rowEmbedding {r m : ℕ} (N : ℕ) (f : Fin r ↪ Fin m) : Cell r N ↪ Cell m N where
  toFun := fun x => (f x.1,x.2)
  inj' := by
    intro x y h
    exact Prod.ext (f.injective (congrArg (fun z : Cell m N => z.1) h))
      (congrArg (fun z : Cell m N => z.2) h)

theorem rowEmbedding_matching {r m N : ℕ} (f : Fin r ↪ Fin m) (S : Finset (Cell r N)) :
    IsMatching (S.map (rowEmbedding N f)) ↔ IsMatching S := by
  constructor
  · intro h
    constructor
    · intro x hx y hy he
      apply (rowEmbedding N f).injective
      exact h.1 (Finset.mem_map.mpr ⟨x,hx,rfl⟩) (Finset.mem_map.mpr ⟨y,hy,rfl⟩) (congrArg f he)
    · intro x hx y hy he
      apply (rowEmbedding N f).injective
      exact h.2 (Finset.mem_map.mpr ⟨x,hx,rfl⟩) (Finset.mem_map.mpr ⟨y,hy,rfl⟩) he
  · intro h
    constructor
    · intro x hx y hy he
      obtain ⟨u,hu,rfl⟩ := Finset.mem_map.mp hx
      obtain ⟨v,hv,rfl⟩ := Finset.mem_map.mp hy
      exact congrArg (rowEmbedding N f) (h.1 hu hv (f.injective he))
    · intro x hx y hy he
      obtain ⟨u,hu,rfl⟩ := Finset.mem_map.mp hx
      obtain ⟨v,hv,rfl⟩ := Finset.mem_map.mp hy
      exact congrArg (rowEmbedding N f) (h.2 hu hv he)

theorem rowEmbedding_rowUnused {r m N : ℕ} (f : Fin r ↪ Fin m)
    (S : Finset (Cell r N)) (i : Fin r) :
    RowUnused (f i) (S.map (rowEmbedding N f)) ↔ RowUnused i S := by
  constructor
  · intro h x hx he
    apply h ((rowEmbedding N f) x) (Finset.mem_map.mpr ⟨x,hx,rfl⟩)
    exact congrArg f he
  · intro h x hx he
    obtain ⟨u,hu,rfl⟩ := Finset.mem_map.mp hx
    exact h u hu (f.injective he)

theorem rowEmbedding_colUnused {r m N : ℕ} (f : Fin r ↪ Fin m)
    (S : Finset (Cell r N)) (j : Fin N) :
    ColUnused j (S.map (rowEmbedding N f)) ↔ ColUnused j S := by
  constructor
  · intro h x hx he
    exact h ((rowEmbedding N f) x) (Finset.mem_map.mpr ⟨x,hx,rfl⟩) he
  · intro h x hx he
    obtain ⟨u,hu,rfl⟩ := Finset.mem_map.mp hx
    exact h u hu he

theorem matching_marginals_row_pullback {r m N B : ℕ} (f : Fin r ↪ Fin m)
    (z : Finset (Cell m N) → ZMod 2) (hz : MatchingMarginals m N B z) :
    MatchingMarginals r N B (fun S => z (S.map (rowEmbedding N f))) := by
  intro S hS hcard i hi
  have h := hz (S.map (rowEmbedding N f)) ((rowEmbedding_matching f S).mpr hS)
    (by simpa using hcard) (f i) ((rowEmbedding_rowUnused f S i).mpr hi)
  dsimp only
  simp_rw [rowEmbedding_colUnused] at h
  calc
    _ = ∑ j : Fin N, if ColUnused j S then z (insert (f i,j) (S.map (rowEmbedding N f))) else 0 := by
      apply Finset.sum_congr rfl
      intro j _
      by_cases hj : ColUnused j S
      · simp only [hj,↓reduceIte,Finset.map_insert]
        rfl
      · simp [hj]
    _ = z (S.map (rowEmbedding N f)) := h

def rowSetEmbedding {m : ℕ} (S : Finset (Fin m)) : Fin S.card ↪ Fin m where
  toFun := fun i => (S.equivFin.symm i).val
  inj' := by
    intro i j h
    exact S.equivFin.symm.injective (Subtype.ext h)

theorem rowSetEmbedding_mem {m : ℕ} (S : Finset (Fin m)) (i : Fin S.card) :
    rowSetEmbedding S i ∈ S := (S.equivFin.symm i).property

theorem rowSetEmbedding_range {m : ℕ} (S : Finset (Fin m)) (i : Fin m) :
    (∃ j, rowSetEmbedding S j=i) ↔ i ∈ S := by
  constructor
  · rintro ⟨j,rfl⟩; exact rowSetEmbedding_mem S j
  · intro hi
    exact ⟨S.equivFin ⟨i,hi⟩,congrArg Subtype.val (S.equivFin.symm_apply_apply ⟨i,hi⟩)⟩

def RowsWithin {m N : ℕ} (S : Finset (Fin m)) (T : Finset (Cell m N)) : Prop :=
  ∀ x ∈ T, x.1 ∈ S

theorem rowSetEmbedding_inRange {m N : ℕ} (S : Finset (Fin m)) (T : Finset (Cell m N)) :
    InRange (rowEmbedding N (rowSetEmbedding S)) T ↔ RowsWithin S T := by
  constructor
  · intro h x hx
    obtain ⟨u,rfl⟩ := h x hx
    exact rowSetEmbedding_mem S u.1
  · intro h x hx
    obtain ⟨i,hi⟩ := (rowSetEmbedding_range S x.1).mpr (h x hx)
    exact ⟨(i,x.2),Prod.ext hi rfl⟩
end
end MathResearch.PolynomialCalculus
