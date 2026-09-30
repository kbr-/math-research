\\ Core of the neck Psi computation (assignE, psis), shared by the cycle bmd-20261001-b scripts; copied from
\\ bmd_cube_neck_psi_pattern.gp, model of bmd_cube_neck_separation.gp.
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
