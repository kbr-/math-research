\\ Separation test for the neck windows at block size two (30 September 2026; cycle bmd-20260930-zm).
\\ Model and enumeration as in bmd_cube_neck_dd_levels.gp: rows sum_q t'_(p+q) eps^(p+q) Delta_j psi_q, levels by
\\ Cauchy-Binet per group.  The row identity holds for every sequence t', so the level sums S_L(beta, t') are
\\ polynomials in an arbitrary sequence t'.  Questions:
\\ (a) does the cancellation of the level sums below 2E survive a generic sequence t' (random values mod q) in place
\\     of t'_m = binom(-5/2, m+n-w), or does it need the binomial structure of tau?
\\ (b) at block size one the leading coefficient is Hankel(t') * G_c(beta), a product.  At block size two, is the
\\     leading coefficient C(beta, t') a product f(beta) g(t')?  Test: the matrix [C(beta_i, t'_j)] over three
\\     random beta and three random t' has rank one exactly when (on these samples) C separates.
\\ Modulo 2^61 - 1.  Cases (e, l, w, c) = (1,2,2,3), (1,2,2,4), (1,3,2,4), (1,3,2,5).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q0 = 2^61 - 1;
assignE(l, w, cc) = my(rows = vecsort(concat(vector(w, r, vector(l, s, r - 1)))), top = rows[#rows - cc + 1..#rows]); sum(i = 1, cc, max(0, i - top[i] - 1));
ddE(l, w, cc) = my(caps = vecsort(concat(vector(l, j, vector(w, r, r - j + 1)))), top = caps[#caps - cc + 1..#caps]); sum(i = 1, cc, max(0, i - top[i]));
\\ level sums S_0..S_(2E) for one beta and a list of t' sequences
levels(e, l, w, cc, bet, tps) = {
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
\\ (c) identify g(t'): at one beta, compare g(t'_j)/g(t'_1) over four random t' with products of Hankel minors
\\     h(k, a) = det[t'_(a+i+j)]_(i,j<k), sum of sizes k = l*w, shifts 1 <= a <= 12, of the same weight
\\     (t'_x -> mu^x t'_x) as g; report every matching product.
hk(t, k, a) = matdet(matrix(k, k, i, j, t[a + i + j - 2]));
identify(e, l, w, cc) = {
  my(n = 4 * e, E = assignE(l, w, cc), len = 2 * (w + 2 * E) + 40);
  my(ts = vector(4, t, vector(len, m, Mod(1 + random(q0 - 1), q0))), bet = vector(l, s, Mod(1 + random(q0 - 1), q0)));
  my(mu = Mod(3, q0), tsc = vector(len, m, mu^m * ts[1][m]));
  my(S = levels(e, l, w, cc, bet, concat(ts, [tsc]))[2], g = vector(5, t, S[t, 2 * E + 1]));
  my(wt = -1); for (x = 0, 400, if (mu^x * g[1] == g[5], wt = x; break));
  my(found = List(), D = l * w);
  \\ multisets of (k, a): partitions of D into parts k with shifts a
  my(parts = List()); forpart(pp = D, listput(parts, Vec(pp)));
  foreach (parts, pp, my(m = #pp);
    forvec(av = vector(m, i, [1, 12]),
      if (sum(i = 1, m, pp[i] * av[i] + pp[i] * (pp[i] - 1)) == wt,
        my(ok = 1, c1 = prod(i = 1, m, hk(ts[1], pp[i], av[i])));
        if (c1 != 0, for (t = 2, 4, if (prod(i = 1, m, hk(ts[t], pp[i], av[i])) * g[1] != c1 * g[t], ok = 0; break)), ok = 0);
        if (ok, listput(found, [pp, av]))), 1));
  emit(Str("  identify e=", e, " l=", l, " w=", w, " c=", cc, ": weight of g ", wt, "; matching products [sizes, shifts]: ", Vec(found)));
}
main() = {
  setrand(20260930);
  my(cases = if (getenv("CASES"), eval(getenv("CASES")), [[1, 2, 2, 3], [1, 2, 2, 4], [1, 3, 2, 4], [1, 3, 2, 5]]));
  foreach (cases, cs,
    my(e = cs[1], l = cs[2], w = cs[3], cc = cs[4], n = 4 * e, E = assignE(l, w, cc), Ep = ddE(l, w, cc), len = 2 * (w + 2 * E) + 8);
    my(tbin = vector(len, m, Mod(binomial(-5/2, m + n - w), q0)));
    \\ TPRANK = r: random t' of linear complexity r (power sums sum_(i<=r) a_i lambda_i^x), for the rank test of
    \\ the second route review (bmd-20260930-zo); the prediction is C = 0 at level 2E when r < c.
    my(rk = if (getenv("TPRANK"), eval(getenv("TPRANK")), 0));
    my(trnd = vector(3, t, if (rk, my(a = vector(rk, i, Mod(1 + random(q0 - 1), q0)), lm = vector(rk, i, Mod(1 + random(q0 - 1), q0))); vector(len, m, sum(i = 1, rk, a[i] * lm[i]^m)), vector(len, m, Mod(1 + random(q0 - 1), q0)))));
    if (rk, emit(Str("  (random t' of linear complexity ", rk, ")")));
    my(tps = concat([tbin], trnd));
    my(C = matrix(3, 3), firsts = List());
    for (i = 1, 3,
      my(bet = vector(l, s, Mod(1 + random(q0 - 1), q0)), r = levels(e, l, w, cc, bet, tps), S = r[2]);
      for (t = 1, 4, listput(firsts, firstnz(S[t, ])));
      for (t = 1, 3, C[i, t] = S[t + 1, 2 * E + 1]));
    my(fb = vector(3, i, firsts[4 * (i - 1) + 1]), fr = vector(9, i, firsts[4 * ((i - 1) \ 3) + 2 + (i - 1) % 3]));
    emit(Str("e=", e, " l=", l, " w=", w, " c=", cc, ": E'=", Ep, " 2E=", 2 * E,
      "; first nonzero level, binomial t': ", fb, "; random t': ", fr,
      "; rank of [C(beta_i, t'_j)] at level 2E: ", matrank(C)));
    identify(e, l, w, cc));
  \\ control: block size one, where g = t'_1^(l-c) * det[t'_(sigma+j)] is proved
  identify(1, 3, 1, 2);
}
default(parisizemax, 2000000000);
main();
quit
