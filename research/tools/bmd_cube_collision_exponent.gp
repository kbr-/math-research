\\ The collision exponent of the Wronskian discriminant from the near-group scales (30 Sept 2026).
\\ Statement: near a generic point of {a_1 = a_2}, with half-separation eps and M = N-2, the roots
\\ of W converging to the collision point are r = binom(M,2) face points at distance ~ eps (distinct
\\ limits) and M-1 neck rings, ring j of 2M points at distance ~ eps^(1-j/M) (distinct directions).
\\ The order of prod (r_i - r_j)^2 over the near group is
\\   e(M) = 2 binom(r,2) + sum_{j=1}^{M-1} (1 - j/M) [4Mr + 2M(2M-1) + 8M^2 (j-1)].
\\ The script gives the closed form, prints the near-group size binom(M,2) + 2M(M-1) (equal to
\\ T_sep - T_conf by the count identity), and compares with the multiplicities measured by the line
\\ certificates
\\ (research/results/bmd-20260929-a/wronskian-disc-N{5,6,7}.json: 96, 386, 1070), which are upper
\\ bounds for the collision exponent.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
e(M) = my(r = binomial(M, 2)); 2 * binomial(r, 2) + sum(j = 1, M - 1, (1 - j / M) * (4 * M * r + 2 * M * (2 * M - 1) + 8 * M^2 * (j - 1)));
main() = {
  \\ closed form by interpolation in M (e is a polynomial of degree 4 in M), checked at more points
  my(P = polinterpolate(vector(6, i, i + 1), vector(6, i, e(i + 1)), 'M));
  my(ok = prod(M = 2, 30, subst(P, 'M, M) == e(M)));
  emit(Str("e(M) = ", factor(P), " = ", P, "; checked for M = 2..30: ", ok));
  my(meas = [96, 386, 1070]);
  for (N = 5, 7, my(M = N - 2); emit(Str("N=", N, ": e = ", e(M), ", measured upper bound ", meas[N - 4],
    ", near-group size ", binomial(M, 2) + 2 * M * (M - 1))));
  emit(Str("N = 8..12: ", vector(5, i, e(i + 5))));
}
main();
