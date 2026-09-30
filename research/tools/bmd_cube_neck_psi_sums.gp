\\ Level sums of the Cauchy-Binet expansion of the peeling neck windows (30 September 2026; cycle bmd-20260930-zf).
\\ Setting as in bmd_cube_neck_psi_levels.gp: det Z[:, W_c] = eps^(const) sum_L eps^L S_L with
\\   S_L = sum over Q with sum Q - l w(w+1)/2 = L of prod_s det T'[:, Q_s] * Psi(Q, W_c).
\\ Question: for which L is S_L nonzero?  Prediction (from the window valuations): S_L = 0 for L < 2 E(c) and
\\ S_(2E(c)) != 0, although individual Psi(Q, W_c) are already nonzero from L = E(c) on.
\\ Each level L <= extra is complete when every w-set with sum excess <= L is enumerated, which holds for
\\ qmax >= w + extra.  Modulo 2^61 - 1, beta = (2, -3, 5)/3.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q0 = 2^61 - 1;
assignE(l, w, cc) = my(rows = vecsort(concat(vector(w, r, vector(l, s, r - 1)))), top = rows[#rows - cc + 1..#rows]); sum(i = 1, cc, max(0, i - top[i] - 1));
run(e, l, w, extra) = {
  my(qmax = w + extra, n = 4 * e, M = n * l, K = w * l, Y = M + K + qmax + 8, lam = -7/2);
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
  for (cc = w, K,
    my(cols = concat(vector(cc, j, -j + qmax + 1), vector(K - cc, j, M + j - 1 + qmax + 1)));
    my(S = vector(extra + 1), cnt = vector(extra + 1));
    forvec(ix = vector(l, s, [1, #cand]),
      my(lev = sum(s = 1, l, vecsum(cand[ix[s]])) - l * w * (w + 1) / 2);
      if (lev <= extra,
        my(Mx = matrix(K, K, a, b, 0), rr = 0);
        for (s = 1, l, foreach (cand[ix[s]], qq, rr++; for (b = 1, K, Mx[rr, b] = P[s][qq][cols[b]])));
        my(d = matdet(Mx));
        if (d != 0, cnt[lev + 1]++; S[lev + 1] += d * prod(s = 1, l, wts[ix[s]]))));
    my(E = assignE(l, w, cc), first = 0); for (L = 0, extra, if (S[L + 1] != 0, first = L; break); if (L == extra, first = oo));
    emit(Str("e=", e, " l=", l, " w=", w, " c=", cc, ": E=", E, ", 2E=", 2 * E, "; levels with nonzero terms: ",
      select(L -> cnt[L + 1] > 0, [0..extra]), "; first nonzero level sum S_L: ", first,
      if (first == 2 * E, " (= 2E)", if (2 * E > extra, " (2E beyond range)", " (MISMATCH)")))));
}
main() = {
  my(cases = if (getenv("CASES"), eval(getenv("CASES")), [[1, 2, 2, 8]]));
  foreach (cases, cs, run(cs[1], cs[2], cs[3], cs[4]));
}
default(parisizemax, 2000000000);
main();
quit
