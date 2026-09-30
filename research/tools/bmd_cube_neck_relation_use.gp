\\ Which quadratic Hankel relations do the neck level sums use? (cycle bmd-20261001-b)
\\ At a window with w = 2, l = 2, each level sum below 2E is sum_Q Psi(Q) h_(Q1) h_(Q2), a linear relation among the
\\ products h_ij h_kl of 2x2 Hankel minors (h_ij = t_i t_(j+1) - t_j t_(i+1)) that holds for Hankel but not generic minors.
\\ For each such level L: the weight is W = sum of all indices; compute
\\   R_H(W) = relations among the products of weight W for Hankel minors, R_P(W) = those for generic minors (Pluecker),
\\ their dimensions, and the dimension of R_P(W) + <Psi-vectors at L for three random beta>: does each Psi-vector lie
\\ in R_H(W), and how many extra (non-Pluecker) directions do the Psi-vectors span?
\\ Also: the counts of all quadratic relations for 2 x n (n = 5..9), to test the pattern C(n,4) + C(n-1,4).
q0 = 2^61 - 1;
default(parisizemax, 4000000000);
read("research/tools/bmd_cube_neck_psi_core.gp");
prods(n, W) = {
  my(S = List()); forsubset([n, 2], v, listput(S, Vec(v))); S = Vec(S);
  my(P = List()); for (i = 1, #S, for (j = i, #S, if (vecsum(S[i]) + vecsum(S[j]) == W, listput(P, [S[i], S[j]])))); Vec(P);
}
relspace(P, n, hank) = {
  \\ basis of relations (kernel of the evaluation map) among the products in P
  my(K = #P + 25, M = matrix(K, #P));
  for (r = 1, K, my(t = vector(n + 2, i, Mod(random(q0), q0)), u = vector(n + 2, i, Mod(random(q0), q0)));
    my(m(Q) = if (hank, t[Q[1]] * t[Q[2] + 1] - t[Q[2]] * t[Q[1] + 1], t[Q[1]] * u[Q[2]] - t[Q[2]] * u[Q[1]]));
    for (c = 1, #P, M[r, c] = m(P[c][1]) * m(P[c][2])));
  matker(M);
}
allrel(n, hank) = {
  my(S = List()); forsubset([n, 2], v, listput(S, Vec(v))); S = Vec(S);
  my(P = List()); for (i = 1, #S, for (j = i, #S, listput(P, [S[i], S[j]]))); P = Vec(P);
  #relspace(P, n, hank);
}
{
  setrand(20261001);
  for (n = 5, 9, my(g = allrel(n, 0), h = allrel(n, 1));
    print("2 x ", n, ": relations generic ", g, " (C(n,4) = ", binomial(n, 4), "), Hankel ", h, " (C(n,4)+C(n-1,4) = ", binomial(n, 4) + binomial(n - 1, 4), ")"));
  foreach ([[1,2,2,4]], cs,
    my(e = cs[1], l = cs[2], w = cs[3], cc = cs[4]);
    my(runs = vector(3, k, psis(e, l, w, cc, vector(l, s, Mod(1 + random(q0 - 1), q0)))), E = runs[1][1]);
    for (L = 0, 2 * E - 1,
      my(ats = vector(3, k, select(v -> v[1] == L, runs[k][2])));
      if (#ats[1],
        my(Wt = vecsum(ats[1][1][2][1]) + vecsum(ats[1][1][2][2]), n = vecmax(concat(apply(v -> concat(v[2]), ats[1]))) + 1, P = prods(n, Wt));
        my(key(Q1, Q2) = if (lex(Q1, Q2) <= 0, [Q1, Q2], [Q2, Q1]));
        my(vecs = vector(3, k, my(v = vectorv(#P)); foreach (ats[k], a, my(kk = key(a[2][1], a[2][2])); for (c = 1, #P, if (P[c] == kk, v[c] += a[3]))); v));
        my(RH = relspace(P, n, 1), RP = relspace(P, n, 0));
        my(inH = vector(3, k, matrank(matconcat([RH, vecs[k]])) == #RH));
        my(extra = matrank(matconcat(concat([RP], vecs))) - matrank(RP));
        print("(1,2,2,4) level ", L, ": weight ", Wt, ", ", #P, " products; relations Hankel ", #RH, ", Pluecker ", matrank(RP),
          "; Psi-vectors in Hankel relations: ", inH, "; extra directions spanned by the three Psi-vectors beyond Pluecker: ", extra))));
}
