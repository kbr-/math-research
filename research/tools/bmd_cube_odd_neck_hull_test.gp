\\ Odd neck hull test (3 October 2026; cycle bmd-20261003-zb).
\\ Falsification test for the two-minimizer condition of the odd neck model (bmd_cube_odd_neck_windows.gp model):
\\ the full L x L matrix (rows: U basis y^(off+i) phi_s uncleared, then the K rows (tau - 1) h), columns = Laurent
\\ exponents.  For each breakpoint c (4 <= c < K) with alpha_c = (f(c+1) - f(c)) / L, and every L-set S obtained from
\\ W_c or W_(c+1) by one exchange (remove one exponent, add one exponent in [-K-2, M+K+2]), check
\\   Phi(S) = val det[:, S] + alpha_c * sum S  >  Phi(W_c) = Phi(W_(c+1)).
\\ Prediction (hull theorem draft): no violation and no tie.  Arithmetic modulo 2^61 - 1; tau truncated at eps^mmax
\\ (a valuation above mmax is reported as a lower bound and counted as passing only if the bound already exceeds).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 2^61 - 1;
run(e, l, mmax) = {
  my(n = 4 * e, M = n * l + 2 * e, K = 4 * l + 2, L = M + K, lo = -K - 2, hi = M + K + 2, Y = hi + 1);
  my(bet = vector(l + 1, s, Mod([2, -3, 5, -7, 11, 13][s], q) / 3), ex = concat(vector(l, s, -7/2), [-3/2]));
  my(phi = vector(l + 1, s, vector(Y + mmax + 1, r, Mod(binomial(ex[s], r - 1), q) * bet[s]^(r - 1))));
  \\ column index for exponent x: x - lo + 1
  my(nc = hi - lo + 1, A = matrix(L, nc, a, b, 0), row = 0);
  my(ub = concat(vector(l, s, [s, 0, n]), [[l + 1, 2 * e - 2, 2 * e]]));
  foreach (ub, bl, for (i = 0, bl[3] - 1, row++; for (x = 0, hi, my(r = x - bl[2] - i); if (r >= 0, A[row, x - lo + 1] = phi[bl[1]][r + 1]))));
  my(t = vector(mmax, m, Mod(binomial(-5/2, m), q)), wb = concat(vector(l, s, [s, 4]), [[l + 1, 2]]));
  foreach (wb, bl, for (p = 0, bl[2] - 1, row++;
    for (m = 1, mmax, for (x = lo, hi, my(r = x + m - (n - 4 + p)); if (r >= 0, A[row, x - lo + 1] += t[m] * 'x^m * phi[bl[1]][r + 1])))));
  my(val = S -> my(Z = matrix(L, L, a, b, A[a, S[b] - lo + 1]), d = matdet(Z)); if (d == 0, oo, valuation(lift(d), 'x)));
  my(W = c -> vector(L, j, j - 1 - c));
  my(fv = vector(K, c, if (c >= 4, val(W(c)), 0)), bad = 0, ties = 0, tested = 0, inexact = 0);
  for (c = 4, K - 1,
    my(al = (fv[c + 1] - fv[c]) / L, base = fv[c] + al * vecsum(W(c)));
    foreach ([W(c), W(c + 1)], S0,
      for (i = 1, L, for (x = lo, hi, if (!setsearch(Set(S0), x),
        my(S = vecsort(concat(vector(L - 1, j, S0[j + (j >= i)]), [x])), v = if (S == W(c) || S == W(c + 1), oo, val(S)));
        tested++;
        if (v == oo, next);
        if (v > mmax, inexact++);
        my(ph = v + al * vecsum(S));
        if (ph < base, bad++; emit(Str("  VIOLATION e=", e, " l=", l, " c=", c, " S=", S, " val ", v)));
        if (ph == base, ties++; emit(Str("  TIE e=", e, " l=", l, " c=", c, " S=", S, " val ", v))))))));
  emit(Str("e=", e, " l=", l, " L=", L, " window vals ", fv[4..K], "; exchanges tested ", tested, ", violations ", bad,
    ", ties ", ties, ", valuations above truncation ", inexact));
}
main() = {
  my(cases = if (getenv("CASES"), eval(getenv("CASES")), [[1, 1], [2, 1], [1, 2]]), mm = if (getenv("MMAX"), eval(getenv("MMAX")), 100));
  foreach (cases, cs, run(cs[1], cs[2], mm));
}
default(parisizemax, 4000000000);
main();
