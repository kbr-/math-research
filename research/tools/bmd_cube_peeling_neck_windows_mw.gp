\\ Peeling neck windows with a general block size (30 September 2026; cycle bmd-20260930-zd, route review).
\\ Same model as bmd_cube_peeling_neck_windows.gp, with the block size 4 of W replaced by w:
\\   U = sum_s Pol_(<n) phi_s, W = y^(n-w) sum_s Pol_(<w) phi_s, tau = (1 + eps/y)^(-5/2), n = 4e >= w,
\\   M = nl, K = wl, windows W_c for w <= c <= K.  (w = 4 is the peeling neck; other w test the mechanism.)
\\ Prediction tested (stated before the run): f(c) = l w n + 2 E_(l,w)(c), where E_(l,w)(c) pairs the negative
\\ columns 1..c in increasing order with the c largest pole indices r in {0..w-1} (each taken l times) and adds
\\ max(0, sigma - r - 1); for w = 4 this is the conjectured formula 16el + 2 sum nu_j.
\\ Exactness as before: tau truncated at eps^mmax, valuations <= mmax exact for the truncation; modulo 2^61 - 1 at
\\ one beta = (2, -3, 5, -7, 11, -13)/3, so upper bounds for the generic valuations.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 2^61 - 1;
assignE(l, w, cc) = {
  my(rows = vecsort(concat(vector(w, r, vector(l, s, r - 1)))), top = rows[#rows - cc + 1..#rows]);
  sum(i = 1, cc, max(0, i - top[i] - 1));
}
neck(e, l, w, mmax) = {
  my(n = 4 * e, M = n * l, K = w * l, Y = M + K + mmax + 8, lam = -7/2, bad = 0);
  if (w > n, error("need w <= n"));
  my(bet = vector(l, s, Mod([2, -3, 5, -7, 11, -13][s], q) / 3));
  my(phi = vector(l, s, vector(Y, r, Mod(binomial(lam, r - 1), q) * bet[s]^(r - 1))));
  my(A = matrix(M, Y, a, b, 0), row = 0);
  for (s = 1, l, for (i = 0, n - 1, row++; for (r = 1, Y - i, A[row, r + i] = phi[s][r])));
  my(A0 = A[, 1..M]);
  if (matrank(A0) < M, error("U not ordinary at 0"));
  my(G = A0^(-1) * A);
  my(t = vector(mmax, m, Mod(binomial(-5/2, m), q)), W = Y + mmax, F = matrix(K, W, a, b, 0), fr = 0);
  for (s = 1, l, for (p = 0, w - 1, fr++;
    my(h = vector(Y, r, if (r - 1 >= n - w + p, phi[s][r - (n - w + p)], 0)));
    for (m = 1, mmax, for (r = 1, Y, if (h[r] != 0, F[fr, r - 1 - m + mmax + 1] += t[m] * 'x^m * h[r])))));
  for (i = 1, K, for (d = 0, M - 1, my(v = F[i, d + mmax + 1]);
    if (v != 0, for (r = 1, Y, if (G[d + 1, r] != 0, F[i, r + mmax] -= v * G[d + 1, r])))));
  my(res = List());
  for (cc = w, K,
    my(cols = concat(vector(cc, j, -j + mmax + 1), vector(K - cc, j, M + j - 1 + mmax + 1)));
    my(dt = matdet(matrix(K, K, a, b, F[a, cols[b]])), v = if (dt == 0, oo, valuation(lift(dt), 'x)));
    my(pred = l * w * n + 2 * assignE(l, w, cc));
    if (v != pred || v > mmax, bad++);
    listput(res, v);
    emit(Str("e=", e, " l=", l, " w=", w, " window c=", cc, ": val ", v, if (v != oo && v <= mmax, " (exact)", " (NOT EXACT)"),
      ", predicted ", pred, if (v == pred, "", " MISMATCH"))));
  my(df = vector(#res - 1, j, res[j + 1] - res[j]));
  emit(Str("  e=", e, " l=", l, " w=", w, ": increments ", df, "; convex: ",
    if (#df <= 1 || vecmin(vector(#df - 1, j, df[j + 1] - df[j])) > 0, "strictly", "NO"),
    "; mismatches or inexact: ", bad));
}
main() = {
  my(cases = if (getenv("CASES"), eval(getenv("CASES")), [[1, 2, 4]]), mm = if (getenv("MMAX"), eval(getenv("MMAX")), 80));
  foreach (cases, cs, neck(cs[1], cs[2], cs[3], mm));
}
default(parisizemax, 4000000000);
main();
