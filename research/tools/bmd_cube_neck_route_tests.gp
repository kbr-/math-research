\\ Route-review tests (30 September 2026; review bmd-20260930-zz).
\\ (1) Restricted spanning: among the fully clean F-curve types of bmd_cube_fcurve_fullclean.gp (same rules, copied
\\     below), keep those with at most one part >= 3, so every neck (n_i, n_j) has min(n_i, n_j) <= 2 and is covered
\\     by thm:cube-two-n-volume (with the multi-cluster lemma for (1,n) necks).  Do they span
\\     N_1(M_(0,N)-bar)^(S_N) for 11 <= N <= 60?  Also report the rank with at most two parts >= 3.
\\ (2) D_n of thm:cube-two-n-volume at c_k = k for 2 <= n <= 60 (exact): nonzero values extend cor:cube-two-n-limit-small.
\\ (3) Markov test for a triple cluster: for real b1 < b2 < b3, the Hankel determinants det[mu_(i+j)] (sizes 1..8) of
\\     the Taylor coefficients mu_k of (sqrt((1 - b_j v)/(1 - b_1 v)) - 1)/v, j = 2, 3, after the sign flip sign(mu_1),
\\     are positive, consistent with each being a Markov function (Cauchy transform of a positive measure on
\\     [b_1, b_j]); a finite check only.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
fb(P, k, N) = my(c = 0); foreach ([[1, 2], [1, 3], [1, 4]], ij, my(t = P[ij[1]] + P[ij[2]]); if (t == k || t == N - k, c++)); for (i = 1, 4, if (P[i] == k || P[i] == N - k, c--)); c;
phi(k) = if (k == 1, 1, k - 2);
minfixperm(S, perms) = {
  my(best = oo);
  foreach (perms, t,
    my(ok = 1); for (i = 1, #S, if (S[t[i]] != S[i] || t[t[i]] != i, ok = 0));
    if (ok, my(isid = (t == vector(#S, i, i)));
      if (!isid || vecmax(S) >= 2, best = min(best, sum(i = 1, #S, if (t[i] == i, phi(S[i]), 0))))));
  best;
}
allperms(n) = my(L = List()); forperm(n, p, listput(L, Vec(p))); Vec(L);
P4 = allperms(4); P3 = allperms(3);
interior(P) = minfixperm(P, P4);
special(P) = {
  my(best = oo, ones = select(x -> x == 1, P));
  foreach ([[1, 2, 3, 4], [1, 3, 2, 4], [1, 4, 2, 3]], pr,
    my(X = P[pr[1]], Y = P[pr[2]], Z = P[pr[3]], W = P[pr[4]]);
    if (#ones == 0,
      my(perms = [[1,2,3,4],[2,1,3,4],[1,2,4,3],[2,1,4,3],[3,4,1,2],[4,3,1,2],[3,4,2,1],[4,3,2,1]]);
      best = min(best, minfixperm([X, Y, Z, W], perms)),
      my(S = if (X == 1, [1 + Y, Z, W], if (Y == 1, [1 + X, Z, W], if (Z == 1, [1 + W, X, Y], [1 + Z, X, Y]))));
      best = min(best, minfixperm(S, P3))));
  best;
}
E(c) = prod(k = 1, #c, 'y - c[k]);
Dn(n, c) = {
  my(EE = E(c), F = n * EE - 'y * deriv(EE, 'y), a = (n + 1) \ 2, bb = 2 * n - a - 1);
  my(rows = vector(bb - n + 1, i, my(m = n + i - 1, R = intformal('y^(m - n) * F, 'y) % EE); vector(n - a, j, polcoef(R, a + j - 1, 'y))));
  if (#rows == 0, 1, matdet(Mat(Vec(rows)~)));
}
main() = {
  my(fail1 = List(), fail2 = List());
  for (N = 11, 60, my(K = N \ 2, f = N % 2, parts = List(), c1 = List(), c2 = List());
    forpart(p = N, listput(parts, Vec(p)), [1, N], [4, 4]);
    foreach (parts, P, if (#select(x -> x == 1, P) <= 1 && interior(P) > f && special(P) > f,
      my(big = #select(x -> x >= 3, P)); if (big <= 1, listput(c1, P)); if (big <= 2, listput(c2, P))));
    my(r1 = if (#c1, matrank(matrix(#c1, K - 1, i, j, fb(c1[i], j + 1, N))), 0), r2 = if (#c2, matrank(matrix(#c2, K - 1, i, j, fb(c2[i], j + 1, N))), 0));
    if (N <= 16 || N % 10 == 0, emit(Str("N=", N, ": clean types with <= 1 part >= 3: ", Vec(c1), " rank ", r1, "; with <= 2 parts >= 3: ", #c2, " types, rank ", r2, "; needed ", K - 1)));
    if (r1 < K - 1, listput(fail1, N)); if (r2 < K - 1, listput(fail2, N)));
  emit(Str("(1) restricted (<= 1 part >= 3) fails to span at N = ", Vec(fail1)));
  emit(Str("(1) restricted (<= 2 parts >= 3) fails to span at N = ", Vec(fail2)));
  my(zero = List()); for (n = 2, 60, if (Dn(n, vector(n, k, k)) == 0, listput(zero, n)));
  emit(Str("(2) D_n(c_k = k) = 0 for n in ", Vec(zero), " (2 <= n <= 60)"));
  foreach ([[-2, 1, 3], [0, 1, 5], [-1, 2, 7]], b,
    my(K = 17, ok = 1);
    for (j = 2, 3, my(f = ((1 - b[j] * x + O(x^(K + 1))) / (1 - b[1] * x + O(x^(K + 1))))^(1/2), mu = vector(K - 1, k, polcoef(f, k, x)));
      \\ Stieltjes normalization: (f - 1)/v = sum mu_(k+1) v^k; test positivity of the Hankel determinants of sign-adjusted moments
      my(s = sign(mu[1]), hs = vector(8, m, matdet(matrix(m, m, i, jj, s * mu[i + jj - 1]))));
      emit(Str("(3) b = ", b, ", ratio j = ", j, ": Hankel determinants sizes 1..8 signs ", apply(sign, hs))));
  );
}
default(parisizemax, 2000000000);
main();
quit
