\\ The operator Q of lem:cube-tie-holonomic-staircase and its action on the point row (8 October 2026; cycle
\\ bmd-20261008-q).  Q = sum_r q_r(k) E^r (r = 0..3m) annihilates h_f(k) p(k) (deg p < 2m) and h_g(k) p(k)
\\ (deg p < m), h_f(k+r)/h_f(k) = prod_(i<r) -(k+i-2m+7/2)/(k+i+1), h_g(k+r)/h_g(k) = prod_(i<r) -c(k+i-m+5/2)/(k+i+1).
\\ Its coefficients solve 3m linear equations over Q(k, c) in 3m+1 unknowns; normalized to coprime polynomials.
\\ The point row's sequence e_1(k) = (-1)^k (k+1)(k+2)/2 gives (Q e_1)(k) = R_1(k, c) e_1(k), R_1 rational.
\\ Prints, for m = 2, 3: the bidegrees of q_0 and q_(3m) and their factorizations; the numerator N_1(k, c) of R_1,
\\ its bidegree and factorization over Q; and, as a cross-check with ex:cube-tie-staircase-pairings, the c-degree of
\\ the factor of N_1(M, c) off c(c-1) at M = d.
default(parisizemax, 4 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
rf(m, r) = prod(i = 0, r - 1, -('k + i - 2 * m + 7/2) / ('k + i + 1));
rg(m, r) = prod(i = 0, r - 1, -'c * ('k + i - m + 5/2) / ('k + i + 1));
fmt(F) = vector(#F[, 1], t, [poldegree(F[t, 1], 'k), poldegree(F[t, 1], 'c), F[t, 2]]);
{
foreach([2, 3], m, my(n = 3 * m, A = matrix(n, n + 1), q, N1, e1r);
  for (j = 0, 2 * m - 1, for (r = 0, n, A[j + 1, r + 1] = rf(m, r) * ('k + r)^j));
  for (j = 0, m - 1, for (r = 0, n, A[2 * m + j + 1, r + 1] = rg(m, r) * ('k + r)^j));
  q = matker(A)[, 1];
  my(den = 1); for (r = 1, n + 1, den = lcm(den, denominator(q[r]))); q = q * den;
  my(g = 0); for (r = 1, n + 1, g = gcd(g, q[r])); q = q / g;
  emit(Str("m = ", m, ": q_0 bidegree ", [poldegree(q[1], 'k), poldegree(q[1], 'c)], ", factors [deg_k, deg_c, mult] ", fmt(factor(q[1])),
    "; q_", n, " bidegree ", [poldegree(q[n + 1], 'k), poldegree(q[n + 1], 'c)], ", factors ", fmt(factor(q[n + 1]))));
  \\ (Q e_1)(k) / e_1(k), e_1(k+r)/e_1(k) = (-1)^r (k+r+1)(k+r+2)/((k+1)(k+2))
  e1r = sum(r = 0, n, q[r + 1] * (-1)^r * ('k + r + 1) * ('k + r + 2)) / (('k + 1) * ('k + 2));
  N1 = numerator(e1r);
  emit(Str("m = ", m, ": R_1 = (Q e_1)/e_1 has numerator of bidegree ", [poldegree(N1, 'k), poldegree(N1, 'c)], ", factors ", fmt(factor(N1)),
    "; denominator factors ", fmt(factor(denominator(e1r)))));
  my(d = m * (m - 1) / 2, v = subst(N1, 'k, d)); v = v / 'c^valuation(v, 'c); while (subst(v, 'c, 1) == 0, v = v / ('c - 1));
  emit(Str("m = ", m, ": N_1(d, c) off c(c-1) has c-degree ", poldegree(v, 'c), " (staircase entry: m^2 = ", m^2, ")")));
}
quit
