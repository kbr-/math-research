\\ Equal-modulus test of the triple window's asymptotic model (cycle bmd-20261009-cf, 9 October 2026).
\\ On the torus |a1| = |a2| = |a3| = 1 all three exponentials have the same size, so the 3 x 3 Darboux determinant governs
\\ the rank asymptotically. The corrected model predicts near-degeneracy where rho exp(-2S) = -1, rho = +-i alternating in
\\ m, i.e. on the real curves S in i pi (+-1/4 + Z) (S is purely imaginary on the torus). Test: a = (exp(i t), exp(i 2.1), 1),
\\ where |Im S| >= 1.7, so the targets are Im S = 3 pi/4, 5 pi/4 (exp(-2S) = i, -i) and -5 pi/4 (exp(-2S) = i); solve for
\\ t in (0, 2 pi) by bisection on Im S (first crossing); compute U_3 at 120 digits for m = 8..31 (both
\\ parities) at those points and at a torus control point, and print the normalized largest 3 x 3 minor; then scan t.
OUT = "research/results/bmd-20261009-cf/triple-window-torus-test.txt";
default(realprecision, 120);
lam = 3/2;
Sf(a) = (a[1] + a[3]) / (a[1] - a[3]) + (a[2] + a[3]) / (a[3] - a[2]) + (a[1] + a[2]) / (a[2] - a[1]);
U3(a, m) = {
  my(d = m * (m - 1) / 2, N0 = d + m, top = N0 + 4, U = matrix(3, 5), prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]]);
  my(rho = vector(top + 1, k, exp(lngamma(k) - lngamma(k + lam + m))));
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
  my(t2 = 2.1, f(t) = imag(Sf([exp(I * t), exp(I * t2), 1])));
  my(pts = List());
  foreach([3 * Pi / 4, 5 * Pi / 4, -5 * Pi / 4], tg,
    \\ scan for a sign change of f - tg, then bisect
    my(prev = f(0.05) - tg, tp = 0.05, found = 0);
    forstep (t = 0.1, 2 * Pi - 0.05, 0.05, my(v = f(t) - tg);
      if (!found && sign(v) != sign(prev) && abs(t - t2) > 0.1 && abs(t - tp) < 0.2,
        my(lo = tp, hi = t); for (it = 1, 200, my(mid = (lo + hi) / 2); if (sign(f(mid) - tg) == sign(f(lo) - tg), lo = mid, hi = mid));
        listput(pts, [tg, (lo + hi) / 2]); found = 1);
      prev = v; tp = t));
  listput(pts, ["control", 4.0]);
  foreach(pts, P, my(a = [exp(I * P[2]), exp(I * t2), 1]);
    write(OUT, "target ", P[1], ", t = ", P[2], ", S = ", Sf(a));
    for (m = 8, 31, write(OUT, "   m = ", m, ": normalized max 3x3 minor = ", meas(U3(a, m)))));
  \\ Scan: for m = 20, 21 the measure along t in [0.2, 6.1] (step 0.05, skipping |t - t2| < 0.1), with Im S, to see
  \\ whether local minima in t sit at the targets and alternate with the parity of m.
  forstep (t = 0.2, 6.1, 0.05, if (abs(t - t2) < 0.1, next); my(a = [exp(I * t), exp(I * t2), 1]);
    write(OUT, "scan t = ", t, "  ImS = ", imag(Sf(a)), "  m20 = ", meas(U3(a, 20)), "  m21 = ", meas(U3(a, 21))));
}
