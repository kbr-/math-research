\\ M = 5 variant (cycle bmd-20261009-i, 9 October 2026) of the window order-minimality and half-speed penalty test
\\ (bmd_window_order_minimality.gp, cycle bmd-20261009-h), on the tree where the row-cost rule fails.
\\ Tested statements (candidates):
\\ (H) half-speed penalty: for every cross coordinate Lambda with 1 <= p <= M-1 and t >= 0,
\\     val [u^(B+t)] P_Lambda >= 2 val Vand + g(k - d(p,t)),  d(p,t) = max{d : dp + d(d-1)/2 <= t};
\\ (W) order minimality: the window Lambda_p = [-p, 2M-1-p] has, at every relative order t, penalty
\\     <= the penalty of every Lambda with the same p at the same t (then each non-window term is strictly
\\     dominated by the window's term of the same order).
\\ Also records whether the windows attain the half-speed bound.
\\ q-adic valuations at q = 1000003 (denominators of the expansion are q-units).
OUT = "research/results/bmd-20261009-i/half-speed-m5.txt";
q = 1000003;
c(n) = if(n < 0, 0, binomial(-3/2, n));
vq(x) = if(x == 0, oo, valuation(x, q));
vand(Y) = prod(a = 1, #Y, prod(b = a + 1, #Y, Y[b] - Y[a]));
g(Y, j) = { if(j < 0, return(0)); my(best = oo); forsubset([#Y, j + 1], S, best = min(best, 2 * vq(vand(vecextract(Y, Vec(S)))))); best };
hd(p, t) = { my(d = 0); while((d + 1) * p + (d + 1) * d / 2 <= t, d++); d };
TMAX = 4;
pens(Y, L, M, V2) = {
  my(N = apply(t -> -t, select(t -> t < 0, L)), p = #N, k = M - p, B = p * (p - 1) / 2 + vecsum(N) + k, NU = B + TMAX);
  my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
    if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
      my(s = r - M); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
  my(D = matdet(X));
  vector(TMAX + 1, j, my(cf = polcoef(D, B + j - 1, 'u)); if(cf == 0, oo, vq(cf) - V2))
};
run(name, Y, cmax) = {
  my(M = #Y, cols = [-M .. cmax], V2 = 2 * vq(vand(Y)), gl = vector(M, j, g(Y, j - 1)));
  my(win = vector(M - 1, p, pens(Y, [-p .. 2 * M - 1 - p], M, V2)));
  my(badH = matrix(M - 1, TMAX + 1), badW = matrix(M - 1, TMAX + 1), ex = List());
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]]), p = #select(t -> t < 0, L));
    if(p >= 1 && p <= M - 1,
      my(pv = pens(Y, L, M, V2), k = M - p);
      for (t = 0, TMAX, my(pen = pv[t + 1]);
        if(pen < gl[k - hd(p, t) + 1], badH[p, t + 1]++; if(#ex < 6, listput(ex, ["H", L, t, pen])));
        if(pen < win[p][t + 1], badW[p, t + 1]++; if(#ex < 12, listput(ex, ["W", L, t, pen, win[p][t + 1]]))))));
  write(OUT, name, " M=", M, ": g(0..M-1) = ", gl);
  for (p = 1, M - 1, my(k = M - p);
    write(OUT, "  p=", p, ": window penalty t=0..", TMAX, ": ", win[p], "; half-speed bound: ", vector(TMAX + 1, j, gl[k - hd(p, j - 1) + 1]),
      "; (H) violations: ", badH[p, ], "; (W) violations: ", badW[p, ]));
  for (i = 1, #ex, write(OUT, "   ", ex[i]));
};
{
  my(e = q);
  my(cfg = [["nested cherries over a cherry", [1, 1 + e, 1 + e + e^3, 3, 3 + e^2]]]);
  for (i = 1, #cfg, run(cfg[i][1], cfg[i][2], 9));
}
