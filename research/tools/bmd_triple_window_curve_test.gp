\\ Falsification test from the asymptotic model of the triple window (cycle bmd-20261009-cf, 9 October 2026).
\\ Model: for large m the leading 3 x 3 Darboux determinant of U_3 is proportional to 1 + r, r = (+-i) exp(-2 S(a)),
\\ S = (a1+a3)/(a1-a3) + (a2+a3)/(a3-a2) + (a1+a2)/(a2-a1), the sign alternating with m. Where r = -1 the model predicts
\\ near rank 2. Test: with a = (x, y, 1), y = 2 + I fixed, solve r = -1 for x (S = s* for the branch values), then compute
\\ U_3 numerically (closed form, high precision) for m = 8..40 at that x and at a control point, and report the
\\ normalized smallest singular value proxy: |largest 3x3 minor| / (product of row norms).
\\ Review outcome: uninformative. With |c1| != |c2| != 1 the model is not in its regime (rows (12) and (23) share a
\\ dominant exponential), so the m^-2 decay measures subleading differences; the valid test is the torus test.
OUT = "research/results/bmd-20261009-cf/triple-window-curve-test.txt";
default(realprecision, 120);
lam = 3/2;
Sf(a) = (a[1] + a[3]) / (a[1] - a[3]) + (a[2] + a[3]) / (a[3] - a[2]) + (a[1] + a[2]) / (a[2] - a[1]);
\\ U_3 numerically: rows (ij|k), columns n = N0..N0+4
U3(a, m) = {
  my(d = m * (m - 1) / 2, N0 = d + m, top = N0 + 4, U = matrix(3, 5), prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]]);
  my(rho = vector(top + 1, k, exp(lngamma(k) - lngamma(k + lam + m))));
  for (r = 1, 3, my([i, j, k] = prs[r]);
    \\ truncation inside the power (default series precision would cut the expansion at 16 terms)
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
  my(y = 2 + I);
  \\ target: exp(-2S) = -eps i^-1 ... solve both branches: S = i pi/4 * s + i pi k, s = +-1, k = 0
  foreach([1, -1], s,
    my(target = I * Pi / 4 * s, pol = numerator(Sf(['x, y, 1]) - target), rts = polroots(pol));
    foreach(rts, x0, if (abs(x0) > 1e-6 && abs(x0 - 1) > 1e-6 && abs(x0 - y) > 1e-6,
      my(a = [x0, y, 1]);
      write(OUT, "branch s = ", s, ", x = ", x0, ", S = ", Sf(a));
      forstep (m = 8, 40, 4, my(U = U3(a, m)); write(OUT, "   m = ", m, ": normalized max 3x3 minor = ", meas(U)));
      break)));
  my(ac = [0.3 - 0.7 * I, y, 1]);
  write(OUT, "control x = 0.3 - 0.7 i, S = ", Sf(ac));
  forstep (m = 8, 40, 4, write(OUT, "   m = ", m, ": normalized max 3x3 minor = ", meas(U3(ac, m))));
}
