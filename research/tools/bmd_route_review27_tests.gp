\\ Route review tests (cycle bmd-20261009-bs, 9 October 2026).
\\ (1) Gegenbauer tie coefficients t_d(c) = [T^d]((1+cT)(1+T))^(-3/2), d = binom(m,2), m = 2..10: multiplicities of
\\     their zeros in c, and whether every zero lies on the unit circle (Szego: Gegenbauer zeros are real and simple in
\\     (-1,1); t_d(c) = c^(d/2) C_d^(3/2)(x) with x = -(1+c)/(2 sqrt c), so zeros map to |c| = 1, and x = 0 (odd d)
\\     gives c = -1 with multiplicity 2).
\\ (2) Falsification arc in the cone class "tie over a caterpillar" (thm:cube-tie-taylor-dominance): cluster
\\     (c(s), 1, s^2 z3, s^4 z4) with c(s) = c0 + s, c0 = -1 (the zero of t_1, m = 2), scaled by x = s^w. C-block
\\     coordinates x^(sum S) p_S; least value over S subset [0, 9], |S| = 6, at rates w in {1/10, ..., 6}: ties reported.
OUT = "research/results/bmd-20261009-bs/review-tests.txt";
default(parisizemax, 2 * 10^9);
\\ explicit coefficient (a first version expanded a series in T with c of higher variable priority and got a series)
tco(d) = sum(i = 0, d, binomial(-3/2, i) * binomial(-3/2, d - i) * 'c^i);
{
  for (m = 2, 10, my(d = m * (m - 1) / 2, t = tco(d), fa = factor(t), mult = List(), circ = 1);
    for (i = 1, #fa~, my(g = fa[i, 1]); if (poldegree(g, 'c) >= 1,
      listput(mult, [poldegree(g, 'c), fa[i, 2], subst(g, 'c, -1) == 0]);
      foreach(polroots(g), r, if (abs(abs(r) - 1) > 1e-20, circ = 0))));
    write(OUT, "(1) m = ", m, ", d = ", d, ": irreducible factors [degree, multiplicity, vanishes at -1] = ", Vec(mult), "; all zeros on |c| = 1: ", circ));
  my(H(r, s, K) = my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)));
  my(NS = 30, Y = [-1 + 's + O('s^NS), 1, 2 * 's^2 + O('s^NS), 5 * 's^4 + O('s^NS)], R = 6, K = 9, P = matrix(R, K + 1), r = 0);
  for (i = 1, 4, for (j = i + 1, 4, r++; my(h = H(Y[i], Y[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  my(vals = List());
  forsubset([K + 1, R], S, my(Sv = Vec(S), dt = matdet(matrix(R, R, i, j, P[i, Sv[j]])));
    if (dt != 0, listput(vals, [valuation(dt, 's), vecsum(Sv) - R, apply(t -> t - 1, Sv)])));
  my(vl = Vec(vals), ties = List());
  forstep (w = 1/10, 6, 1/10, my(best = oo, arg = List());
    foreach(vl, z, my(f = z[1] + w * z[2]); if (f < best, best = f; arg = List([z[3]]), if (f == best, listput(arg, z[3]))));
    if (#arg > 1, listput(ties, [w, Vec(arg)])));
  my(m0 = vecmin(apply(z -> z[1], vl)), s0 = vecmin(apply(z -> if (z[1] == m0, z[2], oo), vl)));
  write(OUT, "(2) tie (c0 = -1 + s, 1) over caterpillar (2 s^2, 5 s^4): least valuation ", m0, " at column sum ", s0, " (T0 column sum 15); val p_T0 = ",
        vecmin(apply(z -> if (z[3] == [0 .. 5], z[1], oo), vl)), "; rates in {1/10..6} with a C-block tie: ", if (#ties, Vec(ties), "none"));
}
