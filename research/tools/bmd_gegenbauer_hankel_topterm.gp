\\ Gegenbauer lead (cycle kej, 9 October 2026): test of the hypothesis suggested by bmd_gegenbauer_hankel_padic.gp:
\\ for every M >= 4 and every prime p dividing M - 1, the top term k = 0 of Q(u) = sum_k a_k u^(D-k), u = 2M/(M-1),
\\ strictly dominates p-adically (V_0 < V_k for all 1 <= k <= D), where V_k = v_p(a_k) + (D - k) v_p(u),
\\ a_k = (-1)^k (3/2)_(d-k)/(k!(d-2k)!), d = binom(M-2,2), D = floor(d/2).  Uses the ratio
\\ a_(k+1)/a_k = -2 (d-2k)(d-2k-1) / ((k+1)(2d-2k+1)), so V_(k+1) - V_k = v_p(ratio) - v_p(u).
\\ Reports, per M, primes p | M-1 where the top term fails to dominate strictly, with the minimal margin min_k (V_k - V_0).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
margin(M, p) = {
  my(d = binomial(M - 2, 2), D = d \ 2, vu = valuation(2 * M, p) - valuation(M - 1, p), V = 0, m = oo, at = -1);
  for(k = 0, D - 1,
    V += valuation(2, p) + valuation(d - 2 * k, p) + valuation(d - 2 * k - 1, p) - valuation(k + 1, p) - valuation(2 * d - 2 * k + 1, p) - vu;
    if(V < m, m = V; at = k + 1));
  [m, at];
}
{
  my(M0 = if(getenv("M0") == 0 || getenv("M0") == "", 4, eval(getenv("M0"))), M1 = if(getenv("M1") == 0 || getenv("M1") == "", 500, eval(getenv("M1"))), fails = List(), small = List());
  for(M = M0, M1,
    foreach(factor(M - 1)[, 1]~, p, my(r = margin(M, p));
      if(r[1] <= 0, listput(fails, [M, p, r]));
      if(r[1] == 1, listput(small, [M, p, r[2]]))));
  emit(Str("M in ", M0, "..", M1, ": primes p | M-1 where the top term does not strictly dominate [M, p, [margin, k]]: ", Vec(fails)));
  emit(Str("cases with margin exactly 1 [M, p, k]: ", #small, " ", Vec(small[1..min(#small, 40)])));
}
quit;
