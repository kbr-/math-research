\\ Accumulation curves of the last-step far roots (3 October 2026; cycle bmd-20261003-zx).
\\ For W_(b-1) at e = 4, 5, 6 (research/results/bmd-20261003-zw/W_last_e*.gp), link roots into chains: from an unvisited root,
\\ repeatedly step to the nearest unvisited root within 2.5 x the median nearest-neighbour distance, in both directions.
\\ Reports the median nearest-neighbour distance times e^2, the number of chains, and per chain (upper half plane, Im >= 0):
\\ its number of points and its two endpoints; and a sample of every 8th point of the longest chains, in x and in t = x/(1+x).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 80);
default(parisizemax, 4000000000);
fmt(z) = Str("(", precision(real(z), 4) * 1., ", ", precision(imag(z), 4) * 1., ")");
{
for (e = 4, 6,
  my(W = read(Str("research/results/bmd-20261003-zw/W_last_e", e, ".gp")), r = select(z -> imag(z) >= -1e-30, polroots(W)), m = #r, nn = vector(m));
  my(all = polroots(W), M = #all);
  for (i = 1, m, nn[i] = vecmin(vector(M, j, if (abs(r[i] - all[j]) < 1e-40, 1e9, abs(r[i] - all[j])))));
  my(med = vecsort(nn)[(m + 1) \ 2], h = 2.5 * med, used = vector(m), chains = List());
  for (s = 1, m, if (used[s], next); used[s] = 1; my(C = List([s]));
    for (dir = 1, 2, my(cur = s);
      while (1, my(best = 0, bd = h);
        for (j = 1, m, if (!used[j] && abs(r[j] - r[cur]) < bd, bd = abs(r[j] - r[cur]); best = j));
        if (!best, break); used[best] = 1; if (dir == 1, listput(C, best), listinsert(C, best, 1)); cur = best);
      if (dir == 1, cur = s));
    listput(chains, Vec(C)));
  my(L = vecsort(Vec(chains), c -> -#c));
  emit(Str("e=", e, ": upper-half roots ", m, ", median NN x e^2 = ", precision(med * e^2, 4) * 1., ", chains ", #L, ", sizes ", apply(c -> #c, L)));
  for (c = 1, min(4, #L), my(C = L[c]);
    emit(Str("  chain ", c, " (", #C, " points): ends x = ", fmt(r[C[1]]), " .. ", fmt(r[C[#C]]),
      "; every 8th point in t: ", strjoin(vector((#C + 7) \ 8, i, fmt(r[C[8 * (i - 1) + 1]] / (1 + r[C[8 * (i - 1) + 1]]))), " ")))));
}
