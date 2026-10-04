\\ MacMahon lead (cycle keg, 9 October 2026): the face minor B_n of lem:cube-ternary-one-root-face equals
\\ PP(n, t0, 1/2 - t0), t0 = binom(n,2) + 2 (check recorded for n <= 6 in the ternary faces review), where MacMahon's
\\ box formula, continued polynomially in the third side c, is PP(a,b,c) = prod_{i<=a, j<=b} (i+j+c-1)/(i+j-1).
\\ Question: is v_3(B_n) > 0 for every n >= 5 (so every consecutive face or co-face degeneration dies), and what is it?
\\ Prints n, v_3(B_n) for n = 1..N (N from env, default 80), and a direct cross-check of the product formula against
\\ the Toeplitz determinant det[binom(1/2, t0 + i - j)] (rows/columns 1..n) for n <= 8.  This consecutive minor is
\\ the face minor B_n only for n <= 6; for n >= 7 the mod-3 face uses the gapped column set E_n (ternary MacMahon entry).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
PP(a, b, c) = prod(i = 1, a, prod(j = 1, b, (i + j + c - 1) / (i + j - 1)));
B(n) = my(t0 = binomial(n, 2) + 2); PP(n, t0, 1/2 - t0);
\\ rows k in top_n = {t0, .., t0+n-1}, consecutive columns e = 0..n-1 (the characteristic-zero extreme set)
Btoep(n) = my(t0 = binomial(n, 2) + 2); matdet(matrix(n, n, i, j, binomial(1/2, t0 + i - j)));
{
  my(N = if(getenv("N") == 0 || getenv("N") == "", 80, eval(getenv("N"))));
  for(n = 1, 8, my(a = B(n), b = Btoep(n)); emit(Str("check n=", n, " PP/Toeplitz ratio: ", a / b)));
  my(v = vector(N, n, valuation(B(n), 3)));
  emit(Str("v3(B_n), n=1..", N, ": ", v));
  emit(Str("n >= 5 with v3 = 0: ", select(n -> v[n] == 0 && n >= 5, vector(N, n, n))));
}
quit;
