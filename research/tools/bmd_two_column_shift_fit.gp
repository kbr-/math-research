\\ Jacobi-Trudi lead entry four (cycle kev, 9 October 2026): the Schur-Hankel expansion of the two-column raise.
\\ M = 4, p = 2 (k = 2, N = 6): the least coefficient tau_11 (x^(A+2) eps^B, divided by Vand^2) of
\\ L_11 = {-2,-1} u {0..3} u {5, 6} and tau_2 of L_2 = {-2,-1} u {0..4} u {7}, at 12 random rational clusters, fitted
\\ exactly to the degree-two Schur-Hankel basis {H_(1,1), H_(2), e1 H_(1), e1^2 H_0, e2 H_0}
\\ (H_mu = sum_(|S|=3) Vand(y_S)^2 s_mu(y_S)).  Reports the fitted coefficients and the residual rank (consistency).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2 * 10^9);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
coefat(ys, L, A, B) = {
  my(M = #ys, G = matrix(2*M, 2*M));
  for (s = 1, M, for (u = 1, 2*M, my(t = L[u]);
    G[s, u] = if (t >= 0, cc(t) * ('x * ys[s])^t, 0);
    G[M + s, u] = sum(r = max(1, -t), B, cc(r) * cc(t + r) * 'eps^r * ('x * ys[s])^(t + r))));
  polcoef(polcoef(matdet(G), B, 'eps), A, 'x);
}
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
e1(Z) = vecsum(Z);
e2(Z) = sum(i = 1, #Z, sum(j = i + 1, #Z, Z[i] * Z[j]));
h2(Z) = sum(i = 1, #Z, sum(j = i, #Z, Z[i] * Z[j]));
HS(Y, k, f) = { my(s = 0); forsubset([#Y, k + 1], S, my(Z = vector(k + 1, i, Y[S[i]])); s += vand(Z)^2 * f(Z)); s; }
{
  setrand(20261009);
  my(M = 4, p = 2, k = 2, N = 6, A = 2*M^2 - 2*M*p + p^2 - p, B = p^2 - p + M, neg = [-2, -1], rows = List(), t11 = List(), t2 = List());
  for (r = 1, 12, my(Y = vector(M, i, (random(61) - 30) / (random(4) + 1)));
    my(V2 = vand(Y)^2, H0 = HS(Y, k, Z -> 1), H1 = HS(Y, k, e1), H2 = HS(Y, k, h2), H11 = HS(Y, k, e2), E1 = e1(Y), E2 = e2(Y));
    listput(rows, [H11, H2, E1 * H1, E1^2 * H0, E2 * H0]);
    listput(t11, coefat(Y, concat(concat(neg, [0 .. 3]), [5, 6]), A + 2, B) / V2);
    listput(t2, coefat(Y, concat(concat(neg, [0 .. 4]), [7]), A + 2, B) / V2));
  my(X = matrix(12, 5, i, j, rows[i][j]));
  emit(Str("rank of the basis on 12 points: ", matrank(X), "; relations among [H_(1,1), H_(2), e1 H_(1), e1^2 H_0, e2 H_0]: ", Vec(matker(X))));
  foreach([[t11, "tau_11 (top two columns raised by 1)"], [t2, "tau_2 (top column raised by 2)"]], T,
    my(v = Col(Vec(T[1])), sol = matinverseimage(X, v));
    emit(Str(T[2], ": in the span: ", #sol > 0, "; one solution ", if(#sol, sol~, "none"))));
}
quit;
