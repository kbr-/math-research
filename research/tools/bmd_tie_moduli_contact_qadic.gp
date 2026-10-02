\\ Contact rank on the failing ray above an excluded tie modulus, q-adic (cycle bmd-20261009-w, 9 October 2026);
\\ q-adic version of bmd_tie_moduli_contact.gp (whose exact run over Q(sqrt(-2))(e) exceeded 600 s).
\\ Tested statement: the limit L0 of the row space of the pair matrix (rows [T^k]((1+r T)(1+s T))^(-3/2), one per pair
\\ of roots, columns 0..K) has every vanishing order (pivot) <= R = number of pairs, so rank A_(R+1) = R near the limit
\\ and the arc avoids K. The arc parameter eta is read as q = 1000003 (valuation-pivoted elimination over Q, limit read
\\ modulo q), as in the record's q-adic tests. Arc: a cherry {1, 1 + q^b} above the cluster q^a (c0, 1, q^10, q^10 + q^20),
\\ N = 6, M = 4. (a, b) = (2, 1) lies on the ray w_x/w_e = 2 where (W') fails at c0 = (1 +- 2 sqrt(-2))/3
\\ (check:cube-cancellation-wprime-trees); c0 is an integer congruent to that q-adic number mod q^PREC.
\\ Controls: (a, b) = (1, 1) (off the ray), and c0 = 2.
OUT = "research/results/bmd-20261009-w/tie-moduli-contact-qadic.txt";
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
  \\ pivots of the row echelon form over F_q
  my(piv = List(), row = 1, B = L, nr = R);
  for (j = 1, K + 1, if (row > nr, break); my(p = 0); for (i = row, nr, if (B[i, j] != 0, p = i; break));
    if (p, my(t = B[row, ]); B[row, ] = B[p, ]; B[p, ] = t; B[row, ] = B[row, ] / B[row, j];
      for (i = 1, nr, if (i != row && B[i, j] != 0, B[i, ] = B[i, ] - B[i, j] * B[row, ])); listput(piv, j - 1); row++));
  Vec(piv);
}
{
  my(K = 19, r = sqrt(-2 + O(q^PREC)));
  my(cA = truncate((1 + 2 * r) / 3), cB = truncate((1 - 2 * r) / 3));
  foreach([["c0 = (1 + 2 sqrt(-2))/3", cA, 2, 1], ["c0 = (1 - 2 sqrt(-2))/3", cB, 2, 1],
           ["control off the ray: c0 = (1 + 2 sqrt(-2))/3", cA, 1, 1], ["control: c0 = 2", 2, 2, 1]], G,
    my([name, c0, a, b] = G);
    my(rts = concat([1, 1 + q^b], q^a * [c0, 1, q^10, q^10 + q^20]));
    my(pv = limitspace(rts, K), R = #rts * (#rts - 1) / 2);
    write(OUT, name, ", (a, b) = ", [a, b], ": R = ", R, ", vanishing orders of L0 ", pv, "; all <= R: ", vecmax(pv) <= R));
  \\ M = 3: a cherry {1, 1 + q^b} above the equilateral cluster q^a (1, w, w^2), w in Z_q (q = 1 mod 3), on its failing
  \\ ray w_x/w_e = 4/3 ((a, b) = (4, 3)); control off the ray (a, b) = (1, 1).
  my(w = truncate((-1 + sqrt(-3 + O(q^PREC))) / 2));
  foreach([[4, 3], [1, 1]], ab, my(rts = concat([1, 1 + q^ab[2]], q^ab[1] * [1, w, w^2]));
    my(pv = limitspace(rts, K), R = #rts * (#rts - 1) / 2);
    write(OUT, "equilateral cluster under a cherry, (a, b) = ", ab, ": R = ", R, ", vanishing orders of L0 ", pv, "; all <= R: ", vecmax(pv) <= R));
}
