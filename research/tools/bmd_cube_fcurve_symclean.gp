\\ Symmetric-clean F-curve types (30 September 2026; cycle bmd-20260930-zr).
\\ An F-curve of type (a,b,c,d) with caterpillar tails (a tail of size k >= 2 is a chain of k-1 three-pointed
\\ components, the last carrying two marks; size 1 is a mark on the spine).  An automorphism s of a point of it,
\\ permuting the marks by an involution p (a limit of Moebius involutions), induces an involution t of the four tails
\\ that swaps only tails of equal size.  Rules (lem:cube-fcurve-symmetric-obstruction): an invariant tail of size 1
\\ is a fixed mark; an invariant tail of size k >= 2 has its first k-2 components fixed pointwise (three fixed special
\\ points), each with a fixed mark, so it contributes at least k-2 fixed marks, and exactly k-2 when its last
\\ component swaps its two marks; swapped tails contribute none.  t = identity needs a nontrivial swap inside a tail.
\\ The type is "clean" when every such s has more than f fixed marks, f = N mod 2 (the involutions with a non-branch
\\ fixed point: none fixed for even N, one for odd N).  Question: for 7 <= N <= 60, do the clean types span
\\ N_1(M_(0,N)-bar)^(S_N) (rank floor(N/2)-1 of [F.B_k])?  And which members of (1,1,m,N-2-m) are not clean?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
fb(P, k, N) = my(c = 0); foreach ([[1, 2], [1, 3], [1, 4]], ij, my(t = P[ij[1]] + P[ij[2]]); if (t == k || t == N - k, c++)); for (i = 1, 4, if (P[i] == k || P[i] == N - k, c--)); c;
fixmin(k) = if (k == 1, 1, k - 2);
\\ minimal fixed marks over nontrivial symmetric structures, oo if none
minfix(P) = {
  my(best = oo);
  \\ t = identity: needs some tail of size >= 2 whose last component swaps (nontrivial p)
  if (vecmax(P) >= 2, best = min(best, sum(i = 1, 4, fixmin(P[i]))));
  \\ one 2-cycle (i j) with P[i] == P[j]
  for (i = 1, 4, for (j = i + 1, 4, if (P[i] == P[j], best = min(best, sum(h = 1, 4, if (h != i && h != j, fixmin(P[h]), 0))))));
  \\ two 2-cycles
  foreach ([[1, 2, 3, 4], [1, 3, 2, 4], [1, 4, 2, 3]], pr, if (P[pr[1]] == P[pr[2]] && P[pr[3]] == P[pr[4]], best = 0));
  best;
}
main() = {
  my(badrank = List());
  for (N = 7, 60,
    my(K = N \ 2, f = N % 2, parts = List(), clean = List());
    forpart(p = N, listput(parts, Vec(p)), [1, N], [4, 4]);
    foreach (parts, P, if (minfix(P) > f, listput(clean, P)));
    my(r = if (#clean, matrank(matrix(#clean, K - 1, i, j, fb(clean[i], j + 1, N))), 0));
    my(fam = List()); for (m = 1, (N - 2) \ 2, if (minfix([1, 1, m, N - 2 - m]) <= f, listput(fam, m)));
    if (N <= 16, emit(Str("N=", N, ": clean types ", #clean, " of ", #parts, ", rank ", r, " of ", K - 1,
      "; non-clean members m of (1,1,m,N-2-m): ", Vec(fam))));
    if (r < K - 1, listput(badrank, N)));
  emit(Str("clean types fail to span for 7 <= N <= 60 at: ", Vec(badrank)));
  \\ explicit clean family: (1,1,m,N-2-m), m < (N-2)/2, plus (1,2,3,N-6) for even N; all clean and spanning?
  my(bad2 = List());
  for (N = 8, 400, my(K = N \ 2, f = N % 2, fam = List());
    for (m = 1, (N - 2) \ 2, if (2 * m != N - 2, listput(fam, [1, 1, m, N - 2 - m])));
    if (N % 2 == 0, listput(fam, vecsort([1, 2, 3, N - 6])));
    my(ok = 1); foreach (fam, P, if (minfix(P) <= f, ok = 0));
    if (!ok || matrank(matrix(#fam, K - 1, i, j, fb(fam[i], j + 1, N))) != K - 1, listput(bad2, N)));
  emit(Str("explicit clean family ((1,1,m,N-2-m), m < (N-2)/2; plus (1,2,3,N-6) for even N) fails for 8 <= N <= 400 at: ", Vec(bad2)));
  \\ for even N: which single clean types complete (1,1,m,N-2-m), m < (N-2)/2, to a spanning set?
  forstep (N = 8, 24, 2, my(K = N \ 2, fam = List(), parts = List(), good = List());
    for (m = 1, (N - 4) \ 2, listput(fam, [1, 1, m, N - 2 - m]));
    forpart(p = N, listput(parts, Vec(p)), [1, N], [4, 4]);
    foreach (parts, P, if (minfix(P) > 0, my(F = concat(Vec(fam), [P]));
      if (matrank(matrix(#F, K - 1, i, j, fb(F[i], j + 1, N))) == K - 1, listput(good, P))));
    emit(Str("  N=", N, ": completing clean types ", Vec(good))));
  \\ candidate uniform completion (2,2,m,N-4-m) with m = (N-4)/2 - 1 (unequal), checked for even 10 <= N <= 400
  my(bad3 = List());
  forstep (N = 10, 400, 2, my(K = N \ 2, F = List());
    for (m = 1, (N - 4) \ 2, listput(F, [1, 1, m, N - 2 - m]));
    my(P = vecsort([2, 2, (N - 4) / 2 - 1, (N - 4) / 2 + 1])); listput(F, P);
    if (minfix(P) <= 0 || matrank(matrix(#F, K - 1, i, j, fb(F[i], j + 1, N))) != K - 1, listput(bad3, N)));
  emit(Str("completion (2,2,(N-4)/2-1,(N-4)/2+1) fails for even 10 <= N <= 400 at: ", Vec(bad3)));
}
default(parisizemax, 2000000000);
main();
quit
