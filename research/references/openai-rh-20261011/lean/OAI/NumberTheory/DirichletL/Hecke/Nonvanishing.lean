import OAI.NumberTheory.DirichletL.Detector.FinalAssemblyUnconditional
import OAI.NumberTheory.DirichletL.Hecke.ConditionalNonvanishing
import OAI.NumberTheory.DirichletL.Hecke.RayFamily

namespace OAI

/-! Finite-order Hecke L-functions over the Eisenstein number field are nonzero to the right of seven eighths, away from the principal pole. -/

noncomputable section

namespace SevenEighths.HeckeFamily

theorem LFunction_ne_zero_of_seven_eighths_lt_re
    (χ : Character) {s : ℂ} (hs : (7 / 8 : ℝ) < s.re)
    (hpole : ¬ (χ.residue = 1 ∧ s = 1)) : LFunction χ s ≠ 0 :=
  LFunction_ne_zero_of_certified_bands
    ProbeFinalAssemblyUnconditional.detector_certified_bands χ hs hpole

theorem LFunction_ofResidue_ne_zero_of_seven_eighths_lt_re
    (M : Ideal O) (hM : M ≠ ⊥) (χ : MulChar (O ⧸ M) ℂ)
    (hu : ∀ u : Oˣ, χ (Ideal.Quotient.mk M (u : O)) = 1)
    {s : ℂ} (hs : (7 / 8 : ℝ) < s.re) (hpole : ¬ (χ = 1 ∧ s = 1)) :
    LFunction (Character.ofResidue M hM χ hu) s ≠ 0 :=
  LFunction_ne_zero_of_seven_eighths_lt_re _ hs hpole

end SevenEighths.HeckeFamily

namespace SevenEighths.HeckeRayFamily

variable (M : Ideal HeckeFamily.O) [NeZero M]

local instance : Finite (HeckeFamily.O ⧸ M) :=
  Ring.HasFiniteQuotients.finiteQuotient (NeZero.ne M)

theorem LFunction_ne_zero_of_seven_eighths_lt_re
    (χ : RayOrthogonality.rayCharacters M) {s : ℂ}
    (hs : (7 / 8 : ℝ) < s.re) (hpole : ¬ (χ = 1 ∧ s = 1)) :
    HeckeFamily.LFunction (character M χ) s ≠ 0 := by
  apply HeckeFamily.LFunction_ne_zero_of_seven_eighths_lt_re _ hs
  rintro ⟨hχ, hs1⟩
  exact hpole ⟨(principal_iff M χ).mp hχ, hs1⟩

end SevenEighths.HeckeRayFamily

end

end OAI
