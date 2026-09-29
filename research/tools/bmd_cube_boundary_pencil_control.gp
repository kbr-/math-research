\\ Control of the boundary pencil lemma (lem:cube-boundary-pencil; 29 September 2026, cycle bmd-20260929-zzm).
\\ Cluster of m = 4 roots t*u(t), u(t) = u* + t v, with u* on F_4 = 0 (reflection-symmetric), plus simple roots.
\\ Tested statement: with k = 6, J0 = {0..5}, J1 = {0..4, 6}, p_J the Pluecker coordinates of the shape's pair space,
\\ if p_J1(u*) != 0 the flat limit is Pol_<5 + <a T^5 + b T^6> + <T^i phi_s : i < 4> + <phi_s phi_s'>, with
\\ (a : b) = lim (p_J0(u(t)) : t p_J1(u(t))), here (d/dt p_J0(u(t))|_0 : p_J1(u*)). Cases: v = 0 (fixed shape,
\\ predicted (0 : 1)), and a transversal v (predicted interior point). Control: the canonical space (1 : 0) and the
\\ endpoint (0 : 1) must differ from the transversal limit. Printed: a, b, rank of [prediction; limit] (R iff equal).
t;
c(n) = binomial(-3/2, n);
phid(a, r, M) = vector(M + 1, k, my(n = k - 1); if (n < r, 0, c(n) * n! / (n - r)! * a^(n - r)));
prodv(u, v, M) = vector(M + 1, k, sum(q = 1, k, u[q] * v[k + 1 - q]));
row(a, b, M) = prodv(phid(a, 0, M), phid(b, 0, M), M);
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
pairmat(u, M) = { my(L = List()); for (a = 1, #u, for (b = a + 1, #u, listput(L, row(u[a], u[b], M)))); matconcat(Col(Vec(L))); }
pl(u, J) = matdet(vecextract(pairmat(u, 7), "1..6", J));
pred(ab, simple, M) =
{
  my(L = List());
  for (w = 0, 4, listput(L, vector(M + 1, j, j - 1 == w)));
  listput(L, vector(M + 1, j, ab[1] * (j - 1 == 5) + ab[2] * (j - 1 == 6)));
  for (q = 1, #simple, my(ps = phid(simple[q], 0, M));
    for (i = 0, 3, listput(L, vector(M + 1, j, if (j > i, ps[j - i], 0)))));
  for (q = 1, #simple, for (q2 = q + 1, #simple, listput(L, row(simple[q], simple[q2], M))));
  matconcat(Col(Vec(L)));
}
{
  my(J0 = [1, 2, 3, 4, 5, 6], J1 = [1, 2, 3, 4, 5, 7]);
  foreach ([[[0, 1, 2, 3], [1]], [[0, 1, 3, 4], [1, 5/2]]], cs,
    my(us = cs[1], simple = cs[2], N = 4 + #simple, R = binomial(N, 2), M = R + 4);
    printf("u* = %s, simple %s, N = %d: p_J0(u*) = %s, p_J1(u*) = %s\n", us, simple, N, pl(us, J0), pl(us, J1));
    foreach ([[0, 0, 0, 0], [0, 0, 0, 1], [0, 1, 0, -2]], v,
      my(ut = us + t * v, p0 = pl(ut, J0), a = polcoef(p0, 1, t), b = pl(us, J1), L, P, Pc, Pe);
      if (polcoef(p0, 0, t) != 0, error("u* not on F_4 = 0"));
      if (v == [0, 0, 0, 0], a = 0);
      my(rows = List(), roots = concat(t * ut, simple));
      for (i = 1, N, for (j = i + 1, N, listput(rows, row(roots[i], roots[j], M))));
      L = flat(matconcat(Col(Vec(rows))));
      P = pred([a, b], simple, M); Pc = pred([1, 0], simple, M); Pe = pred([0, 1], simple, M);
      printf("  v = %s: (a : b) = (%s : %s); rank [prediction; limit] %d, [canonical; limit] %d, [endpoint (0:1); limit] %d, contact rank %d\n",
        v, a, b, matrank(matconcat([P; L])), matrank(matconcat([Pc; L])), matrank(matconcat([Pe; L])),
        matrank(matrix(R, R + 2, r, s, L[r, s])))));
}
