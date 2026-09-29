\\ Canonicity of two-cluster flat limits (29 September 2026; cycle bmd-20260929-zzp).
\\ Clusters h*u at 0 (m roots) and 1 + k*v at 1 (m' roots), centred shapes, no other roots, N = m + m'.
\\ Tested general statement (conj:cube-two-cluster-canonical-limit): for comparable scales (k = rho h, rho != 0) and
\\ shapes with nonzero boundary values, the flat limit is independent of the shapes and of rho, and equals
\\ C_(m,m') = Pol_<binom(m,2) + (1+T)^(-3) <Y^w : w < binom(m',2)> + (1+T)^(-3/2) <1, T..T^a, Y..Y^b>,
\\ Y = T/(1+T), for the least a, b with this space of dimension R containing the limit.
\\ Printed per (m, m'): rank of [limit(case 1); limit(case j)] for the other cases (R iff equal), the extreme-scale
\\ case (h, k) = (t, t^2) compared as a control, and the least (a, b) found for case 1.
t; default(seriesprecision, 120);
c(n) = binomial(-3/2, n);
phid(a, r, M) = vector(M + 1, k, my(n = k - 1); if (n < r, 0, c(n) * n! / (n - r)! * a^(n - r)));
prodv(u, v, M) = vector(M + 1, k, sum(q = 1, k, u[q] * v[k + 1 - q]));
row(a, b, M) = prodv(phid(a, 0, M), phid(b, 0, M), M);
vecs(f, M) = vector(M + 1, k, polcoef(f, k - 1, T));
flat(A) =
{
  my(B = A);
  while (1,
    my(B0 = subst(B, t, 0), K = matker(B0~), l, r, v);
    if (#K == 0, return(B0));
    l = K[, 1]; r = 1; while (l[r] == 0, r++);
    v = l~ * B;
    if (subst(v, t, 0) != 0 * v, error("combination not divisible by t"));
    B[r, ] = v / t);
}
limitof(u, v, h, k, M) =
{
  my(roots = concat(h * u, vector(#v, b, 1 + k * v[b])), rows = List(), N = #roots);
  for (a = 1, N, for (b = a + 1, N, listput(rows, row(roots[a], roots[b], M))));
  flat(matconcat(Col(Vec(rows))));
}
cand(m, mp, a, b, M) =
{
  my(Y = T / (1 + T) + O(T^(M + 1)), L = List());
  for (w = 0, binomial(m, 2) - 1, listput(L, vector(M + 1, j, j - 1 == w)));
  for (w = 0, binomial(mp, 2) - 1, listput(L, vecs((1 + T)^(-3) * Y^w + O(T^(M + 1)), M)));
  for (i = 0, a, listput(L, vecs((1 + T)^(-3/2) * T^i + O(T^(M + 1)), M)));
  for (j = 1, b, listput(L, vecs((1 + T)^(-3/2) * Y^j + O(T^(M + 1)), M)));
  matconcat(Col(Vec(L)));
}
{
  my(shapes = Map());
  foreach ([[2, 2], [3, 2], [3, 3], [4, 2], [4, 3]], mm,
    my(m = mm[1], mp = mm[2], N = m + mp, R = binomial(N, 2), M = R + 6, U, V, cases, L1, best = "none");
    U = if (m == 2, [[-1/2, 1/2], [-1, 1]], m == 3, [[-1, 0, 1], [1, 2, -3]], [[-3, -1, 1, 3], [1, 2, 4, -7]]);
    V = if (mp == 2, [[-1/2, 1/2], [-1, 1]], [[-1, 0, 1], [-2, -1, 3]]);
    cases = [[U[1], V[1], t, t], [U[2], V[1], t, t], [U[1], V[2], t, 2 * t], [U[2], V[2], t, 3 * t], [U[1], V[1], t, t^2]];
    L1 = limitof(cases[1][1], cases[1][2], cases[1][3], cases[1][4], M);
    printf("(m,m')=(%d,%d) R=%d:", m, mp, R);
    for (q = 2, #cases, my(L = limitof(cases[q][1], cases[q][2], cases[q][3], cases[q][4], M));
      printf(" case %d: %d;", q, matrank(matconcat([L1; L]))));
    for (s = 0, 2 * N, if (best != "none", break);
      for (a = 0, s, my(b = s - a, C = cand(m, mp, a, b, M));
        if (matrank(matconcat([C; L1])) == matrank(C), best = [a, b, matrank(C)]; break)));
    printf(" least (a,b, dim candidate) containing case 1: %s\n", best));
}
