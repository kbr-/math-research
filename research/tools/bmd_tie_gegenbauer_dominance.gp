\\ Taylor dominance above a tie and the Gegenbauer tie coefficient (cycle bmd-20261009-ag, 9 October 2026).
\\ t_k(c) = [T^k]((1+cT)(1+T))^(-3/2), the tie coefficient of thm:cube-tie-window-gegenbauer; recurrence
\\ (k+1) t_{k+1} = -(1+c)(k+3/2) t_k - c(k+2) t_{k-1}.
\\ Candidate (conj:cube-tie-dominance-gegenbauer): above a tie (c0, 1) over a caterpillar of m >= 2 roots, Taylor
\\ dominance of the pair span (val p_T0 = min_S val p_S) holds iff t_d(c0) != 0, d = binom(m,2).
\\ (a) factorization of t_1 and t_3 (compare the cofactors (c-1)^2 (c+1), (c-1)^6 c^3 (c+1)(7c^2+2c+7) at M = 4, 5);
\\ (b) M = 6 (m = 4, d = 6), q-adic: Taylor dominance at (c0, 1, q, q+q^2, q+q^2+q^3, q+q^2+q^3+q^4), columns [0,17],
\\     for c0 = 2, c0 a root of t_6 in Z_q (q chosen so that one exists), and c0 a root of 5c^2-2c+5 in Z_q;
\\ (c) the excluded Hankel moduli (M-1)c^2-2c+(M-1) = 0 are not zeros of t_d, d = binom(M-2,2), M = 4..120:
\\     t_d computed by the recurrence in F_p[c]/((M-1)c^2-2c+(M-1)), p = 1000003 > all denominators; nonzero there
\\     certifies nonzero over Q.
OUT = "research/results/bmd-20261009-ag/tie-gegenbauer-dominance.txt";
default(parisizemax, 2 * 10^9);
tpol(k) = polcoef(((1 + 'c * 'x + O('x^(k + 1))) * (1 + 'x))^(-3/2), k, 'x);
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
dominance(Y, q, K) = {
  my(M = #Y, R = M * (M - 1) / 2, P = matrix(R, K + 1), r = 0, vT = -1, vmin = 10^9);
  for (i = 1, M, for (j = i + 1, M, r++; my(h = H(Y[i], Y[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  forsubset([K + 1, R], I, my(d = matdet(matrix(R, R, a, b, P[a, I[b]])));
    if (d != 0, my(v = valuation(d, q)); vmin = min(vmin, v); if (Vec(I) == [1 .. R], vT = v)));
  [vT, vmin];
};
{
  write(OUT, "(a) t_1 = ", factor(tpol(1)), "; t_3 = ", factor(tpol(3)));
  \\ (b)
  my(t6 = tpol(6), qq = 0, root6 = 0);
  forprime(p = 1000003, 1003000, my(rt = polrootspadic(t6, p, 40)); if (#rt > 0 && kronecker(-6, p) == 1, qq = p; root6 = truncate(rt[1]); break));
  write(OUT, "(b) prime q = ", qq, " (t_6 has a root in Z_q and -6 is a square)");
  my(q = qq, r24 = sqrt(-24 + O(q^40)), cH = truncate((1 + r24) / 5));
  foreach([["c0 = 2", 2], ["c0 = root of t_6", root6], ["c0 = Hankel modulus (1+sqrt(-24))/5", cH]], G,
    my(c0 = G[2], Y = [c0, 1, q, q + q^2, q + q^2 + q^3, q + q^2 + q^3 + q^4], res = dominance(Y, q, 17));
    write(OUT, "    M=6, ", G[1], ": val p_T0 = ", res[1], ", min_S val p_S = ", res[2], ", Taylor dominance: ", res[1] == res[2]));
  \\ (c)
  my(p = 1000003, bad = List());
  for (M = 4, 120, my(d = binomial(M - 2, 2), Q = Mod(1, p) * ((M - 1) * 'c^2 - 2 * 'c + (M - 1)), C = Mod(Mod(1, p) * 'c, Q));
    my(t0 = Mod(Mod(1, p), Q), t1 = -(1 + C) * 3 / 2);
    if (d == 0, my(tt = t0); if (tt == 0, listput(bad, M)); next);
    for (k = 1, d - 1, my(t2 = (-(1 + C) * (k + 3/2) * t1 - C * (k + 2) * t0) / (k + 1)); t0 = t1; t1 = t2);
    if (t1 == 0, listput(bad, M)));
  write(OUT, "(c) M = 4..120: Hankel moduli that are zeros of t_d mod p (none certifies the claim over Q): ", Vec(bad));
}
