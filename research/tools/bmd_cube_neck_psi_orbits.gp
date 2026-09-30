\\ Orbit sums of the neck level expansion (30 September 2026; cycle bmd-20260930-zg).
\\ Setting of bmd_cube_neck_psi_sums.gp.  The permutations of the l doubles act on the tuples Q = (Q_1..Q_l);
\\ the weight prod_s det T'[:, Q_s] is invariant.  Question: at each level L between E(c) and 2E(c), do the
\\ weighted minors already cancel within each orbit (orbit sums zero), and which orbits survive at level 2E?
\\ Output per window and level: number of orbits with a nonzero minor, number with a nonzero orbit sum, and the
\\ surviving orbits (as sorted multisets of the Q_s) at level 2E.  Modulo 2^61 - 1, beta = (2, -3, 5)/3.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q0 = 2^61 - 1;
assignE(l, w, cc) = my(rows = vecsort(concat(vector(w, r, vector(l, s, r - 1)))), top = rows[#rows - cc + 1..#rows]); sum(i = 1, cc, max(0, i - top[i] - 1));
run(e, l, w, cmax) = {
  my(extra = 2 * assignE(l, w, cmax), qmax = w + extra, n = 4 * e, M = n * l, K = w * l, Y = M + K + qmax + 8, lam = -7/2);
  my(bet = vector(l, s, Mod([2, -3, 5][s], q0) / 3));
  my(phi = vector(l, s, vector(Y, r, Mod(binomial(lam, r - 1), q0) * bet[s]^(r - 1))));
  my(A = matrix(M, Y, a, b, 0), row = 0);
  for (s = 1, l, for (i = 0, n - 1, row++; for (r = 1, Y - i, A[row, r + i] = phi[s][r])));
  my(G = A[, 1..M]^(-1) * A);
  my(W = Y + qmax, P = vector(l, s, vector(qmax, q, my(v = vector(W));
    for (r = 1, Y, my(col = r - 1 - q); if (col >= -qmax, v[col + qmax + 1] += phi[s][r]));
    for (d = 0, M - 1, my(x = v[d + qmax + 1]); if (x != 0, for (r = 1, Y, v[r + qmax] -= x * G[d + 1, r])));
    v)));
  my(tp = vector(2 * qmax + 8, m, Mod(binomial(-5/2, m + n - w), q0)));
  my(cand = List()); forsubset([qmax, w], v, if (vecsum(Vec(v)) - w * (w + 1) / 2 <= extra, listput(cand, Vec(v))));
  my(wts = vector(#cand, i, matdet(matrix(w, w, pp, jj, tp[pp - 1 + cand[i][jj]]))));
  for (cc = w + 1, cmax,
    my(E = assignE(l, w, cc), cols = concat(vector(cc, j, -j + qmax + 1), vector(K - cc, j, M + j - 1 + qmax + 1)));
    my(orb = Map());
    forvec(ix = vector(l, s, [1, #cand]),
      my(lev = sum(s = 1, l, vecsum(cand[ix[s]])) - l * w * (w + 1) / 2);
      if (lev >= E && lev <= 2 * E,
        my(Mx = matrix(K, K, a, b, 0), rr = 0);
        for (s = 1, l, foreach (cand[ix[s]], qq, rr++; for (b = 1, K, Mx[rr, b] = P[s][qq][cols[b]])));
        my(d = matdet(Mx));
        if (d != 0,
          my(key = [lev, vecsort(vector(l, s, cand[ix[s]]))], old = 0);
          mapisdefined(orb, key, &old); mapput(orb, key, old + d * prod(s = 1, l, wts[ix[s]])))));
    my(ks = Mat(orb));
    for (L = E, 2 * E,
      my(nz = 0, surv = List());
      for (i = 1, #ks~, if (ks[i, 1][1] == L, nz++; if (ks[i, 2] != 0, listput(surv, ks[i, 1][2]))));
      emit(Str("e=", e, " l=", l, " w=", w, " c=", cc, " E=", E, " level ", L, ": orbits with a nonzero minor ", nz,
        ", with nonzero orbit sum ", #surv, if (L == 2 * E && #surv <= 6, Str("; surviving ", Vec(surv)), "")))));
}
main() = {
  my(cases = if (getenv("CASES"), eval(getenv("CASES")), [[1, 2, 2, 4]]));
  foreach (cases, cs, run(cs[1], cs[2], cs[3], cs[4]));
}
default(parisizemax, 2000000000);
main();
quit
