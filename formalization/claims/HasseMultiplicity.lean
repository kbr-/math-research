/-
Claim: supporting module for third-party:DKSS-multiplicity-schwartz-zippel and thm:binary-multiplicity-degree-formula
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-09-24-lean-multiplicity-schwartz-zippel
Scope: Hasse multiplicity of a formal multivariate polynomial at a point, defined as the order (least total
degree of a nonzero coefficient, ⊤ for zero) of the Taylor shift P(a + x); coefficient characterization,
behaviour under sums, products (superadditive, additive over a domain), constants and renaming.
Declarations: MathResearch.HasseMultiplicity.shift MathResearch.HasseMultiplicity.mult MathResearch.HasseMultiplicity.shift_X MathResearch.HasseMultiplicity.shift_C MathResearch.HasseMultiplicity.shift_neg_shift MathResearch.HasseMultiplicity.shift_injective MathResearch.HasseMultiplicity.mult_eq_top_iff MathResearch.HasseMultiplicity.mult_zero MathResearch.HasseMultiplicity.mult_ne_top MathResearch.HasseMultiplicity.coe_le_mult_iff MathResearch.HasseMultiplicity.mult_le_degree MathResearch.HasseMultiplicity.exists_coeff_ne_zero_degree_eq_mult MathResearch.HasseMultiplicity.min_le_mult_add MathResearch.HasseMultiplicity.add_le_mult_mul MathResearch.HasseMultiplicity.mult_mul MathResearch.HasseMultiplicity.constantCoeff_shift MathResearch.HasseMultiplicity.one_le_mult_iff MathResearch.HasseMultiplicity.mult_eq_zero_iff MathResearch.HasseMultiplicity.shift_rename MathResearch.HasseMultiplicity.mult_comp_le_mult_rename MathResearch.HasseMultiplicity.mult_rename_equiv
-/
import Mathlib.RingTheory.MvPowerSeries.Order
import Mathlib.RingTheory.MvPowerSeries.NoZeroDivisors
import Mathlib.Algebra.MvPolynomial.Rename

namespace MathResearch.HasseMultiplicity

open MvPolynomial

noncomputable section

variable {σ τ R : Type*} [CommRing R]

/-- The Taylor shift `P(x) ↦ P(a + x)`. -/
def shift (a : σ → R) : MvPolynomial σ R →ₐ[R] MvPolynomial σ R :=
  aeval fun i => X i + C (a i)

/-- Hasse multiplicity of `P` at `a`: the least total degree of a monomial of `P(a + z)`,
and `⊤` when `P = 0`. -/
def mult (a : σ → R) (P : MvPolynomial σ R) : ℕ∞ :=
  MvPowerSeries.order ((shift a P : MvPolynomial σ R) : MvPowerSeries σ R)

@[simp] theorem shift_X (a : σ → R) (i : σ) : shift a (X i) = X i + C (a i) := by
  simp [shift]

@[simp] theorem shift_C (a : σ → R) (r : R) : shift a (C r) = C r := by
  simp [shift]

theorem shift_neg_shift (a : σ → R) (P : MvPolynomial σ R) : shift (-a) (shift a P) = P := by
  have h : (shift (-a)).comp (shift a) = AlgHom.id R (MvPolynomial σ R) := by
    apply MvPolynomial.algHom_ext
    intro i
    simp [add_assoc]
  exact AlgHom.congr_fun h P

theorem shift_injective (a : σ → R) : Function.Injective (shift a) := by
  intro P Q h
  rw [← shift_neg_shift a P, ← shift_neg_shift a Q, h]

theorem mult_eq_top_iff (a : σ → R) (P : MvPolynomial σ R) : mult a P = ⊤ ↔ P = 0 := by
  rw [mult, MvPowerSeries.order_eq_top_iff, MvPolynomial.coe_eq_zero_iff]
  constructor
  · intro h
    exact shift_injective a (by rw [h, map_zero])
  · rintro rfl
    exact map_zero _

@[simp] theorem mult_zero (a : σ → R) : mult a (0 : MvPolynomial σ R) = ⊤ :=
  (mult_eq_top_iff a 0).2 rfl

theorem mult_ne_top (a : σ → R) {P : MvPolynomial σ R} (hP : P ≠ 0) : mult a P ≠ ⊤ :=
  fun h => hP ((mult_eq_top_iff a P).1 h)

/-- `n ≤ mult a P` iff every coefficient of `P(a + z)` of total degree below `n` vanishes. -/
theorem coe_le_mult_iff (a : σ → R) (P : MvPolynomial σ R) (n : ℕ) :
    (n : ℕ∞) ≤ mult a P ↔ ∀ d : σ →₀ ℕ, d.degree < n → (shift a P).coeff d = 0 := by
  constructor
  · intro h d hd
    have := MvPowerSeries.coeff_of_lt_order (f := ((shift a P : MvPolynomial σ R) :
      MvPowerSeries σ R)) (d := d) (lt_of_lt_of_le (by exact_mod_cast hd) h)
    simpa [MvPolynomial.coeff_coe] using this
  · intro h
    apply MvPowerSeries.nat_le_order
    intro d hd
    simpa [MvPolynomial.coeff_coe] using h d hd

theorem mult_le_degree (a : σ → R) (P : MvPolynomial σ R) {d : σ →₀ ℕ}
    (h : (shift a P).coeff d ≠ 0) : mult a P ≤ d.degree := by
  apply MvPowerSeries.order_le
  simpa [MvPolynomial.coeff_coe] using h

/-- A monomial of `P(a + z)` of least degree. -/
theorem exists_coeff_ne_zero_degree_eq_mult (a : σ → R) {P : MvPolynomial σ R} (hP : P ≠ 0) :
    ∃ d : σ →₀ ℕ, (shift a P).coeff d ≠ 0 ∧ (d.degree : ℕ∞) = mult a P := by
  have hne : ((shift a P : MvPolynomial σ R) : MvPowerSeries σ R) ≠ 0 := by
    rw [Ne, MvPolynomial.coe_eq_zero_iff]
    intro h
    exact hP (shift_injective a (by rw [h, map_zero]))
  obtain ⟨d, hd, hdeg⟩ := MvPowerSeries.exists_coeff_ne_zero_and_order
    (MvPowerSeries.ne_zero_iff_order_finite.1 hne)
  refine ⟨d, ?_, ?_⟩
  · rwa [MvPolynomial.coeff_coe] at hd
  · exact hdeg

theorem min_le_mult_add (a : σ → R) (P Q : MvPolynomial σ R) :
    min (mult a P) (mult a Q) ≤ mult a (P + Q) := by
  simp only [mult, map_add, MvPolynomial.coe_add]
  exact MvPowerSeries.min_order_le_add

theorem add_le_mult_mul (a : σ → R) (P Q : MvPolynomial σ R) :
    mult a P + mult a Q ≤ mult a (P * Q) := by
  simp only [mult, map_mul, MvPolynomial.coe_mul]
  exact MvPowerSeries.le_order_mul

theorem mult_mul [IsDomain R] (a : σ → R) (P Q : MvPolynomial σ R) :
    mult a (P * Q) = mult a P + mult a Q := by
  simp only [mult, map_mul, MvPolynomial.coe_mul]
  exact MvPowerSeries.order_mul _ _

theorem constantCoeff_shift (a : σ → R) (P : MvPolynomial σ R) :
    constantCoeff (shift a P) = eval a P := by
  induction P using MvPolynomial.induction_on with
  | C r => simp
  | add P Q hP hQ => simp [hP, hQ]
  | mul_X P i hP => simp [hP]

theorem one_le_mult_iff (a : σ → R) (P : MvPolynomial σ R) : 1 ≤ mult a P ↔ eval a P = 0 := by
  rw [show (1 : ℕ∞) = ((1 : ℕ) : ℕ∞) by simp, coe_le_mult_iff, ← constantCoeff_shift,
    constantCoeff_eq]
  constructor
  · intro h
    exact h 0 (by simp)
  · intro h d hd
    have : d = 0 := (Finsupp.degree_eq_zero_iff d).1 (by omega)
    rw [this, h]

theorem mult_eq_zero_iff (a : σ → R) (P : MvPolynomial σ R) : mult a P = 0 ↔ eval a P ≠ 0 := by
  rw [Ne, ← one_le_mult_iff, not_le, Order.lt_one_iff]

theorem shift_rename (e : σ → τ) (a : τ → R) (P : MvPolynomial σ R) :
    shift a (rename e P) = rename e (shift (a ∘ e) P) := by
  have h : (shift a).comp (rename e) = (rename e).comp (shift (a ∘ e)) := by
    apply MvPolynomial.algHom_ext
    intro i
    simp
  exact AlgHom.congr_fun h P

/-- Renaming variables never lowers the multiplicity. -/
theorem mult_comp_le_mult_rename (e : σ → τ) (a : τ → R) (P : MvPolynomial σ R) :
    mult (a ∘ e) P ≤ mult a (rename e P) := by
  show _ ≤ MvPowerSeries.order _
  rw [shift_rename]
  apply MvPowerSeries.le_order
  intro d hd
  rw [MvPolynomial.coeff_coe]
  by_contra hne
  obtain ⟨u, hu, hcoeff⟩ := coeff_rename_ne_zero e _ d hne
  have hdeg : u.degree = d.degree := by
    rw [← hu, Finsupp.degree_mapDomain]
  have := mult_le_degree (a ∘ e) P hcoeff
  rw [hdeg] at this
  exact absurd (lt_of_le_of_lt this hd) (lt_irrefl _)

theorem mult_rename_equiv (e : σ ≃ τ) (a : τ → R) (P : MvPolynomial σ R) :
    mult a (rename e P) = mult (a ∘ e) P := by
  apply le_antisymm
  · have h := mult_comp_le_mult_rename e.symm (a ∘ e) (rename e P)
    rwa [rename_rename, show (a ∘ e) ∘ e.symm = a by ext; simp,
      show (⇑e.symm ∘ ⇑e) = id by ext; simp, rename_id] at h
  · exact mult_comp_le_mult_rename e a P

end

end MathResearch.HasseMultiplicity
