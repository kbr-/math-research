\\ Exchange test of the peeling neck windows (30 September 2026; cycle bmd-20260930-zd, route review).
\\ The valuations omg(S) = val det C[:, S] of the Plucker coordinates of the neck model (rows g_d and cleared
\\ f_i, as in bmd_cube_peeling_neck_windows.gp, block size 4) form a valuated matroid (Dress-Wenzel), and so does
\\ omega + alpha * sum S.  By Murota's local optimality theorem a basis minimizes it iff no single exchange
\\ S - i + j is smaller, and the minimizers form the bases of a matroid, connected under single exchanges.
\\ Test: at each breakpoint alpha_c the only exchange neighbours of W_c attaining the minimum are W_(c+1)
\\ (and of W_(c+1) only W_c), and at the midpoints between breakpoints (and in (0, alpha_4), (alpha_(K-1), 1))
\\ every exchange neighbour of the window is strictly larger.  Exchanges j range over [-(K+8), M+K+8];
\\ modulo 2^61 - 1 at one beta, eps-truncation mmax (a valuation above mmax is reported as such).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 2^61 - 1;
build(e, l, mmax) = {
  my(n = 4 * e, M = n * l, K = 4 * l, Y = M + K + mmax + 8, lam = -7/2);
  my(bet = vector(l, s, Mod([2, -3, 5, -7, 11][s], q) / 3));
  my(phi = vector(l, s, vector(Y, r, Mod(binomial(lam, r - 1), q) * bet[s]^(r - 1))));
  my(A = matrix(M, Y, a, b, 0), row = 0);
  for (s = 1, l, for (i = 0, n - 1, row++; for (r = 1, Y - i, A[row, r + i] = phi[s][r])));
  my(G = A[, 1..M]^(-1) * A);
  my(t = vector(mmax, m, Mod(binomial(-5/2, m), q)), W = Y + mmax, F = matrix(K, W, a, b, 0), fr = 0);
  for (s = 1, l, for (p = 0, 3, fr++;
    my(h = vector(Y, r, if (r - 1 >= n - 4 + p, phi[s][r - (n - 4 + p)], 0)));
    for (m = 1, mmax, for (r = 1, Y, if (h[r] != 0, F[fr, r - 1 - m + mmax + 1] += t[m] * 'x^m * h[r])))));
  for (i = 1, K, for (d = 0, M - 1, my(v = F[i, d + mmax + 1]);
    if (v != 0, for (r = 1, Y, if (G[d + 1, r] != 0, F[i, r + mmax] -= v * G[d + 1, r])))));
  \\ full matrix: g rows (zero on negative columns) and f rows; column index col + mmax + 1
  my(C = matrix(M + K, W, a, b, 0));
  for (d = 1, M, for (r = 1, Y, C[d, r + mmax] = G[d, r]));
  for (i = 1, K, for (b = 1, W, C[M + i, b] = F[i, b]));
  [C, M, K, mmax];
}
omg(D, S) = my(C = D[1], mm = D[4], dt = matdet(matrix(#S, #S, a, b, C[a, S[b] + mm + 1]))); if (dt == 0, oo, valuation(lift(dt), 'x));
win(M, K, cc) = concat([vector(cc, j, -cc - 1 + j), vector(M, j, j - 1), vector(K - cc, j, M + j - 1)]);
main() = {
  my(e = 1, l = 2, mmax = if (getenv("MMAX"), eval(getenv("MMAX")), 140));
  if (getenv("EL"), my(el = eval(getenv("EL"))); e = el[1]; l = el[2]);
  my(D = build(e, l, mmax), M = D[2], K = D[3], L = M + K, bad = 0);
  my(f = vector(K - 3, i, omg(D, win(M, K, i + 3))), br = vector(K - 4, i, (f[i + 1] - f[i]) / L));
  emit(Str("e=", e, " l=", l, ": window valuations ", f, ", breakpoints ", br));
  my(lo = -(K + 8), hi = M + K + 8);
  for (cc = 4, K,
    my(S = win(M, K, cc), vS = f[cc - 3], nb = List());
    for (i = 1, #S, for (j = lo, hi, if (!setsearch(Set(S), j),
      my(T = vecsort(concat(vector(#S - 1, k, if (k < i, S[k], S[k + 1])), [j])));
      listput(nb, [T, omg(D, T)]))));
    \\ test points: alpha in the open interval of W_c, and the breakpoint alpha_c (if c < K)
    my(a0 = if (cc == 4, 0, br[cc - 4]), a1 = if (cc == K, 1, br[cc - 3]), mid = (a0 + a1) / 2);
    my(wS = vS + mid * vecsum(S), fails = 0, ties = List());
    foreach (nb, t, if (t[2] != oo && t[2] + mid * vecsum(t[1]) <= wS, fails++));
    if (cc < K, my(wb = vS + a1 * vecsum(S));
      foreach (nb, t, if (t[2] != oo && t[2] + a1 * vecsum(t[1]) < wb, fails++);
        if (t[2] != oo && t[2] + a1 * vecsum(t[1]) == wb, listput(ties, t[1]))));
    my(okties = (cc == K) || (#ties == 1 && ties[1] == win(M, K, cc + 1)));
    \\ the other side: at the left breakpoint alpha_(c-1) the only tie is W_(c-1)
    my(lties = List(), oklt = 1);
    if (cc > 4, my(wl = vS + a0 * vecsum(S));
      foreach (nb, t, if (t[2] != oo && t[2] + a0 * vecsum(t[1]) < wl, fails++);
        if (t[2] != oo && t[2] + a0 * vecsum(t[1]) == wl, listput(lties, t[1])));
      oklt = (#lties == 1 && lties[1] == win(M, K, cc - 1)));
    if (fails || !okties || !oklt, bad++);
    emit(Str("  window c=", cc, ": ", #nb, " exchange neighbours; strictly larger at alpha = ", mid, ": ", if (fails, "NO", "yes"),
      if (cc < K, Str("; ties at alpha_c = ", a1, ": ", #ties, if (okties, " (only W_(c+1))", " (UNEXPECTED)")), ""),
      if (cc > 4, Str("; ties at alpha_(c-1) = ", a0, ": ", #lties, if (oklt, " (only W_(c-1))", " (UNEXPECTED)")), ""))));
  emit(Str("failures: ", bad));
}
default(parisizemax, 4000000000);
main();
