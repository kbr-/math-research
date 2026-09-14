/-
Claim: lem:binary-affine-zero-cover
Source: https://kbr.is-a.dev/math-research/#lean-binary-affine-zero-cover
Scope: Separator already in the first clause for a nontrivial binary semantic cover; both restricted zero sets are exactly its 0 and 1 fibers, with witnesses for both values. No finite-dimensional hypothesis is needed.
Declarations: MathResearch.binary_affine_zero_cover MathResearch.binary_affine_halves_translate
-/
import Mathlib.LinearAlgebra.AffineSpace.AffineMap
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic.FinCases

namespace MathResearch
noncomputable section
open scoped Affine

abbrev BinaryField := ZMod 2
variable {V : Type*} [AddCommGroup V] [Module BinaryField V]
abbrev ParityClause (V : Type*) [AddCommGroup V] [Module BinaryField V] :=
  Finset (V →ᵃ[BinaryField] BinaryField)

def clauseHolds (C : ParityClause V) (x : V) : Prop := ∃ g ∈ C, g x = 1
def clauseZero (C : ParityClause V) (x : V) : Prop := ∀ g ∈ C, g x = 0
def clauseEntails (C D : ParityClause V) : Prop := ∀ x, clauseHolds C x → clauseHolds D x

private lemma binary_cases (x : BinaryField) : x = 0 ∨ x = 1 := by
  fin_cases x
  · exact Or.inl rfl
  · exact Or.inr rfl

lemma clause_not_holds (C : ParityClause V) (x : V) :
    ¬ clauseHolds C x ↔ clauseZero C x := by
  constructor
  · intro h g hg
    rcases binary_cases (g x) with h0 | h1
    · exact h0
    · exact False.elim (h ⟨g, hg, h1⟩)
  · rintro h ⟨g, hg, h1⟩
    have := h g hg
    rw [h1] at this
    exact one_ne_zero this

lemma parity_three (g : V →ᵃ[BinaryField] BinaryField) (a b x : V) :
    g (a - b + x) = g a - g b + g x := by
  exact (g.map_vadd x (a - b)).trans (congrArg (· + g x) (g.linearMap_vsub a b))

lemma clause_zero_three (C : ParityClause V) {a b x : V}
    (ha : clauseZero C a) (hb : clauseZero C b) (hx : clauseZero C x) :
    clauseZero C (a - b + x) := by
  intro g hg
  rw [parity_three, ha g hg, hb g hg, hx g hg]
  simp

theorem binary_affine_zero_cover (A B D : ParityClause V)
    (sound : ∀ x, clauseHolds A x → clauseHolds B x → clauseHolds D x)
    (notA : ¬ clauseEntails A D) (notB : ¬ clauseEntails B D) :
    ∃ u ∈ A, ∃ a b : V,
      clauseZero D a ∧ clauseZero D b ∧ u a = 1 ∧ u b = 0 ∧
      ∀ x, clauseZero D x →
        (clauseZero A x ↔ u x = 0) ∧ (clauseZero B x ↔ u x = 1) := by
  classical
  have cover (x : V) (hx : clauseZero D x) : clauseZero A x ∨ clauseZero B x := by
    by_cases ha : clauseHolds A x
    · right
      apply (clause_not_holds B x).mp
      intro hb
      exact (clause_not_holds D x).mpr hx (sound x ha hb)
    · exact Or.inl ((clause_not_holds A x).mp ha)
  obtain ⟨a, ha, hda⟩ : ∃ a, clauseHolds A a ∧ ¬ clauseHolds D a := by
    simpa [clauseEntails, not_forall] using notA
  obtain ⟨b, hb, hdb⟩ : ∃ b, clauseHolds B b ∧ ¬ clauseHolds D b := by
    simpa [clauseEntails, not_forall] using notB
  have zda := (clause_not_holds D a).mp hda
  have zdb := (clause_not_holds D b).mp hdb
  have zba : clauseZero B a := (clause_not_holds B a).mp (fun h => hda (sound a ha h))
  have zab : clauseZero A b := (clause_not_holds A b).mp (fun h => hdb (sound b h hb))
  obtain ⟨u, hu, hua⟩ := ha
  obtain ⟨v, hv, hvb⟩ := hb
  have hub := zab u hu
  have key (x : V) (hx : clauseZero D x) (hbx : clauseZero B x) : u x = 1 := by
    rcases binary_cases (u x) with h0 | h1
    · have hz := clause_zero_three D zda zdb hx
      have huz : u (a - b + x) = 1 := by rw [parity_three, hua, hub, h0]; simp
      have hvz : v (a - b + x) = 1 := by rw [parity_three, zba v hv, hvb, hbx v hv]; decide
      exact False.elim ((clause_not_holds D _).mpr hz
        (sound _ ⟨u, hu, huz⟩ ⟨v, hv, hvz⟩))
    · exact h1
  refine ⟨u, hu, a, b, zda, zdb, hua, hub, ?_⟩
  intro x hx
  constructor
  · constructor
    · exact fun h => h u hu
    · intro h0
      rcases cover x hx with hA | hB
      · exact hA
      · have := key x hx hB
        rw [h0] at this
        exact False.elim (zero_ne_one this)
  · constructor
    · exact key x hx
    · intro h1
      rcases cover x hx with hA | hB
      · have := hA u hu
        rw [h1] at this
        exact False.elim (one_ne_zero this)
      · exact hB

theorem binary_affine_halves_translate (A B D : ParityClause V)
    (sound : ∀ x, clauseHolds A x → clauseHolds B x → clauseHolds D x)
    (notA : ¬ clauseEntails A D) (notB : ¬ clauseEntails B D) :
    ∃ a b : V, ∃ e : {x : V // clauseZero D x ∧ clauseZero A x} ≃
        {x : V // clauseZero D x ∧ clauseZero B x},
      ∀ x, (e x).val = a - b + x.val := by
  obtain ⟨u, _, a, b, hda, hdb, hua, hub, fibers⟩ := binary_affine_zero_cover A B D sound notA notB
  have flipA (x : V) (hx : clauseZero D x ∧ clauseZero A x) :
      clauseZero D (a - b + x) ∧ clauseZero B (a - b + x) := by
    have hd := clause_zero_three D hda hdb hx.1
    refine ⟨hd, (fibers _ hd).2.mpr ?_⟩
    rw [parity_three, hua, hub, (fibers x hx.1).1.mp hx.2]
    simp
  have flipB (x : V) (hx : clauseZero D x ∧ clauseZero B x) :
      clauseZero D (a - b + x) ∧ clauseZero A (a - b + x) := by
    have hd := clause_zero_three D hda hdb hx.1
    refine ⟨hd, (fibers _ hd).1.mpr ?_⟩
    rw [parity_three, hua, hub, (fibers x hx.1).2.mp hx.2]
    decide
  have twice (x : V) : a - b + (a - b + x) = x := by
    rw [← add_assoc, ZModModule.add_self, zero_add]
  let e : {x : V // clauseZero D x ∧ clauseZero A x} ≃
      {x : V // clauseZero D x ∧ clauseZero B x} := {
    toFun := fun x => ⟨a - b + x.val, flipA x.val x.property⟩
    invFun := fun x => ⟨a - b + x.val, flipB x.val x.property⟩
    left_inv := fun x => Subtype.ext (twice x.val)
    right_inv := fun x => Subtype.ext (twice x.val)
  }
  exact ⟨a, b, e, fun _ => rfl⟩

end
end MathResearch
