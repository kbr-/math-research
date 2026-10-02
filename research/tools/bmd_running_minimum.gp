\\ Running-minimum form of standard-negative minimality (cycle bmd-20261009-p, 9 October 2026); variant of
\\ bmd_standard_negatives_minimality.gp (cycle bmd-20261009-k). Tested statement (candidate): for every cross
\\ coordinate Lambda with negative part N = {1, ..., p} and every relative u-order t,
\\   penalty(Lambda, t) >= min_{t' <= t} penalty(Lambda_p, t').
\\ Also counts violations of the plain form (penalty(Lambda,t) >= penalty(Lambda_p,t)) for comparison. If true, every
\\ right-adjacent single exchange Lambda_p - a + (2M-p), a >= 0, has arc value above the window's (X larger by
\\ 2M-p-a, E equal, penalties termwise >=). ex:cube-window-order-minimality-fails had only delta_N >= 1 violations
\\ in its listed examples. q-adic, q = 1000003; coordinates computed in parallel (parapply).
OUT = "research/results/bmd-20261009-p/running-minimum.txt";
q = 1000003;
c(n) = if(n < 0, 0, binomial(-3/2, n));
vq(x) = if(x == 0, oo, valuation(x, q));
vand(Y) = prod(a = 1, #Y, prod(b = a + 1, #Y, Y[b] - Y[a]));
TMAX = 5;
export(c, vq, q, TMAX);
pens(Y, L) = {
  my(M = #Y, N = apply(t -> -t, select(t -> t < 0, L)), p = #N, k = M - p, B = p * (p - 1) / 2 + vecsum(N) + k, NU = B + TMAX);
  my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
    if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
      my(s = r - M); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
  my(D = matdet(X), V2 = 2 * vq(vand(Y)));
  vector(TMAX + 1, j, my(cf = polcoef(D, B + j - 1, 'u)); if(cf == 0, oo, vq(cf) - V2))
};
export(pens, vand);
run(name, Y, cmax) = {
  my(M = #Y, cols = [-M .. cmax], Ls = List());
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]]), N = apply(t -> -t, select(t -> t < 0, L)), p = #N);
    if(p >= 1 && p <= M - 1 && vecsort(N) == [1 .. p] && L != [-p .. 2 * M - 1 - p], listput(Ls, L)));
  my(win = vector(M - 1, p, pens(Y, [-p .. 2 * M - 1 - p])));
  my(PV = parapply(L -> pens(Y, L), Vec(Ls)), bad = matrix(M - 1, TMAX + 1), cnt = vector(M - 1), ex = List());
  my(plain = matrix(M - 1, TMAX + 1), rmin = vector(M - 1, p, vector(TMAX + 1, t, vecmin(win[p][1..t]))));
  for (i = 1, #Ls, my(L = Ls[i], p = #select(t -> t < 0, L)); cnt[p]++;
    for (t = 0, TMAX, if(PV[i][t + 1] < win[p][t + 1], plain[p, t + 1]++);
      if(PV[i][t + 1] < rmin[p][t + 1], bad[p, t + 1]++; if(#ex < 6, listput(ex, [L, t, PV[i][t + 1], rmin[p][t + 1]])))));
  write(OUT, name, " M=", M, ": coordinates with standard negatives per p: ", cnt);
  for (p = 1, M - 1, write(OUT, "  p=", p, ": window penalties t=0..", TMAX, ": ", win[p], "; running-minimum violations per t: ", bad[p, ], "; plain-form violations per t: ", plain[p, ]));
  for (i = 1, #ex, write(OUT, "   violation [Lambda, t, penalty, window] = ", ex[i]));
};
{
  my(e = q);
  my(cfg = [
    ["two cherries symmetric about 0", [1, 1 + e, -1, -1 - e + e^2], 8],
    ["pair and cherry, e_1 = eta", [1, -1 + e, 2, -2 + e^2], 8],
    ["nested cluster at +-1, e_1 = eta", [1, 1 + e^2, -1 + e, -1 + e + e^3], 8],
    ["symmetric pair plus a root, M = 3", [1, -4 + e, 3], 6],
    ["nested cherries (control)", [1, 1 + e, 1 + e + e^3, 3], 8]]);
  for (i = 1, #cfg, run(cfg[i][1], cfg[i][2], cfg[i][3]));
}
