\\ Second minor of the tie window at Gegenbauer zeros (cycle bmd-20261009-bt, 9 October 2026).
\\ Tested statement: for the tie contact window W(c) ((2m+1) x (2m+3), columns d..d+2m+2, d = binom(m,2); rows as in
\\ bmd_tie_window.gp), the square minor L_m (columns d..d+2m) is proportional to t_d (thm:cube-tie-taylor-dominance), and
\\ the next minor N_m (columns d..d+2m-1, d+2m+1) has no common zero with t_d off c in {0, 1}. Then at every Gegenbauer
\\ zero c0 the row space of W(c0) has pivot set {d..d+2m-1, d+2m+1}, weight 1. m = 2..7.
OUT = "research/results/bmd-20261009-bt/tie-window-second-minor.txt";
default(parisizemax, 2 * 10^9);
b(k) = if (k < 0, 0, binomial(-3/2, k));
row_t(t, n, cols) = vector(#cols, j, b(cols[j] - n) * t^(cols[j] - n));
row_top(cols) = vector(#cols, j, sum(i = 0, cols[j], b(i) * b(cols[j] - i) * 'c^i));
winmat(m, w) = {
  my(R2 = m * (m - 1) / 2, cols = vector(w, j, R2 + j - 1), rows = List());
  for (n = 0, m - 1, listput(rows, row_t('c, n, cols)));
  for (n = 0, m - 1, listput(rows, row_t(1, n, cols)));
  listput(rows, row_top(cols));
  matrix(#rows, w, i, j, rows[i][j]);
}
tco(d) = sum(i = 0, d, binomial(-3/2, i) * binomial(-3/2, d - i) * 'c^i);
strip(f) = { my(g = f); while (subst(g, 'c, 0) == 0 && g != 0, g = g / 'c); while (subst(g, 'c, 1) == 0 && g != 0, g = g / ('c - 1)); g; }
{
  for (m = 2, 7, my(d = m * (m - 1) / 2, W = winmat(m, 2 * m + 3), n = 2 * m + 1);
    my(L = matdet(matrix(n, n, i, j, W[i, j])), cs = concat([1 .. 2 * m], [2 * m + 2]), N = matdet(matrix(n, n, i, j, W[i, cs[j]])));
    my(t = tco(d), Ls = strip(L), Ns = strip(N));
    my(prop = (Ls != 0) && (poldegree(gcd(Ls, t)) == poldegree(t)) && (poldegree(Ls) == poldegree(t)));
    my(g = gcd(Ns, t));
    write(OUT, "m = ", m, ", d = ", d, ": square minor (stripped of c and c-1) proportional to t_d: ", prop,
          "; gcd(next minor, t_d) has degree ", poldegree(g), if (poldegree(g) > 0, Str(" = ", g), " (no common zero)")));
}
