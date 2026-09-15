/-
Claim: lem:functional-matching-normal-form
Source: https://kbr.is-a.dev/math-research/#lean-functional-matching-normal-form
Scope: Linear matching normal form for binary functional-unary polynomials, with original-degree Boolean/exclusion NS error and exact encoding identification.
Declarations: MathResearch.PolynomialCalculus.matchingNormal_monomial MathResearch.PolynomialCalculus.nonmatching_monomial_ns MathResearch.PolynomialCalculus.matchingNormal_ns MathResearch.PolynomialCalculus.functionalUnaryBase_eq MathResearch.PolynomialCalculus.squarefreeExponent_support MathResearch.PolynomialCalculus.supportMonomial_eq_monomial MathResearch.PolynomialCalculus.matchingNormal_support MathResearch.PolynomialCalculus.matchingNormal_boolean_multiple MathResearch.PolynomialCalculus.matchingNormal_exclusion_multiple MathResearch.PolynomialCalculus.matchingNormal_generator_multiple MathResearch.PolynomialCalculus.matchingNormal_ns_zero MathResearch.PolynomialCalculus.matchingNormal_kernel MathResearch.PolynomialCalculus.matchingNormal_support_mul_X MathResearch.PolynomialCalculus.matching_insert_unused MathResearch.PolynomialCalculus.matching_insert_occupied MathResearch.PolynomialCalculus.matchingNormal_row_unused MathResearch.PolynomialCalculus.matchingNormal_row_occupied MathResearch.PolynomialCalculus.matchingNormal_degree MathResearch.PolynomialCalculus.rowEquation_degree_le MathResearch.PolynomialCalculus.rowEquation_degree MathResearch.PolynomialCalculus.rowEquation_ne_zero
-/
import claims.SquarefreePairDivisibility
import claims.AugmentedChains
import Mathlib.LinearAlgebra.Finsupp.LinearCombination
namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial
open scoped BigOperators Classical

abbrev Cell (m N : ℕ) := Fin m × Fin N

def IsMatching {m N : ℕ} (S : Finset (Cell m N)) : Prop :=
  S ∈ (MathResearch.ThirdParty.Augmented.chessboardComplex m N).faces

def exclusionBase (m N : ℕ) : Set (Poly (ZMod 2) (Cell m N)) :=
  {p | ∃ x y : Cell m N, x ≠ y ∧ (x.1=y.1 ∨ x.2=y.2) ∧ p=X x*X y}

def matchingBase (m N : ℕ) : Set (Poly (ZMod 2) (Cell m N)) :=
  booleanBase ∪ exclusionBase m N

def rowBase (m N : ℕ) : Set (Poly (ZMod 2) (Cell m N)) :=
  {p | ∃ i : Fin m, p=(∑ j : Fin N, X (i,j))-1}

def matchingBasis {m N : ℕ} (d : Cell m N →₀ ℕ) : Poly (ZMod 2) (Cell m N) := by
  classical
  exact if IsMatching d.support then supportMonomial d.support else 0

def matchingNormal (m N : ℕ) : Poly (ZMod 2) (Cell m N) →ₗ[ZMod 2] Poly (ZMod 2) (Cell m N) :=
  (Finsupp.linearCombination (ZMod 2) (matchingBasis (m := m) (N := N))).comp
    (AddMonoidAlgebra.coeffLinearEquiv (ZMod 2)).toLinearMap

theorem matchingNormal_monomial (m N : ℕ) (d : Cell m N →₀ ℕ) (c : ZMod 2) :
    matchingNormal m N (monomial d c) = c • matchingBasis d :=
  Finsupp.linearCombination_single (ZMod 2) c d

private theorem collision_of_not_matching {m N : ℕ} (S : Finset (Cell m N))
    (hS : ¬IsMatching S) :
    ∃ x ∈ S, ∃ y ∈ S, x ≠ y ∧ (x.1=y.1 ∨ x.2=y.2) := by
  change ¬(Set.InjOn Prod.fst (S : Set (Cell m N)) ∧
    Set.InjOn Prod.snd (S : Set (Cell m N))) at hS
  by_cases hr : Set.InjOn Prod.fst (S : Set (Cell m N))
  · have hc : ¬Set.InjOn Prod.snd (S : Set (Cell m N)) := fun hc => hS ⟨hr,hc⟩
    simp only [Set.InjOn] at hc
    push Not at hc
    obtain ⟨x,hx,y,hy,he,hne⟩ := hc
    exact ⟨x,hx,y,hy,hne,Or.inr he⟩
  · simp only [Set.InjOn] at hr
    push Not at hr
    obtain ⟨x,hx,y,hy,he,hne⟩ := hr
    exact ⟨x,hx,y,hy,hne,Or.inl he⟩

theorem nonmatching_monomial_ns {m N : ℕ} (S : Finset (Cell m N)) (hS : ¬IsMatching S) :
    supportMonomial S ∈ nsSpace (matchingBase m N) S.card := by
  obtain ⟨x,hx,y,hy,hxy,hcollision⟩ := collision_of_not_matching S hS
  exact supportMonomial_pair_ns _ S x y hx hy hxy
    (Or.inr ⟨x,y,hxy,hcollision,rfl⟩)

theorem matchingNormal_ns (m N : ℕ) (P : Poly (ZMod 2) (Cell m N)) :
    P-matchingNormal m N P ∈ nsSpace (matchingBase m N) P.totalDegree := by
  classical
  have hbool : P-squarefreePart P ∈ nsSpace (matchingBase m N) P.totalDegree :=
    nsSpace_mono (fun _ h => Or.inl h) le_rfl (squarefreePart_ns P)
  have he : squarefreePart P-matchingNormal m N P =
      ∑ d ∈ P.support, P.coeff d • (supportMonomial d.support-matchingBasis d) := by
    change (∑ d ∈ P.support, P.coeff d • supportMonomial d.support) -
      (∑ d ∈ P.support, P.coeff d • matchingBasis d) = _
    rw [← Finset.sum_sub_distrib]
    apply Finset.sum_congr rfl
    intro d _
    rw [smul_sub]
  have herr : squarefreePart P-matchingNormal m N P ∈ nsSpace (matchingBase m N) P.totalDegree := by
    rw [he]
    apply Submodule.sum_mem
    intro d hd
    apply Submodule.smul_mem
    by_cases hm : IsMatching d.support
    · simp [matchingBasis,hm]
    · simp only [matchingBasis,hm,↓reduceIte,sub_zero]
      have hcard : d.support.card ≤ d.sum (fun _ n => n) := by
        change d.support.card ≤ ∑ i ∈ d.support, d i
        calc
          d.support.card = ∑ _i ∈ d.support, 1 := by simp
          _ ≤ ∑ i ∈ d.support, d i := Finset.sum_le_sum (fun i hi =>
            Nat.one_le_iff_ne_zero.mpr (Finsupp.mem_support_iff.mp hi))
      exact nsSpace_mono (Set.Subset.refl _) (hcard.trans (le_totalDegree hd))
        (nonmatching_monomial_ns d.support hm)
  simpa only [sub_add_sub_cancel] using Submodule.add_mem _ hbool herr
theorem functionalUnaryBase_eq (m N : ℕ) :
    functionalUnaryBase (K := ZMod 2) m N = matchingBase m N ∪ rowBase m N := by
  ext p
  constructor
  · rintro (((hb | hr) | hc) | hr)
    · exact Or.inl (Or.inl hb)
    · exact Or.inr hr
    · obtain ⟨i,i',j,hne,rfl⟩ := hc
      exact Or.inl (Or.inr ⟨(i,j),(i',j),fun h => hne (congrArg Prod.fst h),Or.inr rfl,rfl⟩)
    · obtain ⟨i,j,j',hne,rfl⟩ := hr
      exact Or.inl (Or.inr ⟨(i,j),(i,j'),fun h => hne (congrArg Prod.snd h),Or.inl rfl,rfl⟩)
  · rintro ((hb | hc) | hr)
    · exact Or.inl (Or.inl (Or.inl hb))
    · obtain ⟨⟨i,j⟩,⟨i',j'⟩,hne,hc,rfl⟩ := hc
      rcases hc with hr | hc
      · change i=i' at hr
        subst i'
        exact Or.inr ⟨i,j,j',fun h => hne (Prod.ext rfl h),rfl⟩
      · change j=j' at hc
        subst j'
        exact Or.inl (Or.inr ⟨i,i',j,fun h => hne (Prod.ext h rfl),rfl⟩)
    · exact Or.inl (Or.inl (Or.inr hr))

def squarefreeExponent {V : Type} [DecidableEq V] (S : Finset V) : V →₀ ℕ :=
  Finsupp.indicator S (fun _ _ => 1)

theorem squarefreeExponent_support {V : Type} [DecidableEq V] (S : Finset V) :
    (squarefreeExponent S).support = S := by
  ext i
  by_cases hi : i ∈ S <;> simp [squarefreeExponent,Finsupp.mem_support_iff,Finsupp.indicator_apply,hi]

theorem supportMonomial_eq_monomial {V : Type} [DecidableEq V] (S : Finset V) :
    supportMonomial S = monomial (squarefreeExponent S) (1 : ZMod 2) := by
  simpa [supportMonomial,squarefreeExponent] using
    (prod_X_pow (R := ZMod 2) (fun _ : V => 1) S)

theorem matchingNormal_support (m N : ℕ) (S : Finset (Cell m N)) :
    matchingNormal m N (supportMonomial S) = if IsMatching S then supportMonomial S else 0 := by
  classical
  have h := matchingNormal_monomial m N (squarefreeExponent S) 1
  simp only [matchingBasis,squarefreeExponent_support,one_smul] at h
  rw [← supportMonomial_eq_monomial] at h
  exact h

theorem matchingNormal_boolean_multiple (m N : ℕ) (d : Cell m N →₀ ℕ) (c : ZMod 2)
    (x : Cell m N) :
    matchingNormal m N (monomial d c*(X x^2-X x)) = 0 := by
  classical
  have hx2 : (X x : Poly (ZMod 2) (Cell m N))^2 = monomial (Finsupp.single x 2) 1 := by
    simp [X_pow_eq_monomial]
  have hx1 : (X x : Poly (ZMod 2) (Cell m N)) = monomial (Finsupp.single x 1) 1 := rfl
  rw [mul_sub,map_sub,hx2,hx1,monomial_mul_monomial,monomial_mul_monomial,
    matchingNormal_monomial,matchingNormal_monomial]
  simp [matchingBasis,Finsupp.support_add_eq_union]

theorem matchingNormal_exclusion_multiple (m N : ℕ) (d : Cell m N →₀ ℕ) (c : ZMod 2)
    (x y : Cell m N) (hxy : x ≠ y) (hc : x.1=y.1 ∨ x.2=y.2) :
    matchingNormal m N (monomial d c*(X x*X y)) = 0 := by
  classical
  have he : monomial d c*((X x : Poly (ZMod 2) (Cell m N))*X y) =
      monomial (d+Finsupp.single x 1+Finsupp.single y 1) c := by
    change monomial d c*(monomial (Finsupp.single x 1) 1*monomial (Finsupp.single y 1) 1) = _
    rw [monomial_mul_monomial,monomial_mul_monomial]
    simp [add_assoc]
  rw [he,matchingNormal_monomial]
  have hm : ¬IsMatching (d+Finsupp.single x 1+Finsupp.single y 1).support := by
    intro h
    have hx : x ∈ (d+Finsupp.single x 1+Finsupp.single y 1).support := by
      simp [Finsupp.support_add_eq_union]
    have hy : y ∈ (d+Finsupp.single x 1+Finsupp.single y 1).support := by
      simp [Finsupp.support_add_eq_union]
    exact hxy (hc.elim (fun he => h.1 hx hy he) (fun he => h.2 hx hy he))
  simp [matchingBasis,hm]

theorem matchingNormal_generator_multiple (m N : ℕ) (q f : Poly (ZMod 2) (Cell m N))
    (hf : f ∈ matchingBase m N) : matchingNormal m N (q*f) = 0 := by
  classical
  have heq : q*f = ∑ d ∈ q.support, monomial d (q.coeff d)*f := by
    conv_lhs => lhs; rw [q.as_sum]
    rw [Finset.sum_mul]
  rw [heq,map_sum]
  apply Finset.sum_eq_zero
  intro d _
  rcases hf with hb | he
  · obtain ⟨x,rfl⟩ := hb
    exact matchingNormal_boolean_multiple m N d (q.coeff d) x
  · obtain ⟨x,y,hxy,hc,rfl⟩ := he
    exact matchingNormal_exclusion_multiple m N d (q.coeff d) x y hxy hc

theorem matchingNormal_ns_zero (m N B : ℕ) (P : Poly (ZMod 2) (Cell m N))
    (hP : P ∈ nsSpace (matchingBase m N) B) : matchingNormal m N P = 0 := by
  induction hP using Submodule.span_induction with
  | mem p hp =>
    obtain ⟨f,hf,q,rfl,_⟩ := hp
    exact matchingNormal_generator_multiple m N q f hf
  | zero => exact map_zero _
  | add p q _ _ hp hq => rw [map_add,hp,hq,add_zero]
  | smul c p _ hp => rw [map_smul,hp,smul_zero]

theorem matchingNormal_kernel (m N B : ℕ) (P : Poly (ZMod 2) (Cell m N))
    (hP : P.totalDegree ≤ B) :
    P ∈ nsSpace (matchingBase m N) B ↔ matchingNormal m N P = 0 := by
  constructor
  · exact matchingNormal_ns_zero m N B P
  · intro h
    simpa [h] using nsSpace_mono (Set.Subset.refl _) hP (matchingNormal_ns m N P)
theorem matchingNormal_support_mul_X (m N : ℕ) (S : Finset (Cell m N)) (x : Cell m N) :
    matchingNormal m N (supportMonomial S * X x) =
      if IsMatching (insert x S) then supportMonomial (insert x S) else 0 := by
  have hx : (X x : Poly (ZMod 2) (Cell m N)) = monomial (Finsupp.single x 1) 1 := rfl
  rw [supportMonomial_eq_monomial,hx,monomial_mul_monomial,matchingNormal_monomial]
  simp [matchingBasis,Finsupp.support_add_eq_union,squarefreeExponent_support,Finset.union_singleton]

def RowUnused {m N : ℕ} (i : Fin m) (S : Finset (Cell m N)) : Prop :=
  ∀ x ∈ S, x.1 ≠ i

def ColUnused {m N : ℕ} (j : Fin N) (S : Finset (Cell m N)) : Prop :=
  ∀ x ∈ S, x.2 ≠ j

theorem matching_insert_unused {m N : ℕ} (S : Finset (Cell m N)) (hS : IsMatching S)
    (i : Fin m) (hi : RowUnused i S) (j : Fin N) :
    IsMatching (insert (i,j) S) ↔ ColUnused j S := by
  constructor
  · intro h x hx he
    have hx' := h.2 (Finset.mem_insert_of_mem hx) (Finset.mem_insert_self _ _) he
    exact hi x hx (congrArg Prod.fst hx')
  · intro hj
    constructor
    · intro x hx y hy he
      rcases Finset.mem_insert.mp hx with rfl | hx
      · rcases Finset.mem_insert.mp hy with rfl | hy
        · rfl
        · exact False.elim (hi y hy he.symm)
      · rcases Finset.mem_insert.mp hy with rfl | hy
        · exact False.elim (hi x hx he)
        · exact hS.1 hx hy he
    · intro x hx y hy he
      rcases Finset.mem_insert.mp hx with rfl | hx
      · rcases Finset.mem_insert.mp hy with rfl | hy
        · rfl
        · exact False.elim (hj y hy he.symm)
      · rcases Finset.mem_insert.mp hy with rfl | hy
        · exact False.elim (hj x hx he)
        · exact hS.2 hx hy he

theorem matching_insert_occupied {m N : ℕ} (S : Finset (Cell m N)) (hS : IsMatching S)
    (i : Fin m) (j₀ : Fin N) (hj₀ : (i,j₀) ∈ S) (j : Fin N) :
    IsMatching (insert (i,j) S) ↔ j=j₀ := by
  constructor
  · intro h
    exact congrArg Prod.snd (h.1 (Finset.mem_insert_self _ _) (Finset.mem_insert_of_mem hj₀) rfl)
  · rintro rfl
    simpa [Finset.insert_eq_of_mem hj₀] using hS

def rowEquation (m N : ℕ) (i : Fin m) : Poly (ZMod 2) (Cell m N) :=
  (∑ j : Fin N, X (i,j))-1

theorem matchingNormal_row_unused (m N : ℕ) (S : Finset (Cell m N)) (hS : IsMatching S)
    (i : Fin m) (hi : RowUnused i S) :
    matchingNormal m N (supportMonomial S * rowEquation m N i) =
      (∑ j : Fin N, if ColUnused j S then supportMonomial (insert (i,j) S) else 0)-supportMonomial S := by
  rw [rowEquation,mul_sub,Finset.mul_sum,mul_one,map_sub,map_sum,matchingNormal_support]
  simp only [hS,↓reduceIte]
  congr 1
  apply Finset.sum_congr rfl
  intro j _
  rw [matchingNormal_support_mul_X,matching_insert_unused S hS i hi j]

theorem matchingNormal_row_occupied (m N : ℕ) (S : Finset (Cell m N)) (hS : IsMatching S)
    (i : Fin m) (hi : ¬RowUnused i S) :
    matchingNormal m N (supportMonomial S * rowEquation m N i) = 0 := by
  change ¬(∀ x ∈ S, x.1 ≠ i) at hi
  push Not at hi
  obtain ⟨⟨i',j₀⟩,hj₀,he⟩ := hi
  change i'=i at he
  subst i'
  rw [rowEquation,mul_sub,Finset.mul_sum,mul_one,map_sub,map_sum,matchingNormal_support]
  simp only [hS,↓reduceIte]
  have heq : (∑ j : Fin N, matchingNormal m N (supportMonomial S*X (i,j))) = supportMonomial S := by
    calc
      _ = ∑ j : Fin N, if j=j₀ then supportMonomial (insert (i,j) S) else 0 := by
        apply Finset.sum_congr rfl
        intro j _
        rw [matchingNormal_support_mul_X,matching_insert_occupied S hS i j₀ hj₀ j]
        by_cases h : j=j₀ <;> simp [h]
      _ = supportMonomial S := by simp [Finset.insert_eq_of_mem hj₀]
  rw [heq,sub_self]
theorem matchingNormal_degree (m N : ℕ) (P : Poly (ZMod 2) (Cell m N)) :
    (matchingNormal m N P).totalDegree ≤ P.totalDegree := by
  change (∑ d ∈ P.support, P.coeff d • matchingBasis d).totalDegree ≤ _
  apply totalDegree_finsetSum_le
  intro d hd
  apply (totalDegree_smul_le _ _).trans
  by_cases h : IsMatching d.support
  · simp only [matchingBasis,h,↓reduceIte]
    apply (supportMonomial_degree _).trans
    have hcard : d.support.card ≤ d.sum (fun _ n => n) := by
      change d.support.card ≤ ∑ i ∈ d.support, d i
      calc
        d.support.card = ∑ _i ∈ d.support, 1 := by simp
        _ ≤ ∑ i ∈ d.support, d i := Finset.sum_le_sum (fun i hi =>
          Nat.one_le_iff_ne_zero.mpr (Finsupp.mem_support_iff.mp hi))
    exact hcard.trans (le_totalDegree hd)
  · simp [matchingBasis,h]

theorem rowEquation_degree_le (m N : ℕ) (i : Fin m) :
    (rowEquation m N i).totalDegree ≤ 1 := by
  apply (totalDegree_sub _ _).trans
  apply max_le
  · apply totalDegree_finsetSum_le
    intro j _
    simp
  · simp

theorem rowEquation_degree (m N : ℕ) (hN : 1 ≤ N) (i : Fin m) :
    (rowEquation m N i).totalDegree = 1 := by
  apply Nat.le_antisymm (rowEquation_degree_le m N i)
  let j : Fin N := ⟨0,hN⟩
  have hc : (rowEquation m N i).coeff (Finsupp.single (i,j) 1) = 1 := by
    have he (x : Fin N) : Finsupp.single (i,x) (1 : ℕ) = Finsupp.single (i,j) 1 ↔ x=j := by
      constructor
      · intro h
        exact congrArg Prod.snd (Finsupp.single_left_injective (by decide : (1 : ℕ) ≠ 0) h)
      · rintro rfl; rfl
    have hz : (0 : Cell m N →₀ ℕ) ≠ Finsupp.single (i,j) 1 := by
      intro h
      have := congrArg (fun d : Cell m N →₀ ℕ => d (i,j)) h
      simp at this
    simp [rowEquation,coeff_X,coeff_one,he,hz]
  have hs : Finsupp.single (i,j) 1 ∈ (rowEquation m N i).support := by
    exact mem_support_iff.mpr (by rw [hc]; exact one_ne_zero)
  simpa using le_totalDegree hs

theorem rowEquation_ne_zero (m N : ℕ) (hN : 1 ≤ N) (i : Fin m) : rowEquation m N i ≠ 0 := by
  intro h
  have hd := rowEquation_degree m N hN i
  rw [h,totalDegree_zero] at hd
  omega
end
end MathResearch.PolynomialCalculus
