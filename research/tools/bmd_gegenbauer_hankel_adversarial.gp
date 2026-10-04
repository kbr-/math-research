\\ Gegenbauer lead (cycle kej, 9 October 2026): adversarial test of "every prime p | M-1 makes the top term dominate".
\\ For p = 5, 7, 11, 13 choose M = 1 mod p with x_(i0) = (M-2)(M-3) + 1 - 2 i0 divisible by p^10, where
\\ i0 = (p+3)/2 is the first index with p | 2(d-i)+1 (d = (M-2)(M-3)/2 = 1 mod p): Hensel lift of (M-2)(M-3) = 2 i0 - 1.
\\ Then compute V_k - V_0 (notation of bmd_gegenbauer_hankel_topterm.gp) for k <= 60 and report its minimum and where.
\\ Also report, at the same M, whether another prime of 2M(M-1) gives a unique p-adic minimum over k <= 60 at k = 0 or
\\ (cheaply) whether the full certificate holds is NOT checked here: D is about M^2/4, too large to scan.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
partial(M, p, K) = {
  my(d = binomial(M - 2, 2), vu = valuation(2 * M, p) - valuation(M - 1, p), V = 0, m = oo, at = -1);
  for(k = 0, K - 1,
    V += valuation(2, p) + valuation(d - 2 * k, p) + valuation(d - 2 * k - 1, p) - valuation(k + 1, p) - valuation(2 * d - 2 * k + 1, p) - vu;
    if(V < m, m = V; at = k + 1));
  [m, at];
}
{
  foreach([5, 7, 11, 13], p,
    my(i0 = (p + 3) / 2, f = 'M^2 - 5 * 'M + 6 - (2 * i0 - 1), r = polrootspadic(f, p, 10), M = 0);
    \\ pick the root that is 1 mod p
    for(j = 1, #r, my(t = lift(truncate(r[j]))); if(t % p == 1, M = t));
    if(M == 0, emit(Str("p=", p, ": no root = 1 mod p")); next);
    if(M < 4, M += p^10);
    my(d = binomial(M - 2, 2));
    emit(Str("p=", p, " M=", M, " v_p(M-1)=", valuation(M - 1, p), " v_p(2(d-i0)+1)=", valuation(2 * (d - i0) + 1, p),
      " min_{k<=60}(V_k - V_0) [value, k] = ", partial(M, p, 60))));
}
quit;
