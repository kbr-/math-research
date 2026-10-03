\\ Cheap test of the goal-level review of 9 October 2026 (cycle bmd-20261009-cy): growth of the large-m threshold of
\\ prop:cube-triple-window-large-m near a tie of the largest modulus. At a = (1, r e^{1.3 i}, 0.4 e^{2.5 i}) for
\\ r = 0.5, 0.9, 0.97, print the scaled separation (n^2/(m(m+1))) * Delta_n log(R_12/R_13) at the window, against its
\\ limit -B, for m = 4..14. The m at which it is within 10% of -B estimates m0(a) as the tie is approached.
OUT = "research/results/bmd-20261009-cy/route-review32-tests.txt";
default(realprecision, 150);
lam = 3/2;
rows2(a, m) = {
  my(d = m * (m - 1) / 2, N0 = d + m, top = N0 + 1, out = matrix(2, 2), prs = [[1, 2, 3], [1, 3, 2]]);
  my(rho = vector(top + 1)); rho[1] = 1; for (n = 1, top, rho[n + 1] = rho[n] * n / (n + lam + m));
  for (r = 1, 2, my([i, j, k] = prs[r]);
    my(e = Vec(((1 + a[i] * 'T + O('T^(top + 1))) * (1 + a[j] * 'T))^(-lam)));
    for (col = 1, 2, my(n = N0 + col - 1);
      out[r, col] = sum(l = 0, m, binomial(m, l) * a[k]^l * if (n - l >= 0, rho[n - l + 1] * e[n - l + 1], 0))));
  out;
}
{
  foreach([1/2, 9/10, 97/100], r,
    my(a = [1, r * exp(1.3 * I), 0.4 * exp(2.5 * I)], B = a[1] * (a[2] - a[3]) / ((a[1] - a[2]) * (a[1] - a[3])), first = 0, line = List());
    for (m = 4, 14, my(U = rows2(a, m), d = m * (m - 1) / 2, n = d + m);
      my(v = log((U[1, 2] / U[2, 2]) / (U[1, 1] / U[2, 1])) * n^2 / (m * (m + 1)));
      my(rel = abs(v + B) / abs(B)); listput(line, precision(rel, 3));
      if (!first && rel < 0.1, first = m));
    write(OUT, "r = ", r, ": relative error |scaled + B|/|B| for m = 4..14: ", Vec(line), "; first m within 10%: ", if (first, first, "none <= 14")));
}
