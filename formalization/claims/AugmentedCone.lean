/-
Claim: lem:augmented-cone-contraction
Source: https://kbr.is-a.dev/math-research/#lean-augmented-cone-contraction
Scope: Finite F₂ augmented cone contraction, exactness in every cell count, and explicit acyclicity convention.
Declarations: MathResearch.ThirdParty.Augmented.cone_identity MathResearch.ThirdParty.Augmented.cone_supported MathResearch.ThirdParty.Augmented.cone_exact
-/
import claims.AugmentedChainMaps

namespace MathResearch.ThirdParty.Augmented
noncomputable section
open scoped BigOperators
variable {V : Type*} [Fintype V] [DecidableEq V]

def IsCone (K : Complex V) (v : V) : Prop :=
  ∀ s, s ∈ K.faces → insert v s ∈ K.faces

def ExactAt (K : Complex V) (k : ℕ) : Prop :=
  ∀ c, Supported K k c → boundary c = 0 →
    ∃ b, Supported K (k + 1) b ∧ boundary b = c

def AcyclicThrough (K : Complex V) (n : ℕ) : Prop :=
  ∀ k < n, ExactAt K k

def cone (v : V) (c : Coeff V) : Coeff V :=
  fun s => if v ∈ s then c (s.erase v) else 0

theorem cone_identity (v : V) (c : Coeff V) :
    boundary (cone v c) + cone v (boundary c) = c := by
  funext s
  by_cases hv : v ∈ s
  · have hi (w : V) (hw : w ≠ v) :
        (insert w s).erase v = insert w (s.erase v) := by
      ext x
      simp only [Finset.mem_erase, Finset.mem_insert]
      aesop
    have hsum : boundary c (s.erase v) = c s + boundary (cone v c) s := by
      unfold boundary
      rw [← Finset.sum_erase_add _ _ (Finset.mem_univ v)]
      simp only [Finset.notMem_erase, ↓reduceIte, Finset.insert_erase hv]
      have he : (∑ w ∈ Finset.univ.erase v,
          if w ∈ s.erase v then (0 : ZMod 2) else c (insert w (s.erase v))) =
          ∑ w : V, if w ∈ s then 0 else cone v c (insert w s) := by
        rw [← Finset.sum_erase_add _ _ (Finset.mem_univ v)]
        simp only [hv, ↓reduceIte, add_zero]
        apply Finset.sum_congr rfl
        intro w hw
        have hwv : w ≠ v := (Finset.mem_erase.mp hw).1
        simp [Finset.mem_erase, hwv, cone, hv, hi w hwv]
      rw [he, add_comm]
    simp only [Pi.add_apply, cone, hv, ↓reduceIte]
    rw [hsum]
    calc
      _ = (boundary (cone v c) s + boundary (cone v c) s) + c s := by ac_rfl
      _ = c s := by rw [ZModModule.add_self, zero_add]
  · have hb : boundary (cone v c) s = c s := by
      unfold boundary
      rw [Finset.sum_eq_single v]
      · simp [cone, hv]
      · intro w _ hw
        simp [cone, hv, Ne.symm hw]
      · simp
    simpa [Pi.add_apply, cone, hv] using hb

omit [Fintype V] in
theorem cone_supported (K : Complex V) (v : V) (hv : IsCone K v)
    (k : ℕ) (c : Coeff V) (hc : Supported K k c) :
    Supported K (k+1) (cone v c) := by
  intro s hs
  by_cases hvs : v ∈ s
  · simp only [cone, hvs, ↓reduceIte]
    apply hc
    rcases hs with hs | hs
    · left
      intro h
      exact hs (by simpa [Finset.insert_erase hvs] using hv _ h)
    · right
      intro h
      exact hs (by simpa [Finset.insert_erase hvs] using
        Finset.card_insert_of_notMem (Finset.notMem_erase v s) |>.trans (congrArg (·+1) h))
  · simp [cone, hvs]

theorem cone_exact (K : Complex V) (v : V) (hv : IsCone K v) (k : ℕ) :
    ExactAt K k := by
  intro c hc hz
  refine ⟨cone v c, cone_supported K v hv k c hc, ?_⟩
  have h := cone_identity v c
  have hzero : cone v (0 : Coeff V) = 0 := by funext s; simp [cone]
  simpa [hz, hzero] using h

end
end MathResearch.ThirdParty.Augmented
