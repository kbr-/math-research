\\ Cauchy-Sato lead, entry two (cycle kfe, 9 October 2026). Tested statement: for the cherry window
\\ Lambda_p = [-p, 2M-1-p] (lambda = 3/2, x = 1), the coefficient of eps^(B_p + i) of the cross coordinate
\\ P_Lambda equals Vand^2 times an element of the span of {p_mu H_nu : |mu| + |nu| = i}, where p_mu are power
\\ sums of all M roots and H_nu = sum_{|S| = k+1} Vand(y_S)^2 s_nu(y_S), k = M - p (i = 1: p_1 H_(), H_(1);
\\ i = 2: p_1^2 H_(), p_2 H_(), p_1 H_(1), H_(2), H_(1,1)). Exact: integer points y, exact determinants over
\\ Q[eps], linear fit over 24 points; the residual rank decides membership (a fit with no
\\ solution falsifies the statement at that (M, p, i)). Reports the fitted coefficients, normalized.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
\\ exact window coordinate truncated at eps^top, as a polynomial in e
wincoef(Y, p, top) = {
  my(M = #Y, L = vector(2 * M, i, -p - 1 + i), G = matrix(2 * M, 2 * M));
  for (s = 1, M, for (u = 1, 2 * M, my(t = L[u]);
    G[s, u] = if (t >= 0, cc(t) * Y[s]^t, 0);
    G[M + s, u] = sum(r = max(1, -t), top, cc(r) * cc(t + r) * 'e^r * Y[s]^(t + r))));
  matdet(G);
}
schur2(Ys, nu) = {
  if (#nu == 0, return(1));
  my(e1 = vecsum(Ys), e2 = sum(i = 1, #Ys, sum(j = i + 1, #Ys, Ys[i] * Ys[j])));
  if (nu == [1], return(e1));
  if (nu == [2], return(e1^2 - e2));
  if (nu == [1, 1], return(e2));
  error("nu");
}
Hnu(Y, k, nu) = {
  my(M = #Y, s = 0);
  forsubset([M, k + 1], S, my(Ys = vector(k + 1, i, Y[S[i]])); s += vand(Ys)^2 * schur2(Ys, nu));
  s;
}
pw(Y, n) = sum(i = 1, #Y, Y[i]^n);
basis(Y, k, i) = {
  if (i == 0, return([Hnu(Y, k, [])]));
  if (i == 1, return([pw(Y, 1) * Hnu(Y, k, []), Hnu(Y, k, [1])]));
  [pw(Y, 1)^2 * Hnu(Y, k, []), pw(Y, 2) * Hnu(Y, k, []), pw(Y, 1) * Hnu(Y, k, [1]), Hnu(Y, k, [2]), Hnu(Y, k, [1, 1])];
}
{
  setrand(20261009);
  foreach([3, 4, 5], M, for (p = 1, M - 1, my(k = M - p, B = p^2 - p + M, npts = 24, rows = List(), ok = 1);
    my(data = vector(npts));
    for (j = 1, npts,
      my(Y);
      until (#Set(Y) == M, Y = vector(M, i, random(41) - 20));
      my(P = wincoef(Y, p, B + 3), V = vand(Y)^2);
      if (valuation(P, 'e) < B, ok = 0);
      data[j] = [Y, vector(3, i, polcoef(P, B + i - 1, 'e) / V)]);
    if (!ok, emit(Str("M=", M, " p=", p, ": valuation below B_p")));
    for (i = 0, 2,
      my(A = matrix(npts, 1 + #basis(data[1][1], k, i)));
      for (j = 1, npts, my(b = basis(data[j][1], k, i)); for (c = 1, #b, A[j, c] = b[c]); A[j, #b + 1] = -data[j][2][i + 1]);
      my(K = matker(A), sol = "none");
      if (#K == 1 && K[#K[, 1], 1] != 0, my(v = K[, 1] / K[#K[, 1], 1]); sol = v[1 .. #v - 1]~);
      if (#K > 1, sol = Str("underdetermined, kernel dim ", #K));
      emit(Str("M=", M, " p=", p, " k=", k, " B=", B, " i=", i, ": coefficients ", sol)))));
  quit;
}
