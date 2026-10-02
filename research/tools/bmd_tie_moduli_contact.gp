\\ Contact rank on the failing ray above an excluded tie modulus (cycle bmd-20261009-w, 9 October 2026);
\\ variant of bmd_cherry_limit_space.gp (same limit-space elimination).
\\ Tested statement: along the arc, the limit L0 of the row space of the pair matrix (rows [T^k]((1+r T)(1+s T))^(-3/2),
\\ one per pair of roots, columns 0..K) has all vanishing orders <= R = binom(N,2) - 1... precisely: every pivot of L0
\\ is <= R, so rank A_(R+1) = R near the limit and the arc avoids K (lem:cube-contact-plane-criterion setting).
\\ Here R = number of pairs. Arc (eta = e -> 0): a cherry {1, 1 + e^b} above the cluster e^a (c0, 1, e^10, e^10 + e^20),
\\ N = 6, M = 4, a tie over a two-root caterpillar. (a, b) = (2, 1) is rate ratio w_x/w_e = 2 at the scale of the
\\ q-adic test (rates (1/5, 1/10) with depths (1, 2)), where (W') fails at c0 = (1 +- 2 sqrt(-2))/3
\\ (check:cube-cancellation-wprime-trees). Controls: (a, b) = (1, 1) (off the ray) and c0 = 2. Exact over Q(sqrt(-2))(e).
default(parisizemax, 4 * 10^9);
OUT = "research/results/bmd-20261009-w/tie-moduli-contact.txt";
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
Ev = 'e;
Wv = varlower("ww"); SQ = Mod(Wv, Wv^2 + 2);
limitspace(rts, K) = {
  my(n = #rts, R = n * (n - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, n, for (j = i + 1, n, r++; my(h = H(rts[i], rts[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  for (step = 1, R,
    my(bi = 0, bj = 0, bv = 1e9);
    for (i = step, R, for (j = 1, K + 1, if (P[i, j] != 0, my(vv = valuation(P[i, j], 'e)); if (vv < bv || (vv == bv && j < bj), bv = vv; bi = i; bj = j))));
    my(tmp = P[step, ]); P[step, ] = P[bi, ]; P[bi, ] = tmp;
    P[step, ] = P[step, ] / P[step, bj];
    for (i = 1, R, if (i != step && P[i, bj] != 0, P[i, ] = P[i, ] - P[i, bj] * P[step, ])));
  my(L = matrix(R, K + 1, i, j, my(z = P[i, j]); if (z == 0, 0, my(vv = valuation(z, 'e)); if (vv > 0, 0, if (vv < 0, error("negative valuation"), subst(numerator(z), 'e, 0) / subst(denominator(z), 'e, 0))))));
  matrref(L);
}
matrref(L) = {
  my(A = L, piv = List(), row = 1, nr = #A[, 1]);
  for (j = 1, #A, if (row > nr, break); my(p = 0); for (i = row, nr, if (A[i, j] != 0, p = i; break));
    if (p, my(t = A[row, ]); A[row, ] = A[p, ]; A[p, ] = t; A[row, ] = A[row, ] / A[row, j];
      for (i = 1, nr, if (i != row && A[i, j] != 0, A[i, ] = A[i, ] - A[i, j] * A[row, ])); listput(piv, j - 1); row++));
  [A, Vec(piv)];
}
{
  my(K = 19, cA = (1 + 2 * SQ) / 3, cB = (1 - 2 * SQ) / 3);
  foreach([["c0 = (1 + 2 sqrt(-2))/3", cA, 2, 1], ["c0 = (1 - 2 sqrt(-2))/3", cB, 2, 1],
           ["control off the ray: c0 = (1 + 2 sqrt(-2))/3", cA, 1, 1], ["control: c0 = 2", 2, 2, 1]], G,
    my([name, c0, a, b] = G);
    my(rts = concat([1, 1 + 'e^b], 'e^a * [c0, 1, 'e^10, 'e^10 + 'e^20]));
    my(res = limitspace(rts, K), R = #rts * (#rts - 1) / 2);
    write(OUT, name, ", (a, b) = ", [a, b], ": R = ", R, ", vanishing orders of L0 ", res[2], "; all <= R: ", vecmax(res[2]) <= R));
}
