\\ Generic vanishing test for the neck level sums (cycle bmd-20260930-zzz).
\\ Hypothesis (G): for L < 2E the level sum sum_Q Psi(Q) prod_s p_(Q_s)(X) vanishes for a GENERIC w x infinity matrix X,
\\ p_Q(X) = det of the columns Q of X, not only for the Hankel matrix [t'_(p-1+q)].  At L = 2E, compare the level
\\ sum for generic X (expected nonzero or zero?) with the Hankel one.  Psi as in bmd_cube_neck_psi_pattern.gp.
\\ Model as in bmd_cube_neck_separation.gp (lem:cube-neck-level-expansion); Psi(Q) are the beta-minors of the level
\\ expansion.  For each window, one random beta (mod 2^61-1) and each level L <= 2E carrying Psi != 0, the script
\\ prints: the number of tuples with Psi != 0; whether the level sum vanishes at four random generic matrices X
\\ (maximal minors p_Q) and at four random Hankel sequences t' (minors h_Q); the number of distinct Psi values and
\\ their ratio when there are two.  The window (1,2,2,4) is run three times with fresh random draws.
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
pQ(X, Q) = matdet(matrix(#Q, #Q, p, j, X[p, Q[j]]));
hQ(t, Q) = matdet(matrix(#Q, #Q, p, j, t[p - 1 + Q[j]]));
{
  setrand(20260930);
  foreach ([[1,2,2,3],[1,2,2,4],[1,2,2,4],[1,2,2,4],[1,3,2,4],[1,3,2,5],[1,3,2,6],[1,2,3,4],[1,2,3,5],[1,2,3,6]], cs,
    my(e = cs[1], l = cs[2], w = cs[3], cc = cs[4], bet = vector(l, s, Mod(1 + random(q0 - 1), q0)), r = psis(e, l, w, cc, bet), E = r[1], P = r[2], rep = List());
    for (L = 0, 2 * E,
      my(at = select(v -> v[1] == L, P));
      if (#at,
        my(Xs = vector(4, k, matrix(w, 60, i, j, Mod(1 + random(q0 - 1), q0))), ts = vector(4, k, vector(80, m, Mod(1 + random(q0 - 1), q0))));
        my(gen = vector(4, k, sum(i = 1, #at, at[i][3] * prod(j = 1, l, pQ(Xs[k], at[i][2][j])))));
        my(han = vector(4, k, sum(i = 1, #at, at[i][3] * prod(j = 1, l, hQ(ts[k], at[i][2][j])))));
        my(vals = Set(apply(v -> v[3], at)));
        listput(rep, [L, #at, gen == vector(4, k, 0), han == vector(4, k, 0), #vals, if (#vals == 2, bestappr(vals[2] / vals[1]), "-")])));
    print("(e,l,w,c) = ", cs, ", 2E = ", 2 * E, ": [level, #tuples with Psi != 0, generic sum zero, Hankel sum zero, #distinct Psi values, ratio if two] = ", Vec(rep)));
}
