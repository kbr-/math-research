# H06 finite cover double complex

Reuse H01–H05 and chessboard worker's FiniteComplexCover definitions. Finite
coefficients d(J,S) have cover-index count a and vertex count b. Admissibility
requires S in K, S in every L_i for i in J, and J in the vertex-nonempty nerve.
For a=0 these are augmented K chains; for b=0 they are augmented nerve chains.
The horizontal and vertical insertion boundaries commute and square to zero.
For b>0, every horizontal cycle has a horizontal filler: for each fixed S,
cone the index-chain at a selected cover member containing S. This is the H06
row exactness; no spectral sequence or H07 conclusion is assumed.

H07 planned direct proof: induct on b to lift each horizontal cycle d(a,b)
with vertical boundary zero to a horizontal filler u(a+1,b) whose vertical
boundary is zero. For b=0 use nerve exactness. For b>0 first lift horizontally
as x; lift vertical(x) by induction to y; fill y vertically as z in each
intersection; x+horizontal(z) is the desired corrected lift. At a=0 fill that
lift vertically in singleton intersections to fill the original K cycle.
Intersection exactness at cell r for t+r≤ν suffices, matching H11.
Preliminary chain-chase planning during the clean integration pause preceded
this timing session; no duration is retrospectively assigned to that work.
