\\ Outer law of the triple window near a collision (cycle bmd-20261009-kfs, 9 October 2026). Tested hypothesis: outside
\\ the collision layer the normalized measure behaves like m^{-2} F(|1-q|), with F(r) -> 0 as r -> 0, so that
\\ (i) at fixed r, m^2 * measure is bounded below (stable or increasing) in m once m r is large, and
\\ (ii) F(r) ~ r^kappa for small r. For a = (1, 1 - r e^{i phi}, 0.5 e^i), r in {0.05, 0.1, 0.2, 0.4},
\\ phi in {0, pi/2, pi, 3pi/2}, m in {16, 24, 32, 40, 56}: m^2 * measure; then the local exponent
\\ log(F(0.2)/F(0.1))/log 2 and log(F(0.4)/F(0.2))/log 2 at m = 56.
\\ Usage: env OUT=path gp -q bmd_outer_law.gp
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
  my(a3 = 0.5 * exp(I), ms = [16, 24, 32, 40, 56], rr = [0.05, 0.1, 0.2, 0.4], last = matrix(4, 4));
  foreach([0, 1, 2, 3], j, my(phi = j * Pi / 2);
    for (ir = 1, #rr, my(r = rr[ir]);
      my(v = vector(#ms, t, ms[t]^2 * meas(U3([1, 1 - r * exp(I * phi), a3], ms[t]))));
      last[j + 1, ir] = v[#ms];
      emit(Str("phi = ", j, "pi/2, r = ", r, ": m^2 * measure at m = 16, 24, 32, 40, 56: ", apply(x -> precision(x, 4), v))));
    emit(Str("phi = ", j, "pi/2: local exponents at m = 56: log2(F(0.1)/F(0.05)) = ", precision(log(last[j + 1, 2] / last[j + 1, 1]) / log(2), 3),
      ", log2(F(0.2)/F(0.1)) = ", precision(log(last[j + 1, 3] / last[j + 1, 2]) / log(2), 3), ", log2(F(0.4)/F(0.2)) = ",
      precision(log(last[j + 1, 4] / last[j + 1, 3]) / log(2), 3))));
  quit;
}
