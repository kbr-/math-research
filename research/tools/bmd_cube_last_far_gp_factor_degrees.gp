\\ Factor-degree patterns of the non-branch factor G_p (4 October 2026; cycle bmd-20261004-c; Dwork lead of the arithmetic
\\ route review).
\\ Tested statement (conj:cube-last-far-gp-structured): at window primes max(d, 2n+5) < p <= 2n+8e+7, G_p = W_(b-1) mod p
\\ with the factors x, x+1 removed factors over F_p into pieces of bounded degree pattern (as a product of truncated
\\ hypergeometric polynomials would), rather than like a random polynomial of its degree (few factors, largest of
\\ degree about 0.62 deg). Control: the same statistics for W_(b-1) mod primes above the window (no collapse) and the
\\ random-polynomial expectations (expected number of irreducible factors about log(deg) + 0.58).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
Rn(n) = n * (2 * n - 1);
src(e) = if (e <= 3, "research/results/bmd-20261003-zl", if (e <= 6, "research/results/bmd-20261003-zw", if (e == 7, "research/results/bmd-20261003-zy", "research/results/bmd-20261003-zz")));
stats(W, p) = {
  my(F = factormod(W, p), degs = List(), m0 = 0, m1 = 0);
  for (i = 1, #F~, my(g = lift(F[i, 1])); if (g == 'x, m0 = F[i, 2], if (g == 'x + 1, m1 = F[i, 2], for (r = 1, F[i, 2], listput(degs, poldegree(g))))));
  my(v = vecsort(Vec(degs), , 4)); [vecsum(v), #v, if (#v, v[1], 0), v];
}
{
for (e = 4, 8,
  my(W = read(Str(src(e), "/W_last_e", e, ".gp")), n = Rn(e), d = Rn(e + 2), lo = max(d, 2 * n + 5), hi = 2 * n + 8 * e + 7);
  forprime (p = lo + 1, hi + 30,
    my(S = stats(W, p), D = S[1]);
    emit(Str("e=", e, " p=", p, if (p <= hi, " (window)", " (above)"), ": deg G_p ", D, ", irreducible factors ", S[2], " (random expectation about ", precision(log(max(D, 1)) + 0.58, 3) * 1., "), largest ", S[3], " (", precision(S[3] / max(D, 1), 3) * 1., " of deg), degrees ", S[4]))));
}
