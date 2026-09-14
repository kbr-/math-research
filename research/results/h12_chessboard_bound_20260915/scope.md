# H12 dependency and scope map

Target third-party:chessboard-homological-bound: for positive natural a,b,
AcyclicThrough (chessboardComplex a b) (chessboardNu a b). This means every
supported k-cell cycle has a (k+1)-cell filling for every k<nu, including
augmentation k=0. It is the F2 homological consequence of BLVZ Theorem1.1
proved in the publication topology appendix, not homotopical connectivity.

Dependencies are integrated and verified H01–H11: supported chain naturality,
cone identity, homological_cover, first-row coverage/cone exactness,
starIntersection_exactAt, firstRowStar_nerve_acyclic, and nu arithmetic.
The one-row augmentation and transpose transport are small local assembly
helpers, not independently asserted new research results. Strong induction on
min(a,b) permits either orientation of smaller intersection boards. The
homological cover interface also supports nu=1, so only the one-row case needs
a separate direct augmentation proof; explain this equivalent organization in
the full human-readable record. No axiom or hypothesis of H is permitted.

H13's stable-range specialization and conversion to the original exact-face
ChessboardFilling interface are a separate next target and research entry.
The entire bit-PHP paper (R01–R25) and main Frege goal remain outside assignment.
