\\ Mark weights of boundary points of X_4 (29 September 2026; review cycle bmd-20260929-zzv).
\\ Tested hypothesis (W^X_4) at the boundary: limits Lambda* of 4-root shape spaces (pair rows phi(a)phi(b),
\\ phi = (1+aT)^(-3/2), k = 6 rows, columns T^0..T^M) along colliding and hierarchical shape arcs have mark weight
\\ at most m - 2 = 2 (weight = sum of the pivot set minus 0+...+5). Falsified if some limit has weight >= 3.
\\ Printed per arc: the pivot set of the exact t-saturated limit over Q[t] and its weight.
t; M = 16;
c(n) = binomial(-3/2, n);
phid(a, r, M) = vector(M + 1, k, my(n = k - 1); if (n < r, 0, c(n) * n! / (n - r)! * a^(n - r)));
prodv(u, v, M) = vector(M + 1, k, sum(q = 1, k, u[q] * v[k + 1 - q]));
row(a, b, M) = prodv(phid(a, 0, M), phid(b, 0, M), M);
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
pivots(L) = { my(E = matrix(#L[, 1], #L, i, j, L[i, j]), H = matimage(E~)~, P = List(), rk = 0);
  for (j = 1, #L, if (matrank(matrix(#L[, 1], j, a, b, L[a, b])) > rk, rk++; listput(P, j - 1)));
  Vec(P); }
{
  foreach ([[0, t, 1, 2], [0, t, 2 * t, 1], [0, t, 1, 1 + t], [0, t, t^2, 1], [0, t, 1 + t, 1 + 2 * t],
            [0, t, 2 * t, 3 * t], [0, t^2, t, 1], [0, 1, 2 + t, 3], [0, 1, 3 + t, 4], [0, t, 1, 1 + t^2]], u,
    my(rows = List(), L, P);
    for (a = 1, 4, for (b = a + 1, 4, listput(rows, row(u[a], u[b], M))));
    L = flat(matconcat(Col(Vec(rows))));
    P = pivots(L);
    printf("shape arc %s: pivot set %s, mark weight %d\n", u, P, vecsum(P) - 15));
}
