\\ Newton hull at infinity of the last-step far polynomial (4 October 2026; cycle bmd-20261004-z).
\\ Hypothesis (edge as a Newton edge at infinity): the edge ring of W_(b-1) (roots at |x| ~ 5..18 for e = 2, 4) is
\\ predicted by the archimedean Newton polygon of Q(s) = s^D W((1-s)/s), s = 1/(1+x), D = deg W: hull segments of slope
\\ -u predict about (length) roots near |s| = e^u.  For e = 2..9: hull segments (length, predicted |1+x| = e^-u) with
\\ predicted |1+x| >= 4, against the actual number of roots with |1+x| >= 4, and the radii in |1+x| of those roots
\\ (min, median, max), to see whether the ring stays bounded in |x| as e grows.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 60); default(parisizemax, 2000000000);
wfile(e) = { my(d = Map([2, "zl"; 3, "zl"; 4, "zw"; 5, "zw"; 6, "zw"; 7, "zy"; 8, "zz"; 9, "zz"]));
  Str("research/results/bmd-20261003-", mapget(d, e), "/W_last_e", e, ".gp"); }
\\ upper convex hull of points (j, y_j)
hull(pts) = {
  my(H = List());
  foreach (pts, p, while (#H >= 2 && (H[#H][2] - H[#H - 1][2]) * (p[1] - H[#H - 1][1]) <= (p[2] - H[#H - 1][2]) * (H[#H][1] - H[#H - 1][1]), listpop(H));
    listput(H, p));
  Vec(H);
}
{
for (e = 2, 9,
  my(W = read(wfile(e)), D = poldegree(W), Q = 0);
  \\ Q(s) = s^D W((1-s)/s) = sum_j w_j (1-s)^j s^(D-j)
  Q = substpol(subst(W, 'x, (1 - 's) / 's) * 's^D, 's, 's);
  Q = simplify(Q);
  my(pts = List());
  for (j = 0, poldegree(Q, 's), my(c = polcoef(Q, j, 's)); if (c != 0, listput(pts, [j, log(abs(c))])));
  my(H = hull(Vec(pts)), segs = List());
  for (i = 1, #H - 1, my(len = H[i + 1][1] - H[i][1], u = -(H[i + 1][2] - H[i][2]) / len);
    \\ coefficient of s^j grows like rho^-j for roots at |s| = rho: slope -u means roots near |s| = e^u... sign: slope = -log rho
    my(rho = exp(-(H[i + 1][2] - H[i][2]) / len));
    if (1 / rho >= 4, listput(segs, [len, round(1 / rho * 100) / 100.])));
  my(rx = polroots(W), big = select(r -> abs(1 + r) >= 4, rx), rad = vecsort(apply(r -> abs(1 + r), big)));
  emit(Str("e=", e, ": deg W = ", D, ", edge 8e+4 = ", 8 * e + 4, "; hull segments with predicted |1+x| >= 4 [length, |1+x|]: ", Vec(segs),
    " (total ", sum(i = 1, #segs, segs[i][1]), "); roots with |1+x| >= 4: ", #big,
    if (#big, Str(", |1+x| min ", round(rad[1] * 100) / 100., " median ", round(rad[(#rad + 1) \ 2] * 100) / 100., " max ", round(rad[#rad] * 100) / 100.), ""))));
}
