\\ Control of the cross-block factorization lemma (lem:cube-cross-block-factorization; 29 September 2026, cycle bmd-20260929-zzo).
\\ Clusters A = {h u_a} at 0 (m roots, e1(u) = 0) and B = {1 + k v_b} at 1 (m' roots, e1(v) = 0), no other roots.
\\ With Y = T/(1+T), mu_ij = (1+T)^(-3/2) T^i Y^j, c_n = binom(-3/2, n), E = <e_i e_j : i < m, j < m'>, and
\\ K = {kappa : sum kappa_ij c_i c_j mu_ij = 0}, the lemma predicts the flat limit
\\   Pol_<binom(m,2) + {(1+T)^-3 p(Y) : deg p < binom(m',2)} + <c_i c_j mu_ij> + <eps_A U_kappa + eps_B V_kappa : kappa in K>,
\\ U_kappa = sum_j (kappa_(m-2,j) c_m c_j mu_(m,j) + kappa_(m-1,j) c_(m+1) c_j mu_(m+1,j)), V_kappa symmetric in B,
\\ (eps_A : eps_B) = lim (h^2 e2(u) : k^2 e2(v)), when the within-cluster shapes are canonical and dimensions add to R.
\\ Printed per case: dim K, rank of the prediction, rank of [prediction; exact limit] (R iff equal), and a control with
\\ the ratio (eps_A : -eps_B), which should differ.
t; default(seriesprecision, 80);
M0 = 30;
c(n) = binomial(-3/2, n);
phid(a, r, M) = vector(M + 1, k, my(n = k - 1); if (n < r, 0, c(n) * n! / (n - r)! * a^(n - r)));
prodv(u, v, M) = vector(M + 1, k, sum(q = 1, k, u[q] * v[k + 1 - q]));
row(a, b, M) = prodv(phid(a, 0, M), phid(b, 0, M), M);
vecs(f, M) = vector(M + 1, k, polcoef(f, k - 1, T));
flat(A) =
{
  my(B = A);
  while (1,
    my(B0 = subst(B, t, 0), K = matker(B0~), l, r, v);
    if (#K == 0, return(B0));
    l = K[, 1]; r = 1; while (l[r] == 0, r++);
    v = l~ * B;
    if (subst(v, t, 0) != 0 * v, error("combination not divisible by t"));
    B[r, ] = v / t);
}
e2(u) = sum(a = 1, #u, sum(b = a + 1, #u, u[a] * u[b]));
pred(m, mp, epsA, epsB, M) =
{
  my(Y = T / (1 + T) + O(T^(M + 1)), base = (1 + T)^(-3/2) + O(T^(M + 1)), mu, L = List(), cols, K);
  mu = ((i, j) -> vecs(base * T^i * Y^j, M));
  for (w = 0, binomial(m, 2) - 1, listput(L, vector(M + 1, j, j - 1 == w)));
  for (w = 0, binomial(mp, 2) - 1, listput(L, vecs((1 + T)^(-3) * Y^w + O(T^(M + 1)), M)));
  cols = List(); for (i = 0, m - 1, for (j = 0, mp - 1, listput(cols, c(i) * c(j) * mu(i, j)); listput(L, c(i) * c(j) * mu(i, j))));
  K = matker(matconcat(Col(Vec(cols)))~);
  for (q = 1, #K,
    my(kap = K[, q], U = vector(M + 1), V = vector(M + 1), idx = (i, j) -> i * mp + j + 1);
    for (j = 0, mp - 1, U += kap[idx(m - 2, j)] * c(m) * c(j) * mu(m, j) + kap[idx(m - 1, j)] * c(m + 1) * c(j) * mu(m + 1, j));
    for (i = 0, m - 1, V += kap[idx(i, mp - 2)] * c(i) * c(mp) * mu(i, mp) + kap[idx(i, mp - 1)] * c(i) * c(mp + 1) * mu(i, mp + 1));
    listput(L, epsA * U + epsB * V));
  [matconcat(Col(Vec(L))), #K];
}
{
  foreach ([[[-1/2, 1/2], [-1/2, 1/2]], [[-1, 0, 1], [-1/2, 1/2]], [[1, 2, -3], [-1/2, 1/2]], [[-1, 0, 1], [-1, 0, 1]], [[1, 2, -3], [-2, -1, 3]]], sh,
    my(u = sh[1], v = sh[2], m = #u, mp = #v, N = m + mp, R = binomial(N, 2), M = R + 4);
    foreach ([[t, t], [t, 2 * t], [t, t^2], [t^2, t]], hk,
      my(h = hk[1], k = hk[2], e = min(valuation(h, t), valuation(k, t)), eA, eB, P, Pc, L, rows = List(), roots);
      eA = polcoef(h^2, 2 * e, t) * e2(u); eB = polcoef(k^2, 2 * e, t) * e2(v);
      P = pred(m, mp, eA, eB, M); Pc = pred(m, mp, eA, -eB, M);
      roots = concat(h * u, vector(mp, b, 1 + k * v[b]));
      for (a = 1, N, for (b = a + 1, N, listput(rows, row(roots[a], roots[b], M))));
      L = flat(matconcat(Col(Vec(rows))));
      printf("u=%s v=%s (h,k)=%s: dim K %d, (eps_A:eps_B)=(%s:%s), rank prediction %d, [prediction; limit] %d, control %s, contact rank %d\n",
        u, v, hk, P[2], eA, eB, matrank(P[1]), matrank(matconcat([P[1]; L])),
        if (eA != 0 && eB != 0, matrank(matconcat([Pc[1]; L])), "-"), matrank(matrix(R, R + 2, r, s, L[r, s])))));
}
