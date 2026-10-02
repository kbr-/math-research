\\ One-level Hankel penalty test (cycle bmd-20261009-h, 9 October 2026).
\\ Tested statement (candidate, from the trace calculus of thm:cube-first-order-hankel-penalty):
\\ for every cross coordinate Lambda with 1 <= p <= M-1 and every t >= 0,
\\   val [u^(B+t)] P_Lambda >= 2 val Vand + g(k-1)   (at most one Hankel level lost), and
\\   val [u^(B+t)] P_Lambda >= 2 val Vand + g(k)     when t < p.
\\ Records, per tree and (p, t), the least penalty and the number of terms violating each bound.
\\ q-adic valuations at q = 1000003 (the proofs' denominators are q-units).
OUT = "research/results/bmd-20261009-h/one-level-penalty.txt";
q = 1000003;
c(n) = if(n < 0, 0, binomial(-3/2, n));
vq(x) = if(x == 0, oo, valuation(x, q));
vand(Y) = prod(a = 1, #Y, prod(b = a + 1, #Y, Y[b] - Y[a]));
g(Y, j) = { if(j < 0, return(0)); my(best = oo); forsubset([#Y, j + 1], S, best = min(best, 2 * vq(vand(vecextract(Y, Vec(S)))))); best };
TMAX = 6;
run(name, Y, cmax) = {
  my(M = #Y, cols = [-M .. cmax], V2 = 2 * vq(vand(Y)), gl = vector(M, j, g(Y, j - 1)));
  my(least = matrix(M - 1, TMAX + 1, i, j, oo), bad1 = matrix(M - 1, TMAX + 1), bad0 = matrix(M - 1, TMAX + 1), ex = List());
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]]), N = apply(t -> -t, select(t -> t < 0, L)), p = #N);
    if(p >= 1 && p <= M - 1,
      my(k = M - p, B = p * (p - 1) / 2 + vecsum(N) + k, NU = B + TMAX);
      my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
        if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
          my(s = r - M); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
      my(D = matdet(X));
      for (t = 0, TMAX, my(cf = polcoef(D, B + t, 'u));
        if(cf != 0, my(pen = vq(cf) - V2);
          least[p, t + 1] = min(least[p, t + 1], pen);
          if(pen < gl[k], bad1[p, t + 1]++; if(#ex < 6, listput(ex, [L, t, pen, gl[k]])));
          if(t < p && pen < gl[k + 1], bad0[p, t + 1]++)))));
  write(OUT, name, " M=", M, ": g(0..M-1) = ", gl);
  for (p = 1, M - 1, write(OUT, "  p=", p, " (g(k-1)=", gl[M - p], ", g(k)=", gl[M - p + 1], "): least penalty t=0..", TMAX, ": ", least[p, ],
    "; below g(k-1): ", bad1[p, ], "; below g(k) with t<p: ", bad0[p, ]));
  for (i = 1, #ex, write(OUT, "   below g(k-1): Lambda = ", ex[i][1], " t = ", ex[i][2], " penalty ", ex[i][3], " < ", ex[i][4]));
};
{
  my(e = q);
  my(cfg = [
    ["cherry top", [1, 1 + e, 2, 5]],
    ["nested cherries", [1, 1 + e, 1 + e + e^3, 3]],
    ["two separated cherries", [1, 1 + e, 2, 2 + e^2]],
    ["tie over cherry", [2, 1, 3 * e, 3 * e + 5 * e^2]],
    ["cherry over deep cherry", [1, 1 + e, 2 * e^2, 3 * e^3]],
    ["caterpillar cluster", [1, 1 + e, 1 + e + e^2, 1 + e + e^2 + e^3]]]);
  for (i = 1, #cfg, run(cfg[i][1], cfg[i][2], 8));
}
