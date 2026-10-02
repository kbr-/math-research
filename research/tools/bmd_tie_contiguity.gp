\\ Contiguous relations among the confluent tie minors (7 October 2026; cycle bmd-20261007-zd).
\\ N_(m,K) as in bmd_tie_schur_minors.gp (the maximal minor of W^c(c) on the first 3m columns and K, stripped of c and
\\ c-1).  For triples of neighbouring K, find the least delta such that A N_K + B N_K' + C N_K'' = 0 with
\\ deg A, B, C <= delta has a nonzero solution, and print delta against deg N and the factorization of A, B, C.
\\ Generic triples need delta about deg N / 2; a delta bounded in m would be a contiguity relation.
default(parisizemax, 2 * 10^9);
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
bn(x, k) = if (k < 0, 0, binomial(x, k));
rowco(r, m, k) = {
  if (r <= 2 * m, return(bn(-5/2, k - (r - 1))));
  if (r <= 3 * m, my(nn = r - 2 * m - 1); return(bn(-3/2, k - nn) * 'c^max(k - nn, 0)));
  if (r == 3 * m + 1, return(bn(-3, k)));
  if (r == 3 * m + 2, return(sum(aa = 0, k, bn(-3/2, aa) * bn(-3/2, k - aa) * 'c^(k - aa))));
  sum(aa = 0, k - 1, bn(-5/2, aa) * bn(-3/2, k - 1 - aa) * 'c^(k - 1 - aa));
}
strip01(f) = { if (f == 0, return(0)); while (subst(f, 'c, 0) == 0, f /= 'c); while (subst(f, 'c, 1) == 0, f /= ('c - 1)); f / content(f); }
\\ least delta and a relation for three polynomials
rel3(F) = {
  my(D = vecmax(apply(f -> poldegree(f, 'c), F)));
  for (delta = 0, D,
    my(n = 3 * (delta + 1), rows = D + delta + 1, Mt = matrix(rows, n));
    for (z = 1, 3, for (e = 0, delta, my(g = F[z] * 'c^e);
      for (r = 0, rows - 1, Mt[r + 1, (z - 1) * (delta + 1) + e + 1] = polcoef(g, r, 'c))));
    my(K = matker(Mt)); if (#K, my(v = K[, 1], AB = vector(3, z, sum(e = 0, delta, v[(z - 1) * (delta + 1) + e + 1] * 'c^e)));
      return([delta, AB])));
  [-1, 0];
}
{
for (m = 1, 5,
  my(d = m * (m - 1) / 2, W = matrix(3*m + 3, 3*m + 5, r, j, rowco(r, m, d + j - 1)), N = Map());
  forsubset([5, 3], K, my(cols = concat([1 .. 3*m], apply(u -> 3*m + u, Vec(K))));
    mapput(N, Vec(K), strip01(matdet(vecextract(W, "..", cols)))));
  foreach([[[1,2,3],[2,3,4],[3,4,5]], [[1,2,3],[1,2,4],[1,2,5]], [[1,2,3],[1,2,4],[1,3,4]], [[2,3,4],[2,3,5],[2,4,5]]], T,
    my(F = apply(K -> mapget(N, K), T), R = rel3(F));
    emit(Str("m = ", m, ", triple ", T, ": degrees ", apply(f -> poldegree(f, 'c), F), ", least delta ", R[1],
      if (R[1] >= 0, Str(", A,B,C factor degrees ", apply(a -> if (a == 0, "0", apply(poldegree, factor(a)[, 1]~)), R[2])), "")))));
}
