/-
Claim: lem:binary-cube-degree-drop
Source: https://kbr.is-a.dev/math-research/#lean-binary-cube-degree-drop
Scope: Explicit binary cube sums of constant substitutions in selected variable groups lower ordinary total degree by the number of groups and transport bounded ordinary NS certificates when generator images are fixed across the cube.
Declarations: MathResearch.PolynomialCalculus.flipChoice_involutive MathResearch.PolynomialCalculus.flipChoice_ne MathResearch.PolynomialCalculus.cube_sum_cancel MathResearch.PolynomialCalculus.cubeDifference_apply MathResearch.PolynomialCalculus.cubeDifference_monomial_missing MathResearch.PolynomialCalculus.cube_degree_partition MathResearch.PolynomialCalculus.cube_inside_degree_bound MathResearch.PolynomialCalculus.cubeInput_monomial_degree MathResearch.PolynomialCalculus.cubeDifference_monomial_degree MathResearch.PolynomialCalculus.cubeDifference_degree MathResearch.PolynomialCalculus.cubeDifference_fixed_factor MathResearch.PolynomialCalculus.cubeDifference_ns MathResearch.PolynomialCalculus.cubeDifference_annihilates MathResearch.PolynomialCalculus.cubeDifference_low_degree
-/
import claims.PolynomialCalculusSubstitution
namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial
open scoped BigOperators Classical
variable {I V W : Type} [Fintype I]

def flipChoice (i : I) (e : I → ZMod 2) : I → ZMod 2 := Function.update e i (e i+1)

omit [Fintype I] in
theorem flipChoice_involutive (i : I) : Function.Involutive (flipChoice i) := by
  intro e
  funext j
  by_cases hj : j=i
  · subst j
    simp [flipChoice,add_assoc,ZModModule.add_self]
  · simp [flipChoice,hj]

omit [Fintype I] in
theorem flipChoice_ne (i : I) (e : I → ZMod 2) : flipChoice i e ≠ e := by
  intro h
  have hh := congrFun h i
  simp only [flipChoice,Function.update_self] at hh
  have h1 : (1 : ZMod 2)=0 := add_left_cancel (hh.trans (add_zero (e i)).symm)
  exact one_ne_zero h1

theorem cube_sum_cancel {A : Type} [AddCommGroup A] [Module (ZMod 2) A]
    (i : I) (f : (I → ZMod 2) → A) (hf : ∀ e, f (flipChoice i e)=f e) :
    (∑ e : I → ZMod 2, f e)=0 := by
  apply Finset.sum_ninvolution (flipChoice i)
  · intro e
    rw [hf,ZModModule.add_self]
  · intro e _
    exact flipChoice_ne i e
  · intro e
    exact Finset.mem_univ _
  · exact flipChoice_involutive i

def cubeInput (tag : V → Option I) (g : V → Poly (ZMod 2) W)
    (a : V → ZMod 2 → ZMod 2) (e : I → ZMod 2) (v : V) : Poly (ZMod 2) W :=
  match tag v with
  | none => g v
  | some i => C (a v (e i))

def cubeDifference (tag : V → Option I) (g : V → Poly (ZMod 2) W)
    (a : V → ZMod 2 → ZMod 2) : Poly (ZMod 2) V →ₗ[ZMod 2] Poly (ZMod 2) W :=
  ∑ e : I → ZMod 2, (aeval (cubeInput tag g a e)).toLinearMap

theorem cubeDifference_apply (tag : V → Option I) (g : V → Poly (ZMod 2) W)
    (a : V → ZMod 2 → ZMod 2) (P : Poly (ZMod 2) V) :
    cubeDifference tag g a P=∑ e : I → ZMod 2, aeval (cubeInput tag g a e) P := by
  simp [cubeDifference]

omit [Fintype I] in
private theorem cubeInput_flip (tag : V → Option I) (g : V → Poly (ZMod 2) W)
    (a : V → ZMod 2 → ZMod 2) (i : I) (e : I → ZMod 2) (v : V) (hv : tag v ≠ some i) :
    cubeInput tag g a (flipChoice i e) v=cubeInput tag g a e v := by
  cases h : tag v with
  | none => simp [cubeInput,h]
  | some j =>
    have hji : j≠i := fun he => hv (by simpa [he] using h)
    simp [cubeInput,h,flipChoice,hji]

theorem cubeDifference_monomial_missing (tag : V → Option I) (g : V → Poly (ZMod 2) W)
    (a : V → ZMod 2 → ZMod 2) (d : V →₀ ℕ) (c : ZMod 2) (i : I)
    (hi : ∀ v ∈ d.support, tag v ≠ some i) : cubeDifference tag g a (monomial d c)=0 := by
  rw [cubeDifference_apply]
  apply cube_sum_cancel i
  intro e
  rw [aeval_monomial,aeval_monomial]
  congr 1
  unfold Finsupp.prod
  apply Finset.prod_congr rfl
  intro v hv
  dsimp only
  rw [cubeInput_flip tag g a i e v (hi v hv)]

def outsideDegree (tag : V → Option I) (d : V →₀ ℕ) : ℕ :=
  ∑ v ∈ d.support, if tag v=none then d v else 0

def insideDegree (tag : V → Option I) (d : V →₀ ℕ) : ℕ :=
  ∑ i : I, ∑ v ∈ d.support, if tag v=some i then d v else 0

theorem cube_degree_partition (tag : V → Option I) (d : V →₀ ℕ) :
    outsideDegree tag d+insideDegree tag d=d.sum (fun _ n => n) := by
  rw [outsideDegree,insideDegree,Finset.sum_comm,← Finset.sum_add_distrib,Finsupp.sum]
  apply Finset.sum_congr rfl
  intro v _
  cases tag v <;> simp

theorem cube_inside_degree_bound (tag : V → Option I) (d : V →₀ ℕ)
    (h : ∀ i : I, ∃ v ∈ d.support, tag v=some i) : Fintype.card I ≤ insideDegree tag d := by
  calc
    Fintype.card I=∑ _i : I, 1 := by simp
    _ ≤ insideDegree tag d := by
      apply Finset.sum_le_sum
      intro i _
      obtain ⟨v,hv,ht⟩ := h i
      calc
        1≤d v := Nat.one_le_iff_ne_zero.mpr (Finsupp.mem_support_iff.mp hv)
        _=(if tag v=some i then d v else 0) := by simp only [ht,↓reduceIte]
        _≤∑ w ∈ d.support, if tag w=some i then d w else 0 :=
          Finset.single_le_sum (f := fun w => if tag w=some i then d w else 0)
            (fun _ _ => Nat.zero_le _) hv

omit [Fintype I] in
theorem cubeInput_monomial_degree (tag : V → Option I) (g : V → Poly (ZMod 2) W)
    (hg : ∀ v, tag v=none → (g v).totalDegree≤1) (a : V → ZMod 2 → ZMod 2)
    (e : I → ZMod 2) (d : V →₀ ℕ) (c : ZMod 2) :
    (aeval (cubeInput tag g a e) (monomial d c)).totalDegree≤outsideDegree tag d := by
  rw [aeval_monomial]
  apply (totalDegree_mul _ _).trans
  change (C c : Poly (ZMod 2) W).totalDegree+_≤_
  rw [totalDegree_C,zero_add,Finsupp.prod]
  apply (totalDegree_finsetProd _ _).trans
  apply Finset.sum_le_sum
  intro v _
  apply (totalDegree_pow _ _).trans
  cases ht : tag v with
  | none => simpa [outsideDegree,cubeInput,ht] using Nat.mul_le_mul_left (d v) (hg v ht)
  | some i => simp [cubeInput,ht]

theorem cubeDifference_monomial_degree (tag : V → Option I) (g : V → Poly (ZMod 2) W)
    (hg : ∀ v, tag v=none → (g v).totalDegree≤1) (a : V → ZMod 2 → ZMod 2)
    (d : V →₀ ℕ) (c : ZMod 2) :
    (cubeDifference tag g a (monomial d c)).totalDegree≤d.sum (fun _ n => n)-Fintype.card I := by
  by_cases h : ∀ i : I, ∃ v ∈ d.support, tag v=some i
  · rw [cubeDifference_apply]
    apply totalDegree_finsetSum_le
    intro e _
    apply (cubeInput_monomial_degree tag g hg a e d c).trans
    have hc := cube_inside_degree_bound tag d h
    have he := cube_degree_partition tag d
    omega
  · push Not at h
    obtain ⟨i,hi⟩ := h
    rw [cubeDifference_monomial_missing tag g a d c i hi]
    simp

theorem cubeDifference_degree (tag : V → Option I) (g : V → Poly (ZMod 2) W)
    (hg : ∀ v, tag v=none → (g v).totalDegree≤1) (a : V → ZMod 2 → ZMod 2)
    (P : Poly (ZMod 2) V) :
    (cubeDifference tag g a P).totalDegree≤P.totalDegree-Fintype.card I := by
  have he : cubeDifference tag g a P=∑ d ∈ P.support, cubeDifference tag g a (monomial d (P.coeff d)) := by
    conv_lhs => rw [P.as_sum,map_sum]
  rw [he]
  apply totalDegree_finsetSum_le
  intro d hd
  exact (cubeDifference_monomial_degree tag g hg a d _).trans
    (Nat.sub_le_sub_right (le_totalDegree hd) _)
theorem cubeDifference_fixed_factor (tag : V → Option I) (g : V → Poly (ZMod 2) W)
    (a : V → ZMod 2 → ZMod 2) (q f : Poly (ZMod 2) V) (r : Poly (ZMod 2) W)
    (hr : ∀ e : I → ZMod 2, aeval (cubeInput tag g a e) f=r) :
    cubeDifference tag g a (q*f)=cubeDifference tag g a q*r := by
  rw [cubeDifference_apply,cubeDifference_apply,Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro e _
  rw [map_mul,hr e]

theorem cubeDifference_ns (tag : V → Option I) (g : V → Poly (ZMod 2) W)
    (hg : ∀ v, tag v=none → (g v).totalDegree≤1) (a : V → ZMod 2 → ZMod 2)
    (F : Set (Poly (ZMod 2) V)) (G : Set (Poly (ZMod 2) W))
    (hgen : ∀ f ∈ F, ∃ r : Poly (ZMod 2) W, (r=0 ∨ r ∈ G) ∧
      ∀ e : I → ZMod 2, aeval (cubeInput tag g a e) f=r)
    (B : ℕ) (P : Poly (ZMod 2) V) (hP : P ∈ nsSpace F B) :
    cubeDifference tag g a P ∈ nsSpace G (B-Fintype.card I) := by
  induction hP using Submodule.span_induction with
  | mem p hp =>
    obtain ⟨f,hf,q,rfl,hd⟩ := hp
    obtain ⟨r,hr,hres⟩ := hgen f hf
    have he := cubeDifference_fixed_factor tag g a q f r hres
    rcases hr with rfl | hr
    · rw [he,mul_zero]
      exact Submodule.zero_mem _
    · rw [he]
      apply nsSpace_generator hr
      rw [← he]
      exact (cubeDifference_degree tag g hg a (q*f)).trans (Nat.sub_le_sub_right hd _)
  | zero => rw [map_zero]; exact Submodule.zero_mem _
  | add p q _ _ hp hq => rw [map_add]; exact Submodule.add_mem _ hp hq
  | smul c p _ hp => rw [map_smul]; exact Submodule.smul_mem _ c hp

theorem cubeDifference_annihilates (tag : V → Option I) (g : V → Poly (ZMod 2) W)
    (hg : ∀ v, tag v=none → (g v).totalDegree≤1) (a : V → ZMod 2 → ZMod 2)
    (F : Set (Poly (ZMod 2) V)) (G : Set (Poly (ZMod 2) W))
    (hgen : ∀ f ∈ F, ∃ r : Poly (ZMod 2) W, (r=0 ∨ r ∈ G) ∧
      ∀ e : I → ZMod 2, aeval (cubeInput tag g a e) f=r)
    (B : ℕ) (L : Poly (ZMod 2) W →ₗ[ZMod 2] ZMod 2)
    (hL : ∀ q ∈ nsSpace G (B-Fintype.card I), L q=0) :
    ∀ P ∈ nsSpace F B, L (cubeDifference tag g a P)=0 := by
  intro P hP
  exact hL _ (cubeDifference_ns tag g hg a F G hgen B P hP)
theorem cubeDifference_low_degree (tag : V → Option I) (g : V → Poly (ZMod 2) W)
    (a : V → ZMod 2 → ZMod 2) (P : Poly (ZMod 2) V) (hP : P.totalDegree<Fintype.card I) :
    cubeDifference tag g a P=0 := by
  have he : cubeDifference tag g a P=∑ d ∈ P.support, cubeDifference tag g a (monomial d (P.coeff d)) := by
    conv_lhs => rw [P.as_sum,map_sum]
  rw [he]
  apply Finset.sum_eq_zero
  intro d hd
  have hmissing : ¬(∀ i : I, ∃ v ∈ d.support, tag v=some i) := by
    intro h
    have hc := cube_inside_degree_bound tag d h
    have hp := cube_degree_partition tag d
    have hdegree := le_totalDegree hd
    omega
  push Not at hmissing
  obtain ⟨i,hi⟩ := hmissing
  exact cubeDifference_monomial_missing tag g a d (P.coeff d) i hi
end
end MathResearch.PolynomialCalculus
