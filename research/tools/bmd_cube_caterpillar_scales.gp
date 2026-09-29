\\ Caterpillar degeneration of the separated pair space (29 September 2026).
\\ Roots a_j = c_j eps^(j-1), j = 1..N (N = 5), with generic constants c_j. Tested prediction
\\ (derived in the notebook entry): every component at scale |T| ~ eps^(-k) sees one visible root and
\\ two clusters, and the annuli between scales carry no Weierstrass points, so all non-branch roots
\\ of the Wronskian have integer scale exponents log|T|/log(1/eps) in {0, ..., N-1} (up to o(1)).
\\ Exact Wronskian of the binom(N,2) pair functions over Q at eps = 10^-6 and 10^-8; the unrounded
\\ exponents are printed and counted per nearest integer.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
\p 800
default(parisizemax, 2^31);
wronsk(fl) = {
  my(n = #fl, P = matrix(n, n));
  for (i = 1, n, my(L = sum(j = 1, #fl[i], fl[i][j][2] * deriv(fl[i][j][1], T) / fl[i][j][1]), p = 1); for (k = 1, n, P[k, i] = p; p = deriv(p, T) + p * L));
  numerator(matdet(P));
}
main() = {
  my(N = 5, c = [1, 2, -3, 5, -7]);
  foreach ([10^-6, 10^-8], eps,
    my(a = vector(N, j, c[j] * eps^(j - 1)), fl = List());
    for (i = 1, N, for (j = i + 1, N, listput(fl, [[1 + a[i] * T, -3/2], [1 + a[j] * T, -3/2]])));
    my(q = wronsk(Vec(fl)));
    foreach (a, x, while (subst(q, T, -1 / x) == 0, q = q / (T + 1 / x)));
    my(r = polroots(q), ex = vecsort(vector(#r, i, log(abs(r[i])) / log(1 / eps))));
    my(cnt = vector(N, k, #[e | e <- ex, abs(e - (k - 1)) < 0.15]));
    emit(Str("eps=", eps, ": non-branch degree ", poldegree(q), "; counts at integer scales 0..", N - 1, ": ", cnt,
      "; roots off integer scales: ", #ex - vecsum(cnt), "; squarefree ", poldegree(gcd(q, deriv(q))) == 0));
    emit(Str("  exponents: ", apply(e -> round(e * 1000) / 1000., ex))));
}
main();
