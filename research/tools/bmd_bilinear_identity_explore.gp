\\ Sanity check and exploration for thm:cube-hankel-bilinear-identity (cycle bmd-20261009-bh, 9 October 2026).
\\ Identity (proved in the entry): H_k D^2 H_k - (D H_k)^2 = 4k^2 H_(k+1) H_(k-1) + 2k H_k Phi_k[p_2], with
\\ H_k = Hank_k = sum_(|S|=k+1) Vand(y_S)^2 and Phi_k[p_2] = sum_S Vand(y_S)^2 p_2(y_S).
\\ (1) Exact check of the identity at random rational clusters (M = 4..6), Phi_k[p_2] computed by its subset sum.
\\ (2) Exploration along the D-flow (t-series of H_k(y/(1 - t y))): at the clusters of the flow-order review, compare
\\     ord Phi_k[p_2](y_t) with j_k - 1 (the sufficient condition for the order relation (R)), where Phi_k[p_2](y_t) is
\\     read off the identity as (H D^2H - (DH)^2 - 4k^2 H_(k+1) H_(k-1)) / (2k H) with D = d/dt along the flow.
OUT = "research/results/bmd-20261009-bh/bilinear-identity.txt";
default(parisizemax, 4 * 10^9);
\\ (a first run without this stack limit overflowed at M = 5 in part (1); part (2) was unaffected)
hank(pw, M, k) = matdet(matrix(k + 1, k + 1, i, j, if (i + j == 2, M, pw[i + j - 2])));
phip2(y, k) = {
  my(M = #y, s = 0);
  forsubset([M, k + 1], S, my(v = prod(a = 1, k + 1, prod(b = a + 1, k + 1, y[S[b]] - y[S[a]]))); s += v^2 * sum(a = 1, k + 1, y[S[a]]^2));
  s;
}
Dop(f, M) = sum(i = 1, M, eval(Str("y", i))^2 * deriv(f, eval(Str("y", i))));
{
  \\ (1) symbolic in y at M = 4 (all k), numeric substitution check at M = 5, 6
  for (M = 4, 6,
    my(yv = vector(M, i, eval(Str("y", i))), pw = vector(2 * M + 2, n, sum(i = 1, M, yv[i]^n)), H = vector(M + 1, k, if (k == M + 1, 0, hank(pw, M, k - 1))));
    \\ H[k+1] = Hank_k for k = 0..M-1; Hank_M = 0
    for (k = 1, M - 2,
      my(Hk = H[k + 1], DH = Dop(Hk, M), D2H = Dop(DH, M), lhs = Hk * D2H - DH^2, rhs = 4 * k^2 * H[k + 2] * H[k] + 2 * k * Hk * phip2(yv, k));
      if (M == 4, write(OUT, "(1) M = 4, k = ", k, ": identity holds symbolically: ", lhs == rhs),
        my(pt = vector(M, i, random(41) - 20), sub = (f -> my(g = f); for (i = 1, M, g = subst(g, yv[i], pt[i])); g));
        write(OUT, "(1) M = ", M, ", k = ", k, ": identity holds at a random integer point: ", sub(lhs) == sub(rhs)))));
}
floword_series(P, M, k, T) = {
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
      my(T = 3 * M^2, Hs = vector(M + 1, k, if (k == M + 1, 0, floword_series(P, M, k - 1, T))), res = List());
      for (k = 1, M - 2,
        my(H = Hs[k + 1], a = vord(H));
        if (a >= 1 && a < oo,
          my(dH = deriv(H, 'tt), d2H = deriv(dH, 'tt), num = H * d2H - dH^2 - 4 * k^2 * Hs[k + 2] * Hs[k], ph = num / (2 * k * H));
          listput(res, [k, a, vord(ph), vord(ph) >= a - 1])));
      write(OUT, "(2) M = ", M, ", ", P, ": [k, j_k, ord Phi_k[p2], >= j_k - 1] = ", Vec(res))));
}
