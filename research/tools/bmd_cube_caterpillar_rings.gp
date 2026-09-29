\\ Caterpillar neck rings at N = 6 (29 September 2026; falsification test of the route review).
\\ Tested statement: conj:cube-caterpillar-neck-slopes. In the caterpillar a_j = c_j eps^(j-1), j = 1..6,
\\ the annulus between scales 1 and 2 is a neck between the far pair {a1, a2} (effectively {1, infinity})
\\ and a caterpillar cluster of M = 4 roots, so the conjecture predicts rings of 2M = 8 points at relative
\\ slopes binom(j+1,2)/M = 1/4 and 3/4, i.e. at scales 1.25 and 1.75, and none elsewhere in that annulus.
\\ By inversion the annulus between scales 3 and 4 then carries rings at 3.25 and 3.75. The annulus
\\ between 2 and 3 (three far roots, three near) is not covered by the conjecture; it is reported.
\\ Exact Wronskian of the 15 pair functions over Q at eps = 10^-8 and 10^-10; prints the scale
\\ exponents log|T|/log(1/eps) of all non-branch roots, sorted, and whether they are simple.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
\p 2500
default(parisizemax, 2^32);
wronsk(fl) = {
  my(n = #fl, P = matrix(n, n));
  for (i = 1, n, my(L = sum(j = 1, #fl[i], fl[i][j][2] * deriv(fl[i][j][1], T) / fl[i][j][1]), p = 1); for (k = 1, n, P[k, i] = p; p = deriv(p, T) + p * L));
  numerator(matdet(P));
}
main() = {
  my(N = 6, c = [1, 2, -3, 5, -7, 11]);
  foreach ([10^-8, 10^-10], eps,
    my(a = vector(N, j, c[j] * eps^(j - 1)), fl = List());
    for (i = 1, N, for (j = i + 1, N, listput(fl, [[1 + a[i] * T, -3/2], [1 + a[j] * T, -3/2]])));
    my(q = wronsk(Vec(fl)));
    foreach (a, x, while (subst(q, T, -1 / x) == 0, q = q / (T + 1 / x)));
    my(r = polroots(q), ex = vecsort(vector(#r, i, log(abs(r[i])) / log(1 / eps))));
    emit(Str("eps=", eps, ": non-branch degree ", poldegree(q), "; squarefree ", poldegree(gcd(q, deriv(q))) == 0));
    emit(Str("  exponents: ", apply(e -> round(e * 1000) / 1000., ex))));
}
main();
