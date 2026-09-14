/-
Claim: lem:mp-telescoping
Source: https://kbr.is-a.dev/math-research/#mp-telescoping
Scope: Explicit telescoping identity and joint total-degree bounds for coefficients and companions, for finite indexed inputs over any commutative ring. Coefficients may be any polynomials of degree at most one. The source's exact companion-degree equality is replaced by the valid upper bound and refuted when δ is merely an upper bound.
Declarations: MathResearch.mp_telescoping MathResearch.mp_coefficient_degree MathResearch.mp_companion_degree MathResearch.mp_companion_equality_counterexample
-/
import Mathlib.Algebra.MvPolynomial.CommRing
import Mathlib.Tactic.Ring

namespace MathResearch
noncomputable section
open MvPolynomial
open scoped BigOperators

variable {R ι σ : Type*} [CommRing R] [Fintype ι]

def ensProduct (f : ι → R) (r : ℕ → ι → R) (h : ℕ) : R :=
  ∏ v ∈ Finset.range h, (1 - ∑ i, r v i * f i)

def ensCoefficient (f : ι → R) (r : ℕ → ι → R) (h : ℕ) (i : ι) : R :=
  ∑ v ∈ Finset.range h, r v i * ensProduct f r v

theorem mp_telescoping (f : ι → R) (r : ℕ → ι → R) (h : ℕ) :
    1 - ensProduct f r h = ∑ i, ensCoefficient f r h i * f i := by
  induction h with
  | zero => simp [ensProduct, ensCoefficient]
  | succ h ih =>
    have hp : ensProduct f r (h + 1) =
        ensProduct f r h * (1 - ∑ i, r h i * f i) := by
      simp only [ensProduct, Finset.prod_range_succ]
    have hc (i : ι) : ensCoefficient f r (h + 1) i =
        ensCoefficient f r h i + r h i * ensProduct f r h := by
      simp only [ensCoefficient, Finset.sum_range_succ]
    simp_rw [hc, add_mul]
    rw [Finset.sum_add_distrib, ← ih, hp]
    have hs : (∑ i, r h i * ensProduct f r h * f i) =
        ensProduct f r h * ∑ i, r h i * f i := by
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro i _
      ring
    rw [hs]
    ring

variable (f : ι → MvPolynomial σ R) (r : ℕ → ι → MvPolynomial σ R)
variable (δ h : ℕ)

lemma ensProduct_degree
    (hf : ∀ i, (f i).totalDegree ≤ δ)
    (hr : ∀ v < h, ∀ i, (r v i).totalDegree ≤ 1) :
    (ensProduct f r h).totalDegree ≤ h * (δ + 1) := by
  apply (totalDegree_finsetProd _ _).trans
  calc
    _ ≤ ∑ _v ∈ Finset.range h, (δ + 1) := by
      apply Finset.sum_le_sum
      intro v hv
      apply (totalDegree_sub _ _).trans
      apply max_le
      · simp
      · apply totalDegree_finsetSum_le
        intro i _
        exact (totalDegree_mul _ _).trans (by
          simpa [Nat.add_comm] using Nat.add_le_add (hr v (Finset.mem_range.mp hv) i) (hf i))
    _ = h * (δ + 1) := by simp

theorem mp_coefficient_degree (i : ι)
    (hf : ∀ j, (f j).totalDegree ≤ δ)
    (hr : ∀ v < h, ∀ j, (r v j).totalDegree ≤ 1) :
    (ensCoefficient f r h i).totalDegree ≤ 1 + (h - 1) * (δ + 1) := by
  apply totalDegree_finsetSum_le
  intro v hv
  have vh : v < h := Finset.mem_range.mp hv
  have hd := ensProduct_degree f r δ v hf (fun w hw j => hr w (lt_trans hw vh) j)
  apply (totalDegree_mul _ _).trans
  exact (Nat.add_le_add (hr v vh i) hd).trans
    (Nat.add_le_add_left (Nat.mul_le_mul_right (δ + 1) (by omega : v ≤ h - 1)) 1)

theorem mp_companion_degree (i : ι)
    (hf : ∀ j, (f j).totalDegree ≤ δ)
    (hr : ∀ v < h, ∀ j, (r v j).totalDegree ≤ 1) :
    (f i * ensProduct f r h).totalDegree ≤ (f i).totalDegree + h * (δ + 1) := by
  exact (totalDegree_mul _ _).trans
    (Nat.add_le_add_left (ensProduct_degree f r δ h hf hr) _)

/- With h = 1, one constant input f = 1, and the legitimate loose bound δ = 1,
the source's proposed degree equality would give 2 instead of at most 1. -/
theorem mp_companion_equality_counterexample [Nontrivial R] :
    let f : Fin 1 → MvPolynomial (Fin 1) R := fun _ => 1
    let r : ℕ → Fin 1 → MvPolynomial (Fin 1) R := fun _ _ => X 0
    (∀ i, (f i).totalDegree ≤ 1) ∧
    (∀ v < 1, ∀ i, (r v i).totalDegree ≤ 1) ∧
    (f 0 * ensProduct f r 1).totalDegree ≠ (f 0).totalDegree + 1 * (1 + 1) := by
  dsimp
  refine ⟨by simp, by simp, ?_⟩
  have bound := mp_companion_degree
    (fun _ : Fin 1 => (1 : MvPolynomial (Fin 1) R))
    (fun (_ : ℕ) (_ : Fin 1) => (X 0 : MvPolynomial (Fin 1) R)) 0 1 0
    (by simp) (by simp)
  simp only [totalDegree_one, zero_add, zero_add, mul_one, zero_add] at bound ⊢
  omega

end
end MathResearch
