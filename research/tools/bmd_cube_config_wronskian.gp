\\ Squared Wronskian of V_a = <1, z, ((z-a_i)(z-a_j))^(1/2)> for an honest separated configuration a,
\\ modulo PR.  W^2(z0) = det(normalized Taylor matrix)^2 * prod_{i<j}(z0-a_i)(z0-a_j) * const, so
\\ F(z) = W^2 prod (z-a_i)^E is a polynomial; strip the branch factors to get Q = c R^2 (R = prod (z-x)^wt over
\\ non-branch weight points).  Reports deg R, squarefreeness, and branch orders.
PR = 2^61 - 1;
default(parisizemax, 2000000000);
taymat(a, z0, n) = {
  my(N = #a, M = matrix(n, n), r = 1, T = 'T);
  M[1, 1] = 1; M[2, 1] = z0; M[2, 2] = 1;
  r = 2;
  for (i = 1, N, for (j = i + 1, N,
    r++;
    my(g = ((1 + T/(z0 - a[i]) + O(T^n)) * (1 + T/(z0 - a[j]) + O(T^n)))^(1/2));
    for (k = 1, n, M[r, k] = polcoef(g, k - 1, T))));
  M;
}
w2(a, z0) = {
  my(N = #a, n = 2 + N*(N-1)/2, M = taymat(a, Mod(z0, PR), n), d = matdet(M));
  d^2 * prod(i = 1, N, (Mod(z0, PR) - a[i]))^(N - 1);
}
\\ F(z) = W^2 * prod (z-a_i)^E interpolated with degree bound DB; returns [Q, branch orders]
wpoly(a, E, DB) = {
  my(N = #a, pts = vector(DB + 4, k, Mod(k * 7919 + 13, PR)), vals, P);
  vals = vector(DB + 4, k, w2(a, lift(pts[k])) * prod(i = 1, N, pts[k] - a[i])^E);
  P = polinterpolate(pts[1..DB + 1], vals[1..DB + 1], 'z);
  for (k = DB + 2, DB + 4, if (subst(P, 'z, pts[k]) != vals[k], return(0)));
  my(ords = vector(N));
  for (i = 1, N, while (subst(P, 'z, a[i]) == 0, P = P / ('z - a[i]); ords[i]++));
  [P, ords];
}
analyse(a, E) = {
  my(res = 0, DB = 50);
  while (res == 0, DB = 2 * DB; res = wpoly(a, E, DB));
  my(Q = res[1], G = gcd(Q, Q'), R = G, ok);
  \\ Q = c R^2: R = Q / squarefree part if all multiplicities even
  ok = (Q == pollead(Q) / pollead(R)^2 * R^2);
  my(sqf = poldegree(gcd(R, R')) == 0);
  [poldegree(Q), poldegree(R), ok, sqf, res[2] - vector(#a, i, E)];
}
{
  foreach([[2, 3/7, -5/3, 11/4, -1, 7/2], [2, 3/7, -5/3, 11/4, -1, 7/2, -13/5]], b,
    my(a = apply(x -> Mod(x, PR), b), N = #b, r = analyse(a, 3 * N));
    print("N = ", N, ": deg Q = ", r[1], ", deg R = ", r[2], ", Q = c R^2: ", r[3], ", R squarefree: ", r[4], ", branch orders of W^2: ", r[5]));
}
