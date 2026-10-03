\\ Closed form of the reduced level window U_h (cycle bmd-20261009-bz, 9 October 2026).
\\ Tested statement (lem:cube-level-window-gegenbauer-form): for the h-root window of lem:cube-level-window-reduction,
\\ f_M(pair_ij) = sum_(i<=hm) P_i rho^(m)_(M-i) e^(ij)_(M-i) equals Pi_m (a_i a_j)^m sum_l q_l rho^(-m)_(M-2m-l) e^(ij)_(M-2m-l),
\\ with P = prod_l (1+a_l T)^m, q = coefficients of prod_(l != i,j) (1+a_l T)^m, e^(ij) = coefficients of
\\ ((1+a_i T)(1+a_j T))^(-3/2), Pi_m = prod_(j=-m..m-1)(3/2+j), rho^(j)_k = Gamma(k+1)/Gamma(k+3/2-j+1), for every
\\ M >= hm. Exact check (Gamma ratios reduced to rationals) for h = 2, 3, 4, m = 2..4, at rational roots.
OUT = "research/results/bmd-20261009-bz/level-window-closed-form.txt";
lam = 3/2;
\\ rho^(j)_k / rho^(j)_0 as an exact rational: Gamma(k+1)/Gamma(k+lam-j+1) * Gamma(lam-j+1)
rq(j, k) = prod(i = 1, k, i / (i + lam - j));
\\ the two families are compared after multiplying by Gamma(lam-m+1) and Gamma(lam+m+1) respectively:
\\ rho^(m)_k = rq(m,k)/Gamma(lam-m+1), rho^(-m)_k = rq(-m,k)/Gamma(lam+m+1); Pi_m = Gamma(lam+m)/Gamma(lam-m),
\\ so Pi_m rho^(-m) / rho^(m)_0-scale = rq(-m,k) * Gamma(lam+m)/Gamma(lam-m) * Gamma(lam-m+1)/Gamma(lam+m+1)
\\ = rq(-m,k) * (lam-m)/(lam+m).
cc(n) = binomial(-lam, n);
{
  my(allok = 1);
  foreach([[2, [3/7, 1]], [3, [2/7, -5/3, 1]], [4, [2/7, -5/3, 4, 1]]], H, my([h, a] = H);
    for (m = 2, 4, my(P = prod(l = 1, h, (1 + a[l] * 'T)^m), ok = 1, d = m * (m - 1) / 2);
      for (i = 1, h, for (j = i + 1, h,
        my(Q = prod(l = 1, h, if (l == i || l == j, 1, (1 + a[l] * 'T)^m)), Lmax = d + h * m + binomial(h, 2) + 6);
        my(e = vector(Lmax + 1, k, sum(r = 0, k - 1, cc(r) * cc(k - 1 - r) * a[i]^r * a[j]^(k - 1 - r))));
        for (M = h * m, Lmax,
          my(lhs = sum(t = 0, h * m, if (M - t < 0, 0, polcoef(P, t, 'T) * rq(m, M - t) * e[M - t + 1])));
          my(rhs = (lam - m) / (lam + m) * (a[i] * a[j])^m * sum(l = 0, (h - 2) * m, my(n = M - 2 * m - l); if (n < 0, 0, polcoef(Q, l, 'T) * rq(-m, n) * e[n + 1])));
          if (lhs != rhs, ok = 0))));
      if (!ok, allok = 0);
      write(OUT, "h = ", h, ", m = ", m, ", roots ", a, ": closed form holds for every pair and M in [hm, d+hm+C(h,2)+6]: ", ok)));
  write(OUT, "all cases: ", allok);
}
