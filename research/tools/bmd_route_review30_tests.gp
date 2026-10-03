\\ Cheap tests of the route review of 9 October 2026 (cycle bmd-20261009-ck), on the Hermite–Padé table of the triple
\\ window (lem:cube-window-hermite-pade-frobenius), m = 2, n = (1; 2,2,2; 1,1,1), a = (x, y, 1).
\\ (a) Falsification probe: at the common zeros of H(n) and H(n + e0) off the excluded locus, how many of the 36
\\     neighbour determinants vanish (|H| < 1e-40 after normalizing by the coefficient size)? A rank drop needs all 36.
\\ (b) Lee–Yang probe: the zeros of H(n)(x, 2) in x and of H(n)(x, 2 + i): do they lie on one circle |x| = r, or on the
\\     real line? Print |x| and Im x of each zero.
OUT = "research/results/bmd-20261009-ck/route-review30-tests.txt";
default(parisizemax, 4 * 10^9);
default(realprecision, 120);
cc(n) = binomial(-3/2, n);
Hsym(N) = {
  my(a = ['x, 'y, 1], prs = [[1, 2], [1, 3], [2, 3]], tot = vecsum(N), dd = N[1], top = tot, seq = vector(6), rows = List());
  for (i = 1, 3, seq[i] = vector(top + 1, c, cc(c - 1) * a[i]^(c - 1)));
  for (p = 1, 3, my([i, j] = prs[p]); seq[3 + p] = vector(top + 1, c, sum(t = 0, c - 1, cc(t) * cc(c - 1 - t) * a[i]^t * a[j]^(c - 1 - t))));
  for (g = 1, 6, for (r = 0, N[g + 1] - 1, listput(rows, vector(tot - dd, col, my(c = dd + col - 1 - r); if (c >= 0, seq[g][c + 1], 0)))));
  matdet(matrix(#rows, tot - dd, i, j, rows[i][j]));
}
\\ strip the excluded factors x, y, x-1, y-1, x-y
stripx(D) = { while (subst(D, 'x, 0) == 0, D = D / 'x); while (subst(D, 'y, 0) == 0, D = D / 'y); while (subst(D, 'x, 1) == 0, D = D / ('x - 1)); while (subst(D, 'y, 1) == 0, D = D / ('y - 1)); while (subst(D, 'x, 'y) == 0, D = D / ('x - 'y)); D; }
{
  my(base = [1, 2, 2, 2, 1, 1, 1], dirs = List([vector(7)]), Hs = List());
  for (i = 1, 7, listput(dirs, vector(7, k, k == i)));
  for (i = 1, 7, for (j = i, 7, listput(dirs, vector(7, k, (k == i) + (k == j)))));
  foreach(dirs, e, listput(Hs, stripx(Hsym(base + e))));
  my(P = Hs[1], Q = Hs[2], R = polresultant(P, Q, 'y), rts = polroots(R), cnt = vector(37));
  write(OUT, "(a) resultant degree ", poldegree(R));
  foreach(rts, x0, my(py = subst(P, 'x, x0), ys = polroots(py));
    foreach(ys, y0, my(qv = abs(subst(subst(Q, 'x, x0), 'y, y0)) / normlp(Vec(subst(Q, 'x, x0))));
      if (qv > 1e-40, next);
      if (abs(x0) < 1e-30 || abs(y0) < 1e-30 || abs(x0 - 1) < 1e-30 || abs(y0 - 1) < 1e-30 || abs(x0 - y0) < 1e-30, next);
      my(z = 0);
      for (k = 1, 36, my(h = subst(Hs[k], 'x, x0), v = abs(subst(h, 'y, y0)) / max(1e-300, normlp(Vec(h)))); if (v < 1e-40, z++));
      cnt[z + 1]++));
  write(OUT, "(a) common zeros of H(n), H(n+e0): histogram of the number of the 36 neighbours vanishing (index = count+1): ", cnt);
  foreach([2, 2 + I], y0, my(rt = polroots(subst(P, 'y, y0)));
    write(OUT, "(b) H(n)(x, ", y0, "): ", #rt, " zeros; |x| = ", apply(z -> precision(abs(z), 5), rt), "; Im x = ", apply(z -> precision(imag(z), 5), rt)));
}
