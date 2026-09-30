\\ Far components of the odd base peeling (30 September 2026; cycle bmd-20260930-ze).
\\ Tested statement: for N = 2b+1 and 2 <= k <= b (e = k-1, l = b-k), the far component
\\   F_k = P_{<R_e} + <(1+cx)^-3> + x^-(R'_l+2) P_{<R'_l} + (1+cx)^-7/2 P_{<4e} + (1+cx)^-5/2 x^(-4l-3/2) P_{<4l+2}
\\         + x^(-7/2+j0) P_{<m},  (j0, m) = (2e-4el, 4el+2e) if l >= 1, (2, 2e) if l = 0,   R'_n = R_n + 2n,
\\ has Wronskian x^w0 (1+cx)^wc W_k(x) with W_k a polynomial of degree #F_k (Fuchs count from the exponent lists
\\ of bmd_cube_odd_peeling_counts.py), W_k(0) W_k(-1/c) != 0; also reported: squarefree, factor degrees mod q.
\\ Method as in bmd_cube_base_peeling_far.gp: normalized Taylor rows, interpolation at #F_k + 3 points mod 2^61 - 1.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
Ro(n) = Rn(n) + 2 * n;
md(N, c) = my(K = 2 * N - 4); -c * K + binomial(K, 2) - 3 + binomial(binomial(N - 2, 2), 2);
blocks(e, l) = [[0, 0, Rn(e)], [-3, 0, 1], [0, -(Ro(l) + 2), Ro(l)], [-7/2, 0, 4 * e], [-5/2, -4 * l - 3/2, 4 * l + 2], if (l >= 1, [0, -7/2 + 2 * e - 4 * e * l, 4 * e * l + 2 * e], [0, -3/2, 2 * e])];
halfzero(e, l) = my(mm = vector(4 * l + 2, i, 2 - 4 * l + i - 1), pm = if (l >= 1, vector(4 * e * l + 2 * e, i, 2 * e - 4 * e * l + i - 1), vector(2 * e, i, i + 1)), lo = vecmin(concat(mm, pm))); vector(#mm + #pm, i, lo + i - 1);
sum0(e, l) = -sum(j = 3, Ro(l) + 2, j) + sum(j = 0, Rn(e) + 4 * e, j) + vecsum(apply(j -> j - 7/2, halfzero(e, l)));
sumatinf(e, l) = -binomial(Rn(e), 2) + sum(j = 3, Ro(l) + 4 * l + 5, j) + sum(i = 0, 4 * e * l + 6 * e - 1, 9/2 - 4 * e + i);
rowf(ga, be, j, c, x0, R, q) = {
  my(u = vector(R, a, Mod(binomial(be + j, a - 1), q) * x0^(j - a + 1)), r = Mod(c, q) / (1 + c * x0));
  my(v = vector(R, s, Mod(binomial(ga, s - 1), q) * r^(s - 1)));
  vector(R, m, sum(a = 1, m, u[a] * v[m + 1 - a]));
}
Dval(e, l, c, x0, q) = {
  my(R = binomial(2 * (e + l + 1) + 1, 2), rows = List());
  foreach (blocks(e, l), bl, for (j = 0, bl[3] - 1, listput(rows, rowf(bl[1], bl[2], j, c, x0, R, q))));
  if (#rows != R, error("row count"));
  matdet(Mat(Vec(rows)~));
}
export(Rn, Ro, blocks, rowf, Dval);
main() = {
  my(q = 2^61 - 1, CS = [2, -3, 5, -7, 11]);
  foreach ([2, 3, 4], b,
    my(N = 2 * b + 1, R = binomial(N, 2), B = binomial(R, 2), Sc = md(N, 7/2));
    for (k = 2, b,
      my(e = k - 1, l = b - k, c = CS[k], w0 = sum0(e, l) - B, wc = Sc - B, nF = B - Sc - sum0(e, l) - sumatinf(e, l));
      my(bl = blocks(e, l), Sb = sum(i = 1, 6, bl[i][2] * bl[i][3]), Sg = sum(i = 1, 6, bl[i][1] * bl[i][3]));
      if (denominator(Sb - w0) != 1 || denominator(Sg - wc) != 1, error("non-integral exponents"));
      my(xs = vector(nF + 3, i, Mod(i + 1, q)));
      my(ys = parvector(nF + 3, i, Dval(e, l, c, lift(xs[i]), q) * xs[i]^(Sb - w0) * (1 + c * xs[i])^(Sg - wc)));
      my(P = polinterpolate(xs[1..nF + 1], ys[1..nF + 1], 'x));
      my(chk = subst(P, 'x, xs[nF + 2]) == ys[nF + 2] && subst(P, 'x, xs[nF + 3]) == ys[nF + 3], f = factormod(lift(P), q));
      emit(Str("N=", N, " k=", k, " (e,l)=(", e, ",", l, ") c=", c, " #F_k=", nF, ": degree ", poldegree(P),
        ", extra points ", if (chk, "agree", "DISAGREE"), ", W_k(0) ", if (polcoef(P, 0) != 0, "nonzero", "ZERO"),
        ", W_k(-1/c) ", if (subst(P, 'x, Mod(-1, q) / c) != 0, "nonzero", "ZERO"),
        ", squarefree ", if (vecmax(f[, 2]) == 1, "yes", "NO"), "; factor degrees ", vector(#f~, j, poldegree(f[j, 1]))))));
}
default(nbthreads, 12);
default(parisizemax, 2000000000);
main();
