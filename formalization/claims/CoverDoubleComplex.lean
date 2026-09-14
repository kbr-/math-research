/-
Claim: lem:finite-cover-double-complex
Source: https://kbr.is-a.dev/math-research/#lean-finite-cover-double-complex
Scope: Finite F₂ cover double coefficients, commuting square-zero insertion differentials, and positive-vertex-degree horizontal augmented-row exactness.
Declarations: MathResearch.ThirdParty.Augmented.bi_nonzero MathResearch.ThirdParty.Augmented.bi_add MathResearch.ThirdParty.Augmented.horizontal_add MathResearch.ThirdParty.Augmented.vertical_add MathResearch.ThirdParty.Augmented.horizontal_zero MathResearch.ThirdParty.Augmented.vertical_zero MathResearch.ThirdParty.Augmented.horizontal_squared MathResearch.ThirdParty.Augmented.vertical_squared MathResearch.ThirdParty.Augmented.horizontal_vertical MathResearch.ThirdParty.Augmented.admissible_hdown MathResearch.ThirdParty.Augmented.admissible_vdown MathResearch.ThirdParty.Augmented.horizontal_supported MathResearch.ThirdParty.Augmented.vertical_supported MathResearch.ThirdParty.Augmented.horizontal_exact MathResearch.ThirdParty.Augmented.horizontal_at_zero MathResearch.ThirdParty.Augmented.vertical_at_zero MathResearch.ThirdParty.Augmented.totalBoundary_squared
-/
import claims.FiniteComplexCover
import claims.AugmentedCone

namespace MathResearch.ThirdParty.Augmented
noncomputable section
open scoped BigOperators
variable {V I : Type*} [Fintype V] [DecidableEq V] [Fintype I] [DecidableEq I]

abbrev DoubleCoeff (I V : Type*) := Finset I → Finset V → ZMod 2

def horizontal (d : DoubleCoeff I V) : DoubleCoeff I V :=
  fun J S => boundary (fun T => d T S) J

def vertical (d : DoubleCoeff I V) : DoubleCoeff I V :=
  fun J => boundary (d J)

def Admissible (K : Complex V) (L : I → Complex V) (J : Finset I) (S : Finset V) : Prop :=
  S ∈ K.faces ∧ (∀ i ∈ J, S ∈ (L i).faces) ∧ J ∈ (nerve L).faces

def BiSupported (K : Complex V) (L : I → Complex V) (a b : ℕ)
    (d : DoubleCoeff I V) : Prop :=
  ∀ J S, ¬ (J.card = a ∧ S.card = b ∧ Admissible K L J S) → d J S = 0

omit [Fintype V] [Fintype I] [DecidableEq V] [DecidableEq I] in
theorem bi_nonzero {K : Complex V} {L : I → Complex V} {a b : ℕ}
    {d : DoubleCoeff I V} (hd : BiSupported K L a b d) {J S} (h : d J S ≠ 0) :
    J.card = a ∧ S.card = b ∧ Admissible K L J S := by
  by_contra hn
  exact h (hd J S hn)

omit [Fintype V] [Fintype I] [DecidableEq V] [DecidableEq I] in
theorem bi_add {K : Complex V} {L : I → Complex V} {a b : ℕ}
    {d e : DoubleCoeff I V} (hd : BiSupported K L a b d) (he : BiSupported K L a b e) :
    BiSupported K L a b (d+e) := by
  intro J S h
  simp [hd J S h, he J S h]

omit [Fintype V] [DecidableEq V] in
theorem horizontal_add (d e : DoubleCoeff I V) :
    horizontal (d+e) = horizontal d + horizontal e := by
  funext J S
  exact congrFun (boundary_add (fun T => d T S) (fun T => e T S)) J

omit [Fintype I] [DecidableEq I] in
theorem vertical_add (d e : DoubleCoeff I V) :
    vertical (d+e) = vertical d + vertical e := by
  funext J
  exact boundary_add (d J) (e J)

omit [Fintype V] [DecidableEq V] in
@[simp] theorem horizontal_zero : horizontal (0 : DoubleCoeff I V) = 0 := by
  funext J S
  exact congrFun boundary_zero J
omit [Fintype I] [DecidableEq I] in
@[simp] theorem vertical_zero : vertical (0 : DoubleCoeff I V) = 0 := by
  funext J
  exact boundary_zero

omit [Fintype V] [DecidableEq V] in
theorem horizontal_squared (d : DoubleCoeff I V) : horizontal (horizontal d) = 0 := by
  funext J S
  exact congrFun (boundary_boundary (fun T => d T S)) J

omit [Fintype I] [DecidableEq I] in
theorem vertical_squared (d : DoubleCoeff I V) : vertical (vertical d) = 0 := by
  funext J
  exact boundary_boundary (d J)

theorem horizontal_vertical (d : DoubleCoeff I V) :
    horizontal (vertical d) = vertical (horizontal d) := by
  funext J S
  simp only [horizontal, vertical, boundary]
  have hsV (p : Prop) [Decidable p] (f : V → ZMod 2) :
      (if p then 0 else ∑ x, f x) = ∑ x, if p then 0 else f x := by
    split_ifs <;> simp
  have hsI (p : Prop) [Decidable p] (f : I → ZMod 2) :
      (if p then 0 else ∑ x, f x) = ∑ x, if p then 0 else f x := by
    split_ifs <;> simp
  simp_rw [hsV, hsI]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro v _
  apply Finset.sum_congr rfl
  intro i _
  split_ifs <;> rfl

omit [Fintype V] [Fintype I] [DecidableEq V] [DecidableEq I] in
theorem admissible_hdown {K : Complex V} {L : I → Complex V} {J T : Finset I}
    {S : Finset V} (h : J ⊆ T) (hT : Admissible K L T S) : Admissible K L J S :=
  ⟨hT.1, (fun i hi => hT.2.1 i (h hi)), (nerve L).downward h hT.2.2⟩

omit [Fintype V] [Fintype I] [DecidableEq V] [DecidableEq I] in
theorem admissible_vdown {K : Complex V} {L : I → Complex V} {J : Finset I}
    {S T : Finset V} (h : S ⊆ T) (hT : Admissible K L J T) : Admissible K L J S :=
  ⟨K.downward h hT.1, (fun i hi => (L i).downward h (hT.2.1 i hi)), hT.2.2⟩

omit [Fintype V] [DecidableEq V] in
theorem horizontal_supported {K : Complex V} {L : I → Complex V} {a b : ℕ}
    {d : DoubleCoeff I V} (hd : BiSupported K L (a+1) b d) :
    BiSupported K L a b (horizontal d) := by
  intro J S h
  apply Finset.sum_eq_zero
  intro i _
  by_cases hi : i ∈ J
  · simp [hi]
  · simp only [hi, ↓reduceIte]
    apply hd
    intro hh
    apply h
    refine ⟨?_, hh.2.1, admissible_hdown (Finset.subset_insert i J) hh.2.2⟩
    simpa [Finset.card_insert_of_notMem hi] using hh.1

omit [Fintype I] [DecidableEq I] in
theorem vertical_supported {K : Complex V} {L : I → Complex V} {a b : ℕ}
    {d : DoubleCoeff I V} (hd : BiSupported K L a (b+1) d) :
    BiSupported K L a b (vertical d) := by
  intro J S h
  apply Finset.sum_eq_zero
  intro v _
  by_cases hv : v ∈ S
  · simp [hv]
  · simp only [hv, ↓reduceIte]
    apply hd
    intro hh
    apply h
    refine ⟨hh.1, ?_, admissible_vdown (Finset.subset_insert v S) hh.2.2⟩
    simpa [Finset.card_insert_of_notMem hv] using hh.2.1

omit [Fintype V] [DecidableEq V] in
/-- At positive vertex count, each row is contracted at a cover index containing S. -/
theorem horizontal_exact (K : Complex V) (L : I → Complex V) (hcover : Covers K L)
    (a b : ℕ) (hb : 0 < b) (d : DoubleCoeff I V) (hd : BiSupported K L a b d)
    (hz : horizontal d = 0) :
    ∃ u, BiSupported K L (a+1) b u ∧ horizontal u = d := by
  classical
  let pick (S : Finset V) (hS : S ∈ K.faces) : I := Classical.choose (hcover S hS)
  have hpick (S : Finset V) (hS : S ∈ K.faces) : S ∈ (L (pick S hS)).faces :=
    Classical.choose_spec (hcover S hS)
  let u : DoubleCoeff I V := fun J S =>
    if hS : S ∈ K.faces ∧ S.card = b then
      cone (pick S hS.1) (fun T => d T S) J else 0
  refine ⟨u, ?_, ?_⟩
  · intro J S hn
    by_contra hne
    have hS : S ∈ K.faces ∧ S.card = b := by
      by_contra h
      exact hne (by simp [u, h])
    let i := pick S hS.1
    have hi : i ∈ J := by
      by_contra h
      exact hne (by simp [u, hS, cone, i, h])
    have hc : d (J.erase i) S ≠ 0 := by
      simpa [u, hS, cone, i, hi] using hne
    obtain ⟨hcard, _, hgood⟩ := bi_nonzero hd hc
    have hcommon : ∀ j ∈ J, S ∈ (L j).faces := by
      intro j hj
      by_cases he : j = i
      · subst j
        exact hpick S hS.1
      · exact hgood.2.1 j (Finset.mem_erase.mpr ⟨he, hj⟩)
    have hvertex : ∃ v, v ∈ S := Finset.card_pos.mp (by omega)
    obtain ⟨v, hv⟩ := hvertex
    apply hn
    refine ⟨?_, hS.2, hS.1, hcommon, Or.inr ⟨v, ?_⟩⟩
    · have he := Finset.card_erase_add_one hi
      omega
    · intro j hj
      exact (L j).downward (Finset.singleton_subset_iff.mpr hv) (hcommon j hj)
  · funext J S
    by_cases hS : S ∈ K.faces ∧ S.card = b
    · have hcycle : boundary (fun T => d T S) = 0 := by
        funext T
        exact congrFun (congrFun hz T) S
      have hc := cone_identity (pick S hS.1) (fun T => d T S)
      have hzero : cone (pick S hS.1) (0 : Coeff I) = 0 := by
        funext T
        simp [cone]
      rw [hcycle, hzero, add_zero] at hc
      simpa [horizontal, u, hS] using congrFun hc J
    · have hdz : d J S = 0 := hd J S (by
        intro h
        exact hS ⟨h.2.2.1, h.2.1⟩)
      simp [horizontal, boundary, u, hS, hdz]

omit [Fintype V] [DecidableEq V] in
theorem horizontal_at_zero {K : Complex V} {L : I → Complex V} {b : ℕ}
    {d : DoubleCoeff I V} (hd : BiSupported K L 0 b d) : horizontal d = 0 := by
  funext J S
  apply Finset.sum_eq_zero
  intro i _
  by_cases hi : i ∈ J
  · simp [hi]
  · simp only [hi, ↓reduceIte]
    apply hd
    intro hh
    simpa [Finset.card_insert_of_notMem hi] using hh.1

omit [Fintype I] [DecidableEq I] in
theorem vertical_at_zero {K : Complex V} {L : I → Complex V} {a : ℕ}
    {d : DoubleCoeff I V} (hd : BiSupported K L a 0 d) : vertical d = 0 := by
  funext J S
  apply Finset.sum_eq_zero
  intro v _
  by_cases hv : v ∈ S
  · simp [hv]
  · simp only [hv, ↓reduceIte]
    apply hd
    intro hh
    simpa [Finset.card_insert_of_notMem hv] using hh.2.1

def totalBoundary (d : DoubleCoeff I V) : DoubleCoeff I V := horizontal d + vertical d

theorem totalBoundary_squared (d : DoubleCoeff I V) :
    totalBoundary (totalBoundary d) = 0 := by
  simp only [totalBoundary, horizontal_add, vertical_add, horizontal_squared,
    vertical_squared, zero_add, add_zero, horizontal_vertical]
  funext J S
  exact ZModModule.add_self _

end
end MathResearch.ThirdParty.Augmented
