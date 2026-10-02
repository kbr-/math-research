\\ Tests of the route review on the special values of the confluent tie window (7 October 2026; cycle bmd-20261007-zk).
\\ W^c(c) as in bmd_confluent_tie_window.gp.
\\ (L1) Two minors with explicit extremes: the first-columns minor (drop the last two columns) and the last-columns minor
\\      (drop the first two).  gcd stripped of c and c-1, m = 2..6.  Constant gcd for every m would make Z^W_m trivial
\\      through a resultant of two explicit polynomials.
\\ (L2) Smith normal form of W^c(c) over Q[c] (matsnf on the polynomial matrix), m = 1..3: are all invariant factors
\\      products of powers of c and c-1 (left primeness off {0,1})?
\\ (B1) Overlap spectrum: smallest singular value of W^c(c) divided by the largest, at real c on a grid in [-3, 3] avoiding
\\      0 and 1 by 0.05, m = 2..5 (numerical, 60 digits).  A floor bounded away from 0 is evidence for a variational
\\      (Lowdin overlap) lower bound.
default(parisizemax, 4 * 10^9); default(realprecision, 60);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
rowco(r, m, k) = {
  if (r <= 2 * m, return(bn(-5/2, k - (r - 1))));
  if (r <= 3 * m, my(n = r - 2 * m - 1); return(bn(-3/2, k - n) * 'c^max(k - n, 0)));
  if (r == 3 * m + 1, return(bn(-3, k)));
  if (r == 3 * m + 2, return(sum(a = 0, k, bn(-3/2, a) * bn(-3/2, k - a) * 'c^(k - a))));
  sum(a = 0, k - 1, bn(-5/2, a) * bn(-3/2, k - 1 - a) * 'c^(k - 1 - a));
}
winmat(m) = { my(d = m * (m - 1) / 2); matrix(3 * m + 3, 3 * m + 5, r, j, rowco(r, m, d + j - 1)); }
strip01(f) = { if (f == 0, return(0)); while (subst(f, 'c, 0) == 0, f /= 'c); while (subst(f, 'c, 1) == 0, f /= ('c - 1)); f / content(f); }
{
for (m = 2, 6,
  my(A = winmat(m), w = 3 * m + 5, D1 = matdet(vecextract(A, "..", [1 .. w - 2])), D2 = matdet(vecextract(A, "..", [3 .. w])));
  emit(Str("(L1) m = ", m, ": gcd(first, last) stripped of c, c-1 = ", strip01(gcd(D1, D2)), "; degrees ", poldegree(strip01(D1), 'c), ", ", poldegree(strip01(D2), 'c))));
}
{
for (m = 1, 3,
  my(A = winmat(m), S = iferr(matsnf(A~, 6), E, E));
  emit(Str("(L2) m = ", m, ": invariant factors stripped of c, c-1: ", if (type(S) == "t_ERROR", Str("matsnf failed: ", S), apply(f -> if (f == 0, 0, strip01(f)), S)))));
}
{
for (m = 2, 5,
  my(A = winmat(m), worst = oo, at = 0);
  forstep (x = -3, 3, 1/20, if (abs(x) < 1/20 || abs(x - 1) < 1/20, next);
    my(N = substvec(A, ['c], [x * 1.]), sv = sqrt(abs(qfjacobi(N * N~)[1])), r = vecmin(sv) / vecmax(sv));
    if (r < worst, worst = r; at = x));
  emit(Str("(B1) m = ", m, ": min over the grid of sigma_min / sigma_max = ", precision(worst, 6), " at c = ", at)));
}
quit
