/-
Claim: thm:bit-PHP-affine-clause-PC-transfer
Source: https://kbr.is-a.dev/math-research/#lean-bit-PHP-affine-clause-PC-transfer
Scope: Full finite-DAG transfer for compact pair clauses and the actual usual bit-PHP CNF, covering weakening, complementary resolution, and binary semantic rules. Produces one fixed complete old-affine ENS registry with at most3S+binom(m,2) slots, explicit literal/coefficient inventory, and ordinary PC refutation degree max(2h+ℓ,4h+1), without a height restriction. The registry is identified with the family-removal interface.
Declarations: MathResearch.PolynomialCalculus.pigeonPair_card MathResearch.PolynomialCalculus.compact_bitPHP_PC_transfer MathResearch.PolynomialCalculus.usual_bitPHP_PC_transfer MathResearch.PolynomialCalculus.registry_system_eq_ensFamily
-/
import claims.AffineDAGRegistry
import claims.BitPHPInitialBridge
import claims.AffineFamilyRemovalWithUnits

namespace MathResearch.PolynomialCalculus
noncomputable section
open scoped BigOperators
local instance transferClauseDecidableEq {σ : Type} : DecidableEq ((σ → ZMod 2) →ᵃ[ZMod 2] ZMod 2) := Classical.decEq _

abbrev PigeonPair (m : ℕ) := {p : Fin m × Fin m // p.1 < p.2}

theorem pigeonPair_card (m : ℕ) : Fintype.card (PigeonPair m) = m.choose 2 := by
  change Fintype.card {p : Fin m × Fin m // p.1 < p.2} = m.choose 2
  rw [Fintype.card_subtype]
  simpa only [Fintype.card_fin] using (Fintype.card_product_filter_lt (α := Fin m))

def compactPairInitials (m ℓ : ℕ) : Set (FiniteParityClause (BitVar m ℓ)) :=
  {C | ∃ i i' : Fin m, i < i' ∧ C = compactPairClause (ℓ := ℓ) i i'}

def usualBitPHPInitials (m ℓ : ℕ) : Set (FiniteParityClause (BitVar m ℓ)) :=
  {C | ∃ i i' : Fin m, i < i' ∧ ∃ z : BitLabel ℓ, C = usualCNFClause i i' z}

private def pairInitialFamily (m ℓ : ℕ) (p : PigeonPair m) : FiniteParityClause (BitVar m ℓ) :=
  compactPairClause p.val.1 p.val.2

private theorem pairInitial_width (m ℓ : ℕ) (p : PigeonPair m) :
    (pairInitialFamily m ℓ p).card ≤ ℓ := by
  exact (Finset.card_image_le).trans (by simp)

private theorem bitPHP_transfer_of_cover {m ℓ S : ℕ}
    (I : Set (FiniteParityClause (BitVar m ℓ))) (C : Fin S → FiniteParityClause (BitVar m ℓ))
    (dag : AffineDAG I C) (finish : Fin S) (hempty : C finish = ∅)
    (cover : ∀ A ∈ I, ∃ p : PigeonPair m, MathResearch.clauseEntails (pairInitialFamily m ℓ p) A)
    (h : ℕ) (hh : 1 ≤ h) :
    ∃ (N : ℕ) (R : Fin N → FiniteParityClause (BitVar m ℓ)),
      N ≤ 3*S + m.choose 2 ∧
      (∀ c, (R c).card ≤ max ℓ (m*ℓ+2)) ∧
      (∑ c, (R c).card) ≤ N*max ℓ (m*ℓ+2) ∧
      Fintype.card (ClauseRegistryVars R h) ≤ m*ℓ + h*N*max ℓ (m*ℓ+2) ∧
      Derives (registrySystem R h (compactBitBase m ℓ)) (max (2*h+ℓ) (4*h+1)) 1 := by
  obtain ⟨N,R,initial,node,hN,hinit,hnode,hwidth,replay⟩ :=
    affine_dag_registry I C dag (pairInitialFamily m ℓ) ℓ (pairInitial_width m ℓ) cover
  have hw : ∀ c, (R c).card ≤ max ℓ (m*ℓ+2) := by
    simpa only [BitVar,Fintype.card_prod,Fintype.card_fin] using hwidth
  have hinv := registry_inventory_bound R h (max ℓ (m*ℓ+2)) hw
  have hv : Fintype.card (ClauseRegistryVars R h) ≤ m*ℓ+h*N*max ℓ (m*ℓ+2) := by
    simpa only [BitVar,Fintype.card_prod,Fintype.card_fin] using hinv.2
  refine ⟨N,R,?_,hw,hinv.1,hv,?_⟩
  · rw [hN,pigeonPair_card]
  · have hi (p : PigeonPair m) :
        Derives (registrySystem R h (compactBitBase m ℓ)) (max (2*h+ℓ) (4*h+1))
          (registryValue R h (initial p)) :=
      (registry_compact_initial R h (initial p) p.val.1 p.val.2 p.property (hinit p)).mono
        (fun _ h => h) (le_max_left _ _)
    have hp := replay h (compactBitBase m ℓ) (max (2*h+ℓ) (4*h+1)) hh (le_max_right _ _) hi finish
    have hzero : R (node finish) = ∅ := by
      apply Finset.subset_empty.mp
      simpa only [hempty] using (hnode finish).1
    rwa [registry_empty_value R h (node finish) hzero] at hp

theorem compact_bitPHP_PC_transfer {m ℓ S : ℕ}
    (C : Fin S → FiniteParityClause (BitVar m ℓ)) (dag : AffineDAG (compactPairInitials m ℓ) C)
    (finish : Fin S) (hempty : C finish = ∅) (h : ℕ) (hh : 1 ≤ h) :
    ∃ (N : ℕ) (R : Fin N → FiniteParityClause (BitVar m ℓ)),
      N ≤ 3*S + m.choose 2 ∧
      (∀ c, (R c).card ≤ max ℓ (m*ℓ+2)) ∧
      (∑ c, (R c).card) ≤ N*max ℓ (m*ℓ+2) ∧
      Fintype.card (ClauseRegistryVars R h) ≤ m*ℓ + h*N*max ℓ (m*ℓ+2) ∧
      Derives (registrySystem R h (compactBitBase m ℓ)) (max (2*h+ℓ) (4*h+1)) 1 := by
  apply bitPHP_transfer_of_cover _ C dag finish hempty ?_ h hh
  rintro A ⟨i,i',hii,rfl⟩
  exact ⟨⟨(i,i'),hii⟩,fun _ hx => hx⟩

theorem usual_bitPHP_PC_transfer {m ℓ S : ℕ}
    (C : Fin S → FiniteParityClause (BitVar m ℓ)) (dag : AffineDAG (usualBitPHPInitials m ℓ) C)
    (finish : Fin S) (hempty : C finish = ∅) (h : ℕ) (hh : 1 ≤ h) :
    ∃ (N : ℕ) (R : Fin N → FiniteParityClause (BitVar m ℓ)),
      N ≤ 3*S + m.choose 2 ∧
      (∀ c, (R c).card ≤ max ℓ (m*ℓ+2)) ∧
      (∑ c, (R c).card) ≤ N*max ℓ (m*ℓ+2) ∧
      Fintype.card (ClauseRegistryVars R h) ≤ m*ℓ + h*N*max ℓ (m*ℓ+2) ∧
      Derives (registrySystem R h (compactBitBase m ℓ)) (max (2*h+ℓ) (4*h+1)) 1 := by
  apply bitPHP_transfer_of_cover _ C dag finish hempty ?_ h hh
  rintro A ⟨i,i',hii,z,rfl⟩
  exact ⟨⟨(i,i'),hii⟩,compact_clause_entails_CNF i i' z⟩

theorem registry_system_eq_ensFamily {σ : Type} [Fintype σ] {N : ℕ}
    (C : Fin N → FiniteParityClause σ) (h : ℕ) (old : Set (Poly (ZMod 2) σ)) :
    registrySystem C h old = MathResearch.ensFamilySystem
      (fun c (g : C c) => MathResearch.finiteAffinePolynomial g.val) h old := by
  have ho : registryOld C h = MvPolynomial.rename (Sum.inl : σ → ClauseRegistryVars C h) := by
    rw [registryOld,MvPolynomial.rename_eq_aeval]
    rfl
  have he (c : Fin N) : registryFreshEmbedding C h c =
      MathResearch.familyFreshEmbedding (σ := σ) (ι := fun c => C c) (h := h) c := by
    ext z
    cases z <;> rfl
  have hv (c : Fin N) : registryValue C h c = MathResearch.ensFamilyValue
      (fun c (g : C c) => MathResearch.finiteAffinePolynomial g.val) h c := by
    rw [registry_fresh_value,MathResearch.ensFamilyValue,he]
  simp only [registrySystem,MathResearch.ensFamilySystem,registryInput,ho,hv]

end
end MathResearch.PolynomialCalculus
