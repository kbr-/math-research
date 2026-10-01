\\ Direct evaluation of the characteristic-three mark determinant (5 October 2026; cycle bmd-20261005-f).
\\ Statement tested: Delta_(n,2) is not identically zero mod 3 (statement 2's necessary slice).  Delta is the D x D
\\ determinant (D = binom(N,2) + 2) of rows 1, T and the first D coefficients of ((1 + a_i T)(1 + a_j T))^(1/2), labels
\\ a_1 = 0 (dummy) and random a_2..a_N in F_q, q = 3^K.  A nonzero value certifies Delta_(N-1,2) != 0 mod 3.  The record's
\\ finite-field obstructions (thm:cube-finite-field-branch-defect, thm:cube-frobenius-contact) force singularity only when
\\ binom(N,2) >= q; the script asserts q > binom(N,2).  Env NS (list of N), K, TRIALS, SEED.
default(parisizemax, 2000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
{
my(K = eval(getenv("K")), TR = eval(getenv("TRIALS")), g = ffgen(ffinit(3, K, 'a), 'a), one = g^0);
setrand(eval(getenv("SEED")));
foreach(eval(getenv("NS")), N,
  my(D = N * (N - 1) / 2 + 2, bh = vector(D, j, binomial(1/2, j - 1) * Mod(1, 3)), nz = 0, t0 = getwalltime());
  if (3^K <= N * (N - 1) / 2, error("q too small"));
  for (trial = 1, TR,
    my(lab = vector(N, i, if (i == 1, 0 * one, random(g))), M = matrix(D, D), row = 2);
    if (#Set(lab) < N, next);
    M[1, 1] = one; M[2, 2] = one;
    for (i = 1, N, for (j = i + 1, N, row++;
      for (kk = 1, D, M[row, kk] = one * sum(u = 0, kk - 1, lift(bh[u + 1] * bh[kk - u]) * lab[i]^u * lab[j]^(kk - 1 - u)))));
    if (matdet(M) != 0, nz++));
  emit(Str("N = ", N, " (n = ", N - 1, "), D = ", D, ", q = 3^", K, ": nonzero Delta in ", nz, " of ", TR, " random label sets (", getwalltime() - t0, " ms)")));
}
quit;
