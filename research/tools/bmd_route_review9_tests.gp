\\ Tests of the route review of 8 October 2026 (cycle bmd-20261008-r) on the holonomic description of the confluent
\\ tie window (lem:cube-tie-holonomic-staircase, check:cube-tie-holonomic-q).  m = 2, 3.
\\ T1: is the apparent-singularity factor S(k, c) of q_(3m) at k = M the part off c(c-1) of the square pure determinant
\\     on the columns T^M..T^(M+3m-1), for M = d..d+4 (up to a constant)?
\\ T3: gcd over M = d..d+4 of N_1(M, c) (the point-row factor), off c(c-1).
\\ B1: gcd of consecutive shifted square pure determinants H^(M), H^(M+1) (parts off c(c-1)), M = d..d+3.
default(parisizemax, 4 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
pure(r, m, k) = if (r <= 2 * m, bn(-5/2, k - (r - 1)), my(n = r - 2 * m - 1); bn(-3/2, k - n) * 'c^max(k - n, 0));
st(q) = { if (q == 0, return(0)); q = q / 'c^valuation(q, 'c); while (subst(q, 'c, 1) == 0, q = q / ('c - 1)); q / pollead(q, 'c); }
rf(m, r) = prod(i = 0, r - 1, -('k + i - 2 * m + 7/2) / ('k + i + 1));
rg(m, r) = prod(i = 0, r - 1, -'c * ('k + i - m + 5/2) / ('k + i + 1));
{
foreach([2, 3], m, my(n = 3 * m, d = m * (m - 1) / 2, A = matrix(n, n + 1), q, S, N1, H = vector(5));
  for (j = 0, 2 * m - 1, for (r = 0, n, A[j + 1, r + 1] = rf(m, r) * ('k + r)^j));
  for (j = 0, m - 1, for (r = 0, n, A[2 * m + j + 1, r + 1] = rg(m, r) * ('k + r)^j));
  q = matker(A)[, 1]; my(den = 1); for (r = 1, n + 1, den = lcm(den, denominator(q[r]))); q = q * den;
  my(g = 0); for (r = 1, n + 1, g = gcd(g, q[r])); q = q / g;
  my(F = factor(q[n + 1])); S = 1; for (t = 1, #F[, 1], if (poldegree(F[t, 1], 'k) > 0 && poldegree(F[t, 1], 'c) > 0, S = F[t, 1]));
  N1 = numerator(sum(r = 0, n, q[r + 1] * (-1)^r * ('k + r + 1) * ('k + r + 2)) / (('k + 1) * ('k + 2)));
  my(t1 = List(), gN = 0);
  for (Mi = 1, 5, my(M = d + Mi - 1);
    H[Mi] = st(matdet(matrix(n, n, r, j, pure(r, m, M + j - 1))));
    listput(t1, st(subst(S, 'k, M)) == H[Mi]);
    gN = gcd(gN, subst(N1, 'k, M)));
  emit(Str("T1, m = ", m, ": S(M, c) equals the essential square pure determinant at start M, for M = d..d+4: ", Vec(t1)));
  emit(Str("T3, m = ", m, ": gcd over the window of N_1(M, c), off c(c-1), has degree ", poldegree(st(gN), 'c)));
  emit(Str("B1, m = ", m, ": degrees of gcd(H^(M), H^(M+1)) for M = d..d+3: ", vector(4, i, poldegree(gcd(H[i], H[i + 1]), 'c)),
    "; degrees of H^(M): ", vector(5, i, poldegree(H[i], 'c)))));
\\ LY: moduli of the roots of the essential square pure determinant H at start d, m = 2..4 (Lee-Yang-type test:
\\ do the special values of the pure block lie on one circle?)
foreach([2, 3, 4], m, my(n = 3 * m, d = m * (m - 1) / 2, H = st(matdet(matrix(n, n, r, j, pure(r, m, d + j - 1)))));
  emit(Str("LY, m = ", m, ": moduli of the roots of H_m: ", apply(z -> round(abs(z) * 1000) / 1000., Vec(polroots(H))))));
}
quit
