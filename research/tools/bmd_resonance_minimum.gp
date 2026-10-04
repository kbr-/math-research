\\ Near-collision minimum of the triple window (cycle bmd-20261009-kfq, 9 October 2026). Question: does the normalized
\\ measure of U_3(a), a = (1, q, a3), which drops to 2.8e-8 at m = 16 on the filter resonance line q ~ e^{-c1}
\\ (filter-resonance.txt), reach 0 (a rank drop, refuting conj:cube-triple-window-full-rank at m = 16) or stay positive?
\\ Method: pattern search over (q, a3) in R^4 at 120 digits from the recorded line minimum, at m = 16 and m = 10; the
\\ trajectory of the minimum value is printed. A value decreasing to the working precision indicates a zero; a value
\\ stalling at a positive level indicates a positive local minimum. Also reports the three row norms' smallest singular
\\ value ratio sigma_3/sigma_1 of the row-normalized matrix at the final point.
\\ Usage: env OUT=path gp -q bmd_resonance_minimum.gp
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 120);
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
pt(v) = [1, v[1] + I * v[2], v[3] + I * v[4]];
f(v, m) = meas(U3(pt(v), m));
search(v0, m, h0) = {
  my(v = v0, fv = f(v, m), h = h0, it = 0);
  while (vecmax(h) > 1e-40 && it < 3000, it++;
    my(improved = 0);
    for (c = 1, 4, foreach([1, -1], sg, my(w = v); w[c] += sg * h[c]; my(fw = f(w, m)); if (fw < fv, v = w; fv = fw; improved = 1)));
    if (improved, h = h * 1.5, h = h / 2);
    if (it % 200 == 0, emit(Str("    m = ", m, ", iteration ", it, ": measure ", precision(fv, 6)))));
  [v, fv, it];
}
{
  foreach([[16, 0.11695103784355372877, 0.028380592169702293636, 1.4753031183560048395],
           [10, 0, 0, 0]], P,
    my(m = P[1], v0);
    if (m == 16, my(q = exp(-P[2]) * (1 + I * P[3] * P[4])); v0 = [real(q), imag(q), 0.5 * cos(1), 0.5 * sin(1)],
      my(c1 = 2. / m); v0 = [exp(-c1), 0.04, 0.5 * cos(1), 0.5 * sin(1)]);
    emit(Str("m = ", m, ": start q = ", precision(v0[1] + I * v0[2], 8), ", a3 = ", precision(v0[3] + I * v0[4], 8),
      ", measure ", precision(f(v0, m), 6)));
    my(res = search(v0, m, [0.01, 0.01, 0.05, 0.05]), v = res[1]);
    my(U = U3(pt(v), m), Un = matrix(3, 5, r, c, U[r, c] / sqrt(norml2(U[r, ]))), sv = sqrt(abs(polroots(charpoly(Un * conj(Un~))))));
    emit(Str("m = ", m, ": final q = ", precision(v[1] + I * v[2], 12), ", a3 = ", precision(v[3] + I * v[4], 12),
      ", measure ", precision(res[2], 8), " after ", res[3], " iterations; sigma_3/sigma_1 = ",
      precision(vecmin(sv) / vecmax(sv), 6), "; |1 - q| = ", precision(abs(1 - v[1] - I * v[2]), 6))));
  quit;
}
