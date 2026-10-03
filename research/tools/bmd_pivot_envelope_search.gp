\\ Exhaustive envelope search for cor:cube-pivot-envelope-support (cycle bmd-20261009-bf, 9 October 2026).
\\ By lem:cube-nested-family-pivots (with O_1 = [0, 2M-2]), the added orders (o*_1, ..., o*_(M-1)) form a permutation
\\ of [M, 2M-2]; r_M = 0, r_p = r_(p+1) + o*_p - (2M-p-1); family costs f_p / w_x = A_p + r_p + rho B_p with
\\ A_p = 2M^2 - 2Mp + p^2 - p, B_p = p^2 - p + M, rho = w_e/w_x > 0. For each M = 3..8 and each permutation, find the
\\ largest spread max - min of the minimizing families over all rho > 0 (only pairwise intersection points can carry
\\ ties), and count permutations with spread >= 3 (nullity >= 3 under hypothesis (F)). Prints the first instance.
OUT = "research/results/bmd-20261009-bf/pivot-envelope-search.txt";
spreadof(M, o) = {
  my(r = vector(M), c, B, best = 0, wit = 0);
  r[M] = 0;
  forstep (p = M - 1, 1, -1, r[p] = r[p + 1] + o[p] - (2*M - p - 1));
  c = vector(M, p, 2*M^2 - 2*M*p + p^2 - p + r[p]);
  B = vector(M, p, p^2 - p + M);
  for (p = 1, M, for (q = p + 1, M,
    my(rho = (c[p] - c[q]) / (B[q] - B[p]));
    if (rho > 0,
      my(L = vector(M, s, c[s] + rho * B[s]), m = vecmin(L), mins = select(s -> L[s] == m, [1 .. M]));
      my(sp = vecmax(mins) - vecmin(mins));
      if (sp > best, best = sp; wit = [rho, mins, L]))));
  [best, wit];
}
{
  for (M = 3, 8,
    my(base = [M .. 2*M - 2], n = M - 1, cnt = vector(M), first = 0, total = 0);
    forperm(base, o,
      my(res = spreadof(M, Vec(o)));
      total++;
      cnt[res[1] + 1]++;
      if (res[1] >= 3 && first == 0, first = [Vec(o), res[2]]));
    write(OUT, "M = ", M, ": ", total, " permutations; counts by largest spread 0..: ", cnt[1 .. min(M, 6)],
          if (first, Str("; first spread >= 3: o* = ", first[1], ", rho = ", first[2][1], ", minimizers ", first[2][2]), "; no spread >= 3")));
}
