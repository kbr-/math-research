\\ Is the last-step far polynomial lacunary in t = x/(1+x)? (3 October 2026; cycle bmd-20261003-zzg)
\\ P(t) = (1-t)^d W(t/(1-t)) for the saved W_(b-1), e = 4..9: number of nonzero coefficients, and the coefficient profile
\\ log10|c_j| - (upper hull at j) summarized: the number of coefficients more than 10 decades below the hull (near-gaps).  Also the
\\ same for the IV polynomials rho_j of the six-space (Z_e = <u_1,u_2> + t^(k-1/2) V_e): are they of the form A + t^M B with A, B of
\\ low degree?  Reports their nonzero count and near-gap count.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 60);
Rn(n) = n * (2 * n - 1);
src(e) = if (e <= 3, "research/results/bmd-20261003-zl", if (e <= 6, "research/results/bmd-20261003-zw", if (e == 7, "research/results/bmd-20261003-zy", "research/results/bmd-20261003-zz")));
hullval(pts, j) = {
  \\ upper hull value at abscissa j by brute force over pairs bracketing j (pts sorted by abscissa)
  my(best = -1e100);
  for (a = 1, #pts, if (pts[a][1] <= j, for (b = a, #pts, if (pts[b][1] >= j,
    my(v = if (pts[b][1] == pts[a][1], pts[a][2], pts[a][2] + (pts[b][2] - pts[a][2]) * (j - pts[a][1]) / (pts[b][1] - pts[a][1]))); if (v > best, best = v)))));
  best;
}
profile(P) = {
  my(D = poldegree(P), pts = List());
  for (j = 0, D, my(c = polcoef(P, j, 't)); if (c, listput(pts, [j, log(abs(c)) / log(10)])));
  my(v = Vec(pts), gaps = 0);
  if (#v <= 300, foreach (v, p, if (hullval(v, p[1]) - p[2] > 10, gaps++)), gaps = -1);
  [D + 1, #v, gaps];
}
dt(f) = my(b = f[1], g = f[2], p = f[3]); [b - 1, g - 1, b * (1 - 't) * p - g * 't * p + 't * (1 - 't) * deriv(p, 't)];
dx(f) = my(h = dt(f)); [h[1], h[2] + 2, h[3]];
{
for (e = 4, 9,
  my(W = read(Str(src(e), "/W_last_e", e, ".gp")), d = poldegree(W), P = numerator(subst(W, 'x, 't / (1 - 't)) * (1 - 't)^d), pr = profile(P));
  emit(Str("e=", e, ": P coefficients ", pr[1], ", nonzero ", pr[2], ", more than 10 decades below the hull ", pr[3], " (-1: not computed)")));
for (e = 4, 6,
  my(n = Rn(e), k = 4 * e, a = -n - 7/2, out = List());
  for (j = 0, 3, my(f = [j - 7/2, 6 - j, 1]); for (r = 1, n, f = dx(f)); f = [f[1], f[2] + a + k - 1, f[3]];
    for (r = 1, k, f = dt(f)); f = [f[1] + k - a, f[2], f[3]]; for (r = 1, k, f = dt(f));
    my(p = f[3]); p /= 't^valuation(p, 't); while (subst(p, 't, 1) == 0, p /= (1 - 't));
    my(pr = profile(p)); listput(out, Str("rho_", j, ": coefficients ", pr[1], ", nonzero ", pr[2], ", deep gaps ", pr[3])));
  emit(Str("e=", e, " IV images: ", strjoin(Vec(out), "; "))));
}
