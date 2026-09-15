/-
Claim: thm:publication-Res-parity-bit-PHP
Source: https://kbr.is-a.dev/math-research/#lean-publication-bit-PHP-superpolynomial
Scope: Full usual-CNF bit-PHP superpolynomial node lower bound for the finite affine DAG calculus containing both recorded rule conventions. For every real K>0 and sufficiently large bit length, every refutation has more than (2^ℓ)^K nodes.
Declarations: MathResearch.bitPHP_superpolynomial
-/
import claims.AffineFamilyExclusion
import claims.BitPHPClauseTransfer
import Mathlib.Analysis.SpecialFunctions.Pow.Real

namespace MathResearch
noncomputable section
open PolynomialCalculus Filter

 theorem bitPHP_superpolynomial (K : ℝ) (_hK : 0 < K) :
    ∃ L : ℕ, ∀ ℓ ≥ L, ∀ {S : ℕ}
      (C : Fin S → FiniteParityClause (BitVar (2^ℓ+1) ℓ))
      (_dag : AffineDAG (usualBitPHPInitials (2^ℓ+1) ℓ) C)
      (finish : Fin S), C finish = ∅ → ((2^ℓ:ℕ):ℝ)^K < (S:ℝ) := by
  classical
  let a := max (⌈K⌉₊) 2
  have ha : 2 ≤ a := le_max_right _ _
  have hKa : K ≤ (a:ℝ) := (Nat.le_ceil K).trans (by exact_mod_cast (le_max_left (⌈K⌉₊) 2))
  obtain ⟨L,hL⟩ := eventually_atTop.mp
    ((affine_family_polylog_exclusion a 13 1).and (eventually_ge_atTop 2))
  refine ⟨L,?_⟩
  intro ℓ hℓL S C dag finish hempty
  obtain ⟨hex,hℓ⟩ := hL ℓ hℓL
  by_contra hnot
  have hSreal : (S:ℝ) ≤ ((2^ℓ:ℕ):ℝ)^K := le_of_not_gt hnot
  let n : ℕ := 2^ℓ
  have hn : 1 ≤ n := one_le_pow₀ (by decide)
  have hS : S ≤ n^a := by
    have h := hSreal.trans (Real.rpow_le_rpow_of_exponent_le (by exact_mod_cast hn) hKa)
    rw [Real.rpow_natCast] at h
    exact_mod_cast h
  obtain ⟨N,R,hN,_,_,_,hpc⟩ := usual_bitPHP_PC_transfer C dag finish hempty (3*ℓ) (by omega)
  have hchoose := Nat.choose_le_pow (n+1) 2
  have hquad : (n+1)^2 ≤ 4*n^2 := by nlinarith
  have hpow : n^2 ≤ n^a := pow_le_pow_right₀ hn ha
  have hN' : N ≤ 13*2^(a*ℓ)+1 := by
    have hb : N ≤ 13*n^a+1 := by nlinarith
    simpa only [n,← pow_mul,Nat.mul_comm] using hb
  let g : ∀ b : Fin N, {f // f ∈ R b} → AffineInputMap (BitVar (2^ℓ+1) ℓ) :=
    fun _ i => i.val
  have hcount : Nat.card (ProperBlockIndex g) ≤ 13*2^(a*ℓ)+1 := by
    apply le_trans ?_ hN'
    rw [Nat.card_eq_fintype_card]
    calc
      Fintype.card (ProperBlockIndex g) ≤ Fintype.card (Fin N) := Fintype.card_subtype_le _
      _ = N := Fintype.card_fin _
  have hdegree : max (2*(3*ℓ)+ℓ) (4*(3*ℓ)+1) = 12*ℓ+1 := by omega
  rw [hdegree,registry_system_eq_ensFamily] at hpc
  exact hex g hcount (12*ℓ+1) (by simp only [pow_one]; omega) hpc
end
end MathResearch
