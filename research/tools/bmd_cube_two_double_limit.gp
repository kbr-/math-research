\\ Symbolic flat limit of the (2,2) two-cluster class (30 September 2026; cycle bmd-20260930-zv).
\\ Products P_jk = (1 - b_j eps u1)^(1/2) (1 - c_k eps u2)^(1/2), u1 = 1/z, u2 = 1/(z-1) (p1 = 0, p2 = 1 by an affine
\\ map), with symbolic b1, b2, c1, c2.  The script expands to order eps^6 in the coordinates (principal parts at 0 and 1,
\\ value at infinity) and runs the valuation reduction with rational-function coefficients, printing the reduced
\\ orders and the fourth limit function (the one of order 4) as a rational function of z, factored.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
K = 6;
term(a, cc) = 1 / ('z^a * ('z - 1)^cc);
main() = {
  my(b = ['b1, 'b2], c = ['c1, 'c2], F = List());
  for (j = 1, 2, for (k = 1, 2,
    listput(F, sum(a = 0, K, sum(cc = 0, K - a, binomial(1/2, a) * (-b[j])^a * binomial(1/2, cc) * (-c[k])^cc * 'e^(a + cc) * term(a, cc))))));
  \\ valuation reduction on the functions directly (rational functions in z, polynomials in e)
  my(n = 4, R = Vec(F), vals = vector(n));
  for (it = 1, 50,
    for (i = 1, n, vals[i] = valuation(R[i], 'e));
    my(L = vector(n, i, polcoef(R[i], vals[i], 'e)));
    \\ linear dependency among the leading functions over the field of rational functions in b, c
    my(M = matrix(n, n, i, t, 0), basis = List());
    \\ represent leading functions by coefficient vectors in the partial-fraction basis via evaluation at points
    my(pts = [2, 3, 5, 7, 11, 13, 17]);
    my(E = matrix(#pts, n, s, i, subst(L[i], 'z, pts[s])));
    my(ker = matker(E));
    if (#ker == 0, break);
    my(w = ker[, 1], i0 = 0, best = -oo);
    for (i = 1, n, if (w[i] != 0 && vals[i] > best, best = vals[i]; i0 = i));
    R[i0] = sum(i = 1, n, w[i] * 'e^(best - vals[i]) * R[i]);
    R[i0] = R[i0] + O('e^(K + 1)); R[i0] = truncate(R[i0]));
  for (i = 1, n, vals[i] = valuation(R[i], 'e));
  emit(Str("reduced orders ", vals));
  for (i = 1, n, my(f = polcoef(R[i], vals[i], 'e)); emit(Str("  order ", vals[i], ": ", factor(numerator(f)), " / ", factor(denominator(f)))));
}
main();
quit
