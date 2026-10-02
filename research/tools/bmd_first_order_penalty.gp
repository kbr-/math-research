\\ First-order Hankel penalty (cycle bmd-20261009-g, 9 October 2026).
\\ Tested statement (thm:cube-first-order-hankel-penalty): for every cross coordinate Lambda with
\\ 1 <= p <= M-1 negative indices, if p >= 2, or p = 1 with negative part {-1}, then
\\   val [u^(B(Lambda)+1)] P_Lambda >= 2 val Vand + g(k),  k = M - p,
\\ with g(j) = min over (j+1)-subsets of 2 val Vand.  Control: p = 1 with negative part {-n}, n >= 2,
\\ is excluded by the theorem and is expected to drop below g(k) on some tree.
\\ q-adic valuations at two large primes (the proof's denominators are below both).
OUT = "research/results/bmd-20261009-g/first-order-penalty.txt";
c(n) = if(n < 0, 0, binomial(-3/2, n));
vq(x, q) = if(x == 0, oo, valuation(x, q));
vand(Y) = prod(a = 1, #Y, prod(b = a + 1, #Y, Y[b] - Y[a]));
g(Y, j, q) = { my(best = oo); forsubset([#Y, j + 1], S, best = min(best, 2 * vq(vand(vecextract(Y, Vec(S))), q))); best };
run(name, Y, q, cmax) = {
  my(M = #Y, cols = [-M .. cmax], V2 = 2 * vq(vand(Y), q), gl = vector(M, j, g(Y, j - 1, q)));
  my(nhyp = 0, nzero = 0, minmargin = oo, neq = 0, nctl = 0, ndrop = 0, bad = List());
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]]), N = apply(t -> -t, select(t -> t < 0, L)), p = #N);
    if(p >= 1 && p <= M - 1,
      my(k = M - p, B = p * (p - 1) / 2 + vecsum(N) + k, NU = B + 1);
      my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
        if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
          my(s = r - M); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
      my(cf = polcoef(matdet(X), B + 1, 'u), pen = if(cf == 0, oo, vq(cf, q) - V2), hyp = (p >= 2 || N == [1]));
      if(hyp, nhyp++; if(cf == 0, nzero++, my(mg = pen - gl[k + 1]); minmargin = min(minmargin, mg); if(mg == 0, neq++);
          if(mg < 0, listput(bad, [L, pen, gl[k + 1]]))),
        nctl++; if(pen < gl[k + 1], ndrop++))));
  write(OUT, name, " M=", M, " q=", q, ": g(0..M-1) = ", gl, "; hypothesis terms ", nhyp, " (zero ", nzero,
    "), least margin pen - g(k) = ", minmargin, ", attained with equality ", neq, ", violations ", #bad,
    "; control p=1, N != {1}: ", nctl, " terms, below g(k): ", ndrop);
  for (i = 1, min(#bad, 8), write(OUT, "   violation: Lambda = ", bad[i][1], " penalty ", bad[i][2], " < g(k) = ", bad[i][3]));
};
{
  foreach([1000003, 10007], q, my(e = q);
    my(cfg = [
      ["cherry top", [1, 1 + e, 2, 5]],
      ["nested cherries", [1, 1 + e, 1 + e + e^3, 3]],
      ["two separated cherries", [1, 1 + e, 2, 2 + e^2]],
      ["tie over cherry", [2, 1, 3 * e, 3 * e + 5 * e^2]],
      ["cherry over deep cherry", [1, 1 + e, 2 * e^2, 3 * e^3]],
      ["caterpillar cluster", [1, 1 + e, 1 + e + e^2, 1 + e + e^2 + e^3]]]);
    for (i = 1, #cfg, run(cfg[i][1], cfg[i][2], q, 8)));
  my(e = 1000003);
  run("two separated cherries", [1, 1 + e, 2, 2 + e^2, 5], e, 9);
  run("caterpillar over a root", [1, 1 + e, 1 + e + e^2, 1 + e + e^2 + e^3, 4], e, 9);
}
