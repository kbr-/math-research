\\ Factored maximal minors of the reduced triple window (cycle bmd-20261009-ca, 9 October 2026).
\\ Question (route to conj:cube-triple-window-full-rank): with a = (x, y, 1) symbolic, does some 3 x 3 minor of U_3
\\ (closed form of lem:cube-level-window-gegenbauer-form) factor into x, y, x-1, y-1, x-y only (times a constant)? Such a
\\ minor proves rank 3 off those loci. Prints, per m = 2..6 and per column triple, the non-excluded part's total degree.
OUT = "research/results/bmd-20261009-ca/triple-window-minors.txt";
default(parisizemax, 4 * 10^9);
lam = 3/2;
rq(j, k) = prod(i = 1, k, i / (i + lam - j));
cc(n) = binomial(-lam, n);
\\ remove factors x, y, x-1, y-1, x-y (and constants) from a bivariate polynomial
exclpart(f) = { if (f == 0, return(0)); my(fa = factor(f), g = 1);
  for (r = 1, #fa~, my(u = fa[r, 1]); if (!(u == 'x || u == 'y || u == 'x - 1 || u == 'y - 1 || u == 'x - 'y || u == 'y - 'x || poldegree(u, 'x) + poldegree(u, 'y) == 0), g *= u^fa[r, 2]));
  g; }
{
  for (m = 2, 6, my(a = ['x, 'y, 1], d = m * (m - 1) / 2, N0 = d + m, U = matrix(3, 5));
    my(prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]]);
    for (r = 1, 3, my([i, j, k] = prs[r], top = N0 + 4);
      my(e = vector(top + 1, n, sum(t = 0, n - 1, cc(t) * cc(n - 1 - t) * a[i]^t * a[j]^(n - 1 - t))));
      for (col = 1, 5, my(n = N0 + col - 1);
        U[r, col] = sum(l = 0, m, binomial(m, l) * a[k]^l * if (n - l >= 0, rq(-m, n - l) * e[n - l + 1], 0))));
    my(res = List());
    forsubset([5, 3], S, my(Sv = Vec(S), D = matdet(matrix(3, 3, r, t, U[r, Sv[t]])), co = exclpart(D));
      listput(res, [Sv, if (co == 0, "zero", poldegree(subst(subst(co, 'x, 't * 'x), 'y, 't * 'y), 't))]));
    write(OUT, "m = ", m, ": [columns, total degree of the non-excluded part] = ", Vec(res)));
}
