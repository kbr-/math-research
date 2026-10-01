\\ 2-adic segments of the last even-peeling far polynomials (3 October 2026; cycle bmd-20261003-zj).
\\ Conjecture tested (Ore / Montes residual certificate): for every e >= 2 the 2-adic Newton polygon of the primitive
\\ W_(b-1) in Z[x] (c = 1, b = e+2) has a segment of slope -(2 - 2^-(e+1)) and length e 2^(e+1); its residual polynomial
\\ over F_2 (degree e) is squarefree.  A squarefree residual polynomial makes the e 2^(e+1) roots of that slope simple
\\ (they split into factors with distinct residual roots, each of ramification index divisible by 2^(e+1)).
\\ Prediction fixed before the run: at e = 4 a segment of slope -63/32 and length 128.
\\ Prints for e = 1..4: all 2-adic segments (slope, length) and the residual polynomial of each segment.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
farW(e, l, c) = {
  my(bl = [[0, 0, Rn(e)], [-3, 0, 1], [0, -(Rn(l) + 2), Rn(l)], [-7/2, 0, 4 * e], [-5/2, 1/2 - 4 * l, 4 * l], [0, -7/2 + 4 * e - 4 * e * l, 4 * e * l]]);
  my(d = sum(i = 1, 6, bl[i][3]), M = matrix(d, d), row = 0);
  foreach (bl, b, for (j = 0, b[3] - 1, row++; my(g = 'x^j);
    for (m = 1, d, M[row, m] = g; g = deriv(g, 'x) + (b[2] / 'x + b[1] * c / (1 + c * 'x)) * g)));
  my(N = numerator(matdet(M)));
  while (subst(N, 'x, 0) == 0, N = N / 'x); while (subst(N, 'x, -1/c) == 0, N = N / (1 + c * 'x));
  N = N * denominator(content(N)); N / content(N);
}
\\ lower convex hull of (i, v_p(a_i)); for each edge, slope, length and residual polynomial
residuals(P, p) = {
  my(d = poldegree(P), pts = List());
  for (i = 0, d, my(a = polcoef(P, i)); if (a != 0, listput(pts, [i, valuation(a, p)])));
  pts = Vec(pts);
  my(hull = List(), k = 1);
  while (k < #pts,
    my(best = k + 1, bs = (pts[k + 1][2] - pts[k][2]) / (pts[k + 1][1] - pts[k][1]));
    for (j = k + 2, #pts, my(s = (pts[j][2] - pts[k][2]) / (pts[j][1] - pts[k][1])); if (s <= bs, best = j; bs = s));
    listput(hull, [k, best, bs]); k = best);
  my(out = List());
  foreach (hull, h, my(i0 = pts[h[1]][1], i1 = pts[h[2]][1], s = h[3], v = denominator(s), res = 0);
    for (j = h[1], h[2], my(i = pts[j][1], val = pts[j][2]);
      if (val - pts[h[1]][2] == s * (i - i0), res += Mod(polcoef(P, i) / p^val, p) * 'y^((i - i0) / v)));
    \\ newtonpoly convention: slope of the root valuations is minus the hull slope
    listput(out, [-s, i1 - i0, lift(res), if (res == 0, "?", my(F = factormod(lift(res), p)); [vector(#F~, i, [F[i, 1], F[i, 2]])])]));
  Vec(out);
}
main() = {
  my(emax = if (getenv("EMAX"), eval(getenv("EMAX")), 4));
  for (e = 1, emax,
    my(W = farW(e, 1, 1), d = poldegree(W));
    emit(Str("e=", e, " b=", e + 2, " deg ", d, "; predicted segment slope ", -(2 - 2^-(e + 1)), " length ", e * 2^(e + 1), ":"));
    foreach (residuals(W, 2), t, emit(Str("  slope ", t[1], ", length ", t[2], ", residual ", t[3], ", factorization over F_2 ", t[4]))));
}
default(parisizemax, 6000000000);
main();
