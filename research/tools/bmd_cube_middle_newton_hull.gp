\\ Newton polygon of middle-step far polynomials in t = x/(1+x) (3 October 2026; cycle bmd-20261003-zzm).
\\ For W_mid_b<b>_k<k>.gp (l = 2; research/results/bmd-20261003-zzm/): P(t) = (1-t)^d W(t/(1-t)); long edges (length >= 8) of the
\\ upper hull of log|coefficients| as [length, e*u].  Question: do the middle far polynomials have the edge structure of the last
\\ step (four edges of length n + 7/2), or a different one?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 60);
Rn(n) = n * (2 * n - 1);
hull(pts) = {
  my(H = List());
  foreach (pts, p, while (#H >= 2 && (H[#H][2] - H[#H - 1][2]) * (p[1] - H[#H][1]) <= (p[2] - H[#H][2]) * (H[#H][1] - H[#H - 1][1]), listpop(H)); listput(H, p));
  Vec(H);
}
{
foreach ([[6, 4], [7, 5], [8, 6]], B, my(b = B[1], k = B[2], e = k - 1, W = read(Str("research/results/bmd-20261003-zzm/W_mid_b", b, "_k", k, ".gp")), d = poldegree(W));
  my(P = numerator(subst(W, 'x, 't / (1 - 't)) * (1 - 't)^d), D = poldegree(P));
  my(pts = select(p -> p != 0, vector(D + 1, j, my(c = polcoef(P, j - 1, 't)); if (c, [j - 1, log(abs(c))], 0))), H = hull(pts), segs = List());
  for (i = 1, #H - 1, my(l = H[i + 1][1] - H[i][1]); if (l >= 8, listput(segs, [l, precision(-(H[i + 1][2] - H[i][2]) / l * e, 4) * 1.])));
  emit(Str("(b,k)=(", b, ",", k, ") e=", e, ", n + 7/2 = ", Rn(e) + 7/2, ", deg ", D, ": long edges [length, e*u] ", Vec(segs))));
}
