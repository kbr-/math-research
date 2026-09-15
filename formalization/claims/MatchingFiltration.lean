/-
Claim: audit:matching-extension-arbitrary-row-count
Source: https://kbr.is-a.dev/math-research/#lean-matching-extension-stable-filtration
Scope: Full prescribed bounded-functional extension, ordinary NS filtration stability, PC=NS and normalized nonrefutation for N≥1,N≥2B−1 and arbitrary row count m; the source's m≥B hypothesis is unnecessary.
Declarations: MathResearch.PolynomialCalculus.bounded_matching_annihilator_extension MathResearch.PolynomialCalculus.matching_normalized_annihilator MathResearch.PolynomialCalculus.functionalUnary_ns_stable MathResearch.PolynomialCalculus.functionalUnary_ns_filtration MathResearch.PolynomialCalculus.Derives.functionalUnary_ns MathResearch.PolynomialCalculus.functionalUnary_pc_eq_ns MathResearch.PolynomialCalculus.functionalUnary_no_ns_refutation MathResearch.PolynomialCalculus.functionalUnary_no_pc_refutation MathResearch.PolynomialCalculus.functionalUnary_normalized_design MathResearch.PolynomialCalculus.functionalUnary_normalized_span
-/
import claims.MatchingMomentExtension
namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial

theorem functionalUnary_ns_stable (m N B : ℕ) (hN : 1≤N) (hNB : 2*B-1≤N)
    (k : ℕ) (hk : k≤B) (P : Poly (ZMod 2) (Cell m N)) (hP : P.totalDegree≤k) :
    P ∈ nsSpace (functionalUnaryBase m N) B ↔ P ∈ nsSpace (functionalUnaryBase m N) k := by
  constructor
  · intro hp
    by_contra hn
    obtain ⟨L,hLP,hL⟩ := (MathResearch.LinearSeparation.normalized_annihilator_iff
      (nsSpace (functionalUnaryBase m N) k) P).mpr hn
    obtain ⟨E,hE,he⟩ := matching_annihilator_extension m N B hN hNB k hk L hL
    have hz := hE P hp
    have ho := (he P hP).trans hLP
    exact zero_ne_one (hz.symm.trans ho)
  · intro hp
    exact nsSpace_mono (Set.Subset.refl _) hk hp

theorem functionalUnary_ns_filtration (m N B : ℕ) (hN : 1≤N) (hNB : 2*B-1≤N)
    (k : ℕ) (hk : k≤B) :
    nsSpace (functionalUnaryBase (K := ZMod 2) m N) B ⊓ degreeSpace k =
      nsSpace (functionalUnaryBase m N) k := by
  ext P
  constructor
  · rintro ⟨hp,hd⟩
    exact (functionalUnary_ns_stable m N B hN hNB k hk P hd).mp hp
  · intro hp
    exact ⟨nsSpace_mono (Set.Subset.refl _) hk hp,nsSpace_le_degreeSpace _ k hp⟩

theorem Derives.functionalUnary_ns {m N B : ℕ} (hN : 1≤N) (hNB : 2*B-1≤N)
    {P : Poly (ZMod 2) (Cell m N)} (hP : Derives (functionalUnaryBase m N) B P) :
    P ∈ nsSpace (functionalUnaryBase m N) B := by
  induction hP with
  | zero => simp
  | hyp hf hd =>
    have h := nsSpace_generator (q := 1) hf (by simpa using hd)
    simpa using h
  | add hp hq ih jh => exact Submodule.add_mem _ ih jh
  | smul c hp ih => exact Submodule.smul_mem _ c ih
  | @mul_var v f hp hd ih =>
    by_cases hf : f=0
    · simp [hf]
    have hdegree : 1+f.totalDegree≤B := by
      rw [totalDegree_mul_of_isDomain (X_ne_zero v) hf,totalDegree_X] at hd
      exact hd
    have hlow := (functionalUnary_ns_stable m N B hN hNB (B-1) (by omega) f (by omega)).mp ih
    have he : B-1+1=B := by omega
    simpa only [totalDegree_X,he] using nsSpace_mul hlow (X v)

theorem functionalUnary_pc_eq_ns (m N B : ℕ) (hN : 1≤N) (hNB : 2*B-1≤N) :
    pcSpace (functionalUnaryBase (K := ZMod 2) m N) B = nsSpace (functionalUnaryBase m N) B := by
  ext P
  constructor
  · intro hp
    exact Derives.functionalUnary_ns hN hNB hp
  · intro hp
    exact nsSpace_le_pcSpace _ B hp

theorem functionalUnary_no_ns_refutation (m N B : ℕ) (hN : 1≤N) (hNB : 2*B-1≤N) :
    (1 : Poly (ZMod 2) (Cell m N)) ∉ nsSpace (functionalUnaryBase m N) B := by
  obtain ⟨L,hL,h1⟩ := matching_normalized_annihilator m N B hN hNB
  intro hp
  exact one_ne_zero (h1.symm.trans (hL 1 hp))

theorem functionalUnary_no_pc_refutation (m N B : ℕ) (hN : 1≤N) (hNB : 2*B-1≤N) :
    ¬Derives (functionalUnaryBase m N) B (1 : Poly (ZMod 2) (Cell m N)) := by
  intro hp
  exact functionalUnary_no_ns_refutation m N B hN hNB (hp.functionalUnary_ns hN hNB)

theorem functionalUnary_normalized_design (m N B : ℕ) (hN : 1≤N) (hNB : 2*B-1≤N) :
    HasNormalizedFunctional (nsSpace (functionalUnaryBase (K := ZMod 2) m N) B) B :=
  (ns_design_iff _ B).mpr (functionalUnary_no_ns_refutation m N B hN hNB)
def boundedAnnihilatorSpace (m N B : ℕ) :
    Submodule (ZMod 2) (degreeSpace (K := ZMod 2) (V := Cell m N) B →ₗ[ZMod 2] ZMod 2) :=
  ((nsSpace (functionalUnaryBase m N) B).comap (degreeSpace B).subtype).dualAnnihilator

theorem functionalUnary_normalized_span (m N B : ℕ) (hN : 1≤N) (hNB : 2*B-1≤N) :
    boundedAnnihilatorSpace m N B = Submodule.span (ZMod 2)
      {L | L ∈ boundedAnnihilatorSpace m N B ∧ L ⟨1,by simp [degreeSpace]⟩=1} := by
  obtain ⟨E,hE1,hE⟩ := functionalUnary_normalized_design m N B hN hNB
  let A := boundedAnnihilatorSpace m N B
  let v : degreeSpace (K := ZMod 2) (V := Cell m N) B := ⟨1,by simp [degreeSpace]⟩
  let S := Submodule.span (ZMod 2) {L | L ∈ A ∧ L v=1}
  have hEA : E ∈ A := by
    change E ∈ ((nsSpace (functionalUnaryBase m N) B).comap (degreeSpace B).subtype).dualAnnihilator
    rw [Submodule.mem_dualAnnihilator]
    exact hE
  have hES : E ∈ S := Submodule.subset_span ⟨hEA,hE1⟩
  apply le_antisymm
  · intro L hL
    let D := L+(1-L v) • E
    have hDA : D ∈ A := A.add_mem hL (A.smul_mem _ hEA)
    have hD1 : D v=1 := by
      change L v+(1-L v)*E v=1
      rw [hE1]
      ring
    have hDS : D ∈ S := Submodule.subset_span ⟨hDA,hD1⟩
    have h := S.sub_mem hDS (S.smul_mem (1-L v) hES)
    simpa [D] using h
  · apply Submodule.span_le.mpr
    intro L hL
    exact hL.1
end
end MathResearch.PolynomialCalculus
