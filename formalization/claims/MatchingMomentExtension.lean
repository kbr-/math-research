/-
Claim: lem:prescribed-matching-moment-extension
Source: https://kbr.is-a.dev/math-research/#lean-prescribed-matching-moment-extension
Scope: Extension of arbitrary prescribed binary matching moments across degrees by checked row-set fillings; constant moment preserved.
Declarations: MathResearch.PolynomialCalculus.rowset_moment_filling MathResearch.PolynomialCalculus.supported_occupied_row_zero MathResearch.PolynomialCalculus.supported_row_boundary MathResearch.PolynomialCalculus.updateMoments_old MathResearch.PolynomialCalculus.updateMoments_top MathResearch.PolynomialCalculus.matching_moments_step MathResearch.PolynomialCalculus.matching_moments_extend MathResearch.PolynomialCalculus.matching_moments_normalized MathResearch.PolynomialCalculus.momentFunctional_congr MathResearch.PolynomialCalculus.matching_annihilator_extension MathResearch.PolynomialCalculus.bounded_matching_annihilator_extension MathResearch.PolynomialCalculus.matching_normalized_annihilator
-/
import claims.MatchingMomentRelabeling
namespace MathResearch.PolynomialCalculus
noncomputable section
open scoped BigOperators Classical
open MathResearch.ThirdParty.Augmented

def RowSupported {m N : ℕ} (S : Finset (Fin m)) (k : ℕ) (c : Coeff (Cell m N)) : Prop :=
  Supported (chessboardComplex m N) k c ∧ ∀ T, ¬RowsWithin S T → c T=0

theorem rowset_moment_filling (m N : ℕ) (S : Finset (Fin m)) (hs : 1≤S.card)
    (hN : 2*S.card-1≤N) (z : Finset (Cell m N) → ZMod 2)
    (hz : MatchingMarginals m N (S.card-1) z) :
    ∃ y : Coeff (Cell m N), RowSupported S S.card y ∧
      ∀ T, IsMatching T → T.card=S.card-1 → RowsWithin S T → boundary y T=z T := by
  let f := rowSetEmbedding S
  let e := rowEmbedding N f
  let w : Finset (Cell S.card N) → ZMod 2 := fun T => z (T.map e)
  have hw : MatchingMarginals S.card N (S.card-1) w := matching_marginals_row_pullback f z hz
  obtain ⟨d,hd,hbd⟩ := matching_moment_filling S.card N hs hN w hw
  refine ⟨push e d, ⟨?_,?_⟩, ?_⟩
  · exact push_supported e (chessboardComplex S.card N) (chessboardComplex m N)
      (fun T hT => (rowEmbedding_matching f T).mpr hT) S.card d hd
  · intro T hT
    have hr : ¬InRange e T := fun h => hT ((rowSetEmbedding_inRange S T).mp h)
    simp [push,hr]
  · intro T hT hcard hrows
    have hr : InRange e T := (rowSetEmbedding_inRange S T).mpr hrows
    let U := T.preimage e e.injective.injOn
    have hmap : U.map e=T := map_preimage e T hr
    have hU : IsMatching U := (rowEmbedding_matching f U).mp (by
      change IsMatching (U.map e)
      rw [hmap]
      exact hT)
    have hUc : U.card=S.card-1 := by
      have h := congrArg Finset.card hmap
      simp only [Finset.card_map] at h
      exact h.trans hcard
    rw [boundary_push,hbd]
    simp only [push,hr,↓reduceIte]
    change momentLayer S.card N (S.card-1) w U=z T
    simp [momentLayer,hU,hUc,w,hmap]

theorem supported_occupied_row_zero (m N k : ℕ) (c : Coeff (Cell m N))
    (hc : Supported (chessboardComplex m N) k c) (T : Finset (Cell m N)) (hT : IsMatching T)
    (i : Fin m) (hi : ¬RowUnused i T) :
    (∑ j : Fin N, if (i,j) ∈ T then 0 else c (insert (i,j) T))=0 := by
  change ¬(∀ x ∈ T, x.1 ≠ i) at hi
  push Not at hi
  obtain ⟨⟨i',j₀⟩,hj₀,he⟩ := hi
  change i'=i at he
  subst i'
  apply Finset.sum_eq_zero
  intro j _
  by_cases hij : (i,j) ∈ T
  · simp [hij]
  · simp only [hij,↓reduceIte]
    apply hc
    left
    intro h
    have he := (matching_insert_occupied T hT i j₀ hj₀ j).mp h
    exact hij (he.symm ▸ hj₀)

theorem supported_row_boundary (m N k : ℕ) (T : Finset (Cell m N)) (hT : IsMatching T)
    (i : Fin m) (hi : RowUnused i T) (c : Coeff (Cell m N))
    (hc : RowSupported (insert i (T.image Prod.fst)) k c) :
    boundary c T=∑ j : Fin N, if ColUnused j T then c (insert (i,j) T) else 0 := by
  change (∑ x : Fin m × Fin N, if x ∈ T then 0 else c (insert x T))=_
  rw [Fintype.sum_prod_type,Finset.sum_eq_single i]
  · apply Finset.sum_congr rfl
    intro j _
    have hij : (i,j) ∉ T := fun h => hi (i,j) h rfl
    simp only [hij,↓reduceIte]
    by_cases hj : ColUnused j T
    · simp [hj]
    · simp only [hj,↓reduceIte]
      apply hc.1
      left
      exact fun h => hj ((matching_insert_unused T hT i hi j).mp h)
  · intro i' _ hne
    by_cases hi' : RowUnused i' T
    · apply Finset.sum_eq_zero
      intro j _
      have hij : (i',j) ∉ T := fun h => hi' (i',j) h rfl
      simp only [hij,↓reduceIte]
      apply hc.2
      intro hrows
      have hmem := hrows (i',j) (Finset.mem_insert_self _ _)
      rcases Finset.mem_insert.mp hmem with he | he
      · exact hne he
      · exact (rowUnused_iff_not_mem_image T i').mp hi' he
    · exact supported_occupied_row_zero m N k c hc.1 T hT i' hi'
  · simp
abbrev RowSet (m s : ℕ) := {S : Finset (Fin m) // S.card=s}

def matchingRowSet {m N s : ℕ} (T : Finset (Cell m N)) (hT : IsMatching T ∧ T.card=s) : RowSet m s :=
  ⟨T.image Prod.fst, by rw [Finset.card_image_of_injOn hT.1.1,hT.2]⟩

def updateMoments (m N s : ℕ) (z : Finset (Cell m N) → ZMod 2)
    (fill : RowSet m s → Coeff (Cell m N)) : Finset (Cell m N) → ZMod 2 :=
  fun T => if h : IsMatching T ∧ T.card=s then fill (matchingRowSet T h) T else z T

theorem updateMoments_old (m N s : ℕ) (z : Finset (Cell m N) → ZMod 2)
    (fill : RowSet m s → Coeff (Cell m N)) (T : Finset (Cell m N)) (hT : T.card<s) :
    updateMoments m N s z fill T=z T := by
  have h : ¬(IsMatching T ∧ T.card=s) := fun h => Nat.ne_of_lt hT h.2
  simp [updateMoments,h]

theorem updateMoments_top (m N s : ℕ) (z : Finset (Cell m N) → ZMod 2)
    (fill : RowSet m s → Coeff (Cell m N)) (T : Finset (Cell m N))
    (hT : IsMatching T ∧ T.card=s) :
    updateMoments m N s z fill T=fill (matchingRowSet T hT) T := by
  simp [updateMoments,hT]

theorem matching_moments_step (m N s : ℕ) (hs : 1≤s) (hN : 2*s-1≤N)
    (z : Finset (Cell m N) → ZMod 2) (hz : MatchingMarginals m N (s-1) z) :
    ∃ w : Finset (Cell m N) → ZMod 2, MatchingMarginals m N s w ∧
      ∀ T, T.card<s → w T=z T := by
  have hfill : ∀ R : RowSet m s, ∃ y : Coeff (Cell m N), RowSupported R.val s y ∧
      ∀ T, IsMatching T → T.card=s-1 → RowsWithin R.val T → boundary y T=z T := by
    intro R
    simpa only [R.property] using rowset_moment_filling m N R.val
      (by simpa only [R.property] using hs) (by simpa only [R.property] using hN) z
      (by simpa only [R.property] using hz)
  choose fill hfill using hfill
  refine ⟨updateMoments m N s z fill, ?_,updateMoments_old m N s z fill⟩
  intro T hT hcard i hi
  by_cases htop : T.card=s-1
  · have hirow : i ∉ T.image Prod.fst := (rowUnused_iff_not_mem_image T i).mp hi
    let R : RowSet m s := ⟨insert i (T.image Prod.fst), by
      rw [Finset.card_insert_of_notMem hirow,Finset.card_image_of_injOn hT.1,htop]
      omega⟩
    have hrows : RowsWithin R.val T := by
      intro x hx
      exact Finset.mem_insert_of_mem (Finset.mem_image.mpr ⟨x,hx,rfl⟩)
    rw [updateMoments_old m N s z fill T hcard]
    calc
      _ = ∑ j : Fin N, if ColUnused j T then fill R (insert (i,j) T) else 0 := by
        apply Finset.sum_congr rfl
        intro j _
        by_cases hj : ColUnused j T
        · simp only [hj,↓reduceIte]
          have hnew : IsMatching (insert (i,j) T) ∧ (insert (i,j) T).card=s := by
            refine ⟨(matching_insert_unused T hT i hi j).mpr hj, ?_⟩
            rw [Finset.card_insert_of_notMem (fun h => hi (i,j) h rfl),htop]
            omega
          rw [updateMoments_top m N s z fill _ hnew]
          congr 1
          apply Subtype.ext
          simp [matchingRowSet,R,Finset.image_insert]
        · simp [hj]
      _ = boundary (fill R) T :=
        (supported_row_boundary m N s T hT i hi (fill R) (hfill R).1).symm
      _ = z T := (hfill R).2 T hT htop hrows
  · have hlo : T.card<s-1 := by omega
    rw [updateMoments_old m N s z fill T hcard]
    calc
      _ = ∑ j : Fin N, if ColUnused j T then z (insert (i,j) T) else 0 := by
        apply Finset.sum_congr rfl
        intro j _
        by_cases hj : ColUnused j T
        · simp only [hj,↓reduceIte]
          exact updateMoments_old m N s z fill _ (lt_of_le_of_lt (Finset.card_insert_le _ _) (by omega))
        · simp [hj]
      _ = z T := hz T hT hlo i hi

theorem matching_moments_extend (m N B : ℕ) (hN : 2*B-1≤N)
    (k : ℕ) (hk : k≤B) (z : Finset (Cell m N) → ZMod 2) (hz : MatchingMarginals m N k z) :
    ∃ w : Finset (Cell m N) → ZMod 2, MatchingMarginals m N B w ∧
      ∀ T, T.card≤k → w T=z T := by
  induction B generalizing k z with
  | zero =>
    have : k=0 := by omega
    subst k
    exact ⟨z,hz,fun _ _ => rfl⟩
  | succ B ih =>
    by_cases he : k=B+1
    · subst k
      exact ⟨z,hz,fun _ _ => rfl⟩
    · obtain ⟨u,hu,heq⟩ := ih (by omega) k (by omega) z hz
      obtain ⟨w,hw,hew⟩ := matching_moments_step m N (B+1) (by omega) hN u (by simpa using hu)
      refine ⟨w,hw,?_⟩
      intro T hT
      rw [hew T (by omega),heq T hT]

theorem matching_moments_normalized (m N B : ℕ) (hN : 2*B-1≤N) :
    ∃ z : Finset (Cell m N) → ZMod 2, MatchingMarginals m N B z ∧ z ∅=1 := by
  have hzero : MatchingMarginals m N 0 (fun _ => 1) := by intro S _ h; omega
  obtain ⟨z,hz,he⟩ := matching_moments_extend m N B hN 0 (by omega) (fun _ => 1) hzero
  exact ⟨z,hz,he ∅ (by simp)⟩
theorem momentFunctional_congr (m N k : ℕ) (z w : Finset (Cell m N) → ZMod 2)
    (hzw : ∀ T, IsMatching T → T.card≤k → z T=w T)
    (P : Poly (ZMod 2) (Cell m N)) (hP : P.totalDegree≤k) :
    momentFunctional m N z P=momentFunctional m N w P := by
  classical
  conv_lhs => arg 2; rw [P.as_sum]
  conv_rhs => arg 2; rw [P.as_sum]
  rw [map_sum,map_sum]
  apply Finset.sum_congr rfl
  intro d hd
  rw [momentFunctional_monomial,momentFunctional_monomial]
  by_cases h : IsMatching d.support
  · simp only [h,↓reduceIte]
    congr 1
    apply hzw d.support h
    have hc : d.support.card≤d.sum (fun _ n => n) := by
      change d.support.card≤∑ x ∈ d.support, d x
      calc
        d.support.card=∑ _x ∈ d.support, 1 := by simp
        _≤∑ x ∈ d.support, d x := Finset.sum_le_sum (fun x hx =>
          Nat.one_le_iff_ne_zero.mpr (Finsupp.mem_support_iff.mp hx))
    exact hc.trans ((MvPolynomial.le_totalDegree hd).trans hP)
  · simp [h]

theorem matching_annihilator_extension (m N B : ℕ) (hN : 1≤N) (hNB : 2*B-1≤N)
    (k : ℕ) (hk : k≤B) (L : Poly (ZMod 2) (Cell m N) →ₗ[ZMod 2] ZMod 2)
    (hL : AnnihilatesNS (functionalUnaryBase m N) k L) :
    ∃ E : Poly (ZMod 2) (Cell m N) →ₗ[ZMod 2] ZMod 2,
      AnnihilatesNS (functionalUnaryBase m N) B E ∧
      ∀ P, P.totalDegree≤k → E P=L P := by
  let z : Finset (Cell m N) → ZMod 2 := fun T => L (supportMonomial T)
  have hz : MatchingMarginals m N k z := annihilates_implies_marginals m N k L hL
  obtain ⟨w,hw,heq⟩ := matching_moments_extend m N B hNB k hk z hz
  refine ⟨momentFunctional m N w,momentFunctional_annihilates m N B hN w hw,?_⟩
  intro P hP
  rw [momentFunctional_congr m N k w z (fun T _ hT => heq T hT) P hP]
  rw [momentFunctional_of_values]
  symm
  apply annihilates_matching_normal m N k L _ P hP
  intro q hq
  apply hL q
  apply nsSpace_mono _ le_rfl hq
  rw [functionalUnaryBase_eq]
  exact Set.subset_union_left

theorem bounded_matching_annihilator_extension (m N B : ℕ) (hN : 1≤N) (hNB : 2*B-1≤N)
    (k : ℕ) (hk : k≤B)
    (L : degreeSpace (K := ZMod 2) (V := Cell m N) k →ₗ[ZMod 2] ZMod 2)
    (hL : BoundedAnnihilator m N k L) :
    ∃ E : degreeSpace (K := ZMod 2) (V := Cell m N) B →ₗ[ZMod 2] ZMod 2,
      BoundedAnnihilator m N B E ∧
      ∀ P : degreeSpace k, E ⟨P.val,P.property.trans hk⟩=L P := by
  obtain ⟨A,hA,ha⟩ := MathResearch.LinearSeparation.annihilator_extension
    (degreeSpace (K := ZMod 2) (V := Cell m N) k) (nsSpace (functionalUnaryBase m N) k) L hL
  obtain ⟨E,hE,he⟩ := matching_annihilator_extension m N B hN hNB k hk A ha
  refine ⟨E.comp (degreeSpace B).subtype,?_,?_⟩
  · intro P hP
    exact hE P.val hP
  · intro P
    exact (he P.val P.property).trans (hA P)

theorem matching_normalized_annihilator (m N B : ℕ) (hN : 1≤N) (hNB : 2*B-1≤N) :
    ∃ L : Poly (ZMod 2) (Cell m N) →ₗ[ZMod 2] ZMod 2,
      AnnihilatesNS (functionalUnaryBase m N) B L ∧ L 1=1 := by
  obtain ⟨z,hz,hconst⟩ := matching_moments_normalized m N B hNB
  exact ⟨momentFunctional m N z,momentFunctional_annihilates m N B hN z hz,
    (momentFunctional_one m N z).trans hconst⟩
end
end MathResearch.PolynomialCalculus
