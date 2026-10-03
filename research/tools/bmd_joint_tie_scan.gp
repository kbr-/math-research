\\ Joint-tie scan above a cone tie at a Gegenbauer zero (cycle bmd-20261009-bw, 9 October 2026).
\\ Tested statement (the cherry step's conclusion on cone clusters, no section of L0 vanishing to order R+1 = 16): for
\\ the cherry {1, 1 + c_e s^b} above the cone cluster with actual roots x1 s (c(s), 1, 2 s^2, 5 s^4), c(s) = -1 + s (a tie
\\ moving into the Gegenbauer zero c0 = -1 of t_1, over a caterpillar of m = 2 roots), the C-block ties at the cluster
\\ rate 1 (review test bmd-20261009-bs); scanning the cherry rate b = 1..10, c_e in {3, -2, 1/2} and x1 in {1, 2, -3},
\\ every exact limit space has orders <= 15. Reports orders, weight and any CONTACT (max order >= 16).
OUT = "research/results/bmd-20261009-bw/joint-tie-scan.txt";
default(parisizemax, 4 * 10^9);
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
limitorders(rts, K) = {
  my(n = #rts, R = n * (n - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, n, for (j = i + 1, n, r++; my(h = H(rts[i], rts[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  for (step = 1, R,
    my(bi = 0, bj = 0, bv = 1e9);
    for (i = step, R, for (j = 1, K + 1, if (P[i, j] != 0, my(vv = valuation(P[i, j], 's)); if (vv < bv || (vv == bv && j < bj), bv = vv; bi = i; bj = j))));
    my(tmp = P[step, ]); P[step, ] = P[bi, ]; P[bi, ] = tmp;
    P[step, ] = P[step, ] / P[step, bj];
    for (i = 1, R, if (i != step && P[i, bj] != 0, P[i, ] = P[i, ] - P[i, bj] * P[step, ])));
  my(L = matrix(R, K + 1, i, j, my(z = P[i, j]); if (z == 0, 0, my(vv = valuation(z, 's)); if (vv > 0, 0, if (vv < 0, error("negative valuation"), subst(numerator(z), 's, 0) / subst(denominator(z), 's, 0))))));
  my(A = L, piv = List(), row = 1);
  for (j = 1, K + 1, if (row > R, break); my(p = 0); for (i = row, R, if (A[i, j] != 0, p = i; break));
    if (p, my(t = A[row, ]); A[row, ] = A[p, ]; A[p, ] = t; A[row, ] = A[row, ] / A[row, j];
      for (i = 1, R, if (i != row && A[i, j] != 0, A[i, ] = A[i, ] - A[i, j] * A[row, ])); listput(piv, j - 1); row++));
  Vec(piv);
}
{
  my(K = 19, ncontact = 0, nwt = 0, tot = 0);
  for (b = 1, 10, foreach([3, -2, 1/2], ce, foreach([1, 2, -3], x1,
    my(rts = concat([1, 1 + ce * 's^b], x1 * 's * [-1 + 's, 1, 2 * 's^2, 5 * 's^4]));
    my(o = limitorders(rts, K), wt = vecsum(o) - 105);
    tot++; if (wt > 0, nwt++); if (vecmax(o) > 15, ncontact++);
    write(OUT, "b = ", b, ", c_e = ", ce, ", x1 = ", x1, ": orders ", o, ", weight ", wt, if (vecmax(o) > 15, "  CONTACT", "")))));
  write(OUT, "summary: ", tot, " arcs, ", nwt, " of positive weight, ", ncontact, " with a section of order >= 16");
}
