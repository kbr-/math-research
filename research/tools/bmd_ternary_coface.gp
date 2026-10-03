\\ Co-face of the characteristic-three degree-two determinant (cycle bmd-20261009-ab, 9 October 2026).
\\ Over F_3, w_j = (1 + a_j T)^(1/2) = sum_m beta(m) (a_j T)^m (Lucas). As a_n -> 0, the lowest a_n-term of
\\ Delta_n is +- beta(1)^(n-1) beta(2) a_n^(n+1) Delta'_{n-1}, where Delta'_m is the determinant of the Taylor
\\ coefficients 0..D-1 (D = 2m + 3 + binom(m,2)) of the confluent space {1, T, T^2, w_j, T w_j, w_i w_j} on m labels.
\\ (a) check of the co-face formula: the lowest a_n-order and its coefficient, exactly in F_3[a_n] at random
\\     a_1..a_{n-1} in F_(3^12), n = 2..6;
\\ (b) Delta'_m != 0 over F_3, by evaluation at random labels in F_(3^20), m = 1..20 (three tries before reporting zero).
OUT = "research/results/bmd-20261009-ab/coface.txt";
beta(m) = { if (m < 0, return(0)); my(d0 = m % 3, t = m \ 3); while(t, if(t % 3 == 2, return(0)); t \= 3); binomial(2, d0) };
wser(a, D) = sum(m = 0, D - 1, beta(m) * a^m * 'T^m);
coef(P, D) = vector(D, k, polcoef(P, k - 1, 'T));
Delta(as, D, extra) = {
  \\ rows: 1, T, (extra T-powers 2..extra), w_j, (T w_j if extra >= 2), w_i w_j
  my(n = #as, W = vector(n, j, wser(as[j], D)), rows = List());
  for (q = 0, max(1, extra), listput(rows, coef('T^q, D)));
  for (j = 1, n, listput(rows, coef(W[j], D)); if (extra >= 2, listput(rows, coef('T * W[j], D))));
  for (i = 1, n, for (j = i + 1, n, listput(rows, coef(W[i] * W[j], D))));
  if (#rows != D, error("row count ", #rows, " != ", D));
  matdet(Mat(Vecrev(Vec(rows))~)~);
};
default(parisizemax, 2 * 10^9);
g = ffgen(3^20, 'g);
h = ffgen(3^12, 'h);
{
  for (n = 2, 6, my(D = 2 + n + n * (n - 1) / 2, as = vector(n - 1, j, random(h)), x = Mod(1, 3) * 'x);
    my(P = Delta(concat(as, [x]), D, 0));
    my(v = valuation(P, 'x), c = polcoef(P, v, 'x));
    my(Dp = 2 * (n - 1) + 3 + (n - 1) * (n - 2) / 2, ref = Delta(as, Dp, 2) * (2)^(n - 1));
    write(OUT, "(a) n=", n, ": lowest a_n-order ", v, " (predicted ", n + 1, "); coefficient / (beta(1)^(n-1) beta(2) Delta'_{n-1}) = ", if(ref == 0, "ref zero", c / ref)));
  my(good = List(), bad = List());
  for (m = 1, 20, my(D = 2 * m + 3 + m * (m - 1) / 2, v = 0);
    for (t = 1, 3, v = Delta(vector(m, j, random(g)), D, 2); if (v != 0, break));
    if (v != 0, listput(good, m), listput(bad, m)));
  write(OUT, "(b) Delta'_m nonzero (certified by a value) for m = ", Vec(good), "; zero at three random points for m = ", Vec(bad));
}
