\\ The second tie-window minor modulo t_d (cycle bmd-20261009-bu, 9 October 2026).
\\ Question (route to conj:cube-tie-window-second-minor): is N_m congruent modulo t_d to a simple multiple of t_(d+1)?
\\ Prints, for m = 2..7, the residue q = N_m * t_(d+1)^(-1) mod t_d (N_m stripped of c and c-1) and its factorization.
OUT = "research/results/bmd-20261009-bu/second-minor-mod.txt";
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
cpow(f) = { my(a = 0, g = f); while (subst(g, 'c, 0) == 0, g = g / 'c; a++); [a, g]; }
c1pow(f) = { my(a = 0, g = f); while (subst(g, 'c, 1) == 0, g = g / ('c - 1); a++); [a, g]; }
{
  for (m = 2, 7, my(d = m * (m - 1) / 2, W = winmat(m, 2 * m + 3), n = 2 * m + 1);
    my(cs = concat([1 .. 2 * m], [2 * m + 2]), N = matdet(matrix(n, n, i, j, W[i, cs[j]])));
    my(A = cpow(N), B = c1pow(A[2]), Ns = B[2], td = tco(d), t1 = tco(d + 1));
    my(q = lift(Mod(Ns, td) / Mod(t1, td)));
    write(OUT, "m = ", m, ", d = ", d, ": N_m = c^", A[1], " (c-1)^", B[1], " * (deg ", poldegree(Ns), "); N_m / t_(d+1) mod t_d = ", if (poldegree(q) <= 0, q, Str("degree ", poldegree(q), ": ", factor(q))));
    \\ also compare with the derivative, and the simplest guess c^k (c+1)^l times a constant
    my(q2 = lift(Mod(Ns, td) / Mod(deriv(td, 'c), td)));
    write(OUT, "        N_m / t_d' mod t_d = ", if (poldegree(q2) <= 0, q2, Str("degree ", poldegree(q2)))));
}
