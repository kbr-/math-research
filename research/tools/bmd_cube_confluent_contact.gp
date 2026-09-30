\\ Contact at the mark of the limit spaces on the pair-collision and double-pair strata (cycle bmd-20260930-zzr).
\\ Setting of the contact criterion: V_a = <1, z, w_ij>, w_ij = sqrt((z-a_i)(z-a_j)), mark z = infinity, u = 1/z,
\\ R = binom(N,2), M = R + 4, S = ker J_M = {s in V : s = O(u^(M-1))}; the contact locus is K = {S != 0}.
\\ Limits (valuation reduction of V along a_{1,2} = c +- eps, and a_{3,4} = d +- lambda*eps for the double pair):
\\   one double c:   <1, z, 1/(z-c), w_ck, d_c w_ck (k >= 3), w_kl (3 <= k < l)>;
\\   double pair c, d: <1, z, 1/(z-c), 1/(z-d), w_cd, d_c w_cd, d_d w_cd, d_c d_d w_cd,
\\                      w_ck, d_c w_ck, w_dk, d_d w_dk (k >= 5), w_kl (5 <= k < l)>, independent of lambda.
\\ Tested: each limit has dimension R + 2 (so it is the limit), and dim S at generic rational points; control: V_a.
\\ A limit with S != 0 at generic points has contact on the whole stratum.
u;
P0 = 0;
sq(a, b) = sqrt((1 - a*u) * (1 - b*u) + O(u^P0));
w(a, b) = sq(a, b) / u;                                  \\ w_ab in u
dw(a, b) = -(1/2) * sqrt((1 - b*u) / (1 - a*u) + O(u^P0)); \\ d/da of w_ab
ddw(a, b) = (1/4) * u / sq(a, b);                        \\ d^2/(da db) of w_ab
pole(c) = u / (1 - c*u + O(u^P0));                       \\ 1/(z - c)
contact(F, M) = {
  my(A = matrix(M, #F, e, k, polcoef(F[k], e - 2, u)), B = matrix(M + 6, #F, e, k, polcoef(F[k], e - 2, u)));
  [matrank(B), #F - matrank(A)];                          \\ [rank of the space, dim S]
}
generic(a) = {
  my(N = #a, F = List([1 + O(u^P0), u^-1 + O(u^P0)]));
  for (i = 1, N, for (j = i + 1, N, listput(F, w(a[i], a[j]))));
  Vec(F);
}
onedouble(c, b) = {
  my(n = #b, F = List([1 + O(u^P0), u^-1 + O(u^P0), pole(c)]));
  for (k = 1, n, listput(F, w(c, b[k])); listput(F, dw(c, b[k])));
  for (k = 1, n, for (l = k + 1, n, listput(F, w(b[k], b[l]))));
  Vec(F);
}
doublepair(c, d, b) = {
  my(n = #b, F = List([1 + O(u^P0), u^-1 + O(u^P0), pole(c), pole(d), w(c, d), dw(c, d), dw(d, c), ddw(c, d)]));
  for (k = 1, n, listput(F, w(c, b[k])); listput(F, dw(c, b[k])); listput(F, w(d, b[k])); listput(F, dw(d, b[k])));
  for (k = 1, n, for (l = k + 1, n, listput(F, w(b[k], b[l]))));
  Vec(F);
}
{
  setrand(20260930);
  for (N = 7, 9,
    my(R = N*(N-1)/2, M = R + 4, r, a);
    P0 = M + 10;
    for (trial = 1, 3,
      a = vector(N, i, (random(2000) - 1000) / (random(97) + 3));
      r = contact(generic(a), M);
      print("N = ", N, " trial ", trial, ": generic V: dim = ", r[1], " (R+2 = ", R + 2, "), dim S = ", r[2]);
      r = contact(onedouble(a[1], a[3..N]), M);
      print("   one double: dim = ", r[1], ", dim S = ", r[2]);
      r = contact(doublepair(a[1], a[3], a[5..N]), M);
      print("   double pair: dim = ", r[1], ", dim S = ", r[2])));
}

\\ Part 2.  The naive double-pair span above has dimension R + 1, so the true limit needs one more function.
\\ Compute the Grassmannian limit directly: valuation reduction over Q[eps] of the jets of V_a along
\\ a_{1,2} = c +- eps, a_{3,4} = d +- lambda*eps (others fixed), then dim S of the limit, for several lambda.
e;
vred(A, K) = {
  \\ columns of A: jet vectors with entries in Q[e] (truncated below e^K); returns the limit (entries at e = 0)
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
    it++; if (it > 200, error("no convergence")));
}
limitspace(a, M, K) = {
  \\ a: vector of branch points in Q[e]; jets in u of orders -1 .. M+5
  my(N = #a, F = List([1 + O(u^P0), u^-1 + O(u^P0)]));
  for (i = 1, N, for (j = i + 1, N, listput(F, sqrt((1 - a[i]*u) * (1 - a[j]*u) + O(u^P0)) / u)));
  my(A = matrix(M + 6, #F, r, k, my(t = polcoef(F[k], r - 2, u)); truncate(t + O(e^K))));
  vred(A, K);
}
{
  my(N = 7, R = N*(N-1)/2, M = R + 4, K = 9, c = 3/7, d = -11/5, b = [2, -5/3, 7/4], L, r);
  P0 = M + 10;
  foreach ([1, 2, 1/3, -3/2, 5], lam,
    my(a = concat([c + e, c - e, d + lam*e, d - lam*e], b));
    L = limitspace(a, M, K);
    r = matrank(L);
    print("double pair, lambda = ", lam, ": dim of limit = ", r, ", dim S = ", #L - matrank(L[1..M, ])));
  my(a = concat([c + e, c - e], [d, 13/3, 2, -5/3, 7/4]));
  L = limitspace(a, M, K);
  print("one double (reduction): dim of limit = ", matrank(L), ", dim S = ", #L - matrank(L[1..M, ]));
  \\ lambda symbolic (variable l): the limit over Q(l); contact at some lambda iff all maximal minors of the
  \\ first M jet rows vanish there.  Report the gcd of the numerators of several maximal minors.
  my(a = concat([c + e, c - e, d + l*e, d - l*e], b), A, g = 0, rows);
  L = limitspace(a, M, K);
  A = L[1..M, ];
  print("symbolic lambda: rank of limit = ", matrank(L), ", rank of first M jet rows = ", matrank(A));
  setrand(7);
  for (t = 1, 6, rows = vecsort(Vec(numtoperm(M, random(M!)))[1..(R + 2)]);
    g = gcd(g, numerator(matdet(matrix(R + 2, R + 2, i, j, A[rows[i], j])))));
  print("gcd of the numerators of six maximal minors (contact values of lambda): ", factor(g));
  print("generic-l limit specialized at l = 0: rank = ", matrank(subst(L, l, 0)), ", rank of first M jet rows = ", matrank(subst(A, l, 0)));
  \\ The corner lambda -> 0 along honest arcs: d-pair at rate e^2 (and e^3), c-pair at rate e.
  foreach ([2, 3], s,
    my(a2 = concat([c + e, c - e, d + e^s, d - e^s], b));
    L = limitspace(a2, M, K + 4*s);
    print("arc with d-pair at rate e^", s, ": dim of limit = ", matrank(L), ", dim S = ", #L - matrank(L[1..M, ])));
}
