/-
Claim: lem:affine-clause-resolution-PC-degree
Source: https://kbr.is-a.dev/math-research/#lean-affine-clause-resolution-PC-degree
Scope: Complementary-parity resolution preserves max(K,4h+1), using completed premise derivations in one fixed complete registry; contexts may overlap and the conclusion may be empty. A general concrete-certificate engine is instantiated by the registry definitions.
Declarations: MathResearch.PolynomialCalculus.PCClause.resolve MathResearch.PolynomialCalculus.registry_resolution
-/
import claims.AffineClauseRegistry
import claims.BooleanReduction

namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial
open scoped BigOperators
variable {σ ι κ τ : Type} [Fintype ι] [Fintype κ] [Fintype τ]
local instance {ν : Type} : DecidableEq ((ν → ZMod 2) →ᵃ[ZMod 2] ZMod 2) := Classical.decEq _
variable {F : Set (Poly (ZMod 2) σ)} {h K : ℕ}

private theorem derive_mul_bound {f q : Poly (ZMod 2) σ} {B C : ℕ}
    (hf : Derives F B f) (hBC : B ≤ C) (hdeg : q.totalDegree + f.totalDegree ≤ C) :
    Derives F C (q*f) :=
  (hf.mul_polynomial q).mono (fun _ h => h) (max_le hBC hdeg)

private theorem residual_derivation (A : PCClause F h ι) (ia : ι)
    (P : Poly (ZMod 2) σ) (hP : P.totalDegree ≤ 2*h) (hh : 1 ≤ h)
    (hA : Derives F K A.value)
    (hcomp : ∀ i, i ≠ ia → Derives F (2*h+1) (A.input i * P)) :
    Derives F (max K (4*h)) (P - A.cofactor ia * A.input ia * P) := by
  classical
  have hprod : Derives F (max K (4*h)) (A.value * P) := by
    have hv := A.value_degree
    simpa only [mul_comm] using derive_mul_bound hA (le_max_left _ _)
      (show P.totalDegree + A.value.totalDegree ≤ max K (4*h) by omega)
  have hsum : (∑ i ∈ (Finset.univ.erase ia), A.cofactor i * (A.input i * P)) ∈
      pcSpace F (max K (4*h)) := by
    apply Submodule.sum_mem
    intro i hi
    have hi' : i ≠ ia := (Finset.mem_erase.mp hi).1
    have hd := A.prefix_degree i
    have hinput := A.input_degree i
    have hcompdeg : (A.input i * P).totalDegree ≤ 2*h+1 :=
      (totalDegree_mul _ _).trans (by omega)
    exact derive_mul_bound (hcomp i hi') (by omega) (by omega)
  have he : P - A.cofactor ia * A.input ia * P =
      A.value * P + ∑ i ∈ (Finset.univ.erase ia), A.cofactor i * (A.input i * P) := by
    have hi := congrArg (fun q => q * P) A.identity
    rw [sub_mul, one_mul, Finset.sum_mul] at hi
    have hs := Finset.sum_erase_add (s := Finset.univ)
      (f := fun i => A.cofactor i * A.input i * P) (Finset.mem_univ ia)
    rw [← hs] at hi
    simp only [mul_assoc] at hi
    linear_combination hi
  rw [he]
  exact Derives.add hprod hsum

private theorem residual_degree (A : PCClause F h ι) (ia : ι) (hpos : 1 ≤ h)
    (P : Poly (ZMod 2) σ) (hP : P.totalDegree ≤ 2*h) :
    (P - A.cofactor ia * A.input ia * P).totalDegree ≤ 4*h := by
  have hc := A.prefix_degree ia
  have hi := A.input_degree ia
  apply (totalDegree_sub _ _).trans
  apply max_le (by omega)
  apply (totalDegree_mul _ _).trans
  have hh := totalDegree_mul (A.cofactor ia) (A.input ia)
  omega

theorem PCClause.resolve [Fintype σ] (A : PCClause F h ι) (B : PCClause F h κ)
    (T : PCClause F h τ) (ia : ι) (ib : κ) (hh : 1 ≤ h)
    (hop : B.input ib = 1-A.input ia)
    (hctxA : ∀ i, i ≠ ia → ∃ j, T.input j = A.input i)
    (hctxB : ∀ i, i ≠ ib → ∃ j, T.input j = B.input i)
    (hbool : booleanBase ⊆ F) (hA : Derives F K A.value) (hB : Derives F K B.value) :
    Derives F (max K (4*h+1)) T.value := by
  classical
  let u := A.input ia
  let RA := T.value - A.cofactor ia * u * T.value
  let RB := T.value - B.cofactor ib * (1-u) * T.value
  have hca (i : ι) (hi : i ≠ ia) : Derives F (2*h+1) (A.input i * T.value) := by
    obtain ⟨j,hj⟩ := hctxA i hi
    rw [← hj]
    exact T.companion j
  have hcb (i : κ) (hi : i ≠ ib) : Derives F (2*h+1) (B.input i * T.value) := by
    obtain ⟨j,hj⟩ := hctxB i hi
    rw [← hj]
    exact T.companion j
  have hra : Derives F (max K (4*h)) RA := residual_derivation A ia T.value T.value_degree hh hA hca
  have hrb : Derives F (max K (4*h)) RB := by
    simpa only [hop] using residual_derivation B ib T.value T.value_degree hh hB hcb
  have hdRA : RA.totalDegree ≤ 4*h := residual_degree A ia hh T.value T.value_degree
  have hdu : u.totalDegree ≤ 1 := A.input_degree ia
  have hdopp : (1-u).totalDegree ≤ 1 := (totalDegree_sub _ _).trans (max_le (by simp) hdu)
  have hleft : Derives F (max K (4*h+1)) ((1-u)*RA) :=
    derive_mul_bound hra (by omega) (by omega)
  have hboolean : Derives F 2 (u^2-u) :=
    nsSpace_le_pcSpace _ _ (nsSpace_mono hbool (by decide : 2*1 ≤ 2)
      (polynomial_boolean_ns_bound u 1 hdu))
  have hbooldeg : (u^2-u).totalDegree ≤ 2 := hboolean.degree_le
  have hcofactor := A.prefix_degree ia
  have hvalue := T.value_degree
  have hdweight : (A.cofactor ia * T.value).totalDegree ≤ 4*h-1 :=
    (totalDegree_mul _ _).trans (by omega)
  have hcorrection : Derives F (max K (4*h+1)) ((A.cofactor ia*T.value)*(u^2-u)) :=
    derive_mul_bound hboolean (by omega) (by omega)
  have he : (1-u)*RA - (A.cofactor ia*T.value)*(u^2-u) = (1-u)*T.value := by
    dsimp [RA]
    ring
  have hsmall : Derives F (max K (4*h+1)) ((1-u)*T.value) := by
    rw [← he]
    simpa only [sub_eq_add_neg, neg_smul, one_smul] using
      Derives.add hleft (Derives.smul (-1) hcorrection)
  have hdsmall : ((1-u)*T.value).totalDegree ≤ 2*h+1 :=
    (totalDegree_mul _ _).trans (by omega)
  have hcbdeg := B.prefix_degree ib
  have hlast : Derives F (max K (4*h+1)) (B.cofactor ib*((1-u)*T.value)) :=
    derive_mul_bound hsmall le_rfl (by omega)
  have hRB := hrb.mono (fun _ h => h) (show max K (4*h) ≤ max K (4*h+1) by omega)
  have hefinal : B.cofactor ib*((1-u)*T.value) + RB = T.value := by dsimp [RB]; ring
  rw [← hefinal]
  exact Derives.add hlast hRB

private theorem registry_opposite_input {ν : Type} [Fintype ν] {N : ℕ}
    (C : Fin N → FiniteParityClause ν) (h : ℕ)
    (u : (ν → ZMod 2) →ᵃ[ZMod 2] ZMod 2) :
    registryOld C h (MathResearch.finiteAffinePolynomial (MathResearch.oppositeParity u)) =
      1-registryOld C h (MathResearch.finiteAffinePolynomial u) := by
  rw [MathResearch.oppositeParity, map_sub, map_sub]
  have hc : MathResearch.finiteAffinePolynomial (AffineMap.const (ZMod 2) (ν → ZMod 2) 1) = 1 := by
    simp [MathResearch.finiteAffinePolynomial]
  rw [hc, map_one]

theorem registry_resolution {ν : Type} [Fintype ν] {N : ℕ}
    (C : Fin N → FiniteParityClause ν) (h : ℕ)
    (old : Set (Poly (ZMod 2) ν)) (hh : 1 ≤ h) (a b t : Fin N)
    (A B : FiniteParityClause ν) (u : (ν → ZMod 2) →ᵃ[ZMod 2] ZMod 2)
    (ha : C a = insert u A) (hb : C b = insert (MathResearch.oppositeParity u) B)
    (ht : C t = A ∪ B) {K : ℕ}
    (hA : Derives (registrySystem C h old) K (registryValue C h a))
    (hB : Derives (registrySystem C h old) K (registryValue C h b)) :
    Derives (registrySystem C h old) (max K (4*h+1)) (registryValue C h t) := by
  classical
  let ia : C a := ⟨u, by rw [ha]; exact Finset.mem_insert_self _ _⟩
  let ib : C b := ⟨MathResearch.oppositeParity u, by rw [hb]; exact Finset.mem_insert_self _ _⟩
  apply PCClause.resolve (registryClauseData C h old hh a) (registryClauseData C h old hh b)
    (registryClauseData C h old hh t) ia ib hh
  · exact registry_opposite_input C h u
  · intro g hgi
    have hgA : g.val ∈ A := by
      have hm : g.val = u ∨ g.val ∈ A := by simpa [ha] using g.property
      rcases hm with hm | hm
      · exact False.elim (hgi (Subtype.ext hm))
      · exact hm
    let j : C t := ⟨g.val, by rw [ht]; exact Finset.mem_union_left B hgA⟩
    exact ⟨j,rfl⟩
  · intro g hgi
    have hgB : g.val ∈ B := by
      have hm : g.val = MathResearch.oppositeParity u ∨ g.val ∈ B := by simpa [hb] using g.property
      rcases hm with hm | hm
      · exact False.elim (hgi (Subtype.ext hm))
      · exact hm
    let j : C t := ⟨g.val, by rw [ht]; exact Finset.mem_union_right A hgB⟩
    exact ⟨j,rfl⟩
  · exact fun _ hf => Or.inl (Or.inr hf)
  · exact hA
  · exact hB

end
end MathResearch.PolynomialCalculus
