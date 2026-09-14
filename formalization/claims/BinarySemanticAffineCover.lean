/-
Claim: lem:binary-semantic-affine-cover
Source: https://kbr.is-a.dev/math-research/#binary-semantic-affine-cover
Scope: Binary semantic inference reduces to one weakening or two weakenings and one resolution; the basic derivation is sound and introduces at most two auxiliary clauses. Affine restriction preserves semantic inference. Compressed premises and conclusion each have at most dim(V)+1 literals. Separator, translation, and registry-description bounds are in dependency files. The concrete PC-degree simulation is not formalized here.
Declarations: MathResearch.binary_semantic_affine_cover MathResearch.binary_semantic_three_steps MathResearch.parity_derivation_sound MathResearch.binary_auxiliary_count MathResearch.binary_semantic_restriction MathResearch.binary_semantic_compressed
-/
import claims.BinaryAffineZeroCover
import claims.AffineClauseCompression

namespace MathResearch
noncomputable section
variable {V : Type*} [AddCommGroup V] [Module BinaryField V]

local instance : DecidableEq (V →ᵃ[BinaryField] BinaryField) := Classical.decEq _

def oppositeParity (u : V →ᵃ[BinaryField] BinaryField) : V →ᵃ[BinaryField] BinaryField :=
  AffineMap.const BinaryField V 1 - u

@[simp] lemma oppositeParity_apply (u : V →ᵃ[BinaryField] BinaryField) (x : V) :
    oppositeParity u x = 1 - u x := rfl

lemma clause_holds_insert (C : ParityClause V) (u : V →ᵃ[BinaryField] BinaryField) (x : V) :
    clauseHolds (insert u C) x ↔ u x = 1 ∨ clauseHolds C x := by
  classical
  simp [clauseHolds]

theorem binary_semantic_affine_cover (A B D : ParityClause V)
    (sound : ∀ x, clauseHolds A x → clauseHolds B x → clauseHolds D x) :
    clauseEntails A D ∨ clauseEntails B D ∨
      ∃ u ∈ A, clauseEntails A (insert u D) ∧
        clauseEntails B (insert (oppositeParity u) D) := by
  classical
  by_cases hA : clauseEntails A D
  · exact Or.inl hA
  by_cases hB : clauseEntails B D
  · exact Or.inr (Or.inl hB)
  obtain ⟨u, hu, a, b, hda, hdb, hua, hub, fibers⟩ := binary_affine_zero_cover A B D sound hA hB
  refine Or.inr (Or.inr ⟨u, hu, ?_, ?_⟩)
  · intro x hx
    apply (clause_holds_insert D u x).mpr
    by_cases hd : clauseHolds D x
    · exact Or.inr hd
    · have hz := (clause_not_holds D x).mp hd
      have hb := (clause_not_holds B x).mp (fun h => hd (sound x hx h))
      exact Or.inl ((fibers x hz).2.mp hb)
  · intro x hx
    apply (clause_holds_insert D (oppositeParity u) x).mpr
    by_cases hd : clauseHolds D x
    · exact Or.inr hd
    · have hz := (clause_not_holds D x).mp hd
      have ha := (clause_not_holds A x).mp (fun h => hd (sound x h hx))
      left
      simp [oppositeParity_apply, (fibers x hz).1.mp ha]

/-- Basic rules only: premises, semantic weakening, and resolution with a
shared context. The natural number counts new inference nodes. -/
inductive ParityDerivation (A B : ParityClause V) : ParityClause V → ℕ → Prop
  | leftPremise : ParityDerivation A B A 0
  | rightPremise : ParityDerivation A B B 0
  | weaken {C D : ParityClause V} {n : ℕ} : ParityDerivation A B C n →
      clauseEntails C D → ParityDerivation A B D (n + 1)
  | resolve {D : ParityClause V} {u : V →ᵃ[BinaryField] BinaryField} {n m : ℕ} :
      ParityDerivation A B (insert u D) n →
      ParityDerivation A B (insert (oppositeParity u) D) m →
      ParityDerivation A B D (n + m + 1)

theorem binary_semantic_three_steps (A B D : ParityClause V)
    (sound : ∀ x, clauseHolds A x → clauseHolds B x → clauseHolds D x) :
    ∃ n ≤ 3, ParityDerivation A B D n := by
  rcases binary_semantic_affine_cover A B D sound with hA | hB | ⟨u, _, hA, hB⟩
  · exact ⟨1, by decide, .weaken .leftPremise hA⟩
  · exact ⟨1, by decide, .weaken .rightPremise hB⟩
  · exact ⟨3, by decide, .resolve (.weaken .leftPremise hA) (.weaken .rightPremise hB)⟩

theorem parity_derivation_sound {A B D : ParityClause V} {n : ℕ}
    (proof : ParityDerivation A B D n) :
    ∀ x, clauseHolds A x → clauseHolds B x → clauseHolds D x := by
  induction proof with
  | leftPremise => exact fun _ h _ => h
  | rightPremise => exact fun _ _ h => h
  | weaken _ h ih => exact fun x ha hb => h x (ih x ha hb)
  | resolve _ _ ih₁ ih₂ =>
    intro x ha hb
    rcases (clause_holds_insert _ _ _).mp (ih₁ x ha hb) with hu | hd
    · rcases (clause_holds_insert _ _ _).mp (ih₂ x ha hb) with hv | hd
      · simp [oppositeParity_apply, hu] at hv
      · exact hd
    · exact hd

def binaryAuxiliaryClauses (D : ParityClause V) (u : V →ᵃ[BinaryField] BinaryField) :
    Finset (ParityClause V) := {insert u D, insert (oppositeParity u) D}

theorem binary_auxiliary_count (D : ParityClause V) (u : V →ᵃ[BinaryField] BinaryField) :
    (binaryAuxiliaryClauses D u).card ≤ 2 ∧
      ∀ C ∈ binaryAuxiliaryClauses D u, C.card ≤ D.card + 1 := by
  classical
  constructor
  · exact (Finset.card_insert_le _ _).trans (by simp)
  · intro C hC
    simp only [binaryAuxiliaryClauses, Finset.mem_insert, Finset.mem_singleton] at hC
    rcases hC with rfl | rfl
    · exact Finset.card_insert_le _ _
    · exact Finset.card_insert_le _ _

variable {U : Type*} [AddCommGroup U] [Module BinaryField U]

def restrictParityClause (C : ParityClause V) (f : U →ᵃ[BinaryField] V) : ParityClause U :=
  Finset.image (fun g => g.comp f) C

lemma restrict_clause_holds (C : ParityClause V) (f : U →ᵃ[BinaryField] V) (x : U) :
    clauseHolds (restrictParityClause C f) x ↔ clauseHolds C (f x) := by
  classical
  simp [clauseHolds, restrictParityClause, AffineMap.coe_comp]

theorem binary_semantic_restriction (A B D : ParityClause V)
    (sound : ∀ x, clauseHolds A x → clauseHolds B x → clauseHolds D x)
    (f : U →ᵃ[BinaryField] V) :
    ∀ x, clauseHolds (restrictParityClause A f) x →
      clauseHolds (restrictParityClause B f) x → clauseHolds (restrictParityClause D f) x := by
  intro x ha hb
  exact (restrict_clause_holds D f x).mpr
    (sound (f x) ((restrict_clause_holds A f x).mp ha) ((restrict_clause_holds B f x).mp hb))

theorem binary_semantic_compressed [FiniteDimensional BinaryField V]
    (A B D : ParityClause V)
    (sound : ∀ x, clauseHolds A x → clauseHolds B x → clauseHolds D x) :
    ∃ A' B' D' : ParityClause V,
      A'.card ≤ Module.finrank BinaryField V + 1 ∧
      B'.card ≤ Module.finrank BinaryField V + 1 ∧
      D'.card ≤ Module.finrank BinaryField V + 1 ∧
      (∀ x, clauseHolds A' x ↔ clauseHolds A x) ∧
      (∀ x, clauseHolds B' x ↔ clauseHolds B x) ∧
      (∀ x, clauseHolds D' x ↔ clauseHolds D x) ∧
      ∃ n ≤ 3, ParityDerivation A' B' D' n := by
  obtain ⟨A', _, hA, eA⟩ := affine_clause_basis_compression A
  obtain ⟨B', _, hB, eB⟩ := affine_clause_basis_compression B
  obtain ⟨D', _, hD, eD⟩ := affine_clause_basis_compression D
  refine ⟨A', B', D', hA, hB, hD, eA, eB, eD, ?_⟩
  apply binary_semantic_three_steps
  intro x ha hb
  exact (eD x).mpr (sound x ((eA x).mp ha) ((eB x).mp hb))

end
end MathResearch
