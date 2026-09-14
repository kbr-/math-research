/-
Claim: third-party:homological-cover-lemma
Source: https://kbr.is-a.dev/math-research/#lean-homological-cover-lemma
Scope: Finite F₂ augmented homological cover lemma, stated by exact cell-count filling with all required nerve and intersection hypotheses.
Declarations: MathResearch.ThirdParty.Augmented.homological_cover
-/
import claims.CoverDoubleComplex

namespace MathResearch.ThirdParty.Augmented
noncomputable section
open scoped BigOperators
variable {V I : Type*} [Fintype V] [DecidableEq V] [Fintype I] [DecidableEq I]

/-- Exact intersections only where they contribute a genuine nerve face. -/
def IntersectionExact (L : I → Complex V) (n : ℕ) : Prop :=
  ∀ J : Finset I, J.Nonempty → J ∈ (nerve L).faces →
    ∀ r, J.card + r ≤ n → ExactAt (intersection L J) r

omit [Fintype V] in
private theorem bottom_horizontal_exact (K : Complex V) (L : I → Complex V)
    (a : ℕ) (hn : ExactAt (nerve L) a) (d : DoubleCoeff I V)
    (hd : BiSupported K L a 0 d) (hz : horizontal d = 0) :
    ∃ u, BiSupported K L (a+1) 0 u ∧ horizontal u = d := by
  classical
  let c : Coeff I := fun J => d J ∅
  have hc : Supported (nerve L) a c := by
    intro J h
    apply hd J ∅
    intro hh
    exact h.elim (fun h => h hh.2.2.2.2) (fun h => h hh.1)
  have hz' : boundary c = 0 := by
    funext J
    exact congrFun (congrFun hz J) ∅
  obtain ⟨f, hf, hfc⟩ := hn c hc hz'
  let u : DoubleCoeff I V := fun J S => if S = ∅ then f J else 0
  refine ⟨u, ?_, ?_⟩
  · intro J S h
    by_cases hS : S = ∅
    · subst S
      simp only [u, ↓reduceIte]
      apply hf
      by_contra hn'
      push Not at hn'
      apply h
      refine ⟨hn'.2, rfl, K.empty_mem, ?_, hn'.1⟩
      intro i _
      exact (L i).empty_mem
    · simp [u, hS]
  · funext J S
    by_cases hS : S = ∅
    · subst S
      simpa [horizontal, u, c] using congrFun hfc J
    · have hdS : d J S = 0 := hd J S (by
        intro h
        exact hS (Finset.card_eq_zero.mp h.2.1))
      simp [horizontal, boundary, u, hS, hdS]

omit [Fintype I] [DecidableEq I] in
private theorem column_vertical_exact (K : Complex V) (L : I → Complex V)
    (hsub : ∀ i, (L i).faces ⊆ K.faces) (n a b : ℕ) (ha : 0 < a)
    (hab : a+b ≤ n) (hex : IntersectionExact L n) (d : DoubleCoeff I V)
    (hd : BiSupported K L a b d) (hz : vertical d = 0) :
    ∃ u, BiSupported K L a (b+1) u ∧ vertical u = d := by
  classical
  have hf (J : Finset I) (hJ : J.card = a ∧ J ∈ (nerve L).faces) :
      ∃ c, Supported (intersection L J) (b+1) c ∧ boundary c = d J := by
    have hs : Supported (intersection L J) b (d J) := by
      intro S h
      apply hd J S
      intro hh
      exact h.elim (fun h => h hh.2.2.2.1) (fun h => h hh.2.1)
    exact hex J (Finset.card_pos.mp (by omega)) hJ.2 b (by omega)
      (d J) hs (congrFun hz J)
  let u : DoubleCoeff I V := fun J =>
    if hJ : J.card = a ∧ J ∈ (nerve L).faces then Classical.choose (hf J hJ) else 0
  refine ⟨u, ?_, ?_⟩
  · intro J S hn
    by_cases hJ : J.card = a ∧ J ∈ (nerve L).faces
    · simp only [u, hJ]
      have hu := (Classical.choose_spec (hf J hJ)).1
      apply hu
      by_contra hneg
      push Not at hneg
      apply hn
      obtain ⟨i, hi⟩ := Finset.card_pos.mp (show 0 < J.card by omega)
      exact ⟨hJ.1, hneg.2, hsub i (hneg.1 i hi), hneg.1, hJ.2⟩
    · simp [u, hJ]
  · funext J
    by_cases hJ : J.card = a ∧ J ∈ (nerve L).faces
    · simpa [vertical, u, hJ] using (Classical.choose_spec (hf J hJ)).2
    · have hdJ : d J = 0 := by
        funext S
        apply hd
        intro h
        exact hJ ⟨h.1, h.2.2.2.2⟩
      simp [vertical, u, hJ, hdJ]

private theorem closed_horizontal_lift (K : Complex V) (L : I → Complex V)
    (hsub : ∀ i, (L i).faces ⊆ K.faces) (hcover : Covers K L) (n : ℕ)
    (hnerve : AcyclicThrough (nerve L) n) (hex : IntersectionExact L n) (b : ℕ) :
    ∀ a, a+b < n → ∀ d, BiSupported K L a b d → horizontal d = 0 → vertical d = 0 →
      ∃ u, BiSupported K L (a+1) b u ∧ horizontal u = d ∧ vertical u = 0 := by
  induction b with
  | zero =>
    intro a ha d hd hz _
    obtain ⟨u, hu, hud⟩ := bottom_horizontal_exact K L a (hnerve a (by omega)) d hd hz
    exact ⟨u, hu, hud, vertical_at_zero hu⟩
  | succ b ih =>
    intro a ha d hd hz hv
    obtain ⟨x, hx, hxd⟩ := horizontal_exact K L hcover a (b+1) (by omega) d hd hz
    have hhx : horizontal (vertical x) = 0 := by
      rw [horizontal_vertical, hxd, hv]
    obtain ⟨y, hy, hyx, hvy⟩ := ih (a+1) (by omega) (vertical x)
      (vertical_supported hx) hhx (vertical_squared x)
    obtain ⟨z, hzs, hzy⟩ := column_vertical_exact K L hsub n (a+1+1) b
      (by omega) (by omega) hex y hy hvy
    refine ⟨x + horizontal z, bi_add hx (horizontal_supported hzs), ?_, ?_⟩
    · rw [horizontal_add, horizontal_squared, add_zero, hxd]
    · rw [vertical_add, ← horizontal_vertical, hzy, hyx]
      funext J S
      exact ZModModule.add_self _

/-- Cell-count version of the finite homological cover lemma (n=q+2). -/
theorem homological_cover (K : Complex V) (L : I → Complex V)
    (hsub : ∀ i, (L i).faces ⊆ K.faces) (hcover : Covers K L) (n : ℕ)
    (hnerve : AcyclicThrough (nerve L) n) (hex : IntersectionExact L n) :
    AcyclicThrough K n := by
  intro k hk c hc hz
  classical
  let d : DoubleCoeff I V := fun J S => if J = ∅ then c S else 0
  have hd : BiSupported K L 0 k d := by
    intro J S hn
    by_cases hJ : J = ∅
    · subst J
      simp only [d, ↓reduceIte]
      apply hc
      by_contra hneg
      push Not at hneg
      apply hn
      exact ⟨rfl, hneg.2, hneg.1, by simp, Or.inl rfl⟩
    · simp [d, hJ]
  have hv : vertical d = 0 := by
    funext J
    by_cases hJ : J = ∅
    · simpa [vertical, d, hJ] using hz
    · simp only [vertical, d, hJ, ↓reduceIte]
      exact boundary_zero
  obtain ⟨u, hu, hud, huv⟩ := closed_horizontal_lift K L hsub hcover n hnerve hex k
    0 (by omega) d hd (horizontal_at_zero hd) hv
  obtain ⟨z, hzs, hzu⟩ := column_vertical_exact K L hsub n 1 k (by omega)
    (by omega) hex u hu huv
  refine ⟨fun S => horizontal z ∅ S, ?_, ?_⟩
  · intro S hs
    apply horizontal_supported hzs ∅ S
    intro hh
    exact hs.elim (fun h => h hh.2.2.1) (fun h => h hh.2.1)
  · have he : vertical (horizontal z) = d := by
      rw [← horizontal_vertical, hzu, hud]
    funext S
    simpa [vertical, d] using congrFun (congrFun he ∅) S

end
end MathResearch.ThirdParty.Augmented
