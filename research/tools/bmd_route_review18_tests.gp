\\ Route review tests (9 October 2026; cycle bmd-20261009-s).
\\ (1) Falsification: arc-wise kernel minimality (conj:cube-kernel-arc-minimality) at M = 5 above a cluster symmetric
\\     about the origin, (1, 1+eta, -1, -1-eta+eta^2, 2), all p, all k-sets T of [0, 6], t <= 8, u-weights 1,2,3,5,9,
\\     q-adic at q = eta = 1000003 (minimum-term value, the arc convention u = gamma s^w).
\\ (2) Contiguous-relation lead: at a rational configuration and rational u, is K_u(z^(j+1)) in the span of
\\     K_u(z^j), K_u(z^(j-1)) (a scalar three-term recurrence)? Reports the rank of the three columns.
\\ (3) Total-positivity lead: signs of D_T at a real point (rational roots, u = 1/100) over all T, per p.
OUT = "research/results/bmd-20261009-s/review-tests.txt";
q = 1000003;
c(n) = binomial(-3/2, n);
vq(x) = if(x == 0, oo, valuation(x, q));
Zv = varhigher("zz");
T1(F) = { my(d = poldegree(F, Zv)); sum(i = 0, d, polcoef(F, i, Zv) * c(i + 1) / c(i) * Zv^(i + 1)) };
om(v, w) = { my(r = 10^9); for (j = 1, #v, if(v[j] < oo, r = min(r, (j - 1) * w + v[j]))); r };
cols(Y, p, NU, IMAX) = {
  my(M = #Y, P = prod(s = 1, M, Zv - Y[s]));
  my(ncol = vector(p, n, my(r = lift(Mod(sum(m = 0, NU - n, c(m) * c(n + m) * 'u^(n + m) * Zv^m), P))); vector(M, s, polcoef(r, s - 1, Zv))));
  my(kc = vector(IMAX + 1, a, my(F = P * Zv^(a - 1), col = vector(M));
    for (m = 1, NU, F = T1(F); my(r = lift(Mod(F, P))); for (s = 0, M - 1, col[s + 1] += c(m) * polcoef(r, s, Zv) * 'u^m)); col));
  [ncol, kc]
};
{
  my(e = q, Y = [1, 1 + e, -1, -1 - e + e^2, 2], M = 5, WS = [1, 2, 3, 5, 9]);
  write(OUT, "(1) arc-wise kernel minimality, M = 5, cluster symmetric about 0:");
  for (p = 1, M - 1, my(k = M - p, B = p * (p + 1) / 2 + p * (p - 1) / 2 + k, NU = B + 8, C = cols(Y, p, NU, 6), Dv = Map(), bad = 0, n = 0);
    forsubset([7, k], S, my(T = Vec(S) - vector(k, a, 1));
      my(D = matdet(matrix(M, M, r, j, if(j <= p, C[1][j][r], C[2][T[j - p] + 1][r]))));
      mapput(Dv, T, vector(9, t, vq(polcoef(D, B + t - 1, 'u)))));
    my(v0 = mapget(Dv, [0 .. k - 1]));
    foreach(Mat(Dv)[, 1], T, n++; foreach(WS, w, if(om(mapget(Dv, T), w) < om(v0, w), bad++)));
    write(OUT, "  p=", p, ": ", n, " sets, window penalties ", v0, ", arc violations ", bad));
}
{
  my(Y = [1, 3/2, -2, 5/7], M = 4, p = 2, NU = 8, C = cols(Y, p, NU, 5));
  write(OUT, "(2) three-term recurrence test, M = 4, p = 2, u = 1/7:");
  for (j = 1, 4, my(A = matconcat([C[2][j]~, C[2][j + 1]~, C[2][j + 2]~]), Au = subst(A, 'u, 1/7));
    write(OUT, "  j = ", j, ": rank of [K(z^(j-1)), K(z^j), K(z^(j+1))] = ", matrank(Au)));
}
{
  my(Y = [1, 3/2, 2, 7/2], M = 4);
  write(OUT, "(3) signs of D_T at roots (1, 3/2, 2, 7/2), u = 1/100:");
  for (p = 1, M - 1, my(k = M - p, NU = 14, C = cols(Y, p, NU, 5), pos = 0, neg = 0);
    forsubset([6, k], S, my(T = Vec(S) - vector(k, a, 1));
      my(D = subst(matdet(matrix(M, M, r, j, if(j <= p, C[1][j][r], C[2][T[j - p] + 1][r]))), 'u, 1/100));
      if(D > 0, pos++, if(D < 0, neg++)));
    write(OUT, "  p=", p, ": positive ", pos, ", negative ", neg));
}
