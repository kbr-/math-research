\\ Schur-Cohn reflection ratios of the tie stability polynomial (6 October 2026; cycle bmd-20261006-s).  For m = 2..5,
\\ f~ = Delta_(2m) + Delta_(2m+1) (the last two maximal minors of the width-(2m+2) tie window of
\\ research/tools/bmd_tie_window.gp), stripped of c and c-1; prints f~, f~(1), f~(-1) and the ratios a0/an of the exact
\\ Schur-Cohn recursion, testing for an orthogonal-polynomial (Verblunsky-type) closed form.
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
strip01(f) = { while (subst(f, 'c, 0) == 0, f /= 'c); while (subst(f, 'c, 1) == 0, f /= ('c - 1)); f / content(f); }
{
for (m = 2, 5,
  my(Wp = winmat(m, 2 * m + 2), f = strip01(matdet(vecextract(Wp, "..", setminus([1 .. 2 * m + 2], [2 * m + 1]))) + matdet(vecextract(Wp, "..", setminus([1 .. 2 * m + 2], [2 * m + 2])))), rc = List());
  print("m=", m, " f~ = ", f);
  print("  f~(1) = ", factor(subst(f, 'c, 1)), "   f~(-1) = ", if (subst(f, 'c, -1), factor(subst(f, 'c, -1)), 0));
  while (poldegree(f) > 0, my(a0 = polcoef(f, 0), an = pollead(f)); listput(rc, a0 / an); f = (an * f - a0 * polrecip(f)) / 'c; f = f / content(f));
  print("  reflection ratios a0/an: ", Vec(rc)));
}
quit;
