\\ Export of the reduced triple window's maximal minors for exact elimination at a given m (cycle bmd-20261009-kfx,
\\ 9 October 2026; the construction of research/tools/bmd_triple_window_export.gp, parameterized). Writes OUT/triple-minors-mM.ms:
\\ msolve input over Q in x, y, t with the ten 3 x 3 minors of U_3(x, y, 1) (lem:cube-level-window-gegenbauer-form; nonzero
\\ row factors and the Gamma normalization removed, contents cleared) and the Rabinowitsch generator
\\ t*x*y*(x-1)*(y-1)*(x-y) - 1. The system is inconsistent (reduced Groebner basis {1}) iff the window has full rank at every
\\ admissible point (x, y) off the excluded locus, i.e. conj:cube-triple-window-full-rank holds at this m.
\\ Usage: env M=9 OUT=research/results/bmd-20261009-kfx gp -q bmd_triple_window_export_m.gp
default(parisizemax, 4 * 10^9);
lam = 3/2;
rq(j, k) = prod(i = 1, k, i / (i + lam - j));
cc(n) = binomial(-lam, n);
{
  my(m = eval(getenv("M")), outdir = getenv("OUT"));
  my(a = ['x, 'y, 1], d = m * (m - 1) / 2, N0 = d + m, U = matrix(3, 5), prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]]);
  for (r = 1, 3, my([i, j, k] = prs[r], top = N0 + 4);
    my(e = vector(top + 1, n, sum(t = 0, n - 1, cc(t) * cc(n - 1 - t) * a[i]^t * a[j]^(n - 1 - t))));
    for (col = 1, 5, my(n = N0 + col - 1);
      U[r, col] = sum(l = 0, m, binomial(m, l) * a[k]^l * if (n - l >= 0, rq(-m, n - l) * e[n - l + 1], 0))));
  my(gens = List());
  \\ explicit cofactor expansion: matdet on polynomial entries goes through rational functions and was the export's bottleneck
  my(det3(A) = A[1,1] * (A[2,2] * A[3,3] - A[2,3] * A[3,2]) - A[1,2] * (A[2,1] * A[3,3] - A[2,3] * A[3,1]) + A[1,3] * (A[2,1] * A[3,2] - A[2,2] * A[3,1]));
  forsubset([5, 3], S, my(Sv = Vec(S), D = det3(matrix(3, 3, r, t, U[r, Sv[t]]))); if (D != 0, listput(gens, D / content(D))));
  my(G = Str(outdir, "/triple-minors-m", m, ".ms"));
  write(G, "x,y,t"); write(G, "0");
  for (g = 1, #gens, write(G, gens[g], ","));
  write(G, "t*x*y*(x-1)*(y-1)*(x-y)-1");
  \\ total degree as max over x^i of i + deg_y(coefficient): cheap (a substitution x -> z x, y -> z y took minutes at m = 11)
  my(tdeg(P) = vecmax(vector(poldegree(P, 'x) + 1, i, my(c = polcoef(P, i - 1, 'x)); if (c == 0, -1, i - 1 + poldegree(c, 'y)))));
  print("m = ", m, ": ", #gens, " minors, total degrees ", vector(#gens, g, tdeg(gens[g])));
  quit;
}
