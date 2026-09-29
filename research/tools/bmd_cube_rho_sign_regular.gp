\\ Sign regularity of the factor matrices of the neck block matrix (29 September 2026; cycle bmd-20260929-w).
\\ Tested statement: at a positive point b (distinct roots of P), the remainder-integral matrix
\\ Rho[m,t] = [x^m] rem(int_0^x s^t P(s) ds, P) (0 <= m <= M-1, 0 <= t <= 5) and the quotient-integral matrix
\\ Q[u,t] = [x^u] quo(int_0^x s^t P(s) ds, P) (0 <= u <= 5, 0 <= t <= 4) are sign-regular (Karlin): at that point
\\ all nonzero minors of one order share a sign; also after the checkerboard change (-1)^(sum R + sum S).
\\ For each of six random positive rational points and each order, records whether both signs occur AT THAT
\\ POINT, raw and with the checkerboard; one such point and order refutes sign regularity of that matrix.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
rho(P, M) = matrix(M, 6, r, t, polcoef(lift(Mod(intformal(x^(t - 1) * P), P)), r - 1, x));
quo(P, M) = matrix(6, 5, u, t, polcoef(intformal(x^(t - 1) * P) \ P, u - 1, x));
\\ for one matrix A: vector over orders k of [both signs raw?, both signs checkerboard?]
mixed(A) = {
  my(n = #A[, 1], m = #A, K = min(n, m), res = vector(K));
  for (k = 1, K, my(s1 = Set(), s2 = Set());
    forsubset([n, k], R, forsubset([m, k], S,
      my(d = sign(matdet(matrix(k, k, i, j, A[R[i], S[j]]))));
      if (d, s1 = setunion(s1, [d]); s2 = setunion(s2, [d * (-1)^(vecsum(Vec(R)) + vecsum(Vec(S)))]))));
    res[k] = [#s1 > 1, #s2 > 1]);
  res;
}
main() = {
  setrand(777);
  for (M = 3, 4, for (pt = 1, 6,
    my(b = vector(M, i, (random(1000) + 1) / (random(50) + 1)), P = prod(i = 1, M, x - b[i]));
    emit(Str("M=", M, " point ", pt, ": per order [both signs raw, both signs checkerboard]: Rho ", mixed(rho(P, M)), "; Q ", mixed(quo(P, M))))));
}
main();
