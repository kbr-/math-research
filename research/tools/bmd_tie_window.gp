\\ Tie window matrices (6 October 2026; cycle bmd-20261006-n).  Reduction: at a top tie (roots c and 1 above a deep
\\ cluster of m roots), the limit rows outside the deep cluster's span e_0..e_(R''-1), R'' = binom(m,2), are the series
\\ T^n (1+cT)^(-3/2), T^n (1+T)^(-3/2) (0 <= n < m) and ((1+cT)(1+T))^(-3/2).  On the square window of columns
\\ R''..R''+2m their determinant L(c) is the tie leading coefficient (compare research/results/bmd-20261006-k/); on the
\\ contact window R''..R''+2m+2 the tested statement is: the (2m+1) x (2m+3) matrix has full rank for every c not 0, 1,
\\ i.e. the gcd of its maximal minors has no root off c = 0, 1.  Env MS (list of m), OUT.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
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
strip01(f) = { if (f == 0, return(0)); while (subst(f, 'c, 0) == 0, f /= 'c); while (subst(f, 'c, 1) == 0, f /= ('c - 1)); f / content(f); }
{
foreach(eval(getenv("MS")), m,
  my(M = winmat(m, 2 * m + 1), L = strip01(matdet(M)));
  emit(Str("m=", m, " (N=", m + 2, ", top tie): square-window L(c) off c=0,1 factors: ", factor(L)[, 1]~));
  my(W = winmat(m, 2 * m + 3), g = 0);
  forsubset([2 * m + 3, 2 * m + 1], S, g = gcd(g, matdet(vecextract(W, "..", Vec(S)))));
  g = strip01(g);
  emit(Str("  contact window: gcd of maximal minors off c=0,1: ", g, if (poldegree(g) == 0, "  -> full rank for every c != 0,1", "  -> DEFECT")));
  \\ PURE=1 (cycle bmd-20261006-o): list the maximal minors that are c^a (c-1)^b times a constant, i.e. never vanish
  \\ off c = 0, 1 by themselves; such a minor would prove full rank at that m alone.
  if (getenv("PURE") == "1",
    my(pure = List());
    forsubset([2 * m + 3, 2 * m + 1], S, my(d = matdet(vecextract(W, "..", Vec(S)))); if (d != 0 && poldegree(strip01(d)) == 0,
      listput(pure, setminus([1 .. 2 * m + 3], Vec(S)) - [1, 1])));
    emit(Str("  pure minors (dropped window columns, 0-based): ", Vec(pure))));
  \\ SIGNS=1 (cycle bmd-20261006-p): signs of all maximal minors at c = 2, 3, 1/2 (a total-positivity test).
  if (getenv("SIGNS") == "1",
    foreach([2, 3, 1/2], c0, my(sg = List());
      forsubset([2 * m + 3, 2 * m + 1], S, listput(sg, sign(subst(matdet(vecextract(W, "..", Vec(S))), 'c, c0))));
      emit(Str("  c=", c0, ": minors positive ", #select(x -> x > 0, Vec(sg)), ", negative ", #select(x -> x < 0, Vec(sg)), ", zero ", #select(x -> x == 0, Vec(sg))))));
);
}
quit;
