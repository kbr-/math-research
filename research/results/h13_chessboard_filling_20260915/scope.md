# H13 exact filling interface

Target: third-party:BLVZ-chessboard-filling, exactly the existing proposition
MathResearch.ThirdParty.ChessboardFilling, without extra hypotheses. For s≥2
and N≥2s−1, original (s−1)-cell cycles must have original s-cell fillers.

Use H11 stable-range equality nu(s,N)=s, H12 full homological bound, and H03
chessboardChainEquiv with its all-degree boundary compatibility. Handle the
Nat degree identity s−1+1=s explicitly; s=2 retains vertex augmentation.
No new dependency claim or alternative mathematical route is needed.

The proof is in ChessboardFillingProof.lean to avoid an import cycle: foundations
already import the original ChessboardFilling.lean definitions. That original
interface file remains statement-only; the index links the actual proof module.
This is no longer an open theorem once chessboard_filling is verified. Verify
incrementally with Lake's caches as requested; inspect cached types and axioms
without re-elaborating unchanged source proofs. R10 and the remaining publication
route are consumers outside this assignment; proving H does not prove them.
