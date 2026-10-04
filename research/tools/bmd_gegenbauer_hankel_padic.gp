\\ Gegenbauer lead (cycle kej, 9 October 2026): p-adic certificate that the Hankel and Gegenbauer moduli are disjoint.
\\ Statement (check:cube-hankel-moduli-not-gegenbauer, recorded for M <= 120): C^(3/2)_d(x) != 0 at x^2 = M/(2(M-1)),
\\ d = binom(M-2, 2).  Write C_d(x) = sum_k a_k (2x)^(d-2k), a_k = (-1)^k (3/2)_(d-k) / (k! (d-2k)!), so that
\\ C_d(x) = (2x)^(d mod 2) Q(u), Q(u) = sum_{k<=D} a_k u^(D-k), D = floor(d/2), u = 4x^2 = 2M/(M-1).
\\ Certificate: a prime p such that V_k = v_p(a_k) + (D-k) v_p(u) has a unique minimum over k = 0..D; then Q(u) != 0.
\\ v_p(a_k) uses (3/2)_n = (2n+1)! / (4^n n!) and Legendre's formula.  Primes tried: those dividing 2M(M-1).
\\ Output per M: the certifying primes with the minimizing k, or NONE.  Range M = M0..M1 from env (default 4..300).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
vfac(n, p) = my(s = 0, q = p); while(q <= n, s += n \ q; q *= p); s;
cert(M, p) = {
  my(d = binomial(M - 2, 2), D = d \ 2, vu = valuation(2 * M, p) - valuation(M - 1, p), best = oo, arg = -1, cnt = 0);
  for(k = 0, D, my(n = d - k, v = vfac(2 * n + 1, p) - 2 * n * valuation(2, p) - vfac(n, p) - vfac(k, p) - vfac(d - 2 * k, p) + (D - k) * vu);
    if(v < best, best = v; arg = k; cnt = 1, if(v == best, cnt++)));
  if(cnt == 1, arg, -1);
}
{
  my(M0 = if(getenv("M0") == 0 || getenv("M0") == "", 4, eval(getenv("M0"))), M1 = if(getenv("M1") == 0 || getenv("M1") == "", 300, eval(getenv("M1"))), none = List());
  for(M = M0, M1,
    my(ps = factor(2 * M * (M - 1))[, 1]~, ok = List());
    foreach(ps, p, my(k = cert(M, p)); if(k >= 0, listput(ok, [p, k])));
    if(#ok == 0, listput(none, M));
    emit(Str("M=", M, " d=", binomial(M - 2, 2), " certificates [p, k]: ", Vec(ok))));
  emit(Str("M in ", M0, "..", M1, " without a certificate: ", Vec(none)));
}
quit;
