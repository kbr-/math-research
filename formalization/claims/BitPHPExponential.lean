/-
Claim: cor:bit-PHP-exponential-parameter-bound
Source: https://kbr.is-a.dev/math-research/#bit-PHP-exponential-parameter-corollary
Scope: Full usual-CNF bit-PHP exponential node lower bound for the finite affine DAG calculus containing both recorded rule conventions. For every bit length ℓ ≥ 32, with n = 2^ℓ holes and n+1 pigeons, every refutation has more than exp(n/(32768 ℓ²)) nodes. The explicit threshold 32 strengthens the notebook's "sufficiently large"; the base-two form is a direct consequence. No optimization of the constant is claimed.
Declarations: MathResearch.bitPHP_exponential_room MathResearch.bitPHP_exponential MathResearch.bitPHP_exponential_base_two
-/
import claims.AffineFamilyExclusion
import claims.BitPHPClauseTransfer
import Mathlib.Analysis.SpecialFunctions.Pow.Real

namespace MathResearch
noncomputable section
open PolynomialCalculus

/-- The only growth comparison used: a cubic in the bit length below `2^ℓ`. -/
theorem bitPHP_exponential_room (ℓ : ℕ) (hℓ : 32 ≤ ℓ) :
    32768*((2*ℓ+4)*ℓ^2) ≤ 2^ℓ := by
  induction ℓ, hℓ using Nat.le_induction with
  | base => norm_num
  | succ ℓ hℓ ih =>
    have h2 : 32*ℓ^2 ≤ ℓ*ℓ^2 := Nat.mul_le_mul_right _ hℓ
    have h1 : 32*ℓ ≤ ℓ*ℓ := Nat.mul_le_mul_right _ hℓ
    have hstep : (2*(ℓ+1)+4)*(ℓ+1)^2 ≤ 2*((2*ℓ+4)*ℓ^2) := by nlinarith
    calc
      32768*((2*(ℓ+1)+4)*(ℓ+1)^2) ≤ 32768*(2*((2*ℓ+4)*ℓ^2)) :=
        Nat.mul_le_mul_left _ hstep
      _ = 2*(32768*((2*ℓ+4)*ℓ^2)) := by ring
      _ ≤ 2*2^ℓ := Nat.mul_le_mul_left _ ih
      _ = 2^(ℓ+1) := by ring

theorem bitPHP_exponential : ∀ ℓ ≥ 32, ∀ {S : ℕ}
    (C : Fin S → FiniteParityClause (BitVar (2^ℓ+1) ℓ))
    (_dag : AffineDAG (usualBitPHPInitials (2^ℓ+1) ℓ) C)
    (finish : Fin S), C finish = ∅ →
    Real.exp (((2^ℓ:ℕ):ℝ)/(32768*(ℓ:ℝ)^2)) < (S:ℝ) := by
  intro ℓ hℓ S C dag finish hempty
  classical
  by_contra hnot
  let n : ℕ := 2^ℓ
  let x : ℝ := ((n:ℕ):ℝ)/(32768*(ℓ:ℝ)^2)
  have hS : (S:ℝ) ≤ Real.exp x := le_of_not_gt hnot
  have hn1 : 1 ≤ n := Nat.one_le_two_pow
  have hroom : 32768*((2*ℓ+4)*ℓ^2) ≤ n := bitPHP_exponential_room ℓ hℓ
  have hℓℓ : 32*ℓ ≤ ℓ*ℓ := Nat.mul_le_mul_right _ hℓ
  have h64 : 64*ℓ ≤ n := by nlinarith
  -- Real-number bookkeeping.
  have hℓR : (32:ℝ) ≤ (ℓ:ℝ) := by exact_mod_cast hℓ
  have hnR : (1:ℝ) ≤ (n:ℝ) := by exact_mod_cast hn1
  have hden : (0:ℝ) < 32768*(ℓ:ℝ)^2 := by positivity
  have hxmul : x*(32768*(ℓ:ℝ)^2) = (n:ℝ) := div_mul_cancel₀ _ hden.ne'
  have hroomR : (32768:ℝ)*((2*(ℓ:ℝ)+4)*(ℓ:ℝ)^2) ≤ (n:ℝ) := by exact_mod_cast hroom
  have hx : 2*(ℓ:ℝ)+4 ≤ x := by
    rw [le_div_iff₀ hden]
    nlinarith
  have hx0 : 0 ≤ x := by linarith
  -- exp x ≥ 16 n².
  have he2 : (2:ℝ) ≤ Real.exp 1 := by
    have h := Real.add_one_le_exp (1:ℝ)
    linarith
  have hncast : (n:ℝ) = (2:ℝ)^ℓ := by
    simp only [n]
    push_cast
    ring
  have hexp : 16*(n:ℝ)^2 ≤ Real.exp x := by
    have hmono : Real.exp (((2*ℓ+4:ℕ):ℝ)) ≤ Real.exp x := by
      apply Real.exp_le_exp.mpr
      push_cast
      exact hx
    have hpow : (2:ℝ)^(2*ℓ+4) ≤ Real.exp 1^(2*ℓ+4) :=
      pow_le_pow_left₀ (by norm_num) he2 _
    rw [Real.exp_one_pow] at hpow
    have hring : (2:ℝ)^(2*ℓ+4) = 16*((2:ℝ)^ℓ)^2 := by ring
    rw [hncast, ← hring]
    exact hpow.trans hmono
  -- Inventory.
  let M : ℕ := 3*S + (n+1).choose 2
  have hchoose : (n+1).choose 2 ≤ 4*n^2 := by
    have h := Nat.choose_le_pow (n+1) 2
    nlinarith
  have hM : 1 ≤ M := by
    have h : 0 < (n+1).choose 2 := Nat.choose_pos (by omega)
    omega
  have hMR : (M:ℝ) ≤ 3*Real.exp x + 4*(n:ℝ)^2 := by
    have hc : (((n+1).choose 2:ℕ):ℝ) ≤ 4*(n:ℝ)^2 := by exact_mod_cast hchoose
    simp only [M]
    push_cast
    linarith
  have hMpos : (0:ℝ) < 4*(M:ℝ) := by
    have : (1:ℝ) ≤ (M:ℝ) := by exact_mod_cast hM
    linarith
  have h4M : 4*(M:ℝ) ≤ Real.exp (2*x) := by
    rw [two_mul, Real.exp_add]
    have hn2 : (1:ℝ) ≤ (n:ℝ)^2 := one_le_pow₀ hnR
    nlinarith
  have hlog : Real.log (4*(M:ℝ)) ≤ 2*x := (Real.log_le_iff_le_exp hMpos).mpr h4M
  -- The kernel degree k = ⌊n/(32ℓ)⌋.
  let k : ℕ := n/(32*ℓ)
  have hqpos : 0 < 32*ℓ := by omega
  have hkmul : k*(32*ℓ) ≤ n := Nat.div_mul_le_self n (32*ℓ)
  have hkpos : 1 ≤ k := Nat.div_pos (by omega) hqpos
  have hkn : k ≤ n := Nat.div_le_self n (32*ℓ)
  have hklt : n < (k+1)*(32*ℓ) := by
    have h1 := Nat.div_add_mod n (32*ℓ)
    have h2 := Nat.mod_lt n hqpos
    have h3 : (32*ℓ)*(n/(32*ℓ)) = k*(32*ℓ) := Nat.mul_comm _ _
    nlinarith
  have hnk : n ≤ 64*ℓ*k := by nlinarith
  have hnkR : (n:ℝ) ≤ 64*(ℓ:ℝ)*(k:ℝ) := by exact_mod_cast hnk
  have hsq : (((n+1:ℕ):ℝ))*Real.log (4*(M:ℝ)) ≤ (k:ℝ)^2 := by
    have hm : (((n+1:ℕ):ℝ)) ≤ 2*(n:ℝ) := by
      push_cast
      linarith
    have hm0 : (0:ℝ) ≤ ((n+1:ℕ):ℝ) := Nat.cast_nonneg _
    have hstep1 : (((n+1:ℕ):ℝ))*Real.log (4*(M:ℝ)) ≤ (2*(n:ℝ))*(2*x) := by
      calc
        _ ≤ (((n+1:ℕ):ℝ))*(2*x) := mul_le_mul_of_nonneg_left hlog hm0
        _ ≤ (2*(n:ℝ))*(2*x) := mul_le_mul_of_nonneg_right hm (by linarith)
    have hsqr := mul_self_le_mul_self (by linarith : (0:ℝ) ≤ (n:ℝ)) hnkR
    have hfin : (2*(n:ℝ))*(2*x) ≤ (k:ℝ)^2 := by
      have hscaled : ((2*(n:ℝ))*(2*x))*(32768*(ℓ:ℝ)^2) ≤ (k:ℝ)^2*(32768*(ℓ:ℝ)^2) := by
        have : ((2*(n:ℝ))*(2*x))*(32768*(ℓ:ℝ)^2) = 4*(n:ℝ)*(n:ℝ) := by
          rw [← hxmul]
          ring
        rw [this]
        nlinarith [sq_nonneg ((ℓ:ℝ)*(k:ℝ))]
      exact le_of_mul_le_mul_right hscaled hden
    exact hstep1.trans hfin
  have hℓk : k ≤ ℓ*k := Nat.le_mul_of_pos_left _ (by omega)
  have hpack : 4*(k-1) < n := by
    have : 32*k ≤ n := by nlinarith
    omega
  have hB : 2*(k*((12*ℓ+1)+1))-1 ≤ n := by
    have : 2*(k*((12*ℓ+1)+1)) ≤ n := by nlinarith
    omega
  -- Transfer and exclusion.
  obtain ⟨N,R,hN,_,_,_,hpc⟩ := usual_bitPHP_PC_transfer C dag finish hempty (3*ℓ) (by omega)
  let g : ∀ b : Fin N, {f // f ∈ R b} → AffineInputMap (BitVar (2^ℓ+1) ℓ) :=
    fun _ i => i.val
  have hcount : Nat.card (ProperHighIndex g k) ≤ M := by
    apply le_trans ((proper_high_count_le_proper_count g k).trans ?_) hN
    rw [Nat.card_eq_fintype_card]
    calc
      Fintype.card (ProperBlockIndex g) ≤ Fintype.card (Fin N) := Fintype.card_subtype_le _
      _ = N := Fintype.card_fin _
  have hdegree : max (2*(3*ℓ)+ℓ) (4*(3*ℓ)+1) = 12*ℓ+1 := by omega
  rw [hdegree,registry_system_eq_ensFamily] at hpc
  exact affine_family_exclusion_of_square (2^ℓ+1) ℓ M k (12*ℓ+1) (by omega) (by omega) hM
    hkpos (by omega) hsq (by omega) hpack hB g hcount hpc

/-- The same bound with base two, since `2 ≤ e`. -/
theorem bitPHP_exponential_base_two : ∀ ℓ ≥ 32, ∀ {S : ℕ}
    (C : Fin S → FiniteParityClause (BitVar (2^ℓ+1) ℓ))
    (_dag : AffineDAG (usualBitPHPInitials (2^ℓ+1) ℓ) C)
    (finish : Fin S), C finish = ∅ →
    (2:ℝ)^(((2^ℓ:ℕ):ℝ)/(32768*(ℓ:ℝ)^2)) < (S:ℝ) := by
  intro ℓ hℓ S C dag finish hempty
  refine lt_of_le_of_lt ?_ (bitPHP_exponential ℓ hℓ C dag finish hempty)
  have hy : (0:ℝ) ≤ ((2^ℓ:ℕ):ℝ)/(32768*(ℓ:ℝ)^2) := by positivity
  have hlog2 : Real.log 2 ≤ 1 := by
    have h := Real.log_le_sub_one_of_pos (by norm_num : (0:ℝ) < 2)
    linarith
  rw [Real.rpow_def_of_pos (by norm_num : (0:ℝ) < 2)]
  apply Real.exp_le_exp.mpr
  nlinarith
end
end MathResearch
