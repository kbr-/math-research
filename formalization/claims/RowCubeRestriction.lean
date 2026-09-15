/-
Claim: lem:row-cube-residual-restriction
Source: https://kbr.is-a.dev/math-research/#lean-row-cube-residual-restriction
Scope: Concrete selected-row one-hot cube restrictions send every ordinary functional-unary generator to zero or a fixed residual generator; exact decoder coordinate compatibility and bounded NS transport.
Declarations: MathResearch.PolynomialCalculus.rowCube_generators MathResearch.PolynomialCalculus.rowCubeDifference_degree MathResearch.PolynomialCalculus.rowCubeDifference_ns MathResearch.PolynomialCalculus.coordinateRowCube_cols_card MathResearch.PolynomialCalculus.rowCube_decoder_selected MathResearch.PolynomialCalculus.rowCube_decoder_outside MathResearch.PolynomialCalculus.rowCube_decoder_comp
-/
import claims.BinaryCubeDegreeDrop
import claims.DisjointCoordinatePairs
import claims.MatchingFiltration
namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial
open scoped BigOperators Classical

structure RowCubeData (m N : ℕ) where
  rows : Finset (Fin m)
  cols : Finset (Fin N)
  point : rows → ZMod 2 → Fin N
  point_mem : ∀ i b, point i b ∈ cols
  point_injective : ∀ e : rows → ZMod 2, Function.Injective (fun i => point i (e i))

def complementEquiv {n : ℕ} (S : Finset (Fin n)) : {j : Fin n // j ∉ S} ≃ Fin (n-S.card) :=
  Fintype.equivFinOfCardEq (by simp [Fintype.card_subtype_compl])

theorem complement_sum {n : ℕ} (S : Finset (Fin n)) {A : Type} [AddCommMonoid A]
    (f : Fin (n-S.card) → A) :
    (∑ j : Fin n, if h : j ∉ S then f (complementEquiv S ⟨j,h⟩) else 0)=∑ j, f j := by
  calc
    _ = ∑ j : {j : Fin n // j ∉ S}, f (complementEquiv S j) := by
      have h := Fintype.sum_subtype_add_sum_subtype (fun j : Fin n => j ∉ S)
        (fun j => if h : j ∉ S then f (complementEquiv S ⟨j,h⟩) else 0)
      have hleft : (∑ j : {j : Fin n // j ∉ S},
          if h : j.val ∉ S then f (complementEquiv S ⟨j.val,h⟩) else 0)=
          ∑ j : {j : Fin n // j ∉ S}, f (complementEquiv S j) := by
        apply Finset.sum_congr rfl
        intro j _
        simp [j.property]
      have hright : (∑ j : {j : Fin n // ¬j ∉ S},
          if h : j.val ∉ S then f (complementEquiv S ⟨j.val,h⟩) else 0)=0 := by
        apply Finset.sum_eq_zero
        intro j _
        simp [j.property]
      rw [hleft,hright,add_zero] at h
      exact h.symm
    _ = ∑ j, f j := Fintype.sum_equiv (complementEquiv S) _ _ (fun _ => rfl)

abbrev RowCubeResidual {m N : ℕ} (D : RowCubeData m N) := Cell (m-D.rows.card) (N-D.cols.card)

def rowCubeTag {m N : ℕ} (D : RowCubeData m N) (v : Cell m N) : Option D.rows :=
  if h : v.1 ∈ D.rows then some ⟨v.1,h⟩ else none

def rowCubeFree {m N : ℕ} (D : RowCubeData m N) (v : Cell m N) : Poly (ZMod 2) (RowCubeResidual D) :=
  if hi : v.1 ∉ D.rows then
    if hj : v.2 ∉ D.cols then X (complementEquiv D.rows ⟨v.1,hi⟩,complementEquiv D.cols ⟨v.2,hj⟩) else 0
  else 0

def rowCubeScalar {m N : ℕ} (D : RowCubeData m N) (v : Cell m N) (b : ZMod 2) : ZMod 2 :=
  if hi : v.1 ∈ D.rows then if v.2=D.point ⟨v.1,hi⟩ b then 1 else 0 else 0

def rowCubeInput {m N : ℕ} (D : RowCubeData m N) (e : D.rows → ZMod 2) :
    Cell m N → Poly (ZMod 2) (RowCubeResidual D) :=
  cubeInput (rowCubeTag D) (rowCubeFree D) (rowCubeScalar D) e

def rowCubeMap {m N : ℕ} (D : RowCubeData m N) (e : D.rows → ZMod 2) :
    Poly (ZMod 2) (Cell m N) →ₐ[ZMod 2] Poly (ZMod 2) (RowCubeResidual D) := aeval (rowCubeInput D e)

def rowCubeDifference {m N : ℕ} (D : RowCubeData m N) :
    Poly (ZMod 2) (Cell m N) →ₗ[ZMod 2] Poly (ZMod 2) (RowCubeResidual D) :=
  cubeDifference (rowCubeTag D) (rowCubeFree D) (rowCubeScalar D)

theorem rowCubeInput_selected {m N : ℕ} (D : RowCubeData m N) (e : D.rows → ZMod 2)
    (i : D.rows) (j : Fin N) :
    rowCubeInput D e (i.val,j)=C (if j=D.point i (e i) then 1 else 0) := by
  simp [rowCubeInput,cubeInput,rowCubeTag,rowCubeScalar,i.property]

theorem rowCubeInput_outside {m N : ℕ} (D : RowCubeData m N) (e : D.rows → ZMod 2)
    (i : Fin m) (hi : i ∉ D.rows) (j : Fin N) :
    rowCubeInput D e (i,j)=
      if hj : j ∉ D.cols then X (complementEquiv D.rows ⟨i,hi⟩,complementEquiv D.cols ⟨j,hj⟩) else 0 := by
  simp [rowCubeInput,cubeInput,rowCubeTag,rowCubeFree,hi]

theorem rowCubeInput_free_degree {m N : ℕ} (D : RowCubeData m N) (v : Cell m N) :
    (rowCubeFree D v).totalDegree ≤ 1 := by
  unfold rowCubeFree
  split_ifs <;> simp

theorem rowCubeMap_X {m N : ℕ} (D : RowCubeData m N) (e : D.rows → ZMod 2) (v : Cell m N) :
    rowCubeMap D e (X v)=rowCubeInput D e v := aeval_X _ _

theorem rowCubeMap_row_selected {m N : ℕ} (D : RowCubeData m N) (e : D.rows → ZMod 2) (i : D.rows) :
    rowCubeMap D e (rowEquation m N i.val)=0 := by
  rw [rowEquation,map_sub,map_sum,map_one]
  simp_rw [rowCubeMap_X,rowCubeInput_selected]
  simp

theorem rowCubeMap_row_outside {m N : ℕ} (D : RowCubeData m N) (e : D.rows → ZMod 2)
    (i : Fin m) (hi : i ∉ D.rows) :
    rowCubeMap D e (rowEquation m N i)=rowEquation (m-D.rows.card) (N-D.cols.card) (complementEquiv D.rows ⟨i,hi⟩) := by
  rw [rowEquation,rowEquation,map_sub,map_sum,map_one]
  simp_rw [rowCubeMap_X,rowCubeInput_outside D e i hi]
  congr 1
  exact complement_sum D.cols (fun j => (X (complementEquiv D.rows ⟨i,hi⟩,j) : Poly (ZMod 2) (RowCubeResidual D)))
theorem rowCube_boolean_image {m N : ℕ} (D : RowCubeData m N) (v : Cell m N) :
    ∃ r : Poly (ZMod 2) (RowCubeResidual D), (r=0 ∨ r ∈ booleanBase) ∧
      ∀ e : D.rows → ZMod 2, rowCubeMap D e (X v^2-X v)=r := by
  rcases v with ⟨i,j⟩
  by_cases hi : i ∈ D.rows
  · refine ⟨0,Or.inl rfl,?_⟩
    intro e
    rw [map_sub,map_pow,rowCubeMap_X,rowCubeInput_selected D e ⟨i,hi⟩ j]
    split_ifs <;> simp
  · by_cases hj : j ∉ D.cols
    · let v' : RowCubeResidual D := (complementEquiv D.rows ⟨i,hi⟩,complementEquiv D.cols ⟨j,hj⟩)
      refine ⟨X v'^2-X v',Or.inr ⟨v',rfl⟩,?_⟩
      intro e
      rw [map_sub,map_pow,rowCubeMap_X,rowCubeInput_outside D e i hi j]
      simp [hj,v']
    · refine ⟨0,Or.inl rfl,?_⟩
      intro e
      rw [map_sub,map_pow,rowCubeMap_X,rowCubeInput_outside D e i hi j]
      simp [hj]

theorem rowCube_selected_collision {m N : ℕ} (D : RowCubeData m N) (e : D.rows → ZMod 2)
    (x y : Cell m N) (hx : x.1 ∈ D.rows) (hxy : x≠y) (hc : x.1=y.1 ∨ x.2=y.2) :
    rowCubeInput D e x*rowCubeInput D e y=0 := by
  rcases x with ⟨i,j⟩
  rcases y with ⟨i',j'⟩
  by_cases hy : i' ∈ D.rows
  · rw [rowCubeInput_selected D e ⟨i,hx⟩ j,rowCubeInput_selected D e ⟨i',hy⟩ j']
    by_cases hcol : j=D.point ⟨i,hx⟩ (e ⟨i,hx⟩)
    · by_cases hcol' : j'=D.point ⟨i',hy⟩ (e ⟨i',hy⟩)
      · have he : (⟨i,hx⟩ : D.rows)=⟨i',hy⟩ := by
          rcases hc with hr | hc
          · exact Subtype.ext hr
          · exact D.point_injective e (hcol.symm.trans (hc.trans hcol'))
        have hp := congrArg (fun r : D.rows => D.point r (e r)) he
        exact False.elim (hxy (Prod.ext (congrArg Subtype.val he) (hcol.trans (hp.trans hcol'.symm))))
      · simp [hcol']
    · simp [hcol]
  · rcases hc with hr | hc
    · change i=i' at hr
      exact False.elim (hy (hr ▸ hx))
    · change j=j' at hc
      subst j'
      rw [rowCubeInput_selected D e ⟨i,hx⟩ j,rowCubeInput_outside D e i' hy j]
      by_cases hj : j ∉ D.cols
      · have hcol : j≠D.point ⟨i,hx⟩ (e ⟨i,hx⟩) := fun h => hj (h.symm ▸ D.point_mem ⟨i,hx⟩ (e ⟨i,hx⟩))
        simp [hcol]
      · simp [hj]

theorem rowCube_exclusion_image {m N : ℕ} (D : RowCubeData m N) (x y : Cell m N)
    (hxy : x≠y) (hc : x.1=y.1 ∨ x.2=y.2) :
    ∃ r : Poly (ZMod 2) (RowCubeResidual D),
      (r=0 ∨ r ∈ exclusionBase (m-D.rows.card) (N-D.cols.card)) ∧
      ∀ e : D.rows → ZMod 2, rowCubeMap D e (X x*X y)=r := by
  by_cases hx : x.1 ∈ D.rows
  · refine ⟨0,Or.inl rfl,?_⟩
    intro e
    rw [map_mul,rowCubeMap_X,rowCubeMap_X]
    exact rowCube_selected_collision D e x y hx hxy hc
  · by_cases hy : y.1 ∈ D.rows
    · refine ⟨0,Or.inl rfl,?_⟩
      intro e
      rw [map_mul,rowCubeMap_X,rowCubeMap_X,mul_comm]
      exact rowCube_selected_collision D e y x hy (Ne.symm hxy) (hc.elim (fun h => Or.inl h.symm) (fun h => Or.inr h.symm))
    · by_cases hxcol : x.2 ∉ D.cols
      · by_cases hycol : y.2 ∉ D.cols
        · let x' : RowCubeResidual D := (complementEquiv D.rows ⟨x.1,hx⟩,complementEquiv D.cols ⟨x.2,hxcol⟩)
          let y' : RowCubeResidual D := (complementEquiv D.rows ⟨y.1,hy⟩,complementEquiv D.cols ⟨y.2,hycol⟩)
          have hne : x'≠y' := by
            intro h
            apply hxy
            apply Prod.ext
            · exact congrArg Subtype.val ((complementEquiv D.rows).injective (congrArg (fun z : RowCubeResidual D => z.1) h))
            · exact congrArg Subtype.val ((complementEquiv D.cols).injective (congrArg (fun z : RowCubeResidual D => z.2) h))
          have hc' : x'.1=y'.1 ∨ x'.2=y'.2 := by
            rcases hc with h | h
            · exact Or.inl (congrArg (complementEquiv D.rows) (Subtype.ext h))
            · exact Or.inr (congrArg (complementEquiv D.cols) (Subtype.ext h))
          refine ⟨X x'*X y',Or.inr ⟨x',y',hne,hc',rfl⟩,?_⟩
          intro e
          rw [map_mul,rowCubeMap_X,rowCubeMap_X,rowCubeInput_outside D e x.1 hx x.2,rowCubeInput_outside D e y.1 hy y.2]
          simp [hxcol,hycol,x',y']
        · refine ⟨0,Or.inl rfl,?_⟩
          intro e
          rw [map_mul,rowCubeMap_X,rowCubeMap_X,rowCubeInput_outside D e y.1 hy y.2]
          simp [hycol]
      · refine ⟨0,Or.inl rfl,?_⟩
        intro e
        rw [map_mul,rowCubeMap_X,rowCubeMap_X,rowCubeInput_outside D e x.1 hx x.2]
        simp [hxcol]
theorem rowCube_generators {m N : ℕ} (D : RowCubeData m N)
    (f : Poly (ZMod 2) (Cell m N)) (hf : f ∈ functionalUnaryBase m N) :
    ∃ r : Poly (ZMod 2) (RowCubeResidual D),
      (r=0 ∨ r ∈ functionalUnaryBase (m-D.rows.card) (N-D.cols.card)) ∧
      ∀ e : D.rows → ZMod 2, rowCubeMap D e f=r := by
  rw [functionalUnaryBase_eq] at hf
  rcases hf with (hb | he) | hr
  · obtain ⟨v,rfl⟩ := hb
    obtain ⟨r,hr,hmap⟩ := rowCube_boolean_image D v
    refine ⟨r,?_,hmap⟩
    rcases hr with hr | hr
    · exact Or.inl hr
    · exact Or.inr (Or.inl (Or.inl (Or.inl hr)))
  · obtain ⟨x,y,hxy,hc,rfl⟩ := he
    obtain ⟨r,hr,hmap⟩ := rowCube_exclusion_image D x y hxy hc
    refine ⟨r,?_,hmap⟩
    rcases hr with hr | hr
    · exact Or.inl hr
    · right
      rw [functionalUnaryBase_eq]
      exact Or.inl (Or.inr hr)
  · obtain ⟨i,rfl⟩ := hr
    by_cases hi : i ∈ D.rows
    · exact ⟨0,Or.inl rfl,fun e => rowCubeMap_row_selected D e ⟨i,hi⟩⟩
    · refine ⟨rowEquation (m-D.rows.card) (N-D.cols.card) (complementEquiv D.rows ⟨i,hi⟩),?_,?_⟩
      · right
        rw [functionalUnaryBase_eq]
        exact Or.inr ⟨_,rfl⟩
      · exact fun e => rowCubeMap_row_outside D e i hi

theorem rowCubeDifference_apply {m N : ℕ} (D : RowCubeData m N) (P : Poly (ZMod 2) (Cell m N)) :
    rowCubeDifference D P=∑ e : D.rows → ZMod 2, rowCubeMap D e P := by
  classical
  unfold rowCubeDifference rowCubeMap rowCubeInput
  convert cubeDifference_apply (rowCubeTag D) (rowCubeFree D) (rowCubeScalar D) P using 1
  congr 1
  ext e
  simp

theorem rowCubeDifference_degree {m N : ℕ} (D : RowCubeData m N) (P : Poly (ZMod 2) (Cell m N)) :
    (rowCubeDifference D P).totalDegree ≤ P.totalDegree-D.rows.card := by
  simpa only [rowCubeDifference,Fintype.card_coe] using
    cubeDifference_degree (rowCubeTag D) (rowCubeFree D) (fun v _ => rowCubeInput_free_degree D v)
      (rowCubeScalar D) P

theorem rowCubeDifference_ns {m N : ℕ} (D : RowCubeData m N) (B : ℕ)
    (P : Poly (ZMod 2) (Cell m N)) (hP : P ∈ nsSpace (functionalUnaryBase m N) B) :
    rowCubeDifference D P ∈ nsSpace (functionalUnaryBase (m-D.rows.card) (N-D.cols.card)) (B-D.rows.card) := by
  have h := cubeDifference_ns (rowCubeTag D) (rowCubeFree D) (fun v _ => rowCubeInput_free_degree D v)
    (rowCubeScalar D) (functionalUnaryBase m N) (functionalUnaryBase (m-D.rows.card) (N-D.cols.card))
    (fun f hf => rowCube_generators D f hf) B P hP
  simpa only [rowCubeDifference,Fintype.card_coe] using h

def coordinateRowCube (m ℓ : ℕ) (S : Finset (Fin m)) (d : Fin m → Fin ℓ)
    (c : Fin m → Fin (2^ℓ)) (hc : CoordinatePairsDisjoint ℓ S d c) : RowCubeData m (2^ℓ) := by
  let point : S → ZMod 2 → Fin (2^ℓ) := fun i b => if b=0 then c i.val else flipColumn ℓ (d i.val) (c i.val)
  have hp : ∀ i b, point i b ∈ coordinatePair ℓ (d i.val) (c i.val) := by
    intro i b
    dsimp [point]
    split_ifs <;> simp [coordinatePair]
  refine ⟨S,coordinatePairs ℓ S d c,point,?_,?_⟩
  · intro i b
    exact Finset.mem_biUnion.mpr ⟨i.val,i.property,hp i b⟩
  · intro e i j h
    apply Subtype.ext
    by_contra hij
    have hd := hc i.val i.property j.val j.property hij
    exact Finset.disjoint_left.mp hd (hp i (e i)) (by simpa only [h] using hp j (e j))

theorem coordinateRowCube_cols_card (m ℓ : ℕ) (S : Finset (Fin m)) (d : Fin m → Fin ℓ)
    (c : Fin m → Fin (2^ℓ)) (hc : CoordinatePairsDisjoint ℓ S d c) :
    (coordinateRowCube m ℓ S d c hc).cols.card=2*S.card := coordinatePairs_card ℓ S d c hc
theorem rowCube_decoder_selected {m ℓ : ℕ} (D : RowCubeData m (2^ℓ))
    (e : D.rows → ZMod 2) (i : D.rows) (t : Fin ℓ) :
    rowCubeMap D e (decoderInput m ℓ (i.val,t)) = C (bitLabelEquiv ℓ (D.point i (e i)) t) := by
  simp only [decoderInput,map_sum,apply_ite,map_zero,rowCubeMap_X,rowCubeInput_selected]
  rw [Finset.sum_eq_single (D.point i (e i))]
  · simp only [ite_true]
    generalize bitLabelEquiv ℓ (D.point i (e i)) t = b
    fin_cases b
    · change (if (0 : ZMod 2)=1 then (1 : Poly (ZMod 2) (RowCubeResidual D)) else 0)=C (0 : ZMod 2)
      simp
    · change (if (1 : ZMod 2)=1 then (1 : Poly (ZMod 2) (RowCubeResidual D)) else 0)=C (1 : ZMod 2)
      simp
  · intro j _ hj
    simp [hj]
  · simp

theorem rowCube_decoder_outside {m ℓ : ℕ} (D : RowCubeData m (2^ℓ))
    (e e' : D.rows → ZMod 2) (i : Fin m) (hi : i ∉ D.rows) (t : Fin ℓ) :
    rowCubeMap D e (decoderInput m ℓ (i,t)) = rowCubeMap D e' (decoderInput m ℓ (i,t)) := by
  simp only [decoderInput,map_sum,apply_ite,map_zero,rowCubeMap_X,rowCubeInput_outside D e i hi,
    rowCubeInput_outside D e' i hi]

theorem rowCube_decoder_comp {m ℓ : ℕ} (D : RowCubeData m (2^ℓ))
    (e : D.rows → ZMod 2) (P : Poly (ZMod 2) (Fin m × Fin ℓ)) :
    rowCubeMap D e (compactDecoder m ℓ P) =
      aeval (fun v => rowCubeMap D e (decoderInput m ℓ v)) P := by
  have h : (rowCubeMap D e).comp (compactDecoder m ℓ) =
      aeval (fun v => rowCubeMap D e (decoderInput m ℓ v)) := by
    apply MvPolynomial.algHom_ext
    intro v
    simp [compactDecoder]
  exact DFunLike.congr_fun h P

end
end MathResearch.PolynomialCalculus
