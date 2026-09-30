\\ Symmetric F-curve spanning sets on M_(0,N)-bar (30 September 2026; cycle bmd-20260930-zp).
\\ For an F-curve with partition (n1,n2,n3,n4) of the N marked points, the intersection with a boundary divisor
\\ Delta_S is 1 if S or its complement is n_i u n_j (i != j), -1 if S or its complement is one part n_i, and 0
\\ otherwise (Keel and McKernan, Contractible extremal rays on M_(0,n)-bar).  For the S_N-symmetric divisors
\\ B_k = sum_(|S| = k, S up to complement) Delta_S, 2 <= k <= floor(N/2), which span Pic(M_(0,N)-bar / S_N) (x) Q,
\\ F.B_k = #{i<j : n_i + n_j in {k, N-k}} - #{i : n_i in {k, N-k}}, counting each unordered split once.
\\ Question: for 5 <= N <= 16, is the rank of [F_P . B_k] over all partitions P equal to floor(N/2) - 1, and do the
\\ partitions (1,1,m,N-2-m), 1 <= m <= (N-2)/2, already span?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
fb(P, k, N) = {
  my(pairs = List(), c = 0);
  \\ the three splits {i,j} | {complement}: each unordered split counted once
  foreach ([[1, 2], [1, 3], [1, 4]], ij, my(t = P[ij[1]] + P[ij[2]]); if (t == k || t == N - k, c++));
  for (i = 1, 4, if (P[i] == k || P[i] == N - k, c--));
  c;
}
main() = {
  for (N = 5, 16,
    my(K = N \ 2, parts = List());
    forpart(p = N, listput(parts, Vec(p)), [1, N], [4, 4]);
    my(M = matrix(#parts, K - 1, i, j, fb(parts[i], j + 1, N)));
    my(fam = List()); for (m = 1, (N - 2) \ 2, listput(fam, [1, 1, m, N - 2 - m]));
    my(Mf = matrix(#fam, K - 1, i, j, fb(fam[i], j + 1, N)));
    emit(Str("N=", N, ": floor(N/2)-1 = ", K - 1, "; rank over all ", #parts, " partitions ", matrank(M),
      "; rank of the family (1,1,m,N-2-m) (", #fam, " curves) ", matrank(Mf))));
  \\ the family alone, for 17 <= N <= 400
  my(bad = List());
  for (N = 17, 400, my(K = N \ 2, fam = vector((N - 2) \ 2, m, [1, 1, m, N - 2 - m]));
    if (matrank(matrix(#fam, K - 1, i, j, fb(fam[i], j + 1, N))) != K - 1, listput(bad, N)));
  emit(Str("family (1,1,m,N-2-m) spans for 17 <= N <= 400 except: ", Vec(bad)));
}
main();
quit
