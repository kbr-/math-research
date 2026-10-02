\\ Hankel penalty, valuative form (8 October 2026; cycle bmd-20261008-zv).
\\ Tested statements, at points y whose coordinates are integer polynomials in eta = q = 1000003 (cluster trees):
\\ (1) conj:cube-leading-hankel-penalty, valuative: for 1 <= p <= M-1, k = M - p and every Lambda+ of 2M - p
\\     nonnegative columns in [0, 2M+1], val_q D_Lambda >= g(k) := min_{|S| = k+1} 2 val_q Vand(y_S),
\\     with D_Lambda as in lem:cube-cross-leading-coefficient; and the windows (Lambda+ = [0, 2M-1-p]) attain g(k).
\\ (2) the graded form, at M = 4 only: for every Lambda in [-4, 8] with 1 <= p <= 3 and t = 0..3, the u^(B+t)
\\     coefficient of P_Lambda has val_q >= 2 val Vand(y) + g(max(k - t, 0)).
\\ q-adic reading: val_q of an integer expression >= the eta-order, so a value below the bound refutes.
OUT = "research/results/bmd-20261008-zv/hankel-penalty-qadic.txt";
q = 1000003;
c(n) = if(n < 0, 0, binomial(-3/2, n));
vand(Y) = prod(a = 1, #Y, prod(b = a + 1, #Y, Y[b] - Y[a]));
vq(x) = if(x == 0, oo, valuation(x, q));
g(Y, k) = { my(best = oo); forsubset([#Y, k + 1], S, best = min(best, 2 * vq(vand(vecextract(Y, Vec(S)))))); best };
hvec(Y, n) = { my(s = Ser(1 / prod(i = 1, #Y, 1 - Y[i] * 'z), 'z, n + 1)); vector(n + 1, j, polcoef(s, j - 1, 'z)) };
D(H, M, k, Lp) = {
  matdet(matrix(#Lp, M + k, a, b, my(i = Lp[a]);
  if(b <= M, my(n = b - 1 + i - M + 1); if(n < 0, 0, H[n + 1]), my(n = (b - M - 1) + i - M + 2); if(n < 0, 0, H[n + 1] / (i + 1)))));
};
leadtest(name, Y) = {
  my(M = #Y, R = 2 * M + 1, H = hvec(Y, 4 * M + 4));
  for (p = 1, M - 1, my(k = M - p, gk = g(Y, k), cnt = 0, worst = oo, win = oo, bad = 0);
    forsubset([R + 1, 2 * M - p], S, my(Lp = vector(2 * M - p, i, S[i] - 1), d = D(H, M, k, Lp));
      if(d != 0, cnt++; my(e = vq(d) - gk); worst = min(worst, e); if(e < 0, bad++);
        if(Lp == [0 .. 2 * M - 1 - p], win = e)));
    write(OUT, name, " M=", M, " p=", p, " k=", k, ": g(k)=", gk, ", ", cnt, " nonzero D, least excess ", worst,
      ", below bound ", bad, ", window excess ", win));
};
gradedtest(name, Y) = {
  my(M = #Y, cols = [-4 .. 8], V2 = 2 * vq(vand(Y)), worst = vector(4, t, oo), bad = 0, cnt = 0);
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]]), N = apply(t -> -t, select(t -> t < 0, L)), p = #N);
    if(p >= 1 && p <= M - 1,
      my(k = M - p, B = p * (p - 1) / 2 + vecsum(N) + k);
      my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
        if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
          my(s = r - M); sum(m = max(1, -t), B + 4, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
      my(Dt = matdet(X)); cnt++;
      for (t = 0, 3, my(cf = polcoef(Dt, B + t, 'u));
        if(cf != 0, my(e = vq(cf) - V2 - g(Y, max(k - t, 0))); worst[t + 1] = min(worst[t + 1], e); if(e < 0, bad++)))));
  write(OUT, name, " graded M=", M, ": ", cnt, " sets with 1 <= p <= 3; least excess at t=0..3: ", worst, "; below bound: ", bad);
};
{
  my(e = q);
  my(cfg = [
    ["cherry top", [1, 1 + e, 2, 5]],
    ["nested cherries", [1, 1 + e, 1 + e + e^3, 3]],
    ["two cherries", [1, 1 + e, 2, 2 + e^2]],
    ["tie over caterpillar", [2, 1, 3 * e, 5 * e^2]],
    ["tie over cherry", [2, 1, 3 * e, 3 * e + 5 * e^2]],
    ["cherry top", [1, 1 + e, 2, 5, 7]],
    ["nested cherries", [1, 1 + e, 1 + e + e^3, 3, 4]],
    ["tie over cherry", [2, 1, 3 * e, 3 * e + 5 * e^2, 7 * e^3]],
    ["three-root cluster", [1, 1 + e, 1 + 3 * e, 4, 6]],
    ["cherry top", [1, 1 + e, 2, 5, 7, 11]],
    ["tie over cherry over pair", [2, 1, 3 * e, 3 * e + 5 * e^2, 7 * e^3, 7 * e^3 + e^5]]]);
  for (i = 1, #cfg, leadtest(cfg[i][1], cfg[i][2]));
  for (i = 1, 5, gradedtest(cfg[i][1], cfg[i][2]));
}
