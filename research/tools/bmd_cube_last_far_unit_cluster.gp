\\ The unit-root 2-adic cluster of the last even-peeling far polynomials (3 October 2026; cycle bmd-20261003-zl).
\\ At first order the 4(e+1) unit roots of W_(b-1) (c = 1) all reduce to -1 (residual (y+1)^(4e+4)).  Expand W in t = x+1
\\ and take the 2-adic Newton polygon in t: its segments of positive slope (roots with v_2(x+1) > 0) are the unit cluster;
\\ each segment of slope s (root valuation of t) and its residual polynomial over F_2 are printed.
\\ Question: is there a uniform type (slopes, lengths) with residuals without roots of multiplicity >= 3?  That would prove
\\ the 4(e+1) roots of the cluster have multiplicity at most two for every e (Ore at second order).
\\ The polynomials W_(b-1) are also written to the output directory (as PARI expressions) for reuse.
OUT = getenv("OUT"); WDIR = getenv("WDIR");
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
    my(F = factormod(lift(res), p));
    listput(out, [-s, i1 - i0, vector(#F~, i, [poldegree(F[i, 1]), F[i, 2]])]));
  Vec(out);
}
main() = {
  my(emax = if (getenv("EMAX"), eval(getenv("EMAX")), 4));
  for (e = 1, emax,
    my(W = farW(e, 1, 1), T = subst(W, 'x, 't - 1), d = poldegree(W));
    if (WDIR != 0 && WDIR != "", write(Str(WDIR, "/W_last_e", e, ".gp"), W));
    emit(Str("e=", e, " b=", e + 2, " deg ", d, ", unit cluster predicted size ", 4 * (e + 1), "; segments in t = x+1 [root valuation of t, length, residual factor (degree, multiplicity)]:"));
    foreach (residuals(T, 2), r, if (r[1] > 0, emit(Str("  ", r)))));
}
default(parisizemax, 6000000000);
main();
