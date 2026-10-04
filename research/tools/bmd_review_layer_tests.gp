\\ Tests of the goal-level review of 9 October 2026 (cycle bmd-20261009-kfr), triple window U_3.
\\ (T1) Falsification attempt of conj:cube-triple-window-collision-layer: m^2 * measure(U_3(1, 1 - (X/m) e^{i phi}, a3))
\\      at X in {4, 6, 8, 12}, phi in {0, pi/2, pi, 3pi/2}, a3 = 0.5 e^i, m in {16, 24, 32, 40}. The conjecture (fixed C)
\\      predicts values bounded below uniformly in m at each X >= C; a steady decrease in m at fixed X refutes fixed C.
\\ (T2) Noerlund-Rice representation of the filtered amplitude A = sum_l binom(m,l) (-q)^l g(l) (row (13|2), first
\\      window column, Darboux phi): A = (-1)^m/(2 pi i) * contour integral of q^s g(s) m!/(s(s-1)...(s-m)) ds over the
\\      circle |s - m/2| = m/2 + 1/2 (trapezoid rule, 4000 nodes; a first version with intnum gave a wrong value), at
\\      m = 16 and q = 1 - 2i/m; relative difference printed.
\\ (T3) Avoided crossing: sigma_3/sigma_1 of the row-normalized U_3 along a line through the stalled m = 16 minimum of
\\      resonance-minimum.txt (direction of a3), 21 points: printed profile.
\\ Usage: env OUT=path gp -q bmd_review_layer_tests.gp
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
sratio(U) = {
  my(Un = matrix(3, 5, r, c, U[r, c] / sqrt(norml2(U[r, ]))), sv = sqrt(abs(polroots(charpoly(Un * conj(Un~))))));
  vecmin(sv) / vecmax(sv);
}
{
  my(a3 = 0.5 * exp(I));
  foreach([0, 1, 2, 3], j, my(phi = j * Pi / 2);
    foreach([4, 6, 8, 12], X,
      my(row = vector(4, t, my(m = 8 * (t + 1)); precision(m^2 * meas(U3([1, 1 - X / m * exp(I * phi), a3], m)), 4)));
      emit(Str("(T1) phi = ", j, "pi/2, X = ", X, ": m^2 * measure at m = 16, 24, 32, 40: ", row))));
  my(m = 16, n = m * (m - 1) / 2 + m, L = lam + m, q = 1 - 2 * I / m);
  my(lg(l) = lngamma(n + L + 1) - lngamma(n - l + L + 1) + lngamma(n - l + 1) - lngamma(n + 1) + (lam - 1) * log((n - l) / n));
  my(A = sum(l = 0, m, binomial(m, l) * (-q)^l * exp(lg(l))));
  my(R = m / 2 + 1 / 2, F(s) = exp(s * log(q) + lg(s)) * m! / prod(t = 0, m, s - t));
  \\ trapezoid rule (periodic analytic integrand): (1/(2 pi i)) contour integral = mean of F(s) R e^{i th}
  my(NT = 4000, I1 = sum(k = 0, NT - 1, my(th = 2 * Pi * k / NT, s = m / 2 + R * exp(I * th)); F(s) * R * exp(I * th)) / NT);
  emit(Str("(T2) m = 16, q = 1 - 2i/m: A = ", precision(A, 8), "; (-1)^m * contour = ", precision((-1)^m * I1, 8),
    "; relative difference ", precision(abs((-1)^m * I1 - A) / abs(A), 3)));
  my(q0 = 0.8896287502391267634 + 0.03724873453596354108 * I, b0 = 0.2836277154340698587 + 0.4800750207234075718 * I);
  my(prof = vector(21, k, my(t = (k - 11) * 0.002); precision(sratio(U3([1, q0, b0 + t], 16)), 4)));
  emit(Str("(T3) sigma_3/sigma_1 along a3 = a3* + t, t = -0.02..0.02 step 0.002, m = 16: ", prof));
  quit;
}
