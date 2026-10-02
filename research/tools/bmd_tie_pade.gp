\\ Pade form of the confluent tie pure block (7 October 2026; cycle bmd-20261007-zq).
\\ Tested statement (lem:cube-tie-pure-pade-normality): with d = binom(m,2), alpha = 5/2 + d, beta = 3/2 + d and
\\ h_c(T) = (1+T)^(-alpha) (1+cT)^beta = sum_k h_k T^k, the pure block determinant Delta_m(c) and the Toeplitz
\\ determinant C_m(c) = det[h_(m+i-j)]_(0<=i,j<2m) have the same part prime to c(c-1), up to sign, (both equal H_m up to a constant);
\\ and the (2m+1) x 2m Toeplitz matrix [h_(m+i-j)]_(0<=i<=2m, j<2m) has rank 2m for all c outside {0,1} iff the pure
\\ rows have full rank on the 3m+1 columns T^d..T^(d+3m) (gcd of its 2m-minors, stripped).  m = 1..5.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
strip01(f) = { if (f == 0, return(0)); while (subst(f, 'c, 0) == 0, f /= 'c); while (subst(f, 'c, 1) == 0, f /= ('c - 1)); f / content(f); }
hc(m, k) = { my(d = m * (m - 1) / 2, al = 5/2 + d, be = 3/2 + d); if (k < 0, 0, sum(j = 0, k, bn(-al, k - j) * bn(be, j) * 'c^j)); }
{
for (m = 1, 5,
  my(d = m * (m - 1) / 2, n = 3 * m);
  my(B = matrix(n, n, r, j, my(k = d + j - 1); if (r <= 2 * m, bn(-5/2, k - (r - 1)), my(q = r - 2 * m - 1); bn(-3/2, k - q) * 'c^max(k - q, 0))));
  my(D = strip01(matdet(B)), C = strip01(matdet(matrix(2 * m, 2 * m, i, j, hc(m, m + i - j)))));
  my(Tw = matrix(2 * m + 1, 2 * m, i, j, hc(m, m + i - j)), g = 0);
  for (drop = 1, 2 * m + 1, g = gcd(g, matdet(vecextract(Tw, select(t -> t != drop, [1 .. 2 * m + 1]), [1 .. 2 * m]))));
  emit(Str("m = ", m, ": stripped pure determinant = stripped Toeplitz determinant: ", D == C || D == -C, " (degree ", poldegree(D, 'c),
    "); wide Toeplitz gcd stripped: ", strip01(g))));
}
quit
