# Integral homology of chessboard complexes M_{m,n} (faces: partial matchings of an m x n board), by HAP.
# Bridge test of the DAG review (odd-prime thread, 26 Sept 2026): does F_3 homology differ from rational
# homology (3-torsion, Shareshian-Wachs) on the board shapes the record uses (N >= 2t-1) or on PHP shapes
# (t = N+1)? Output: for each (m,n) and degree d, HAP's integral invariants (0 = free Z summand, q = Z/q).
LoadPackage("HAP");
Boards := [[3,4],[3,5],[4,4],[4,5],[4,6],[4,7],[5,5],[5,6],[5,7],[6,6],[6,7]];
out := OutputTextFile("chessboard_homology.txt", false);
SetPrintFormattingStatus(out, false);
for b in Boards do
  m := b[1]; n := b[2]; k := Minimum(m, n);
  faces := [];
  for rows in Combinations([1..m], k) do
    for cols in Arrangements([1..n], k) do
      Add(faces, List([1..k], i -> (rows[i]-1)*n + cols[i]));
    od;
  od;
  K := MaximalSimplicesToSimplicialComplex(faces);
  for d in [0..k-1] do
    h := Homology(K, d);
    AppendTo(out, m, " ", n, " ", d, " ", h, "\n");
    Print(m, " ", n, " ", d, " ", h, "\n");
  od;
od;
CloseStream(out);
QUIT;
