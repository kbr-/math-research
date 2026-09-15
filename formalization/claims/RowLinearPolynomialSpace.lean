/-
Claim: lem:row-linear-polynomial-space
Source: https://kbr.is-a.dev/math-research/#lean-row-linear-polynomial-space
Scope: Ordinary row-linear polynomial space, exact dimension, total-degree bound and maximal nonzero coefficient. No quotient injection or PC separation assertion.
Declarations: MathResearch.rowMonomialCells_rows MathResearch.rowMonomialCells_card MathResearch.rowMonomialExponent_degree MathResearch.rowMonomialExponent_injective MathResearch.rowMonomialIndex_card MathResearch.rowLinearSpace_finrank MathResearch.rowLinearSpace_totalDegree_le MathResearch.rowLinearSpace_top_coefficient
-/
import Mathlib.RingTheory.MvPolynomial.Basic
import Mathlib.Data.Fintype.Powerset
import Mathlib.LinearAlgebra.Dimension.Constructions

namespace MathResearch
open MvPolynomial
noncomputable section
open scoped BigOperators

/-- Choose at most k rows and one bit coordinate in every selected row. -/
abbrev RowMonomialIndex (m ℓ k : ℕ) :=
  Σ j : Fin (k + 1), Σ S : (Finset.univ : Finset (Fin m)).powersetCard j.val,
    (S.val → Fin ℓ)

def rowMonomialCells {m ℓ k : ℕ} (x : RowMonomialIndex m ℓ k) :
    Finset (Fin m × Fin ℓ) :=
  Finset.univ.map ⟨(fun r => (r.val, x.2.2 r)), by
    intro a b h
    apply Subtype.ext
    exact congrArg Prod.fst h⟩

def rowMonomialExponent {m ℓ k : ℕ} (x : RowMonomialIndex m ℓ k) :
    (Fin m × Fin ℓ) →₀ ℕ := (rowMonomialCells x).val.toFinsupp

def rowLinearSpace (K : Type*) [CommSemiring K] (m ℓ k : ℕ) :
    Submodule K (MvPolynomial (Fin m × Fin ℓ) K) :=
  restrictSupport K (Set.range (@rowMonomialExponent m ℓ k))

theorem rowMonomialIndex_card (m ℓ k : ℕ) :
    Fintype.card (RowMonomialIndex m ℓ k) =
      ∑ j ∈ Finset.range (k + 1), m.choose j * ℓ ^ j := by
  simp only [RowMonomialIndex, Fintype.card_sigma]
  rw [← Fin.sum_univ_eq_sum_range]
  apply Finset.sum_congr rfl
  intro j _
  have hcard (S : (Finset.univ : Finset (Fin m)).powersetCard j.val) :
      Fintype.card S.val = j.val := by
    simpa using (Finset.mem_powersetCard.mp S.property).2
  simp only [Fintype.card_fun, Fintype.card_fin, hcard]
  simp

theorem rowMonomialCells_rows {m ℓ k : ℕ} (x : RowMonomialIndex m ℓ k) :
    (rowMonomialCells x).image Prod.fst = x.2.1.val := by
  ext r
  rw [Finset.mem_image]
  constructor
  · rintro ⟨v, hv, rfl⟩
    obtain ⟨r, _, rfl⟩ := Finset.mem_map.mp hv
    exact r.property
  · intro hr
    refine ⟨(r, x.2.2 ⟨r, hr⟩), ?_, rfl⟩
    exact Finset.mem_map.mpr ⟨⟨r, hr⟩, Finset.mem_univ _, rfl⟩

theorem rowMonomialCells_card {m ℓ k : ℕ} (x : RowMonomialIndex m ℓ k) :
    (rowMonomialCells x).card = x.1.val := by
  simp only [rowMonomialCells, Finset.card_map, Finset.card_univ, Fintype.card_coe]
  exact (Finset.mem_powersetCard.mp x.2.1.property).2

private theorem rowMonomialCells_injective {m ℓ k : ℕ} :
    Function.Injective (@rowMonomialCells m ℓ k) := by
  intro x y h
  have hj : x.1 = y.1 := Fin.ext <| by
    rw [← rowMonomialCells_card x, ← rowMonomialCells_card y, h]
  have hs : x.2.1.val = y.2.1.val := by
    rw [← rowMonomialCells_rows x, ← rowMonomialCells_rows y, h]
  rcases x with ⟨j, ⟨S, f⟩⟩
  rcases y with ⟨j', ⟨T, g⟩⟩
  simp only at hj hs
  subst j'
  have hST : S = T := Subtype.ext hs
  subst T
  have hf : f = g := by
    funext r
    have hm : (r.val, f r) ∈ rowMonomialCells ⟨j, S, f⟩ := by
      exact Finset.mem_map.mpr ⟨r, Finset.mem_univ _, rfl⟩
    rw [h] at hm
    obtain ⟨u, _, hu⟩ := Finset.mem_map.mp hm
    have hur : u = r := Subtype.ext (congrArg Prod.fst hu)
    subst u
    exact (congrArg Prod.snd hu).symm
  subst g
  rfl

theorem rowMonomialExponent_injective {m ℓ k : ℕ} :
    Function.Injective (@rowMonomialExponent m ℓ k) := by
  intro x y h
  apply rowMonomialCells_injective
  apply Finset.val_injective
  exact Multiset.toFinsupp.injective h

theorem rowMonomialExponent_degree {m ℓ k : ℕ} (x : RowMonomialIndex m ℓ k) :
    (rowMonomialExponent x).sum (fun _ n => n) = x.1.val := by
  change (rowMonomialCells x).val.toFinsupp.sum (fun _ => id) = x.1.val
  rw [Multiset.toFinsupp_sum_eq]
  exact rowMonomialCells_card x

instance rowLinearSpace_finite (K : Type*) [Field K] (m ℓ k : ℕ) :
    Module.Finite K (rowLinearSpace K m ℓ k) := by
  let e := Equiv.ofInjective (@rowMonomialExponent m ℓ k) rowMonomialExponent_injective
  let _ := Fintype.ofEquiv (RowMonomialIndex m ℓ k) e
  exact Module.Finite.of_basis (basisRestrictSupport K _)

theorem rowLinearSpace_finrank (K : Type*) [Field K] (m ℓ k : ℕ) :
    Module.finrank K (rowLinearSpace K m ℓ k) =
      ∑ j ∈ Finset.range (k + 1), m.choose j * ℓ ^ j := by
  let e := Equiv.ofInjective (@rowMonomialExponent m ℓ k) rowMonomialExponent_injective
  let _ := Fintype.ofEquiv (RowMonomialIndex m ℓ k) e
  rw [rowLinearSpace, Module.finrank_eq_card_basis (basisRestrictSupport K _)]
  rw [← Fintype.card_congr e, rowMonomialIndex_card]

theorem rowLinearSpace_totalDegree_le {K : Type*} [Field K] {m ℓ k : ℕ}
    {p : MvPolynomial (Fin m × Fin ℓ) K} (hp : p ∈ rowLinearSpace K m ℓ k) :
    p.totalDegree ≤ k := by
  rw [totalDegree, Finset.sup_le_iff]
  intro a ha
  obtain ⟨x, rfl⟩ := hp ha
  rw [rowMonomialExponent_degree]
  exact Nat.le_of_lt_succ x.1.isLt

theorem rowLinearSpace_top_coefficient {K : Type*} [Field K] {m ℓ k : ℕ}
    {p : MvPolynomial (Fin m × Fin ℓ) K} (hp : p ∈ rowLinearSpace K m ℓ k)
    (hne : p ≠ 0) :
    ∃ x : RowMonomialIndex m ℓ k,
      p.coeff (rowMonomialExponent x) ≠ 0 ∧ x.1.val = p.totalDegree := by
  obtain ⟨a, ha, he⟩ := Finset.exists_mem_eq_sup p.support
    (MvPolynomial.support_nonempty.mpr hne) (fun a => a.sum (fun _ n => n))
  obtain ⟨x, rfl⟩ := hp ha
  refine ⟨x, MvPolynomial.mem_support_iff.mp ha, ?_⟩
  simpa [totalDegree, rowMonomialExponent_degree] using he.symm

end
end MathResearch
