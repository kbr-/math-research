\\ Cherry above a tie cluster at the zero of the window coefficient (8 October 2026; cycle bmd-20261008-zk).
\\ Prediction (Hankel form conj:cube-cherry-hankel-coefficient, L_j = c Hank_(M-j)): for a tie cluster with
\\ normalized roots (c0, 1, 0, 0), M = 4, the regime-3 window coefficient L_3 is proportional to
\\ Hank_1(c0,1,0,0) = 3 c0^2 - 2 c0 + 3, which vanishes at c0 = (1 +- 2 sqrt(2) i)/3.  There condition (W') of
\\ cor:cube-cherry-step is at risk on arcs in regime p = 3 (w_x/(w_x+w_e) in (1/2, 3/4]).
\\ Configuration (as in bmd_route_review11_tests.gp): cherry {1, 1+e^b}, tie c0 e^a, e^a, deeper roots e^(a+d),
\\ -3 e^(a+d+1) (a caterpillar), so w_x = a, w_e = b and the deeper scale is d.  R = 15.  Prints the vanishing orders
\\ of the limit pair space at T = 0: unramified means 0..14; avoidance of K needs the largest <= R+1 = 16.
\\ Controls: the same arcs at c0 = 2 (where Hank_1 != 0).  Arcs: rates (w_x, w_e) = (2, 1) (rho = 2/3, regime 3), deeper
\\ scale d = 1, 2, 4.  A first run that also had (3,2,2), (3,1,2), (5,3,1) was stopped after 30 min on (3,2,2), the
\\ number-field series being costly at larger exponents; its three finished arcs agree with this run.
default(parisizemax, 6 * 10^9); default(seriesprecision, 80);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
t = varlower("t");
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
orders(rts, K) = {
  my(n = #rts, R = n * (n - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, n, for (j = i + 1, n, r++; my(h = H(rts[i], rts[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  for (step = 1, R,
    my(bi = 0, bj = 0, bv = 1e9);
    for (i = step, R, for (j = 1, K + 1, if (P[i, j] != 0, my(vv = valuation(P[i, j], 'e)); if (vv < bv || (vv == bv && j < bj), bv = vv; bi = i; bj = j))));
    my(tmp = P[step, ]); P[step, ] = P[bi, ]; P[bi, ] = tmp;
    P[step, ] = P[step, ] / P[step, bj];
    for (i = 1, R, if (i != step && P[i, bj] != 0, P[i, ] = P[i, ] - P[i, bj] * P[step, ])));
  my(L = matrix(R, K + 1, i, j, my(z = P[i, j]); if (z == 0, 0, my(vv = valuation(z, 'e)); if (vv > 0, 0, subst(numerator(z), 'e, 0) / subst(denominator(z), 'e, 0)))));
  my(rk = 0, pv = List()); for (j = 1, K + 1, if (matrank(vecextract(L, "..", [1 .. j])) > rk, rk++; listput(pv, j - 1)));
  Vec(pv);
}
{
  my(z = Mod(t, t^2 - 2 * t + 9) / 3);
  emit(Str("check: 3 c0^2 - 2 c0 + 3 at the predicted zero = ", 3 * z^2 - 2 * z + 3));
  foreach([["zero (1+2sqrt(2)i)/3", z], ["control 2", 2]], C, my(c0 = C[2]);
    foreach([[2, 1, 1], [2, 1, 2], [2, 1, 4]], abd,
      my([a, b, d] = abd, rts = [1, 1 + 'e^b, c0 * 'e^a, 'e^a, 'e^(a + d), -3 * 'e^(a + d + 1)], R = 15, o = orders(rts, R + 3));
      emit(Str("c0 = ", C[1], ", (w_x, w_e, d) = ", abd, ": orders ", o, "; unramified: ", o == [0 .. R - 1], "; largest <= R+1: ", vecmax(o) <= R + 1))));
}
quit
