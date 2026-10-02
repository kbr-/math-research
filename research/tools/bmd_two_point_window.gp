\\ Two-point window (7 October 2026; cycle bmd-20261007-x).  Tested statement (a product formula): for a, b not
\\ integers, p, q >= 1 and d >= 0, the (p+q)-square matrix of the coefficients of T^d..T^(d+p+q-1) of the rows
\\ T^i (1+T)^(-a) (i < p) and T^n (1+cT)^(-b) (n < q) has determinant const * c^A (1-c)^B.  This is the pure part of
\\ the confluent tie window (a = 5/2, b = 3/2, p = 2m, q = m, d = binom(m,2)).  Prints the factorization of the
\\ determinant in c for small (a, b, p, q, d), including the confluent tie cases.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(x, k) = if (k < 0, 0, binomial(x, k));
{
win(a, b, p, q, d) = matrix(p + q, p + q, r, j, my(k = d + j - 1);
  if (r <= p, bn(-a, k - (r - 1)), my(n = r - p - 1); bn(-b, k - n) * 'c^max(k - n, 0)));
}
{
foreach([[5/2, 3/2, 2, 1, 0], [5/2, 3/2, 4, 2, 1], [5/2, 3/2, 6, 3, 3], [5/2, 3/2, 8, 4, 6],
         [5/2, 3/2, 4, 2, 0], [5/2, 3/2, 4, 2, 3], [5/2, 3/2, 2, 2, 0], [5/2, 3/2, 3, 3, 2], [1/3, 7/5, 3, 2, 1]], t,
  my(D = matdet(win(t[1], t[2], t[3], t[4], t[5])), F = factor(D));
  emit(Str("(a,b,p,q,d) = ", t, ": det factors ", F[, 1]~, " with exponents ", F[, 2]~)));
}
