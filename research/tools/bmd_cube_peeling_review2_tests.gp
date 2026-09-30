\\ Tests of the second peeling route review (30 September 2026; cycle bmd-20260930-zj).
\\ (1) Reality lead (Wronskians of Jacobi-type functions): compute the far polynomial W_k of the even peeling
\\     exactly over Q (c = 1) for (b,k) = (3,2), (4,2), (4,3) and count its real roots (polsturm), with the degree.
\\     All roots real would point to interlacing/electrostatic proofs of simplicity.
\\ (2) Perfectness lead (Hermite-Pade normality of binomial systems): for random degree vectors (n_1..n_l),
\\     1 <= n_s <= 6, l <= 4, test that sum_s Pol_(<n_s)(y) (1 + beta_s y)^(-7/2) is ordinary at y = 0 (Wronskian
\\     at 0 nonzero) modulo 2^61 - 1 at random beta.  All ordinary would support perfectness of the system,
\\     the property behind G_c != 0 and the tail minors of U.
\\ (3) Newton-polygon irreducibility lead (Dumas, Coleman, Filaseta): factor each exact W_k of (1) over Q and
\\     print its p-adic Newton polygon segments for p < 50; an irreducible W_k is squarefree in characteristic 0.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
md(N, c) = my(K = 2 * N - 4); -c * K + binomial(K, 2) - 3 + binomial(binomial(N - 2, 2), 2);
sum0(e, l) = -sum(j = 3, Rn(l) + 2, j) + sum(j = 0, Rn(e) + 4 * e, j) + sum(i = 4 * e - 4 * e * l, 4 * e + 4 * l - 1, i - 7/2);
sumatinf(e, l) = -binomial(Rn(e), 2) + sum(j = 3, Rn(l) + 4 * l + 3, j) + sum(i = -4 * e * l, 4 * e - 1, 7/2 - i);
blocks(e, l) = [[0, 0, Rn(e)], [-3, 0, 1], [0, -(Rn(l) + 2), Rn(l)], [-7/2, 0, 4 * e], [-5/2, 1/2 - 4 * l, 4 * l], [0, -7/2 + 4 * e - 4 * e * l, 4 * e * l]];
rowq(ga, be, j, c, x0, R) = {
  my(u = vector(R, a, binomial(be + j, a - 1) * x0^(j - a + 1)), r = c / (1 + c * x0));
  my(v = vector(R, s, binomial(ga, s - 1) * r^(s - 1)));
  vector(R, m, sum(a = 1, m, u[a] * v[m + 1 - a]));
}
Dq(e, l, c, x0) = {
  my(R = Rn(e + l + 1), rows = List());
  foreach (blocks(e, l), bl, for (j = 0, bl[3] - 1, listput(rows, rowq(bl[1], bl[2], j, c, x0, R))));
  matdet(Mat(Vec(rows)~));
}
Wexact(b, k) = {
  my(N = 2 * b, R = Rn(b), B = binomial(R, 2), Sc = md(N, 7/2), e = k - 1, l = b - k, c = 1);
  my(w0 = sum0(e, l) - B, wc = Sc - B, nF = B - Sc - sum0(e, l) - sumatinf(e, l));
  my(Sb = sum(i = 1, 6, blocks(e, l)[i][2] * blocks(e, l)[i][3]), Sg = sum(i = 1, 6, blocks(e, l)[i][1] * blocks(e, l)[i][3]));
  my(xs = vector(nF + 2, i, i + 1), ys = vector(nF + 2, i, Dq(e, l, c, xs[i]) * xs[i]^(Sb - w0) * (1 + c * xs[i])^(Sg - wc)));
  my(P = polinterpolate(xs[1..nF + 1], ys[1..nF + 1], 'x));
  if (subst(P, 'x, xs[nF + 2]) != ys[nF + 2], error("interpolation"));
  P;
}
main() = {
  foreach ([[3, 2], [4, 2], [4, 3]], bk,
    my(P = Wexact(bk[1], bk[2]));
    emit(Str("b=", bk[1], " k=", bk[2], " (c = 1): degree ", poldegree(P), ", real roots ", polsturm(P), ", squarefree over Q ", poldegree(gcd(P, P')) == 0));
    my(F = factor(P)[, 1]);
    emit(Str("  factor degrees over Q: ", apply(poldegree, F~), ", content ", content(P)));
    forprime (p = 2, 47, my(nv = newtonpoly(P, p), segs = List(), i = 1);
      while (i <= #nv, my(j = i); while (j < #nv && nv[j + 1] == nv[i], j++); listput(segs, [j - i + 1, nv[i]]); i = j + 1);
      emit(Str("  p=", p, " newton segments [length, slope]: ", Vec(segs)))));
  my(q = 2^61 - 1, bad = 0, tot = 0);
  setrand(20260930);
  for (trial = 1, 60,
    my(l = 2 + random(3), ns = vector(l, s, 1 + random(6)), L = vecsum(ns), bet = vector(l, s, Mod(1 + random(10^9), q)));
    my(rows = List());
    for (s = 1, l, for (i = 0, ns[s] - 1, listput(rows, vector(L, r, if (r - 1 >= i, Mod(binomial(-7/2, r - 1 - i), q) * bet[s]^(r - 1 - i), 0)))));
    tot++; if (matdet(Mat(Vec(rows)~)) == 0, bad++));
  emit(Str("perfectness test: ", tot, " random degree vectors (l = 2..4, n_s = 1..6), non-ordinary at 0: ", bad));
}
default(parisizemax, 3000000000);
main();
quit
