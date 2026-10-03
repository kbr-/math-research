\\ Ratio exploration for the order relation (R) (cycle bmd-20261009-bi, 9 October 2026).
\\ By thm:cube-hankel-bilinear-identity, at a flow line with ord H_k = a >= 2, (R) holds iff ord Phi_k[p_2] >= a - 2 and
\\ rho := 2k phi / (-a c) != 1, where c = [t^a] H_k(y_t) and phi = [t^(a-2)] Phi_k[p_2](y_t). The script reports rho at the
\\ clusters of the flow-order review (M = 4..8) to look for a closed formula in (a, k, M).
OUT = "research/results/bmd-20261009-bi/ratio-explore.txt";
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
    foreach(['z^M + 'z + 1, 'z^M - 1, 'z^M + 'z^2 + 1, 'z^M + 'z^3 - 2, 'z^M + 3*'z - 5], P,
      my(T = 3 * M^2, Hs = vector(M + 1, k, if (k == M + 1, 0, flowhank(P, M, k - 1, T))), res = List());
      for (k = 1, M - 2,
        my(H = Hs[k + 1] + O('tt^T), a = vord(H));
        if (a >= 2 && a < oo,
          my(dH = deriv(H, 'tt), d2H = deriv(dH, 'tt), num = H * d2H - dH^2 - 4 * k^2 * Hs[k + 2] * Hs[k], ph = num / (2 * k * H));
          my(c = polcoeff(H, a, 'tt), phi = polcoeff(ph, a - 2, 'tt));
          listput(res, [k, a, 2 * k * phi / (-a * c)])));
      write(OUT, "M = ", M, ", ", P, ": [k, j_k, rho] = ", Vec(res))));
}
