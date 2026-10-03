\\ Two-root face of the characteristic-three degree-two determinant (cycle bmd-20261009-aa, 9 October 2026).
\\ beta(m) = [x^m](1+x)^(1/2) mod 3 (Lucas); A = {beta != 0}; E_{n-1} = the n-1 smallest elements of A.
\\ G_n(a_1, a_2) = det over columns k in {binom(n-1,2)+2, ..., binom(n+1,2)+1} (2n-1 columns) of the rows
\\   beta(k-e) beta(e) a_1^(k-e) (e in E_{n-1}), beta(k-e) beta(e) a_2^(k-e) (e in E_{n-1}),
\\   sum_m beta(m) beta(k-m) a_1^m a_2^(k-m).
\\ Tested statement (two-root face step): G_n is not identically zero over F_3. Evaluated at a_2 = 1 and a_1 a random
\\ element of F_(3^20) (a nonzero value certifies G_n != 0); a zero value is retested at two more points.
\\ Also B_n (the one-root minor) for comparison.
OUT = "research/results/bmd-20261009-aa/two-root-face.txt";
beta(m) = { if (m < 0, return(0)); my(d0 = m % 3, t = m \ 3); while(t, if(t % 3 == 2, return(0)); t \= 3); binomial(2, d0) };
En(n) = { my(L = List(), m = 0); while(#L < n, if(beta(m), listput(L, m)); m++); Vec(L) };
g = ffgen(3^20, 'g);
Gval(n, x, y) = {
  my(E = En(n - 1), k0 = (n - 1) * (n - 2) / 2 + 2, S = 2 * n - 1, Mx = matrix(S, S));
  for (c = 1, S, my(k = k0 + c - 1);
    for (r = 1, n - 1, my(e = E[r]); Mx[r, c] = beta(k - e) * beta(e) * x^(k - e); Mx[n - 1 + r, c] = beta(k - e) * beta(e) * y^(k - e));
    Mx[S, c] = sum(m = 0, k, beta(m) * beta(k - m) * x^m * y^(k - m)));
  matdet(Mx);
};
{
  my(good = List(), bad = List());
  for (n = 2, 40, my(v = Gval(n, random(g), g^0));
    if (v == 0, v = Gval(n, random(g), g^0); if (v == 0, v = Gval(n, random(g), g^0)));
    if (v != 0, listput(good, n), listput(bad, n)));
  write(OUT, "two-root minor G_n nonzero over F_3 (certified by a nonzero value) for n = ", Vec(good));
  write(OUT, "G_n zero at three random points for n = ", Vec(bad));
  \\ exact: G_n as a polynomial in a_1 over F_3 (a_2 = 1, homogeneity), n = 2..12
  my(ex = vector(11, i, my(n = i + 1, P = Gval(n, Mod(1, 3) * 'x, Mod(1, 3))); [n, P == 0, if(P == 0, -1, poldegree(P))]));
  write(OUT, "exact over F_3[a_1] (a_2 = 1): [n, G_n identically zero, degree] = ", ex);
}
