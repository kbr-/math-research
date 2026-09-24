/-
Claim: thm:binary-multiplicity-lower-bound
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#binary-multiplicity-lower-bound
Scope: For every k and n ≥ ⌊log₂ k⌋ + 2, every P ∈ F_2[x_1,…,x_n] with Hasse multiplicity ≥ k at every
nonzero point and multiplicity < k at the origin has total degree ≥ 2k + n − 2 − ⌊log₂ k⌋. The claim's
k ≥ 1 is not needed (for k = 0 the hypotheses are contradictory). Proof: the note's deduction at
n = ⌊log₂ k⌋ + 2, then the one-dimension step for each further variable.
Declarations: MathResearch.BinaryMultiplicityLowerBound.lower_bound
-/
import claims.BinaryMultiplicityCoverBound
import claims.OneDimensionStep

namespace MathResearch.BinaryMultiplicityLowerBound

open MvPolynomial MathResearch.HasseMultiplicity

theorem lower_bound (k : ℕ) {n : ℕ} (hn : Nat.log 2 k + 2 ≤ n) (P : MvPolynomial (Fin n) (ZMod 2))
    (hP : ∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P) (h0 : mult 0 P < k) :
    2 * k + n - 2 - Nat.log 2 k ≤ P.totalDegree := by
  have hklt : k < 2 ^ (Nat.log 2 k + 1) := Nat.lt_pow_succ_log_self (by norm_num) k
  induction n, hn using Nat.le_induction with
  | base =>
    have hb := BinaryMultiplicityCoverBound.cover_bound_of_origin (by omega) k hP h0
    have hdiv : k / 2 ^ (Nat.log 2 k + 2 - 1) = 0 := by
      apply Nat.div_eq_of_lt
      rw [show Nat.log 2 k + 2 - 1 = Nat.log 2 k + 1 by omega]
      exact hklt
    rw [hdiv] at hb
    omega
  | succ n hn ih =>
    set e : Fin (n + 1) ≃ Option (Fin n) := finSuccEquiv n
    set P' := rename e P
    have hmult' : ∀ a : Option (Fin n) → ZMod 2, mult a P' = mult (a ∘ e) P := fun a =>
      mult_rename_equiv e a P
    have hP' : ∀ a : Option (Fin n) → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a P' := by
      intro a ha
      rw [hmult']
      apply hP
      intro h
      apply ha
      funext o
      have := congrFun h (e.symm o)
      simpa using this
    have h0' : mult 0 P' < k := by
      rw [hmult']
      exact h0
    have hk : k < 2 ^ (Fintype.card (Fin n) + 1) := by
      rw [Fintype.card_fin]
      exact lt_of_lt_of_le hklt (Nat.pow_le_pow_right (by norm_num) (by omega))
    obtain ⟨S, hS, hS0, hSdeg⟩ := OneDimensionStep.one_dimension_step k hk P' hP' h0'
    have hih := ih S hS (by rw [hS0]; exact h0')
    have hdeg : P'.totalDegree = P.totalDegree := totalDegree_renameEquiv e P
    omega

end MathResearch.BinaryMultiplicityLowerBound
