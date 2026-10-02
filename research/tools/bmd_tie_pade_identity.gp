\\ Determinant identity det B_m = kappa c^(m d) C_m for the confluent tie pure block (7 October 2026; cycle bmd-20261007-zq).
\\ C_m = det[h_(m+i-j)]_(i,j<2m), h_c = (1+T)^(-5/2-d) (1+cT)^(3/2+d), d = binom(m,2).  Prints det B_m / (c^(m d) C_m)
\\ for m = 1..5 (must be a nonzero rational constant).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
hc(m, k) = { my(d = m * (m - 1) / 2, al = 5/2 + d, be = 3/2 + d); if (k < 0, 0, sum(j = 0, k, bn(-al, k - j) * bn(be, j) * 'c^j)); }
{
for (m = 1, 5,
  my(d = m * (m - 1) / 2, n = 3 * m);
  my(B = matrix(n, n, r, j, my(k = d + j - 1); if (r <= 2 * m, bn(-5/2, k - (r - 1)), my(q = r - 2 * m - 1); bn(-3/2, k - q) * 'c^max(k - q, 0))));
  my(C = matdet(matrix(2 * m, 2 * m, i, j, hc(m, m + i - j))), ratio = matdet(B) / ('c^(m * d) * C));
  emit(Str("m = ", m, ": det B_m / (c^(m d) C_m) = ", ratio, ", constant: ", type(ratio) == "t_INT" || type(ratio) == "t_FRAC")));
}
quit
