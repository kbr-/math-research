\\ Pellet separation of the far-root circles (3 October 2026; cycle bmd-20261003-zzg).
\\ Pellet's theorem: if |a_k| r^k > sum_{j != k} |a_j| r^j for a polynomial sum a_j t^j, then exactly k roots lie in |t| < r.
\\ For P(t) = (1-t)^d W(t/(1-t)), W = saved W_(b-1), e = 4..9: at each upper-hull vertex k between two long segments
\\ (length >= 8), take r = exp of minus the mean of the two adjacent slopes, test Pellet exactly (rational arithmetic on |a_j|
\\ with r replaced by a nearby rational), and report k and the margin log(|a_k| r^k / sum_{j != k} |a_j| r^j).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 80);
src(e) = if (e <= 6, "research/results/bmd-20261003-zw", if (e == 7, "research/results/bmd-20261003-zy", "research/results/bmd-20261003-zz"));
hull(pts) = {
  my(H = List());
  foreach (pts, p, while (#H >= 2 && (H[#H][2] - H[#H - 1][2]) * (p[1] - H[#H][1]) <= (p[2] - H[#H][2]) * (H[#H][1] - H[#H - 1][1]), listpop(H)); listput(H, p));
  Vec(H);
}
{
for (e = 4, 9,
  my(W = read(Str(src(e), "/W_last_e", e, ".gp")), d = poldegree(W), P = numerator(subst(W, 'x, 't / (1 - 't)) * (1 - 't)^d), D = poldegree(P));
  my(A = vector(D + 1, j, abs(polcoef(P, j - 1, 't))), pts = select(p -> p != 0, vector(D + 1, j, if (A[j], [j - 1, log(A[j])], 0))), H = hull(pts));
  my(segs = List()); for (i = 1, #H - 1, my(l = H[i + 1][1] - H[i][1]); listput(segs, [i, l, (H[i + 1][2] - H[i][2]) / l]));
  my(long = select(s -> s[2] >= 8, Vec(segs)), res = List());
  for (q = 1, #long - 1, my(s1 = long[q], s2 = long[q + 1]);
    \\ the vertex between the two long segments with the best Pellet margin
    my(best = [-1e100, 0]);
    for (v = s1[1] + 1, s2[1], my(k = H[v][1], u = -(s1[3] + s2[3]) / 2, r = bestappr(exp(u), 10^12), lead = A[k + 1] * r^k, rest = sum(j = 0, D, if (j != k, A[j + 1] * r^j, 0)));
      my(mg = log(lead) - log(rest)); if (mg > best[1], best = [mg, k]));
    listput(res, [best[2], precision(best[1], 4) * 1.]));
  emit(Str("e=", e, ": long segments ", #long, "; Pellet at the vertices between them [k, log-margin] (margin > 0: exactly k roots in |t| < r): ", Vec(res))));
}
