\\ Far components of the peeling degeneration of the base (30 September 2026; cycle bmd-20260930-zb).
\\ Tested statement: for 2 <= p <= b-1, e = p-1, l = b-p, the far component
\\   F_p = P_{<R_e} + <(1+cx)^-3> + x^-(R_l+2) P_{<R_l} + (1+cx)^-7/2 P_{<4e}
\\         + (1+cx)^-5/2 x^(1/2-4l) P_{<4l} + x^(-7/2+4e-4el) P_{<4el},   R_n = n(2n-1),
\\ has Wronskian x^w0 (1+cx)^wc W_p(x), where w0 = Sigma_0 - binom(R,2) and wc = Sigma_c - binom(R,2)
\\ come from the exponent lists of the entry (bmd_cube_base_peeling_counts.py), and W_p is a polynomial
\\ of degree #F_p (the Fuchs count) with W_p(0) != 0 and W_p(-1/c) != 0.  Also reported: whether W_p
\\ is squarefree (simple Weierstrass points) and its factor degrees mod q = 2^61 - 1.
\\ Method: rows are Taylor coefficients at x0 of x^(beta+j)(1+cx)^gamma divided by x0^beta (1+c x0)^gamma;
\\ the determinant D(x0) times x0^(S_beta - w0) (1+c x0)^(S_gamma - wc) is W_p(x0) up to a constant; it is
\\ evaluated at #F_p + 3 points, interpolated through #F_p + 1 of them and checked at the other two.
\\ c = CS[p] with CS = (2, -3, 5, -7, 11, ...) as in the caterpillar script, so b = 3, 4 compare with its edges.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
md(N, c) = my(K = 2 * N - 4); -c * K + binomial(K, 2) - 3 + binomial(binomial(N - 2, 2), 2);
\\ exponent sums of F_p at 0 (x-orders) and at infinity (w-orders), as in the counts script
sum0(e, l) = -sum(j = 3, Rn(l) + 2, j) + sum(j = 0, Rn(e) + 4 * e, j) + sum(i = 4 * e - 4 * e * l, 4 * e + 4 * l - 1, i - 7/2);
sumatinf(e, l) = -binomial(Rn(e), 2) + sum(j = 3, Rn(l) + 4 * l + 3, j) + sum(i = -4 * e * l, 4 * e - 1, 7/2 - i);
blocks(e, l) = [[0, 0, Rn(e)], [-3, 0, 1], [0, -(Rn(l) + 2), Rn(l)], [-7/2, 0, 4 * e], [-5/2, 1/2 - 4 * l, 4 * l], [0, -7/2 + 4 * e - 4 * e * l, 4 * e * l]];
\\ normalized row of x^(be+j)(1+cx)^ga at x0, R Taylor coefficients, entries in Z/q
rowf(ga, be, j, c, x0, R, q) = {
  my(u = vector(R, a, Mod(binomial(be + j, a - 1), q) * x0^(j - a + 1)), r = Mod(c, q) / (1 + c * x0));
  my(v = vector(R, s, Mod(binomial(ga, s - 1), q) * r^(s - 1)));
  vector(R, m, sum(a = 1, m, u[a] * v[m + 1 - a]));
}
Dval(e, l, c, x0, q) = {
  my(R = Rn(e + l + 1), rows = List());
  foreach (blocks(e, l), bl, for (j = 0, bl[3] - 1, listput(rows, rowf(bl[1], bl[2], j, c, x0, R, q))));
  if (#rows != R, error("row count"));
  matdet(Mat(Vec(rows)~));
}
export(Rn, blocks, rowf, Dval);
main() = {
  my(q = 2^61 - 1, CS = [2, -3, 5, -7, 11, -13, 17, -19], bs = if (getenv("BS"), eval(getenv("BS")), [3, 4]));
  foreach (bs, b,
    my(N = 2 * b, R = Rn(b), B = binomial(R, 2), Sc = md(N, 7/2));
    for (p = 2, b - 1,
      my(e = p - 1, l = b - p, c = CS[p], w0 = sum0(e, l) - B, wc = Sc - B);
      my(nF = B - Sc - sum0(e, l) - sumatinf(e, l));
      my(Sb = sum(k = 1, 6, blocks(e, l)[k][2] * blocks(e, l)[k][3]), Sg = sum(k = 1, 6, blocks(e, l)[k][1] * blocks(e, l)[k][3]));
      my(A0 = Sb - w0, Ac = Sg - wc);
      if (denominator(A0) != 1 || denominator(Ac) != 1 || denominator(nF) != 1, error("non-integral exponents"));
      my(xs = vector(nF + 3, i, Mod(i + 1, q)));
      if (#select(x -> x == 0 || 1 + c * x == 0, xs), error("bad point"));
      my(ys = parvector(nF + 3, i, Dval(e, l, c, lift(xs[i]), q) * xs[i]^A0 * (1 + c * xs[i])^Ac));
      my(P = polinterpolate(xs[1..nF + 1], ys[1..nF + 1], 'x));
      my(chk = subst(P, 'x, xs[nF + 2]) == ys[nF + 2] && subst(P, 'x, xs[nF + 3]) == ys[nF + 3]);
      my(f = factormod(lift(P), q));
      emit(Str("b=", b, " p=", p, " (e,l)=(", e, ",", l, ") c=", c, " R=", R, " #F_p=", nF, ": degree ", poldegree(P),
        ", extra points ", if (chk, "agree", "DISAGREE"), ", W_p(0) ", if (polcoef(P, 0) != 0, "nonzero", "ZERO"),
        ", W_p(-1/c) ", if (subst(P, 'x, Mod(-1, q) / c) != 0, "nonzero", "ZERO"),
        ", squarefree ", if (vecmax(f[, 2]) == 1, "yes", "NO"), "; factor degrees and exponents ",
        vector(#f~, j, [poldegree(f[j, 1]), f[j, 2]])))));
}
default(nbthreads, 12);
default(parisizemax, 2000000000);
main();
