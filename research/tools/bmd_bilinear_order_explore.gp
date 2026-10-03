\\ Exploration for the order relation (R) (cycle bmd-20261009-bh, 9 October 2026); split from
\\ bmd_bilinear_identity_explore.gp, whose symbolic part (1) timed out at M = 6, k = 4 before this part ran.
\\ Along the D-flow (t-series of H_k(y/(1 - t y))), at clusters of the flow-order review, compare ord Phi_k[p_2](y_t)
\\ with j_k - 1 (a sufficient condition for (R)), where by thm:cube-hankel-bilinear-identity
\\ Phi_k[p_2](y_t) = (H D^2H - (DH)^2 - 4k^2 H_(k+1) H_(k-1)) / (2k H) with D = d/dt. Also reports the leading
\\ coefficients c = [t^a] H_k and phi = [t^(a-2)] Phi_k[p_2] and the non-cancellation quantity -a c - 2k phi,
\\ whose nonvanishing is equivalent to (R) when ord Phi_k[p_2] >= a - 2.
OUT = "research/results/bmd-20261009-bh/order-explore.txt";
default(parisizemax, 2 * 10^9);
flowhank(P, M, k, T) = {
  my(Q = subst(P, 'z, 'x / (1 + 'tt * 'x)) * (1 + 'tt * 'x)^M + O('tt^T));
  Q = Q / polcoeff(Q, M, 'x);
  my(a = vector(M, j, polcoeff(Q, M - j, 'x)), pw = vector(2*k + 1));
  for (j = 1, 2*k, my(s = if (j <= M, j * a[j], 0)); for (i = 1, min(j - 1, M), s += a[i] * pw[j - i]); pw[j] = -s);
  matdet(matrix(k + 1, k + 1, i, j, if (i + j == 2, M, pw[i + j - 2])));
}
vord(f) = if (f == 0, oo, valuation(f, 'tt));
{
  for (M = 4, 8,
    foreach(['z^M + 'z + 1, 'z^M - 1, 'z^M + 'z^2 + 1, 'z^M + 'z^3 - 2], P,
      my(T = 3 * M^2, Hs = vector(M + 1, k, if (k == M + 1, 0, flowhank(P, M, k - 1, T))), res = List());
      for (k = 1, M - 2,
        my(H = Hs[k + 1] + O('tt^T), a = vord(H));
        if (a >= 1 && a < oo,
          my(dH = deriv(H, 'tt), d2H = deriv(dH, 'tt), num = H * d2H - dH^2 - 4 * k^2 * Hs[k + 2] * Hs[k], ph = num / (2 * k * H));
          my(c = polcoeff(H, a, 'tt), phi = if (a >= 2, polcoeff(ph, a - 2, 'tt), 0));
          listput(res, [k, a, vord(ph), -a * c - 2 * k * phi != 0])));
      write(OUT, "M = ", M, ", ", P, ": [k, j_k, ord Phi_k[p2], -a c - 2k phi != 0] = ", Vec(res))));
}
