import OAI.NumberTheory.DirichletL.Energy.CertifiedExistence
import OAI.NumberTheory.DirichletL.Detector.FinalAssemblyCertifiedBands
import OAI.NumberTheory.DirichletL.Moments.DetectorPlainSlotProfile

namespace OAI

noncomputable section
open scoped Classical BigOperators SchwartzMap ContDiff ComplexConjugate

namespace SevenEighths.ProbeFinalAssemblyUnconditional
open ProbeFinalAssembly ProbeFinalAssemblyCertifiedBands
open CenteredMomentEnergyCertifiedExistence CenteredMomentDetectorPlainMomentParameters
open CenteredMomentDetectorPlainSlotProfile

theorem detector_certified_bands:DetectorCertifiedBands:=by
  intro hβ D _hfine F bΦ hbΦ
  have hp:=fixed_parameters D
  apply terminal_certificate (α:=Fin D.N) F.modulus ⊤ le_top
    (fun x=>conj (F.W x)) 1 2 (1/4) (9/4) bΦ 0 1 (33/50) (33/50) 2
      (kappaPlain D) (stageError D)
  · norm_num
  · exact conjugate_source_support F
  · exact Complex.conjCLE.contDiff.comp (F.W.smooth ⊤)
  · norm_num
  · norm_num
  · norm_num
  · norm_num
  · exact hbΦ
  · norm_num
  · norm_num
  · exact hp.2.2.2.2.1.le
  · exact hp.2.2.1
  · linarith
  · unfold kappaPlain
    linarith

theorem dirichlet_nonzero (q:ℕ)(hq:q≠0)(χ:DirichletCharacter ℂ q)(s:ℂ)
    (hs:(7/8:ℝ)<s.re)(hexc:¬(χ=1 ∧ s=1)):
    letI:NeZero q:=⟨hq⟩
    DirichletCharacter.LFunction χ s≠0:=
  dirichlet_of_certified detector_certified_bands q hq χ s hs hexc

theorem zeta_nonzero (s:ℂ)(hs:(7/8:ℝ)<s.re):riemannZeta s≠0:=
  zeta_of_certified detector_certified_bands s hs

end SevenEighths.ProbeFinalAssemblyUnconditional

end

end OAI
