\\ Last-step far polynomials from the explicit six-space, e = 3..6 (3 October 2026; cycle bmd-20261003-zw).
\\ Builds Z_e of prop:cube-last-far-six-space (same steps as bmd_cube_last_far_six_space.gp), takes the far part of its
\\ Wronskian in t, maps back to x (x = t/(1-t)), checks e = 3 against the saved W_last_e3.gp, writes W_last_e<e>.gp for e >= 4,
\\ and reports root geometry: degree, squarefreeness (exact), min/median nearest-neighbour ratio, root radius range, distance to
\\ the branch points, number of real roots.  Question: do the separation ratio and the root region converge as e grows?
OUT = getenv("OUT");
DIR = getenv("DIR");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
dt(f) = my(b = f[1], g = f[2], p = f[3]); [b - 1, g - 1, b * (1 - 't) * p - g * 't * p + 't * (1 - 't) * deriv(p, 't)];
dx(f) = my(h = dt(f)); [h[1], h[2] + 2, h[3]];
normf(f) = { my(b = f[1], g = f[2], p = f[3], v); if (p == 0, return(f)); v = valuation(p, 't); p /= 't^v; b += v;
  v = 0; while (subst(p, 't, 1) == 0, p /= (1 - 't); v++); [b, g + v, p]; }
far(P) = { P /= 't^valuation(P, 't); while (subst(P, 't, 1) == 0, P /= (1 - 't)); P; }
farW(e) = {
  my(n = Rn(e), k = 4 * e, a = -n - 7/2, B = concat([[0, 3, 1], [-3, 3, 1]], vector(4, j, [j - 1 - 7/2, 7 - j, 1])), Y = vector(6));
  for (i = 1, 6, my(f = B[i]); for (r = 1, n, f = dx(f)); f = [f[1], f[2] + a + k - 1, f[3]];
    for (r = 1, k, f = dt(f)); f = [f[1] + k - a, f[2], f[3]]; for (r = 1, k, f = dt(f)); Y[i] = normf(f));
  my(G = vecmin(apply(f -> f[2], Y)), V = apply(f -> [f[1], G, f[3] * (1 - 't)^(f[2] - G)], Y), M = matrix(6, 6));
  for (i = 1, 6, my(f = V[i]); for (m = 0, 5, M[i, m + 1] = f[3]; f = dt(f)));
  my(Wt = far(matdet(M)), m = poldegree(Wt), Wx = numerator(subst(Wt, 't, 'x / (1 + 'x)) * (1 + 'x)^m));
  Wx / content(Wx);
}
geom(W) = {
  my(r = polroots(W), m = #r, nn = vector(m));
  for (i = 1, m, nn[i] = vecmin(vector(m - 1, j, my(k = if (j < i, j, j + 1)); abs(r[i] - r[k]))));
  my(s = vecsort(nn));
  [precision(s[1] / s[(m + 1) \ 2], 8), precision(s[1], 8), precision(vecmin(abs(r)), 8), precision(vecmax(abs(r)), 8),
   precision(vecmin(abs(r + vectorv(m, i, 1))), 8), #polrootsreal(W)];
}
{
default(realprecision, 300); default(parisizemax, 4000000000);
for (e = 3, 6,
  my(W = farW(e));
  if (e == 3, my(S = read("research/results/bmd-20261003-zl/W_last_e3.gp"));
    emit(Str("e=3 control: equals saved W_last_e3 up to sign: ", W == S || W == -S)));
  if (e >= 4 && DIR != 0 && DIR != "", write(Str(DIR, "/W_last_e", e, ".gp"), W));
  my(g = geom(W));
  emit(Str("e=", e, ": deg ", poldegree(W), " (4(2e^2+e+1) = ", 4 * (2 * e^2 + e + 1), "), squarefree ", poldegree(gcd(W, W')) == 0,
    ", min/median NN ratio ", g[1], ", min distance ", g[2], ", |r| in [", g[3], ", ", g[4], "], min |r+1| ", g[5], ", real roots ", g[6])));
}
