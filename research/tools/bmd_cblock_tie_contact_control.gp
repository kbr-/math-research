\\ Discriminating control for check:cube-cblock-tie-contact (cycle bmd-20261009-br, 9 October 2026).
\\ prop:cube-cblock-tie-joint-weight predicts, on a transverse arc above the four-root tie, exactly one nonzero x1 at which
\\ the limit pair space L0 has weight 1 (orders 0..13, 15). With x1 = X, the lowest e-coefficient of the T0 Taylor minor
\\ of the full pair matrix is, by the proposition, K X^m (A + B X). It is computed exactly at X = 1..5; m and -A/B are
\\ fitted (with a consistency check), and the predicted bad x1 = -A/B is rerun by exact limit space to confirm weight 1.
\\ (A first version with X symbolic over Q(X)(e) timed out at 600 s.)
OUT = "research/results/bmd-20261009-br/cblock-tie-contact-control.txt";
default(parisizemax, 4 * 10^9);
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
limitspace(rts, K) = {
  my(n = #rts, R = n * (n - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, n, for (j = i + 1, n, r++; my(h = H(rts[i], rts[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  for (step = 1, R,
    my(bi = 0, bj = 0, bv = 1e9);
    for (i = step, R, for (j = 1, K + 1, if (P[i, j] != 0, my(vv = valuation(P[i, j], 'e)); if (vv < bv || (vv == bv && j < bj), bv = vv; bi = i; bj = j))));
    my(tmp = P[step, ]); P[step, ] = P[bi, ]; P[bi, ] = tmp;
    P[step, ] = P[step, ] / P[step, bj];
    for (i = 1, R, if (i != step && P[i, bj] != 0, P[i, ] = P[i, ] - P[i, bj] * P[step, ])));
  matrix(R, K + 1, i, j, my(z = P[i, j]); if (z == 0, 0, my(vv = valuation(z, 'e)); if (vv > 0, 0, if (vv < 0, error("negative valuation"), subst(numerator(z), 'e, 0) / subst(denominator(z), 'e, 0)))));
}
orders(L) = {
  my(A = L, piv = List(), row = 1, R = #A[, 1]);
  for (j = 1, #A, if (row > R, break); my(p = 0); for (i = row, R, if (A[i, j] != 0, p = i; break));
    if (p, my(t = A[row, ]); A[row, ] = A[p, ]; A[p, ] = t; A[row, ] = A[row, ] / A[row, j];
      for (i = 1, R, if (i != row && A[i, j] != 0, A[i, ] = A[i, ] - A[i, j] * A[row, ])); listput(piv, j - 1); row++));
  Vec(piv);
}
pairmat(rts, K) = {
  my(n = #rts, R = n * (n - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, n, for (j = i + 1, n, r++; my(h = H(rts[i], rts[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  P;
}
ys = [0, 1, 3, 4]; uu = [2, -1, 1, 3]; vv = [1, 0, 0, 0]; bb = 2; ce = 3;
arc(x1) = concat([1, 1 + ce * 'e^bb], vector(4, q, x1 * 'e * (ys[q] + 'e * vv[q] + 'e^2 * uu[q])));
{
  my(K = 19, data = List());
  for (X = 1, 5, my(P = pairmat(arc(X), 14), D = matdet(P), mu = valuation(D, 'e));
    listput(data, [X, mu, polcoef(D, mu, 'e)]));
  write(OUT, "transverse v = ", vv, ", b = ", bb, ", c_e = ", ce, ": [x1, valuation of the T0 Taylor minor] = ", apply(z -> [z[1], z[2]], Vec(data)));
  \\ fit c(X) = K X^m (A + B X): for some m, the values c(X)/X^m must be affine in X
  my(found = 0);
  for (m = 0, 400, my(w = apply(z -> z[3] / z[1]^m, Vec(data)));
    my(B = w[2] - w[1], A = w[1] - B);
    if (B != 0 && vector(5, i, A + B * i) == w, found = 1;
      my(xs = -A / B);
      write(OUT, "  fit: lowest coefficient = X^", m, " (", A, " + ", B, " X); predicted bad x1 = ", xs);
      my(o = orders(limitspace(arc(xs), K)));
      write(OUT, "  exact limit space at x1 = ", xs, ": orders ", o, ", weight ", vecsum(o) - 105, ", max order ", vecmax(o));
      break));
  if (!found, write(OUT, "  no fit of the form X^m (A + B X) for m <= 400"));
}
