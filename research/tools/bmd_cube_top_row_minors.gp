\\ Top-row block minors with arbitrary columns (29 September 2026; cycle bmd-20260929-w).
\\ Tested statement (lem:cube-top-row-block-minors): for 1 <= k <= M-1, rows M-k..M-1 and columns
\\ S = {D_1 < ... < D_k}, D_j >= M, of the neck block matrix Gamma,
\\ det Gamma[R,S] = (-1)^(k(k-1)/2) (prod beta_D / prod beta_m) (lam-1)^k (M-k-1)!/(M-1)! / M
\\                  * det[ sum_r b_r^s f_j(b_r) ]_(0<=s<=k, j=-1..k), f_(-1) = 1, f_D = quo(int_0 quo(x^D,P) P, P).
\\ Checks it exactly at random rational roots for M = 2..6, all k <= M-1 and ten random column sets
\\ in [M, M+7] per (M,k), at lam = 3/2 and 1/3.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
gcol(P, M, lam, m, D) = {
  my(be = n -> binomial(-lam, n), G = (mm, n) -> if (mm < 0, 0, be(n) / be(mm) * polcoef(lift(Mod(x^n, P)), mm, x)));
  G(m, D + 1) - G(m - 1, D) - G(m, M) * G(M - 1, D);
}
main() = {
  setrand(99);
  my(cnt = 0, ok = 1);
  foreach ([3/2, 1/3], lam, for (M = 2, 6, for (k = 1, M - 1, for (rep = 1, 10,
    my(b = vector(M, i, (random(2001) - 1000) / (random(97) + 1)), P = prod(i = 1, M, x - b[i]), be = n -> binomial(-lam, n));
    my(S = vecsort(vecextract([M .. M + 7], numtoperm(8, random(8!)))[1..k]));
    my(lhs = matdet(matrix(k, k, i, j, gcol(P, M, lam, M - k + i - 1, S[j]))));
    my(f = concat([1], vector(k, j, (intformal((x^S[j] \ P) * P)) \ P)));
    my(tr = matrix(k + 1, k + 1, s, j, sum(r = 1, M, b[r]^(s - 1) * subst(f[j], x, b[r]))));
    my(c = (-1)^(k * (k - 1) / 2) * prod(j = 1, k, be(S[j])) / prod(m = M - k, M - 1, be(m)) * (lam - 1)^k * (M - k - 1)! / (M - 1)! / M);
    cnt++; if (lhs != c * matdet(tr), ok = 0; emit(Str("FAIL lam=", lam, " M=", M, " k=", k, " S=", S)))))));
  emit(Str("checked ", cnt, " (lam, M, k, S) cases; all hold: ", ok));
}
main();
