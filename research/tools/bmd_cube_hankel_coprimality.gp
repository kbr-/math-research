\\ Merging-locus hypothesis (G1): shifted-minor identity and Hankel coprimality (30 Sept 2026).
\\ Tested statements (lambda = 3/2, P = prod_(r<=M)(x - b_r), H_k = det[p_(i+j)]_(0<=i,j<=k),
\\ S_k = det[p_(i+j) (j<k), p_(i+k+1)], p the power sums of b):
\\ (1) det Gamma'_k = gamma_(M,k) S_k modulo H_k, with gamma_(M,k) a nonzero constant: on points of
\\     Z_k = {H_k = 0} (found over F_p) the ratio det Gamma'_k / S_k is the same at every point.
\\     Gamma'_k is the neck window block on rows M-k..M-1 and columns M..M+k-2, M+k.
\\ (2) gcd(H_k, S_k) = gcd(H_k, H_(k-1)) = gcd(H_k, H_(k+1)) = 1 in Q[b] for small M, all
\\     1 <= k <= M-2 (proved in the entry when 2k+2 <= M; the other k are evidence only).
p = 2^61 - 1;
lam = 3/2;
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(j) = binomial(-lam, j);
pw(b, e) = sum(r = 1, #b, b[r]^e);
Hk(b, k) = matdet(matrix(k + 1, k + 1, i, j, pw(b, i + j - 2)));
Sk(b, k) = matdet(matrix(k + 1, k + 1, i, j, pw(b, i + j - 2 + (j == k + 1))));
gammadet(b, k, shifted) = {
  my(M = #b, P = prod(r = 1, M, 'x - b[r]));
  my(G(m, n) = if (m < 0, 0, if (n < M, m == n, beta(n) / beta(m) * polcoeff(lift(Mod('x^n, P)), m, 'x))));
  matdet(matrix(k, k, i, j, my(m = M - k + i - 1, D = M + j - 1 + (shifted && j == k));
    G(m, D + 1) - G(m - 1, D) - G(m, M) * G(M - 1, D)));
}
\\ a point of Z_k over F_p: random b_1..b_(M-1), b_M a root of H_k in the last coordinate
zpoint(M, k) = {
  while (1,
    my(bf = vector(M - 1, r, Mod(random(p), p)), f = Hk(concat(bf, ['t]), k), r = polrootsmod(f * Mod(1, p)));
    if (#r, return(concat(bf, [r[1]]))));
}
main() = {
  setrand(20260930);
  foreach ([4, 5, 6], M,
    for (k = 1, M - 2,
      my(rat = vector(3, q, my(b = zpoint(M, k)); if (Hk(b, k) != 0, error("not on Z_k"));
        gammadet(b, k, 1) / Sk(b, k)));
      emit(Str("M=", M, " k=", k, ": det Gamma'_k / S_k on three points of Z_k: ", rat,
        "; constant ", rat[1] == rat[2] && rat[2] == rat[3], "; nonzero ", rat[1] != 0))));
  \\ Coprimality on random rational lines b = alpha + t beta (exact over Q): a common factor of
  \\ positive degree restricts to a nonconstant common factor unless beta is special, so gcd 1 on a
  \\ line is evidence (and, in the proved range, a consistency check). Every pair G1 needs: H_k with
  \\ S_k and with H_j, j != k, 1 <= j <= M-1; M = 4..8, two lines each.
  foreach ([4, 5, 6, 7, 8], M,
    for (k = 1, M - 2,
      my(bad = List());
      for (ln = 1, 2,
        my(al = vector(M, r, random(201) - 100), be = vector(M, r, random(201) - 100), b = al + 't * be);
        my(h = Hk(b, k), coll = prod(i = 1, M, prod(j = i + 1, M, b[i] - b[j])));
        my(g = gcd(h, Sk(b, k)));
        if (poldegree(g, 't) > 0, listput(bad, [ln, "S", g, poldegree(gcd(g, coll), 't), al, be]));
        for (j = 1, M - 1, if (j != k, g = gcd(h, Hk(b, j));
          if (poldegree(g, 't) > 0, listput(bad, [ln, j, g, poldegree(gcd(g, coll), 't), al, be])))));
      emit(Str("M=", M, " k=", k, " (proved range 2k+2<=M: ", 2 * k + 2 <= M,
        "): lines with a common factor [line, partner, gcd, degree of its collision part, alpha, beta]: ",
        Vec(bad)))));
  \\ twelve further lines at M = 7, k = 5, where one line above shows a common factor; count common
  \\ factors, and those not made of collision factors b_i - b_j (a line can cross a double-pair point,
  \\ a codimension-two locus where H_(M-2), H_(M-1) and S_(M-2) all vanish)
  my(M = 7, k = 5, nall = 0, nnc = 0);
  for (ln = 1, 12,
    my(al = vector(M, r, random(201) - 100), be = vector(M, r, random(201) - 100), b = al + 't * be);
    my(h = Hk(b, k), coll = prod(i = 1, M, prod(j = i + 1, M, b[i] - b[j])));
    my(gs = concat([gcd(h, Sk(b, k))], vector(M - 1, j, if (j == k, 1, gcd(h, Hk(b, j))))));
    foreach (gs, g, if (poldegree(g, 't) > 0, nall++;
      my(g0 = g); while (poldegree(gcd(g0, coll), 't) > 0, g0 = g0 / gcd(g0, coll)); if (poldegree(g0, 't) > 0, nnc++))));
  emit(Str("M=7 k=5: twelve further lines, common factors found: ", nall, ", of them not collision factors: ", nnc));
}
main();
