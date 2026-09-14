/-
Claim: third-party:BLVZ-chessboard-filling
Source: https://kbr.is-a.dev/math-research/#lean-chessboard-filling
Scope: Complete proof of the original ChessboardFilling proposition H over F₂, including s=2 augmentation, with no additional hypotheses or unproved dependencies.
Declarations: MathResearch.ThirdParty.chessboard_filling
-/
import «third-party-claims».ChessboardHomology

namespace MathResearch.ThirdParty
open Augmented
noncomputable section

theorem chessboard_filling : ChessboardFilling := by
  intro s N hs hN c hz
  have hac := chessboard_homological_bound s N (by omega) (by omega)
  rw [chessboardNu_stable_range hN] at hac
  let C := chessboardChainEquiv s N (s-1) c
  have hc : boundary C.val = 0 := (chessboard_cycle_iff s N (s-1) c).mp hz
  obtain ⟨d, hd, hdc⟩ := hac (s-1) (by omega) C.val C.property hc
  have hdegree : s - 1 + 1 = s := by omega
  let D : chains (chessboardComplex s N) s := ⟨d, by
    change Supported (chessboardComplex s N) s d
    simpa [hdegree] using hd⟩
  let b := (chessboardChainEquiv s N s).symm D
  refine ⟨b, ?_⟩
  apply (chessboardChainEquiv s N (s-1)).injective
  apply Subtype.ext
  rw [← chessboard_boundary s N s b]
  have hb : (chessboardChainEquiv s N s b).val = d := by
    dsimp [b]
    rw [LinearEquiv.apply_symm_apply]
  rw [hb]
  exact hdc

end
end MathResearch.ThirdParty
