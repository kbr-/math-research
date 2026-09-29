\\ Discriminant form of the neck blocks (29 September 2026).
\\ Tested statement (notebook entry of cycle bmd-20260929-u): for monic P of degree M with roots b and
\\ 1 <= k <= M-1, the neck-theorem block Gamma_k (rows M-k..M-1, columns M..M+k-1, entries
\\ G_{m,D+1} - G_{m-1,D} - G_{m,M} G_{M-1,D}, G_{m,n} = (beta_n/beta_m) [x^m](x^n mod P), beta_n = binom(-lam,n))
\\ satisfies det Gamma_k = (-1)^(k(k-1)/2) (prod_D beta_D / prod_m beta_m) (lam-1)^k (M-k-1)!/(M+k)! * Hank_k,
\\ Hank_k = det[p_(i+j)(b)]_(0<=i,j<=k), p_n the power sums. Part 1 checks this exactly at one random
\\ rational point per (M,k), M = 2..8, for lam = 3/2, 1/3, 7/5. Part 2 prints the e-valuation of det Gamma_k
\\ for the caterpillar cluster b_i = c_i e^(i-1), M = 2..6, k = 0..M, against 2 binom(k+1,3)
\\ (the least valuation of a squared Vandermonde of k+1 caterpillar roots).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
gam(b, M, k, lam) = {
  my(P = prod(i = 1, M, x - b[i]), be = n -> binomial(-lam, n));
  my(G = (m, n) -> if (m < 0, 0, be(n) / be(m) * polcoef(lift(Mod(x^n, P)), m, x)));
  matdet(matrix(k, k, r, s, my(m = M - k + r - 1, D = M + s - 1); G(m, D + 1) - G(m - 1, D) - G(m, M) * G(M - 1, D)));
}
hank(b, k) = matdet(matrix(k + 1, k + 1, i, j, sum(t = 1, #b, b[t]^(i + j - 2))));
cst(M, k, lam) = {
  my(be = n -> binomial(-lam, n));
  (-1)^(k * (k - 1) / 2) * prod(D = M, M + k - 1, be(D)) / prod(m = M - k, M - 1, be(m)) * (lam - 1)^k * (M - k - 1)! / (M + k)!;
}
main() = {
  setrand(20260929);
  my(ok = 1, cnt = 0);
  foreach ([3/2, 1/3, 7/5], lam,
    for (M = 2, 8, for (k = 1, M - 1,
      my(b = vector(M, i, (random(2001) - 1000) / (random(97) + 1)));
      my(g = gam(b, M, k, lam), h = hank(b, k));
      cnt++; if (h == 0 || g != cst(M, k, lam) * h, ok = 0; emit(Str("FAIL lam=", lam, " M=", M, " k=", k))))));
  emit(Str("Part 1: identity checked at ", cnt, " (lam, M, k) triples; all hold: ", ok));
  for (M = 2, 6,
    my(c = vector(M, i, random(19) + 2), b = vector(M, i, c[i] * e^(i - 1)), vals = vector(M + 1));
    for (k = 0, M, my(g = if (k == 0, 1, gam(b, M, k, 3/2))); vals[k + 1] = if (g == 0, "zero", valuation(g, e)));
    emit(Str("Part 2: M=", M, " c=", c, ": val det Gamma_k (k=0..M) = ", vals, "; 2 binom(k+1,3) = ", vector(M + 1, k, 2 * binomial(k, 3)))));
}
main();
