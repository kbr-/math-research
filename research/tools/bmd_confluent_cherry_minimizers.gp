\\ Minimal Cauchy-Binet triples of the confluent cherry's reduced expansion (7 October 2026; cycle bmd-20261007-zf).
\\ Same term valuation as bmd_confluent_cherry_windows2.gp (blocks V at columns N1, w^(-1)V at columns C2 = N2 - 1,
\\ E' with Gale n >= t + 2).  Lists, for each window [-j, 3M-1-j] and caterpillar valuations v, every minimizing
\\ pair (N1, C2) with the complement Gamma = ([-1, 3M-1-j] \ (N1 u C2)), and the excess vectors E1, E2, E3 by
\\ sorted position (position M is the top, paired with the root of valuation v_1 = 0).
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
fval(N, M, bq) = my(Ns = vecsort(N)); sum(i = 1, M, Ns[i] * bq[M + 1 - i]);
excess(N) = my(Ns = vecsort(N)); vector(#Ns, i, Ns[i] - (i - 1));
mins(M, a, w, vv, j) = {
  my(Lam = [-j .. 3*M - 1 - j], bq = vector(M, q, a + vv[q]), best = oo, arg = List());
  my(pos = select(t -> t >= 0, Lam));
  forsubset([#pos, M], S1, my(c1 = vecextract(pos, Vec(S1)), rest = select(t -> t >= -1 && !setsearch(Set(c1), t), Lam));
    forsubset([#rest, M], S2, my(c2 = vecextract(rest, Vec(S2)), L3 = vecsort(setminus(setminus(Set(Lam), Set(c1)), Set(c2))));
      my(N3 = vector(M));
      for (i = 1, M, N3[i] = max(L3[i] + 2, i - 1); if (i > 1, N3[i] = max(N3[i], N3[i - 1] + 1)));
      my(N2 = apply(t -> t + 1, c2), T = fval(c1, M, bq) + fval(N2, M, bq) + fval(N3, M, bq) + w * (vecsum(N3) - vecsum(L3)));
      if (T < best, best = T; arg = List());
      if (T == best, listput(arg, [vecsort(c1), vecsort(c2), select(t -> t >= -1, L3), excess(c1), excess(N2), excess(N3)]))));
  [best, Vec(arg)];
}
{
foreach([[2, 1, 1, [0, 2], 3], [2, 1, 1, [0, 2], 2], [3, 1, 1, [0, 1, 2], 4], [3, 1, 1, [0, 1, 2], 3], [3, 1, 1, [0, 1, 2], 2]], c,
  my(R = mins(c[1], c[2], c[3], c[4], c[5]));
  emit(Str("M = ", c[1], ", j = ", c[5], ", v = ", c[4], ": least ", R[1], ", ", #R[2], " minimizers [N1, C2, Gamma, E1, E2, E3]:"));
  foreach(R[2], x, emit(Str("    ", x))));
}
