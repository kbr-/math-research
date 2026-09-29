\\ The two triple roots of the Wronskian at the six-root repeated factor (30 September 2026).
\\ Input: DATA.gp from bmd_cube_repeated_factor_hyperplanes.py (A, B line rows, G exponent-four
\\ factors). At every F_p-rational root u0 of G on the first LN lines, with a = a(u0):
\\  (1) q(z) = gcd(W, W', W'') is the product of the triple-root factors of W_a (expected degree 2);
\\  (2) harmonic test: for every pair {x, y} of the seven points a_1..a_6, infinity, is {x, y} harmonic
\\      with respect to the roots of q = z^2 - s z + P, i.e. x y - s (x + y) / 2 + P = 0
\\      (x - s/2 = 0 for y = infinity)? Such a pair is swapped by the involution fixing both roots;
\\  (3) do the roots of q satisfy p^(k)(z) = 0 for p = prod (z - a_i), k = 1..5 (resultant test)?
\\ Controls: the same tests at a random point of each line with q replaced by a random quadratic.
p = 2^61 - 1;
N = 6; R = 15; lam = 45; th = 30;
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta32(m) = binomial(-3/2, m);
Hk(k, x, y) = sum(m = 0, k, beta32(m) * beta32(k - m) * x^m * y^(k - m));
pairs = vector(R); pc = 0; for (i = 1, N, for (j = i + 1, N, pc++; pairs[pc] = [i, j]));
Amat(b, L) = matrix(R, L + 1, r, k, Hk(k - 1, b[pairs[r][1]], b[pairs[r][2]]));
Fb(b) = matdet(Amat(b, R - 1)) / prod(r = 1, R, (b[pairs[r][1]] - b[pairs[r][2]])^(N - 2));
W(a, z) = Fb(vector(N, i, 1/(a[i] - z))) * prod(i = 1, N, a[i] - z)^th;
dk(f, k) = my(g = f); for (i = 1, k, g = deriv(g, 'z)); g;
tests(a, q) = {
  my(s = -polcoef(q, 1), P = polcoef(q, 0), harm = List(), der = List(), pp = prod(i = 1, N, 'z - a[i]));
  for (i = 1, N, for (j = i + 1, N, if (a[i] * a[j] - s * (a[i] + a[j]) / 2 + P == 0, listput(harm, [i, j]))));
  for (i = 1, N, if (a[i] - s / 2 == 0, listput(harm, [i, "inf"])));
  for (k = 1, 5, if (polresultant(q, dk(pp, k), 'z) == 0, listput(der, k)));
  [Vec(harm), Vec(der)];
}
LN = if (getenv("LN"), eval(getenv("LN")), 2);
{
setrand(1);
for (l = 1, LN,
  my(us = apply(r -> lift(r), polrootsmod(G[l], p)), zs = vector(2 * lam + 1, h, Mod(h + 7, p)));
  emit(Str("line ", l, " (seed ", SEEDS[l], "): ", #us, " rational roots"));
  foreach (us, u0,
    my(a = vector(N, i, Mod(A[l, i], p) + Mod(B[l, i], p) * u0));
    my(w = polinterpolate(zs, vector(#zs, h, W(a, zs[h])), 'z));
    my(q = gcd(gcd(w, deriv(w, 'z)), dk(w, 2)));
    q = q / pollead(q);
    my(t = tests(a, q), f = factormod(lift(q), p));
    emit(Str("  u0 = ", u0, ": deg q = ", poldegree(q), ", q splits as ", vector(#f~, k, poldegree(f[k, 1])),
      "; harmonic pairs ", t[1], "; roots of p^(k) for k in ", t[2])));
  my(a = vector(N, i, Mod(A[l, i], p) + Mod(B[l, i], p) * random(p)), q = 'z^2 + random(p) * 'z + random(p));
  emit(Str("  control (random point, random quadratic): ", tests(a, Mod(1, p) * q))));
}
