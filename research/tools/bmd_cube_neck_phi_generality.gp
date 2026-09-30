\\ Which structure of the cluster functions does the neck vanishing use? (1 October 2026; cycle bmd-20261001-c)
\\ Model of bmd_cube_neck_separation.gp: U = sum_s P_(<n) phi_s, rows (tau - 1) y^(n-w+p) phi_s modulo U,
\\ tau = sum_m t_m (eps/y)^m, window columns: negative 1..c and high M..M+K-c-1; level sums S_L by Cauchy-Binet.
\\ The divided differences of the original script are a constant invertible change of rows within each p, so
\\ they are omitted here (they scale every window minor by a nonzero constant).
\\ Tested statement (conj:cube-neck-hankel-leading, vanishing part): S_L = 0 for L < 2E and S_(2E) != 0, where
\\ the cluster functions are
\\   mode 0: phi_s = (1 + beta_s y)^(-7/2)          (the neck model);
\\   mode 1: phi_s = F(beta_s y), F a random series with F(0) = 1 (dilates of one common function);
\\   mode 2: phi_s independent random series with phi_s(0) = 1;
\\ and t' is binomial or random.  Modulo 2^61 - 1, random points: a probabilistic finite check.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q0 = 2^61 - 1;
assignE(l, w, cc) = my(rows = vecsort(concat(vector(w, r, vector(l, s, r - 1)))), top = rows[#rows - cc + 1..#rows]); sum(i = 1, cc, max(0, i - top[i] - 1));
rnd() = Mod(1 + random(q0 - 1), q0);
levels(e, l, w, cc, phi, tps) = {
  my(E = assignE(l, w, cc), extra = 2 * E, qmax = w + extra, n = 4 * e, M = n * l, K = w * l, Y = #phi[1]);
  my(A = matrix(M, Y, a, b, 0), row = 0);
  for (s = 1, l, for (i = 0, n - 1, row++; for (r = 1, Y - i, A[row, r + i] = phi[s][r])));
  my(G = A[, 1..M]^(-1) * A, W = Y + qmax);
  my(D = vector(l, j, vector(qmax, q, my(v = vector(W));
    for (r = 1, Y, my(col = r - 1 - q); if (col >= -qmax, v[col + qmax + 1] += phi[j][r]));
    for (d = 0, M - 1, my(x = v[d + qmax + 1]); if (x != 0, for (r = 1, Y, v[r + qmax] -= x * G[d + 1, r])));
    v)));
  my(cand = List()); forsubset([qmax, w], v, if (vecsum(Vec(v)) - w * (w + 1) / 2 <= extra, listput(cand, Vec(v))));
  my(cols = concat(vector(cc, j, -j + qmax + 1), vector(K - cc, j, M + j - 1 + qmax + 1)));
  my(nt = #tps, S = matrix(nt, extra + 1));
  my(wts = vector(nt, t, vector(#cand, i, matdet(matrix(w, w, pp, jj, tps[t][pp - 1 + cand[i][jj]])))));
  forvec(ix = vector(l, s, [1, #cand]),
    my(lev = sum(j = 1, l, vecsum(cand[ix[j]])) - l * w * (w + 1) / 2);
    if (lev <= extra,
      my(Mx = matrix(K, K, a, b, 0), rr = 0);
      for (j = 1, l, foreach (cand[ix[j]], qq, rr++; for (b = 1, K, Mx[rr, b] = D[j][qq][cols[b]])));
      my(d = matdet(Mx));
      if (d != 0, for (t = 1, nt, S[t, lev + 1] += d * prod(j = 1, l, wts[t][ix[j]])))));
  [E, S];
}
firstnz(v) = for (i = 1, #v, if (v[i] != 0, return(i - 1))); oo;
main() = {
  setrand(20261001);
  my(cases = [[1, 2, 2, 3], [1, 2, 2, 4], [1, 3, 2, 4], [1, 3, 2, 5], [1, 2, 3, 4], [1, 2, 3, 5]]);
  foreach (cases, cs,
    my(e = cs[1], l = cs[2], w = cs[3], cc = cs[4], n = 4 * e, E = assignE(l, w, cc), len = 2 * (w + 2 * E) + 8);
    my(Y = n * l + w * l + (w + 2 * E) + 8);
    my(tps = [vector(len, m, Mod(binomial(-5/2, m + n - w), q0)), vector(len, m, rnd())]);
    my(line = Str("e=", e, " l=", l, " w=", w, " c=", cc, " 2E=", 2 * E, ": first nonzero level [binomial t', random t']"));
    for (mode = 0, 2,
      my(res = List());
      for (trial = 1, 2,
        my(bet = vector(l, s, rnd()), F = concat([Mod(1, q0)], vector(Y - 1, r, rnd())));
        my(phi = vector(l, s, vector(Y, r,
          if (mode == 0, Mod(binomial(-7/2, r - 1), q0) * bet[s]^(r - 1),
          mode == 1, F[r] * bet[s]^(r - 1),
          if (r == 1, Mod(1, q0), rnd())))));
        my(S = levels(e, l, w, cc, phi, tps)[2]);
        listput(res, [firstnz(S[1, ]), firstnz(S[2, ])]));
      line = Str(line, "; mode ", mode, ": ", Vec(res)));
    emit(line));
}
default(parisizemax, 2000000000);
main();
quit
