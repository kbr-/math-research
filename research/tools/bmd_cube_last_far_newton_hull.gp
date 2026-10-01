\\ Archimedean Newton polygon of the last-step far polynomial in t = x/(1+x) (3 October 2026; cycle bmd-20261003-zzg).
\\ Ostrowski: root moduli of a polynomial are approximated by the slopes of the upper convex hull of (j, log|c_j|); a hull
\\ segment of horizontal length l and slope -u predicts about l roots near |t| = e^u.  For e = 6..9: P(t) = (1-t)^d W(t/(1-t))
\\ (W = saved W_(b-1), d = deg W), hull segments of length >= 8, reported as (length, e * u), against the observed circle
\\ peaks of e log|t| (circle-radii.txt).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 60);
Rn(n) = n * (2 * n - 1);
src(e) = if (e <= 6, "research/results/bmd-20261003-zw", if (e == 7, "research/results/bmd-20261003-zy", "research/results/bmd-20261003-zz"));
hull(pts) = {
  my(H = List());
  foreach (pts, p, while (#H >= 2 && (H[#H][2] - H[#H - 1][2]) * (p[1] - H[#H][1]) <= (p[2] - H[#H][2]) * (H[#H][1] - H[#H - 1][1]), listpop(H)); listput(H, p));
  Vec(H);
}
{
for (e = 6, 9,
  my(W = read(Str(src(e), "/W_last_e", e, ".gp")), d = poldegree(W), P = numerator(subst(W, 'x, 't / (1 - 't)) * (1 - 't)^d));
  my(pts = select(p -> p != 0, vector(poldegree(P) + 1, j, my(c = polcoef(P, j - 1, 't)); if (c, [j - 1, log(abs(c))], 0))));
  my(H = hull(pts), segs = List());
  for (i = 1, #H - 1, my(l = H[i + 1][1] - H[i][1], s = (H[i + 1][2] - H[i][2]) / l); if (l >= 8, listput(segs, [l, precision(-s * e, 4) * 1.])));
  emit(Str("e=", e, ": deg P = ", poldegree(P), ", hull vertices ", #H, ", segments (length >= 8) as [length, e*u] with predicted |t| = exp(u): ", Vec(segs))));
}
