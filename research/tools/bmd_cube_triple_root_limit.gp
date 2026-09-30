\\ Triple-root flat limits of the pair space (cycle bmd-20260930-zzs).  Pair rows phi(a_i) phi(a_j), phi(a) = (1+aT)^(-3/2).
\\ Claim tested: in the empty-character block of a triple cluster x + u_i, the rows g(u_i,u_j) = (1+u_iX)^(-3/2)(1+u_jX)^(-3/2)
\\ = sum_n P_n(u_i,u_j) X^n have Pluecker coordinates p_I (I = three exponents) divisible by the Vandermonde V(u), with
\\ p_{012} = c V(u), c != 0; hence along every arc u -> 0 the block tends to <1, X, X^2>.
\\ (1) symbolic check of divisibility for all I within exponents 0..6;
\\ (2) exact flat limits (valuation reduction over Q[e]) of the whole pair row space at N = 6, 7 along a generic arc and
\\ along nested arcs (two cluster points closer at rate e^2, e^3), compared with the predicted space
\\ phi_x^2 <1,X,X^2> + sum_z phi_x phi_z <1,X,X^2> + <phi_z phi_z'>, and its contact rank on T^0..T^(R+1).
X; T; e;
P(n, u, v) = polcoef((1 + u*X + O(X^(n+1)))^(-3/2) * (1 + v*X + O(X^(n+1)))^(-3/2), n, X);
{
  my(u = [u1, u2, u3], pr = [[1,2],[1,3],[2,3]], V = (u2-u1)*(u3-u1)*(u3-u2), ok = 1, c);
  forsubset([7, 3], I,
    my(M = matrix(3, 3, k, j, P(I[j] - 1, u[pr[k][1]], u[pr[k][2]])), d = matdet(M));
    if (d != 0 && denominator(d / V) != 1, ok = 0; print("not divisible: I = ", I));
    if (I == Vecsmall([1,2,3]), c = d / V));
  print("(1) all 3x3 Pluecker coordinates on exponents 0..6 divisible by V(u): ", ok, ";  p_012 / V = ", c);
}
P0 = 0;
vred(A, K) = {
  my(n = #A, B = A, it = 0);
  while (1,
    for (k = 1, n, my(v = vecmin(vector(#B[, k], r, if (B[r, k] == 0, K, valuation(B[r, k], e)))));
      if (v >= K, error("column lost to truncation"));
      B[, k] = B[, k] / e^v);
    my(L = subst(B, e, 0), ker = matker(L));
    if (#ker == 0, return(L));
    my(kv = ker[, 1], j = 0);
    for (k = 1, n, if (kv[k] != 0, j = k));
    B[, j] = sum(k = 1, n, kv[k] * B[, k]);
    it++; if (it > 300, error("no convergence")));
}
ph(a) = (1 + a*T + O(T^P0))^(-3/2);
jets(F, L) = matrix(L, #F, r, k, truncate(polcoef(F[k], r - 1, T) + O(e^60)));
{
  foreach ([6, 7], N,
    my(R = N*(N-1)/2, L = R + 8, x = 2/5, z = vector(N - 3, i, [3, -7/4, 5/2, -1/3][i]), Xs, pred = List(), Lp, K = 14);
    P0 = L + 2;
    Xs = T / (1 + x*T + O(T^P0));
    for (n = 0, 2, listput(pred, ph(x)^2 * Xs^n));
    for (i = 1, #z, for (n = 0, 2, listput(pred, ph(x) * ph(z[i]) * Xs^n)));
    for (i = 1, #z, for (j = i + 1, #z, listput(pred, ph(z[i]) * ph(z[j]))));
    Lp = jets(Vec(pred), L);
    print("N = ", N, ": predicted space has rank ", matrank(Lp), " (R = ", R, "), rank on T^0..T^(R+1): ", matrank(Lp[1..R+2, ]));
    foreach ([[e, 3*e], [e, e + e^2], [e, e + e^3], [e^2, e^2 + e^5]], sh,
      my(a = concat([x, x + sh[1], x + sh[2]], z), F = List(), Lim);
      for (i = 1, N, for (j = i + 1, N, listput(F, ph(a[i]) * ph(a[j]))));
      Lim = vred(jets(Vec(F), L), K);
      print("   cluster x, x+", sh[1], ", x+", sh[2], ": limit rank ", matrank(Lim), ", rank with prediction ",
        matrank(matconcat([Lim, Lp])), ", contact rank on T^0..T^(R+1): ", matrank(Lim[1..R+2, ]))));
}
