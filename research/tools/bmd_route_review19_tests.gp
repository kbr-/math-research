\\ Goal-level review tests (cycle bmd-20261009-x, 9 October 2026).
\\ (1) Falsification attempt, exact: the limit pair space L0 (pair matrix rows [T^k]((1+rT)(1+sT))^(-3/2), columns
\\     0..K, elimination of bmd_cherry_limit_space.gp) along the arc of a cherry {1, 1 + e^3} above the equilateral
\\     cluster e^4 (1, w, w^2), w^2 + w + 1 = 0, on the ray w_x/w_e = 4/3 where (W') fails, exact over Q(w)(e).
\\     Tested statement: every vanishing order of L0 is <= R (R = 10 pairs), so the arc avoids K.
\\ (2) Lead test: on the failing rays recorded in hankel-cancellation-wprime.txt, the union of the tied leaders
\\     Lambda_M and Lambda' = Lambda_{M-1} - M + (M+1) has exactly 2M + 1 elements (M = 3, 4), so the leading cross
\\     space lies in a coordinate space of dimension 2M + 1.
\\ (3) Bridge test: Q = sum (y_i - y_j)^2 has a zero with distinct coordinates modulo q = 1000003 at M = 3.
OUT = "research/results/bmd-20261009-x/review-tests.txt";
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
Ev = 'e;
Wv = varlower("ww"); W = Mod(Wv, Wv^2 + Wv + 1);
limitspace(rts, K) = {
  my(n = #rts, R = n * (n - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, n, for (j = i + 1, n, r++; my(h = H(rts[i], rts[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  for (step = 1, R,
    my(bi = 0, bj = 0, bv = 10^9);
    for (i = step, R, for (j = 1, K + 1, if (P[i, j] != 0, my(vv = valuation(P[i, j], 'e)); if (vv < bv || (vv == bv && j < bj), bv = vv; bi = i; bj = j))));
    my(tmp = P[step, ]); P[step, ] = P[bi, ]; P[bi, ] = tmp;
    P[step, ] = P[step, ] / P[step, bj];
    for (i = 1, R, if (i != step && P[i, bj] != 0, P[i, ] = P[i, ] - P[i, bj] * P[step, ])));
  my(L = matrix(R, K + 1, i, j, my(z = P[i, j]); if (z == 0, 0, my(vv = valuation(z, 'e)); if (vv > 0, 0, if (vv < 0, error("negative valuation"), subst(numerator(z), 'e, 0) / subst(denominator(z), 'e, 0))))));
  my(piv = List(), row = 1, B = L, nr = R);
  for (j = 1, K + 1, if (row > nr, break); my(p = 0); for (i = row, nr, if (B[i, j] != 0, p = i; break));
    if (p, my(t = B[row, ]); B[row, ] = B[p, ]; B[p, ] = t; B[row, ] = B[row, ] / B[row, j];
      for (i = 1, nr, if (i != row && B[i, j] != 0, B[i, ] = B[i, ] - B[i, j] * B[row, ])); listput(piv, j - 1); row++));
  Vec(piv);
}
{
  my(rts = concat([1, 1 + 'e^3], 'e^4 * [1, W, W^2]), pv = limitspace(rts, 13));
  write(OUT, "(1) cherry above the equilateral cluster, rates (4, 3), exact over Q(w)(e): R = 10, vanishing orders ", pv, "; all <= R: ", vecmax(pv) <= 10);
  for (M = 3, 4, my(LM = [-M .. M - 1], Lp = setunion(Set([-M + 1 .. M - 1]), [M + 1]));
    write(OUT, "(2) M=", M, ": |Lambda_M u Lambda'| = ", #setunion(Set(LM), Lp), " (2M+1 = ", 2 * M + 1, "), union ", setunion(Set(LM), Lp)));
  \\ y = (0, 1, a): Q = 2(a^2 - a + 1), zero for a = (1 + sqrt(-3))/2 mod q
  my(q = 1000003, r = lift(sqrt(Mod(-3, q))), a = lift((1 + Mod(r, q)) / 2));
  write(OUT, "(3) q = ", q, ": y = (0, 1, a) with a = ", a, " has Q mod q = ", lift(Mod(2 * (1 - a + a^2), q)), " and distinct coordinates mod q: ", a % q != 0 && a % q != 1);
}
