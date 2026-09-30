\\ Level structure of the neck windows in the divided-difference basis (30 September 2026; cycle bmd-20260930-zi).
\\ Rows: group j (Newton divided difference over beta_1..beta_(j+1)) and p < w, row = sum_q t'_(p+q) eps^(p+q)
\\ Delta_j psi_q.  Cauchy-Binet per group: choices Q = (Q_0..Q_(l-1)) of w-sets, level L = sum_j sum Q_j - lw(w+1)/2,
\\ weight prod_j det[t'_(p+q)]_(p<w, q in Q_j), minor Psi' of the rows Delta_j psi_q on the window columns.
\\ Question (block size w >= 2): between the divided-difference bound E' and 2E, do the level sums vanish, and at
\\ level 2E which choices Q contribute (how many, and whether one dominates)?  Also: the lowest level with a nonzero
\\ single term.  Modulo 2^61 - 1 at beta = (2, -3, 5)/3; levels enumerated completely up to 2E (q <= w + 2E).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q0 = 2^61 - 1;
assignE(l, w, cc) = my(rows = vecsort(concat(vector(w, r, vector(l, s, r - 1)))), top = rows[#rows - cc + 1..#rows]); sum(i = 1, cc, max(0, i - top[i] - 1));
ddE(l, w, cc) = my(caps = vecsort(concat(vector(l, j, vector(w, r, r - j + 1)))), top = caps[#caps - cc + 1..#caps]); sum(i = 1, cc, max(0, i - top[i]));
run(e, l, w, cc) = {
  my(E = assignE(l, w, cc), Ep = ddE(l, w, cc), extra = 2 * E, qmax = w + extra, n = 4 * e, M = n * l, K = w * l, Y = M + K + qmax + 8, lam = -7/2);
  my(bet = vector(l, s, Mod([2, -3, 5][s], q0) / 3));
  my(phi = vector(l, s, vector(Y, r, Mod(binomial(lam, r - 1), q0) * bet[s]^(r - 1))));
  my(A = matrix(M, Y, a, b, 0), row = 0);
  for (s = 1, l, for (i = 0, n - 1, row++; for (r = 1, Y - i, A[row, r + i] = phi[s][r])));
  my(G = A[, 1..M]^(-1) * A, W = Y + qmax);
  my(dd = vector(l, j, vector(l, s, if (s > j, 0, 1 / prod(i = 1, j, if (i == s, 1, bet[s] - bet[i]))))));
  \\ Delta_j psi_q rows
  my(D = vector(l, j, vector(qmax, q, my(v = vector(W));
    for (s = 1, j, for (r = 1, Y, my(col = r - 1 - q); if (col >= -qmax, v[col + qmax + 1] += dd[j][s] * phi[s][r])));
    for (d = 0, M - 1, my(x = v[d + qmax + 1]); if (x != 0, for (r = 1, Y, v[r + qmax] -= x * G[d + 1, r])));
    v)));
  my(tp = vector(2 * qmax + 8, m, Mod(binomial(-5/2, m + n - w), q0)));
  my(cand = List()); forsubset([qmax, w], v, if (vecsum(Vec(v)) - w * (w + 1) / 2 <= extra, listput(cand, Vec(v))));
  my(wts = vector(#cand, i, matdet(matrix(w, w, pp, jj, tp[pp - 1 + cand[i][jj]]))));
  my(cols = concat(vector(cc, j, -j + qmax + 1), vector(K - cc, j, M + j - 1 + qmax + 1)));
  my(S = vector(extra + 1), firstterm = oo, top = List());
  forvec(ix = vector(l, s, [1, #cand]),
    my(lev = sum(j = 1, l, vecsum(cand[ix[j]])) - l * w * (w + 1) / 2);
    if (lev <= extra,
      my(Mx = matrix(K, K, a, b, 0), rr = 0);
      for (j = 1, l, foreach (cand[ix[j]], qq, rr++; for (b = 1, K, Mx[rr, b] = D[j][qq][cols[b]])));
      my(d = matdet(Mx));
      if (d != 0, my(t = d * prod(j = 1, l, wts[ix[j]])); S[lev + 1] += t; firstterm = min(firstterm, lev);
        if (lev == extra, listput(top, vector(l, j, cand[ix[j]]))))));
  my(firstsum = oo); for (L = 0, extra, if (S[L + 1] != 0, firstsum = L; break));
  emit(Str("e=", e, " l=", l, " w=", w, " c=", cc, ": E=", E, " E'=", Ep, " 2E=", 2 * E, "; first nonzero term level ", firstterm,
    "; first nonzero level sum ", firstsum, "; terms at 2E: ", #top, if (#top <= 8, Str(" ", Vec(top)), "")));
}
main() = {
  my(cases = if (getenv("CASES"), eval(getenv("CASES")), [[1, 2, 2, 4]]));
  foreach (cases, cs, run(cs[1], cs[2], cs[3], cs[4]));
}
default(parisizemax, 2000000000);
main();
quit
