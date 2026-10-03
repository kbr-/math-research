\\ Cheap tests of the goal-level review of 9 October 2026 (cycle bmd-20261009-cr) on the triple window U_3
\\ (lem:cube-level-window-gegenbauer-form), around prop:cube-triple-window-large-m.
\\ (a) Transition region: a = ((1 + c/m) e^{4i}, e^{2.1 i}, 1) for c in {-2,-1,-0.5,0,0.5,1,2} and m = 16, 32: the
\\     normalized largest 3x3 minor (divided by the product of row norms), times m^2. Uniformity predicts values bounded
\\     away from 0 across c at both m.
\\ (b) Effective threshold: at a = (-5/3, 1, 2/7), the minor on columns {1,2,3} divided by its leading prediction
\\     kappa * Delta * (s-1)^2 * (row and column factors) is hard to normalize; instead print the scaled separation
\\     Delta * m^2 / 4 against -B (the predicted limit) for m = 4..12, to see from which m the leading term is within 10%.
OUT = "research/results/bmd-20261009-cr/route-review31-tests.txt";
default(realprecision, 150);
lam = 3/2;
U3(a, m) = {
  my(d = m * (m - 1) / 2, N0 = d + m, top = N0 + 5, U = matrix(3, 6), prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]]);
  my(rho = vector(top + 1)); rho[1] = 1; for (n = 1, top, rho[n + 1] = rho[n] * n / (n + lam + m));
  for (r = 1, 3, my([i, j, k] = prs[r]);
    my(e = Vec(((1 + a[i] * 'T + O('T^(top + 1))) * (1 + a[j] * 'T))^(-lam)));
    for (col = 1, 6, my(n = N0 + col - 1);
      U[r, col] = sum(l = 0, m, binomial(m, l) * a[k]^l * if (n - l >= 0, rho[n - l + 1] * e[n - l + 1], 0))));
  U;
}
meas(U) = {
  my(best = 0); forsubset([5, 3], S, my(Sv = Vec(S)); best = max(best, abs(matdet(matrix(3, 3, r, t, U[r, Sv[t]])))));
  best / prod(r = 1, 3, sqrt(norml2(vector(5, c, U[r, c]))));
}
{
  foreach([16, 32], m,
    my(row = List());
    foreach([-2, -1, -1/2, 0, 1/2, 1, 2], c, my(a = [(1 + c / m) * exp(4 * I), exp(2.1 * I), 1]);
      listput(row, precision(meas(U3(a, m)) * m^2, 4)));
    write(OUT, "(a) m = ", m, ": m^2 * measure for c = -2,-1,-0.5,0,0.5,1,2: ", Vec(row)));
  my(a = [-5/3, 1, 2/7], B = a[1] * (a[2] - a[3]) / ((a[1] - a[2]) * (a[1] - a[3])));
  for (m = 4, 12, my(U = U3(a, m), d = m * (m - 1) / 2, n = d + m);
    my(v = log(U[1, 2] / U[2, 2]) - log(U[1, 1] / U[2, 1]));
    write(OUT, "(b) m = ", m, ": scaled separation ", precision(v * n^2 / (m * (m + 1)), 6), " vs -B = ", precision(-B * 1., 6)));
}
