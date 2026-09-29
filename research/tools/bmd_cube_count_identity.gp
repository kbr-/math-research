\\ Count identity of the cluster degeneration for all N (review test, 29 September 2026).
\\ From the local exponent formulas (minimal branch and infinity multiplicities; entries of 29 September):
\\  separated total non-branch weight  Tsep(N) = (N-2) E - N ms,  ms = binom(N-1,2) + binom(R-N+1,2),
\\  confluent total non-branch weight  Tconf(N) = degP - md - (N-2) ms,
\\     degP = (N-3) E + N - 2,  md = Sd + 4N - 5,
\\     Sd = -5(N-2) + binom(2N-4,2) - 3 + binom(binom(N-2,2),2),
\\ with R = binom(N,2), E = binom(R,2). The degeneration picture (binary face r = binom(N-2,2) points,
\\ neck 2M(M-1) points with M = N-2, bubble = confluent space of N roots) predicts
\\  Tsep(N) = binom(N-2,2) + 2(N-2)(N-3) + Tconf(N)  for every N >= 4.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
f(N) = {
  my(R = binomial(N, 2), E = binomial(R, 2), ms = binomial(N - 1, 2) + binomial(R - N + 1, 2));
  my(Tsep = (N - 2) * E - N * ms);
  my(Sd = -5 * (N - 2) + binomial(2 * N - 4, 2) - 3 + binomial(binomial(N - 2, 2), 2), md = Sd + 4 * N - 5, degP = (N - 3) * E + N - 2);
  my(Tconf = degP - md - (N - 2) * ms);
  [Tsep, Tconf, binomial(N - 2, 2) + 2 * (N - 2) * (N - 3) + Tconf];
}
main() = {
  my(bad = []);
  for (N = 4, 60, my(v = f(N)); if (v[1] != v[3], bad = concat(bad, [N])));
  emit(Str("N=5,6,7: ", [f(5), f(6), f(7)], "; identity fails for N in 4..60: ", bad));
  \\ symbolic check: treat N as a variable (all quantities are polynomials in N)
  my(n = 'n, R = n*(n-1)/2, E = R*(R-1)/2, ms = (n-1)*(n-2)/2 + (R-n+1)*(R-n)/2);
  my(Tsep = (n - 2) * E - n * ms, q = (n-2)*(n-3)/2);
  my(Sd = -5*(n-2) + (2*n-4)*(2*n-5)/2 - 3 + q*(q-1)/2, md = Sd + 4*n - 5, degP = (n-3)*E + n - 2);
  my(Tconf = degP - md - (n - 2) * ms);
  emit(Str("symbolic Tsep - (binom(n-2,2) + 2(n-2)(n-3) + Tconf) = ", Tsep - (q + 2*(n-2)*(n-3) + Tconf)));
  emit(Str("symbolic Tsep = ", factor(Tsep), " ; Tconf = ", factor(Tconf)));
}
main();
