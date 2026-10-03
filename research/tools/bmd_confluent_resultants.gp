\\ Resultant structure of the confluent tie window (cycle bmd-20261009-cm, 9 October 2026).
\\ W^c(c) (lem:cube-confluent-tie-reduction): rows (1+T)^-5/2 T^i (i < 2m), T^n (1+cT)^-3/2 (n < m), (1+T)^-3,
\\ ((1+T)(1+cT))^-3/2, T (1+T)^-5/2 (1+cT)^-3/2, on the columns T^d..T^(d+3m+4), d = C(m, 2). Its square minors
\\ D_j(c) on columns d+j..d+j+3m+2 (j = 0, 1, 2), with the factors c and c - 1 removed. Question: do the pairwise
\\ resultants Res(D_0, D_1), Res(D_1, D_2), Res(D_0, D_2) factor into small primes only (a closed product formula, as
\\ for Gegenbauer polynomials), or carry large prime factors? Also gcd(D_0, D_1, D_2) (full rank fails at its roots).
\\ Prints, for m = 2..5: degrees, the gcd degree, and the largest prime factor of each resultant's numerator.
OUT = "research/results/bmd-20261009-cm/confluent-resultants.txt";
default(parisizemax, 4 * 10^9);
coef(f, top) = vector(top + 1, k, polcoef(f, k - 1, 'T));
strip(D) = { while (subst(D, 'c, 0) == 0, D = D / 'c); while (subst(D, 'c, 1) == 0, D = D / ('c - 1)); D; }
bigp(r) = { my(F = factor(numerator(abs(r)))); if (#F~ == 0, 1, F[#F~, 1]); }
{
  for (m = 2, 5,
    my(d = m * (m - 1) / 2, top = d + 3 * m + 4, rows = List());
    my(A = (1 + 'T + O('T^(top + 1)))^(-5/2), C = (1 + 'c * 'T + O('T^(top + 1)))^(-3/2));
    for (i = 0, 2 * m - 1, listput(rows, coef('T^i * A, top)));
    for (n = 0, m - 1, listput(rows, coef('T^n * C, top)));
    listput(rows, coef((1 + 'T + O('T^(top + 1)))^(-3), top));
    listput(rows, coef(A * C * (1 + 'T), top));
    listput(rows, coef('T * A * C, top));
    my(D = vector(3, j, strip(matdet(matrix(#rows, #rows, r, k, rows[r][d + j + k - 1])))));
    my(g = gcd(gcd(D[1], D[2]), D[3]));
    write(OUT, "m = ", m, ": degrees ", apply(poldegree, D), ", gcd degree ", poldegree(g));
    foreach([[1, 2], [2, 3], [1, 3]], pr, my(R = polresultant(D[pr[1]], D[pr[2]]));
      write(OUT, "  Res(D_", pr[1] - 1, ", D_", pr[2] - 1, "): ", if (R == 0, "0", Str("largest prime factor ", bigp(R), ", log10 |R| ", precision(log(abs(R)) / log(10.), 6))))));
}
