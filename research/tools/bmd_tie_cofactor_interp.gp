\\ Tie Taylor cofactor F(c, 1, 0^(M-2)) by interpolation (cycle bmd-20261009-ae, 9 October 2026).
\\ F = p_T0 / Vand^(M-2) for the pair span rows [w^t]((1+y_i w)(1+y_j w))^(-3/2) (lem:cube-cofactor-gives-unique-cblock).
\\ For integer c, F(c,1,0..0) is the e^0 value of the exact quotient along y = (c, 1, e z_3, ..., e z_M) (symbolic e).
\\ Interpolates in c from NPTS integer values (NPTS above the degree, checked by one extra point) and factors,
\\ M = 4, 5, 6 (M = 4, 5 reproduce tie-taylor-cofactor.txt).
OUT = "research/results/bmd-20261009-ae/tie-cofactor-interp.txt";
default(parisizemax, 4 * 10^9);
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
Fval(M, c) = {
  my(R = M * (M - 1) / 2, z = [2, 5, 11, 23], Y = concat([c, 1], vector(M - 2, i, 'e * z[i])), P = matrix(R, R), r = 0);
  for (i = 1, M, for (j = i + 1, M, r++; my(h = H(Y[i], Y[j], R - 1)); for (k = 1, R, P[r, k] = h[k])));
  my(V = prod(i = 1, M, prod(j = i + 1, M, Y[i] - Y[j]))^(M - 2));
  subst(matdet(P) / V, 'e, 0);
};
export(H, Fval);
{
  foreach([[4, 8], [5, 18], [6, 45]], G, my([M, NPTS] = G);
    my(xs = vector(NPTS + 1, i, i + 1), ys = parapply(c -> Fval(M, c), xs));
    my(F = polinterpolate(xs[1..NPTS], ys[1..NPTS], 'c), ok = (subst(F, 'c, xs[NPTS + 1]) == ys[NPTS + 1]));
    write(OUT, "M=", M, " (", NPTS, " points, extra point agrees: ", ok, "): degree ", poldegree(F), ", F = ", factor(F)));
}
