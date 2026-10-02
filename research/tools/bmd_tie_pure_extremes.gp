\\ Extreme coefficients of the pure block of the confluent tie window (7 October 2026; cycle bmd-20261007-zh).
\\ Pure block: coefficients of T^d..T^(d+3m-1), d = binom(m,2), of T^i (1+T)^(-5/2) (i < 2m) and T^n (1+cT)^(-3/2) (n < m).
\\ Tested statement (lem:cube-tie-pure-extreme-coefficients): its determinant Delta_m(c) has c-order exactly m d and degree
\\ exactly m (d + 2m), with lowest coefficient +- s_(d^m)(1^(3/2)) s_((d+m)^(2m))(1^(5/2)) and top coefficient
\\ +- s_(d^(2m))(1^(5/2)) s_((d+2m)^m)(1^(3/2)), where s_(u^h)(1^a) = prod over the cells (i,j) of the h x u rectangle of
\\ (a + j - i) / hook (hook-content formula).  Checks m = 1..6 exactly.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
pure(m) = { my(d = m * (m - 1) / 2); matrix(3 * m, 3 * m, r, j, my(k = d + j - 1);
  if (r <= 2 * m, bn(-5/2, k - (r - 1)), my(n = r - 2 * m - 1); bn(-3/2, k - n) * 'c^max(k - n, 0))); }
rect(u, h, a) = prod(i = 0, h - 1, prod(j = 0, u - 1, (a + j - i) / ((u - 1 - j) + (h - 1 - i) + 1)));
{
for (m = 1, 6,
  my(d = m * (m - 1) / 2, D = matdet(pure(m)), lo = valuation(D, 'c), hi = poldegree(D, 'c));
  my(clo = polcoef(D, lo, 'c), chi = pollead(D, 'c));
  my(plo = rect(d, m, 3/2) * rect(d + m, 2 * m, 5/2), phi = rect(d, 2 * m, 5/2) * rect(d + 2 * m, m, 3/2));
  emit(Str("m = ", m, ": c-order ", lo, " (predicted ", m * d, "), degree ", hi, " (predicted ", m * (d + 2 * m), "), (c-1)-order ",
    valuation(D, 'c - 1), "; lowest coefficient = +-prediction: ", abs(clo) == abs(plo), ", top coefficient = +-prediction: ", abs(chi) == abs(phi))));
}
quit
