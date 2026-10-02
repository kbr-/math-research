\\ Pure rows of the confluent tie window on all 3m+5 window columns (7 October 2026; cycle bmd-20261007-zq).
\\ Question: do the 3m pure rows T^i (1+T)^(-5/2) (i < 2m), T^n (1+cT)^(-3/2) (n < m) have full rank 3m on the 3m+5
\\ columns T^d..T^(d+3m+4) at every c outside {0,1}?  Prints the gcd of their 3m-minors stripped of c and c-1 (the gcd
\\ stops once trivial), m = 1..5.  A trivial gcd splits the special values of the window into this pure statement
\\ and the independence of the three extra rows modulo the pure span.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
strip01(f) = { if (f == 0, return(0)); while (subst(f, 'c, 0) == 0, f /= 'c); while (subst(f, 'c, 1) == 0, f /= ('c - 1)); f / content(f); }
{
for (m = 1, 5,
  my(d = m * (m - 1) / 2, w = 3 * m + 5, n = 3 * m, g = 0, used = 0);
  my(A = matrix(n, w, r, j, my(k = d + j - 1); if (r <= 2 * m, bn(-5/2, k - (r - 1)), my(q = r - 2 * m - 1); bn(-3/2, k - q) * 'c^max(k - q, 0))));
  forsubset([w, n], S, used++; g = gcd(g, matdet(vecextract(A, "..", Vec(S)))); if (g != 0 && poldegree(strip01(g), 'c) == 0, break));
  emit(Str("m = ", m, ": minors used ", used, " of ", binomial(w, n), "; gcd stripped of c, c-1: ", strip01(g))));
}
quit
