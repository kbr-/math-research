\\ Cauchy-Binet structure of the peeling neck windows (30 September 2026; cycle bmd-20260930-zf).
\\ Modulo U, the neck rows are f_(s,p) = eps^(n-w) sum_(q>=1) t'_(p+q) eps^(p+q) psi_(s,q), t'_m = binom(-5/2, m+n-w),
\\ psi_(s,q) = y^(-q) phi_s reduced modulo U (middle columns cleared).  By Cauchy-Binet,
\\   det Z[:, W_c] = eps^(K(n-w) + l w(w-1)/2) sum_Q eps^(sum Q) prod_s det T'[:, Q_s] * Psi(Q, W_c),
\\ over choices Q = (Q_1..Q_l) of w-sets of pole orders, with Psi an eps-free minor of the psi rows.
\\ Question: for each window c, which Q have Psi(Q, W_c) != 0 at the smallest sum Q, what is that level,
\\ and does the weighted sum at that level vanish?  (Observed: f(c) - lwn = 2 E(c), twice the assignment count.)
\\ Cases: (e, l, w) with n = 4e; q ranges over 1..qmax; modulo 2^61 - 1, beta = (2, -3, 5)/3.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q0 = 2^61 - 1;
run(e, l, w, qmax, extra) = {
  my(n = 4 * e, M = n * l, K = w * l, Y = M + K + qmax + 8, lam = -7/2);
  my(bet = vector(l, s, Mod([2, -3, 5][s], q0) / 3));
  my(phi = vector(l, s, vector(Y, r, Mod(binomial(lam, r - 1), q0) * bet[s]^(r - 1))));
  my(A = matrix(M, Y, a, b, 0), row = 0);
  for (s = 1, l, for (i = 0, n - 1, row++; for (r = 1, Y - i, A[row, r + i] = phi[s][r])));
  my(G = A[, 1..M]^(-1) * A);
  \\ psi rows: index (s, q); columns -qmax..Y-1 at index col + qmax + 1
  my(W = Y + qmax, P = vector(l, s, vector(qmax, q, my(v = vector(W));
    for (r = 1, Y, my(col = r - 1 - q); if (col >= -qmax, v[col + qmax + 1] += phi[s][r]));
    for (d = 0, M - 1, my(x = v[d + qmax + 1]); if (x != 0, for (r = 1, Y, v[r + qmax] -= x * G[d + 1, r])));
    v)));
  my(tp = vector(2 * qmax + 8, m, Mod(binomial(-5/2, m + n - w), q0)));
  my(subsets = select(S -> #S == w, apply(v -> Vec(v), forsubset_list(qmax, w))));
  for (cc = w, K,
    my(cols = concat(vector(cc, j, -j + qmax + 1), vector(K - cc, j, M + j - 1 + qmax + 1)));
    my(base = l * w * (w + 1) / 2, best = oo, hits = List(), wsum = Map());
    \\ enumerate tuples of subsets with sum Q - base <= extra
    my(cand = select(S -> vecsum(S) - w * (w + 1) / 2 <= extra, subsets));
    forvec(ix = vector(l, s, [1, #cand]),
      my(Qs = vector(l, s, cand[ix[s]]), lev = sum(s = 1, l, vecsum(Qs[s])) - base);
      if (lev <= extra && lev <= best,
        my(Mx = matrix(K, K, a, b, 0), rr = 0);
        for (s = 1, l, foreach (Qs[s], qq, rr++; for (b = 1, K, Mx[rr, b] = P[s][qq][cols[b]])));
        my(d = matdet(Mx));
        if (d != 0,
          my(wt = d * prod(s = 1, l, matdet(matrix(w, w, pp, jj, tp[pp - 1 + Qs[s][jj]]))));
          if (lev < best, best = lev; hits = List(); wsum = Map());
          listput(hits, Qs);
          my(old = 0); mapisdefined(wsum, lev, &old); mapput(wsum, lev, old + wt))));
    my(tot = 0); if (best != oo, mapisdefined(wsum, best, &tot));
    emit(Str("e=", e, " l=", l, " w=", w, " c=", cc, ": minimal level ", best, " (predicted 2E = ", 2 * assignE(l, w, cc), "), ",
      #hits, " nonzero Q there, weighted sum ", if (tot != 0, "nonzero", "ZERO"), "; examples ", Vec(hits)[1..min(#hits, 3)])));
}
assignE(l, w, cc) = my(rows = vecsort(concat(vector(w, r, vector(l, s, r - 1)))), top = rows[#rows - cc + 1..#rows]); sum(i = 1, cc, max(0, i - top[i] - 1));
forsubset_list(N, k) = my(L = List()); forsubset([N, k], v, listput(L, v)); L;
main() = {
  my(cases = if (getenv("CASES"), eval(getenv("CASES")), [[1, 2, 2]]));
  foreach (cases, cs, run(cs[1], cs[2], cs[3], cs[4], cs[5]));
}
default(parisizemax, 2000000000);
main();
quit
