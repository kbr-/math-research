\\ Contact rank at the triple-tie rate (cycle bmd-20261009-y, 9 October 2026); variant of
\\ bmd_tie_moduli_contact_qadic.gp (same q-adic limit-space elimination, q = 1000003).
\\ At the excluded tie modulus c0 = (1 +- 2 sqrt(-2))/3, M = 4, the rate (w_x, w_e) = (1, 1/2) with cluster depths
\\ (1, 2) has three tied leading cross coordinates Lambda_4, Lambda_3 and Lambda' = {-3..3, 5}, whose union has
\\ 2M + 2 = 10 elements (check:cube-cancellation-wprime-trees), outside prop:cube-cherry-step-any-set.
\\ Tested statement: L0 (limit row space of the pair matrix, rows [T^k]((1+rT)(1+sT))^(-3/2), columns 0..K) has every
\\ vanishing order <= R, so rank A_(R+1) = R and the arc avoids K.
\\ Arc, rescaled by 2: a cherry {1, 1 + q} above q^2 (c0, 1, q^2, q^2 + q^4) (rates (2, 1), depths (2, 4)).
\\ Controls: rates (2, 1) with depths (10, 20) (on the ray, two leaders), and c0 = 2 at the triple-tie scaling.
OUT = "research/results/bmd-20261009-y/triple-tie-contact.txt";
q = 1000003; PREC = 200;
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
vq(z) = valuation(z, q);
limitspace(rts, K) = {
  my(n = #rts, R = n * (n - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, n, for (j = i + 1, n, r++; my(h = H(rts[i], rts[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  for (step = 1, R,
    my(bi = 0, bj = 0, bv = 10^9);
    for (i = step, R, for (j = 1, K + 1, if (P[i, j] != 0, my(vv = vq(P[i, j])); if (vv < bv || (vv == bv && j < bj), bv = vv; bi = i; bj = j))));
    my(tmp = P[step, ]); P[step, ] = P[bi, ]; P[bi, ] = tmp;
    P[step, ] = P[step, ] / P[step, bj];
    for (i = 1, R, if (i != step && P[i, bj] != 0, P[i, ] = P[i, ] - P[i, bj] * P[step, ])));
  my(L = matrix(R, K + 1, i, j, my(z = P[i, j]); if (z == 0, Mod(0, q), my(vv = vq(z)); if (vv > 0, Mod(0, q), if (vv < 0, error("negative valuation"), Mod(z, q))))));
  my(piv = List(), row = 1, B = L, nr = R);
  for (j = 1, K + 1, if (row > nr, break); my(p = 0); for (i = row, nr, if (B[i, j] != 0, p = i; break));
    if (p, my(t = B[row, ]); B[row, ] = B[p, ]; B[p, ] = t; B[row, ] = B[row, ] / B[row, j];
      for (i = 1, nr, if (i != row && B[i, j] != 0, B[i, ] = B[i, ] - B[i, j] * B[row, ])); listput(piv, j - 1); row++));
  Vec(piv);
}
{
  my(K = 19, r = sqrt(-2 + O(q^PREC)));
  my(cA = truncate((1 + 2 * r) / 3), cB = truncate((1 - 2 * r) / 3));
  foreach([["triple tie, c0 = (1 + 2 sqrt(-2))/3", cA, 2], ["triple tie, c0 = (1 - 2 sqrt(-2))/3", cB, 2],
           ["control on the ray, two leaders, c0 = (1 + 2 sqrt(-2))/3", cA, 10], ["control: c0 = 2", 2, 2]], G,
    my([name, c0, d] = G);
    my(rts = concat([1, 1 + q], q^2 * [c0, 1, q^d, q^d + q^(2 * d)]));
    my(pv = limitspace(rts, K), R = #rts * (#rts - 1) / 2);
    write(OUT, name, ", depths (", d, ", ", 2 * d, "): R = ", R, ", vanishing orders of L0 ", pv, "; all <= R: ", vecmax(pv) <= R));
}
