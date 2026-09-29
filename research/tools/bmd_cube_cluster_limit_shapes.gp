\\ Shape dependence of pair-space flat limits at a cluster of m roots (29 September 2026; cycle bmd-20260929-zzl).
\\ Pair rows: coefficient vectors (T^0..T^M) of phi(a)phi(b), phi(a) = (1 + aT)^(-3/2); cluster roots t*u_1..t*u_m
\\ (u_1 = 0), simple roots s_1.., flat limit at t = 0 by t-saturation over Q[t] (as in bmd_cube_two_double_osculating_limit.gp).
\\ Tested statements:
\\ (1) lem:cube-triple-cluster-canonical-limit: for m = 3 the flat limit is independent of the shape u, also along
\\     hierarchical arcs (u_2 = t), and equals W_T = <phi^2, phi phi', phi'^2 - phi phi''/2> + <phi, phi', phi''> phi_s
\\     + <phi_s phi_s'> (phi = phi(0)), when W_T has dimension R;
\\ (2) lem:cube-cluster-renormalization for m = 4: for shapes u with distinct entries and F_4(u) != 0, where
\\     F_m(u) = det A_(k-1)(u) / prod_(a<b) (u_a - u_b)^(m-2), k = binom(m,2), the limit is the canonical space
\\     Wc = <T^0..T^(k-1)> + <T^i phi_s : i < m> + <phi_s phi_s'> (cluster centred at 0); shapes with F_4(u) = 0
\\     (reflection-symmetric ones, since F_4 is an odd cubic) and hierarchical arcs are controls, not predictions.
\\ Printed per case: F_m(shape) (for constant shapes), rank of the limit, rank of [Wc; limit] (R iff equal to Wc),
\\ and rank on columns 0..R+1. (For m = 3, Wc equals W_T.)
t;
c(n) = binomial(-3/2, n);
phid(a, r, M) = vector(M + 1, k, my(n = k - 1); if (n < r, 0, c(n) * n! / (n - r)! * a^(n - r)));
prodv(u, v, M) = vector(M + 1, k, sum(q = 1, k, u[q] * v[k + 1 - q]));
row(a, b, M) = prodv(phid(a, 0, M), phid(b, 0, M), M);
flat(A) =
{
  my(B = A, steps = 0);
  while (1,
    my(B0 = subst(B, t, 0), K = matker(B0~), l, r, v);
    if (#K == 0, return([B0, steps]));
    l = K[, 1]; r = 1; while (l[r] == 0, r++);
    v = l~ * B;
    if (subst(v, t, 0) != 0 * v, error("combination not divisible by t"));
    B[r, ] = v / t; steps++);
}
limitof(roots, M) =
{
  my(rows = List(), n = #roots);
  for (i = 1, n, for (j = i + 1, n, listput(rows, row(roots[i], roots[j], M))));
  flat(matconcat(Col(Vec(rows))))[1];
}
wt(simple, M) =
{
  my(p = phid(0, 0, M), p1 = phid(0, 1, M), p2 = phid(0, 2, M), L);
  L = List([prodv(p, p, M), prodv(p, p1, M), prodv(p1, p1, M) - prodv(p, p2, M) / 2]);
  for (m = 1, #simple, my(ps = phid(simple[m], 0, M));
    listput(L, prodv(p, ps, M)); listput(L, prodv(p1, ps, M)); listput(L, prodv(p2, ps, M)));
  for (m = 1, #simple, for (m2 = m + 1, #simple, listput(L, row(simple[m], simple[m2], M))));
  matconcat(Col(Vec(L)));
}
wc(m, simple, M) =
{
  my(L = List(), k = binomial(m, 2));
  for (w = 0, k - 1, listput(L, vector(M + 1, j, j - 1 == w)));
  for (q = 1, #simple, my(ps = phid(simple[q], 0, M));
    for (i = 0, m - 1, listput(L, vector(M + 1, j, if (j > i, ps[j - i], 0)))));
  for (q = 1, #simple, for (q2 = q + 1, #simple, listput(L, row(simple[q], simple[q2], M))));
  matconcat(Col(Vec(L)));
}
fm(u) =
{
  my(m = #u, k = binomial(m, 2), A = List(), d);
  for (a = 1, m, for (b = a + 1, m, listput(A, row(u[a], u[b], k - 1))));
  d = matdet(matconcat(Col(Vec(A))));
  d / prod(a = 1, m, prod(b = a + 1, m, (u[a] - u[b])^(m - 2)));
}
{
  print("check: W_T equals Wc for m = 3, simple [1, 5/2]: ", matrank(matconcat([wt([1, 5/2], 14); wc(3, [1, 5/2], 14)])) == 10);
  foreach ([[3, [1, 5/2]], [3, [1, 5/2, -7/3]], [4, [1]], [4, [1, 5/2]]], cs,
    my(m = cs[1], simple = cs[2], N = m + #simple, R = binomial(N, 2), M = R + 4, shapes, W);
    shapes = if (m == 3, [[0, 1, 2], [0, 1, -3], [0, 2, 7], [0, t, 1], [0, t^2, t]],
                          [[0, 1, 3, 7], [0, 1, -2, 5], [0, 2, 3, 9], [0, 1, 2, 3], [0, 1, 3, 4], [0, t, 1, 2], [0, t, 2*t, 1]]);
    W = wc(m, simple, M);
    printf("m=%d simple=%s N=%d R=%d: rank Wc = %d\n", m, simple, N, R, matrank(W));
    for (k = 1, #shapes,
      my(L = limitof(concat(t * shapes[k], simple), M), f = if (variable(shapes[k]) == [], fm(shapes[k]), "arc"));
      printf("  shape %s: F_m %s, rank limit %d, rank with Wc %d, rank on columns 0..R+1 %d\n", shapes[k], f,
        matrank(L), matrank(matconcat([W; L])), matrank(matrix(R, R + 2, r, s, L[r, s])))));
}
