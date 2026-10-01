\\ Newton polygons of the block-IV six-space polynomials rho_j against the far polynomial (3 October 2026; cycle bmd-20261003-zzh).
\\ Hypothesis (six-space splitting): each rho_j (Z_e = <u_1,u_2> + t^(k-1/2) V_e, V_e = <(1-t)^(3-j) rho_j>) splits in coefficient
\\ magnitude as A_j + t^M B_j with one long Newton edge, and the four edge slopes of the far polynomial P(t) (newton-hull.txt:
\\ e*u = -2.63, -1.06, 0.51, 2.12 at e = 6; -2.07, -0.83, 0.41, 1.68 at e = 9) are the four rho_j slopes (sorted).
\\ For e = 6..9 and j = 0..3: the long edges (length >= 8) of the upper hull of log|coefficients| of (1-t)^(3-j) rho_j, as
\\ [length, e*u] with u = -slope.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 60);
Rn(n) = n * (2 * n - 1);
dt(f) = my(b = f[1], g = f[2], p = f[3]); [b - 1, g - 1, b * (1 - 't) * p - g * 't * p + 't * (1 - 't) * deriv(p, 't)];
dx(f) = my(h = dt(f)); [h[1], h[2] + 2, h[3]];
hull(pts) = {
  my(H = List());
  foreach (pts, p, while (#H >= 2 && (H[#H][2] - H[#H - 1][2]) * (p[1] - H[#H][1]) <= (p[2] - H[#H][2]) * (H[#H][1] - H[#H - 1][1]), listpop(H)); listput(H, p));
  Vec(H);
}
edges(P, e) = {
  my(D = poldegree(P), pts = select(p -> p != 0, vector(D + 1, j, my(c = polcoef(P, j - 1, 't)); if (c, [j - 1, log(abs(c))], 0))), H = hull(pts), out = List());
  for (i = 1, #H - 1, my(l = H[i + 1][1] - H[i][1]); if (l >= 8, listput(out, [l, precision(-(H[i + 1][2] - H[i][2]) / l * e, 4) * 1.])));
  Vec(out);
}
{
for (e = 6, 9,
  my(n = Rn(e), k = 4 * e, a = -n - 7/2, out = List());
  for (j = 0, 3, my(f = [j - 7/2, 6 - j, 1]); for (r = 1, n, f = dx(f)); f = [f[1], f[2] + a + k - 1, f[3]];
    for (r = 1, k, f = dt(f)); f = [f[1] + k - a, f[2], f[3]]; for (r = 1, k, f = dt(f));
    my(p = f[3]); p /= 't^valuation(p, 't);
    listput(out, Str("j=", j, " (deg ", poldegree(p), "): ", edges(p, e))));
  emit(Str("e=", e, ": ", strjoin(Vec(out), "; "))));
}
