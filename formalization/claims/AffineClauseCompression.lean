/-
Claim: lem:affine-clause-basis-compression
Source: https://kbr.is-a.dev/math-research/#lean-affine-clause-basis-compression
Scope: Every finite binary affine clause has a semantically equivalent subclause with at most dim(V)+1 literals; no satisfiability hypothesis is needed.
Declarations: MathResearch.affine_clause_basis_compression MathResearch.affine_clause_registry_compression
-/
import claims.BinaryAffineZeroCover
import Mathlib.Algebra.Field.ZMod
import Mathlib.LinearAlgebra.AffineSpace.FiniteDimensional
import Mathlib.LinearAlgebra.LinearIndependent.Lemmas

namespace MathResearch
noncomputable section
variable {V : Type*} [AddCommGroup V] [Module BinaryField V]

lemma clause_zero_span (C : ParityClause V) (x : V) (hx : clauseZero C x)
    (g : V →ᵃ[BinaryField] BinaryField)
    (hg : g ∈ Submodule.span BinaryField (C : Set (V →ᵃ[BinaryField] BinaryField))) : g x = 0 := by
  let ev : (V →ᵃ[BinaryField] BinaryField) →ₗ[BinaryField] BinaryField := {
    toFun := fun f => f x
    map_add' := by intros; rfl
    map_smul' := by intros; rfl
  }
  have hs : Submodule.span BinaryField (C : Set (V →ᵃ[BinaryField] BinaryField)) ≤ ev.ker := by
    apply Submodule.span_le.mpr
    intro f hf
    exact hx f hf
  exact hs hg

theorem affine_clause_basis_compression [FiniteDimensional BinaryField V]
    (C : ParityClause V) :
    ∃ S : ParityClause V, S ⊆ C ∧ S.card ≤ Module.finrank BinaryField V + 1 ∧
      ∀ x, clauseHolds S x ↔ clauseHolds C x := by
  classical
  obtain ⟨s, hs, hspan, hli⟩ := exists_linearIndependent BinaryField
    (C : Set (V →ᵃ[BinaryField] BinaryField))
  have hfinite : s.Finite := C.finite_toSet.subset hs
  let S : ParityClause V := hfinite.toFinset
  have hSC : S ⊆ C := by simpa [S] using hs
  have hspanS : Submodule.span BinaryField (S : Set (V →ᵃ[BinaryField] BinaryField)) =
      Submodule.span BinaryField (C : Set (V →ᵃ[BinaryField] BinaryField)) := by simpa [S] using hspan
  have hliS : LinearIndependent BinaryField (fun g : S => (g : V →ᵃ[BinaryField] BinaryField)) := by
    let inc : S → s := fun g => ⟨g.val, hfinite.mem_toFinset.mp g.property⟩
    exact hli.comp inc (fun x y h => Subtype.ext (congrArg (fun z : s => z.val) h))
  refine ⟨S, hSC, ?_, ?_⟩
  · have bound := hliS.finset_card_le_finrank
    simpa [AffineMap.finrank_eq] using bound
  · intro x
    have zeros : clauseZero S x ↔ clauseZero C x := by
      constructor
      · intro h g hg
        apply clause_zero_span S x h g
        rw [hspanS]
        exact Submodule.subset_span hg
      · intro h g hg
        exact h g (hSC hg)
    have := not_congr zeros
    simpa only [← clause_not_holds, not_not] using this

theorem affine_clause_registry_compression [FiniteDimensional BinaryField V]
    (N : ℕ) (C : Fin N → ParityClause V) :
    ∃ S : Fin N → ParityClause V,
      (∀ i, S i ⊆ C i ∧ (S i).card ≤ Module.finrank BinaryField V + 1 ∧
        ∀ x, clauseHolds (S i) x ↔ clauseHolds (C i) x) ∧
      (∑ i, (S i).card * (Module.finrank BinaryField V + 1)) ≤
        N * (Module.finrank BinaryField V + 1) ^ 2 := by
  classical
  choose S hS using fun i => affine_clause_basis_compression (C i)
  refine ⟨S, hS, ?_⟩
  calc
    _ ≤ ∑ _i : Fin N, (Module.finrank BinaryField V + 1) ^ 2 := by
      apply Finset.sum_le_sum
      intro i _
      simpa [pow_two] using Nat.mul_le_mul_right (Module.finrank BinaryField V + 1) (hS i).2.1
    _ = _ := by simp

end
end MathResearch
