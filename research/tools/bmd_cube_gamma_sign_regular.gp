\\ Sign regularity of the neck block matrix at positive roots (29 September 2026; route review test).
\\ Tested statement (total-positivity lead of the route review): for positive distinct cluster roots b,
\\ every minor of the matrix Gam[m,D] = G_{m,D+1} - G_{m-1,D} - G_{m,M} G_{M-1,D} (rows 0 <= m <= M-1,
\\ columns M <= D <= M+5, lambda = 3/2) has a sign depending only on its row and column sets.
\\ If so, the multiscale leading coefficients of all block minors cannot cancel for positive c.
\\ Samples six random positive rational points per M = 3, 4 and compares signs of all minors.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(n) = binomial(-3/2, n);
gm(b, M, W) = {
  my(P = prod(i = 1, M, x - b[i]), G = (m, n) -> if (m < 0, 0, beta(n) / beta(m) * polcoef(lift(Mod(x^n, P)), m, x)));
  matrix(M, W, r, s, my(m = r - 1, D = M + s - 1); G(m, D + 1) - G(m - 1, D) - G(m, M) * G(M - 1, D));
}
main() = {
  setrand(4242);
  my(W = 6);
  for (M = 3, 4,
    my(pts = vector(6, t, vector(M, i, (random(1000) + 1) / (random(50) + 1))), mats = vector(6, t, gm(pts[t], M, W)));
    my(tot = 0, bad = 0, zero = 0);
    forsubset(M, R, if (#R == 0, next);
      forsubset([W, #R], S,
        my(sg = vector(6, t, sign(matdet(matrix(#R, #R, i, j, mats[t][R[i], S[j]])))));
        tot++;
        if (vecmin(sg) == 0 && vecmax(sg) == 0, zero++, if (#Set(sg) > 1, bad++))));
    emit(Str("M=", M, ": minors ", tot, ", identically zero at all points ", zero, ", sign changes across points ", bad)));
}
main();
