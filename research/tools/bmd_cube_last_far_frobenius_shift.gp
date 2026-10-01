\\ Frobenius shift of the last-step far space modulo window primes (3 October 2026; cycle bmd-20261003-zzy).
\\ Tested statement (lem:cube-last-far-frobenius-shift): for an odd prime p > d = R_(e+2), q = (p-1)/2, the far part of
\\ W_(b-1) mod p (factors x, 1+x removed) equals, up to a nonzero constant, the far part of the Wronskian over F_p of the
\\ polynomial space
\\   V_p = x^3(1+x)^3 P_<n (+) x^3 (+) (1+x)^3 (+) x^3 (1+x)^q P_<4e (+) x^q (1+x)^3 P_<4e (+) x^q (1+x)^(q+1) P_<4,
\\ obtained from F_(b-1) by shifting every half-integral exponent by p/2 and multiplying by x^3 (1+x)^3.
\\ Exact check at e = 1, 2, 3 and every window prime max(d, 2n) < p <= 2n + 8e + 7, and also at a few primes above the window.
OUT = getenv("OUT");
default(parisizemax, 4000000000);
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
src(e) = my(f = Str("research/results/bmd-20261003-zl/W_last_e", e, ".gp")); iferr(read(f), E, read(Str("research/results/bmd-20261003-zw/W_last_e", e, ".gp")));
farpart(P) = { if (P == 0, return(0)); P /= 'x^valuation(P, 'x); while (subst(P, 'x, -1) == 0, P /= ('x + 1)); P; }
{
for (e = 1, 3,
  my(W = src(e), n = Rn(e), d = Rn(e + 2), lo = max(d, 2 * n), hi = 2 * n + 8 * e + 7, res = List());
  forprime (p = lo + 1, hi + 20,
    my(q = (p - 1) / 2, V = List());
    for (j = 0, n - 1, listput(V, 'x^(3 + j) * (1 + 'x)^3));
    listput(V, 'x^3); listput(V, (1 + 'x)^3);
    for (j = 0, 4 * e - 1, listput(V, 'x^(3 + j) * (1 + 'x)^q); listput(V, 'x^(q + j) * (1 + 'x)^3));
    for (j = 0, 3, listput(V, 'x^(q + j) * (1 + 'x)^(q + 1)));
    my(K = #V);
    if (K != d, emit(Str("dimension mismatch ", K, " vs ", d)); next);
    my(M = matrix(K, K, i, r, 0));
    for (i = 1, K, my(f = V[i] * Mod(1, p)); for (r = 1, K, M[i, r] = f; f = deriv(f, 'x)));
    my(Wp = farpart(matdet(M)), Ws = farpart(W * Mod(1, p)));
    my(ok = (Wp != 0) && (poldegree(Wp) == poldegree(Ws)) && (Wp * pollead(Ws) == Ws * pollead(Wp)));
    listput(res, [p, if (p <= hi, "window", "above"), ok, poldegree(Ws), Wp == 0]));
  emit(Str("e=", e, ": d = ", d, ", window (", lo, ", ", hi, "]; [p, place, far parts proportional mod p, far degree of W_(b-1) mod p, W(V_p) = 0 over F_p]: ", Vec(res))));
}
