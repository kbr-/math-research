\\ Controls for the filter resonance (cycle bmd-20261009-kfq, 9 October 2026, added after review).
\\ (a) Resonance or proximity: at m = 16 and 24, with a = (1, q, 0.5 e^i), the normalized measure of U_3 at
\\     q = 1 - r e^{i phi} for the distance r = |1 - q*| of the line minimum q* (filter-resonance.txt) and phi in a
\\     24-point circle; the resonance point has q* ~ e^{-c1}, i.e. phi ~ 0. If the measure on the circle is as small
\\     away from phi ~ 0 as at q*, the smallness is proximity to the collision; if it is much larger, it is resonance.
\\     Also the measure at the coalescence distance r = 2/m^2 along phi = 0 and phi = pi/2.
\\ (b) Truncation: on the resonance line, the exact amplitude A against the quadratic-cumulant sum
\\     Aq = sum_l binom(m,l) (-q)^l e^{c1 l + c2 l^2}: max over the line of |A/Aq - 1| and of |log|A/Aq||.
\\ Usage: env OUT=path gp -q bmd_resonance_controls.gp
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 80);
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
  foreach([[16, 1.4753031183560048395], [24, -2.535414271785401922]], P, my(m = P[1], n = m * (m - 1) / 2 + m, L = lam + m);
    my(lg(l) = lngamma(n + L + 1) - lngamma(n - l + L + 1) + lngamma(n - l + 1) - lngamma(n + 1) + (lam - 1) * log((n - l) / n));
    my(c1 = psi(n + L + 1) - psi(n + 1) - (lam - 1) / n, c2 = (lg(1e-15) + lg(-1e-15) - 2 * lg(0)) / 1e-30 / 2, s = sqrt(2 * c2));
    my(qs = exp(-c1) * (1 + I * s * P[2]), r = abs(1 - qs), mres = meas(U3([1, qs, a3], m)));
    my(circ = vector(24, k, my(phi = 2 * Pi * (k - 1) / 24); [precision(phi, 3), precision(meas(U3([1, 1 - r * exp(I * phi), a3], m)), 3)]));
    emit(Str("m = ", m, ": line minimum q* = ", precision(qs, 8), ", r = |1 - q*| = ", precision(r, 6), ", arg(1 - q*) = ",
      precision(arg(1 - qs), 4), ", measure ", precision(mres, 5)));
    emit(Str("  (a) circle |1 - q| = r, [phi, measure]: ", circ));
    my(rc = 2. / m^2);
    emit(Str("  (a) coalescence distance r = 2/m^2: measure at phi = 0 ", precision(meas(U3([1, 1 - rc, a3], m)), 4),
      ", at phi = pi/2 ", precision(meas(U3([1, 1 - I * rc, a3], m)), 4)));
    my(A(q) = sum(l = 0, m, binomial(m, l) * (-q)^l * exp(lg(l))), Aq(q) = sum(l = 0, m, binomial(m, l) * (-q)^l * exp(c1 * l + c2 * l^2)));
    my(dev = 0, ldev = 0);
    forstep(y = -3 * sqrt(m), 3 * sqrt(m), 6 * sqrt(m) / 200, my(q = exp(-c1) * (1 + I * s * y), t = A(q) / Aq(q));
      dev = max(dev, abs(t - 1)); ldev = max(ldev, abs(log(abs(t)))));
    emit(Str("  (b) exact A against the quadratic-cumulant sum on the line |y| <= 3 sqrt(m): max |A/Aq - 1| = ",
      precision(dev, 4), ", max |log|A/Aq|| = ", precision(ldev, 4)));
    my(rad = vector(25, k, my(rr = 10^(-3 + 3 * (k - 1) / 24)); [precision(rr * m, 3), precision(meas(U3([1, 1 - I * rr, a3], m)), 3)]));
    emit(Str("  (c) radial scan at phi = pi/2, [m * |1 - q|, measure]: ", rad)));
  quit;
}
