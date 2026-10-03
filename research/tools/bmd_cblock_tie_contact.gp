\\ Contact test above the four-root C-block tie (cycle bmd-20261009-br, 9 October 2026).
\\ Tested statement (the cherry step's conclusion, no section of L0 vanishing to order R+1): for a cherry {1, 1 + c_e e^b}
\\ above the four-root cluster with actual roots a_q = x1 e (y*_q + e v_q + e^2 u_q), y* = (0,1,3,4) (equal midpoints,
\\ F(y*) = 0, j_F = 1), the limit L0 of the pair row space (R = 15 rows, columns 0..K) has all vanishing orders <= R = 15.
\\ By prop:cube-cblock-flowed-arc the flowed arc is a/x, so E has weight 1 at the tie rate w_x = 1 iff l(v) = 0
\\ (l = y1 + y4 - y2 - y3): tangent arcs (l(v) = 0) are the candidates for contact, transverse arcs the control.
\\ The limit space is computed by valuation-pivoted elimination over Q(e) (as in bmd_cherry_limit_space.gp).
OUT = "research/results/bmd-20261009-br/cblock-tie-contact.txt";
default(parisizemax, 4 * 10^9);
\\ (the truncation goes inside the power: a first run applied ^(-3/2) at the default series precision 16 and failed at K = 19)
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
limitorders(rts, K) = {
  my(n = #rts, R = n * (n - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, n, for (j = i + 1, n, r++; my(h = H(rts[i], rts[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  for (step = 1, R,
    my(bi = 0, bj = 0, bv = 1e9);
    for (i = step, R, for (j = 1, K + 1, if (P[i, j] != 0, my(vv = valuation(P[i, j], 'e)); if (vv < bv || (vv == bv && j < bj), bv = vv; bi = i; bj = j))));
    my(tmp = P[step, ]); P[step, ] = P[bi, ]; P[bi, ] = tmp;
    P[step, ] = P[step, ] / P[step, bj];
    for (i = 1, R, if (i != step && P[i, bj] != 0, P[i, ] = P[i, ] - P[i, bj] * P[step, ])));
  my(L = matrix(R, K + 1, i, j, my(z = P[i, j]); if (z == 0, 0, my(vv = valuation(z, 'e)); if (vv > 0, 0, if (vv < 0, error("negative valuation"), subst(numerator(z), 'e, 0) / subst(denominator(z), 'e, 0))))));
  \\ vanishing orders = pivot columns of the reduced row echelon form
  my(A = L, piv = List(), row = 1);
  for (j = 1, K + 1, if (row > R, break); my(p = 0); for (i = row, R, if (A[i, j] != 0, p = i; break));
    if (p, my(t = A[row, ]); A[row, ] = A[p, ]; A[p, ] = t; A[row, ] = A[row, ] / A[row, j];
      for (i = 1, R, if (i != row && A[i, j] != 0, A[i, ] = A[i, ] - A[i, j] * A[row, ])); listput(piv, j - 1); row++));
  Vec(piv);
}
{
  my(K = 19, ys = [0, 1, 3, 4], u = [2, -1, 1, 3]);
  my(vs = [["tangent", [1, 0, 1, 0]], ["tangent", [1, 1, 1, 1]], ["tangent", [2, 3, -1, 0]], ["transverse", [1, 2, -1, 5]], ["transverse", [1, 0, 0, 0]]]);
  foreach(vs, V, my([kind, v] = V);
    foreach([[1, 1, 3], [1, 2, 3], [1, 3, -2], [1, 5, 3], [2, 1, 3], [5, 1, -2], [1, 1, 7], [1, 2, 1/2]], A, my([x1, b, ce] = A);
      my(rts = concat([1, 1 + ce * 'e^b], vector(4, q, x1 * 'e * (ys[q] + 'e * v[q] + 'e^2 * u[q]))));
      my(o = limitorders(rts, K), wt = vecsum(o) - 15 * 14 / 2);
      write(OUT, kind, " v = ", v, ", x1 = ", x1, ", e-rate b = ", b, ", c_e = ", ce, ": orders ", o, ", weight ", wt, ", max order ", vecmax(o), if (vecmax(o) > 15, "  CONTACT", ""))));
}
