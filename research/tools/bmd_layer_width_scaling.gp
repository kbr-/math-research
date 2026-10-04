\\ Width of the triple window's collision layer (cycle bmd-20261009-kfs, 9 October 2026). Tested question: does the
\\ layer width scale like 1/m or like m^{-1/2}? For a = (1, 1 - r e^{i phi}, 0.5 e^i), phi in {0, pi/2, pi, 3pi/2} and
\\ m in {16, 24, 32, 40, 56}, find by bisection in log r on [1e-3, 1] the largest crossing radius r* where
\\ m^2 * measure(U_3) rises through 0.1 (scanning down from r = 1 on a log grid, then bisecting the first sub-0.1
\\ interval), and print r* m and r* sqrt(m). A constant r* m means width 1/m; a constant r* sqrt(m) means m^{-1/2}.
\\ Also m^2 * measure at r = 2/sqrt(m) and r = 3/sqrt(m) in each direction.
\\ Usage: env OUT=path gp -q bmd_layer_width_scaling.gp
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 200);  \\ filter cancellation costs about m log10(2/r) digits (90 at m = 56, r = 0.05)
lam = 3/2;
U3(a, m) = {
  my(d = m * (m - 1) / 2, N0 = d + m, top = N0 + 5, U = matrix(3, 5), prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]]);
  my(rho = vector(top + 1)); rho[1] = 1; for (n = 1, top, rho[n + 1] = rho[n] * n / (n + lam + m));
  for (r = 1, 3, my([i, j, k] = prs[r]);
    my(e = Vec(((1 + a[i] * 'T + O('T^(top + 1))) * (1 + a[j] * 'T))^(-lam)));
    for (col = 1, 5, my(n = N0 + col - 1);
      U[r, col] = sum(l = 0, m, binomial(m, l) * a[k]^l * if (n - l >= 0, rho[n - l + 1] * e[n - l + 1], 0))));
  U;
}
meas(U) = {
  my(best = 0); forsubset([5, 3], S, my(Sv = Vec(S)); best = max(best, abs(matdet(matrix(3, 3, r, t, U[r, Sv[t]])))));
  best / prod(r = 1, 3, sqrt(norml2(U[r, ])));
}
{
  my(a3 = 0.5 * exp(I));
  foreach([16, 24, 32, 40, 56], m,
    my(rs = List(), extra = List());
    foreach([0, 1, 2, 3], j, my(phi = j * Pi / 2, h(r) = m^2 * meas(U3([1, 1 - r * exp(I * phi), a3], m)) - 0.1);
      my(hi = 0., lo = 0.);
      forstep(k = 0, -60, -1, my(r = 10.^(k / 20.)); if (h(r) < 0, lo = r; hi = 10.^((k + 1) / 20.); break));
      if (lo == 0, listput(rs, "none"); next);
      for (it = 1, 30, my(mid = sqrt(lo * hi)); if (h(mid) < 0, lo = mid, hi = mid));
      listput(rs, [j, precision(hi * m, 4), precision(hi * sqrt(m), 4)]);
      listput(extra, [j, precision(h(2 / sqrt(m)) + 0.1, 3), precision(h(3 / sqrt(m)) + 0.1, 3)]));
    emit(Str("m = ", m, ": [phi/(pi/2), r* m, r* sqrt(m)] = ", Vec(rs)));
    emit(Str("        [phi/(pi/2), m^2*measure at r = 2/sqrt(m), at r = 3/sqrt(m)] = ", Vec(extra))));
  quit;
}
