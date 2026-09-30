\\ Pattern of the beta-minors Psi(Q) of the neck level expansion (cycle bmd-20260930-zzz).
\\ Model as in bmd_cube_neck_separation.gp (lem:cube-neck-level-expansion): the level sum is
\\   S_L(beta, t') = sum over l-tuples Q = (Q_1..Q_l) of w-sets of pole orders at level L of Psi(Q) prod_s h_(Q_s)(t'),
\\ h_Q(t') = det[t'_(p-1+q)]_(p<=w, q in Q).  Question: between the first nonzero Psi level and 2E, how do the
\\ contributions cancel?  For one random beta (mod 2^61-1), list at each level L <= 2E the l-tuples with Psi != 0
\\ and their values, and whether the level sum vanishes at eight random t'.
q0 = 2^61 - 1;
assignE(l, w, cc) = my(rows = vecsort(concat(vector(w, r, vector(l, s, r - 1)))), top = rows[#rows - cc + 1..#rows]); sum(i = 1, cc, max(0, i - top[i] - 1));
psis(e, l, w, cc, bet) = {
  my(E = assignE(l, w, cc), extra = 2 * E, qmax = w + extra, n = 4 * e, M = n * l, K = w * l, Y = M + K + qmax + 8, lam = -7/2);
  my(phi = vector(l, s, vector(Y, r, Mod(binomial(lam, r - 1), q0) * bet[s]^(r - 1))));
  my(A = matrix(M, Y, a, b, 0), row = 0);
  for (s = 1, l, for (i = 0, n - 1, row++; for (r = 1, Y - i, A[row, r + i] = phi[s][r])));
  my(G = A[, 1..M]^(-1) * A, W = Y + qmax);
  my(dd = vector(l, j, vector(l, s, if (s > j, 0, 1 / prod(i = 1, j, if (i == s, 1, bet[s] - bet[i]))))));
  my(D = vector(l, j, vector(qmax, q, my(v = vector(W));
    for (s = 1, j, for (r = 1, Y, my(col = r - 1 - q); if (col >= -qmax, v[col + qmax + 1] += dd[j][s] * phi[s][r])));
    for (d = 0, M - 1, my(x = v[d + qmax + 1]); if (x != 0, for (r = 1, Y, v[r + qmax] -= x * G[d + 1, r])));
    v)));
  my(cand = List()); forsubset([qmax, w], v, if (vecsum(Vec(v)) - w * (w + 1) / 2 <= extra, listput(cand, Vec(v))));
  my(cols = concat(vector(cc, j, -j + qmax + 1), vector(K - cc, j, M + j - 1 + qmax + 1)));
  my(out = List());
  forvec(ix = vector(l, s, [1, #cand]),
    my(lev = sum(j = 1, l, vecsum(cand[ix[j]])) - l * w * (w + 1) / 2);
    if (lev <= extra,
      my(Mx = matrix(K, K, a, b, 0), rr = 0);
      for (j = 1, l, foreach (cand[ix[j]], qq, rr++; for (b = 1, K, Mx[rr, b] = D[j][qq][cols[b]])));
      my(d = matdet(Mx)); if (d != 0, listput(out, [lev, vector(l, j, cand[ix[j]]), d]))));
  [E, Vec(out)];
}
hQ(t, Q) = matdet(matrix(#Q, #Q, p, j, t[p - 1 + Q[j]]));
{
  setrand(20260930);
  foreach ([[1, 2, 2, 3], [1, 2, 2, 4], [1, 3, 2, 4]], cs,
    my(e = cs[1], l = cs[2], w = cs[3], cc = cs[4], bet = vector(l, s, Mod(1 + random(q0 - 1), q0)), r = psis(e, l, w, cc, bet), E = r[1], P = r[2]);
    print("(e,l,w,c) = ", cs, ": E = ", E, ", 2E = ", 2 * E);
    for (L = 0, 2 * E,
      my(at = select(v -> v[1] == L, P), ts = vector(8, t, vector(40, m, Mod(1 + random(q0 - 1), q0))));
      if (#at,
        \\ multiset of the Q's (species-unordered) and the value of the level sum at random t'
        my(vals = vector(8, t, sum(i = 1, #at, at[i][3] * prod(j = 1, l, hQ(ts[t], at[i][2][j])))));
        print("   level ", L, ": ", #at, " tuples with Psi != 0; level sum zero at 8 random t': ", vals == vector(8, t, 0));
        if (#at <= 12, foreach (at, v, print("      Q = ", v[2], "  Psi = ", lift(v[3])))))));
}
