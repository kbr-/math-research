\\ Tests of the goal-level review of 9 October 2026 (cycle bmd-20261009-kfy), triple window.
\\ (T1) Falsification attempt of conj:cube-triple-window-collision-scaling: at delta = 2 log(m)/m and m = 96 the ratio
\\      m^2 * measure / delta^2 for the eight series of the collision-scaling growth test (a3 in {0.5 e^i, -0.7+0.2i},
\\      phi in {0, pi/2, pi, 3pi/2}); the conjecture needs it bounded below (the m <= 72 values were >= 4.2, increasing).
\\ (T2) lem:cube-pair-coefficient-explicit-darboux against the truth: for a_i = 1, a_j = q = 0.6 e^{0.9 i} (radial ray,
\\      theta = 0, d0 = distance from u/q to [0, oo)), the actual relative error |e_n/((-a_i)^n main) - 1 - (j-part)| is
\\      compared with the bound 2^{1/4} D |u|^{3/2}/(2n+1) at n = 50, 200, 800; the j-part (-a_j)^n phi_{j;i} is removed
\\      using its own leading term (|q|^n small).
\\ (T3) Gegenbauer form: e^{(ij)}_n = (-sqrt(a_i a_j))^n C_n^{3/2}((a_i + a_j)/(2 sqrt(a_i a_j))) at a random pair, n = 0..60.
\\ Usage: env OUT=path gp -q bmd_review_kfy_tests.gp
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 300);  \\ cancellation about m log10(2/delta) = 130 digits at m = 96
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
  my(m = 96, dl = 2 * log(m) / m);
  foreach([0.5 * exp(I), -0.7 + 0.2 * I], a3, foreach([0, 1, 2, 3], j,
    emit(Str("(T1) m = 96, a3 = ", precision(a3, 3), ", phi = ", j, "pi/2: m^2 * measure / delta^2 = ",
      precision(m^2 * meas(U3([1, 1 - dl * exp(I * j * Pi / 2), a3], m)) / dl^2, 4)))));
  my(q = 0.6 * exp(0.9 * I), u = 1 - q, sj = u / q, d0 = if (real(sj) >= 0, abs(imag(sj)), abs(sj)), D = 3/2 * abs(q)^(-3/2) * d0^(-5/2));
  my(e = Vec(((1 + 'T + O('T^802)) * (1 + q * 'T))^(-lam)));
  foreach([50, 200, 800], n, my(main = u^(-lam) * gamma(n + lam) / (gamma(lam) * gamma(n + 1)));
    my(jpart = (-q)^n * (1 - 1 / q)^(-lam) * gamma(n + lam) / (gamma(lam) * gamma(n + 1)));
    my(act = abs((e[n + 1] - jpart) / ((-1)^n * main) - 1), bnd = 2^(1/4) * D * abs(u)^(3/2) / (2 * n + 1));
    emit(Str("(T2) n = ", n, ": actual relative error ", precision(act, 4), ", bound ", precision(bnd, 4), ", ratio ", precision(act / bnd, 4))));
  my(ai = 0.7 + 0.3 * I, aj = -0.4 + 0.9 * I, s = sqrt(ai * aj), x = (ai + aj) / (2 * s), ee = Vec(((1 + ai * 'T + O('T^62)) * (1 + aj * 'T))^(-lam)));
  \\ Gegenbauer C_n^lam(x) by the three-term recurrence n C_n = 2x(n+lam-1) C_{n-1} - (n+2lam-2) C_{n-2}
  my(C = vector(61)); C[1] = 1; C[2] = 2 * lam * x;
  for (n = 2, 60, C[n + 1] = (2 * x * (n + lam - 1) * C[n] - (n + 2 * lam - 2) * C[n - 1]) / n);
  my(dev = vecmax(vector(61, n, abs(ee[n] - (-s)^(n - 1) * C[n]) / max(1, abs(ee[n])))));
  emit(Str("(T3) max relative deviation of e_n from (-sqrt(a_i a_j))^n C_n^{3/2}(x), n = 0..60: ", precision(dev, 4)));
  quit;
}
