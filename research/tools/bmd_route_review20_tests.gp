\\ Goal-level review tests on statement 2 (cycle bmd-20261009-ac, 9 October 2026).
\\ (1) Falsification attempt: the four-step co-face condition. Delta^(4)_m is the Taylor determinant, columns
\\     0..p_4 + 5m + binom(m,2) - 1 with p_4 = 12, of {T^t : t < 12} u {T^q w_j : q in {0,1,2,3,4}} u {w_i w_j}, over F_3,
\\     w_j = (1 + a_j T)^(1/2) (Lucas). Its nonvanishing would give Delta_{m+4,2} != 0 (sketch in the co-face entry).
\\     Evaluated at random labels in F_(3^20), m = 1..6 (m = 1 must vanish: it equals a^* B_5).
\\ (2) Outside lead (MacMahon's box formula): for n <= 6, B_n = det[binom(1/2, t0 + i - j)]_{0<=i,j<n},
\\     t0 = binom(n,2) + 2, should equal PP(n, t0, 1/2 - t0) = prod_{i<=n, j<=t0} (i + j + (1/2 - t0) - 1)/(i + j - 1)
\\     (plane partitions in an n x t0 x c box, extended polynomially in c). Compare values and 3-adic valuations.
OUT = "research/results/bmd-20261009-ac/review-tests.txt";
default(parisizemax, 2 * 10^9);
beta(m) = { if (m < 0, return(0)); my(d0 = m % 3, t = m \ 3); while(t, if(t % 3 == 2, return(0)); t \= 3); binomial(2, d0) };
g = ffgen(3^20, 'g);
D4(m) = {
  my(as = vector(m, j, random(g)), D = 12 + 5 * m + m * (m - 1) / 2, W = vector(m, j, sum(k = 0, D - 1, beta(k) * as[j]^k * 'T^k)), rows = List());
  for (t = 0, 11, listput(rows, vector(D, k, (k - 1 == t) * g^0)));
  for (j = 1, m, for (q = 0, 4, my(P = 'T^q * W[j]); listput(rows, vector(D, k, polcoef(P, k - 1, 'T)))));
  for (i = 1, m, for (j = i + 1, m, my(P = W[i] * W[j]); listput(rows, vector(D, k, polcoef(P, k - 1, 'T)))));
  matdet(matrix(D, D, r, c, rows[r][c]));
};
PP(r, s, c) = prod(i = 1, r, prod(j = 1, s, (i + j + c - 1) / (i + j - 1)));
{
  for (m = 1, 6, my(v = 0); for (t = 1, 3, v = D4(m); if (v != 0, break));
    write(OUT, "(1) m=", m, ": Delta^(4)_m ", if(v != 0, "nonzero (certified)", "zero at three random points")));
  for (n = 1, 6, my(t0 = n * (n - 1) / 2 + 2, B = matdet(matrix(n, n, i, j, binomial(1/2, t0 + i - j))), M = PP(n, t0, 1/2 - t0));
    write(OUT, "(2) n=", n, ": B_n / PP = ", B / M, ", v_3(B_n) = ", valuation(B, 3), ", v_3(PP) = ", valuation(M, 3)));
}
