\\ Falsification test of the goal-level route review of cycle keh (9 October 2026): part (b) of
\\ research/tools/bmd_ternary_coface.gp (cycle ab) at the next sizes m = 21..24, i.e. n = m + 1 = 22..25.
\\ Statement tested: Delta'_m != 0 over F_3 (check:cube-ternary-confluent-nonvanishing, recorded for m <= 20), which by
\\ lem:cube-ternary-coface gives Delta_{n,2} != 0 mod 3 for n = m + 1.  Delta'_m is the determinant of the Taylor
\\ coefficients 0..D-1, D = 2m + 3 + binom(m,2), of {1, T, T^2, w_j, T w_j, w_i w_j}, w_j = (1 + a_j T)^(1/2) over F_3.
\\ A nonzero value at random labels in F_(3^20) certifies nonvanishing; three zero tries are reported as a candidate zero.
\\ Each size is printed (with its time) as soon as it is done.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(m) = { if (m < 0, return(0)); my(d0 = m % 3, t = m \ 3); while(t, if(t % 3 == 2, return(0)); t \= 3); binomial(2, d0) };
wser(a, D) = sum(m = 0, D - 1, beta(m) * a^m * 'T^m);
coef(P, D) = vector(D, k, polcoef(P, k - 1, 'T));
Delta(as, D) = {
  my(n = #as, W = vector(n, j, wser(as[j], D)), rows = List());
  for (q = 0, 2, listput(rows, coef('T^q, D)));
  for (j = 1, n, listput(rows, coef(W[j], D)); listput(rows, coef('T * W[j], D)));
  for (i = 1, n, for (j = i + 1, n, listput(rows, coef(W[i] * W[j], D))));
  if (#rows != D, error("row count ", #rows, " != ", D));
  matdet(matrix(D, D, r, c, rows[r][c]));
};
default(parisizemax, 2 * 10^9);
g = ffgen(3^20, 'g);
setrand(20261009);
{
  for (m = 21, 24, my(D = 2 * m + 3 + m * (m - 1) / 2, v = 0, t0 = getabstime(), tries = 0);
    for (t = 1, 3, tries = t; v = Delta(vector(m, j, random(g)), D); if (v != 0, break));
    emit(Str("m=", m, " (n=", m + 1, ") D=", D, ": ", if(v != 0, "nonzero", "zero at three random points"), " after ", tries, " tries, ", (getabstime() - t0) \ 1000, " s")));
}
quit;
