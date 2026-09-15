/-
Claim: lem:disjoint-binary-coordinate-pairs
Source: https://kbr.is-a.dev/math-research/#lean-disjoint-binary-coordinate-pairs
Scope: Pairwise disjoint binary coordinate edges for any finite family of directions under 4(t−1)<2^ℓ; exact used-label cardinality, bit differences, and sufficient positive residual-board parameters for the R14 range.
Declarations: MathResearch.PolynomialCalculus.flipColumn_label MathResearch.PolynomialCalculus.flipColumn_involutive MathResearch.PolynomialCalculus.flipColumn_ne MathResearch.PolynomialCalculus.coordinatePair_card MathResearch.PolynomialCalculus.coordinate_pair_avoiding MathResearch.PolynomialCalculus.coordinatePairs_card MathResearch.PolynomialCalculus.exists_disjoint_coordinate_pairs MathResearch.PolynomialCalculus.coordinatePair_bit_sum MathResearch.PolynomialCalculus.cube_residual_parameters
-/
import claims.CompactBitDecoder
namespace MathResearch.PolynomialCalculus
noncomputable section
open scoped BigOperators Classical

def flipColumn (ℓ : ℕ) (t : Fin ℓ) (c : Fin (2^ℓ)) : Fin (2^ℓ) :=
  (bitLabelEquiv ℓ).symm (bitLabelEquiv ℓ c+Pi.single t 1)

theorem flipColumn_label (ℓ : ℕ) (t : Fin ℓ) (c : Fin (2^ℓ)) (u : Fin ℓ) :
    bitLabelEquiv ℓ (flipColumn ℓ t c) u = bitLabelEquiv ℓ c u + if u=t then 1 else 0 := by
  simp [flipColumn,Pi.single_apply,eq_comm]

theorem flipColumn_involutive (ℓ : ℕ) (t : Fin ℓ) : Function.Involutive (flipColumn ℓ t) := by
  intro c
  apply (bitLabelEquiv ℓ).injective
  funext u
  simp [flipColumn,add_assoc,ZModModule.add_self]

theorem flipColumn_ne (ℓ : ℕ) (t : Fin ℓ) (c : Fin (2^ℓ)) : flipColumn ℓ t c ≠ c := by
  intro h
  have hh := congrArg (fun j => bitLabelEquiv ℓ j t) h
  rw [flipColumn_label] at hh
  simp only [↓reduceIte] at hh
  have h1 : (1 : ZMod 2)=0 := add_left_cancel (hh.trans (add_zero (bitLabelEquiv ℓ c t)).symm)
  exact one_ne_zero h1

def coordinatePair (ℓ : ℕ) (t : Fin ℓ) (c : Fin (2^ℓ)) : Finset (Fin (2^ℓ)) :=
  {c,flipColumn ℓ t c}

theorem coordinatePair_card (ℓ : ℕ) (t : Fin ℓ) (c : Fin (2^ℓ)) :
    (coordinatePair ℓ t c).card=2 := by
  exact Finset.card_pair (Ne.symm (flipColumn_ne ℓ t c))

theorem coordinate_pair_avoiding (ℓ : ℕ) (t : Fin ℓ) (F : Finset (Fin (2^ℓ)))
    (hF : 2*F.card<2^ℓ) : ∃ c : Fin (2^ℓ), c ∉ F ∧ flipColumn ℓ t c ∉ F := by
  let bad := F ∪ F.image (flipColumn ℓ t)
  have hbad : bad.card<(Finset.univ : Finset (Fin (2^ℓ))).card := by
    calc
      bad.card≤F.card+(F.image (flipColumn ℓ t)).card := Finset.card_union_le _ _
      _=2*F.card := by rw [Finset.card_image_of_injective _ (flipColumn_involutive ℓ t).injective]; omega
      _<(Finset.univ : Finset (Fin (2^ℓ))).card := by simpa using hF
  obtain ⟨c,_,hc⟩ := Finset.exists_mem_notMem_of_card_lt_card hbad
  refine ⟨c,fun h => hc (Finset.mem_union_left _ h),?_⟩
  intro h
  apply hc
  apply Finset.mem_union_right
  exact Finset.mem_image.mpr ⟨flipColumn ℓ t c,h,flipColumn_involutive ℓ t c⟩

def CoordinatePairsDisjoint {I : Type} (ℓ : ℕ) (S : Finset I)
    (d : I → Fin ℓ) (c : I → Fin (2^ℓ)) : Prop :=
  ∀ i ∈ S, ∀ j ∈ S, i≠j → Disjoint (coordinatePair ℓ (d i) (c i)) (coordinatePair ℓ (d j) (c j))

def coordinatePairs {I : Type} (ℓ : ℕ) (S : Finset I)
    (d : I → Fin ℓ) (c : I → Fin (2^ℓ)) : Finset (Fin (2^ℓ)) :=
  S.biUnion (fun i => coordinatePair ℓ (d i) (c i))

theorem coordinatePairs_card {I : Type} (ℓ : ℕ) (S : Finset I)
    (d : I → Fin ℓ) (c : I → Fin (2^ℓ)) (hc : CoordinatePairsDisjoint ℓ S d c) :
    (coordinatePairs ℓ S d c).card=2*S.card := by
  rw [coordinatePairs,Finset.card_biUnion hc]
  simp [coordinatePair_card,Nat.mul_comm]

theorem exists_disjoint_coordinate_pairs {I : Type} [DecidableEq I] (ℓ : ℕ)
    (S : Finset I) (d : I → Fin ℓ) (hS : 4*(S.card-1)<2^ℓ) :
    ∃ c : I → Fin (2^ℓ), CoordinatePairsDisjoint ℓ S d c := by
  revert hS
  induction S using Finset.induction_on with
  | empty =>
    intro _
    refine ⟨fun _ => ⟨0,by positivity⟩,?_⟩
    intro i hi
    simp at hi
  | @insert i S hi ih =>
    intro hS
    have hfour : 4*S.card<2^ℓ := by simpa [Finset.card_insert_of_notMem hi] using hS
    obtain ⟨c,hc⟩ := ih (by omega)
    let F := coordinatePairs ℓ S d c
    obtain ⟨a,ha,hfa⟩ := coordinate_pair_avoiding ℓ (d i) F (by
      have hcard := coordinatePairs_card ℓ S d c hc
      change 2*(coordinatePairs ℓ S d c).card<2^ℓ
      rw [hcard]
      omega)
    have hnew : ∀ j ∈ S, Disjoint (coordinatePair ℓ (d i) a) (coordinatePair ℓ (d j) (c j)) := by
      intro j hj
      apply Finset.disjoint_left.mpr
      intro x hx hxj
      have hxF : x ∈ F := Finset.mem_biUnion.mpr ⟨j,hj,hxj⟩
      simp only [coordinatePair,Finset.mem_insert,Finset.mem_singleton] at hx
      rcases hx with rfl | rfl
      · exact ha hxF
      · exact hfa hxF
    refine ⟨Function.update c i a,?_⟩
    intro j hj l hl hjl
    rcases Finset.mem_insert.mp hj with hjiEq | hjS
    · subst j
      rcases Finset.mem_insert.mp hl with hliEq | hlS
      · exact False.elim (hjl hliEq.symm)
      · have hli : l≠i := fun h => hi (h ▸ hlS)
        simpa [hli] using hnew l hlS
    · have hji : j≠i := fun h => hi (h ▸ hjS)
      rcases Finset.mem_insert.mp hl with hliEq | hlS
      · subst l
        simpa [hji] using (hnew j hjS).symm
      · have hli : l≠i := fun h => hi (h ▸ hlS)
        simpa [hji,hli] using hc j hjS l hlS hjl

theorem coordinatePair_bit_sum (ℓ : ℕ) (t : Fin ℓ) (c : Fin (2^ℓ)) (u : Fin ℓ) :
    (∑ j ∈ coordinatePair ℓ t c, bitLabelEquiv ℓ j u)=if u=t then 1 else 0 := by
  rw [coordinatePair,Finset.sum_pair (Ne.symm (flipColumn_ne ℓ t c)),flipColumn_label]
  rw [← add_assoc,ZModModule.add_self,zero_add]

theorem cube_residual_parameters (ℓ k B t : ℕ) (hℓ : 2≤ℓ) (hk : 1≤k) (htk : t≤k)
    (hkB : k≤B) (hpack : 4*(k-1)<2^ℓ) (hB : 2*B-1≤2^ℓ) :
    1≤2^ℓ-2*t ∧ 2*(B-t)-1≤2^ℓ-2*t := by
  have hpow : 2^ℓ=4*2^(ℓ-2) := by
    have he : ℓ=2+(ℓ-2) := by omega
    conv_lhs => rw [he,pow_add]
    simp
  have hsmall : 4*k≤2^ℓ := by
    have hp : 4*(k-1)<4*2^(ℓ-2) := by rwa [← hpow]
    have hh : 4*k≤4*2^(ℓ-2) := by omega
    exact hh.trans_eq hpow.symm
  have hfour : 4≤2^ℓ := by
    rw [hpow]
    have hp : 0<2^(ℓ-2) := pow_pos (by decide : 0<(2 : ℕ)) _
    omega
  constructor <;> omega
end
end MathResearch.PolynomialCalculus
