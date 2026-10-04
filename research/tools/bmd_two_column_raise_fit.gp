\\ Cauchy-Sato lead, entry three (cycle kff, 9 October 2026). Tested statement: the least coefficient (u^(B_p))
\\ of the cherry coordinate on the two-column raise L_11 = [-p, N-3] u {N-1, N} (lambda = 3/2, x = 1, eps = u,
\\ N = 2M - p, k = M - p) equals Vand^2 times a combination of H_(1,1), p_1 H_(1), p_1^2 Hank_k, p_2 Hank_k with
\\ constant coefficients; the H_(1,1) coefficient is nonzero for k >= 2 and zero for k = 1. Exact: integer
\\ clusters, exact determinants over Q[eps], linear fit over 24 points (a fit with no solution falsifies).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
coord(Y, L, top) = {
  my(M = #Y, G = matrix(2 * M, 2 * M));
  for (s = 1, M, for (u = 1, 2 * M, my(t = L[u]);
    G[s, u] = if (t >= 0, cc(t) * Y[s]^t, 0);
    G[M + s, u] = sum(r = max(1, -t), top, cc(r) * cc(t + r) * 'e^r * Y[s]^(t + r))));
  matdet(G);
}
schur2(Ys, nu) = {
  if (#nu == 0, return(1));
  my(e1 = vecsum(Ys), e2 = sum(i = 1, #Ys, sum(j = i + 1, #Ys, Ys[i] * Ys[j])));
  if (nu == [1], return(e1));
  if (nu == [1, 1], return(e2));
  error("nu");
}
Hnu(Y, k, nu) = { my(s = 0); forsubset([#Y, k + 1], S, my(Ys = vector(k + 1, i, Y[S[i]])); s += vand(Ys)^2 * schur2(Ys, nu)); s; }
pw(Y, n) = sum(i = 1, #Y, Y[i]^n);
{
  setrand(20261009);
  foreach([3, 4, 5], M, for (p = 1, M - 1, my(k = M - p, N = 2 * M - p, B = p^2 - p + M, npts = 24);
    if (N - 3 < 0, next);
    my(L = concat(vector(N - 2 + p, i, -p - 1 + i), [N - 1, N]));
    my(W = vector(2 * M, i, -p - 1 + i), A = matrix(npts, 5));
    for (j = 1, npts,
      my(Y); until (#Set(Y) == M, Y = vector(M, i, random(41) - 20));
      my(P = coord(Y, L, B + 1), Q = coord(Y, W, B + 1), V = vand(Y)^2, c0 = polcoef(Q, B, 'e) / (V * Hnu(Y, k, [])));
      if (valuation(P, 'e) < B, emit("valuation below B"));
      my(H0 = Hnu(Y, k, []), H1 = Hnu(Y, k, [1]), H11 = Hnu(Y, k, [1, 1]), p1 = pw(Y, 1), p2 = pw(Y, 2));
      my(row = [H11, p1 * H1, p1^2 * H0, p2 * H0, -polcoef(P, B, 'e) / V / c0]);
      for (c = 1, 5, A[j, c] = row[c]));
    my(K = matker(A), sol = "none");
    if (#K == 1 && K[5, 1] != 0, sol = (K[, 1] / K[5, 1])[1 .. 4]~);
    if (#K > 1, sol = Str("underdetermined, kernel dim ", #K));
    emit(Str("M=", M, " p=", p, " k=", k, ": [H11, p1 H1, p1^2 Hank, p2 Hank] coefficients / window constant = ", sol))));
  quit;
}
