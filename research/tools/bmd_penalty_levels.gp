\\ Penalty levels of cross-coordinate terms (9 October 2026; cycle bmd-20261009-e).
\\ For every coordinate Lambda (columns [-M, 2M], 1 <= p <= M-1) and u-order t = n - B(Lambda), records the least
\\ penalty v - 2 val Vand over all sets in each class (p, delta_N, t), and the largest j with that penalty >= g(j)
\\ (g(j) = min over (j+1)-subsets of 2 val Vand). Question: which function f(p, delta_N, t) gives penalty >= g(k - f)?
\\ The graded theorem gives f = t; partial domination needs f <= ... One prime q = 1000003; trees with distinct g-levels.
OUT = "research/results/bmd-20261009-e/penalty-levels.txt";
q = 1000003;
c(n) = if(n < 0, 0, binomial(-3/2, n));
vq(x) = if(x == 0, oo, valuation(x, q));
vand(Y) = prod(a = 1, #Y, prod(b = a + 1, #Y, Y[b] - Y[a]));
g(Y, j) = { if(j < 0, return(0)); my(best = oo); forsubset([#Y, j + 1], S, best = min(best, 2 * vq(vand(vecextract(Y, Vec(S)))))); best };
NU = 20;
levels(name, Y) = {
  my(M = #Y, cols = [-M .. 2 * M], V2 = 2 * vq(vand(Y)), best = Map(), gl = vector(M, j, g(Y, j - 1)));
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]]), N = apply(t -> -t, select(t -> t < 0, L)), p = #N);
    if(p >= 1 && p <= M - 1,
      my(k = M - p, B = p * (p - 1) / 2 + vecsum(N) + k, dN = vecsum(N) - p * (p + 1) / 2);
      my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
        if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
          my(s = r - M); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
      my(D = matdet(X));
      for (t = 0, min(3, NU - B), my(cf = polcoef(D, B + t, 'u));
        if(cf != 0, my(key = [p, dN, t], pen = vq(cf) - V2);
          if(!mapisdefined(best, key) || mapget(best, key) > pen, mapput(best, key, pen))))));
  write(OUT, name, " M=", M, ": g(0..M-1) = ", gl);
  my(K = Vec(best)); \\ keys
  foreach(K, key, my(pen = mapget(best, key), k = M - key[1], lev = -1);
    for (j = 0, k, if(pen >= gl[j + 1], lev = j));
    write(OUT, "  p=", key[1], " delta_N=", key[2], " t=", key[3], ": least penalty ", pen, ", largest j with penalty >= g(j): ", lev,
      " (k=", k, ", graded bound uses j=", max(k - key[3], 0), ")"));
};
{
  my(e = q);
  levels("nested cherries", [1, 1 + e, 1 + e + e^3, 3]);
  levels("caterpillar cluster", [1, 1 + e, 1 + e + e^2, 1 + e + e^2 + e^3]);
}
