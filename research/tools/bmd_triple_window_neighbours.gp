\\ Hermite–Padé neighbour determinants of the triple window (cycle bmd-20261009-cj, 9 October 2026).
\\ The window W_3 is the type-I Hermite–Padé problem for the seven functions 1, w_i^-3 = (1+a_i T)^-3/2, (w_i w_j)^-3
\\ with multi-index n = (d; m, m, m; 1, 1, 1), d = C(m, 2) (lem:cube-triple-window-elliptic-form): it has full rank iff
\\ no nonzero form of index n has order >= |n| + 2. Such a form has index n'' and order >= |n''| for every n'' >= n with
\\ |n''| <= |n| + 2, so it makes the square determinant H(n'') vanish at all 36 such n''. Hence if one H(n'') has no
\\ zero off the excluded locus x y (x-1)(y-1)(x-y) (a = (x, y, 1)), the window has full rank everywhere.
\\ H(n''): rows T^r g for r < n''_g over the six non-polynomial functions g, on columns d''..|n''|-1 (the polynomial
\\ rows are unit vectors and drop out). For m = 2, 3 print, for each n'', the factorization pattern of H(n'') over Q:
\\ (degree, multiplicity, excluded?) of each irreducible factor, and flag n'' whose H is supported on the excluded locus.
OUT = "research/results/bmd-20261009-cj/triple-window-neighbours.txt";
default(parisizemax, 4 * 10^9);
cc(n) = binomial(-3/2, n);
totdeg(f) = poldegree(subst(subst(f, 'x, 's * 'x), 'y, 's * 'y), 's);
{
  my(a = ['x, 'y, 1], prs = [[1, 2], [1, 3], [2, 3]], excl = ['x, 'y, 'x - 1, 'y - 1, 'x - 'y]);
  foreach([2, 3], m,
    my(d = m * (m - 1) / 2, base = [d, m, m, m, 1, 1, 1], dirs = List([vector(7)]));
    for (i = 1, 7, listput(dirs, vector(7, k, k == i)));
    for (i = 1, 7, for (j = i, 7, listput(dirs, vector(7, k, (k == i) + (k == j)))));
    foreach(dirs, e, my(nn = base + e, tot = vecsum(nn), dd = nn[1], top = tot - 1, rows = List());
      \\ coefficient sequences of the six functions up to T^top
      my(seq = vector(6));
      for (i = 1, 3, seq[i] = vector(top + 1, c, cc(c - 1) * a[i]^(c - 1)));
      for (p = 1, 3, my([i, j] = prs[p]); seq[3 + p] = vector(top + 1, c, sum(t = 0, c - 1, cc(t) * cc(c - 1 - t) * a[i]^t * a[j]^(c - 1 - t))));
      for (g = 1, 6, for (r = 0, nn[g + 1] - 1, listput(rows, vector(tot - dd, col, my(c = dd + col - 1 - r); if (c >= 0, seq[g][c + 1], 0)))));
      my(M = matrix(#rows, tot - dd, i, j, rows[i][j]), D = matdet(M));
      if (D == 0, write(OUT, "m = ", m, " n'' = ", nn, ": H = 0 identically"); next);
      my(F = factor(D), pat = List(), onlyexcl = 1);
      for (k = 1, #F~, my(f = F[k, 1]); if (poldegree(f, 'x) + poldegree(f, 'y) == 0, next);
        my(isx = 0); foreach(excl, q, if (f / q == 1 || f / q == -1, isx = 1));
        if (!isx, onlyexcl = 0);
        listput(pat, [totdeg(f), F[k, 2], isx]));
      write(OUT, "m = ", m, " n'' = ", nn, ": size ", #rows, ", factors (deg, mult, excluded) ", Vec(pat), if (onlyexcl, "  <-- excluded only", ""))));
}
