/-
Claim: cor:generic-CNF-density-exponential-form
Source: https://kbr.is-a.dev/math-research/#lean-generic-CNF-density-exponential-form
Scope: Full corollary over the binary field. An elementary binomial estimate C(a+k,k) ≤ C(a+r+k,k)·exp(-rk/(a+r+k)), and its combination with the verified proof-size criterion: under the criterion's hypotheses and h(k+1)+1 ≤ v, dim U ≤ (3S+|J|)·C(v+k,k)·exp(-(h(k+1)+1)k/(v+k)), together with the weaker exponent -hk²/(v+k). Stated without division by C(v+k,k); the density dim U / C(v+k,k) is a reading of the inequality, not a Lean term. The hypothesis h(k+1)+1 ≤ v is explicit. No asymptotic statement and no relation between k and a separation degree is formalized.
Declarations: MathResearch.PolynomialCalculus.choose_restriction_exp_bound MathResearch.PolynomialCalculus.generic_CNF_density_bound MathResearch.PolynomialCalculus.generic_CNF_density_bound_simple
-/
import claims.GenericCNFSubspaceCriterion
import Mathlib.Analysis.SpecialFunctions.Exp

namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial

/-- Removing `r` of `a+r` variables shrinks the degree-`k` monomial count by at least the
factor `exp(-r k/(a+r+K))`, for every `k ≤ K`. -/
theorem choose_restriction_exp_bound (a r K : ℕ) : ∀ k ≤ K,
    (((a+k).choose k : ℕ) : ℝ) ≤
      (((a+r+k).choose k : ℕ) : ℝ) * Real.exp (-(r:ℝ)/((a:ℝ)+r+K))^k := by
  intro k
  induction k with
  | zero => intro _; simp
  | succ k ih =>
    intro hk
    have ih' := ih (by omega)
    set q : ℝ := Real.exp (-(r:ℝ)/((a:ℝ)+r+K)) with hq
    have hq0 : 0 ≤ q := (Real.exp_pos _).le
    have hden : (0:ℝ) < (a:ℝ)+r+K := by
      have : (1:ℝ) ≤ (K:ℝ) := by exact_mod_cast (by omega : 1 ≤ K)
      positivity
    have hkK : (k:ℝ)+1 ≤ (K:ℝ) := by exact_mod_cast hk
    -- One factor: a+k+1 ≤ (a+r+k+1) q.
    have hstep : (a:ℝ)+k+1 ≤ ((a:ℝ)+r+k+1)*q := by
      have hexp : 1 - (r:ℝ)/((a:ℝ)+r+K) ≤ q := by
        have h := Real.add_one_le_exp (-(r:ℝ)/((a:ℝ)+r+K))
        rw [hq]
        have hneg : -(r:ℝ)/((a:ℝ)+r+K) = -((r:ℝ)/((a:ℝ)+r+K)) := neg_div _ _
        linarith
      have hratio : ((a:ℝ)+r+k+1)/((a:ℝ)+r+K) ≤ 1 := by
        rw [div_le_one hden]
        linarith
      have hr0 : (0:ℝ) ≤ (r:ℝ) := Nat.cast_nonneg _
      have hpos : (0:ℝ) ≤ (a:ℝ)+r+k+1 := by positivity
      have h1 : ((a:ℝ)+r+k+1)*(1 - (r:ℝ)/((a:ℝ)+r+K)) ≤ ((a:ℝ)+r+k+1)*q :=
        mul_le_mul_of_nonneg_left hexp hpos
      have h2 : ((a:ℝ)+r+k+1)*(1 - (r:ℝ)/((a:ℝ)+r+K)) =
          ((a:ℝ)+r+k+1) - (r:ℝ)*(((a:ℝ)+r+k+1)/((a:ℝ)+r+K)) := by ring
      have h3 : (r:ℝ)*(((a:ℝ)+r+k+1)/((a:ℝ)+r+K)) ≤ (r:ℝ) := by
        simpa using mul_le_mul_of_nonneg_left hratio hr0
      linarith
    -- Absorption identities, cast to the reals.
    have hA : ((a:ℝ)+k+1)*(((a+k).choose k : ℕ) : ℝ) =
        (((a+(k+1)).choose (k+1) : ℕ) : ℝ)*((k:ℝ)+1) := by
      exact_mod_cast Nat.add_one_mul_choose_eq (a+k) k
    have hB : ((a:ℝ)+r+k+1)*(((a+r+k).choose k : ℕ) : ℝ) =
        (((a+r+(k+1)).choose (k+1) : ℕ) : ℝ)*((k:ℝ)+1) := by
      exact_mod_cast Nat.add_one_mul_choose_eq (a+r+k) k
    have hk1 : (0:ℝ) < (k:ℝ)+1 := by positivity
    have hA0 : (0:ℝ) ≤ (((a+k).choose k : ℕ) : ℝ) := Nat.cast_nonneg _
    have hB0 : (0:ℝ) ≤ (((a+r+k).choose k : ℕ) : ℝ)*q^k :=
      mul_nonneg (Nat.cast_nonneg _) (pow_nonneg hq0 k)
    have hak : (0:ℝ) ≤ (a:ℝ)+k+1 := by positivity
    have hchain : (((a+(k+1)).choose (k+1) : ℕ) : ℝ)*((k:ℝ)+1) ≤
        ((((a+r+(k+1)).choose (k+1) : ℕ) : ℝ)*q^(k+1))*((k:ℝ)+1) := by
      calc
        _ = ((a:ℝ)+k+1)*(((a+k).choose k : ℕ) : ℝ) := hA.symm
        _ ≤ ((a:ℝ)+k+1)*((((a+r+k).choose k : ℕ) : ℝ)*q^k) :=
          mul_le_mul_of_nonneg_left ih' hak
        _ ≤ (((a:ℝ)+r+k+1)*q)*((((a+r+k).choose k : ℕ) : ℝ)*q^k) :=
          mul_le_mul_of_nonneg_right hstep hB0
        _ = (((a:ℝ)+r+k+1)*(((a+r+k).choose k : ℕ) : ℝ))*q^(k+1) := by ring
        _ = _ := by rw [hB]; ring
    exact le_of_mul_le_mul_right hchain hk1

/-- The proof-size criterion in density form. -/
theorem generic_CNF_density_bound {σ J : Type} [Fintype σ] [Fintype J] {S : ℕ}
    (I : Set (FiniteParityClause σ)) (C : Fin S → FiniteParityClause σ)
    (dag : AffineDAG I C) (finish : Fin S) (hempty : C finish = ∅)
    (A : J → FiniteParityClause σ) (w : ℕ) (hwidth : ∀ j, (A j).card ≤ w)
    (cover : ∀ D ∈ I, ∃ j, MathResearch.clauseEntails (A j) D)
    (old : Set (Poly (ZMod 2) σ)) (hF : booleanBase ⊆ old)
    (hold : ∀ j, clauseFalsityPolynomial (A j) ∈ old)
    (h k : ℕ) (hh : 1 ≤ h) (hk : 1 ≤ k) (hv : h*(k+1)+1 ≤ Fintype.card σ)
    (U : Submodule (ZMod 2) (MvPolynomial σ (ZMod 2))) (hU : ∀ p ∈ U, p.totalDegree ≤ k)
    (hsep : ∀ f ∈ U, Derives old (k*(max (2*h+w) (4*h+1)+1)) f → f = 0) :
    ((Module.finrank (ZMod 2) U : ℕ) : ℝ) ≤
      ((3*S + Fintype.card J : ℕ) : ℝ) * (((Fintype.card σ + k).choose k : ℕ) : ℝ) *
        Real.exp (-(((h*(k+1)+1 : ℕ) : ℝ) * (k:ℝ)) / ((Fintype.card σ : ℝ) + k)) := by
  have hcrit := generic_CNF_subspace_criterion I C dag finish hempty A w hwidth cover old hF hold
    h k hh hk U hU hsep
  obtain ⟨a,ha⟩ : ∃ a, Fintype.card σ = a + (h*(k+1)+1) := ⟨_, (Nat.sub_add_cancel hv).symm⟩
  have hsub : Fintype.card σ - (h*(k+1)+1) = a := by omega
  rw [hsub] at hcrit
  have hbin := choose_restriction_exp_bound a (h*(k+1)+1) k k le_rfl
  rw [← Real.exp_nat_mul] at hbin
  have hexp : (k:ℝ) * (-(((h*(k+1)+1 : ℕ) : ℝ)) / ((a:ℝ) + ((h*(k+1)+1 : ℕ) : ℝ) + k)) =
      -(((h*(k+1)+1 : ℕ) : ℝ) * (k:ℝ)) / ((Fintype.card σ : ℝ) + k) := by
    rw [ha]
    push_cast
    ring
  rw [hexp, ← ha] at hbin
  have hcritR : ((Module.finrank (ZMod 2) U : ℕ) : ℝ) ≤
      ((3*S + Fintype.card J : ℕ) : ℝ) * (((a+k).choose k : ℕ) : ℝ) := by
    exact_mod_cast hcrit
  have hN : (0:ℝ) ≤ ((3*S + Fintype.card J : ℕ) : ℝ) := Nat.cast_nonneg _
  calc
    _ ≤ ((3*S + Fintype.card J : ℕ) : ℝ) * (((a+k).choose k : ℕ) : ℝ) := hcritR
    _ ≤ ((3*S + Fintype.card J : ℕ) : ℝ) * ((((Fintype.card σ + k).choose k : ℕ) : ℝ) *
        Real.exp (-(((h*(k+1)+1 : ℕ) : ℝ) * (k:ℝ)) / ((Fintype.card σ : ℝ) + k))) :=
      mul_le_mul_of_nonneg_left hbin hN
    _ = _ := by ring

/-- The same bound with the simpler, weaker exponent `-h k²/(v+k)`. -/
theorem generic_CNF_density_bound_simple {σ J : Type} [Fintype σ] [Fintype J] {S : ℕ}
    (I : Set (FiniteParityClause σ)) (C : Fin S → FiniteParityClause σ)
    (dag : AffineDAG I C) (finish : Fin S) (hempty : C finish = ∅)
    (A : J → FiniteParityClause σ) (w : ℕ) (hwidth : ∀ j, (A j).card ≤ w)
    (cover : ∀ D ∈ I, ∃ j, MathResearch.clauseEntails (A j) D)
    (old : Set (Poly (ZMod 2) σ)) (hF : booleanBase ⊆ old)
    (hold : ∀ j, clauseFalsityPolynomial (A j) ∈ old)
    (h k : ℕ) (hh : 1 ≤ h) (hk : 1 ≤ k) (hv : h*(k+1)+1 ≤ Fintype.card σ)
    (U : Submodule (ZMod 2) (MvPolynomial σ (ZMod 2))) (hU : ∀ p ∈ U, p.totalDegree ≤ k)
    (hsep : ∀ f ∈ U, Derives old (k*(max (2*h+w) (4*h+1)+1)) f → f = 0) :
    ((Module.finrank (ZMod 2) U : ℕ) : ℝ) ≤
      ((3*S + Fintype.card J : ℕ) : ℝ) * (((Fintype.card σ + k).choose k : ℕ) : ℝ) *
        Real.exp (-((h:ℝ) * (k:ℝ)^2) / ((Fintype.card σ : ℝ) + k)) := by
  refine (generic_CNF_density_bound I C dag finish hempty A w hwidth cover old hF hold h k hh hk
    hv U hU hsep).trans ?_
  apply mul_le_mul_of_nonneg_left _ (by positivity)
  apply Real.exp_le_exp.mpr
  have hden : (0:ℝ) < (Fintype.card σ : ℝ) + k := by
    have : (1:ℝ) ≤ (k:ℝ) := by exact_mod_cast hk
    positivity
  rw [div_le_div_iff_of_pos_right hden]
  have hh0 : (0:ℝ) ≤ (h:ℝ) := Nat.cast_nonneg _
  have hk0 : (0:ℝ) ≤ (k:ℝ) := Nat.cast_nonneg _
  push_cast
  nlinarith [mul_nonneg hh0 hk0, mul_nonneg (mul_nonneg hh0 hk0) hk0]

end
end MathResearch.PolynomialCalculus
