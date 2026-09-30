\\ Cheap tests of two bridges in the route review of cycle bmd-20260930-zzu, on the weight polynomial of
\\ V_a = <1, z, ((z-a_i)(z-a_j))^(1/2)>: F(z) = W(z)^2 prod (z-a_i)^E, a polynomial (bmd_cube_config_wronskian.gp);
\\ after removing branch factors F = c R^2 with R the non-branch weight polynomial.  Numerical, realprecision 150:
\\ F is sampled on a circle of K = 2048 points (E clears the poles of the normalized Taylor determinant) and interpolated by DFT; coefficients below 10^-100 relative are zero.
\\  (a) non-crossing / Hermitian model: for real separated a, are all roots of R real?
\\  (b) Airault-McKean-Moser locus: do the roots z_i satisfy sum_{j != i} (z_i - z_j)^(-3) = 0 for every i?
default(parisizemax, 4000000000);
PR = 2^61 - 1;
taymat(a, z0, n) = {
  my(N = #a, M = matrix(n, n), r = 2, T = 'T);
  M[1, 1] = 1; M[2, 1] = z0; M[2, 2] = 1;
  for (i = 1, N, for (j = i + 1, N,
    r++;
    my(g = ((1 + T/(z0 - a[i]) + O(T^n)) * (1 + T/(z0 - a[j]) + O(T^n)))^(1/2));
    for (k = 1, n, M[r, k] = polcoef(g, k - 1, T))));
  M;
}
Fval(a, z0, E) = my(N = #a); matdet(taymat(a, z0, 2 + N*(N-1)/2))^2 * prod(i = 1, N, z0 - a[i])^(N - 1 + E);
{
  default(realprecision, 150);
  foreach ([[2, 3/7, -5/3, 11/4], [2, 3/7, -5/3, 11/4, -1]], a,
    my(N = #a, E = 2 * (N - 1) * (1 + N*(N-1)/2), K = 2048, rho = 4., w = exp(2 * Pi * I / K), vals, F, R, rts, d, amm, nreal, D, cf);
    vals = vector(K, k, Fval(a, rho * w^(k - 1), E));
    cf = vector(K, m, sum(k = 1, K, vals[k] * w^(-(k - 1) * (m - 1))) / K / rho^(m - 1));
    D = K - 1; while (abs(cf[D + 1]) * rho^D < 10^-100 * vecmax(abs(vals)), D--);
    if (D > K - 50, print("coefficient profile log10|c_m rho^m / max|: ", vector(26, j, my(m = 20 * (j - 1)); if (m < K, round(log(abs(cf[m + 1]) * rho^m / vecmax(abs(vals)) + 10^-200) / log(10)))));
      error("degree too close to the sample count"));
    F = sum(m = 0, D, cf[m + 1] * 'z^m);
    F = real(F);                                  \\ real configuration: real coefficients
    for (i = 1, N, while (abs(subst(F, 'z, a[i])) < 10^-60 * vecmax(abs(Vec(F))), F = F \ ('z - a[i])));
    rts = polroots(F);                            \\ roots of c R^2: each non-branch root twice
    my(u = List());
    for (k = 1, #rts, if (vecsum(vector(#u, j, abs(u[j] - rts[k]) < 10^-40)) == 0, listput(u, rts[k])));
    rts = Vec(u); d = #rts;
    nreal = vecsum(vector(d, k, abs(imag(rts[k])) < 10^-40));
    amm = vecmax(vector(d, i, abs(sum(j = 1, d, if (j != i, (rts[i] - rts[j])^(-3))))));
    print("N = ", N, ", real configuration ", a, ": deg F = ", D, ", distinct non-branch weight roots = ", d,
      " (deg F after branch factors = ", poldegree(F), "), real among them = ", nreal,
      ", max_i |sum_j (z_i - z_j)^(-3)| = ", precision(amm, 10)));
}
