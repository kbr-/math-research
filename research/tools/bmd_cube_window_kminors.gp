\\ Toeplitz minors behind the neck window valuations.
\\
\\ Setting: K^sigma_(m,d) = beta_m beta_(m-d) sigma^(m-d) (beta_j = binom(-3/2,j), zero for j<0),
\\ rows m, columns d. For a window W_k = {-M+k,...,M-1+k} and M-sets A, A' of nonnegative
\\ integers, kappa(A,A') = det [K^+_(A,W_k) ; K^-_(A',W_k)]. The Cauchy-Binet expansion is
\\ det C[:,W_k] = sum_(A,A') s_A(b) s_A'(b) eps^(sum A + sum A') kappa(A,A').
\\ Question: for each valuation level L = sum A + sum A' from the Hall bound M(M-1)+k^2 up to the
\\ conjectured M(M-1)+k(k+1), which kappa(A,A') are nonzero? (Are the vanishings individual, or
\\ only cancellations in the sum?)  Output: for each (M,k,L) the number of pairs with nonzero kappa.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(j) = if (j < 0, 0, binomial(-3/2, j));
K(sig, m, d) = beta(m) * beta(m - d) * sig^(m - d);
subsetsum(L, M, maxv) = {
  \\ all M-subsets of {0..maxv} with sum L
  my(res = List());
  forsubset([maxv + 1, M], s, my(v = apply(x -> x - 1, Vec(s))); if (vecsum(v) == L, listput(res, v)));
  Vec(res);
}
kappa(A, B, W) = matdet(matrix(2 * #A, #W, r, c, if (r <= #A, K(1, A[r], W[c]), K(-1, B[r - #A], W[c]))));
main() = {
  for (M = 2, 4,
    for (k = 0, M,
      my(W = vector(2 * M, j, -M + k + j - 1), base = M * (M - 1), maxv = M + k + 2);
      for (L = base + k^2, base + k * (k + 1),
        my(tot = 0, nz = 0);
        for (LA = 0, L,
          my(SA = subsetsum(LA, M, maxv), SB = subsetsum(L - LA, M, maxv));
          foreach (SA, A, foreach (SB, B, tot++; if (kappa(A, B, W) != 0, nz++))));
        emit(Str("M=", M, " k=", k, " level L=", L, " (Hall ", base + k^2, ", conjectured ", base + k * (k + 1), "): pairs ", tot, ", nonzero kappa ", nz)))));
}
main();
