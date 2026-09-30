\\ Node form of the neck level sums (cycle bmd-20261001-a): the secant lead of the neck Hankel review.
\\ With t'_x = sum_m a_m lambda_m^x (nodes m = 1..r), Cauchy-Binet gives
\\   h_Q(t') = sum_{|M| = w} a_M V(lambda_M) det[lambda_m^q]_(m in M, q in Q),  V(lambda_M) = det[lambda_m^(p-1)]_(p<=w, m in M),
\\ so S_L = sum over l-tuples (M_1..M_l) of prod_s a_(M_s) T_L(M_1..M_l), with
\\   T_L(M) = prod_s V(lambda_(M_s)) * sum_Q Psi(Q) prod_s det[lambda_m^q]_(m in M_s, q in Q_s).
\\ Question: for L < 2E, does T_L vanish for every tuple (termwise), or only after summing the tuples with the same
\\ monomial prod_s a_(M_s) (the same multiset union of the M_s)?  Psi as in bmd_cube_neck_psi_pattern.gp; random beta
\\ and random nodes modulo 2^61-1, r = lw nodes.
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
{
  setrand(20261001);
  foreach ([[1,2,2,4],[1,2,3,5],[1,3,2,5]], cs,
    my(e = cs[1], l = cs[2], w = cs[3], cc = cs[4], bet = vector(l, s, Mod(1 + random(q0 - 1), q0)), r = psis(e, l, w, cc, bet), E = r[1], P = r[2]);
    my(nn = l * w, lam = vector(nn, m, Mod(1 + random(q0 - 1), q0)), subs = List());
    forsubset([nn, w], v, listput(subs, Vec(v)));
    subs = Vec(subs);
    my(V(M) = matdet(matrix(w, w, p, j, lam[M[j]]^(p - 1))), dQ(M, Q) = matdet(matrix(w, w, i, j, lam[M[i]]^Q[j])));
    print("(e,l,w,c) = ", cs, ", 2E = ", 2 * E, ", nodes ", nn);
    for (L = 0, 2 * E,
      my(at = select(v -> v[1] == L, P));
      if (#at,
        my(nz = 0, tot = 0, cls = Map());
        forvec(ix = vector(l, s, [1, #subs]),
          my(Ms = vector(l, s, subs[ix[s]]), T = prod(s = 1, l, V(Ms[s])) * sum(i = 1, #at, at[i][3] * prod(s = 1, l, dQ(Ms[s], at[i][2][s]))));
          tot++; if (T != 0, nz++);
          my(key = vecsort(concat(Ms)), old = 0); if (mapisdefined(cls, key, &old), mapput(cls, key, old + T), mapput(cls, key, T)));
        my(cnz = 0, ctot = 0); foreach (Mat(cls)[, 2], x, ctot++; if (x != 0, cnz++));
        print("   level ", L, ": tuples with T != 0: ", nz, " of ", tot, "; monomial classes with nonzero sum: ", cnz, " of ", ctot))));
}
