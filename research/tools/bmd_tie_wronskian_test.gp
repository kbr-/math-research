\\ Karlin-Szego test for the confluent tie pure block (7 October 2026; cycle bmd-20261007-zr).
\\ Question: is H_m (the part of det B_m prime to c(c-1)) proportional to the part prime to c(c-1) of a Wronskian in c
\\ of consecutive coefficients h_a, ..., h_(a+k-1) of h_c = (1+T)^(-5/2-d) (1+cT)^(3/2+d)?  (Karlin-Szego: Hankel
\\ determinants of classical orthogonal polynomials are (x^2-1)^N times Wronskians.)  Scans 0 <= a <= 3m, 1 <= k <= 2m,
\\ m = 2, 3, 4.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
strip01(f) = { if (f == 0, return(0)); while (subst(f, 'c, 0) == 0, f /= 'c); while (subst(f, 'c, 1) == 0, f /= ('c - 1)); f / content(f); }
hc(m, k) = { my(d = m * (m - 1) / 2, al = 5/2 + d, be = 3/2 + d); if (k < 0, 0, sum(j = 0, k, bn(-al, k - j) * bn(be, j) * 'c^j)); }
wr(v) = { my(k = #v); matdet(matrix(k, k, i, j, dn(v[j], i - 1))); }
dn(f, n) = { for (t = 1, n, f = deriv(f, 'c)); f; }
{
for (m = 2, 4,
  my(H = strip01(matdet(matrix(2 * m, 2 * m, i, j, hc(m, m + i - j)))), hits = List());
  for (a = 0, 3 * m, for (k = 1, 2 * m,
    my(W = wr(vector(k, i, hc(m, a + i - 1)))); if (W != 0, my(S = strip01(W)); if (S == H || S == -H, listput(hits, [a, k])))));
  emit(Str("m = ", m, ": deg H_m = ", poldegree(H), "; Wronskians of h_a..h_(a+k-1) equal to H_m (stripped): ", Vec(hits))));
}
quit
